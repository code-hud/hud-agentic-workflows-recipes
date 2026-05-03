# Blast Radius

> Score the production blast radius of every pull request and post the result as a comment.

When a PR is opened, this workflow asks Hud "what does production look like for the code this PR touches?" and turns the answer into a single 0–100 score plus a written report. Reviewers see at a glance whether they're looking at a one-line tweak to a hot path or a sweeping change to dead code.

## Why teams use it

- Reviewers prioritize attention by score. Risky PRs get more eyes.
- New engineers see the production reality of code they're touching for the first time.
- The score is an output, so you can gate merges, require extra approvers, or slow-roll deploys based on it.

## Available platforms

| Platform | Path | Notes |
|---|---|---|
| GitHub Actions | [`github-actions/`](github-actions/) | Composite action + thin workflow. Posts a PR comment. |

## Adapting it to your team

Common adaptations live as recipes:

- Want to scope by team? See [`recipes/team-splitting/`](../../recipes/team-splitting/).
- Routing through AWS Bedrock instead of Anthropic? See [`docs/auth.md`](../../docs/auth.md).
