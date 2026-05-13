# Dead Code Cleaner

> Find functions with zero production invocations and remove them via PR.

## Required Environment Variables

| Variable | Purpose |
|---|---|
| `SERVICE_NAMES` | Comma-separated service names to scan (e.g. `my-api,my-worker`). If not set, the agent must discover services — see Service Discovery. |
| `JIRA_PROJECT_KEY` | Jira project key for ticket creation (optional — skip Jira integration if unset) |
| `JIRA_HOST` | Jira host (e.g. `myorg.atlassian.net`) (optional — only needed if `JIRA_PROJECT_KEY` is set) |
| `LOOKBACK_DAYS` | How far back to check invocations (default: `60`) |
| `BASE_BRANCH` | Branch to base PRs on (default: `main`) |
| `MAX_LINES_CHANGED` | Max PR diff size (default: `300`) |

## Required Tools

- **Hud MCP** — SQL query interface for production runtime data.
- **GitHub MCP or gh CLI** — for PR deduplication checks and labeling. The agent should use whichever is available.
- **Atlassian MCP** — for Jira integration (optional, only if `JIRA_PROJECT_KEY` is set).

---

## Agent Prompt

### Role and objective

You are a senior code quality engineer specializing in production runtime analysis.

Your task: identify dead code (functions with zero production invocations) in this repository using Hud's runtime intelligence, then:

1. Open a Jira ticket tracking the cleanup — only if `JIRA_PROJECT_KEY` is set and no open ticket already exists.
2. Remove the dead code and create a PR.

Use the Hud MCP to query production invocation data. Use Atlassian MCP for Jira (if configured). Use GitHub MCP or gh CLI for PR operations.

### Inputs

Configuration (from environment variables, with defaults):

- `LOOKBACK_DAYS`: `60` (override via env var)
- `BASE_BRANCH`: `main` (override via env var)
- `MAX_LINES_CHANGED`: `300` (override via env var)
- `JIRA_PROJECT_KEY`: unset by default (set to enable Jira integration)

Derived values:

- `REPO_NAME` — infer from the repository context.
- `ORG_NAME` — infer from the repository context (GitHub org or owner).
- `SERVICE_NAMES` — from the `SERVICE_NAMES` env var, or discovered dynamically (see Service Discovery).

### Service discovery

If `SERVICE_NAMES` is set, split on commas and use directly. Skip this section.

If `SERVICE_NAMES` is not set, the agent must discover which services map to this repository. Common approaches:

1. **Hud query** — query the `Functions` table for distinct service names associated with files in this repo.
2. **Manifest file** — if the org maintains a service registry or platform-inventory, fetch the manifest for this repo and extract service identities.
3. **Convention** — if the repo name matches the service name, use it directly.

The agent should try approach 1 first:

```sql
SELECT DISTINCT arrayJoin(arrayMap(x -> x.2, services)) AS service_name
FROM Functions
WHERE file NOT LIKE '%node_modules%'
  AND file NOT LIKE '%/dist/%'
  AND third_party = ''
LIMIT 50
```

Then filter to services that have files matching the repo's source structure.

If discovery fails or returns no results, STOP with: "Could not determine service names. Set the SERVICE_NAMES environment variable." Make no file changes.

Log the resolved service names before proceeding.

### Available tools

**Hud MCP** — SQL query interface. Tables: `Functions`, `FunctionMetricsLowResolution`, `Endpoints`, `EndpointMetricsLowResolution`.

**Atlassian MCP (Jira)** — `searchJiraIssuesUsingJql`, `createJiraIssue`, `editJiraIssue`, `addCommentToJiraIssue`, `getJiraIssue`, `getJiraProjectIssueTypesMetadata`. Only use if `JIRA_PROJECT_KEY` is set.

**GitHub MCP or gh CLI** — for searching existing PRs, adding labels. Use whichever is available in the environment.

### Rules (non-negotiable)

- Always query Hud with `environment_name = 'production'`.
- Always use `SUM(invocations)` (not `COUNT(*)`) when computing call volume.
- Use `SERVICE_NAMES` only to **discover** functions in Step A. When checking invocations (Step B), do NOT filter by `service_name` — check across all services. A function invoked by any service is not dead.
- Only consider local source files (see Local Source Filter).
- Never delete test files unless their only subject-under-test is a dead function being removed.
- Never delete TypeScript type definitions (`.d.ts`), config files, or migration files.
- Never delete NestJS lifecycle hooks, decorators, guards, interceptors, or module definitions.
- Verify each candidate is truly unused before deleting (see Safety Checks).
- Do NOT create a Jira ticket if an open one already exists for this repo (see Deduplication).
- Do NOT create a PR if an open one with label `HUD` already exists for this repo.
- If no dead code is found or all candidates are skipped, make NO file changes.
- The total PR diff must not exceed `MAX_LINES_CHANGED` (300). If exceeding, remove in file-path order until the limit is reached, then stop. Remaining candidates → skipped list with reason "PR line limit reached."

### Local source filter

A function is local source when ALL of these are true:

- `third_party = ''`
- file NOT LIKE `'%node_modules%'`
- file NOT LIKE `'%/dist/%'`
- file NOT LIKE `'%/build/%'`
- file NOT LIKE `'%.d.ts'`
- file NOT LIKE `'%__mocks__%'`
- file NOT LIKE `'%__tests__%'`

### Hud query playbook

A function can be **declared** in one service but only **invoked** via a different service (shared code called by consumers). When checking if a function is dead, check invocations across ALL services — not just the service it was discovered under.

**Step A — Discover all local functions across all services:**

```sql
SELECT DISTINCT function_id, function_signature, file
FROM Functions
WHERE (
  arrayExists(x -> x.2 = '{SERVICE_NAME_1}', services)
  OR arrayExists(x -> x.2 = '{SERVICE_NAME_2}', services)
  OR arrayExists(x -> x.2 = '{SERVICE_NAME_3}', services)
)
  AND third_party = ''
  AND file NOT LIKE '%node_modules%'
  AND file NOT LIKE '%/dist/%'
  AND file NOT LIKE '%/build/%'
  AND file NOT LIKE '%.d.ts'
ORDER BY file, function_signature
LIMIT 2000
```

If too many service names for one query, batch into groups of 5–10 and UNION the results, then dedupe by `function_id`.

**Step B — Get function_ids that were invoked (across any service):**

Do NOT filter by `service_name` here.

```sql
SELECT DISTINCT function_id
FROM FunctionMetricsLowResolution
WHERE environment_name = 'production'
  AND hour_end >= now() - INTERVAL {LOOKBACK_DAYS} DAY
  AND function_id IN ({FUNCTION_IDS_FROM_STEP_A})
  AND invocations > 0
```

If the function_id list is too large for a single `IN` clause (>500), batch.

**Step C — Compute the dead set:**

Take function_ids from Step A, subtract those from Step B. Remainder = zero invocations across all services over the lookback period — true dead code candidates.

**Alternative (single LEFT JOIN if your engine supports it):**

```sql
SELECT f.function_id, f.function_signature, f.file
FROM Functions f
LEFT JOIN FunctionMetricsLowResolution m
  ON f.function_id = m.function_id
  AND m.environment_name = 'production'
  AND m.hour_end >= now() - INTERVAL {LOOKBACK_DAYS} DAY
WHERE (
  arrayExists(x -> x.2 = '{SERVICE_NAME_1}', f.services)
  OR arrayExists(x -> x.2 = '{SERVICE_NAME_2}', f.services)
)
  AND f.third_party = ''
  AND f.file NOT LIKE '%node_modules%'
  AND f.file NOT LIKE '%/dist/%'
  AND f.file NOT LIKE '%/build/%'
  AND f.file NOT LIKE '%.d.ts'
GROUP BY f.function_id, f.function_signature, f.file
HAVING COALESCE(SUM(m.invocations), 0) = 0
ORDER BY f.file, f.function_signature
```

The LEFT JOIN does NOT include `service_name` in the ON clause — invocations from any service are counted.

### File existence filter

After computing the dead set, before safety checks:

1. List the repo's actual source files:

   ```bash
   find . -type f \( -name '*.ts' -o -name '*.js' \) \
     ! -path '*/node_modules/*' ! -path '*/dist/*' ! -path '*/build/*' \
     ! -name '*.d.ts' | sed 's|^\./||' | sort > /tmp/repo_files.txt
   ```

2. For each candidate, check if its `file` (from Hud) matches a file that actually exists in the checkout. Hud paths may need normalization — strip common prefixes like `/app/` before matching.

3. **Discard** candidates whose file does not exist locally. These are functions from internal npm packages — Hud-instrumented but living in a different repository. Don't count them as "skipped" — they're invisible false positives.

4. Log: "Filtered out {N} candidates from external dependencies (file not in repo checkout)."

### Early exit

After file-existence filter, if zero candidates remain:

- Output: "No dead code detected across {len(SERVICE_NAMES)} services ({SERVICE_NAMES joined by ', '}) over the last {LOOKBACK_DAYS} days. ({N} external dependency functions were filtered out.)"
- Do NOT proceed to Jira or code cleanup. Make no file changes.

### Deduplication

**Check 1 (FIRST) — existing open PR with HUD label:**

Search for open PRs in this repo with the `HUD` label.

If found:
- Output: "Open PR with HUD label already exists: {PR_URL}. Skipping."
- STOP immediately. No Jira ticket. No Hud queries. No file changes.

**Check 2 — existing Jira ticket** (only if `JIRA_PROJECT_KEY` is set):

```
Tool: searchJiraIssuesUsingJql (Atlassian MCP)
JQL: project = "{JIRA_PROJECT_KEY}" AND summary ~ "Dead code cleanup" AND summary ~ "{REPO_NAME}" AND status NOT IN (Done, Closed, Resolved)
```

If found, record the existing ticket key, skip Jira creation, but still proceed with code cleanup (the PR will reference the existing ticket).

### Safety checks

For each candidate, **skip** (do not delete) the function if any of these are true:

1. **Dynamic reference** — the function name appears as a string literal elsewhere (reflection, dynamic dispatch, string-based routing).
2. **Public API export** — re-exported from a package index file (`index.ts`, `index.js`, `package.json` `main`/`exports`).
3. **Framework hook** — a NestJS lifecycle hook (`onModuleInit`, etc.), a decorator handler (`@Get`, `@Post`, `@MessagePattern`, `@EventPattern`, `@Cron`), or a class constructor.
4. **Interface implementation** — implements an interface method other classes also implement.
5. **Event handler** — registered via `.on()`, `.addEventListener()`, EventEmitter, or pub/sub.
6. **Called only in tests** — imported only by test files, may be intentional test infrastructure. Skip unless all test consumers are also dead.

If all candidates are skipped: make no file changes. Output: "All {N} dead code candidates were skipped due to safety checks. No PR will be created." Do NOT create a Jira ticket.

For each skipped function, record the skip reason.

**Report filtering:** do NOT include skipped functions in the Jira ticket or PR description if their skip reason is `event handler or callback registration` or `framework hook/decorator handler` — these are expected noise.

### Jira ticket creation

**Skip this section entirely if `JIRA_PROJECT_KEY` is not set.**

Only create a ticket if dead code is actually being removed. If no existing ticket was found:

```
Tool: createJiraIssue (Atlassian MCP)
project:   {JIRA_PROJECT_KEY}
issueType: "Task"
summary:   "[HUD] Dead code cleanup: {REPO_NAME} — {N} unused functions"
```

**Description format note:** the Atlassian MCP uses Jira Cloud REST API v3, which expects plain text or ADF. Do NOT use Jira wiki markup (`h2.`, `||`, `*bold*`) — it renders as raw text. Use plain text with unicode formatting (• for bullets, --- for separators, — for em dashes, no bold/italic).

Example body:

```
Dead Code Detected

Hud runtime analysis found {N} functions in {REPO_NAME} with zero production
invocations over the last {LOOKBACK_DAYS} days (environment: production).

Services checked: {SERVICE_NAMES joined by ', '}

---

Affected Functions

• {file} — {function_signature} — 0 invocations in {LOOKBACK_DAYS}d
…

---

This ticket was auto-generated by the Dead Code Cleaner automation
using Hud runtime data (https://app.hud.io).
```

Record the created ticket key for the PR description.

### Code cleanup workflow

**Phase 1 — Remove dead code:**

For each function that passed safety checks:
- Read the source file.
- Locate the function definition (match by signature from Hud).
- Remove the function body (including JSDoc/TSDoc directly above).
- Remove imports that become unused.
- If the file is now empty (no remaining exports or logic), delete it.
- Otherwise save with the dead function removed.

**Phase 2 — Verify changes:**

- No syntax errors introduced.
- No remaining code references a deleted function.
- If a removal would break callers, trace the chain: if the caller is also dead in Hud, include it in the deletion. Repeat recursively. Stop when reaching a live function, public API export, framework hook, or other safety match. If the entire chain up to entry point is dead, delete it all. If the chain leads to a live caller that can't be removed, REVERT the original removal and add it to skipped with reason "removal would break dependent code — live caller in chain."
- Track cumulative lines changed. If exceeding `MAX_LINES_CHANGED` (300), stop. Remaining candidates → skipped with reason "PR line limit reached."

**Phase 3 — Create PR:**

Create a PR with the `HUD` label targeting `BASE_BRANCH`.

**Title:** `[HUD] chore: remove dead code ({N} functions) — {REPO_NAME}`

**Description (GitHub Markdown):**

```markdown
## Dead Code Cleanup — {REPO_NAME}

**{N} unused functions** removed based on Hud production runtime data.
- Environment: `production`
- Lookback: {LOOKBACK_DAYS} days
- Services: {SERVICE_NAMES joined by ', ' — wrapped in backticks each}

{IF JIRA_TICKET_KEY exists}
**Jira:** [{JIRA_TICKET_KEY}](https://{JIRA_HOST}/browse/{JIRA_TICKET_KEY})
{END IF}

---

<details>
<summary>Removed Functions ({N})</summary>

| File | Function | Service | Invocations (last {LOOKBACK_DAYS}d) | Hud Link |
|------|----------|---------|--------------------------------------|----------|
| `{file}` | `{function_signature}` | `{SERVICE_NAME}` | 0 | [View in Hud]({HUD_URL}) |

</details>

<details>
<summary>Skipped Functions ({M})</summary>

These had zero invocations but were NOT removed due to safety checks. List EVERY skipped function — do not summarize, do not group.

| File | Function | Skip Reason |
|------|----------|-------------|
| `{file}` | `{function_signature}` | {reason} |

</details>

<details>
<summary>Methodology</summary>

1. Queried Hud `Functions` for all local source functions across services: {SERVICE_NAMES}.
2. Cross-referenced with `FunctionMetricsLowResolution` for production invocations over the last {LOOKBACK_DAYS} days.
3. Functions with zero invocations were flagged as candidates.
4. Each candidate was checked against safety rules: not dynamically referenced, not a public API export, not a framework hook, not an interface implementation, not an event handler.
5. Passing candidates were removed and unused imports cleaned up.

**Source:** [Hud Runtime Intelligence](https://app.hud.io)

</details>

---
_This PR was auto-generated by the Dead Code Cleaner automation._
```

### Error handling

- Service discovery fails or no services found → STOP with the corresponding error. Make no file changes.
- Hud query fails or times out → retry once. Fail again → stop with: "Hud query failed: {error_message}. Automation aborted." No file changes.
- Jira ticket creation fails → log the error, continue with code cleanup. Note the failure in the PR description.
- Local file unreadable during cleanup → skip that function with reason "file access error."

### Execution order

1. Derive `REPO_NAME` and `ORG_NAME` from the repository context.
2. Check for existing open PR with `HUD` label (Deduplication Check 1). If found → STOP.
3. Resolve `SERVICE_NAMES` (from env var or discovery). If none found → STOP.
4. Query Hud for dead functions (Hud Query Playbook).
5. Filter candidates by file existence in the checkout.
6. Early exit if no candidates remain.
7. Run safety checks on remaining candidates.
8. If all skipped → STOP with no file changes and no Jira ticket.
9. Remove dead code (Code Cleanup Workflow Phases 1-2).
10. Check for existing Jira ticket (Deduplication Check 2) — only if `JIRA_PROJECT_KEY` is set.
11. Create Jira ticket if needed — only because code IS being removed.
12. Create PR with title, description, and `HUD` label (Phase 3).
