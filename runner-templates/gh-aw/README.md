# gh-aw Template

Minimal [gh-aw](https://github.github.com/gh-aw/) agent skeleton: Hud MCP + Claude engine, no task. Drop your task description in and ship.

## Prerequisites

Install the gh-aw CLI extension (one-time):

```bash
gh extension install github/gh-aw
```

Initialize your repo for agentic workflows (one-time per repo):

```bash
gh aw init
```

This sets up `.gitattributes`, the dispatcher agent, and other scaffolding. See the [gh-aw quick start](https://github.github.com/gh-aw/setup/quick-start/) for details.

## How to install

| Step | Action |
|---|---|
| **Copy to your repo** | Copy `.github/workflows/agent.md` into your repo at `.github/workflows/agent.md` |
| **Replace the prompt** | Open `agent.md` and replace the `## Task` section with your prompt |
| **Compile** | `gh aw compile` |
| **Commit** | Commit both `agent.md` and the generated `agent.lock.yml` |
| **Set secrets** | `HUD_MCP_KEY` - get from Hud dashboard → Settings → MCP keys |
|  | `ANTHROPIC_API_KEY` - get from console.anthropic.com (or [Bedrock](../../docs/auth.md)) |
| **Push and run** | `git push` then `gh aw run agent` to test |

Or scaffold from scratch instead of copying: `gh aw new my-workflow --engine claude`

## Files

| Path | Purpose |
|---|---|
| `.github/workflows/agent.md` | The gh-aw workflow: frontmatter (config) + body (agent prompt) |

## How a gh-aw workflow file works

A gh-aw workflow is a single `.md` file with two parts:

```markdown
---
# Frontmatter: YAML config block between --- markers.
# This is the workflow configuration — triggers, permissions,
# env vars, MCP servers, network rules, tools, etc.
name: my-workflow
engine: claude
on:
  workflow_dispatch:
env:
  MY_VAR: "value"
mcp-servers:
  hud-mcp:
    command: "npx"
    args: ["-y", "hud-mcp@v2"]
    env:
      HUD_MCP_KEY: "${{ secrets.HUD_MCP_KEY }}"
---

# Body: the agent prompt.
# Everything below the second --- is what the AI agent reads and executes.

## Task
Describe what the agent should do here.
```

`gh aw compile` reads the frontmatter and generates a full GitHub Actions `.lock.yml` from it. The body becomes the agent's instructions.

For the full frontmatter reference, see the [gh-aw docs](https://github.github.com/gh-aw/setup/creating-workflows/).

## Where to put the prompt

Open `.github/workflows/agent.md` and replace the `## Task` section with your task prompt. You can grab a ready-made prompt from [`task-recipes/prompts/`](../../task-recipes/prompts/) (e.g. `weekly-report/main.md`, `rollback-check.md`) or write your own.

### Simple prompts (single file)

For prompts like `blast-radius.md` or `rollback-check.md`: paste the prompt into the body section. No frontmatter changes needed beyond what the template already provides.

### Complex prompts (multiple files, extra env vars)

Prompts like `weekly-report/` need additional setup:

1. **Check the prompt's env var table.** Add any required variables to the `env:` block in the frontmatter.
2. **Copy supporting files.** If the prompt references files (e.g. `deep-insights/*.txt`), copy them alongside the workflow at the path the prompt expects.
3. **Add secrets.** If the prompt needs secrets beyond `HUD_MCP_KEY` and `ANTHROPIC_API_KEY` (e.g. `SLACK_BOT_TOKEN`), add them as repo secrets and reference them in the `env:` block.
4. **Add network rules.** If the prompt calls external APIs (e.g. Slack), add the domains to the `network.allowed` list.
5. **Add safe-outputs.** If the prompt creates PRs, add the appropriate `safe-outputs` block.

See the prompt's README for specific instructions, or check the [weekly report example](../../full-examples/weekly-report-gh-aw/) for a fully worked complex workflow.

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
| `ANTHROPIC_API_KEY` | console.anthropic.com (or [`docs/auth.md`](../../docs/auth.md) for the Bedrock variant). The `engine: claude` line in the workflow frontmatter picks this up from repo secrets automatically — no env block needed. |

## Common tweaks

- **Schedule it.** Add a `schedule:` block to the `on:` frontmatter section (note: GitHub `schedule:` only fires on the default branch).
- **Add Slack output.** Include `SLACK_BOT_TOKEN` in env + add `api.slack.com` and `slack.com` to the network allow-list.
- **Self-heal PRs.** Add `safe-outputs: { create-pull-request: { draft: true } }` to the frontmatter.
- **Tighten the network allow-list.** The default allows `defaults`, `node`, `github`, plus `api.hud.io` / `cdn.hud.io`. Remove anything you don't need.
- **Adjust timeout.** Default is 30 minutes. Bump for long analysis runs.

## Useful CLI commands

| Command | What it does |
|---|---|
| `gh aw new my-workflow --engine claude` | Scaffold a new workflow file |
| `gh aw compile` | Generate `.lock.yml` from the `.md` file |
| `gh aw validate` | Validate without generating lock files |
| `gh aw run weekly-report` | Trigger a workflow run immediately |
| `gh aw secrets set` | Set repo secrets from the CLI |
| `gh aw mcp add workflow-name server-name` | Add an MCP server from the registry |
| `gh aw logs` | Download and analyze workflow run logs |

Full CLI reference: [gh-aw CLI docs](https://github.github.com/gh-aw/setup/cli/)

## Reference examples

- [Weekly report](../../full-examples/weekly-report-gh-aw/) — full multi-phase analysis workflow with Slack output and self-heal.
