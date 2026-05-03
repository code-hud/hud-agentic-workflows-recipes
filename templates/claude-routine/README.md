# Claude Routine Template

Two flavors of "Claude with Hud, no specific task" — pick based on how you want to invoke it.

## Skill (on-demand, local)

**Path:** [`skill/.claude/skills/hud-agent/SKILL.md`](skill/.claude/skills/hud-agent/SKILL.md)

A Claude Code skill — invoked by an engineer from a Claude Code session. Lives in the customer's repo at `.claude/skills/<name>/SKILL.md`.

**Best for:**
- Tasks the developer kicks off when they hit an issue.
- Exploration where the human reviews verdict + reasoning interactively.
- Repo-local skills that travel with the codebase.

**How to install:**
1. Copy the file structure into your repo (`cp -r skill/.claude/skills/hud-agent <your-repo>/.claude/skills/`).
2. Rename `hud-agent` to whatever fits your task.
3. Edit the `## Task` section and the frontmatter `description`.
4. Make sure the user's local Claude Code config has the Hud MCP registered.
5. In a Claude Code session in the repo, type `/<your-skill-name>` (or describe what you want — Claude auto-discovers).

## Scheduled remote (continuous, no human in loop)

**Path:** [`scheduled-remote/task.md`](scheduled-remote/task.md)

A prompt registered with the `mcp__scheduled-tasks` MCP. Runs on Anthropic infrastructure on a cron. Posts results to a configured sink (Slack, PagerDuty, GitHub issue, webhook).

**Best for:**
- Continuous monitoring that fires without anyone invoking.
- Multi-service fleets where one task covers everything.
- Hands-off gates (e.g. every deploy, every hour).

**How to install:**
1. Open `scheduled-remote/task.md`. Read the "How to register" section.
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

- [Rollback check](../../examples/rollback-check/claude-routine/) — both variants of a real production rollback gate.
