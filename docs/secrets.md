# Secrets

Every example documents its own required secrets. This is the consolidated view — what each example needs and where each secret comes from.

## Master list

| Secret | Required by | Source |
|---|---|---|
| `HUD_MCP_KEY` | All examples | Hud dashboard → Settings → MCP keys |
| `ANTHROPIC_API_KEY` | All examples (Anthropic route) | console.anthropic.com |
| `AWS_ROLE_TO_ASSUME` | All examples (Bedrock route only) | IAM role with `bedrock:InvokeModel` |
| `SLACK_BOT_TOKEN` | weekly-report | Slack app with `chat:write` + `users:read.email` scopes |
| `SLACK_CHANNEL` | weekly-report | Slack channel ID (or override per-run) |
| `TEAM_READ_TOKEN` | Any workflow using [`recipes/team-splitting/2-github-teams/`](../recipes/team-splitting/2-github-teams/) | GitHub PAT with `read:org` scope |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | dead-code-cleanup (Cursor) | PAT with org-wide `repo` scope |

## Per-example checklist

### blast-radius (github-actions)

- [ ] `HUD_MCP_KEY`
- [ ] `ANTHROPIC_API_KEY` (or `AWS_ROLE_TO_ASSUME` for Bedrock — see [`auth.md`](auth.md))

### weekly-report (gh-aw)

- [ ] `HUD_MCP_KEY`
- [ ] `ANTHROPIC_API_KEY` (or `AWS_ROLE_TO_ASSUME` for Bedrock)
- [ ] `SLACK_BOT_TOKEN`
- [ ] `SLACK_CHANNEL` (or override per dispatch)

### dead-code-cleanup (Cursor)

- [ ] `HUD_MCP_KEY` (in Cursor MCP config)
- [ ] `GITHUB_PERSONAL_ACCESS_TOKEN` (set as automation-level env var **and** in GitHub MCP config — MCP env vars don't propagate to shell commands)
- [ ] Atlassian MCP enabled in Cursor (no separate token to manage)

### rollback-check (Claude routine — both variants)

**Skill variant:**
- [ ] Local Claude Code config has Hud MCP registered with `HUD_MCP_KEY`.

**Scheduled-remote variant:**
- [ ] The `mcp__scheduled-tasks` runner has Hud MCP available with `HUD_MCP_KEY`.
- [ ] Output sink configured (Slack token, GitHub PAT, webhook URL — depends on where you send the verdict).

## Storage rules

- Always store as repo or org secrets in GitHub Settings.
- Never hardcode in YAML or markdown.
- Rotate `HUD_MCP_KEY` if a workflow run leaks (e.g. logged accidentally). Rotation is from the Hud dashboard.
- For long-lived `GITHUB_PERSONAL_ACCESS_TOKEN`, prefer fine-grained PATs or GitHub App tokens to classic PATs. Set an expiry calendar reminder.
