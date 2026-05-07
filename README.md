# Hud Agentic Workflows — Recipes

> A catalog of working agentic workflows and automations built on [Hud](https://hud.io) runtime data. Copy, adapt, install.

## What's in here

This repo collects ready-to-install agentic workflows that turn Hud's production runtime data into actionable developer-facing automations — surfaced where developers already work (PRs, IDE, Slack, weekly reports).

The mental model is **runner + prompt**: pick what you want to run on (templates) and what you want it to do (recipes/prompts), then drop them into your repo.

| Folder | What | Use it when |
|---|---|---|
| [`templates/`](templates/) | Runner skeletons — gh-aw, GitHub Actions, Cursor, Claude routine | Pick the platform you want to run on |
| [`recipes/prompts/`](recipes/prompts/) | Use-case prompts — blast-radius, weekly-report, dead-code-cleanup, rollback-check | Pick what you want the agent to do |
| [`recipes/team-splitting/`](recipes/team-splitting/) | Cross-cutting patterns for scoping by team or service | Adapt any combo to your team shape |
| [`examples/`](examples/) | Fully worked combos (runner + prompt + install README) | Reference / install-ready starting points |

## Quick start

Pick a **runner** + pick a **prompt** → combine in your repo.

1. **Choose a runner** from [`templates/`](templates/) — gh-aw, GitHub Actions, Cursor Cloud Agent, or Claude routine (skill or scheduled remote).
2. **Choose a prompt** from [`recipes/prompts/`](recipes/prompts/) — blast-radius, weekly-report, dead-code-cleanup, or rollback-check.
3. **Drop both into your repo**, set the secrets ([`docs/secrets.md`](docs/secrets.md)), and ship a test PR / scheduled run.
4. **Different combo?** (Codex over GitHub Actions, weekly-report on Cursor, etc.) Ask your agent to adapt the runner template to fit the prompt — separating runner from prompt is what makes that easy.

Want a complete worked combo as reference? See [`examples/`](examples/) — each is one runner + one prompt, install-ready.

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

| Folder | What |
|---|---|
| [`prompts/`](recipes/prompts/) | The four use-case prompts — drop them into any runner |
| [`team-splitting/`](recipes/team-splitting/) | Three strategies for scoping a workflow by team or service (config file · GitHub Teams · `package.json`) |

## Auth

All examples use a single `HUD_MCP_KEY` secret to authenticate the Hud MCP server (`npx -y hud-mcp@v2`). New to Hud? Start at [hud.io](https://hud.io); the dashboard's Settings → MCP keys page is where you mint the key.

For Bedrock-routed customers, see [`docs/auth.md`](docs/auth.md). For the consolidated list of every secret each example needs, see [`docs/secrets.md`](docs/secrets.md).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) — TL;DR: pick a use case folder (or open one), add a platform sub-folder, include a `README.md` per leaf.

## License

MIT. See [`LICENSE`](LICENSE).
