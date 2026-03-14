import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// ハニーポットのURL
const HONEYPOT_PATH = '/api/v1/all-players-download.json';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const ip = request.ip || 'unknown';
  const userAgent = request.headers.get('user-agent') || 'unknown';

  // ハニープロットへのアクセスを検知
  if (pathname === HONEYPOT_PATH) {
    console.warn(`[BOT DETECTED] IP: ${ip}, UA: ${userAgent}, Path: ${pathname}`);
    
    // ボットと確定したアクセスには 403 を返す（または無限ループやダミーデータへ）
    return new NextResponse(
      JSON.stringify({ error: 'Access Denied', message: 'Automated collection is prohibited.' }),
      { 
        status: 403, 
        headers: { 'Content-Type': 'application/json' } 
      }
    );
  }

  // TODO: ここにIPベースのレート制限ロジックを追加可能
  // Vercel KV や Upstash を使うとセッションベースの Token Bucket も実装可能

  return NextResponse.next();
}

// ミドルウェアを適用するパス
export const config = {
  matcher: [
    /*
     * すべてのリクエストパスに対して実行（静的ファイル、画像等を除く）
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
