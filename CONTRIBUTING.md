# Contributing

Thanks for adding to the playbook. The repo is organized for **readers landing from a Slack share** — every leaf folder should make sense on its own.

## Adding a new example

1. Pick a use case. If it's new, create `examples/<use-case-slug>/`. If it's a new platform variant of an existing use case, add it under the existing folder.
2. Inside the use-case folder, create a sub-folder per platform: `gh-aw/`, `github-actions/`, `cursor/`, or `claude-routine/`.
3. Drop the workflow files in. For most platforms this is a single workflow file + prompt + a `README.md`.
4. Write a `README.md` at the platform-folder level. It should answer:
   - **What does this do?** (one sentence)
   - **What secrets does it need?** (table)
   - **Where do the files go in the customer repo?** (paths)
   - **How do I verify it works?** (3-step test)
5. Write a `README.md` at the use-case level if there are multiple platform variants — link to each.

## Adding a new template

Templates are blank skeletons (Hud + a model, no task). Add under `templates/<platform>/`. Include a `README.md` that says: "drop your prompt here," "set these secrets," "run with this command."

## Adding a new recipe

Recipes are cross-cutting patterns — e.g. team-splitting strategies, secret rotation, monorepo path detection. They plug into multiple examples without being workflows themselves. Add under `recipes/<pattern-name>/`.

## Style

- Per-leaf `README.md` is mandatory. Anyone landing on the leaf via a deep link should not need to read the parent README to understand what they're looking at.
- Sanitize customer specifics. Use `acme`, `acme-org`, `acme.atlassian.net`, `ACME` (Jira project key) as placeholders.
- Auth: always `HUD_MCP_KEY` + `npx -y hud-mcp@v2`. **Never** ship OIDC token-exchange patterns against Hud — that's a legacy and always wrong.
- Models: prefer `sonnet` as the default; document Bedrock alternatives in the README, don't fork the workflow.

## What goes where (decision tree)

```
Is it a workflow that runs end-to-end on its own?            → examples/<use-case>/<platform>/
Is it a blank skeleton with no task content?                 → templates/<platform>/
Is it a pattern shared by multiple workflows?                → recipes/<pattern>/
Is it a doc that doesn't sit beside code?                    → docs/
```

## Out of scope (for now)

- Languages / SDK detection beyond what's already covered.
- Multi-repo installs.
- Customer-specific bundles. (These live in the internal `customer-ops-scripts/per-company/` folder, not here.)
