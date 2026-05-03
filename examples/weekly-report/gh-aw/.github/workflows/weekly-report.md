---
description: |
  Weekly deep-insights report for Hud production.
  Analyzes week-over-week performance and error regressions using the hud-mcp
  MCP server, generates actionable fixes, annotates contributors via git blame
  + Slack lookup, applies quality gates, optionally self-heals the best fix as
  a draft PR, formats a Slack Block Kit message, and posts it to a channel.

name: gh-aw-hud report

on:
  workflow_dispatch:
    inputs:
      investigation_mode:
        description: '"weekly" (default) for week-over-week, or "audit" for absolute health check'
        required: false
        default: 'weekly'
        type: choice
        options:
          - weekly
          - audit
      additional_context:
        description: 'Additional context to append to the analysis prompt (optional)'
        required: false
        type: string
      slack_channel:
        description: 'Slack channel to send the report to (overrides SLACK_CHANNEL secret)'
        required: false
        type: string
      services:
        description: 'Comma-separated service names to scope the analysis (e.g. my-api,my-worker). Leave empty to analyze all services.'
        required: false
        type: string
      open_pr:
        description: 'Run self-heal step and open a PR with fixes'
        required: false
        default: true
        type: boolean

engine: claude
strict: false
timeout-minutes: 90

permissions:
  id-token: write
  contents: read
  pull-requests: read

network:
  allowed:
    - defaults
    - node
    - github
    - "api.hud.io"
    - "cdn.hud.io"
    - "api.slack.com"
    - "slack.com"
    - "*.lambda-url.eu-central-1.on.aws"

tools:
  edit:
  bash: [":*"]
  github:
    toolsets: [repos, pull_requests]
  web-fetch:

mcp-servers:
  hud-mcp:
    command: "npx"
    args: ["-y", "hud-mcp@v2"]
    env:
      HUD_MCP_KEY: "${{ secrets.HUD_MCP_KEY }}"

safe-outputs:
  create-pull-request:
    draft: true
    labels: [self-heal]

env:
  SLACK_BOT_TOKEN: "${{ secrets.SLACK_BOT_TOKEN }}"
  SLACK_CHANNEL: "${{ github.event.inputs.slack_channel || secrets.SLACK_CHANNEL }}"
  HUD_SERVICES: "${{ github.event.inputs.services }}"

runtimes:
  node:
    version: "22"

steps:
  - name: Checkout repository
    uses: actions/checkout@v5
    with:
      fetch-depth: 0
      persist-credentials: false


---

# Weekly Hud Report

## Job Description

You are an AI performance and reliability engineer for `${{ github.repository }}`.
Your task: generate a weekly deep-insights report analyzing production data, propose fixes for ongoing issues, annotate contributors, apply quality gates, optionally self-heal the most impactful issue, and deliver the report to Slack.

**Parameters for this run:**
- **Investigation mode:** `${{ github.event.inputs.investigation_mode }}` (default: weekly)
- **Slack channel:** `$SLACK_CHANNEL` (input override or `SLACK_CHANNEL` secret)
- **Services filter:** `${{ github.event.inputs.services }}` (empty = all services)
- **Additional context:** `${{ github.event.inputs.additional_context }}`
- **Self-heal enabled:** `${{ github.event.inputs.open_pr }}` (default: true)

Execute the following phases **sequentially**. Each phase has a detailed prompt file — read it and follow its instructions precisely.

---

## Phase 1 — Analysis

**Goal:** Analyze Hud production data and write findings to `/tmp/analysis_findings.md`.

1. Determine which prompt file to use:
   - If investigation mode is `audit`: read `.github/workflows/deep-insights/health-audit.txt`
   - Otherwise: read `.github/workflows/deep-insights/investigate.txt`

2. Read the selected prompt file in its entirety.

3. **Services filter:** If `$HUD_SERVICES` is non-empty, scope ALL queries to only those service names (comma-separated). Do not include data from any other service.

4. If additional context was provided above (not "(none)"), incorporate it into your analysis.

5. Follow ALL instructions in the prompt file. Use the **hud-mcp** MCP server for all data queries (metrics, forensics, metadata).

6. Write your complete findings to `/tmp/analysis_findings.md`.

7. After writing, confirm the file exists and print a short summary (number of insights, categories).

**CRITICAL:** Do NOT proceed to Phase 2 until `/tmp/analysis_findings.md` exists and contains findings.

---

## Phase 2 — Solution Generation

**Goal:** For each ONGOING insight, generate a concrete suggested fix.

1. Read `.github/workflows/deep-insights/solutions.txt` in its entirety.

2. Follow its instructions: read `/tmp/analysis_findings.md`, then for each ONGOING insight, investigate the root cause and generate a fix. Launch sub-agents in parallel for each ONGOING insight.

3. Write the enriched findings (with `### Suggested Fix` sections) back to `/tmp/analysis_findings.md`.

4. Confirm by printing a summary of fixes generated.

---

## Phase 3 — Blame & Slack Annotations

**Goal:** Annotate findings with the Slack handles of contributors who last touched the root-cause code.

### Step 3a: Build Slack email map

Run this bash script to build a mapping from git author emails to Slack user IDs. The `SLACK_BOT_TOKEN` environment variable is available.

```bash
python3 - "$SLACK_BOT_TOKEN" <<'PY'
import json, subprocess, sys, urllib.request, urllib.parse

token = sys.argv[1]
emails_raw = subprocess.check_output(["git", "log", "--format=%ae", "--all"], text=True)
unique_emails = sorted(set(e.strip() for e in emails_raw.splitlines() if e.strip()))

slack_map = {}
for email in unique_emails:
    try:
        url = "https://slack.com/api/users.lookupByEmail?" + urllib.parse.urlencode({"email": email})
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        if data.get("ok"):
            user = data["user"]
            profile = user.get("profile", {})
            slack_map[email] = {
                "slack_id": user["id"],
                "display_name": profile.get("display_name") or user.get("name", ""),
                "real_name": profile.get("real_name") or user.get("real_name", ""),
            }
    except Exception:
        pass

name_raw = subprocess.check_output(["git", "log", "--format=%an\t%ae", "--all"], text=True)
name_to_email = {}
for line in name_raw.splitlines():
    if "\t" not in line:
        continue
    name, email = line.split("\t", 1)
    name = name.strip().lower()
    if name and email.strip() in slack_map and name not in name_to_email:
        name_to_email[name] = email.strip()

output = {"by_email": slack_map, "by_name": name_to_email}
with open("/tmp/slack_email_map.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"Mapped {len(slack_map)}/{len(unique_emails)} emails to Slack users")
PY
```

### Step 3b: Annotate findings with blame context

1. Read `.github/workflows/deep-insights/blame.txt` in its entirety.

2. Follow its instructions to annotate `/tmp/analysis_findings.md` with `**Contributors:** <@SLACK_ID>` lines using git blame and the Slack map at `/tmp/slack_email_map.json`.

---

## Phase 4 — Quality Pass (Deslop)

**Goal:** Remove redundancy, enforce quality gates, and polish the findings.

1. Read `.github/workflows/deep-insights/deslop.txt` in its entirety.

2. Follow its instructions to clean up `/tmp/analysis_findings.md`: apply quality gates, merge duplicates, enforce limits, fix formatting.

3. Write the cleaned version back to `/tmp/analysis_findings.md`.

---

## Phase 5 — Self Heal

**Goal:** Select the best fix and apply it as a draft PR.

**Skip this phase entirely** if self-heal is disabled (the parameter above says `false`).

1. Read `.github/workflows/deep-insights/self-heal.txt` in its entirety.

2. Follow the **scoring** and **fix selection** instructions (Phases 1-4 of self-heal.txt).

3. If a fix qualifies (score >= 20), apply the code changes using the edit tool.

4. **IMPORTANT — PR creation:** Do NOT follow the git branch/commit/push/PR instructions in self-heal.txt. Instead, the safe-outputs system will automatically create a draft PR from your file changes. Just make sure you've edited only the files that need fixing.

5. If no fix qualifies, note "No suitable fix found" and continue to Phase 6.

---

## Phase 6 — Format & Send to Slack

**Goal:** Convert findings to Slack Block Kit JSON and post to the channel.

### Step 6a: Format as Slack JSON

1. Read `.github/workflows/deep-insights/format.txt` in its entirety.

2. Read `/tmp/analysis_findings.md`.

3. Following the format.txt instructions, convert the findings into a Slack `chat.postMessage` JSON payload. Use the channel from the `$SLACK_CHANNEL` environment variable.

4. Write the JSON payload to `/tmp/slack_json.json`.

### Step 6b: Enforce Slack limits

Run this script to split oversized blocks and enforce the 50-block limit:

```bash
python3 <<'PY'
import json, sys

CHAR_LIMIT = 2990

def split_text_block(block):
    text_obj = block.get('text', {})
    text = text_obj.get('text', '')
    if len(text) <= CHAR_LIMIT:
        return [block]
    parts, current = [], ''
    for line in text.split('\n'):
        candidate = (current + '\n' + line) if current else line
        if len(candidate) > CHAR_LIMIT and current:
            parts.append(current)
            current = line
        else:
            current = candidate
    if current:
        parts.append(current)
    final_parts = []
    for part in parts:
        while len(part) > CHAR_LIMIT:
            cut = part.rfind('\n', 0, CHAR_LIMIT)
            if cut < CHAR_LIMIT // 2:
                cut = part.rfind(' ', 0, CHAR_LIMIT)
            if cut < CHAR_LIMIT // 2:
                cut = CHAR_LIMIT
            final_parts.append(part[:cut])
            part = part[cut:].lstrip()
        if part:
            final_parts.append(part)
    return [
        {**block, 'text': {'type': text_obj.get('type', 'mrkdwn'), 'text': p}}
        for p in final_parts
    ]

with open('/tmp/slack_json.json') as f:
    payload = json.load(f)

blocks = payload.get('blocks', [])
expanded = []
for b in blocks:
    if b.get('type') == 'section' and isinstance(b.get('text'), dict):
        expanded.extend(split_text_block(b))
    else:
        expanded.append(b)

if len(expanded) > 49:
    expanded = expanded[:48]
    expanded.append({'type': 'divider'})
    expanded.append({
        'type': 'context',
        'elements': [{'type': 'mrkdwn', 'text': ':scissors: _Report truncated. See workflow logs for full report._'}]
    })

payload['blocks'] = expanded
with open('/tmp/slack_json.json', 'w') as f:
    json.dump(payload, f)

print(f"Final payload: {len(expanded)} blocks")
PY
```

### Step 6c: Post to Slack

```bash
# Add channel to payload
PAYLOAD=$(jq --arg ch "$SLACK_CHANNEL" '.channel = $ch' /tmp/slack_json.json)

RESPONSE=$(curl -s -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  --data "$PAYLOAD")

SLACK_OK=$(echo "$RESPONSE" | jq -r '.ok')
if [ "$SLACK_OK" = "true" ]; then
  echo "Report sent to Slack successfully"
else
  SLACK_ERROR=$(echo "$RESPONSE" | jq -r '.error // "unknown"')
  echo "Slack error: $SLACK_ERROR"

  # Fallback: send plain text
  curl -s -X POST "https://slack.com/api/chat.postMessage" \
    -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
    -H "Content-Type: application/json" \
    --data "$(jq -n --arg ch "$SLACK_CHANNEL" --arg t "Weekly Deep Insights Report — see workflow logs for full report" '{channel: $ch, text: $t}')"
fi
```

If a self-heal PR was created in Phase 5, also post a thread reply linking to it.

---

## Final Summary

After all phases complete, print a brief status summary:
- Phase 1 (Analysis): number of insights found
- Phase 2 (Solutions): number of fixes generated
- Phase 3 (Blame): number of contributors annotated
- Phase 4 (Deslop): number of insights retained
- Phase 5 (Self-Heal): fix applied or skipped
- Phase 6 (Slack): posted or failed
