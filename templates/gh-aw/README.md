# gh-aw Template

Minimal [gh-aw](https://github.com/githubnext/gh-aw) agent skeleton: Hud MCP + Claude engine, no task. Drop your task description in and ship.

## How to install

| Step | Action |
|---|---|
| **Copy to your repo** | `.github/workflows/agent.md` → same path |
| **Then run** | `gh aw compile` → commit generated `agent.lock.yml` |
| **Set secrets (GitHub repo settings → Secrets)** | `HUD_MCP_KEY` - get from Hud dashboard → Settings → MCP keys |
|  | `ANTHROPIC_API_KEY` - get from console.anthropic.com (or [Bedrock](../../docs/auth.md)) |

## Files

| Path | Purpose |
|---|---|
| `.github/workflows/agent.md` | The gh-aw workflow. frontmatter wired up, body has a placeholder `## Task` section |

## Where to put the prompt

Open `.github/workflows/agent.md` and replace the `## Task` section with your task prompt. You can grab a ready-made prompt from [`recipes/prompts/`](../../recipes/prompts/) (e.g. `weekly-report/main.md`, `rollback-check.md`) or write your own.

## Setup

1. Copy `.github/workflows/agent.md` into your repo at the same path.
2. Add `HUD_MCP_KEY` and `ANTHROPIC_API_KEY` as repo secrets.
3. Replace the `## Task` section with your prompt (see above).
4. Run `gh aw compile` to generate `agent.lock.yml`. Commit both files.
5. Run the workflow manually for first verification.

## Required secrets

| Secret | Where it comes from |
|---|---|
| `HUD_MCP_KEY` | Hud dashboard → Settings → MCP keys |
| `ANTHROPIC_API_KEY` | console.anthropic.com (or [`docs/auth.md`](../../docs/auth.md) for the Bedrock variant). The `engine: claude` line in the workflow frontmatter picks this up from repo secrets automatically. no env block needed. |

## Common tweaks

- **Schedule it.** Add a `schedule:` block to the `on:` frontmatter section (note: GitHub `schedule:` only fires on the default branch).
- **Add Slack output.** Add `safe-outputs: { create-pull-request: ... }` for self-heal PRs, or include `SLACK_BOT_TOKEN` env + a final step that posts to Slack.
- **Tighten the network allow-list.** The default allows `defaults`, `node`, `github`, plus `api.hud.io` / `cdn.hud.io` (the latter for runtime resources fetched by `hud-mcp@v2`. *not* for the legacy `mcp-linux-x64` download path documented as wrong in [`docs/auth.md`](../../docs/auth.md)). Remove anything you don't need.
- **Adjust timeout.** Default is 30 minutes. Bump for long analysis runs.

## Reference examples

- [Weekly report](../../examples/weekly-report-gh-aw/). a full multi-phase analysis workflow with Slack output and self-heal.
