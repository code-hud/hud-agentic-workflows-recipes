# Hud Agentic Workflows — Recipes

> A catalog of working agentic workflows and automations built on [Hud](https://hud.io) runtime data. Copy, adapt, install.

## What's in here

This repo collects ready-to-install examples of agentic workflows that turn Hud's production runtime data into actionable developer-facing automations — surfaced where developers already work (PRs, IDE, Slack, weekly reports). Each example ships with the workflow code, prompts, and an install README.

Three layers:

| Folder | What | Use it when |
|---|---|---|
| [`templates/`](templates/) | Blank skeletons (Hud + a model, no task) for each platform | Starting a new agent and want a clean scaffold |
| [`examples/`](examples/) | Real, working use cases | You have a specific use case (blast radius, weekly report, dead code, rollback) |
| [`recipes/`](recipes/) | Cross-cutting patterns (e.g. team-splitting) that plug into any example | Adapting an example to your team/service shape |

## Quick start

1. Pick an example from [`examples/`](examples/) that matches a pain you're feeling.
2. Read its `README.md` — it lists the secrets you need and where each file goes.
3. Copy the files into your repo, set the secrets, and ship a test PR / scheduled run.

If you're starting from scratch with a custom task, start in [`templates/`](templates/) instead.

## Examples

| Use case | Platform | What it does |
|---|---|---|
| [Blast radius](examples/blast-radius/) | GitHub Actions | Posts a per-PR comment scoring the change's blast radius using production traffic + dependency data. |
| [Weekly report](examples/weekly-report/) | gh-aw (GitHub Agentic Workflows) | Generates a weekly Slack report of regressions, optimization opportunities, and self-heal PRs. |
| [Dead-code cleanup](examples/dead-code-cleanup/) | Cursor (Cloud Agent) | Finds zero-traffic functions and opens a cleanup PR. |
| [Rollback check](examples/rollback-check/) | Claude routine (skill or scheduled remote) | Compares current vs. previous release health to recommend go / no-go on rollback. |

## Templates

| Platform | Path | Best for |
|---|---|---|
| gh-aw | [`templates/gh-aw/`](templates/gh-aw/) | Markdown+YAML workflows on GitHub, executed by the gh-aw runtime |
| GitHub Actions | [`templates/github-actions/`](templates/github-actions/) | Standard `.yml` workflows; portable, well-known |
| Cursor | [`templates/cursor/`](templates/cursor/) | Cursor Cloud Agents (configured via dashboard, prompt pasted in) |
| Claude routine | [`templates/claude-routine/`](templates/claude-routine/) | On-demand skills or scheduled remote agents |

## Recipes

| Pattern | Path |
|---|---|
| Team-splitting (3 ways: config file · GitHub Teams · `package.json`) | [`recipes/team-splitting/`](recipes/team-splitting/) |

## Auth

All examples use a single `HUD_MCP_KEY` secret to authenticate the Hud MCP server (`npx -y hud-mcp@v2`). For Bedrock-routed customers, see [`docs/auth.md`](docs/auth.md).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) — TL;DR: pick a use case folder (or open one), add a platform sub-folder, include a `README.md` per leaf.

## License

MIT. See [`LICENSE`](LICENSE).
