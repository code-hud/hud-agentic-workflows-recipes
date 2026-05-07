# GitHub Actions Template

Minimal GitHub Actions skeleton wired up with Hud MCP. Standard `.yml` workflows. portable to any GitHub repo.

The default composite action uses **Claude Code CLI**, but the pattern is CLI-agnostic. swap in [Codex CLI](https://github.com/openai/codex), [Aider](https://aider.chat), or any agent CLI that reads an MCP config. The Hud MCP setup step is the same regardless of which CLI runs the prompt.

## How to install

| Step | Action |
|---|---|
| **Copy to your repo** | `.github/workflows/run-agent.yml` → same path |
|  | `.github/actions/hud-claude/action.yml` → same path |
|  | `.github/actions/hud-claude/prompt.txt` → same path |
| **Configure in UI** | *(none)* |
| **Set secrets** | `HUD_MCP_KEY`. Hud dashboard → Settings → MCP keys |
|  | `ANTHROPIC_API_KEY`. console.anthropic.com (or [Bedrock](../../docs/auth.md)) |

## Files

| Path | Purpose |
|---|---|
| `.github/workflows/run-agent.yml` | The workflow. manual dispatch, with commented-out PR / cron triggers |
| `.github/actions/hud-claude/action.yml` | Composite action. installs Claude CLI, configures Hud MCP, runs a prompt |
| `.github/actions/hud-claude/prompt.txt` | Default task prompt (used when no inline prompt is passed) |

## Where to put the prompt

Replace the contents of `.github/actions/hud-claude/prompt.txt` with your task prompt. You can grab a ready-made prompt from [`recipes/prompts/`](../../recipes/prompts/) (e.g. `blast-radius.md`, `dead-code-cleanup.md`) or write your own.

Alternatively, pass an inline prompt via the `task_prompt` workflow input and leave `prompt.txt` as-is.

## Setup

1. Copy all three files into your repo at the same paths.
2. Add `HUD_MCP_KEY` and `ANTHROPIC_API_KEY` as repo secrets.
3. Replace `prompt.txt` with your prompt (see above).
4. Run the workflow manually (Actions → Hud Agent → Run workflow) for first verification.

## Required secrets

| Secret | Where it comes from |
|---|---|
| `HUD_MCP_KEY` | Hud dashboard → Settings → MCP keys |
| `ANTHROPIC_API_KEY` | console.anthropic.com (or [`docs/auth.md`](../../docs/auth.md) for Bedrock) |

## Common tweaks

- **Run on PRs.** Uncomment the `pull_request_target` trigger in `run-agent.yml`. Add scope filters (`branches:`, `paths:`) as needed.
- **Run on a schedule.** Uncomment the `schedule:` trigger. Cron only fires on the default branch.
- **Use a different model.** Pass `model: 'opus'` (or any Claude model alias) on the action call.
- **Use Bedrock.** Add the AWS credentials step (commented in `run-agent.yml`), drop `anthropic-api-key`, and set env vars on the action call: `CLAUDE_CODE_USE_BEDROCK: '1'`, `AWS_REGION`, `ANTHROPIC_MODEL`. See [`docs/auth.md`](../../docs/auth.md).
- **Two-step prompt.** If your prompt is long or templated, keep `prompt.txt` for the base + use the `task-prompt` input for per-run overrides.
- **Use a different agent CLI.** Replace the "Install Claude Code CLI" and "Run agent" steps in `action.yml` with your CLI of choice. Keep the "Setup MCP config" step. it writes a standard `.mcp.json` that any MCP-compatible CLI can read.

## Reference examples

- [Blast radius](../../examples/blast-radius-github-actions/). production example with PR-comment output, scoring rubric, and diff handling.
