---
name: hud-agent
description: |
  Blank gh-aw agent skeleton wired up with the Hud MCP server.
  Drop your task description into the "## Task" section below.

on:
  workflow_dispatch:
    inputs:
      additional_context:
        description: 'Optional free-text context to append to the task'
        required: false
        type: string

engine: claude
strict: false
timeout-minutes: 30

permissions:
  contents: read

network:
  allowed:
    - defaults
    - node
    - github
    - "api.hud.io"
    - "cdn.hud.io"

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

# Hud Agent

You have access to the **hud-mcp** MCP server for querying Hud production runtime data, plus standard tools (edit, bash, github, web-fetch).

If `additional_context` is provided, factor it in.

## Task

> Replace this section with your task description.
>
> Examples:
> - "Find functions with zero invocations in the last 60 days and open a draft PR removing them."
> - "Summarize the top 5 endpoints by error rate over the last 7 days and post to Slack."
> - "Compare the current deployment's health to the previous version and recommend rollback / investigate / clean."
>
> Reference the [examples/](../../../../examples/) folder for working patterns.

When you finish, print a short summary of what you did and any next steps.
