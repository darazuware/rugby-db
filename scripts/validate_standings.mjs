/**
 * CI gate: validates data/standings.json against the Zod schema (Zod v4).
 * Run after scrape_standings.py and before `astro build`.
 *
 * Exit codes:
 *   0 — all leagues valid
 *   1 — validation failures found
 *
 * Usage:
 *   node scripts/validate_standings.mjs
 *   node scripts/validate_standings.mjs --warn   # warn only, don't exit 1
 */

import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { z } from "zod";

const __dirname = dirname(fileURLToPath(import.meta.url));
const WARN_ONLY  = process.argv.includes("--warn");
const DATA_PATH  = resolve(__dirname, "../data/standings.json");

// ---------------------------------------------------------------------------
// Helpers for Zod v4 — coerce numeric fields that may arrive as strings
// ---------------------------------------------------------------------------

const coerceInt = (v) => {
  if (v === null || v === undefined || v === "") return 0;
  const n = typeof v === "number" ? v : parseInt(String(v).trim(), 10);
  return isNaN(n) ? 0 : Math.max(0, n);
};

const coerceOptionalInt = (v) => {
  if (v === null || v === undefined || v === "") return undefined;
  const n = typeof v === "number" ? v : parseInt(String(v).trim(), 10);
  return isNaN(n) ? undefined : Math.max(0, n);
};

// Zod v4: use preprocess for coercion before type checking
const CoercedInt = z.preprocess(coerceInt, z.number().int().nonnegative());
const CoercedOptionalInt = z.preprocess(coerceOptionalInt, z.number().int().nonnegative().optional());

// ---------------------------------------------------------------------------
// Schema definitions
// ---------------------------------------------------------------------------

const StandingEntrySchema = z.object({
  rank:         CoercedInt,
  team_name:    z.string().min(1),
  display_name: z.string().optional(),
  flag:         z.string().optional(),
  slug:         z.string().min(1),
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

const CompetitionStandingsSchema = z.object({
  sport_type:  z.literal("rugby_union"),
  competition: z.string(),
  season:      z.string(),
  updated_at:  z.string(),
  standings:   z.array(StandingEntrySchema),
  results:     z.array(z.any()).optional().default([]),
  error:       z.string().optional(),
});

const VALID_LEAGUES = ["league-one", "top14", "urc", "super-rugby", "premiership"];

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

let raw;
try {
  raw = JSON.parse(readFileSync(DATA_PATH, "utf8"));
} catch (err) {
  console.error(`[validate_standings] Cannot read ${DATA_PATH}:`, err.message);
  process.exit(1);
}

let failures = 0;

for (const league of VALID_LEAGUES) {
  const leagueData = raw[league];

  if (!leagueData) {
    console.warn(`[validate_standings] MISSING league: ${league}`);
    failures++;
    continue;
  }

  const result = CompetitionStandingsSchema.safeParse(leagueData);

  if (!result.success) {
    const issues = result.error.issues;
    console.error(`[validate_standings] FAIL ${league}: ${issues.length} issue(s)`);
    issues.slice(0, 5).forEach((issue) => {
      console.error(`  ↳ ${(issue.path || []).join(".")} — ${issue.message}`);
    });
    failures++;
    continue;
  }

  const count    = result.data.standings.length;
  const errNote  = result.data.error ? ` [scrape error: ${result.data.error}]` : "";
  console.log(`[validate_standings] OK  ${league.padEnd(14)} — ${count} teams${errNote}`);
}

if (failures > 0) {
  console.error(`\n[validate_standings] ${failures} league(s) failed validation.`);
  if (!WARN_ONLY) process.exit(1);
} else {
  console.log("\n[validate_standings] All leagues passed.");
}
