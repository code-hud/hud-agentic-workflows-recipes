# Prompts

Use-case prompts you can pair with any runner from [`../../templates/`](../../templates/).

## What's in here

| Prompt | What it does |
|---|---|
| [`blast-radius.md`](blast-radius.md) | Score the blast radius of a PR (0–100) and write a markdown report |
| [`weekly-report/`](weekly-report/) | Multi-phase weekly deep-insights report on production health, with optional self-heal PR |
| [`dead-code-cleanup.md`](dead-code-cleanup.md) | Find functions with zero production traffic and propose deletions |
| [`rollback-check.md`](rollback-check.md) | Compare current vs. previous release health, return a structured verdict |

Each prompt documents required environment variables and tools at the top. Prompts are runner-agnostic — they use env vars and generic instructions so you can pair them with any runner.

## How to use

1. Pick a prompt above.
2. Pick a runner from [`../../templates/`](../../templates/). gh-aw, GitHub Actions, Cursor, or Claude routine.
3. Drop both into your repo at the runner's expected paths. See the runner's README for paths and required secrets.
4. Set the `HUD_MCP_KEY` secret (and any others the prompt and runner need).
5. Ship a test run.

## Mapping to fully worked examples

For each prompt here, there's a complete worked example (runner + prompt + install README) under [`../../examples/`](../../examples/):

| Prompt | Example pairing |
|---|---|
| `blast-radius.md` | [`examples/blast-radius-github-actions/`](../../examples/blast-radius-github-actions/) |
| `weekly-report/` | [`examples/weekly-report-gh-aw/`](../../examples/weekly-report-gh-aw/) |
| `dead-code-cleanup.md` | [`examples/dead-code-cleanup-cursor/`](../../examples/dead-code-cleanup-cursor/) |
| `rollback-check.md` | [`examples/rollback-check-claude-routine/`](../../examples/rollback-check-claude-routine/) |

The examples are install-ready. Pick one if you want a working starting point and adapt from there.
