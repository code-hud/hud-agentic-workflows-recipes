# Deployment Rollback Check

> Analyze a recent deployment for regressions and recommend ROLLBACK / INVESTIGATE / WARN / CLEAN.

Analyze a service deployment for critical regressions and determine whether to recommend a rollback. Uses per-version analysis so multiple concurrently running versions are evaluated independently, with newest-wins endpoint ownership and function-level change attribution when regressions are found.

## Tools

- `hud` (MCP) — use `hud-get-schema` before other hud tools, `hud-get-skill` to fetch `use-hud-forensics` and `create-hud-url` skills, `hud-query` for SQL, and `hud-get-forensics` for traces.

## Analysis Steps

### Step 0: Discover recently deployed services

Run Steps 1–5 for **each** discovered service. If multiple services are found, process them in parallel using subagents where possible.

### Step 1: Build version-to-endpoint map (subagent)

**Delegate this step to a `generalPurpose` subagent** so the main agent's context stays focused on regression analysis. The subagent receives `service_name`, performs all queries and dedup logic, and returns a single structured result.

**Subagent prompt shape:**

```text
Build a per-version endpoint ownership map for service {service_name}.

Use hud tools only. Start with hud-get-schema.

1. Query all distinct service_version tags with first_seen time and traffic volume
   from EndpointMetricsHighResolution (last 24h).
2. Order versions by first_seen = MIN(timestamp_end). Never compare version strings
   lexicographically -- version ordering is by observed first_seen only.
3. Query all EndpointDeployments for the same service in the analysis window.
4. Correlate each deployment to a version by matching deployment timestamps
   to version first_seen times. Use a fuzzy window: a deployment belongs to a
   version if deployment_timestamp falls within 10 minutes BEFORE or AFTER the version's
   first_seen time (deployments register before version traffic appears).
5. For versions WITH matched deployments:
   Deduplicate with newest-wins: if an endpoint was deployed in multiple versions,
   assign ownership only to the newest version by first_seen. Mark the endpoint
   as skipped in all older versions.
6. For versions WITHOUT any matched deployments (config/infra deployments):
   Mark as ownership_mode: "traffic_based". Find newly invoked endpoints and
   functions — query endpoints and functions that appear in this version's traffic
   but NOT in any older version's traffic. These are the "owned" items.
   If no newly invoked endpoints are found, assign no endpoints
   under this version as owned.
7. Include service_id in the output (from EndpointMetricsHighResolution or
   Endpoints.services) for Hud URL generation.
8. Return the structured result below and nothing else.
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
- `baseline_exclusion` is the same list, used to build `NOT IN` filters.
- `ownership_mode` is `"deployment_based"` when EndpointDeployments matched, `"traffic_based"` when no deployments matched.
- For `traffic_based` versions: `newly_invoked_function_ids` lists functions invoked under this version but not under older versions — prime suspects for config-triggered regressions.
- If no usable version tags exist, the subagent returns `fallback: time_based` and the main agent uses time-based cohorts (Baseline = 4h pre-deploy, Target = post-deploy excluding first 5 min warmup).

### Step 2: Pass 1 — Analyze owned endpoints per version

For each version in `version_map`, analyze only that version's `owned_endpoint_ids`.

Define cohorts as:
- **Target cohort**: metrics where `session_tags['service_version'] = '{owning_version}'` — only traffic from the owning version. Use `EndpointMetricsHighResolution` with `timestamp_end`.
- **Baseline cohort**: metrics for the same endpoints where `session_tags['service_version'] != '{owning_version}'`, using a wider historical window (48h+). Use `EndpointMetricsLowResolution` with `hour_end` for efficiency on this wider window (it has `session_tags` too).

Rules:
- Compare versions by `first_seen`, never by string ordering.
- Use explicit `IN (...)` / `NOT IN (...)` lists — never lexicographic comparison.
- If a version or endpoint has too little traffic for a stable comparison, mark it as `insufficient_data` and skip verdict escalation for that item.
- Never let newer-version traffic influence an older version's Target cohort.
- `endpoint_type` must be in the GROUP BY when using `endpoint_error_rate()` — ClickHouse requires all non-aggregated columns in GROUP BY.

**Error signals:**
- Error rate change via `endpoint_error_rate()`. Threshold: >2x AND absolute increase >5%.
- New error fingerprints (fingerprints in Target not in Baseline) from `sumMap(fingerprints)`. Threshold: >5 occurrences.
- For new fingerprints: fetch forensics via `hud-get-forensics` to get exception name/message/stack.
- Note: `fingerprint` is singular (String) in the `Forensics` table, but `fingerprints` is plural (Map) in metrics tables.

**Performance signals:**
- P50, P90, P99 via `percentileMS(duration_buckets, X)`.
- Classify:
  - **Tail Widening**: P90 increased > 50% AND P50 is stable (increased < 20%).
  - **Whole Distribution Shift**: P50 increased > 30% AND P90 increased > 30%.
  - **Critical Tail**: Only P99 increased > 100% (P50/P90 stable).

### Step 2b: Function change attribution (on regression)

Run this step only when Pass 1 detects a regressed endpoint.

For each regressed endpoint:
1. Query `FunctionMetricsHighResolution` with `wrapped_endpoint_id = {endpoint_id}` to get all `function_id` values active in the Target window.
2. Query `FunctionDeployments` for those function IDs in the same service and analysis window.
3. Join `Functions` for `function_signature` and `file`.
4. Classify:
   - **Recently deployed functions**: `function_id` appears in `FunctionDeployments` within the window.
   - **Newly invoked functions**: `function_id` appears in the version's `newly_invoked_function_ids` from Step 1 (config deployments).
   - **Not recently deployed functions**: `function_id` does NOT appear in either list.
5. Report per endpoint: "Endpoint X regressed. Recently deployed: [A.method(), B.handler()]. Newly invoked: [E.newFunc()]. Not recently deployed: [C.helper(), D.util()]."

Interpretation guidance:
- Regressed endpoint + recently deployed or newly invoked functions → stronger evidence for **CODE_ISSUE**, supports ROLLBACK.
- Regressed endpoint + no recently deployed or newly invoked functions → stronger evidence for **ENVIRONMENTAL** or **OUTBOUND**, supports INVESTIGATE.
- Mixed → focus forensic analysis on the recently deployed and newly invoked functions first.

### Step 3: Pass 2 — Check non-owned endpoints (collateral)

Check non-owned endpoints for collateral damage. Do NOT query all endpoints — focus on the top 20 by largest regression:

1. Query all non-owned endpoint_ids in the same service that had traffic in the analysis window.
2. Compute average duration (or P50) for both Target and Baseline cohorts per endpoint.
3. Rank by absolute P50 difference (target P50 - baseline P50) descending.
4. Take the top 20 by largest P50 increase, plus any with error rate > 5%.

Compare these for:
- Error rate spikes
- Latency regressions

If non-owned endpoints show similar degradation patterns, flag as **environmental** (shared resource, external platform, infrastructure).

### Step 4: Pass 3 — Outbound root-cause analysis

When degradation is detected (in either pass), fetch 3-5 forensics for each degraded endpoint's new fingerprints and examine the `outbounds` array.

**Forensic outbound structure**:
Each forensic has an `outbounds[]` array. Each entry has EITHER:
- `error` field (when the outbound **failed**): contains `error.type` and `error.message` (e.g., `AxiosError`)
- `result` field (when the outbound **succeeded**): contains `result.status_code` and `result.body`

Common outbound fields:
- `type`: `"db"` or `"http"`
- `args.url` + `args.method` (for HTTP outbounds)
- `args.query` (for DB outbounds)
- `duration` / `durationNs`
- `function_signature`

**Analysis logic:**
- Filter to outbounds that have an `error` field (failed external calls).
- Group by `error.type` and outbound target (URL domain for HTTP, table name for DB).
- If the majority of errors trace back to outbound failures, classify as **OUTBOUND_ISSUE**.
- If errors are in application code (no outbound errors, or outbounds succeed but exception happens in the execution flow), classify as **CODE_ISSUE**.

### Step 5: Decision matrix

Apply the decision matrix per analyzed version. Function attribution from Step 2b strengthens the decision but does not override other evidence on its own.

| Owned endpoints degraded | Non-owned degraded | Root cause | Verdict |
|---|---|---|---|
| Yes | No | Code | **ROLLBACK** |
| Yes | No | Outbound | **INVESTIGATE (OUTBOUND)** |
| Yes | Yes | Any | **INVESTIGATE (ENVIRONMENTAL)** |
| No | Yes | Any | **WARN** |
| No | No | N/A | **CLEAN** |

**Agent override**: The thresholds above are guidelines, not hard rules. If you observe a pattern that clearly indicates a deployment-caused issue — even if it falls below the numeric thresholds (e.g., a small but critical endpoint with few invocations showing 100% errors, or a brand-new crash type with only 3 occurrences but on a payment-critical path) — you may escalate to ROLLBACK or INVESTIGATE at your discretion. Include a short "Agent reasoning" section explaining why you escalated despite not meeting the standard thresholds.

## Output

Return a structured result with:
- `verdict`: One of `ROLLBACK`, `INVESTIGATE_OUTBOUND`, `INVESTIGATE_ENVIRONMENTAL`, `WARN`, `CLEAN` — the **worst** verdict across all analyzed versions.
- `service_name`: The evaluated service.
- `service_id`: Numeric service ID for Hud URL generation.
- `summary`: One-line human-readable summary.
- `details`: Object containing:
  - `per_version`: Array of per-version analyses (see below).
  - `agent_reasoning`: (optional) Explanation if agent override was used.

Each `per_version` entry should contain:
- `version`: the version tag.
- `first_seen`: when this version was first observed.
- `ownership_mode`: `"deployment_based"` or `"traffic_based"`.
- `verdict`: per-version verdict.
- `deployed_endpoints`: endpoints owned by this version (after dedup) with error rate, latency, new fingerprints analysis.
- `skipped_endpoints`: endpoints deployed in this version but re-deployed in a newer one.
- `function_attribution`: for each regressed endpoint, lists of `recently_deployed_functions`, `newly_invoked_functions`, and `not_recently_deployed_functions` with signatures and files.
- `collateral_endpoints`: non-owned endpoint degradation signals (top 20 by diff).
- `outbound_analysis`: root-cause classification with evidence.
- `forensic_links`: Array of `{ forensic_id, endpoint, fingerprint }` for Hud URLs.

## Key query patterns

All queries use `hud-query` via the hud MCP. Only non-obvious patterns shown — straightforward table queries (EndpointDeployments, FunctionDeployments, Functions, Forensics) follow directly from the step descriptions above.

**Version discovery** — version tag lives inside `session_tags` map:

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

**Metric functions** — these require specific signatures:
- Error rate: `endpoint_error_rate(m.endpoint_type, sumMap(m.exceptions), sumMap(m.status_codes), sum(m.invocations), sum(m.msg_count))` — `endpoint_type` MUST be in GROUP BY.
- Latency: `percentileMS(duration_buckets, 90)` for P90, etc.
- Fingerprints: `sumMap(m.fingerprints)` — `fingerprints` (plural, Map) in metrics tables vs. `fingerprint` (singular, String) in Forensics.

**Collateral: top 20 non-owned endpoints by P50 diff** — use a CTE to compute per-endpoint P90 in both cohorts, then rank by diff.

**Hud URLs** — use `hud-get-skill` with `skill: 'create-hud-url'` to generate Hud app links for endpoints and functions.
