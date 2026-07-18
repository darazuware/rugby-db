import { defineMiddleware } from "astro:middleware";
import legacyRedirects from "../data/redirects.json";
import masterRedirects from "../data/master/_meta/redirects.json";
import retiredSlugs from "../data/master/_meta/retired_slugs.json";

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
  if (retiredSlugSet.has(cleanPath) || retiredSlugSet.has(decodedPath)) {
    return new Response(null, {
      status: 301,
      headers: {
        'Location': RETIRED_REDIRECT_TARGET,
        'Cache-Control': 'public, max-age=3600'
      }
    });
  }

  // 次の処理（ページレンダリング等）へ
  return next();
});
