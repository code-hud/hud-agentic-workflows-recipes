# GitHub Actions + Claude Code CLI

Minimal GitHub Actions skeleton wired up with Hud MCP and Claude Code CLI. Standard `.yml` workflow, portable to any GitHub repo.

> Looking for Codex CLI instead? See [`github-actions-codex/`](../github-actions-codex/).

## How to install

| Step | Action |
|---|---|
| **Copy to your repo** | Copy these files into your repo, keeping the same paths: |
|  | `.github/workflows/run-agent.yml` |
|  | `.github/actions/hud-claude/action.yml` |
|  | `.github/actions/hud-claude/prompt.txt` |
| **Set secrets (GitHub repo settings → Secrets)** | `HUD_MCP_KEY` - get from Hud dashboard → Settings → MCP keys |
|  | `ANTHROPIC_API_KEY` - get from console.anthropic.com (or [Bedrock](../../docs/auth.md)) |

## Where to put the prompt

Replace the contents of `.github/actions/hud-claude/prompt.txt` with your task prompt. You can grab a ready-made prompt from [`task-recipes/prompts/`](../../task-recipes/prompts/) (e.g. `blast-radius.md`, `dead-code-cleanup.md`) or write your own.

Alternatively, pass an inline prompt via the `task_prompt` workflow input and leave `prompt.txt` as-is.

### Complex prompts (multiple files, extra env vars)

Prompts like `weekly-report/` need additional setup beyond replacing `prompt.txt`:

1. **Check the prompt's env var table.** Add any required variables as `env:` in the workflow's agent step, and pass them through the composite action.
2. **Copy supporting files.** If the prompt references files (e.g. `deep-insights/*.txt`), copy them into `.github/actions/hud-claude/` alongside `prompt.txt`, and set `PROMPT_DIR` to point there.
3. **Add secrets.** If the prompt needs secrets beyond `HUD_MCP_KEY` and `ANTHROPIC_API_KEY`, add them as repo secrets and pass them as env vars.
4. **Add triggers.** Uncomment or add the appropriate trigger (`schedule:`, `pull_request_target:`) in `run-agent.yml`.

See the [blast radius example](../../full-examples/blast-radius-github-actions/) for a fully worked complex workflow.

## Files

| Path | Purpose |
|---|---|
| `.github/workflows/run-agent.yml` | The workflow: manual dispatch, with commented-out PR / cron triggers |
| `.github/actions/hud-claude/action.yml` | Composite action: installs Claude Code CLI, configures Hud MCP (`.mcp.json`), runs the prompt |
| `.github/actions/hud-claude/prompt.txt` | Default task prompt (used when no inline prompt is passed) |

## Setup

1. Copy all three files into your repo at the same paths.
2. Add `HUD_MCP_KEY` and `ANTHROPIC_API_KEY` as repo secrets.
3. Replace `prompt.txt` with your prompt (see above).
4. Run the workflow manually (Actions → Hud Agent → Run workflow) for first verification.

## Common tweaks

- **Run on PRs.** Uncomment the `pull_request_target` trigger in `run-agent.yml`.
- **Run on a schedule.** Uncomment the `schedule:` trigger. Cron only fires on the default branch.
- **Use a different model.** Pass `model: 'opus'` (or `sonnet`, `haiku`) on the action call.
- **Use Bedrock.** Add the AWS credentials step (commented in `run-agent.yml`), drop `anthropic-api-key`, and set env vars: `CLAUDE_CODE_USE_BEDROCK: '1'`, `AWS_REGION`, `ANTHROPIC_MODEL`. See [`docs/auth.md`](../../docs/auth.md).

## Reference examples

- [Blast radius](../../full-examples/blast-radius-github-actions/) - production example with PR-comment output, scoring rubric, and diff handling.
