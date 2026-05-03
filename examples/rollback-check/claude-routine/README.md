# Rollback Check — Claude Routine

The same analysis is shipped two ways. Pick based on how you want to invoke it.

## Skill (on-demand, local)

**Path:** [`skill/.claude/skills/rollback-check/SKILL.md`](skill/.claude/skills/rollback-check/SKILL.md)

A Claude Code skill — invoked from a Claude Code session by an engineer (e.g. "run rollback-check on payments-api"). Lives in the customer's repo at `.claude/skills/rollback-check/SKILL.md`.

**Best for:**
- **Incident response.** SRE on-call invokes during a degradation window.
- **Pre-release gates.** Engineer manually checks a service before promoting to prod.
- **Exploration.** You want to look at the verdict + reasoning interactively before deciding.

**How to install:**
1. Copy `skill/.claude/skills/rollback-check/SKILL.md` into your repo at the same path.
2. Make sure your local Claude Code config has the Hud MCP registered with `HUD_MCP_KEY`.
3. In a Claude Code session in the repo, type `/rollback-check` (or just describe what you want — Claude auto-discovers the skill).

## Scheduled remote (continuous, no human in loop)

**Path:** [`scheduled-remote/task.md`](scheduled-remote/task.md)

The same prompt, registered as a scheduled remote task running on Anthropic infrastructure. Fires on a cron and posts a verdict to a configured sink (Slack, PagerDuty, GitHub issue, webhook).

**Best for:**
- **Continuous monitoring.** Every 15 minutes, every deploy, every hour — independent of any human.
- **Hands-off rollback gates.** A deploy webhook triggers it; the verdict gates the next promotion.
- **Multi-service fleets.** One scheduled task covers all services without anyone needing to remember.

**How to install:**
1. Open `scheduled-remote/task.md` and read the "How to register" section.
2. Use `mcp__scheduled-tasks__create_scheduled_task` to register the prompt with your desired cadence.
3. Wire a delivery step (Slack post / GitHub issue / webhook) onto the result so verdicts go where the team will see them.

## Picking between them

| If you want… | Use |
|---|---|
| To kick off the check by hand during an incident | Skill |
| To run continuously without anyone invoking | Scheduled remote |
| To explore the verdict interactively before acting | Skill |
| To gate every deploy automatically | Scheduled remote |
| To live alongside the codebase and travel with the repo | Skill |
| To run independently of the repo (no one needs to be in Claude Code) | Scheduled remote |

You can ship both — they don't conflict. The skill is for humans; the scheduled remote is for the machine.

## Differences in content

The body of both prompts is identical — same analysis steps, same decision matrix, same SQL patterns. The only differences are:

- **Skill** has frontmatter (`name`, `description`) so Claude Code can auto-discover it.
- **Scheduled remote** has a section explaining how to register the task with the scheduler MCP.

If you change the analysis logic, edit both files — they need to stay in sync.
