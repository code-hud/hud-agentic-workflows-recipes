#!/usr/bin/env python3
"""
Discover team-to-services mapping by reading the `author` field
of each service's package.json.

Walks `apps/*/package.json` (configurable), extracts the author name,
normalizes it to a team key (lowercase, dashes), groups services by team.

Usage:
    python3 discover.py
    python3 discover.py --root services --out /tmp/teams.json

Filters via env vars (CI-friendly):
    HUD_TEAMS    — comma-separated team keys to scope to
    HUD_SERVICES — comma-separated service names to scope to

Output format (written to --out, default /tmp/team_services.json):

    {
      "platform": {
        "display_name": "Platform",
        "services": ["api-gateway", "auth-service"]
      },
      "billing": {
        "display_name": "Billing",
        "services": ["invoice-service"]
      }
    }
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from typing import Any


def normalize_team_key(name: str) -> str:
    return name.lower().replace(" ", "-").replace("_", "-")


def extract_team(author: Any) -> str:
    """Pull the human team name out of an `author` field.
    Supports object form (`{name, email}`) and string form (`Team <email>`)."""
    if isinstance(author, dict):
        return (author.get("name") or "").strip()
    if isinstance(author, str):
        # Strip trailing "<email>" or "(url)"
        return author.split("<")[0].split("(")[0].strip()
    return ""


def discover(roots: list[str], out_path: str) -> dict[str, Any]:
    candidates: list[str] = []
    for root in roots:
        candidates.extend(glob.glob(f"{root}/*/package.json"))

    # Optional service filter (HUD_SERVICES env)
    services_filter = (os.environ.get("HUD_SERVICES") or "").strip()
    allowed_services: set[str] | None = (
        {s.strip() for s in services_filter.split(",") if s.strip()}
        if services_filter
        else None
    )

    # Optional team filter (HUD_TEAMS env)
    teams_filter = (os.environ.get("HUD_TEAMS") or "").strip()
    allowed_teams: set[str] | None = (
        {normalize_team_key(t) for t in teams_filter.split(",") if t.strip()}
        if teams_filter
        else None
    )

    teams: dict[str, dict[str, Any]] = {}
    skipped: list[tuple[str, str]] = []

    for pj in sorted(candidates):
        service_dir = os.path.basename(os.path.dirname(pj))

        if allowed_services is not None and service_dir not in allowed_services:
            continue

        try:
            with open(pj) as f:
                data = json.load(f)
        except Exception as e:
            skipped.append((service_dir, f"parse error: {e}"))
            continue

        team = extract_team(data.get("author"))
        if not team:
            skipped.append((service_dir, "no author field"))
            continue

        team_key = normalize_team_key(team)
        teams.setdefault(team_key, {"display_name": team, "services": []})
        teams[team_key]["services"].append(service_dir)

    # Apply team filter (after grouping, so we log requested teams that don't exist)
    if allowed_teams is not None:
        missing = allowed_teams - set(teams.keys())
        teams = {k: v for k, v in teams.items() if k in allowed_teams}
        if missing:
            print(f"WARNING: requested teams not found in repo: {sorted(missing)}")

    with open(out_path, "w") as f:
        json.dump(teams, f, indent=2)

    scope_note = (
        f" (filtered to {sorted(allowed_teams)})" if allowed_teams is not None else ""
    )
    print(f"Discovered {len(teams)} team(s){scope_note}:")
    for k, v in teams.items():
        print(f"  - {k} ({v['display_name']}): {', '.join(v['services'])}")

    if skipped:
        print("Skipped services (no team mapping):")
        for svc, reason in skipped:
            print(f"  - {svc}: {reason}")

    return teams


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--root",
        action="append",
        default=None,
        help="Root directory containing service folders (default: apps). Pass multiple times for multiple roots.",
    )
    p.add_argument(
        "--out",
        default="/tmp/team_services.json",
        help="Output JSON path (default: /tmp/team_services.json)",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if no teams are discovered (default: warn and exit 0 so the calling workflow can still run).",
    )
    args = p.parse_args()

    roots = args.root or ["apps"]
    teams = discover(roots, args.out)

    if not teams:
        msg = "No teams discovered."
        if args.strict:
            print(f"ERROR: {msg} Aborting.", file=sys.stderr)
            return 1
        print(f"WARNING: {msg} Wrote empty result to {args.out}.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
