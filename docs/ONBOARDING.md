# Contributor Onboarding

Use this checklist when you are new to this repo or when you need to dogfood a
fresh install before release.

## 1. Know the package boundary

`skills/last30days/` is the installable Agent Skill. `npx skills add` copies
that directory recursively, so only runtime files belong there:

- `SKILL.md`
- `scripts/last30days.py`
- `scripts/lib/`
- runtime helpers such as `store.py`, `watchlist.py`, `briefing.py`,
  `setup-keychain.sh`, and `setup-pass.sh`
- `references/`

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
  tests/test_hermes_skillignore.py \
  tests/test_plugin_contract.py \
  tests/test_version_consistency.py \
  tests/test_source_log_visibility.py

LAST30DAYS_BUILD_ALLOW_DIRTY=1 bash dev/last30days/scripts/build-skill.sh
```

The artifact check should show a small `.skill` bundle with runtime files
present and repo-only files absent.

## 4. Run the full gates before installation

```bash
uv run pytest
go test ./...
```

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

## 6. Dogfood the installed engine

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

## 7. Opt-in Facebook dogfood

Facebook uses an operator-authenticated, retained agent-browser profile. Do not
run this smoke in CI. First use the current `publicOperatorUrl` returned by
agent-browser to sign in, then run:

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

## 8. Opt-in LinkedIn dogfood

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
It rejects sponsored and non-post cards and requires canonical LinkedIn post or
activity permalinks, authors, and in-range dates. Never automate or bypass a
LinkedIn checkpoint.
