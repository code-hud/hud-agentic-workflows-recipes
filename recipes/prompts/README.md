# Prompts

Use-case prompts you can pair with any runner from [`../../templates/`](../../templates/).

## What's in here

| Prompt | What it does |
|---|---|
| [`blast-radius.md`](blast-radius.md) | Score the blast radius of a PR (0–100) and write a markdown report |
| [`weekly-report/`](weekly-report/) | Multi-phase weekly deep-insights report on production health, with optional self-heal PR |
| [`dead-code-cleanup.md`](dead-code-cleanup.md) | Find functions with zero production traffic and propose deletions |
| [`rollback-check.md`](rollback-check.md) | Compare current vs. previous release health, return a structured verdict |

## How to use

1. Pick a prompt above.
2. Pick a runner from [`../../templates/`](../../templates/) — gh-aw, GitHub Actions, Cursor, or Claude routine.
3. Drop both into your repo at the runner's expected paths. See the runner's README for paths and required secrets.
4. Set the `HUD_MCP_KEY` secret (and any others the runner needs — full list in [`../../docs/secrets.md`](../../docs/secrets.md)).
5. Ship a test run.

## A note on runner coupling

Some prompts contain runner-specific references by default — `dead-code-cleanup.md` mentions Cursor's "Open Pull Request" automation output, `rollback-check.md` is shaped as a Claude Code skill (with frontmatter), and `weekly-report/main.md` uses gh-aw frontmatter. **Each prompt works as-is on the runner it was originally paired with.**

If you're using a different runner (say, the dead-code-cleanup prompt on GitHub Actions, or the weekly-report prompt on Cursor), the runner-specific bits need light adaptation. Easiest path: open the prompt and the runner template side-by-side and ask Claude (or your agent of choice) to adapt the prompt to the new runner's conventions.

## Mapping to fully worked examples

For each prompt here, there's a complete worked example (runner + prompt + install README) under [`../../examples/`](../../examples/):

| Prompt | Example pairing |
|---|---|
| `blast-radius.md` | [`examples/blast-radius/github-actions/`](../../examples/blast-radius/github-actions/) |
| `weekly-report/` | [`examples/weekly-report/gh-aw/`](../../examples/weekly-report/gh-aw/) |
| `dead-code-cleanup.md` | [`examples/dead-code-cleanup/cursor/`](../../examples/dead-code-cleanup/cursor/) |
| `rollback-check.md` | [`examples/rollback-check/claude-routine/skill/`](../../examples/rollback-check/claude-routine/skill/) |

The examples are install-ready — pick one if you want a working starting point and adapt from there.
