# Hud Agentic Workflows: Recipes

Production agentic workflows powered by [Hud](https://hud.io) runtime data. Pick a use case, pick a runner, copy the files.

## The matrix

Every workflow is a **use case** (what the agent does) running on a **runner** (where it executes). Any use case works on any runner.

|  | [GitHub Actions](templates/github-actions/) | [gh-aw](templates/gh-aw/) | [Cursor](templates/cursor/) | [Claude routine](templates/claude-routine/) |
|---|:---:|:---:|:---:|:---:|
| **[Blast radius](recipes/prompts/blast-radius.md)** | [**example**](examples/blast-radius-github-actions/) | combine | combine | combine |
| **[Weekly report](recipes/prompts/weekly-report/)** | combine | [**example**](examples/weekly-report-gh-aw/) | combine | combine |
| **[Dead-code cleanup](recipes/prompts/dead-code-cleanup.md)** | combine | combine | [**example**](examples/dead-code-cleanup-cursor/) | combine |
| **[Rollback check](recipes/prompts/rollback-check.md)** | combine | combine | combine | [**example**](examples/rollback-check-claude-routine/) |

**example** = fully worked, install-ready. Click to go straight to the install guide.
**combine** = grab the [prompt](recipes/prompts/) + [runner template](templates/), adapt. See [How to combine](#how-to-combine).

## Pick your path

### I know what use case and runner I want
Click the cell in the matrix. If it says **example**, follow the install README. If it says **combine**, see [How to combine](#how-to-combine).

### I have a use case but need to pick a runner
Read the [Runners](#runners) table to compare, then click your cell.

### I want to build something custom
Pick a runner from [`templates/`](templates/), write your own prompt (or use [`recipes/prompts/`](recipes/prompts/) as a starting point).

## Runners

| Runner | Integration | What you do | Best for |
|---|---|---|---|
| **GitHub Actions** | Copy files | Copy `.github/` files to repo, set secrets | PR-triggered workflows, cron jobs, teams already on GH Actions |
| **gh-aw** | Copy files | Copy `.github/workflows/*.md`, run `gh aw compile`, set secrets | Same triggers as GH Actions but with markdown+YAML agent format |
| **Cursor** | Copy + UI | Copy `AGENTS.md` to repo, create automation in Cursor dashboard, add MCP servers, set secrets | Teams using Cursor, manual or scheduled triggers |
| **Claude routine** | Copy file _or_ register | **Skill:** copy `.claude/skills/` to repo. **Scheduled:** register prompt via MCP tool call | On-demand (skill) or continuous cron monitoring (scheduled) |

GitHub Actions is CLI-agnostic. Default uses Claude Code CLI; swap in Codex or any MCP-compatible CLI.

## How to combine

When the matrix says **combine**, you're pairing a prompt with a runner template:

1. Grab the **prompt** from [`recipes/prompts/`](recipes/prompts/). Click the use case name in the matrix row header.
2. Grab the **runner template** from [`templates/`](templates/). Click the runner name in the matrix column header.
3. Follow the runner template's README for where to place the prompt and what to configure.
4. Each prompt notes its native runner and what to adapt for other runners (usually just output format and trigger wiring).

## Repo structure

```
templates/              Runner skeletons. How it runs.
  github-actions/         Copy .github/ files to repo
  gh-aw/                  Copy .github/workflows/*.md to repo
  cursor/                 Copy AGENTS.md to repo + UI setup
  claude-routine/
    skill/                Copy .claude/skills/ to repo
    scheduled-remote/     Register via MCP tool call (no files)

recipes/
  prompts/              Use-case prompts. What it does.
    blast-radius.md
    weekly-report/
    dead-code-cleanup.md
    rollback-check.md
  team-splitting/       Cross-cutting patterns for scoping by team.

examples/               Fully worked combos (runner + prompt + install README).
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
| Per-example secrets checklist | [`docs/secrets.md`](docs/secrets.md) |

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Pick a use case folder (or create one), add a runner sub-folder, include a `README.md` per leaf.

## License

MIT. See [`LICENSE`](LICENSE).
