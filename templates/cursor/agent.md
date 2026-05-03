# Hud Agent — Cursor Cloud Agent (Template)

This document is a **specification** for a Cursor Cloud Agent. To run it: configure the MCP servers below in Cursor's dashboard, then paste the Agent Prompt section into a new Cursor Automation.

---

## Setup

### 1. MCP servers

Configure in Cursor → Settings → MCP Servers:

**Hud MCP** (custom):

```json
{
  "mcpServers": {
    "Hud-MCP": {
      "command": "npx",
      "args": ["-y", "hud-mcp@v2"],
      "env": {
        "HUD_MCP_KEY": "YOUR_HUD_MCP_KEY"
      }
    }
  }
}
```

Optional: add other MCPs your task needs (GitHub, Atlassian, Slack, etc.) per the same pattern.

### 2. Automation output

Pick the output that matches your task:
- **Open Pull Request** — for tasks that modify code (uncheck "Draft" if you want ready-for-review).
- **Send Message** — for tasks that produce a report (Slack, email).
- **None** — for tasks that just write files or trigger other automations.

### 3. Environment variables

Add any tokens your shell commands need (e.g. `GITHUB_PERSONAL_ACCESS_TOKEN` for `curl` calls) at the automation level — MCP env vars are only available to the MCP process, not your shell.

---

## Agent prompt

> Paste this section into the Cursor Automation prompt field. Replace the `## Task` placeholder with your actual task.

### Role

You are an engineer with access to Hud production runtime data via the `@hud` MCP server. Use Hud to ground your work in actual production behavior — not assumptions.

### Available tools

- **Hud MCP (`@hud`)** — SQL query interface against production data. Tables include `Functions`, `FunctionMetricsLowResolution`, `Endpoints`, `EndpointMetricsLowResolution`, `Forensics`, `EndpointDeployments`, `FunctionDeployments`. Always use `environment_name = 'production'`.
- Cursor's built-in editing, shell, and file tools.

### Task

> Replace this section with your actual task.
>
> Examples:
> - "Find all functions with zero invocations in the last 60 days. Run safety checks (don't delete framework hooks, public exports, dynamic references). Open a PR removing the dead ones."
> - "Identify the top 5 endpoints by error rate over the last 7 days. Investigate the most recent fingerprints with `hud-get-forensics`. Open a Jira ticket per endpoint with the proposed fix."
>
> Reference the examples/ folder in the parent repo for working patterns.

### Output

When you finish, print a short summary covering:
- What you did (or why you didn't act)
- Any safety checks that excluded items
- Where to look next (PR URL, Jira ticket, etc.)
