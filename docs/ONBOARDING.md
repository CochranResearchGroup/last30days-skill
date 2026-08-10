# Contributor Onboarding

Use this checklist when you are new to this repo or when you need to dogfood a
fresh install before release.

## 1. Know the package boundary

`skills/last30days/` is the installable Agent Skill. `npx skills add` copies
that directory recursively, so only Skill compatibility and client files
belong there:

- `SKILL.md`
- `references/monitoring.md`, `administration.md`, and `maintenance.md`
- `references/direct-engine-compatibility.md`
- `scripts/last30days.py`
- `scripts/lib/`
- runtime helpers such as `store.py`, `watchlist.py`, `briefing.py`,
  `service.py`, `install-service.sh`, `setup-keychain.sh`, and `setup-pass.sh`
- `references/`

The first-class service product is packaged from the repo-owned `service/`
boundary. `service/VERSION`, `service/runtime-manifest.json`, its builder,
transactional installer, and systemd template stay outside the Skill payload.
The manifest explicitly selects the still-canonical Python runtime sources
during this migration packet; service artifacts contain no `SKILL.md`, Skill
docs, setup scripts, or Skill lifecycle authority.

`SKILL.md` is the concise ordinary MCP client and should remain no more than
300 lines. Privileged and compatibility mechanics belong in the gated
references above; adding them back to the ordinary Skill is a product-boundary
regression.

Repo-only files stay outside the installable skill:

- `dev/last30days/scripts/` - release, eval, comparison, and verification
  helpers
- `dev/last30days/agents/` - repo-only agent adapter experiments
- `assets/last30days/` - media assets
- `docs/`, `fixtures/`, `tests/`, and CI metadata

Do not rely on `.skillignore` to keep files out of `npx skills add`; the
installer does not honor it. The durable rule is: if it should not install, do
not put it under `skills/last30days/`.

## 2. Set up the dev environment

```bash
uv run pytest tests/test_plugin_contract.py
PYTHONPATH=skills/last30days/scripts python3 skills/last30days/scripts/last30days.py --diagnose
```

Python 3.12+ is required. The repo uses `uv`; the local virtualenv lives in
`.venv/`.

## 3. Run the fast install-readiness checks

```bash
uv run pytest \
  tests/test_build_skill_artifact.py \
  tests/test_skill_service_first_contract.py \
  tests/test_hermes_skillignore.py \
  tests/test_plugin_contract.py \
  tests/test_service_runtime_package.py \
  tests/test_service_lifecycle_install.py \
  tests/test_version_consistency.py \
  tests/test_source_log_visibility.py

LAST30DAYS_BUILD_ALLOW_DIRTY=1 bash dev/last30days/scripts/build-skill.sh
bash service/scripts/build-runtime.sh
```

The artifact check should show a small `.skill` bundle with runtime files
present and repo-only files absent.

## 4. Run the full gates before installation

```bash
python3 dev/last30days/scripts/audit_plan_authority.py
uv run pytest
go test ./...
```

The authority audit must report exactly one integrated campaign authority and
verify that every open roadmap lane has a current actionable plan, the latest
goal checkpoint carries all required governance fields, and the latest
runbook turn has complete closeout evidence.

Run the Go command from `mcp/`:

```bash
(cd mcp && go test ./...)
```

## 5. Install from the working tree

Remove the previous copied install first so deleted files do not linger:

```bash
rm -rf "$HOME/.agents/skills/last30days"
npx skills add . -g -y -a codex
```

Then verify the installed copy:

```bash
find "$HOME/.agents/skills/last30days" -maxdepth 3 -type f | sort
PYTHONPATH="$HOME/.agents/skills/last30days/scripts" \
  python3 "$HOME/.agents/skills/last30days/scripts/last30days.py" --diagnose
```

The installed copy should not contain `assets/`, `agents/`,
`scripts/build-skill.sh`, `scripts/evaluate_search_quality.py`,
`scripts/test_device_auth.py`, or `scripts/verify_v3.py`.

For a Linux service-backed dogfood run, install the independently built service
artifact rather than making the copied Skill its lifecycle authority:

```bash
bash service/scripts/build-runtime.sh
bash service/scripts/install.sh install \
  --artifact dist/service/last30days-service-0.2.9.tar.gz
bash service/scripts/install.sh diagnose
service_launcher="${XDG_DATA_HOME:-$HOME/.local/share}/last30days/service/last30days-service"
"$service_launcher" \
  query "last30days installed service smoke" --freshness cache_only
```

Dogfood one upgrade and `service/scripts/install.sh rollback` only with
reviewed, version-distinct artifacts. Confirm that `current` and `previous`
resolve under `releases/`, the readiness receipt matches the live version,
contract digest, schema 12, and manifest digest, and the managed unit contains
no `.agents/skills` path.

For v4 release review, verify the three independent identities explicitly:
Skill/plugin `4.0.0`, MCP manifest and binary stamp `4.0.1`, and service plus
runtime manifest `0.2.9`. The repository tag names the Skill release and must
not be reused as the MCP binary version.

Then connect the MCP bundle and verify its listed surface is `service_info`,
`query`, `refresh`, `job_status`, `topic`, `temporal_query`,
`profile_history`, `coverage`, `collection`, and `maintenance_status`. Verify
the capability, source, and topic resources. Confirm that `temporal_query`
with `profile_id=default` reports only the public partition and remains
cache-only. A query handler must not launch
`last30days.py` or create a browser process.

Dogfood the installed Skill with a fresh agent context. It should read only
`SKILL.md`, call `service_info` first, and complete one cache-only query without
loading any file under `references/`. Then ask for read-only coverage
monitoring and verify only `references/monitoring.md` is needed.

For a local Codex checkout, install and verify the current adapter explicitly:

```bash
bash mcp/scripts/install-codex.sh
codex mcp get last30days
go version -m "$HOME/.local/bin/last30days-pp-mcp"
```

The installer validates and regenerates the canonical Go contract before it
builds. Any service-contract compatibility change must advance
`mcp/manifest.json` and add one exact immutable entry to
`mcp/compatibility-releases.json`; otherwise generation and installation fail
closed.

The binary must be enabled at user scope, point at the owner-private service
socket, report the current repository revision with `modified=false` when the
checkout is clean, and return cached evidence without creating a refresh job
when `freshness_policy=cache_only`.

For App Intelligence maintenance-plane changes, also run:

```bash
uv run pytest \
  tests/test_service_collection.py \
  tests/test_service_product.py \
  tests/test_service_graphiti.py \
  tests/test_service_intelligence_contracts.py \
  tests/test_service_intelligence.py \
  tests/test_service_migrations.py \
  tests/test_service_install.py
schema_dir="$(mktemp -d)"
codex app-server generate-json-schema --out "$schema_dir"
```

Delete the temporary schema directory after inspection. Verify one real
read-only structured turn against the installed app-server when its protocol
or client changes, and retain the returned model, thread, and turn IDs in the
validation receipt. The turn must use an output schema. Confirm that rejected
output is still recorded, call/branch/test/rework bounds fail closed, artifacts
reject credential or browser-session fields, and neither publication nor live
source configuration changes can occur from a model decision or approval
record alone.

The packaged operator entry point is `service.py intelligence
{enrich,evaluate} --job-id ... --input ...`. Its input must be normalized
public evidence, never a browser page dump or session diagnostic. Normal MCP
and Skill research flows must not invoke this command.

The adapter-maintenance entry point is `service.py repair
{investigate,evaluate} --policy ...`. Exercise it only in a disposable fixture
repository during onboarding. Verify that concurrent branch/evaluation claims
fail closed, the durable policy cannot change between commands, branch names
stay under `last30days-repair/`, test commands must match the policy exactly,
and the temporary detached worktree is removed after evaluation.

## 6. Dogfood the compatibility Engine explicitly

The Engine is no longer the ordinary Skill path. Run this section only as an
operator/developer after explicitly selecting the compatibility/debug path.
The installed MCP/service smoke above is the primary product acceptance.

Use the installed copy, not the repo checkout:

```bash
plan="$(mktemp)"
cat > "$plan" <<'JSON'
{
  "raw_topic": "last30days onboarding smoke",
  "intent": "concept",
  "freshness_mode": "evergreen_ok",
  "cluster_mode": "none",
  "subqueries": [
    {
      "label": "primary",
      "search_query": "last30days onboarding smoke",
      "ranking_query": "What evidence proves the installed last30days engine can run?",
      "sources": ["reddit", "hackernews", "polymarket"],
      "weight": 1.0
    }
  ],
  "source_weights": {
    "reddit": 0.34,
    "hackernews": 0.33,
    "polymarket": 0.33
  }
}
JSON

PYTHONPATH="$HOME/.agents/skills/last30days/scripts" \
  python3 "$HOME/.agents/skills/last30days/scripts/last30days.py" \
  "last30days onboarding smoke" \
  --emit=json \
  --search=reddit,hackernews,polymarket \
  --plan "$plan" \
  --quick \
  --mock
```

For an output-file smoke that avoids live network/API calls:

```bash
tmpdir="$(mktemp -d)"
plan="$(mktemp)"
cat > "$plan" <<'JSON'
{
  "raw_topic": "last30days onboarding smoke",
  "intent": "concept",
  "freshness_mode": "evergreen_ok",
  "cluster_mode": "none",
  "subqueries": [
    {
      "label": "primary",
      "search_query": "last30days onboarding smoke",
      "ranking_query": "What evidence proves the installed last30days engine can run?",
      "sources": ["reddit", "hackernews", "polymarket"],
      "weight": 1.0
    }
  ],
  "source_weights": {
    "reddit": 0.34,
    "hackernews": 0.33,
    "polymarket": 0.33
  }
}
JSON

PYTHONPATH="$HOME/.agents/skills/last30days/scripts" \
  python3 "$HOME/.agents/skills/last30days/scripts/last30days.py" \
  "last30days onboarding smoke" \
  --emit=html \
  --search=reddit,hackernews,polymarket \
  --plan "$plan" \
  --quick \
  --mock \
  --output "$tmpdir/smoke.html"
test -s "$tmpdir/smoke.html"
```

Use a live run only when you want to test current external source behavior.
For install/readiness checks, `--diagnose` plus mock smoke tests are enough to
prove the installed runtime can import, parse flags, execute the pipeline, and
write output.

## 7. Opt-in X agent-browser dogfood

The X browser backend reuses an operator-authenticated retained profile and is
never enabled implicitly. Do not run this smoke in CI. Confirm that the
agent-browser access plan selects the intended X profile. The access plan's
shared-acquisition browser and session hints are authoritative over the
optional configured session name. Then run:

```bash
LAST30DAYS_X_BROWSER_LIVE_SMOKE=1 \
LAST30DAYS_X_BROWSER_PROFILE=last30days-facebook \
LAST30DAYS_X_BROWSER_SESSION=last30days-facebook \
uv run pytest tests/test_x_browser.py -k live -vv
```

The smoke runs three low-volume dated Latest searches through one retained
session. It requires canonical numeric status permalinks, authors, meaningful
text, and in-range dates, and stops on login, checkpoint, restriction, or
search-state mismatch without exporting cookies.

## 8. Opt-in Facebook dogfood

Facebook uses an operator-authenticated, retained agent-browser profile. Do not
run this smoke in CI. First use the current `publicOperatorUrl` returned by
agent-browser to sign in. The scraper must reuse a compatible broker-selected
profile owner even when the configured session name belongs to another client.
Then run:

```bash
LAST30DAYS_FACEBOOK_LIVE_SMOKE=1 \
LAST30DAYS_FACEBOOK_PROFILE=last30days-facebook \
LAST30DAYS_FACEBOOK_SESSION=last30days-facebook \
uv run pytest tests/test_facebook.py -k live -vv
```

The smoke runs three low-volume queries in one retained browser. It requires
query-specific search URLs and rejects every item without a canonical post
permalink, author, and in-range publication date. `auth_required`,
`checkpoint_required`, and `operator_ingress_unavailable` are operator actions;
do not bypass them or fall back to broad home-feed extraction.

After either browser smoke, inspect
`~/.config/last30days/agent-browser.json`. It should contain stable target
profile, browser-build, host, provider, and sharing-policy selections. It must
not contain cookies, credentials, profile paths, operator URLs, browser or
session IDs, route or display IDs, tabs, or page data.

## 9. Opt-in LinkedIn dogfood

LinkedIn uses the same retained agent-browser contract but should normally use
its own `last30days-linkedin` profile. A deliberately shared profile is allowed
through the overrides below when the browser already owns both logins. Complete
login or security verification manually through the returned operator URL,
then run:

```bash
LAST30DAYS_LINKEDIN_LIVE_SMOKE=1 \
LAST30DAYS_LINKEDIN_PROFILE=last30days-linkedin \
LAST30DAYS_LINKEDIN_SESSION=last30days-linkedin \
uv run pytest tests/test_linkedin.py -k live -vv
```

The smoke runs three low-volume latest-content queries in one retained browser.
LinkedIn user-like browser actions default to at least four seconds apart
and no more than six per rolling minute. The scraper reuses one LinkedIn tab
and stops without retrying when a search-limit, throttling, restriction, or
unusual-activity warning appears.
It rejects sponsored and non-post cards and requires canonical LinkedIn post or
activity permalinks, authors, and in-range dates. Never automate or bypass a
LinkedIn checkpoint.

Profile-adapter changes must also run:

```bash
uv run pytest \
  tests/test_linkedin_profile.py \
  tests/test_service_profiles.py \
  tests/test_service_intelligence_contracts.py
```

Profile canaries use an exact `/in/<slug>/` or `/company/<slug>/` URL through a
reviewed `surface_kind=profile` collection spec. Verify that auth/checkpoint
failures stop before navigation, raw evidence exists before profile rows,
section spans resolve to immutable evidence, and messages/connections/
invitations are never touched.
