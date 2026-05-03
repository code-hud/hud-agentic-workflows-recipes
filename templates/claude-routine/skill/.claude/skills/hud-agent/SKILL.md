---
name: hud-agent
description: Use when investigating production behavior, generating reports from runtime data, or auditing code health. Replace the Task section below with the specific use case before shipping.
---

# Hud Agent

A blank skeleton for a Claude Code skill that uses the Hud MCP for production runtime data.

## Tools

- `hud` (MCP) — start with `hud-get-schema` to understand the schema, then use `hud-query` for SQL, `hud-get-forensics` for traces, and `hud-get-skill` to fetch helper skills like `use-hud-forensics` or `create-hud-url`.

## Setup

The user's local Claude Code config must have the Hud MCP registered with `HUD_MCP_KEY`. If not, they can add it via:

```bash
claude mcp add --transport stdio --scope user hud npx -y hud-mcp@v2 -- -e HUD_MCP_KEY=$HUD_MCP_KEY
```

(Or by editing `~/.claude.json` directly.)

## Task

> Replace this section with the actual task description.
>
> Examples:
> - "Compare the current deployment's health to the previous version and recommend rollback / investigate / clean."
> - "List the top 10 functions by error rate in the last 24 hours. For each, fetch a sample forensic and propose a fix."
> - "Audit the repo for dead code — query Hud for functions with zero invocations, run safety checks, propose deletions."
>
> Reference the [examples/](../../../../../../examples/) folder for working patterns.

## Output

Return a structured summary. For incident-response skills, include:
- One-line verdict (e.g. ROLLBACK / INVESTIGATE / CLEAN).
- Evidence (key metrics, fingerprints, function attributions).
- Suggested next action.

For reporting skills, return a markdown table or JSON the user can pipe into another tool.
