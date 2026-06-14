# Hud Agentic Workflows: Recipes

Production agentic workflows powered by [Hud](https://hud.io) runtime data. A coding agent runs a defined task automatically — on a PR, a deploy, or a schedule — grounded in your real production metrics instead of source and diffs alone.

**New to agentic workflows?** See the [concept guide in the Hud docs](https://docs.hud.io/docs/agentic-workflows). This repo is the hands-on version: pick a use case, pick a runner, copy the files.

## The matrix

Every workflow is a **use case** (what the agent does) running on a **runner** (where it executes). Any use case works on any runner.

|  | GitHub Actions ([Claude](runner-templates/github-actions-claude/) · [Codex](runner-templates/github-actions-codex/)) | [gh-aw](runner-templates/gh-aw/) | [Cursor](runner-templates/cursor/) | [Claude routine](runner-templates/claude-routine/) |
|---|:---:|:---:|:---:|:---:|
| **[Blast radius](task-recipes/prompts/blast-radius.md)** | [see example](full-examples/blast-radius-github-actions/) | [mix & match](#how-to-mix--match) | [mix & match](#how-to-mix--match) | [mix & match](#how-to-mix--match) |
| **[Weekly report](task-recipes/prompts/weekly-report/)** | [mix & match](#how-to-mix--match) | [see example](full-examples/weekly-report-gh-aw/) | [mix & match](#how-to-mix--match) | [mix & match](#how-to-mix--match) |
| **[Dead-code cleanup](task-recipes/prompts/dead-code-cleanup.md)** | [mix & match](#how-to-mix--match) | [mix & match](#how-to-mix--match) | [see example](full-examples/dead-code-cleanup-cursor/) | [mix & match](#how-to-mix--match) |
| **[Rollback check](task-recipes/prompts/rollback-check.md)** | [mix & match](#how-to-mix--match) | [mix & match](#how-to-mix--match) | [mix & match](#how-to-mix--match) | [see example](full-examples/rollback-check-claude-routine/) |

**see example** = fully worked, install-ready. Click to go straight to the install guide.
**mix & match** = grab the [prompt](task-recipes/prompts/) + [runner template](runner-templates/) and wire them together. See [How to combine](#how-to-mix--match).

## Pick your path

### I know what use case and runner I want
Click the cell in the matrix. If it says **see example**, follow the install README. If it says **mix & match**, see [How to combine](#how-to-mix--match).

### I have a use case but need to pick a runner
Read the [Runners](#runners) table to compare, then click your cell.

### I want to build something custom
Pick a runner from [`runner-templates/`](runner-templates/), write your own prompt (or use [`task-recipes/prompts/`](task-recipes/prompts/) as a starting point).

## Runners

| Runner | Integration | What you do | Best for |
|---|---|---|---|
| **GitHub Actions** | Copy files | Copy `.github/` files to repo, set secrets. Two templates: [Claude CLI](runner-templates/github-actions-claude/) or [Codex CLI](runner-templates/github-actions-codex/). | PR-triggered workflows, cron jobs, teams already on GH Actions |
| **gh-aw** | Copy files | Copy `.github/workflows/*.md`, run `gh aw compile`, set secrets | Same triggers as GH Actions but with markdown+YAML agent format |
| **Cursor** | Copy + UI | Copy `AGENTS.md` to repo, create automation in Cursor dashboard, add MCP servers, set secrets | Teams using Cursor, manual or scheduled triggers |
| **Claude routine** | Copy file _or_ register | **Skill:** copy `.claude/skills/` to repo. **Scheduled:** register prompt via MCP tool call | On-demand (skill) or continuous cron monitoring (scheduled) |


## How to mix & match

When the matrix says **mix & match**, you're pairing a prompt with a runner template:

1. Grab the **prompt** from [`task-recipes/prompts/`](task-recipes/prompts/). Click the use case name in the matrix row header.
2. Grab the **runner template** from [`runner-templates/`](runner-templates/). Click the runner name in the matrix column header.
3. Follow the runner template's README for where to place the prompt and what to configure.
4. Check the prompt's env var table for any variables you need to wire up in the runner config.

## Repo structure

```
runner-templates/              Runner skeletons. How it runs.
  github-actions-claude/  GitHub Actions + Claude Code CLI
  github-actions-codex/   GitHub Actions + Codex CLI
  gh-aw/                  Copy .github/workflows/*.md to repo
  cursor/                 Copy AGENTS.md to repo + UI setup
  claude-routine/
    skill/                Copy .claude/skills/ to repo
    scheduled-remote/     Register via MCP tool call (no files)

task-recipes/
  prompts/              Use-case prompts. What it does.
    blast-radius.md
    weekly-report/
    dead-code-cleanup.md
    rollback-check.md
  team-splitting/       Cross-cutting patterns for scoping by team.

full-examples/               Fully worked combos (runner + prompt + install README).
  blast-radius-github-actions/
  weekly-report-gh-aw/
  dead-code-cleanup-cursor/
  rollback-check-claude-routine/

docs/                   Auth guides, secrets reference, screenshots.
```

## Auth

Every workflow authenticates to Hud with a single `HUD_MCP_KEY` secret passed to `npx -y hud-mcp@v2`.

Get the key: [hud.io](https://hud.io) → Settings → MCP keys.

| Topic | Doc |
|---|---|
| Anthropic vs Bedrock model auth | [`docs/auth.md`](docs/auth.md) |

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Pick a use case folder (or create one), add a runner sub-folder, include a `README.md` per leaf.

## License

MIT. See [`LICENSE`](LICENSE).
