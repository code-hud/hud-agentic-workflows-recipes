# gh-aw Template

Minimal [gh-aw](https://github.com/githubnext/gh-aw) agent skeleton: Hud MCP + Claude engine, no task. Drop your task description in and ship.

## Files

| Path | Purpose |
|---|---|
| `.github/workflows/agent.md` | The gh-aw workflow — frontmatter wired up, body has a placeholder `## Task` section |

## Setup

1. Copy `.github/workflows/agent.md` into your repo at the same path.
2. Add `HUD_MCP_KEY` and `ANTHROPIC_API_KEY` as repo secrets.
3. Run `gh aw compile` to generate `agent.lock.yml`. Commit both files.
4. Edit the `## Task` section with your actual task.

## Required secrets

| Secret | Where it comes from |
|---|---|
| `HUD_MCP_KEY` | Hud dashboard → Settings → MCP keys |
| `ANTHROPIC_API_KEY` | console.anthropic.com (or [`docs/auth.md`](../../docs/auth.md) for the Bedrock variant). The `engine: claude` line in the workflow frontmatter picks this up from repo secrets automatically — no env block needed. |

## Common tweaks

- **Schedule it.** Add a `schedule:` block to the `on:` frontmatter section (note: GitHub `schedule:` only fires on the default branch).
- **Add Slack output.** Add `safe-outputs: { create-pull-request: ... }` for self-heal PRs, or include `SLACK_BOT_TOKEN` env + a final step that posts to Slack.
- **Tighten the network allow-list.** The default allows `defaults`, `node`, `github`, plus `api.hud.io` / `cdn.hud.io` (the latter for runtime resources fetched by `hud-mcp@v2` — *not* for the legacy `mcp-linux-x64` download path documented as wrong in [`docs/auth.md`](../../docs/auth.md)). Remove anything you don't need.
- **Adjust timeout.** Default is 30 minutes. Bump for long analysis runs.

## Reference examples

- [Weekly report](../../examples/weekly-report/gh-aw/) — a full multi-phase analysis workflow with Slack output and self-heal.
