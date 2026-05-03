# Hud Agent — Scheduled Remote Task (Template)

A blank skeleton for a Claude scheduled remote task that uses the Hud MCP for production runtime data. The agent runs on Anthropic infrastructure on a cron.

## How to register

The `scheduled-tasks` MCP is currently an Anthropic-managed server — check the Claude Code docs for the canonical install path; if it's not enabled in your environment, ship the on-demand [skill variant](../skill/) instead.

Use `mcp__scheduled-tasks__create_scheduled_task` to register the prompt below. From a Claude Code session:

```
Use the scheduled-tasks MCP to create a task with:
- name: "<short-name>"
- schedule: "<cron expression>"   e.g. "0 14 * * MON" for Mondays 14:00 UTC
- prompt: <paste the contents of the "Prompt" section below>
- enabled: true
```

The exact arguments depend on your `mcp__scheduled-tasks` server's schema — run `mcp__scheduled-tasks__list_scheduled_tasks` first to confirm fields.

## Required setup

1. **Hud MCP available** — the scheduled-task runner needs the hud MCP registered with a valid `HUD_MCP_KEY` secret.
2. **Output sink** — decide where the task's verdict / report goes: Slack, GitHub issue, PagerDuty, custom webhook. Wire delivery as a follow-on step (e.g. by chaining with an HTTP-call MCP) — the prompt below produces structured content; delivery is separate.

## When to use this variant (vs. the [skill variant](../skill/))

Use scheduled-remote when:
- You want **continuous monitoring** without anyone needing to invoke it.
- The cadence is fixed (cron-based — every N minutes/hours/days).
- The output should land in a chat channel or ticket system, not a Claude Code session.

Use a skill instead when the agent should be invoked on-demand by a developer during incident response or pre-release gates.

---

## Prompt

> Paste this entire section into the scheduled task's prompt field. Replace `## Task` with your actual task.

### Role

You are an engineer with access to Hud production runtime data via the `hud` MCP. Use Hud to ground your analysis in actual production behavior — not assumptions.

### Tools

- `hud` (MCP) — start with `hud-get-schema`. Use `hud-query` for SQL, `hud-get-forensics` for traces, `hud-get-skill` for helper skills (e.g. `use-hud-forensics`, `create-hud-url`).

### Task

> Replace this section with your actual task.
>
> Examples:
> - "Every 15 minutes: check the latest service deployment. If error rate >2x baseline, output a ROLLBACK recommendation."
> - "Every hour: list the top 5 endpoints by P99 latency increase vs. the same hour last week. Output as JSON."
> - "Daily at 09:00 UTC: scan all services for newly-introduced error fingerprints. Output one line per service: name, fingerprint count, top exception type."

### Output

Return a structured result the delivery step can render. Default shape:

```json
{
  "summary": "<one-line human-readable summary>",
  "verdict": "<short label, e.g. CLEAN | WARN | ALERT>",
  "details": { ... },
  "links": ["<Hud URLs>"]
}
```

If nothing actionable is found, return `verdict: "CLEAN"` with a brief summary so the delivery step can decide whether to suppress the message.
