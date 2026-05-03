# GitHub Actions Template

Minimal GitHub Actions skeleton wired up with Hud MCP and Claude Code CLI. Standard `.yml` workflows — portable to any GitHub repo.

## Files

| Path | Purpose |
|---|---|
| `.github/workflows/run-agent.yml` | The workflow — manual dispatch, with commented-out PR / cron triggers |
| `.github/actions/hud-claude/action.yml` | Composite action — installs Claude CLI, configures Hud MCP, runs a prompt |
| `.github/actions/hud-claude/prompt.txt` | Default task prompt (used when no inline prompt is passed) |

## Setup

1. Copy all three files into your repo at the same paths.
2. Add `HUD_MCP_KEY` and `ANTHROPIC_API_KEY` as repo secrets.
3. Edit `.github/actions/hud-claude/prompt.txt` with your actual task — or pass an inline prompt via the `task_prompt` workflow input.
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

## Reference examples

- [Blast radius](../../examples/blast-radius/github-actions/) — production example with PR-comment output, scoring rubric, and diff handling.
