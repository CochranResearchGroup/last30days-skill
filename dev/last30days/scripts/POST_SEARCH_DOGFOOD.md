# Stored-post search runtime acceptance

Users search stored posts with `/last30days` and a cache-only search request,
for example `/last30days search stored browser-agent posts by alice`. The
agent-facing `search_posts` tool and `POST /v1/posts/search` share the same
filters, immutable evidence, revision modes and pagination contract.

This repository-only acceptance probe proves that contract against a fresh,
versioned WI-001 development runtime. It imports the existing synthetic test
fixtures, so use the repository's `uv` development environment. It is excluded
from Skill installs. It never changes installed services, reads private data,
or calls providers. It builds the fresh MCP adapter offline; Go dependencies
must already be cached.

From a clean assigned topic worktree, build the service artifact twice with
fixed `SOURCE_DATE_EPOCH=0` using `service/scripts/build-runtime.sh --output-dir`
and compare hashes. Do not refresh or alter the runtime manifest to bypass a
stale-manifest failure; return that coordinator-owned join.

For development acceptance only, invoke:

```sh
uv run python dev/last30days/scripts/post_search_dogfood.py \
  --state-root /absolute/private/unique-state-base \
  --runtime-root /absolute/private/short-runtime-base \
  --artifact /absolute/build/last30days-service-0.3.117.tar.gz
```

Both roots must be outside the worktree and all installed service roots. The
controller derives the exact lane-owned paths, checks a clean source commit,
verifies the artifact and rejects existing state. Keep the worktree unchanged
until the probe exits: controller restart and teardown validate the same
commit-bound descriptor. Never repoint an existing runtime to another commit.

The probe starts one runtime, seeds only its empty synthetic database, runs
fresh HTTP/MCP discovery and 19 filter/revision/identity/access cases, and
checks the complete database digest around read-only calls. It then explicitly
publishes one synthetic revision, proves old pagination remains pinned, stops
and restarts the same isolated identity, and proves the old cursor fails with
`cursor_stale`. Publication is a fixture mutation and has separate before/after
digests; search remains read-only. Cursors are process-local, so callers restart
search after expiry, eviction or service restart.

The receipt is retained beneath the derived runtime's
`receipts/search-packet4.json`, with both runtime process identities,
artifact/manifest/contract identity, MCP discovery and case digests, restart
evidence, controller teardown, and a fresh OS census including the owned process
sessions. Failures retain their receipt and attempt exact-owner teardown.
State, logs, built adapter and evidence are retained for review; the probe does
not remove historical roots. The printed path and hash locate the receipt.

Passing this probe establishes provider-free runtime behavior. Packet 3's
frozen performance sample remains separate; this probe makes no new latency,
semantic-quality, installed-runtime or production claim.
