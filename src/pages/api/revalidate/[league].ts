/**
 * ISR On-Demand Revalidation endpoint.
 *
 * POST /api/revalidate/<league>
 * Header: x-revalidate-secret: <REVALIDATE_SECRET env var>
 *
 * Triggers Vercel ISR revalidation by fetching each affected page
 * with the `x-prerender-revalidate` bypass token header.
 * Requires `isr.bypassToken` set in astro.config.mjs.
 */

import type { APIRoute } from "astro";
import { VALID_LEAGUES, type LeagueId } from "../../../lib/schemas/standings";

const LEAGUE_PATHS: Record<LeagueId, string[]> = {
  "league-one":  ["/standings", "/leagues/league-one",  "/teams/league-one"],
  "top14":       ["/standings", "/leagues/top14",        "/teams/top14"],
  "urc":         ["/standings", "/leagues/urc",          "/teams/urc"],
  "super-rugby": ["/standings", "/leagues/super-rugby",  "/teams/super-rugby"],
  "premiership": ["/standings", "/leagues/premiership",  "/teams/premiership"],
};

export const POST: APIRoute = async ({ params, request }) => {
  const secret = request.headers.get("x-revalidate-secret");
  if (!secret || secret !== import.meta.env.REVALIDATE_SECRET) {
    return new Response(
      JSON.stringify({ error: "Unauthorized" }),
      { status: 401, headers: { "Content-Type": "application/json" } }
    );
  }

  const league = params.league as string;
  if (!VALID_LEAGUES.includes(league as LeagueId)) {
    return new Response(
      JSON.stringify({ error: `Unknown league: ${league}` }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  const paths = LEAGUE_PATHS[league as LeagueId];
  const origin = new URL(request.url).origin;

  // Trigger Vercel ISR revalidation via bypass token on each affected page
  const results = await Promise.allSettled(
    paths.map(path =>
      fetch(`${origin}${path}`, {
        headers: { "x-prerender-revalidate": secret },
      })
    )
  );

  const failed = results
    .map((r, i) => ({ path: paths[i], r }))
    .filter(({ r }) => r.status === "rejected" || (r.status === "fulfilled" && !r.value.ok))
    .map(({ path }) => path);

  if (failed.length > 0) {
    console.warn(`[revalidate] Failed paths: ${failed.join(", ")}`);
  }

  console.log(`[revalidate] Triggered ISR for league=${league}, paths=${paths.join(", ")}`);

  return new Response(
    JSON.stringify({ revalidated: true, league, paths }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
};

export const GET: APIRoute = () =>
  new Response(
    JSON.stringify({ error: "Method not allowed. Use POST." }),
    { status: 405, headers: { "Content-Type": "application/json" } }
  );
