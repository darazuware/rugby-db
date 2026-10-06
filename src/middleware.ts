import { defineMiddleware } from "astro:middleware";
import legacyRedirects from "../data/redirects.json";
import masterRedirects from "../data/master/_meta/redirects.json";
import retiredSlugs from "../data/master/_meta/retired_slugs.json";
import {
  canHaveIndividualPlayerPage,
  getAllPlayers,
  getPlayerSlugResolution,
  getTeamPagePaths,
  isIndexablePlayer,
  isIndexablePlayerSlug,
  playerFallbackPath,
} from "./lib/master";

// ハニーポットのURL (実データAPIと分離)
const HONEYPOT_PATH = '/api/v1/hidden-dataset.json';

// P2-4: 旧記事URL(legacy) + P1-4 移行(master旧slug→新slug)を統合。
// キーが重複する場合は master（新スキーマ側）を優先。
// キーは decode + 末尾スラッシュ除去で正規化（日本語/末尾/付きのキーが一致しない問題の対策）。
const redirects: Record<string, string> = {};
for (const [k, v] of Object.entries({
  ...(legacyRedirects as Record<string, string>),
  ...(masterRedirects as Record<string, string>),
})) {
  let key = k;
  try { key = decodeURIComponent(k); } catch { /* そのまま */ }
  redirects[key.replace(/\/$/, "")] = v;
}

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

// 01_DESIGN §2: 個別ページを持たない選手（非indexable・統合で消えた slug）の 301 先。
// 個別ページがある slug / master に存在しない slug は null（呼び出し側で通常処理）。
const PLAYER_PATH = /^\/players\/([^/]+)\/?$/;
async function resolvePlayerRedirect(path: string): Promise<string | null> {
  const m = PLAYER_PATH.exec(path);
  if (!m) return null;
  const slug = m[1];
  if (isIndexablePlayerSlug(slug)) return null;
  const player = (await getPlayerSlugResolution().catch(() => new Map())).get(slug);
  if (!player || player.league === "highschool") return null;
  if (isIndexablePlayer(player)) return `/players/${player.slug}/`; // 統合された旧 slug
  return playerFallbackPath(player, await getTeamPagePaths());
}

// redirects.json の行き先が master に存在しない選手 slug（ページ無し）か。
// 該当時は 404 を避けて一覧へ 301（事実は補完しない）。
async function isMissingPlayerPath(path: string): Promise<boolean> {
  const m = PLAYER_PATH.exec(path);
  if (!m) return false;
  const slug = m[1];
  if (isIndexablePlayerSlug(slug)) return false;
  const resolution = await getPlayerSlugResolution().catch(() => null);
  return !!resolution && !resolution.has(slug);
}

export const onRequest = defineMiddleware(async (context, next) => {
  const { url, request } = context;
  const pathname = url.pathname;
  
  // ハニーポットへのアクセスを検知
  // ヘッダーはここでのみ読む（プリレンダー時に Astro.request.headers 警告を出さないため）
  if (pathname === HONEYPOT_PATH) {
    const ip = request.headers?.get('x-forwarded-for') || 'unknown';
    const userAgent = request.headers?.get('user-agent') || 'unknown';
    console.warn(`[BOT DETECTED] IP: ${ip}, UA: ${userAgent}, Path: ${pathname}`);
    
    return new Response(
      JSON.stringify({ error: 'Access Denied', message: 'Automated collection is prohibited.' }),
      { 
        status: 403, 
        headers: { 'Content-Type': 'application/json' } 
      }
    );
  }

  // 高校生(hs-)選手は個別ページ無し（10のポリシー）→ 学校一覧へ301
  if (/^\/players\/hs-/.test(decodeURIComponent(pathname))) {
    return new Response(null, { status: 301, headers: { 'Location': '/schools/', 'Cache-Control': 'public, max-age=3600' } });
  }

  // リダイレクト処理
  const cleanPath = pathname.replace(/\/$/, "");
  const decodedPath = decodeURIComponent(cleanPath);
  const redirectTarget = (redirects as Record<string, string>)[cleanPath] || (redirects as Record<string, string>)[decodedPath];

  if (redirectTarget) {
    // 旧 /player/<slug>（廃止ルート）→ /players/<slug>、高校生(hs-)選手は個別ページ無し→学校一覧
    const legacy = /^\/player\/([^/]+)\/?$/.exec(redirectTarget);
    const normalized = legacy ? `/players/${legacy[1]}/` : redirectTarget;
    if (/^\/players\/hs-/.test(decodeURIComponent(normalized))) {
      return new Response(null, { status: 301, headers: { 'Location': '/schools/', 'Cache-Control': 'public, max-age=3600' } });
    }
    // 存在しないチームページ宛ての301は、リーグ一覧（mlrは一覧なし→/teams/）へ
    const tm = /^\/teams\/([^/]+)\/([^/]+)\/?$/.exec(redirectTarget);
    if (tm) {
      const live = new Set([...(await getTeamPagePaths().catch(() => new Map<string, string>())).values()].map((p) => p.replace(/\/$/, "")));
      if (live.size > 0 && !live.has(redirectTarget.replace(/\/$/, ""))) {
        const fb = tm[1] === "mlr" ? "/teams/" : `/teams/${tm[1]}/`;
        return new Response(null, { status: 301, headers: { 'Location': fb, 'Cache-Control': 'public, max-age=3600' } });
      }
    }
    if (legacy) {
      const t = (await resolvePlayerRedirect(normalized)) ?? ((await isMissingPlayerPath(normalized)) ? RETIRED_REDIRECT_TARGET : normalized);
      return new Response(null, { status: 301, headers: { 'Location': encodeURI(t), 'Cache-Control': 'public, max-age=3600' } });
    }
    // redirects.json の行き先が非indexable選手なら、1ホップで最終先へ
    const finalTarget =
      (await resolvePlayerRedirect(redirectTarget)) ??
      ((await isMissingPlayerPath(redirectTarget)) ? RETIRED_REDIRECT_TARGET : null);
    if (finalTarget) {
      return new Response(null, {
        status: 301,
        headers: { 'Location': encodeURI(finalTarget), 'Cache-Control': 'public, max-age=3600' },
      });
    }
    return new Response(null, {
      status: 301,
      headers: {
        'Location': redirectTarget,
        'Cache-Control': 'public, max-age=31536000, immutable'
      }
    });
  }

  // 非indexable選手・統合済みslug → チーム名簿アンカーへ301（基準変更で復活し得るので immutable にしない）
  const playerTarget = await resolvePlayerRedirect(decodedPath);
  if (playerTarget) {
    return new Response(null, {
      status: 301,
      headers: { 'Location': encodeURI(playerTarget), 'Cache-Control': 'public, max-age=3600' },
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
