# Blast Radius — GitHub Actions

A composite GitHub Action that analyzes the blast radius of a pull request using Hud production runtime data and posts the result as a PR comment.

## What it does

On every PR (or manual dispatch), the action:

1. Resolves the PR number and pulls the diff (with a 350 KB cap and graceful fallback for large diffs).
2. Cross-references touched code against Hud's production traffic data — invocations, traffic share, latency sensitivity, error rates, distinct endpoint counts.
3. Asks Claude to score the change on a weighted blast-radius rubric and write a markdown report.
4. Posts the report as a PR comment (configurable).
5. Surfaces a numeric `blast-radius-score` output (0–100) for downstream gating.

If the PR touches no Hud-tracked functions, the action exits gracefully without commenting.

## Files

| Path | Purpose |
|---|---|
| `.github/workflows/pr-blast-radius.yml` | Thin workflow that triggers on PR + dispatches and calls the action |
| `.github/actions/blast-radius/action.yml` | Composite action — installs Claude CLI, sets up MCP, runs the analysis |
| `.github/actions/blast-radius/blast-radius-prompt.txt` | The analysis prompt fed to Claude |

Drop these into your customer repo at the same paths.

## Required secrets

| Secret | Where it comes from |
|---|---|
| `HUD_MCP_KEY` | Hud dashboard → Settings → MCP keys |
| `ANTHROPIC_API_KEY` | console.anthropic.com (or use the Bedrock variant — see below) |

## Workspace name

The action defaults `WORKSPACE_NAME_KEY` to `${{ github.repository }}` (e.g. `org-name/api`). If your Hud workspace was created with a different name, override via the `workspace-name` input or you'll see "no Hud functions found" on every run.

## Required permissions

The workflow needs:

```yaml
permissions:
  contents: read
  pull-requests: write
```

`pull-requests: write` is what lets the action post the PR comment.

## Inputs you might want to tweak

All defaults are sensible. The most common tweaks:

| Input | Default | When to change |
|---|---|---|
| `model` | `opus` | Pass `sonnet`/`haiku` for faster/cheaper runs, or a Bedrock model ID for the Bedrock route |
| `lookback-days` | `7` | Increase if your prod traffic is bursty week-over-week |
| `max-functions` | `80` | Raise for very large monorepos |
| `comment-on-pr` | `true` | Set `false` to gate via the score output instead of comments |
| `weight-*` | various | Re-tune the scoring rubric for your team's risk profile |

See `action.yml` for the full input list.

## Verify it works

1. Add `HUD_MCP_KEY` + `ANTHROPIC_API_KEY` as repo secrets.
2. Drop the three files into your repo.
3. Pick a file with known production traffic — open the Hud dashboard's Functions view, sort by invocations, and grab a top-ranked file. Modify any line in it.
4. Open a test PR. The workflow should run and post a comment within ~2–3 minutes.

## Bedrock alternative

If you're routing Claude via AWS Bedrock instead of the Anthropic API:

1. Add `permissions.id-token: write` to the workflow.
2. Add an `aws-actions/configure-aws-credentials@v4` step before the action call (template commented in `pr-blast-radius.yml`).
3. Set `CLAUDE_CODE_USE_BEDROCK: '1'`, `AWS_REGION: us-west-2`, and `ANTHROPIC_MODEL: 'anthropic.claude-sonnet-4-5-v2:0'` as **job-level** `env:` (commented stub in `pr-blast-radius.yml`). Composite-action inputs don't propagate to the inner Claude CLI step — env does.
4. Pass the Bedrock model ID through the `model` input (e.g. `model: 'anthropic.claude-sonnet-4-5-v2:0'`) and leave `anthropic-api-key:` empty.
5. Replace the `ANTHROPIC_API_KEY` secret with `AWS_ROLE_TO_ASSUME` (IAM role with `bedrock:InvokeModel` permission).

See [`docs/auth.md`](../../../docs/auth.md) for the full Bedrock setup.

## Scope-gating variants

The default workflow runs on every PR to `main`. Common variants:

- **Team-only** — gate by GitHub team membership. See [`recipes/team-splitting/2-github-teams/`](../../../recipes/team-splitting/2-github-teams/).
- **Label-only** — only run when a specific label is set. Add a `check-label` job before `blast-radius`.
- **Path-only** — uncomment the `paths:` filter on `pull_request_target`.
