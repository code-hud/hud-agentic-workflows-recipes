# Team Splitting — GitHub Teams

Gate workflow execution on whether the actor (PR author, dispatcher) is an active member of a specific GitHub Team.

## Files

| Path | Purpose |
|---|---|
| `lookup.yml` | A drop-in `check-membership` job snippet for GitHub Actions |

## How to use

### 1. Add the job to your workflow

Copy the `check-membership:` job from `lookup.yml` into your workflow's `jobs:` block. Set `TEAM_SLUG` to your team's slug (the URL-friendly name, e.g. `platform` for `https://github.com/orgs/<org>/teams/platform`).

### 2. Gate your downstream jobs on the output

```yaml
my-actual-job:
  needs: check-membership
  if: needs.check-membership.outputs.is-authorized == 'true'
  runs-on: ubuntu-latest
  steps:
    - ...
```

### 3. Add the secret

| Secret | Where it comes from |
|---|---|
| `TEAM_READ_TOKEN` | A GitHub PAT (or fine-grained PAT, or GitHub App installation token) with `read:org` scope |

A fine-grained PAT scoped to "Read members of organization" is the cleanest option. For long-lived setups, prefer a GitHub App over a PAT.

## What the snippet does

- On `workflow_dispatch`, always allow — assumes a maintainer is triggering manually.
- Resolves the PR author (`github.event.pull_request.user.login`).
- Calls `GET /orgs/{org}/teams/{team_slug}/memberships/{username}` via `gh api`.
- Sets the job output `is-authorized` to `"true"` if the actor's membership state is `active`, else `"false"`.

## When it breaks

- **PAT expires.** Use a GitHub App token or a fine-grained PAT with a long expiry; alert when it's near expiration.
- **Team slug changes.** GitHub renames the slug if you rename the team in the UI. Worth a periodic sanity check.
- **Pending memberships.** The check requires `state = active`. Pending invites are denied. Adjust if your org wants pending invites to count.
- **Forks.** PRs from forks won't have a meaningful `user.login` for org-internal team checks. If you accept fork PRs, you'll need a different gating strategy.

## When to pick this pattern

- Your org already uses GitHub Teams as the source of truth for ownership.
- You want gating to follow real org membership changes automatically (no config file to update).
- You're gating on **who can trigger** (actor-based), not **what to analyze** (service-based). For service scoping, prefer [`1-config-file/`](../1-config-file/) or [`3-package-json/`](../3-package-json/).
