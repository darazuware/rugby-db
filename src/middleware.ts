import { defineMiddleware } from "astro:middleware";
import redirects from "../data/redirects.json";

// ハニーポットのURL (実データAPIと分離)
const HONEYPOT_PATH = '/api/v1/hidden-dataset.json';

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

  // 次の処理（ページレンダリング等）へ
  return next();
});
