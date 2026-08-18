// src/lib/affiliates.ts
// P4-1: アフィリエイトリンク一元管理。ASP変更・URL差替は本ファイルのみで完結させる。
// 参照: docs/renewal/07_AFFILIATE.md
//
// 重要: 現在のURLは各サービスの公式サイト（アフィリエイトIDなし）。
// 実際のアフィリエイトリンクはユーザーがASP管理画面から取得し、本ファイルに直接貼ること。
// AIはこのファイルに実ID（ASPリンク）を書かない。

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
    dazn: { id: "dazn", name: "DAZN", url: "https://www.dazn.com/ja-JP/welcome" },
    jsports: { id: "jsports", name: "J SPORTS", url: "https://www.jsports.co.jp/rugby/" },
    wowow: { id: "wowow", name: "WOWOW", url: "https://www.wowow.co.jp/" },
    skyperfectv: { id: "skyperfectv", name: "スカパー!", url: "https://www.skyperfectv.co.jp/" },
};

// リーグID → 視聴サービス対応表
export const LEAGUE_WATCH_MAP: Record<string, string[]> = {
    "league-one": ["jsports", "dazn"],
    "league-one-d1": ["jsports", "dazn"],
    "league-one-d2": ["jsports", "dazn"],
    "league-one-d3": ["jsports", "dazn"],
    "top14": ["dazn"],
    "super-rugby": ["wowow"],
    // urc / premiership は国内視聴手段が未検証のため未登録（既存記事は「国内配信なし」と記載、
    // DAZN配信の根拠を確認できたら追加する）。未登録リーグはボタン非表示になる。
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

export interface AccommodationProvider {
    id: string;
    name: string;
    /** ASP経由の宿泊予約導線URL。本番URLはユーザーが貼るまでプレースホルダーのまま。 */
    url: string;
}

// 宿泊予約サービス定義（P4-2、参照: docs/renewal/07_AFFILIATE.md）
// エリア指定は data/manual/venue_areas.json を引いて呼び出し側が付与する（URL自体は固定プレースホルダー）。
export const ACCOMMODATION_PROVIDERS: Record<string, AccommodationProvider> = {
    rakutentravel: { id: "rakutentravel", name: "楽天トラベル", url: "https://travel.rakuten.co.jp/" },
    jalan: { id: "jalan", name: "じゃらん", url: "https://www.jalan.net/" },
};

/** 全宿泊予約サービスを返す（リーグ非依存、会場エリアが判明した試合/チームページでのみ表示する） */
export function getAccommodationProviders(): AccommodationProvider[] {
    return Object.values(ACCOMMODATION_PROVIDERS);
}

export interface MagazineProvider {
    id: string;
    name: string;
    /** キャンペーン等の訴求文言 */
    campaign: string;
    /** ASP経由の申込導線URL */
    url: string;
}

// 雑誌読み放題サービス（P4-7想定）。楽天マガジンのキャンペーンURLはユーザー提供の実リンク。
export const MAGAZINE_PROVIDERS: Record<string, MagazineProvider> = {
    rakutenmagazine: {
        id: "rakutenmagazine",
        name: "楽天マガジン",
        campaign: "今なら3ヶ月10円",
        url: "https://magazine.rakuten.co.jp/cpn/260730/?scid=af_ls_TG_2608cpn&argument=vqhTTgFN&dmai=a6a6197b22d8da",
    },
};

export function getMagazineProvider(id: string = "rakutenmagazine"): MagazineProvider {
    return MAGAZINE_PROVIDERS[id];
}

export interface FlightProvider {
    id: string;
    name: string;
    /** ASP経由の航空券検索導線URL。本番URLはユーザーが貼るまでプレースホルダーのまま。 */
    url: string;
}

// 海外宿泊予約サービス（P4-5）。venue_areas.json は国内会場のみのため、
// RWC2027（豪州）等の海外開催地ではこちらを使う。
export const OVERSEAS_ACCOMMODATION_PROVIDERS: Record<string, AccommodationProvider> = {
    agoda: { id: "agoda", name: "Agoda", url: "https://www.agoda.com/ja-jp/" },
    bookingcom: { id: "bookingcom", name: "Booking.com", url: "https://www.booking.com/index.ja.html" },
};

/** 海外宿泊予約サービス一覧を返す（RWC2027特集ページ等、海外開催地ページ専用）。参照: docs/renewal/07_AFFILIATE.md */
export function getOverseasAccommodationProviders(): AccommodationProvider[] {
    return Object.values(OVERSEAS_ACCOMMODATION_PROVIDERS);
}

// 航空券検索サービス（P4-5、RWC2027等の海外渡航向け）
export const FLIGHT_PROVIDERS: Record<string, FlightProvider> = {
    skyticket: { id: "skyticket", name: "skyticket", url: "https://skyticket.jp/" },
    expedia: { id: "expedia", name: "Expedia", url: "https://www.expedia.co.jp/" },
};

/** 航空券検索サービス一覧を返す（RWC2027特集ページ等、海外渡航ページ専用）。参照: docs/renewal/07_AFFILIATE.md */
export function getFlightProviders(): FlightProvider[] {
    return Object.values(FLIGHT_PROVIDERS);
}
