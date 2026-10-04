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

// 英語名 → ISO国コード（FLAG_MAPに無い国の国旗を生成する）
const ISO_BY_EN: Record<string, string> = {
  "Chinese Taipei": "TW", "Taiwan": "TW", "Ivory Coast": "CI", "Côte d'Ivoire": "CI", "Cote d'Ivoire": "CI",
  "Czechia": "CZ", "Czech Republic": "CZ", "Poland": "PL", "Sweden": "SE", "Lithuania": "LT", "Latvia": "LV",
  "Ukraine": "UA", "Moldova": "MD", "Croatia": "HR", "Serbia": "RS", "Slovenia": "SI", "Slovakia": "SK",
  "Hungary": "HU", "Bulgaria": "BG", "Malta": "MT", "Norway": "NO", "Denmark": "DK", "Finland": "FI",
  "Andorra": "AD", "Austria": "AT", "Luxembourg": "LU", "Monaco": "MC", "Israel": "IL", "Greece": "GR",
  "Turkey": "TR", "Türkiye": "TR", "Bosnia & Herzegovina": "BA", "Bosnia and Herzegovina": "BA", "Cyprus": "CY",
  "Lebanon": "LB", "Iran": "IR", "Jordan": "JO", "Uzbekistan": "UZ", "Singapore": "SG", "Thailand": "TH",
  "India": "IN", "Indonesia": "ID", "Pakistan": "PK", "Vietnam": "VN", "Laos": "LA", "Cambodia": "KH",
  "Mongolia": "MN", "Guam": "GU", "Fiji": "FJ", "Solomon Islands": "SB", "Vanuatu": "VU", "New Caledonia": "NC",
  "Tahiti": "PF", "American Samoa": "AS", "Niue": "NU", "Tuvalu": "TV", "Nauru": "NR", "Palau": "PW",
  "Senegal": "SN", "Madagascar": "MG", "Mauritius": "MU", "Morocco": "MA", "Tunisia": "TN", "Zambia": "ZM",
  "Botswana": "BW", "Nigeria": "NG", "Ghana": "GH", "Cameroon": "CM", "Burkina Faso": "BF", "Mali": "ML",
  "Tanzania": "TZ", "Rwanda": "RW", "Burundi": "BI", "Malawi": "MW", "Mozambique": "MZ", "Eswatini": "SZ",
  "Swaziland": "SZ", "Lesotho": "LS", "Ethiopia": "ET", "Egypt": "EG", "Togo": "TG", "Benin": "BJ",
  "Gabon": "GA", "Mexico": "MX", "Paraguay": "PY", "Peru": "PE", "Venezuela": "VE", "Bolivia": "BO",
  "Ecuador": "EC", "Costa Rica": "CR", "Panama": "PA", "Guatemala": "GT", "El Salvador": "SV", "Honduras": "HN",
  "Jamaica": "JM", "Trinidad & Tobago": "TT", "Trinidad and Tobago": "TT", "Barbados": "BB", "Bahamas": "BS",
  "Bermuda": "BM", "Cayman Islands": "KY", "Guyana": "GY", "Saint Vincent and the Grenadines": "VC",
  "St Vincent & The Grenadines": "VC", "Saint Lucia": "LC", "Curacao": "CW", "Curaçao": "CW", "Cuba": "CU",
  "Dominican Republic": "DO", "Haiti": "HT", "Puerto Rico": "PR", "Belarus": "BY", "Estonia": "EE", "Albania": "AL",
  "North Macedonia": "MK", "Montenegro": "ME", "Iceland": "IS", "Kyrgyzstan": "KG", "Tajikistan": "TJ",
  "Azerbaijan": "AZ", "Armenia": "AM", "Qatar": "QA", "UAE": "AE", "United Arab Emirates": "AE", "Bahrain": "BH",
  "Kuwait": "KW", "Saudi Arabia": "SA", "Oman": "OM", "Syria": "SY", "Iraq": "IQ", "Afghanistan": "AF",
  "Bangladesh": "BD", "Nepal": "NP", "Myanmar": "MM", "Brunei": "BN", "Macau China": "MO", "Macau": "MO",
  "Japan": "JP", "Samoa": "WS", "Tonga": "TO", "Uganda": "UG", "Kenya": "KE", "Zimbabwe": "ZW", "Namibia": "NA",
  "Algeria": "DZ", "Colombia": "CO", "Kazakhstan": "KZ", "Sri Lanka": "LK", "Philippines": "PH", "Malaysia": "MY",
  "South Korea": "KR", "Korea": "KR", "China": "CN", "Hong Kong China": "HK", "Hong Kong": "HK",
  "Cook Islands": "CK", "Papua New Guinea": "PG", "Russia": "RU", "Brazil": "BR", "Belgium": "BE",
  "Switzerland": "CH", "Germany": "DE", "Netherlands": "NL", "Spain": "ES", "Portugal": "PT", "Romania": "RO",
  "Chile": "CL", "Uruguay": "UY", "Georgia": "GE", "Canada": "CA", "USA": "US", "United States": "US",
  "Argentina": "AR", "Italy": "IT", "Ireland": "IE", "France": "FR", "Australia": "AU", "New Zealand": "NZ",
  "South Africa": "ZA",
};

const ENG_FLAGS: Record<string, string> = {
  England: '🏴󠁧󠁢󠁥󠁮󠁧󠁿', Wales: '🏴󠁧󠁢󠁷󠁬󠁳󠁿', Scotland: '🏴󠁧󠁢󠁳󠁣󠁴󠁿',
};

const isoToFlag = (iso: string): string =>
  [...iso.toUpperCase()].map((c) => String.fromCodePoint(0x1f1e6 + c.charCodeAt(0) - 65)).join('');

function resolveFlag(jp: string, en: string): string {
  if (FLAG_MAP[jp]) return FLAG_MAP[jp];
  if (FLAG_MAP[en]) return FLAG_MAP[en];
  if (ENG_FLAGS[en]) return ENG_FLAGS[en];
  const iso = ISO_BY_EN[en];
  return iso ? isoToFlag(iso) : '';
}

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
        flag: resolveFlag(jp, en),
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
