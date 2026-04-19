/**
 * ISR On-Demand Revalidation endpoint.
 *
 * Called after standings data is updated to purge only the affected league's
 * cached pages on Vercel, without a full redeploy.
 *
 * Usage:
 *   POST /api/revalidate/<league>
 *   Header: x-revalidate-secret: <REVALIDATE_SECRET env var>
 *
 * On success:
 *   { revalidated: true, league, paths }
 *
 * Required env vars (set in Vercel dashboard):
 *   REVALIDATE_SECRET  — shared secret to authenticate the request
 *   VERCEL_TOKEN       — Vercel API token with deployment scope
 *   VERCEL_TEAM_ID     — (optional) team slug / ID if project is under a team
 *   VERCEL_PROJECT_ID  — Vercel project ID
 */

import type { APIRoute } from "astro";
import { VALID_LEAGUES, type LeagueId } from "../../../lib/schemas/standings";

// Pages to revalidate per league — add any new routes that consume standings
const LEAGUE_PATHS: Record<LeagueId, string[]> = {
  "league-one":  ["/standings", "/leagues/league-one",  "/teams/league-one"],
  "top14":       ["/standings", "/leagues/top14",        "/teams/top14"],
  "urc":         ["/standings", "/leagues/urc",          "/teams/urc"],
  "super-rugby": ["/standings", "/leagues/super-rugby",  "/teams/super-rugby"],
  "premiership": ["/standings", "/leagues/premiership",  "/teams/premiership"],
};

export const POST: APIRoute = async ({ params, request }) => {
  // ── Auth ─────────────────────────────────────────────────────────────────
  const secret = request.headers.get("x-revalidate-secret");
  if (!secret || secret !== import.meta.env.REVALIDATE_SECRET) {
    return new Response(
      JSON.stringify({ error: "Unauthorized" }),
      { status: 401, headers: { "Content-Type": "application/json" } }
    );
  }

  // ── Validate league param ─────────────────────────────────────────────────
  const league = params.league as string;
  if (!VALID_LEAGUES.includes(league as LeagueId)) {
    return new Response(
      JSON.stringify({ error: `Unknown league: ${league}` }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  const paths = LEAGUE_PATHS[league as LeagueId];

  // ── Vercel On-Demand Revalidation ─────────────────────────────────────────
  const token     = import.meta.env.VERCEL_TOKEN;
  const projectId = import.meta.env.VERCEL_PROJECT_ID;
  const teamId    = import.meta.env.VERCEL_TEAM_ID;   // optional

  if (!token || !projectId) {
    // Missing env vars: log but don't crash (useful in local dev)
    console.warn("[revalidate] VERCEL_TOKEN or VERCEL_PROJECT_ID not set — skipping purge.");
    return new Response(
      JSON.stringify({ revalidated: true, league, paths, note: "env vars missing, purge skipped" }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  }

  const teamParam = teamId ? `?teamId=${encodeURIComponent(teamId)}` : "";
  const purgeUrl  = `https://api.vercel.com/v1/data-cache/purge-tags${teamParam}`;

  try {
    const purgeResp = await fetch(purgeUrl, {
      method: "DELETE",
      headers: {
        Authorization:  `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ projectId, tags: [`standings-${league}`, "standings"] }),
    });

    if (!purgeResp.ok) {
      const body = await purgeResp.text();
      console.error(`[revalidate] Vercel purge failed (${purgeResp.status}): ${body}`);
      return new Response(
        JSON.stringify({ error: "Vercel purge failed", status: purgeResp.status }),
        { status: 502, headers: { "Content-Type": "application/json" } }
      );
    }

    console.log(`[revalidate] Purged cache for league=${league}, paths=${paths.join(", ")}`);

    return new Response(
      JSON.stringify({ revalidated: true, league, paths }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );
  } catch (err) {
    console.error("[revalidate] Unexpected error:", err);
    return new Response(
      JSON.stringify({ error: "Internal error" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
};

// Reject non-POST methods
export const GET: APIRoute = () =>
  new Response(
    JSON.stringify({ error: "Method not allowed. Use POST." }),
    { status: 405, headers: { "Content-Type": "application/json" } }
  );
