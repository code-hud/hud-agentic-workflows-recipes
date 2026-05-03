# Glossary

Quick definitions for terms that recur across this repo.

## Agent shapes

**Agentic workflow** — a workflow where an LLM (Claude, in our case) makes decisions and takes actions, vs. a deterministic script. Concretely: any workflow where the LLM is in the loop reading data, deciding what to do, and producing output (PR, message, file change).

**MCP (Model Context Protocol)** — Anthropic's open protocol for giving an LLM access to external tools and data. The Hud MCP server lets Claude run SQL queries against your production runtime data.

**MCP server** — a process that exposes tools and data to an LLM via MCP. We always invoke Hud's via `npx -y hud-mcp@v2` with `HUD_MCP_KEY` in env.

## Platforms

**GitHub Actions** — the standard `.yml` workflow format. Stable, portable, runs on GitHub's runners.

**gh-aw (GitHub Agentic Workflows)** — a markdown-flavored workflow format that compiles down to GitHub Actions. The `.md` file holds frontmatter + agent prompt; running `gh aw compile` produces a `.lock.yml` you commit alongside. Best for workflows where the prompt *is* the workflow.

**Cursor Cloud Agents (formerly Background Agents)** — Cursor's hosted agent runtime. Configured via the dashboard UI; prompts are pasted in. Repo files can declare MCP servers (`.cursor/mcp.json`) and hooks (`.cursor/hooks.json`), but agent prompts themselves don't have a fixed repo path.

**Claude routine** — umbrella term for two shapes: a Claude Code **skill** (`.claude/skills/<name>/SKILL.md`) for on-demand local invocation, or a **scheduled remote task** (registered via `mcp__scheduled-tasks__create_scheduled_task`) for cron-driven cloud execution. Both run the same prompt; only the wrapper differs.

## Hud concepts

**Service** — a logical unit of code Hud is instrumenting. Usually a single deployable (one Docker image or process). A repo can have many services.

**Function** — a named function tracked by Hud, identified by `function_id`. Functions belong to one or more services (`services` is an array column on the `Functions` table).

**Endpoint** — an HTTP route, queue handler, scheduled job, or other entry point Hud groups by. Identified by `endpoint_id`.

**Forensic** — a captured trace of one execution: the call chain, args, outbound calls, errors, timing. Fetched via `hud-get-forensics`.

**Fingerprint** — a stable identifier for a class of error (similar to a Sentry fingerprint). `fingerprint` (singular String) is on `Forensics`; `fingerprints` (plural Map) on metrics tables.

**`session_tags`** — a free-form `Map(String, String)` on metric and forensic rows where SDK-side tags land (e.g. `service_version`, `tenant_id`, `region`). Read with `session_tags['key']`.

**Environment** — a top-level dimension that separates production from staging from dev. Always query with `environment_name = 'production'` for these workflows.

**Tag** — set via `setTag(key, value)` from the SDK; lands in `session_tags`. Use for cross-environment dimensions (region, deployment color, A/B group).

**`includeModules` / `excludeDirs`** — SDK config knobs. `includeModules` opts an internal library *into* instrumentation (the SDK only auto-instruments your own code by default). `excludeDirs` opts directories *out* (e.g. third-party scripts checked into your repo).

**Workspace** — a Hud workspace is the top-level account boundary. Maps roughly 1:1 to a customer org. The MCP defaults to `WORKSPACE_NAME_KEY = github.repository`.

## Workflow concepts

**Composite action** — a GitHub Action that wraps multiple steps into one reusable block. Lives at `.github/actions/<name>/action.yml`. Used in `examples/blast-radius/github-actions/` and `templates/github-actions/` to encapsulate "install Claude + write MCP config + run prompt."

**Self-heal** — a workflow that, after detecting an issue, applies a fix and opens a PR. The `weekly-report` example does this in Phase 5: pick the highest-scoring fix, edit the files, let `safe-outputs.create-pull-request` open the PR.

**Blast radius (the score)** — a 0–100 score combining how heavily-trafficked, latency-sensitive, and error-exposed the touched code is. The `blast-radius` example outputs this number plus a written report.

**Deslop** — a quality-pass step in the weekly-report workflow that merges duplicates, enforces character limits, and removes redundancy from generated content before it goes out.
