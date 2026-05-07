# GitHub Actions + Codex CLI

Minimal GitHub Actions skeleton wired up with Hud MCP and OpenAI Codex CLI. Standard `.yml` workflow, portable to any GitHub repo.

> Looking for Claude Code CLI instead? See [`github-actions-claude/`](../github-actions-claude/).

## How to install

| Step | Action |
|---|---|
| **Copy to your repo** | `.github/workflows/run-agent.yml` → same path |
|  | `.github/actions/hud-codex/action.yml` → same path |
|  | `.github/actions/hud-codex/prompt.txt` → same path |
| **Set secrets (GitHub repo settings → Secrets)** | `HUD_MCP_KEY` - get from Hud dashboard → Settings → MCP keys |
|  | `OPENAI_API_KEY` - get from platform.openai.com |

## Where to put the prompt

Replace the contents of `.github/actions/hud-codex/prompt.txt` with your task prompt. You can grab a ready-made prompt from [`recipes/prompts/`](../../recipes/prompts/) (e.g. `blast-radius.md`, `dead-code-cleanup.md`) or write your own.

Alternatively, pass an inline prompt via the `task_prompt` workflow input and leave `prompt.txt` as-is.

## Files

| Path | Purpose |
|---|---|
| `.github/workflows/run-agent.yml` | The workflow: manual dispatch, with commented-out PR / cron triggers |
| `.github/actions/hud-codex/action.yml` | Composite action: installs Codex CLI, configures Hud MCP (`config.toml`), runs the prompt |
| `.github/actions/hud-codex/prompt.txt` | Default task prompt (used when no inline prompt is passed) |

## Setup

1. Copy all three files into your repo at the same paths.
2. Add `HUD_MCP_KEY` and `OPENAI_API_KEY` as repo secrets.
3. Replace `prompt.txt` with your prompt (see above).
4. Run the workflow manually (Actions → Hud Agent → Run workflow) for first verification.

## Common tweaks

- **Run on PRs.** Uncomment the `pull_request_target` trigger in `run-agent.yml`.
- **Run on a schedule.** Uncomment the `schedule:` trigger. Cron only fires on the default branch.
- **Use a different model.** Pass `model: 'o3'` (or `o4-mini`, `gpt-4.1`) on the action call.
