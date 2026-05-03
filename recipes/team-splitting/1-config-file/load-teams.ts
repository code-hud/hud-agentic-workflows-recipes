/**
 * Load a teams-to-services mapping from a YAML config file.
 *
 * Usage:
 *   const teams = loadTeams('.github/teams.yaml');
 *   const platformServices = teams.platform.services;
 *   const isBillingMember = teams.billing.members.includes(actor);
 *
 * Filters via env vars (CI-friendly):
 *   HUD_TEAMS    — comma-separated team keys to scope to
 *   HUD_SERVICES — comma-separated service names to scope to
 */

import * as fs from 'node:fs';
import * as yaml from 'js-yaml';

export interface Team {
  display_name: string;
  slack_channel?: string;
  services: string[];
  members?: string[];
}

export type TeamsMap = Record<string, Team>;

export function loadTeams(path: string): TeamsMap {
  const raw = fs.readFileSync(path, 'utf-8');
  const parsed = yaml.load(raw) as TeamsMap;

  if (!parsed || typeof parsed !== 'object') {
    throw new Error(`teams config at ${path} is empty or invalid`);
  }

  // Apply HUD_TEAMS filter from env if present (CI scoping).
  const teamsFilter = (process.env.HUD_TEAMS || '').trim();
  const allowedTeams = teamsFilter
    ? new Set(teamsFilter.split(',').map((t) => t.trim()).filter(Boolean))
    : null;

  // Apply HUD_SERVICES filter from env if present (filters services within each team).
  const servicesFilter = (process.env.HUD_SERVICES || '').trim();
  const allowedServices = servicesFilter
    ? new Set(servicesFilter.split(',').map((s) => s.trim()).filter(Boolean))
    : null;

  const filtered: TeamsMap = {};
  for (const [key, team] of Object.entries(parsed)) {
    if (allowedTeams && !allowedTeams.has(key)) continue;

    const services = allowedServices
      ? team.services.filter((s) => allowedServices.has(s))
      : team.services;

    if (services.length === 0) continue;
    filtered[key] = { ...team, services };
  }

  return filtered;
}

/** Resolve which team owns a given service. Returns null if unmapped. */
export function teamForService(teams: TeamsMap, service: string): string | null {
  for (const [key, team] of Object.entries(teams)) {
    if (team.services.includes(service)) return key;
  }
  return null;
}

/** Resolve which team a GitHub actor belongs to. Returns null if not mapped. */
export function teamForActor(teams: TeamsMap, actor: string): string | null {
  for (const [key, team] of Object.entries(teams)) {
    if (team.members?.includes(actor)) return key;
  }
  return null;
}

// CLI entry point: print resolved teams as JSON.
//   npx tsx load-teams.ts .github/teams.yaml
if (require.main === module) {
  const path = process.argv[2] || '.github/teams.yaml';
  const teams = loadTeams(path);
  console.log(JSON.stringify(teams, null, 2));
}
