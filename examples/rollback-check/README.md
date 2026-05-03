# Rollback Check

> Compare current vs. previous release health and recommend rollback / investigate / clean.

After a deploy, the question every SRE asks is "should I roll this back?" Most teams answer it by squinting at dashboards. This routine answers it by:

1. Identifying which endpoints belong to the new version (deployment-based or, for config-only deploys, traffic-based).
2. Comparing each endpoint's error rate, P50/P90/P99, and error fingerprints against a 48-hour baseline of the same endpoints on prior versions.
3. Tracing regressed endpoints to recently deployed or newly invoked functions to localize blame.
4. Checking non-owned endpoints for collateral (= environmental, not the new code's fault).
5. Examining outbound failures to distinguish CODE_ISSUE vs OUTBOUND_ISSUE.
6. Returning a verdict on a five-level scale: ROLLBACK / INVESTIGATE_OUTBOUND / INVESTIGATE_ENVIRONMENTAL / WARN / CLEAN.

## Why teams use it

- **Faster rollback decisions.** "Should we roll back?" gets a structured answer in seconds, not 20 minutes of dashboard digging.
- **Reduces false-positive rollbacks.** Distinguishes between code regressions (rollback-worthy) and environmental issues (rolling back won't help).
- **Function-level attribution** — when a regression is found, points at the specific functions that were deployed or newly invoked, so the on-call has a starting point.

## Available platforms

| Platform | Path | Notes |
|---|---|---|
| Claude Code skill | [`claude-routine/skill/`](claude-routine/skill/) | On-demand, local. Engineer or SRE invokes from a Claude Code session. |
| Scheduled remote agent | [`claude-routine/scheduled-remote/`](claude-routine/scheduled-remote/) | Continuous, runs on a cron. Posts verdicts to Slack / PagerDuty / webhook. |

Both shapes use the same analysis logic; only the wrapper differs. See [`claude-routine/README.md`](claude-routine/README.md) for picking between them.

## Adapting it to your team

- **Different version-tag convention?** The version-discovery query reads `session_tags['service_version']`. Replace with whatever tag your services emit (e.g. `git_sha`, `release_id`).
- **No deployment events in Hud?** The workflow falls back to traffic-based ownership (newly-invoked endpoints/functions per version) and time-based cohorts. No config changes needed.
- **Different verdict thresholds?** Edit the Step 5 decision matrix. The `Agent override` section already permits escalation outside the numeric thresholds when patterns warrant it.
- **Different output sink (not Slack)?** For the scheduled-remote variant, swap the delivery step. The structured `verdict` JSON is platform-agnostic.
