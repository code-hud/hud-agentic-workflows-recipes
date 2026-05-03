# Dead Code Cleanup — Cursor (Cloud Agent)

A Cursor Cloud Agent that finds zero-traffic functions in production using Hud, opens a Jira ticket, and creates a PR removing them.

## What it does

Triggered manually (or on schedule once Cursor supports it):

1. **Service discovery** — fetches the platform-inventory manifest to find all services running in this repo.
2. **Hud query** — finds local source functions with zero production invocations over the last 60 days, across all services.
3. **File-existence filter** — discards candidates from internal npm packages whose source lives in another repo.
4. **Safety checks** — skips dynamic references, public API exports, framework hooks, interface implementations, event handlers, and test-only code.
5. **Caller-chain trace** — if removing a function would break a caller that's also dead, deletes the chain together.
6. **Jira + PR** — opens a Jira ticket (or references an existing one) and a non-draft PR with the removals. PR is labeled `HUD`.

If no dead code is found, or all candidates are skipped, the run exits cleanly without opening a PR or ticket.

## Files

| Path | Purpose |
|---|---|
| `dead-code-cleaner.md` | The full agent specification — setup section + agent prompt |

Cursor doesn't store agent prompts at a fixed repo path. This file is **documentation** — open it, configure your Cursor automation per the Setup section, paste the Agent Prompt section into the automation field.

## Required secrets / config

| Item | Where it lives | Notes |
|---|---|---|
| `HUD_MCP_KEY` | Hud MCP server config in Cursor | Hud dashboard → Settings → MCP keys |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | Cursor automation env var **and** GitHub MCP env | Org-wide `repo` scope. Must be set at the automation level (not just the MCP) for shell `curl` to use it. |
| Atlassian integration | Cursor's built-in Atlassian app | Just enable; no extra config |

## Customer-specific values to replace

Before pasting the prompt into Cursor, search-and-replace:

| Placeholder | Replace with |
|---|---|
| `org-name` | Your GitHub org slug |
| `dimensions/org-name` | Your service-inventory path |
| `org-name.atlassian.net` | Your Jira host |
| `ORG` (Jira project key) | Your Jira project key |
| `BASE_BRANCH: master` | Your default branch (commonly `main`) |

Also confirm the fixed-value inputs at the top of the agent prompt match your conventions:

- `JIRA_PROJECT_KEY`
- `LOOKBACK_DAYS` (default: 60)
- `BASE_BRANCH` (default: `master` — change to `main` for most repos)
- `MAX_LINES_CHANGED` (default: 300)

## Verify it works

1. Configure all three MCP servers in Cursor's dashboard.
2. Add `GITHUB_PERSONAL_ACCESS_TOKEN` as an automation-level env var.
3. Create a new Cursor automation, paste the Agent Prompt section in.
4. Set output → "Open Pull Request" (uncheck Draft).
5. Run on a repo that's instrumented by Hud and has at least 60 days of production data. Expect either a clean exit ("no dead code found") or a PR within a few minutes.

## Why this requires the platform-inventory manifest

The agent needs the list of service names this repo deploys to in order to query Hud. If your org doesn't have a platform-inventory manifest, replace the Service Discovery section with an alternative:

- Hardcode `SERVICE_NAMES` if it's a single-service repo.
- Read from `package.json` per-service folder (see [`recipes/team-splitting/3-package-json/`](../../../recipes/team-splitting/3-package-json/) for a related pattern).
- Read from a static config file (see [`recipes/team-splitting/1-config-file/`](../../../recipes/team-splitting/1-config-file/)).
