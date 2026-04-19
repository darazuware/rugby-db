/**
 * worldRankings.ts
 * BFF shared module: World Rugby API fetch + fallback to cached JSON.
 * Used by both the API endpoint and the SSR page (to avoid self-HTTP calls).
 */
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';

const WR_API_BASE = 'https://api.wr-rims-prod.pulselive.com/rugby/v3/rankings';
const CACHE_PATH = join(process.cwd(), 'data', 'world_rankings.json');
const TIMEOUT_MS = 8000;

const COUNTRY_MAP: Record<string, string> = {
  "South Africa": "南アフリカ", "Ireland": "アイルランド", "New Zealand": "ニュージーランド",
  "France": "フランス", "England": "イングランド", "Scotland": "スコットランド",
  "Argentina": "アルゼンチン", "Italy": "イタリア", "Fiji": "フィジー",
  "Australia": "オーストラリア", "Wales": "ウェールズ", "Georgia": "ジョージア",
  "Samoa": "サモア", "Japan": "日本", "Portugal": "ポルトガル",
  "Tonga": "トンガ", "Uruguay": "ウルグアイ", "Spain": "スペイン",
  "USA": "アメリカ", "Romania": "ルーマニア", "Canada": "カナダ",
  "Chile": "チリ", "Namibia": "ナミビア", "Hong Kong China": "香港",
  "Netherlands": "オランダ", "Russia": "ロシア", "Brazil": "ブラジル",
  "Belgium": "ベルギー", "Switzerland": "スイス", "Germany": "ドイツ",
  "Zimbabwe": "ジンバブエ", "Kenya": "ケニア", "Algeria": "アルジェリア",
  "Uganda": "ウガンダ", "South Korea": "韓国", "China": "中国",
  "Cook Islands": "クック諸島", "Papua New Guinea": "パプアニューギニア",
  "Colombia": "コロンビア", "Kazakhstan": "カザフスタン",
  "Sri Lanka": "スリランカ", "Philippines": "フィリピン", "Malaysia": "マレーシア",
};

const FLAG_MAP: Record<string, string> = {
  '日本': '🇯🇵', 'オーストラリア': '🇦🇺', 'ニュージーランド': '🇳🇿', '南アフリカ': '🇿🇦',
  'フィジー': '🇫🇯', 'トンガ': '🇹🇴', 'サモア': '🇼🇸', 'フランス': '🇫🇷',
  'イングランド': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'ウェールズ': '🏴󠁧󠁢󠁷󠁬󠁳󠁿', 'スコットランド': '🏴󠁧󠁢󠁳󠁣󠁴󠁿',
  'アイルランド': '🇮🇪', 'イタリア': '🇮🇹', 'アルゼンチン': '🇦🇷', 'アメリカ': '🇺🇸',
  'カナダ': '🇨🇦', 'ジョージア': '🇬🇪', 'ウルグアイ': '🇺🇾', 'ポルトガル': '🇵🇹',
  'ルーマニア': '🇷🇴', 'ナミビア': '🇳🇦', 'チリ': '🇨🇱', '韓国': '🇰🇷',
  '中国': '🇨🇳', '香港': '🇭🇰', 'オランダ': '🇳🇱', 'スペイン': '🇪🇸',
  'ロシア': '🇷🇺', 'ブラジル': '🇧🇷', 'ベルギー': '🇧🇪', 'スイス': '🇨🇭',
  'ドイツ': '🇩🇪', 'ジンバブエ': '🇿🇼', 'ケニア': '🇰🇪', 'アルジェリア': '🇩🇿',
  'ウガンダ': '🇺🇬', 'クック諸島': '🇨🇰', 'パプアニューギニア': '🇵🇬',
};

export interface RankingEntry {
  rank: number;
  previousRank: number;
  points: number;
  team_en: string;
  team_jp: string;
  abbreviation: string;
  flag: string;
}

export interface RankingsPayload {
  updated_at: string;
  mens: RankingEntry[];
  womens: RankingEntry[];
  source?: 'live' | 'cache';
}

async function fetchCategory(cat: 'mru' | 'wru'): Promise<{ date: string; rankings: RankingEntry[] }> {
  const res = await fetch(`${WR_API_BASE}/${cat}?language=en`, {
    signal: AbortSignal.timeout(TIMEOUT_MS),
    headers: { 'User-Agent': 'Mozilla/5.0 (compatible; RugbyPicksBot/1.0)' },
  });
  if (!res.ok) throw new Error(`WR API ${cat} returned ${res.status}`);
  const data = await res.json();

  const date: string = data?.effective?.label ?? new Date().toISOString().slice(0, 10);
  const entries: any[] = data?.entries ?? [];

  return {
    date,
    rankings: entries.map((e: any) => {
      const en: string = e?.team?.name ?? '';
      const jp: string = COUNTRY_MAP[en] ?? en;
      return {
        rank: e.pos ?? 0,
        previousRank: e.previousPos ?? 0,
        points: e.pts ?? 0,
        team_en: en,
        team_jp: jp,
        abbreviation: e?.team?.abbreviation ?? '',
        flag: FLAG_MAP[jp] ?? FLAG_MAP[en] ?? '',
      };
    }),
  };
}

async function loadCache(): Promise<RankingsPayload> {
  const raw = await readFile(CACHE_PATH, 'utf-8');
  return { ...JSON.parse(raw), source: 'cache' };
}

/**
 * メイン取得関数: World Rugby APIを試み、失敗時はキャッシュJSONにフォールバック。
 */
export async function getWorldRankings(): Promise<RankingsPayload> {
  try {
    const [mens, womens] = await Promise.all([
      fetchCategory('mru'),
      fetchCategory('wru'),
    ]);
    return {
      updated_at: mens.date,
      mens: mens.rankings,
      womens: womens.rankings,
      source: 'live',
    };
  } catch {
    return loadCache();
  }
}
