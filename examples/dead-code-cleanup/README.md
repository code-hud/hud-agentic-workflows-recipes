# Dead Code Cleanup

> Find zero-traffic functions, open a Jira ticket, and ship a PR removing them.

Most codebases accumulate dead code at the rate of feature work. Most teams know they should clean it up but never quite get around to it. This workflow uses Hud's production runtime data to find functions with zero invocations over the last 60 days, runs safety checks (don't delete framework hooks, public APIs, dynamic references, etc.), and ships the cleanup as an automated PR.

## Why teams use it

- **Lower review burden** — engineers come back from vacation to a PR that says "delete these 12 unused helpers" with proof from production.
- **Continuous, not heroic** — runs weekly. Avoids the dreaded "let's spend a quarter cleaning up tech debt" project.
- **Safer than IDE-based dead-code finders** — uses runtime traffic, not static analysis. Catches dynamically-dispatched code IDE tools miss, and avoids false positives from reflection-based frameworks.

## Available platforms

| Platform | Path | Notes |
|---|---|---|
| Cursor (Cloud Agent) | [`cursor/`](cursor/) | Manual trigger via Cursor dashboard. Opens Jira ticket + non-draft PR. |

## Adapting it to your team

- **No platform-inventory manifest?** See the alternative service-discovery options in the cursor README.
- **Different Jira project / no Jira at all?** Strip the Jira section from the agent prompt; the workflow still works PR-only.
- **Different `LOOKBACK_DAYS`?** 60 is the default; some teams prefer 90 to avoid catching seasonal code.
