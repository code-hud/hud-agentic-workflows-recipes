# Claude Routine Template

Two flavors of "Claude with Hud, no specific task". pick based on how you want to invoke it.

## How to install

| Variant | Step | Action |
|---|---|---|
| **Skill** | **Copy to your repo** | Copy `.claude/skills/hud-agent/SKILL.md` into your repo at the same path |
|  | **Configure locally** | Register Hud MCP: `claude mcp add -e HUD_MCP_KEY=$HUD_MCP_KEY --scope user --transport stdio hud -- npx -y hud-mcp@v2` |
|  | **Invoke** | In a Claude Code session, type `/hud-agent` |
| **Scheduled remote** | **Copy to your repo** | *(nothing. no files)* |
|  | **Register** | From a Claude Code session, use `mcp__scheduled-tasks__create_scheduled_task` with the prompt from `scheduled-remote/task.md` |
|  | **Configure** | Wire a delivery step (Slack / webhook / GitHub issue) for the output |

## Skill (on-demand, local)

**Path:** [`skill/.claude/skills/hud-agent/SKILL.md`](skill/.claude/skills/hud-agent/SKILL.md)

A Claude Code skill. Invoked by an engineer from a Claude Code session. Lives in your repo at `.claude/skills/<name>/SKILL.md`.

**Best for:**
- Tasks the developer kicks off when they hit an issue.
- Exploration where the human reviews verdict + reasoning interactively.
- Repo-local skills that travel with the codebase.

**Where to put the prompt:** Open `SKILL.md` and replace the `## Task` section with your task prompt. You can grab a ready-made prompt from [`recipes/prompts/`](../../recipes/prompts/) (e.g. `rollback-check.md`, `blast-radius.md`) or write your own.

**How to install:**
1. Copy the file structure into your repo (`cp -r skill/.claude/skills/hud-agent <your-repo>/.claude/skills/`).
2. Rename `hud-agent` to whatever fits your task.
3. Replace the `## Task` section with your prompt (see above) and update the frontmatter `description`.
4. Make sure your local Claude Code config has the Hud MCP registered.
5. In a Claude Code session in the repo, type `/<your-skill-name>` (or describe what you want; Claude auto-discovers).

## Scheduled remote (continuous, no human in loop)

**Path:** [`scheduled-remote/task.md`](scheduled-remote/task.md)

A prompt registered with the `mcp__scheduled-tasks` MCP. Runs on Anthropic infrastructure on a cron. Posts results to a configured sink (Slack, PagerDuty, GitHub issue, webhook).

**Best for:**
- Continuous monitoring that fires without anyone invoking.
- Multi-service fleets where one task covers everything.
- Hands-off gates (e.g. every deploy, every hour).

**Where to put the prompt:** Open `scheduled-remote/task.md` and replace the `## Task` section with your task prompt. Same source: grab from [`recipes/prompts/`](../../recipes/prompts/) or write your own.

**How to install:**
1. Open `scheduled-remote/task.md`. Replace the `## Task` section with your prompt.
2. Use `mcp__scheduled-tasks__create_scheduled_task` to register the prompt with your desired cadence.
3. Wire a delivery step (Slack post / GitHub issue / webhook) so the verdict goes somewhere visible.

## Picking between them

| If you want… | Use |
|---|---|
| To invoke by hand during an incident or audit | Skill |
| To run continuously without any human | Scheduled remote |
| To explore the verdict interactively before acting | Skill |
| To gate every deploy automatically | Scheduled remote |
| To live with the codebase | Skill |
| To live independently of any repo | Scheduled remote |

You can ship both. The skill is for humans; the scheduled remote is for the machine. Just keep their analysis logic in sync.

## Reference examples

- [Rollback check](../../examples/rollback-check-claude-routine/). both variants of a real production rollback gate.
