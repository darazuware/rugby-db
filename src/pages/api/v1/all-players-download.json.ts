export const prerender = true;
import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import teamsData from '../../../../data/teams.json';
import { getMasterPlayersLegacyShape, masterCoveredLegacyLeagues } from '../../../lib/masterAdapters';

export const GET: APIRoute = async () => {
  try {
    // 1. master (SSOT) 対応済みリーグの選手（04/P2-3: league-one のみ。masterAdapters.ts 参照）
    const coveredLeagues = masterCoveredLegacyLeagues();
    const masterDataLists = await Promise.all(
      coveredLeagues.map((league) => getMasterPlayersLegacyShape(league)),
    );
    const masterData = masterDataLists.flat();
    const coveredWithData = new Set(
      coveredLeagues.filter((_, i) => masterDataLists[i].length > 0),
    );

    // 2. master 未対応リーグ分は既存 content collection から（重複防止のため対応済みリーグは除外）
    const allPlayers = await getCollection('players');

    // チーム名からディビジョンへのマッピング作成
    const teamToDivision: Record<string, string> = {};
    (teamsData as any[]).forEach((t: any) => {
        if (t.team_name && t.division) {
            teamToDivision[t.team_name.trim()] = t.division.trim();
        }
    });

    const legacyData = allPlayers
      .filter((p) => !coveredWithData.has((p.data.league || '').trim()))
      .map(p => {
      const normalizedTeamName = p.data.team?.trim() || "";
      const division = (normalizedTeamName ? teamToDivision[normalizedTeamName] : "") || p.data.division || "";

      // スラグをフラットに変換（ディレクトリ名を除去）
      const parts = p.slug.split('/');
      const flatSlug = parts[parts.length - 1];

      return {
        slug: flatSlug,
        data: {
          ...p.data,
          division: division
        }
      };
    });

    const data = [...masterData, ...legacyData];

    return new Response(
      JSON.stringify(data),
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Cache-Control': 'public, max-age=3600, s-maxage=86400, stale-while-revalidate=604800'
        }
      }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ status: "error", message: "Failed to fetch player data" }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
};
