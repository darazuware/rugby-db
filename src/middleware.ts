import { defineMiddleware } from "astro:middleware";
import legacyRedirects from "../data/redirects.json";
import masterRedirects from "../data/master/_meta/redirects.json";
import retiredSlugs from "../data/master/_meta/retired_slugs.json";
import { canHaveIndividualPlayerPage, getAllPlayers } from "./lib/master";

// ハニーポットのURL (実データAPIと分離)
const HONEYPOT_PATH = '/api/v1/hidden-dataset.json';

// P2-4: 旧記事URL(legacy) + P1-4 移行(master旧slug→新slug)を統合。
// キーが重複する場合は master（新スキーマ側）を優先。
const redirects: Record<string, string> = {
  ...(legacyRedirects as Record<string, string>),
  ...(masterRedirects as Record<string, string>),
};

// P1-4 退避リスト（旧地域リーグ/個別高校大学ページ・未整備プロリーグ選手など、
// master化していない旧slug）。個別ページは復元しないため一覧ページへ301集約する（04）。
const retiredSlugSet = new Set(retiredSlugs as string[]);
const RETIRED_REDIRECT_TARGET = "/players";

// P4-6: 退避リスト作成（P1-4）当時 master 未整備だった旧 pro slug（super-rugby /
// urc / premiership 等）は、その後のスクレイパー整備で master に実ページを持ち得る。
// 現行 master に存在する slug は退避 301 の対象から除外する（実ページ優先）。
// master 読み込みは退避リスト該当時のみ・初回のみ（以後キャッシュ）。読み込み不能な
// 環境では空集合になり従来どおり 301 する（保守的フォールバック）。
let currentPlayerPathsPromise: Promise<Set<string>> | null = null;
function getCurrentPlayerPaths(): Promise<Set<string>> {
  if (!currentPlayerPathsPromise) {
    currentPlayerPathsPromise = getAllPlayers()
      .then(
        (players) =>
          new Set(
            players
              .filter(canHaveIndividualPlayerPage)
              .map((p) => `/players/${p.slug}`),
          ),
      )
      .catch(() => new Set<string>());
  }
  return currentPlayerPathsPromise;
}

export const onRequest = defineMiddleware(async (context, next) => {
  const { url, request } = context;
  const pathname = url.pathname;
  
  // Vercel環境でのIP取得 (ビルド時は null または unknown になる可能性があるためガード)
  const ip = request.headers?.get('x-forwarded-for') || 'unknown';
  const userAgent = request.headers?.get('user-agent') || 'unknown';

  // ハニーポットへのアクセスを検知
  if (pathname === HONEYPOT_PATH) {
    console.warn(`[BOT DETECTED] IP: ${ip}, UA: ${userAgent}, Path: ${pathname}`);
    
    return new Response(
      JSON.stringify({ error: 'Access Denied', message: 'Automated collection is prohibited.' }),
      { 
        status: 403, 
        headers: { 'Content-Type': 'application/json' } 
      }
    );
  }

  // リダイレクト処理
  const cleanPath = pathname.replace(/\/$/, "");
  const decodedPath = decodeURIComponent(cleanPath);
  const redirectTarget = (redirects as Record<string, string>)[cleanPath] || (redirects as Record<string, string>)[decodedPath];

  if (redirectTarget) {
    return new Response(null, {
      status: 301,
      headers: {
        'Location': redirectTarget,
        'Cache-Control': 'public, max-age=31536000, immutable'
      }
    });
  }

  // P2-4: 退避リスト（master未整備の旧slug）は一覧ページへ301集約（404回避・04）
  // P4-6: ただし現行 master に実ページがある slug は 301 しない（上記コメント参照）
  if (retiredSlugSet.has(cleanPath) || retiredSlugSet.has(decodedPath)) {
    const currentPaths = await getCurrentPlayerPaths();
    if (!currentPaths.has(cleanPath) && !currentPaths.has(decodedPath)) {
      return new Response(null, {
        status: 301,
        headers: {
          'Location': RETIRED_REDIRECT_TARGET,
          'Cache-Control': 'public, max-age=3600'
        }
      });
    }
  }

  // 次の処理（ページレンダリング等）へ
  return next();
});
