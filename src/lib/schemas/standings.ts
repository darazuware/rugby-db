import { z } from "zod";

// ---------------------------------------------------------------------------
// Coercion helpers — accept both string and number (backward compat)
// ---------------------------------------------------------------------------

const coerceInt = (v: unknown): number => {
  if (v === null || v === undefined || v === "") return 0;
  const n = typeof v === "number" ? v : parseInt(String(v).trim(), 10);
  return isNaN(n) ? 0 : Math.max(0, n);
};

const coerceOptionalInt = (v: unknown): number | undefined => {
  if (v === null || v === undefined || v === "") return undefined;
  const n = typeof v === "number" ? v : parseInt(String(v).trim(), 10);
  return isNaN(n) ? undefined : Math.max(0, n);
};

const CoercedInt = z.preprocess(coerceInt, z.number().int().nonnegative());
const CoercedOptionalInt = z.preprocess(coerceOptionalInt, z.number().int().nonnegative().optional());

// ---------------------------------------------------------------------------
// Standing entry
// ---------------------------------------------------------------------------

export const StandingEntrySchema = z.object({
  rank:         CoercedInt,
  team_name:    z.string(),
  display_name: z.string().optional(),
  flag:         z.string().optional(),
  slug:         z.string(),
  played:       CoercedInt,
  won:          CoercedInt,
  drawn:        CoercedInt,
  lost:         CoercedInt,
  diff:         z.union([z.string(), z.number()]).transform(String),
  points:       CoercedInt,
  try_bonus:    CoercedOptionalInt,
  losing_bonus: CoercedOptionalInt,
  division:     z.string().optional(),
});

export type StandingEntry = z.infer<typeof StandingEntrySchema>;

// ---------------------------------------------------------------------------
// Per-competition standings block (strict — enforces sport_type)
// ---------------------------------------------------------------------------

export const CompetitionStandingsSchema = z.object({
  sport_type:  z.literal("rugby_union"),
  competition: z.string(),
  season:      z.string(),
  updated_at:  z.string(),
  standings:   z.array(StandingEntrySchema),
  results:     z.array(z.any()).optional().default([]),
  error:       z.string().optional(),
});

export type CompetitionStandings = z.infer<typeof CompetitionStandingsSchema>;

// ---------------------------------------------------------------------------
// Root standings.json schema (partial — tolerates missing leagues)
// ---------------------------------------------------------------------------

export const StandingsFileSchema = z.object({
  "league-one":  CompetitionStandingsSchema,
  "top14":       CompetitionStandingsSchema,
  "urc":         CompetitionStandingsSchema,
  "super-rugby": CompetitionStandingsSchema,
  "premiership": CompetitionStandingsSchema,
}).partial();

export type StandingsFile = z.infer<typeof StandingsFileSchema>;

export const VALID_LEAGUES = ["league-one", "top14", "urc", "super-rugby", "premiership"] as const;
export type LeagueId = typeof VALID_LEAGUES[number];
