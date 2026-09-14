"""Provider-free behavior through the monitor product command interface."""

from datetime import datetime, timezone
import sqlite3

from lib.service_monitor_application import MonitorApplication
from lib.service_post_search import PostSearchBackend
from tests.test_service_collection import _coordinator, _follow_spec
from tests.test_service_post_search import _seed_post_corpus


def composition(tmp_path):
    db, _, _, _, collections = _coordinator(tmp_path)
    _seed_post_corpus(db)
    spec = collections.put_spec(_follow_spec())
    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        row = dict(conn.execute("SELECT * FROM document_versions WHERE version_id='version-legacy-current'").fetchone())
        row.update(version_id='follow-version-1', content_hash='sha256:follow-version-1', access_partition_id='profile:x-primary')
        conn.execute(f"INSERT INTO document_versions ({','.join(row)}) VALUES ({','.join('?' for _ in row)})", tuple(row.values()))
        conn.execute("UPDATE documents SET source='x', access_partition_id='profile:x-primary'")
        conn.execute("UPDATE documents SET current_version_id='follow-version-1'")
        conn.execute("""INSERT INTO document_version_sightings
            (version_id, acquisition_id, collection_spec_id, collection_run_id,
             observed_at, access_partition_id)
            VALUES ('follow-version-1', 'follow-fixture', ?, 'fixture-run',
                    '2026-09-05T12:01:00Z', 'profile:x-primary')""",
                     (spec.collection_spec_id,))
    backend = PostSearchBackend(db, clock=lambda: datetime(2026, 9, 14, tzinfo=timezone.utc))
    app = MonitorApplication(db, backend, collection_reader=collections,
                             access_partitions=lambda profile: ('public', 'profile:' + profile),
                             clock=lambda: '2026-09-14T00:00:00Z')
    ref = {'schema_version': 1, 'view_kind': 'follow',
           'collection_spec_id': spec.collection_spec_id, 'spec_version': 1}
    return app, collections, ref


def command(app, action, **fields):
    return app.command({'profile_id': 'x-primary', 'command': {'action': action, **fields}})


def create(app, ref):
    return command(app, 'create', monitor_id='monitor-fixture', name='Fixture follow',
                   view_ref=ref, cadence_seconds=3600, max_items=20, retention_days=30)


def test_real_follow_to_frozen_digest_is_explicit_and_restart_safe(tmp_path):
    app, collections, ref = composition(tmp_path)
    created = create(app, ref)
    assert created['lifecycle_state'] == 'disabled'
    command(app, 'activate', monitor_id=created['monitor_id'])
    captured = command(app, 'capture', monitor_id=created['monitor_id'], capture_id='first')
    assert captured['view_ref'] == ref
    assert len(captured['evidence']) == 1
    result = command(app, 'evaluate', monitor_id=created['monitor_id'], snapshot_id=captured['snapshot_id'])
    digest = result['digest']
    assert digest['comparison_status'] == 'baseline_only'
    assert digest['current_count'] == 1
    assert command(app, 'baseline', monitor_id=created['monitor_id']) == {'baseline': None}
    command(app, 'accept', run_id=result['run']['run_id'])
    second = command(app, 'capture', monitor_id=created['monitor_id'], capture_id='second')
    result2 = command(app, 'evaluate', monitor_id=created['monitor_id'], snapshot_id=second['snapshot_id'])
    assert result2['digest']['counts']['unchanged'] == 1
    assert result2['digest']['entries'][0]['evidence_refs'][0]['version_id'] == 'follow-version-1'
    reopened = MonitorApplication(app.db_path, app.search_backend,
                                  collection_reader=collections, access_partitions=app.access_partitions)
    assert command(reopened, 'digest', run_id=result2['run']['run_id']) == result2['digest']
    assert command(reopened, 'capture', monitor_id=created['monitor_id'], capture_id='second') == second
