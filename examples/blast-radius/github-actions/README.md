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
| `lookback-days` | `7` | Increase if your prod traffic is bursty week-over-week |
| `max-functions` | `80` | Raise for very large monorepos |
| `comment-on-pr` | `true` | Set `false` to gate via the score output instead of comments |
| `weight-*` | various | Re-tune the scoring rubric for your team's risk profile |

See `action.yml` for the full input list.

## Verify it works

1. Add `HUD_MCP_KEY` + `ANTHROPIC_API_KEY` as repo secrets.
2. Drop the three files into your repo.
3. Open a test PR that modifies a file with known production traffic.
4. Check that the workflow runs and posts a comment within ~2-3 minutes.

## Bedrock alternative

If you're routing Claude via AWS Bedrock instead of the Anthropic API:

1. Add `permissions.id-token: write` to the workflow.
2. Add an `aws-actions/configure-aws-credentials@v4` step before the action call (template commented in `pr-blast-radius.yml`).
3. Replace the `anthropic-api-key` input with env vars: `CLAUDE_CODE_USE_BEDROCK: '1'`, `AWS_REGION: us-west-2`, `ANTHROPIC_MODEL: 'anthropic.claude-sonnet-4-5-v2:0'`.
4. Replace the `ANTHROPIC_API_KEY` secret with `AWS_ROLE_TO_ASSUME` (IAM role with `bedrock:InvokeModel` permission).

See [`docs/auth.md`](../../../docs/auth.md) for the full Bedrock setup.

## Scope-gating variants

The default workflow runs on every PR to `main`. Common variants:

- **Team-only** — gate by GitHub team membership. See [`recipes/team-splitting/2-github-teams/`](../../../recipes/team-splitting/2-github-teams/).
- **Label-only** — only run when a specific label is set. Add a `check-label` job before `blast-radius`.
- **Path-only** — uncomment the `paths:` filter on `pull_request_target`.
