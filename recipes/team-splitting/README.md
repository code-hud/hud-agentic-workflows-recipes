# Team Splitting

Three patterns for scoping a workflow by team. Pick one based on where your team-to-service mapping naturally lives.

## Picking between them

| Pattern | Use when | Trade-off |
|---|---|---|
| [`1-config-file/`](1-config-file/) | You want a single source of truth for ownership in a YAML/JSON file checked into the repo | Requires keeping the file in sync with reality |
| [`2-github-teams/`](2-github-teams/) | Your team membership already lives in GitHub Teams and you trust it as the source of truth | Needs a PAT with `read:org` scope; only works for orgs with Teams configured |
| [`3-package-json/`](3-package-json/) | Each service has its own folder with a `package.json` (Node monorepo) | Only works if `package.json` `author` field is reliably populated |

## What "team splitting" usually does in a workflow

In any of the examples in this repo, you might want to:

- **Gate execution** — only run for PRs from team X (blast-radius style).
- **Scope queries** — run the analysis only on team X's services (weekly-report style).
- **Route output** — post each team's report to that team's Slack channel.

These three concerns can use the same team-resolution pattern. The recipes here output a `team → [services]` (or `actor → team`) map; the calling workflow picks how to use it.

## Combining patterns

Nothing stops you from using two at once. For example:
- **GitHub Teams** gates *who can trigger* the workflow (`actor → team`).
- **package.json** scopes *what the workflow analyzes* (`team → [services]`).
- **Config file** overrides specific edge cases (a service whose ownership was recently transferred).
