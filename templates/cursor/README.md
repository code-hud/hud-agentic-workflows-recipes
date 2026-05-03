# Cursor Template

Minimal Cursor Cloud Agent skeleton wired up with the Hud MCP server. Use this as a starting point when building a new agent that needs production runtime data.

## Files

| Path | Purpose |
|---|---|
| `agent.md` | Specification + agent prompt — read it, configure Cursor per the Setup section, paste the Agent Prompt section into a new automation |

Cursor doesn't store agent prompts at a fixed repo path. This file is **documentation**, not a config file. Cursor agents are configured through the dashboard UI.

## Setup

1. Open `agent.md`. Read the Setup section.
2. Configure the Hud MCP server in Cursor → Settings → MCP Servers.
3. Add any extra MCPs (GitHub, Atlassian, Slack…) your task needs.
4. Set automation-level environment variables for any tokens your shell commands use.
5. Create a new Cursor Automation, paste the Agent Prompt section in, replace the `## Task` placeholder with your actual task.
6. Pick an output — Open PR, Send Message, or None.

## Required config

| Item | Where | Notes |
|---|---|---|
| `HUD_MCP_KEY` | Hud MCP server config in Cursor | Hud dashboard → Settings → MCP keys |
| Output sink | Cursor Automation output dropdown | Open PR / Send Message / None |
| Extra MCPs | Cursor MCP config | Match to your task needs |

## Common tweaks

- **Multi-MCP tasks.** Add GitHub, Atlassian, Slack, or any other MCP via the same config pattern. The agent picks them up by tool name.
- **Schedule.** Cursor's automation scheduler (when available) can fire this on a cron. Until then, trigger manually or via webhook.
- **Output to PR.** Cursor's "Open Pull Request" output reads from your file changes — modify files in the sandbox and the platform creates the PR.

## Reference examples

- [Dead-code cleanup](../../examples/dead-code-cleanup/cursor/) — real Cursor automation with Hud + GitHub + Atlassian MCPs and PR + Jira output.
