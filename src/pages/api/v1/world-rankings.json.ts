import type { APIRoute } from 'astro';
import { getWorldRankings } from '../../../lib/worldRankings';

export const GET: APIRoute = async () => {
  const data = await getWorldRankings();
  const isLive = data.source === 'live';

  return new Response(JSON.stringify(data), {
    headers: {
      'Content-Type': 'application/json',
      // ライブ取得時は1時間キャッシュ、フォールバック時は10分
      'Cache-Control': isLive
        ? 'public, s-maxage=3600, stale-while-revalidate=86400'
        : 'public, s-maxage=600, stale-while-revalidate=3600',
      'X-Data-Source': data.source ?? 'unknown',
    },
  });
};
