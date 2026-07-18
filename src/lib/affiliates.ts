// src/lib/affiliates.ts
// P4-1: アフィリエイトリンク一元管理。ASP変更・URL差替は本ファイルのみで完結させる。
// 参照: docs/renewal/07_AFFILIATE.md
//
// 重要: URLは全てプレースホルダー（#TODO_ASP_URL）。
// 実際のアフィリエイトリンクはユーザーがASP管理画面から取得し、本ファイルに直接貼ること。
// AIはこのファイルに実IDを書かない。

export const AFFILIATE_LINK_ATTRS = {
    rel: "sponsored noopener",
    target: "_blank",
} as const;

export interface WatchProvider {
    id: string;
    name: string;
    /** ASP経由の視聴導線URL。本番URLはユーザーが貼るまでプレースホルダーのまま。 */
    url: string;
}

// 視聴サービス定義（ASP切替時はここだけ差し替える）
export const WATCH_PROVIDERS: Record<string, WatchProvider> = {
    dazn: { id: "dazn", name: "DAZN", url: "#TODO_ASP_URL" },
    jsports: { id: "jsports", name: "J SPORTS", url: "#TODO_ASP_URL" },
    wowow: { id: "wowow", name: "WOWOW", url: "#TODO_ASP_URL" },
    skyperfectv: { id: "skyperfectv", name: "スカパー!", url: "#TODO_ASP_URL" },
};

// リーグID → 視聴サービス対応表
export const LEAGUE_WATCH_MAP: Record<string, string[]> = {
    "league-one": ["jsports", "dazn"],
    "league-one-d1": ["jsports", "dazn"],
    "league-one-d2": ["jsports", "dazn"],
    "league-one-d3": ["jsports", "dazn"],
    "top14": ["dazn"],
    "super-rugby": ["wowow"],
    "urc": ["dazn"],
    "premiership": ["dazn"],
};

/**
 * リーグIDから視聴サービス一覧を返す。
 * league-one-d1 等の未登録派生IDは "league-one" にフォールバックする。
 */
export function getWatchProviders(leagueId?: string | null): WatchProvider[] {
    if (!leagueId) return [];
    const providerIds =
        LEAGUE_WATCH_MAP[leagueId] ??
        (leagueId.startsWith("league-one") ? LEAGUE_WATCH_MAP["league-one"] : undefined);
    if (!providerIds) return [];
    return providerIds.map((id) => WATCH_PROVIDERS[id]).filter((p): p is WatchProvider => Boolean(p));
}

// PR表記の共通文言（景表法ステマ規制対応）
export const PR_NOTICE_TEXT = "本ページにはプロモーションが含まれます";
