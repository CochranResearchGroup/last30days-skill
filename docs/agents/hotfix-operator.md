# Provider-free hotfix drill

WI-007 supplies a dormant hotfix control path and a disposable release drill.
The repo-only operator command is `dev/last30days/scripts/hotfix_operator.py`.
It does not activate an incident or provide an operational deployment command.

## Incident handling

The coordinator qualifies a production-impacting defect from current evidence,
records the WI locator, expected/observed behavior, affected identities,
rollback evidence, overlaps, and exact effect authority, then owns priority
integration. The real hotfix slot stays dormant until that qualification.
Feature work whose surface conflicts pauses and must reconcile to the accepted
hotfix merge before its own integration. Unaffected work may continue.

Source integration, staging acceptance, incident-specific deployment authority,
deployment readback, and rollback remain distinct gates. This drill supplies
provider-free acceptance for those controls. A real staging environment,
authenticated canary, upgrade, or rollback requires its own exact authority.
GitHub issue state is independent of repo-local WI-007 completion.

## Preflight and source identity

Use a standalone clean local clone with exact source commits retained. A linked
worktree's `.git` pointer is deliberately rejected. Create the clone with
`git clone --no-hardlinks --no-checkout`, check out the selected commit, and
retain the exact previous release commit as an ancestor. No fixture version
edit or synthetic re-commit is needed. The selected commit must equal that
clone's `origin/main`; verify current owned-fork custody before preparing it.
Preflight never fetches or makes a current remote-state claim.

Run with a clean child environment (using the desired absolute Python 3.12+
executable) so ambient provider/configuration variables fail visibly:

```sh
env -i PATH=/usr/bin:/bin python3 dev/last30days/scripts/hotfix_operator.py preflight \
  --source-root /tmp/wi007-source-clone \
  --source-commit SOURCE_COMMIT_40_HEX \
  --previous-commit PREVIOUS_COMMIT_40_HEX
```

Replace the uppercase commit placeholders with verified values. Both committed
runtime manifests must match their payloads and the versions must differ.
Git pointer files, `commondir`, object alternates, metadata symlinks, included
configuration, dirty source, stale source identity, and ambient credentials or
runtime configuration are rejected. No host Git hooks or fsmonitor runs.

## Disposable drill

```sh
env -i PATH=/usr/bin:/bin python3 dev/last30days/scripts/hotfix_operator.py drill \
  --source-root /tmp/wi007-source-clone \
  --source-commit SOURCE_COMMIT_40_HEX \
  --previous-commit PREVIOUS_COMMIT_40_HEX \
  --output /tmp/wi007-acceptance.json

python3 dev/last30days/scripts/hotfix_operator.py report /tmp/wi007-acceptance.json
```

The output must be a new JSON file. Existing evidence is never overwritten.
The drill owns a private temporary root, builds the candidate twice with
`SOURCE_DATE_EPOCH=0`, and uses the current installer with a fake user manager.
Each scenario owns its database, configuration, socket, and frozen host-copy
directory. `HOME` and `CODEX_HOME` are never overridden. The fixture calls the
installer's `--skill-host-root PATH` option with its own empty private directory;
the option defaults to the existing user-home behavior outside the fixture and
only scopes refresh of frozen `.agents`, `.claude`, and `.codex` entrypoints.
Relative, symlinked, non-owner, and group/world-writable overrides are rejected.

Five separately named scenarios run once: upgrade, failed-upgrade restoration,
rollback, rollback-forward, and terminal recovery failure. Each has at most one
upgrade. Rollback-forward has one explicit backward setup operation and one
explicit forward operation; it is never an automatic retry. The installer owns
its atomic release switches and snapshot restoration. The drill adds no second
recovery attempt if the installer's recovery fails.

The service and schema migration are synthetic. The actual committed artifacts
are built and installed into disposable directories, but their provider/service
code is not executed. The fixture uses schemas 17/18 and sentinel rows to prove
the installer's preservation behavior. These results do not establish product
migration correctness or operational staging readiness.

Receipt readback binds source commits, artifact/build hashes, manifests,
contracts, versions, synthetic schema, readiness, database content digests,
sentinel rows, socket peer PID/start identity, and raw installer results. The
separate disposable Git history proves priority integration and affected-lane
reconciliation. Replayed hotfix contracts remain `mode=drill`; their simulated
merge commits are distinct from the actual artifact source commits.

`report` performs no Git, process, network, or database operation. It validates
receipt consistency and replays the controller gates. Its `done_eligible` result
is evidence for coordinator reconciliation; it neither closes a work item nor
grants deployment authority. The digest detects accidental modification; the
receipt is not a cryptographic attestation against a malicious producer.

## Bounds and incomplete outcomes

The baseline was 3.00 seconds wall time. The complete drill ceiling is 60s;
builder calls are bounded at 30s, installer calls at 15s, readiness at 1s, and
child termination at 3s. Crossing a bound fails the run and retains partial
evidence. A failed expected-recovery scenario may pass its test while retaining
the simulated incident outcome `blocked`; it never claims the defect fixed.

The manager can only control the drill's original child handles. Teardown uses
pidfds and process birth identity, then a fresh `/proc` census before deleting
the exact owned root. Unknown ownership or a residual process retains the root
for diagnosis. The failed JSON receipt names that root; do not retry or delete
it blindly. Successful teardown removes disposable worktrees, processes,
sockets, databases, and artifacts while retaining the requested JSON receipt.

The final receipt makes no fresh production-health assertion. Production is
outside the fixture's paths, manager, and effect authority. Operational checks
remain separate from the provider-free drill.
