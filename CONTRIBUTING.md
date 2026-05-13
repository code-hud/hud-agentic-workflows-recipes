# Contributing

Thanks for contributing. Every leaf folder should make sense on its own, even when linked directly.

## Adding a new example

1. Pick a use case. If it's new, create `examples/<use-case-slug>/`. If it's a new runner variant of an existing use case, add it under the existing folder.
2. Inside the use-case folder, create a sub-folder per runner: `github-actions/`, `gh-aw/`, `cursor/`, or `claude-routine/`.
3. Drop the workflow files in. For most runners this is a single workflow file + prompt + a `README.md`.
4. Write a `README.md` at the runner-folder level. It **must** include a standardized `## How to install` table at the top:
   ```markdown
   ## How to install

   | Step | Action |
   |---|---|
   | **Copy to your repo** | Copy `path/to/file` into your repo at the same path |
   | **Configure in UI** | *(none)* or numbered steps |
   | **Set secrets** | `SECRET_NAME` (where to get it) |
   ```
   After the install block, answer:
   - **What does this do?** (one sentence)
   - **How do I verify it works?** (3-step test)
5. Write a `README.md` at the use-case level if there are multiple runner variants. Link to each.
6. Update the [matrix](README.md#the-matrix) in the root README to add the new cell.

## Adding a new template

Templates are blank skeletons (Hud + a runner, no task). Add under `templates/<runner>/`. Include a `README.md` with the same `## How to install` table format. For Cursor templates, ship an `AGENTS.md` (copyable to repo root); for other runners, ship the actual config files at their target paths.

## Adding a new recipe

Recipes are cross-cutting patterns (e.g. team-splitting strategies, secret rotation, monorepo path detection). They plug into multiple examples without being workflows themselves. Add under `recipes/<pattern-name>/`.

## Style

- Per-leaf `README.md` is mandatory. Anyone landing on the leaf via a deep link should not need to read the parent README to understand what they're looking at.
- Sanitize org-specific values. Use `org-name` (GitHub org slug), `org-name.atlassian.net` (Jira host), and `ORG` (Jira project key) as placeholders.
- Auth: always `HUD_MCP_KEY` + `npx -y hud-mcp@v2`. Do not use OIDC token-exchange patterns.
- Models: prefer `sonnet` as the default; document Bedrock alternatives in the README, don't fork the workflow.

## What goes where (decision tree)

```
Is it a workflow that runs end-to-end on its own?            → examples/<use-case>/<runner>/
Is it a blank skeleton with no task content?                 → templates/<runner>/
Is it a pattern shared by multiple workflows?                → recipes/<pattern>/
Is it a doc that doesn't sit beside code?                    → docs/
```

## Out of scope (for now)

- Languages / SDK detection beyond what's already covered.
- Multi-repo installs.
- Org-specific bundles.
