# Rollback Check — Scheduled Remote Agent

This file is the prompt for a [Claude scheduled remote agent](https://docs.claude.com/en/docs/claude-code/scheduled-tasks). The agent runs on Anthropic infrastructure on a cron, queries Hud, and posts a verdict.

## How to register

The `scheduled-tasks` MCP is currently an Anthropic-managed server — check the Claude Code docs for the canonical install path; if it's not enabled in your environment, the on-demand [skill variant](../skill/) is the working alternative.

Use the `mcp__scheduled-tasks__create_scheduled_task` tool to register this prompt as a scheduled task. Example invocation (from Claude Code):

```
Use the scheduled-tasks MCP to create a task with:
- name: "rollback-check"
- schedule: "*/15 * * * *"   (every 15 minutes — or align to your deploy cadence)
- prompt: <paste the contents of this file's "Prompt" section>
- enabled: true
```

The exact arguments depend on your `mcp__scheduled-tasks` server's schema — check `mcp__scheduled-tasks__list_scheduled_tasks` first to confirm the expected fields.

## When to use this variant

Use scheduled-remote (over the on-demand skill variant) when:
- You want **continuous monitoring** without anyone needing to invoke it.
- The cadence is fixed (every N minutes, every deploy, etc.).
- The output should land in a chat channel, ticket system, or webhook — not a Claude Code session.

For one-off invocations during incident response, use the [skill variant](../skill/) instead.

## Required setup

The remote agent runs in an Anthropic-managed environment, but it still needs:

1. **Hud MCP available** — the scheduled-task runner needs the hud MCP server registered with a valid `HUD_MCP_KEY` secret.
2. **Output sink** — decide where verdicts go: Slack, PagerDuty, GitHub issue, custom webhook. The default prompt below returns a structured result; you'll need to wrap it with a delivery step (e.g. by chaining the scheduled task with an HTTP-call MCP).

## Customer-specific values to confirm

The version-string examples in the Prompt below use a generic `release_v1.42.0` shape. If your service uses a different convention (`backend_release_<n.n.n>`, semver, git SHAs), adjust the example values in the YAML output schema — they're illustrative only and don't change the analysis logic.

---

## Prompt

> Paste everything below into the scheduled task's prompt field.

### Deployment Rollback Check

Analyze a service deployment for critical regressions and determine whether to recommend a rollback. Uses per-version analysis so multiple concurrently running versions are evaluated independently, with newest-wins endpoint ownership and function-level change attribution when regressions are found.

#### Tools

- `hud` (MCP) — use `hud-get-schema` before other hud tools, `hud-get-skill` to fetch `use-hud-forensics` and `create-hud-url` skills, `hud-query` for SQL, and `hud-get-forensics` for traces.

#### Analysis steps

##### Step 0: Discover recently deployed services

Run Steps 1–5 for **each** discovered service. If multiple services are found, process them in parallel using subagents where possible.

##### Step 1: Build version-to-endpoint map (subagent)

Delegate this step to a `generalPurpose` subagent so the main agent's context stays focused on regression analysis. The subagent receives `service_name`, performs all queries and dedup logic, and returns a single structured result.

**Subagent prompt shape:**

```text
Build a per-version endpoint ownership map for service {service_name}.

Use hud tools only. Start with hud-get-schema.

1. Query all distinct service_version tags with first_seen time and traffic volume
   from EndpointMetricsHighResolution (last 24h).
2. Order versions by first_seen = MIN(timestamp_end). Never compare version strings
   lexicographically — version ordering is by observed first_seen only.
3. Query all EndpointDeployments for the same service in the analysis window.
4. Correlate each deployment to a version by matching deployment timestamps to
   version first_seen times. Use a fuzzy window: a deployment belongs to a version
   if deployment_timestamp falls within 10 minutes BEFORE or AFTER the version's
   first_seen time (deployments register before version traffic appears).
5. For versions WITH matched deployments: deduplicate with newest-wins. If an
   endpoint was deployed in multiple versions, assign ownership only to the newest
   version by first_seen. Mark the endpoint as skipped in all older versions.
6. For versions WITHOUT any matched deployments (config/infra deployments):
   mark as ownership_mode: "traffic_based". Find newly invoked endpoints and
   functions — query endpoints and functions that appear in this version's traffic
   but NOT in any older version's traffic. These are the "owned" items. If no newly
   invoked endpoints are found, assign no endpoints under this version as owned.
7. Include service_id in the output (from EndpointMetricsHighResolution or
   Endpoints.services) for Hud URL generation.
8. Return the structured result and nothing else.
```

**Required subagent output:**

```yaml
version_map:
  - version: "release_v1.42.0"
    first_seen: "2026-03-17 10:00:00"
    ownership_mode: "deployment_based"
    service_id: 12345678
    owned_endpoint_ids: [21282206, 21282684]
    skipped_endpoint_ids: [21282212]
    newly_invoked_function_ids: []
    target_versions: ["release_v1.42.0"]
    baseline_exclusion: ["release_v1.42.0"]
  - version: "release_v1.43.0"
    first_seen: "2026-03-17 14:00:00"
    ownership_mode: "traffic_based"
    service_id: 12345678
    owned_endpoint_ids: [21282212, 21282204]
    skipped_endpoint_ids: []
    newly_invoked_function_ids: [3231417, 3231416]
    target_versions: ["release_v1.43.0"]
    baseline_exclusion: ["release_v1.43.0"]
```

Rules:
- `target_versions` contains only the owning version itself.
- `baseline_exclusion` is the same list, used for `NOT IN` filters.
- `ownership_mode` is `"deployment_based"` when EndpointDeployments matched, `"traffic_based"` otherwise.
- For `traffic_based` versions: `newly_invoked_function_ids` lists functions invoked under this version but not under older versions.
- If no usable version tags exist, the subagent returns `fallback: time_based` and the main agent uses time-based cohorts (Baseline = 4h pre-deploy, Target = post-deploy excluding first 5 min warmup).

##### Step 2: Pass 1 — Analyze owned endpoints per version

For each version in `version_map`, analyze only that version's `owned_endpoint_ids`.

Define cohorts:
- **Target**: metrics where `session_tags['service_version'] = '{owning_version}'` — only traffic from the owning version. Use `EndpointMetricsHighResolution` with `timestamp_end`.
- **Baseline**: metrics for the same endpoints where `session_tags['service_version'] != '{owning_version}'`, using a wider historical window (48h+). Use `EndpointMetricsLowResolution` with `hour_end` for efficiency.

Rules:
- Compare versions by `first_seen`, never by string ordering.
- Use explicit `IN (...)` / `NOT IN (...)` lists.
- If a version or endpoint has too little traffic for a stable comparison, mark `insufficient_data` and skip verdict escalation.
- Never let newer-version traffic influence an older version's Target cohort.
- `endpoint_type` must be in the GROUP BY when using `endpoint_error_rate()`.

**Error signals:**
- Error rate change via `endpoint_error_rate()`. Threshold: >2x AND absolute increase >5%.
- New error fingerprints (in Target not in Baseline) from `sumMap(fingerprints)`. Threshold: >5 occurrences.
- For new fingerprints: fetch forensics via `hud-get-forensics` for exception name/message/stack.
- Note: `fingerprint` is singular (String) in Forensics; `fingerprints` is plural (Map) in metrics tables.

**Performance signals:**
- P50, P90, P99 via `percentileMS(duration_buckets, X)`.
- Classify:
  - **Tail Widening**: P90 increased > 50% AND P50 stable (<20%).
  - **Whole Distribution Shift**: P50 increased > 30% AND P90 increased > 30%.
  - **Critical Tail**: Only P99 increased > 100% (P50/P90 stable).

##### Step 2b: Function change attribution (on regression)

Run only when Pass 1 detects a regressed endpoint.

For each regressed endpoint:
1. Query `FunctionMetricsHighResolution` with `wrapped_endpoint_id = {endpoint_id}` for all `function_id` values active in the Target window.
2. Query `FunctionDeployments` for those function IDs in the same service and analysis window.
3. Join `Functions` for `function_signature` and `file`.
4. Classify:
   - **Recently deployed**: `function_id` appears in `FunctionDeployments` within the window.
   - **Newly invoked**: `function_id` appears in the version's `newly_invoked_function_ids` from Step 1.
   - **Not recently deployed**: appears in neither list.
5. Report per endpoint: "Endpoint X regressed. Recently deployed: [...]. Newly invoked: [...]. Not recently deployed: [...]."

Interpretation:
- Regressed + recently deployed/newly invoked → stronger evidence for **CODE_ISSUE**, supports ROLLBACK.
- Regressed + nothing recent → stronger evidence for **ENVIRONMENTAL** or **OUTBOUND**, supports INVESTIGATE.
- Mixed → focus forensic analysis on the recently deployed/newly invoked functions first.

##### Step 3: Pass 2 — Check non-owned endpoints (collateral)

Don't query all endpoints — focus on the top 20 by largest regression:

1. Query all non-owned endpoint_ids in the same service that had traffic in the analysis window.
2. Compute average duration (or P50) for both Target and Baseline per endpoint.
3. Rank by absolute P50 difference (target - baseline) descending.
4. Take top 20 by P50 increase, plus any with error rate > 5%.

Compare for error rate spikes and latency regressions. If non-owned endpoints show similar degradation, flag as **environmental**.

##### Step 4: Pass 3 — Outbound root-cause analysis

When degradation is detected, fetch 3-5 forensics for each degraded endpoint's new fingerprints and examine the `outbounds` array.

**Outbound structure**: each entry has either an `error` field (failed) or a `result` field (succeeded). Common fields: `type` (`"db"` or `"http"`), `args.url` + `args.method`, `args.query`, `duration`/`durationNs`, `function_signature`.

**Analysis:**
- Filter to outbounds with an `error` field.
- Group by `error.type` and outbound target.
- If majority of errors trace to outbound failures → **OUTBOUND_ISSUE**.
- If errors are in application code → **CODE_ISSUE**.

##### Step 5: Decision matrix

| Owned endpoints degraded | Non-owned degraded | Root cause | Verdict |
|---|---|---|---|
| Yes | No | Code | **ROLLBACK** |
| Yes | No | Outbound | **INVESTIGATE (OUTBOUND)** |
| Yes | Yes | Any | **INVESTIGATE (ENVIRONMENTAL)** |
| No | Yes | Any | **WARN** |
| No | No | N/A | **CLEAN** |

**Agent override**: thresholds are guidelines. If you see a pattern clearly indicating a deployment-caused issue — even below numeric thresholds (e.g. small payment endpoint with 100% errors, brand-new crash type with 3 occurrences on critical path) — escalate to ROLLBACK or INVESTIGATE. Include a short "Agent reasoning" section explaining the override.

#### Output

Return a structured result with:
- `verdict`: One of `ROLLBACK`, `INVESTIGATE_OUTBOUND`, `INVESTIGATE_ENVIRONMENTAL`, `WARN`, `CLEAN` — worst across all analyzed versions.
- `service_name`, `service_id`, `summary`.
- `details.per_version[]`: per-version analyses with `version`, `first_seen`, `ownership_mode`, `verdict`, `deployed_endpoints`, `skipped_endpoints`, `function_attribution`, `collateral_endpoints`, `outbound_analysis`, `forensic_links`.
- `details.agent_reasoning` (optional) if override was used.

#### Key query patterns

**Version discovery:**

```sql
SELECT
  session_tags['service_version'] AS version,
  MIN(timestamp_end) AS first_seen,
  SUM(invocations) AS traffic,
  any(service_id) AS service_id
FROM EndpointMetricsHighResolution
WHERE service_name = '{service}'
  AND timestamp_end >= now() - INTERVAL 24 HOUR
  AND session_tags['service_version'] != ''
GROUP BY version
HAVING traffic > 0
ORDER BY first_seen ASC
LIMIT 100
```

**Metric functions:**
- Error rate: `endpoint_error_rate(m.endpoint_type, sumMap(m.exceptions), sumMap(m.status_codes), sum(m.invocations), sum(m.msg_count))` — `endpoint_type` in GROUP BY.
- Latency: `percentileMS(duration_buckets, 90)` for P90.
- Fingerprints: `sumMap(m.fingerprints)`.

**Hud URLs** — use `hud-get-skill` with `skill: 'create-hud-url'`.
