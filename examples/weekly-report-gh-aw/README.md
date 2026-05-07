# Weekly Report (gh-aw)

> A weekly Slack post summarizing what regressed in production, with proposed fixes and (optionally) a self-heal PR.

![Weekly production report posted to Slack: top regressions, contributors @-mentioned, self-heal PR linked](../../docs/weekly-report.png)

Every Monday morning the team gets a single Slack message: "here's what got worse last week, here's why, here's the fix, and a draft PR is already open." Engineers see the issue with their @-mention, click into the PR, and decide whether to merge it.

## How to install

| Step | Action |
|---|---|
| **Copy to your repo** | `.github/workflows/weekly-report.md` → same path |
|  | `.github/workflows/deep-insights/*.txt` → same path (all 7 files) |
| **Then run** | `gh aw compile` → commit generated `weekly-report.lock.yml` |
| **Set secrets (GitHub repo settings → Secrets)** | `HUD_MCP_KEY` - get from Hud dashboard → Settings → MCP keys |
|  | `ANTHROPIC_API_KEY` - get from console.anthropic.com |
|  | `SLACK_BOT_TOKEN` - Slack app with `chat:write` + `users:read.email` scopes |
|  | `SLACK_CHANNEL` - target Slack channel ID |

## What it does

On a schedule (or via manual dispatch), the workflow:

1. **Analyzes** the past week of production data via Hud MCP: error regressions, performance degradations, fingerprints, traffic shifts.
2. **Generates fixes** - for each ongoing issue, sub-agents in parallel investigate the root cause and propose a concrete code fix.
3. **Annotates contributors** - runs `git blame` on the suspect lines, looks up the authors in Slack, and tags them in the report.
4. **Quality pass (deslop)** - merges duplicates, enforces limits, removes redundancy.
5. **Self-heals (optional)** - for the highest-scoring fix, applies the change and opens a draft PR.
6. **Posts to Slack** - formats the result as Slack Block Kit and posts to a configured channel. Falls back to plain text if blocks fail.

The phases are defined as separate prompt files under `deep-insights/`, so individual phases can be re-tuned without touching the main workflow.

## Files

| Path | Purpose |
|---|---|
| `.github/workflows/weekly-report.md` | The gh-aw workflow (frontmatter + agent prompt) |
| `.github/workflows/deep-insights/*.txt` | Phase prompts: `investigate.txt` and `health-audit.txt` are alternates picked by `investigation_mode`; `solutions`, `blame`, `deslop`, `self-heal`, and `format` always run |

## Inputs

All inputs are optional; the workflow has sensible defaults.

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
4. Go to Actions → Weekly Hud Report → Run workflow. Watch the Slack channel for the result (~5-10 min for a typical run).

For the first few runs, consider:
- Setting `open_pr: false` to disable self-heal until you trust the fixes.
- Scoping `services` to one or two services to limit cost.

## Adapting it

- **Different service layout** (not `apps/*/package.json`)? Edit Phase 0 in the workflow.
- **Multi-team setup** with one report per team? See [`recipes/team-splitting/3-package-json/`](../../recipes/team-splitting/3-package-json/) for the team-grouping pattern.
- **Different schedule** (daily / bi-weekly)? Adjust the cron in the workflow frontmatter.
- **Different chat platform** (Teams instead of Slack)? Replace Phase 6. The rest of the pipeline writes to a markdown file that's chat-platform-agnostic.
- **Jira integration?** Phase 6's Slack message includes an "Open Jira Ticket" button. Search-and-replace `org-name` (Jira host) and `ORG` (Jira project ID) in `deep-insights/format.txt`, or strip the button entirely if you don't use Jira.

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
