# Cursor Template

Minimal Cursor Cloud Agent skeleton wired up with the Hud MCP server. Use this as a starting point when building a new agent that needs production runtime data.

## How to install

| Step | Action |
|---|---|
| **Copy to your repo** | `AGENTS.md` → repo root |
| **Configure in UI** | 1. Go to [cursor.com/automations](https://cursor.com/automations) → Create automation → select your repo and branch |
|  | 2. Go to [cursor.com/agents](https://cursor.com/agents) → MCP dropdown → add Hud MCP server (see [MCP config](#mcp-config) below) |
|  | 3. Write your task prompt in the automation prompt field (or keep it minimal. the agent reads `AGENTS.md` from the repo automatically) |
|  | 4. Pick an output. Open PR, Send Message, or None |
|  | 5. Pick a trigger. schedule, GitHub event, Slack message, or manual |
| **Set secrets (Cursor workspace secrets)** | `HUD_MCP_KEY` - get from Hud dashboard → Settings → MCP keys |

## Where to put the prompt

Open `AGENTS.md` and replace the `## Task` section with your task prompt. You can grab a ready-made prompt from [`task-recipes/prompts/`](../../task-recipes/prompts/) (e.g. `dead-code-cleanup.md`, `blast-radius.md`) or write your own. Cursor Cloud reads `AGENTS.md` from your repo root automatically.

## Files

| Path | Purpose |
|---|---|
| `AGENTS.md` | Agent instructions with your prompt. Copy to repo root. |
| `README.md` | This install guide (not copied to your repo) |

## MCP config

Add this in the Cursor dashboard MCP dropdown when configuring your cloud agent:

**Hud MCP:**

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

Add other MCPs (GitHub, Atlassian, Slack, etc.) the same way if your task needs them.

## Common tweaks

- **Multi-MCP tasks.** Add GitHub, Atlassian, Slack, or any other MCP via the same config pattern. The agent picks them up by tool name.
- **Environment variables.** Add any tokens your shell commands need (e.g. `GITHUB_PERSONAL_ACCESS_TOKEN`) at the automation level. MCP env vars are only available to the MCP process, not your shell.
- **Output to PR.** Select "Open Pull Request" as the automation output. the agent modifies files in the sandbox and Cursor creates the PR automatically.

## Reference examples

- [Dead-code cleanup](../../full-examples/dead-code-cleanup-cursor/). real Cursor automation with Hud + GitHub + Atlassian MCPs and PR + Jira output.
