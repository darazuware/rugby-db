export const prerender = true;
import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import teamsData from '../../../../data/teams.json';

export const GET: APIRoute = async () => {
  try {
    const allPlayers = await getCollection('players');
    
    // チーム名からディビジョンへのマッピング作成
    const teamToDivision: Record<string, string> = {};
    (teamsData as any[]).forEach((t: any) => {
        if (t.team_name && t.division) {
            teamToDivision[t.team_name.trim()] = t.division.trim();
        }
    });

    const data = allPlayers.map(p => {
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

    return new Response(
      JSON.stringify(data),
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
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
