# GitHub Actions Template

Minimal GitHub Actions skeleton wired up with Hud MCP. Standard `.yml` workflows, portable to any GitHub repo.

Ships with two agent CLIs out of the box. Pick one:

| CLI | Action path | Model API key |
|---|---|---|
| **Claude Code** (Anthropic) | `.github/actions/hud-claude/` | `ANTHROPIC_API_KEY` |
| **Codex** (OpenAI) | `.github/actions/hud-codex/` | `OPENAI_API_KEY` |

Both actions wire up the Hud MCP server the same way. The prompt file (`prompt.txt`) is identical and interchangeable.

## How to install

### Option A: Claude Code CLI

| Step | Action |
|---|---|
| **Copy to your repo** | `.github/workflows/run-agent.yml` → same path |
|  | `.github/actions/hud-claude/action.yml` → same path |
|  | `.github/actions/hud-claude/prompt.txt` → same path |
| **Set secrets (GitHub repo settings → Secrets)** | `HUD_MCP_KEY` - get from Hud dashboard → Settings → MCP keys |
|  | `ANTHROPIC_API_KEY` - get from console.anthropic.com (or [Bedrock](../../docs/auth.md)) |

### Option B: Codex CLI

| Step | Action |
|---|---|
| **Copy to your repo** | `.github/workflows/run-agent.yml` → same path |
|  | `.github/actions/hud-codex/action.yml` → same path |
|  | `.github/actions/hud-codex/prompt.txt` → same path |
| **Set secrets (GitHub repo settings → Secrets)** | `HUD_MCP_KEY` - get from Hud dashboard → Settings → MCP keys |
|  | `OPENAI_API_KEY` - get from platform.openai.com |

Then edit `run-agent.yml`: comment out Option A, uncomment Option B (both are in the file).

## Files

| Path | Purpose |
|---|---|
| `.github/workflows/run-agent.yml` | The workflow. Manual dispatch, with commented-out PR / cron triggers. Contains both CLI options. |
| `.github/actions/hud-claude/action.yml` | Composite action: installs Claude Code CLI, configures Hud MCP (`.mcp.json`), runs a prompt |
| `.github/actions/hud-claude/prompt.txt` | Default task prompt for Claude |
| `.github/actions/hud-codex/action.yml` | Composite action: installs Codex CLI, configures Hud MCP (`config.toml`), runs a prompt |
| `.github/actions/hud-codex/prompt.txt` | Default task prompt for Codex |

## Where to put the prompt

Replace the contents of `prompt.txt` (in whichever action you chose) with your task prompt. You can grab a ready-made prompt from [`recipes/prompts/`](../../recipes/prompts/) (e.g. `blast-radius.md`, `dead-code-cleanup.md`) or write your own.

Alternatively, pass an inline prompt via the `task_prompt` workflow input and leave `prompt.txt` as-is.

## Setup

1. Copy the workflow + your chosen action into your repo at the same paths.
2. Add `HUD_MCP_KEY` + your CLI's API key as repo secrets.
3. If using Codex, edit `run-agent.yml` to uncomment Option B and comment out Option A.
4. Replace `prompt.txt` with your prompt (see above).
5. Run the workflow manually (Actions → Hud Agent → Run workflow) for first verification.

## Common tweaks

- **Run on PRs.** Uncomment the `pull_request_target` trigger in `run-agent.yml`. Add scope filters (`branches:`, `paths:`) as needed.
- **Run on a schedule.** Uncomment the `schedule:` trigger. Cron only fires on the default branch.
- **Use a different model.** Pass `model:` on the action call (Claude: `sonnet`, `opus`, `haiku`; Codex: `o4-mini`, `o3`, `gpt-4.1`).
- **Use Bedrock (Claude only).** Add the AWS credentials step (commented in `run-agent.yml`), drop `anthropic-api-key`, and set env vars: `CLAUDE_CODE_USE_BEDROCK: '1'`, `AWS_REGION`, `ANTHROPIC_MODEL`. See [`docs/auth.md`](../../docs/auth.md).

## Reference examples

- [Blast radius](../../examples/blast-radius-github-actions/) - production example with PR-comment output, scoring rubric, and diff handling (uses Claude Code CLI).
