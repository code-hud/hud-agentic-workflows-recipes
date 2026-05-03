# Team Splitting — package.json

Discover team-to-services mapping at runtime by reading the `author` field of each service's `package.json`. Works for Node monorepos where ownership lives next to the code.

## Files

| Path | Purpose |
|---|---|
| `discover.py` | Walks `apps/*/package.json`, extracts `author`, groups services by team, writes JSON output |

This is the same pattern used in [`examples/weekly-report/gh-aw/`](../../../examples/weekly-report/gh-aw/) Phase 0, factored out as a standalone script.

## How to use

### 1. Make sure `package.json` has an `author`

Each service's `package.json` should set `author` either as an object or a string:

```json
{
  "name": "@org-name/api-gateway",
  "author": { "name": "Platform" }
}
```

```json
{
  "name": "@org-name/billing",
  "author": "Billing <billing@org-name.com>"
}
```

The script extracts the team name (stripping any `<email>` or `(url)` suffix) and normalizes it to a team key (lowercase, dashes).

### 2. Run the script in your workflow

```yaml
- name: Discover teams
  shell: bash
  run: python3 recipes/team-splitting/3-package-json/discover.py

- name: Read result
  shell: bash
  run: cat /tmp/team_services.json
```

The script writes JSON to `/tmp/team_services.json` (configurable via `--out`):

```json
{
  "platform": {
    "display_name": "Platform",
    "services": ["api-gateway", "auth-service"]
  }
}
```

### 3. CI scoping via env vars

| Env var | Effect |
|---|---|
| `HUD_TEAMS` | Comma-separated team keys to include |
| `HUD_SERVICES` | Comma-separated service names to include (filter within each team) |

These slot into the workflow inputs already in [`examples/weekly-report/gh-aw/`](../../../examples/weekly-report/gh-aw/).

### 4. Different repo layout

Default scans `apps/*/package.json`. For different roots:

```bash
python3 discover.py --root services --root packages
```

## When it breaks

- **Service ships without `author` populated.** It lands in the skipped list — surface this as a warning, not a hard fail, so the report still runs.
- **Two services with the same `author`.** They group together — that's the point. If they shouldn't, fix the `author` field, not the script.
- **Author field as raw email.** The string-form parser strips `<...>` so `"alice@org-name.com"` becomes empty. Use the object form (`{ "name": "Team", "email": "..." }`) when in doubt.

## When to pick this pattern

- You have a Node monorepo with `apps/*` (or similar) layout.
- `package.json` `author` is something engineers maintain (or you can lint it).
- You don't want a separate config file to keep in sync with the codebase.

## Adapting to other languages

The shape works for any language — just point the script at the right manifest:

- **Python**: read `pyproject.toml` `[project] authors`.
- **Go**: parse `go.mod` `module` line + a sibling `OWNERS` file.
- **JVM**: parse `pom.xml` `<developers>` or `build.gradle.kts` extra properties.

Same pattern, different parser.
