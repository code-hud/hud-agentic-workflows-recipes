# Weekly Report — gh-aw (GitHub Agentic Workflows)

A weekly deep-insights report for production health, delivered to Slack. Built as a [gh-aw](https://github.com/githubnext/gh-aw) workflow — markdown + YAML, executed by the gh-aw runtime on top of GitHub Actions.

## What it does

On a schedule (or via manual dispatch), the workflow:

1. **Analyzes** the past week of production data via Hud MCP — error regressions, performance degradations, fingerprints, traffic shifts.
2. **Generates fixes** — for each ongoing issue, sub-agents in parallel investigate the root cause and propose a concrete code fix.
3. **Annotates contributors** — runs `git blame` on the suspect lines, looks up the authors in Slack, and tags them in the report.
4. **Quality pass (deslop)** — merges duplicates, enforces limits, removes redundancy.
5. **Self-heals (optional)** — for the highest-scoring fix, applies the change and opens a draft PR.
6. **Posts to Slack** — formats the result as Slack Block Kit and posts to a configured channel. Falls back to plain text if blocks fail.

The phases are defined as separate prompt files under `deep-insights/`, so individual phases can be re-tuned without touching the main workflow.

## Files

| Path | Purpose |
|---|---|
| `.github/workflows/weekly-report.md` | The gh-aw workflow (frontmatter + agent prompt) |
| `.github/workflows/deep-insights/*.txt` | Six phase prompts: investigate, health-audit, solutions, blame, deslop, self-heal, format |

Drop these into your customer repo at the same paths and run `gh aw compile` to generate the `.lock.yml`.

## Required secrets

| Secret | Where it comes from |
|---|---|
| `HUD_MCP_KEY` | Hud dashboard → Settings → MCP keys |
| `ANTHROPIC_API_KEY` | console.anthropic.com |
| `SLACK_BOT_TOKEN` | A Slack app with `chat:write` + `users:read.email` scopes, installed in your workspace |
| `SLACK_CHANNEL` | The default channel ID (overridable per-run via dispatch input) |

## Inputs

All inputs are optional — the workflow has sensible defaults.

| Input | Purpose |
|---|---|
| `investigation_mode` | `weekly` (default, week-over-week) or `audit` (absolute health check) |
| `slack_channel` | Override the default channel for this run |
| `services` | Comma-separated service names to scope the analysis |
| `additional_context` | Free-text appended to the analysis prompt |
| `open_pr` | Whether to run self-heal and open a fix PR (default `true`) |

## Verify it works

1. Set the four secrets in your repo.
2. Drop the workflow files into `.github/workflows/` and run `gh aw compile`.
3. Commit both `weekly-report.md` and the generated `weekly-report.lock.yml`.
4. Go to Actions → Weekly Hud Report → Run workflow. Watch the Slack channel for the result (~5–10 min for a typical run).

For the first few runs, consider:
- Setting `open_pr: false` to disable self-heal until you trust the fixes.
- Scoping `services` to one or two services to limit cost.

## Service discovery

Phase 0 of the workflow scans `apps/*/package.json` to discover services. If your repo layout differs (e.g. `services/*/`, `packages/*/`, Python `pyproject.toml`), edit the discovery script in `weekly-report.md` Phase 0.

The default reads the `author` field from each `package.json` to group services by team. See [`recipes/team-splitting/3-package-json/`](../../../recipes/team-splitting/3-package-json/) for the standalone version of this pattern.

## Schedule

The workflow currently runs on `workflow_dispatch` only (manual). To run weekly, add a `schedule:` block to the frontmatter:

```yaml
on:
  schedule:
    - cron: '0 14 * * MON'    # Mondays at 14:00 UTC
  workflow_dispatch:
    # ... existing inputs
```

Note: GitHub `schedule:` only fires on the default branch.
