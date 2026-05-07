# Team Splitting — Config File

Map services and members to teams via a YAML file checked into the repo.

## Files

| Path | Purpose |
|---|---|
| `teams.yaml` | Example mapping — drop into your repo at `.github/teams.yaml` (or wherever) |
| `load-teams.ts` | Reusable loader with env-var filters for CI scoping |

## How to use

### 1. Author your `teams.yaml`

Copy the example, replace with your real teams. Each team can include:

- `display_name` — human-readable name (used in reports / Slack messages)
- `slack_channel` — where to route notifications (optional)
- `services` — list of service names this team owns
- `members` — GitHub usernames (optional, for actor-gating)

### 2. Load it from your workflow

**TypeScript / Node:**

```ts
import { loadTeams, teamForActor, teamForService } from './load-teams';

const teams = loadTeams('.github/teams.yaml');
const team = teamForActor(teams, process.env.GITHUB_ACTOR!);
if (!team) {
  console.error(`No team membership for ${process.env.GITHUB_ACTOR}`);
  process.exit(1);
}
console.log(`Running for team ${team}`);
```

**From a GitHub Actions step (no Node):**

```yaml
- name: Resolve team
  id: team
  shell: bash
  run: |
    set -euo pipefail
    TEAM=$(yq -r ".. | select(.members) | select(.members[] == \"$GITHUB_ACTOR\") | path | .[0]" .github/teams.yaml | head -1)
    if [ -z "$TEAM" ]; then
      echo "No team for $GITHUB_ACTOR"
      exit 1
    fi
    echo "team=$TEAM" >> "$GITHUB_OUTPUT"
```

### 3. CI scoping via env vars

The TS loader honors:

| Env var | Effect |
|---|---|
| `HUD_TEAMS` | Comma-separated team keys to include (skip everything else) |
| `HUD_SERVICES` | Comma-separated service names to include (filters within each team) |

These slot in nicely with the workflow inputs in [`examples/weekly-report-gh-aw/`](../../../examples/weekly-report-gh-aw/).

## When it breaks

- **The file goes stale.** Common failure mode for static config. Mitigate with a CI lint that asserts every service in `apps/*` exists in `teams.yaml`, or invert the relationship and use the [`3-package-json/`](../3-package-json/) pattern.
- **A service ships before being added.** Treat unmapped services as a build failure (or route them to a default team).

## When to pick this pattern

- You don't have GitHub Teams set up (or can't trust them as source of truth).
- Your service-to-team mapping involves nuance the file system can't capture (e.g. a service is co-owned).
- You want one obvious place to look for "who owns X."
