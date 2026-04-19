import { z } from "zod";
import {
  StandingEntrySchema,
  CompetitionStandingsSchema,
  StandingsFileSchema,
  type StandingEntry,
  type CompetitionStandings,
  type LeagueId,
} from "./schemas/standings";

// Empty fallback returned when data is missing / invalid
const EMPTY_COMPETITION: CompetitionStandings = {
  sport_type:  "rugby_union",
  competition: "unknown",
  season:      "",
  updated_at:  "",
  standings:   [],
  results:     [],
};

/**
 * Lenient schema for reading — accepts the legacy format that lacks metadata.
 * sport_type / competition / season / updated_at default to safe values so the
 * site never crashes on a pre-migration standings.json.
 */
const LenientCompetitionSchema = z.object({
  sport_type:  z.string().optional().default("rugby_union"),
  competition: z.string().optional().default(""),
  season:      z.string().optional().default(""),
  updated_at:  z.string().optional().default(""),
  standings:   z.array(StandingEntrySchema).optional().default([]),
  results:     z.array(z.any()).optional().default([]),
  error:       z.string().optional(),
});

/**
 * Parse the full standings.json with Zod safeParse.
 * Never throws — returns an object with empty league data on failure.
 */
export function loadStandingsFile(raw: unknown): Record<LeagueId, CompetitionStandings> {
  const leagues: LeagueId[] = ["league-one", "top14", "urc", "super-rugby", "premiership"];
  const out = {} as Record<LeagueId, CompetitionStandings>;

  if (!raw || typeof raw !== "object") {
    console.error("[safeStandings] standings.json is not an object, using empty fallback.");
    for (const id of leagues) out[id] = { ...EMPTY_COMPETITION, competition: id };
    return out;
  }

  for (const id of leagues) {
    const leagueRaw = (raw as Record<string, unknown>)[id];
    out[id] = _parseLeagueBlock(leagueRaw, id);
  }

  return out;
}

/**
 * Extract the standings array for a single league safely.
 * Handles both the new format (with sport_type/competition/season/updated_at)
 * and the legacy format ({ standings: [...], results: [...] }).
 * Falls back to [] on any failure — never throws.
 */
export function getLeagueStandings(raw: unknown, leagueId: LeagueId): StandingEntry[] {
  if (!raw || typeof raw !== "object") return [];

  const leagueRaw = (raw as Record<string, unknown>)[leagueId];
  return _parseLeagueBlock(leagueRaw, leagueId).standings;
}

// ---------------------------------------------------------------------------
// Internal
// ---------------------------------------------------------------------------

function _parseLeagueBlock(leagueRaw: unknown, leagueId: LeagueId): CompetitionStandings {
  if (!leagueRaw) return { ...EMPTY_COMPETITION, competition: leagueId };

  // Legacy format: the value is a plain array of standings
  if (Array.isArray(leagueRaw)) {
    return _parseStandingsArray(leagueRaw, leagueId);
  }

  // Try full / lenient parse
  const result = LenientCompetitionSchema.safeParse(leagueRaw);
  if (!result.success) {
    console.error(`[safeStandings] ${leagueId} parse error:`, result.error.issues.slice(0, 2));
    return { ...EMPTY_COMPETITION, competition: leagueId };
  }

  return {
    sport_type:  "rugby_union",
    competition: result.data.competition || leagueId,
    season:      result.data.season,
    updated_at:  result.data.updated_at,
    standings:   result.data.standings,
    results:     result.data.results,
    error:       result.data.error,
  };
}

function _parseStandingsArray(arr: unknown[], leagueId: LeagueId): CompetitionStandings {
  const entries: StandingEntry[] = [];
  for (const item of arr) {
    const r = StandingEntrySchema.safeParse(item);
    if (r.success) entries.push(r.data);
  }
  return { ...EMPTY_COMPETITION, competition: leagueId, standings: entries };
}

export type { StandingEntry, CompetitionStandings, LeagueId };
