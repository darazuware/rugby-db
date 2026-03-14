import { defineMiddleware } from "astro:middleware";

// ハニーポットのURL
const HONEYPOT_PATH = '/api/v1/all-players-download.json';

export const onRequest = defineMiddleware(async (context, next) => {
  const { url, request } = context;
  const pathname = url.pathname;
  
  // Vercel環境でのIP取得（context.clientAddress も使用可能）
  const ip = request.headers.get('x-forwarded-for') || 'unknown';
  const userAgent = request.headers.get('user-agent') || 'unknown';

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

  // 次の処理（ページレンダリング等）へ
  return next();
});
