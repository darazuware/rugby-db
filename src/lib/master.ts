/**
 * master.ts
 * data/master/ (SSOT) の読み込み・リーグ結合・slug索引・人物重複マージの一元化（04）。
 *
 * 各ページはこのモジュール経由でのみ master データを取得する。
 * 型は pipeline/schemas.py（pydantic, 01準拠）に合わせる。フィールド追加時は
 * 両方を同時に更新すること。
 */
import { readFile, readdir } from "node:fs/promises";
import { join } from "node:path";

// ---------------------------------------------------------------------------
// リーグキー（pipeline/schemas.py: TEAM_LEAGUES / NO_TEAM_LEAGUES）
// ---------------------------------------------------------------------------

export const TEAM_LEAGUES = [
  "league-one-d1",
  "league-one-d2",
  "league-one-d3",
  "top14",
  "super-rugby",
  "urc",
  "premiership",
  "nrl",
  "mlr",
] as const;

export const NO_TEAM_LEAGUES = [
  "national",
  "sevens-national",
  "age-grade",
  "university",
  "highschool",
] as const;

export const LEAGUE_KEYS = [...TEAM_LEAGUES, ...NO_TEAM_LEAGUES] as const;

export type TeamLeagueKey = (typeof TEAM_LEAGUES)[number];
export type NoTeamLeagueKey = (typeof NO_TEAM_LEAGUES)[number];
export type LeagueKey = (typeof LEAGUE_KEYS)[number];

// ---------------------------------------------------------------------------
// 型（pipeline/schemas.py と1:1対応）
// ---------------------------------------------------------------------------

export interface Caps {
  team: string;
  count: number;
  source_url: string | null;
}

export interface CareerEntry {
  team: string;
  from: number | null;
  to: number | null;
  source_url: string | null;
}

export interface SeasonStats {
  season: string;
  matches: number | null;
  tries: number | null;
  points: number | null;
}

export interface Education {
  school_id: string | null;
  name_raw: string | null;
  type: "hs" | "univ";
  grad_year: number | null;
  source_url: string | null;
  scraped_at: string | null;
}

export interface Player {
  id: string;
  source: string;
  source_url: string;
  scraped_at: string;
  name_en: string | null;
  name_ja: string | null;
  name_kana: string | null;
  slug: string;
  position: string | null;
  team_id: string | null;
  league: LeagueKey;
  height_cm: number | null;
  weight_kg: number | null;
  birthdate: string | null;
  nationality: string[];
  caps: Caps | null;
  league_caps: number | null;
  career: CareerEntry[];
  season_stats: SeasonStats | null;
  education: Education[];
  instagram: string | null;
  image_url: string | null;
  squad: string | null;
  is_featured: boolean;
  is_minor: boolean;
  merged_from: string[];
}

export interface Stadium {
  name: string;
  source_url: string | null;
}

export interface Team {
  id: string;
  league: TeamLeagueKey;
  name_ja: string | null;
  name_en: string | null;
  source_url: string;
  scraped_at: string;
  home_area: string | null;
  home_stadiums: Stadium[];
  founded: number | null;
  colors: Record<string, string>;
  official_url: string | null;
  roster_mode: "full" | "partial";
  roster_ids: string[];
}

export interface Match {
  id: string;
  league: LeagueKey;
  season: string;
  round: number | null;
  kickoff_utc: string | null;
  home_team_id: string;
  away_team_id: string;
  home_score: number | null;
  away_score: number | null;
  status: "scheduled" | "finished" | "postponed";
  venue: string | null;
  venue_raw: string | null;
  source_url: string;
  scraped_at: string;
}

export interface StandingRow {
  rank: number;
  team_id: string;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  points: number;
  bonus: number | null;
}

export interface Standing {
  league: LeagueKey;
  season: string;
  scraped_at: string;
  source_url: string;
  rows: StandingRow[];
}

/** dup_id → canonical_id（data/manual/player_merges.json、01の canonical_id 運用） */
export type PlayerMerges = Record<string, string>;

/**
 * 学校（10_YOUTH_AGEGRADE.md, P5-1）。data/master/schools/schools.json の1レコード。
 * pref/name_kana はソースに無い限り null（P5-5/P5-6の公式名簿スクレイパーが実データで埋める）。
 */
export interface School {
  id: string;
  name: string;
  name_kana: string | null;
  type: "hs" | "univ";
  pref: string | null;
  source_url: string | null;
  scraped_at: string | null;
}

// ---------------------------------------------------------------------------
// パス
// ---------------------------------------------------------------------------

const MASTER_DIR = join(process.cwd(), "data", "master");
const PLAYERS_DIR = join(MASTER_DIR, "players");
const TEAMS_DIR = join(MASTER_DIR, "teams");
const MATCHES_DIR = join(MASTER_DIR, "matches");
const STANDINGS_DIR = join(MASTER_DIR, "standings");
const SCHOOLS_FILE = join(MASTER_DIR, "schools", "schools.json");
const EPISODES_DIR = join(PLAYERS_DIR, "episodes");
const MANUAL_DIR = join(process.cwd(), "data", "manual");

// ---------------------------------------------------------------------------
// 低レベル読み込み（存在しないファイル/ディレクトリは静かに空を返す。
// data/master は pipeline 以外書き換え禁止のため、ここは読み取り専用）
// ---------------------------------------------------------------------------

async function readJsonSafe<T>(path: string, fallback: T): Promise<T> {
  try {
    const raw = await readFile(path, "utf-8");
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

async function readDirSafe(dir: string): Promise<string[]> {
  try {
    return await readdir(dir);
  } catch {
    return [];
  }
}

// ---------------------------------------------------------------------------
// Players
// ---------------------------------------------------------------------------

let _playersCache: Promise<Player[]> | null = null;

async function loadPlayerMerges(): Promise<PlayerMerges> {
  return readJsonSafe<PlayerMerges>(join(MANUAL_DIR, "player_merges.json"), {});
}

/**
 * player_merges（dup_id → canonical_id）を適用する。
 * - canonical.merged_from に dup_id を追記
 * - canonical が null/空の代表情報（caps / nationality）のみ dup から補う（01 L89 相当）
 *   既存の canonical 値は上書きしない
 * - dup 側/canonical 側どちらかが players 内に無い場合は保守的に何もしない
 * - 戻り値からは dup_id を除外する（04: getStaticPaths から除外）
 */
export function applyPlayerMerges(players: Player[], merges: PlayerMerges): Player[] {
  const entries = Object.entries(merges ?? {});
  if (entries.length === 0) return players;

  const byId = new Map(players.map((p) => [p.id, p]));
  const dupIds = new Set<string>();

  for (const [dupId, canonicalId] of entries) {
    const dup = byId.get(dupId);
    const canonical = byId.get(canonicalId);
    if (!dup || !canonical) continue; // 保守的: 片方が master に無ければ統合しない

    dupIds.add(dupId);

    const mergedFrom = new Set(canonical.merged_from);
    mergedFrom.add(dupId);
    for (const m of dup.merged_from) mergedFrom.add(m);
    canonical.merged_from = Array.from(mergedFrom);

    if (canonical.caps == null && dup.caps != null) {
      canonical.caps = dup.caps;
    }
    if ((canonical.nationality?.length ?? 0) === 0 && (dup.nationality?.length ?? 0) > 0) {
      canonical.nationality = dup.nationality;
    }
    // education: 同一校（type+name_raw一致）の grad_year が canonical 側で空なら dup から
    // 補う（在学中/卒業済みの判定に必要）。canonical に無い type（例: 高校歴が無い）は
    // dup 側のレコードをそのまま追加する（caps/nationalityと同じ「null/空のときのみ
    // 相手から補う」方針。既存の canonical 値は一切上書きしない）。
    canonical.education = canonical.education ?? [];
    for (const ce of canonical.education) {
      if (ce.grad_year != null) continue;
      const match = (dup.education ?? []).find(
        (de) => de.type === ce.type && de.name_raw === ce.name_raw && de.grad_year != null
      );
      if (match) ce.grad_year = match.grad_year;
    }
    const canonicalTypes = new Set(canonical.education.map((ce) => ce.type));
    for (const de of dup.education ?? []) {
      if (!canonicalTypes.has(de.type)) {
        canonical.education.push(de);
        canonicalTypes.add(de.type);
      }
    }
  }

  return players.filter((p) => !dupIds.has(p.id));
}

/**
 * 同一 id が複数リーグのファイルに入っている重複を1レコードに畳む。
 *
 * all.rugby 由来の代表選手（national.json）は、同じ id・同じ slug のまま所属クラブ
 * リーグ（top14 / urc / super-rugby / premiership）にも入っている。そのまま結合すると
 * slug が衝突し getStaticPaths が重複パスを返すため、ここで統合する。
 *
 * - canonical はクラブ側（league !== "national"）。所属チームページとの整合を優先する。
 *   全レコードが national の場合は最初のレコードを canonical にする。
 * - canonical が null/空の項目のみ相手側から補う（既存値は上書きしない。applyPlayerMerges と同じ方針）。
 *   例外: height_cm/weight_kg はscraped_atがより新しい方の値を採用する（食い違い対策。後述）。
 * - id が同じなので merged_from には積まない（別 id の人物統合は player_merges 側の役目）。
 */
export function dedupePlayersById(players: Player[]): Player[] {
  const byId = new Map<string, Player>();
  const result: Player[] = [];

  for (const player of players) {
    const existing = byId.get(player.id);
    if (!existing) {
      const copy = { ...player };
      byId.set(player.id, copy);
      result.push(copy);
      continue;
    }
    // クラブ側を canonical にする（既存が national なら入れ替える）
    const canonical = existing.league === "national" && player.league !== "national"
      ? Object.assign(existing, player, {
          caps: existing.caps ?? player.caps,
          nationality: existing.nationality?.length ? existing.nationality : player.nationality,
          career: existing.career?.length ? existing.career : player.career,
          education: existing.education?.length ? existing.education : player.education,
        })
      : existing;
    const other = canonical === existing ? player : existing;

    if (canonical.caps == null) canonical.caps = other.caps;
    if (canonical.league_caps == null) canonical.league_caps = other.league_caps;
    if ((canonical.nationality?.length ?? 0) === 0) canonical.nationality = other.nationality;
    if ((canonical.career?.length ?? 0) === 0) canonical.career = other.career;
    if ((canonical.education?.length ?? 0) === 0) canonical.education = other.education;
    if (canonical.season_stats == null) canonical.season_stats = other.season_stats;
    // 身長体重は取得元ページのスナップショットのため、リーグ間で値が食い違うことがある
    // （同じ選手・同じsourceでもページ取得時期によって表記が変わる）。scraped_atが
    // より新しい方を正とする（同値・比較不能なら既存値を優先=挙動を変えない）。
    const otherIsNewer = !!other.scraped_at && !!canonical.scraped_at
      && other.scraped_at > canonical.scraped_at;
    if (otherIsNewer && other.height_cm != null) {
      canonical.height_cm = other.height_cm;
    } else if (canonical.height_cm == null) {
      canonical.height_cm = other.height_cm;
    }
    if (otherIsNewer && other.weight_kg != null) {
      canonical.weight_kg = other.weight_kg;
    } else if (canonical.weight_kg == null) {
      canonical.weight_kg = other.weight_kg;
    }
    if (canonical.birthdate == null) canonical.birthdate = other.birthdate;
    if (canonical.name_ja == null) canonical.name_ja = other.name_ja;
    if (canonical.name_kana == null) canonical.name_kana = other.name_kana;
    if (canonical.instagram == null) canonical.instagram = other.instagram;
    if (canonical.image_url == null) canonical.image_url = other.image_url;
  }

  return result;
}

// ---------------------------------------------------------------------------
// 未成年ポリシー（10_YOUTH_AGEGRADE.md「未成年の個人情報ポリシー（絶対）」）
//
// is_minor=true の選手は、テンプレート側の実装ミスに依存せず、この読み込み層で
// 禁止フィールドを強制的に null 化する。ページ・コンポーネント・APIエンドポイントは
// すべて getAllPlayers() 系の関数を経由するため、ここで一度塞げば全経路に効く。
//
// 掲載禁止（10）: 生年月日（学年のみ可）・身長体重・SNSアカウント・写真/AIイラスト。
// 写真/AIイラストは PlayerAvatar.astro 側で isMinor を見て強制フォールバックする
// （instagram_accounts.json / illustrations/ はこのデータ層の外にあるため、image_url /
//  instagram を null 化するだけでは塞げない）。
// ---------------------------------------------------------------------------

const MINOR_FORBIDDEN_FIELDS = [
  "birthdate",
  "height_cm",
  "weight_kg",
  "instagram",
  "image_url",
] as const;

/** is_minor=true の選手から禁止フィールドを null 化した新しいオブジェクトを返す（純関数）。 */
export function sanitizeMinorPlayer(player: Player): Player {
  if (!player.is_minor) return player;
  const sanitized = { ...player };
  for (const field of MINOR_FORBIDDEN_FIELDS) {
    (sanitized as Record<string, unknown>)[field] = null;
  }
  return sanitized;
}

/**
 * 選手個別ページ（/players/{slug}）を生成してよいか（10「高校生の個別ページは作らない」）。
 * league="highschool" は学校ページ内の一覧行のみで表示し、個別ページは生成しない。
 * 大学進学・U代表/セブンズ代表選出（education の追加や squad/league の変化）により
 * league が highschool 以外になった時点で個別ページ対象になる。
 */
export function canHaveIndividualPlayerPage(player: Player): boolean {
  return player.league !== "highschool";
}

/**
 * 加入発表直後など最小限のフィールドしか持たないレコード（例: lo_announced_*）を
 * Player 型の契約（配列/オブジェクトフィールドは常に存在）に合わせて補完する。
 * data/master 自体は書き換えない（pipeline 以外禁止）。
 */
function normalizePlayer(p: Player): Player {
  return {
    name_en: p.name_en ?? null,
    name_ja: p.name_ja ?? null,
    name_kana: p.name_kana ?? null,
    position: p.position ?? null,
    team_id: p.team_id ?? null,
    height_cm: p.height_cm ?? null,
    weight_kg: p.weight_kg ?? null,
    birthdate: p.birthdate ?? null,
    nationality: p.nationality ?? [],
    caps: p.caps ?? null,
    league_caps: p.league_caps ?? null,
    career: p.career ?? [],
    season_stats: p.season_stats ?? null,
    education: p.education ?? [],
    instagram: p.instagram ?? null,
    image_url: p.image_url ?? null,
    squad: p.squad ?? null,
    is_featured: p.is_featured ?? false,
    is_minor: p.is_minor ?? false,
    merged_from: p.merged_from ?? [],
    ...p,
  };
}

async function loadAllPlayersRaw(): Promise<Player[]> {
  const lists = await Promise.all(
    LEAGUE_KEYS.map((league) =>
      readJsonSafe<Player[]>(join(PLAYERS_DIR, `${league}.json`), []),
    ),
  );
  return lists.flat().map(normalizePlayer).map(sanitizeMinorPlayer);
}

/** 全リーグの選手を結合し、人物重複マージを適用したリストを返す（キャッシュ済み）。 */
export function getAllPlayers(): Promise<Player[]> {
  if (!_playersCache) {
    _playersCache = (async () => {
      const [raw, merges] = await Promise.all([loadAllPlayersRaw(), loadPlayerMerges()]);
      return applyPlayerMerges(dedupePlayersById(raw), merges);
    })();
  }
  return _playersCache;
}

let _playerBySlugCache: Promise<Map<string, Player>> | null = null;

function buildPlayerSlugIndex(players: Player[]): Map<string, Player> {
  return new Map(players.map((p) => [p.slug, p]));
}

async function getPlayerSlugIndex(): Promise<Map<string, Player>> {
  if (!_playerBySlugCache) {
    _playerBySlugCache = getAllPlayers().then(buildPlayerSlugIndex);
  }
  return _playerBySlugCache;
}

export async function getPlayerBySlug(slug: string): Promise<Player | undefined> {
  const index = await getPlayerSlugIndex();
  return index.get(slug);
}

export async function getPlayerById(id: string): Promise<Player | undefined> {
  const players = await getAllPlayers();
  return players.find((p) => p.id === id);
}

export async function getPlayersByTeam(teamId: string): Promise<Player[]> {
  const players = await getAllPlayers();
  return players.filter((p) => p.team_id === teamId);
}

export async function getPlayersByLeague(league: LeagueKey): Promise<Player[]> {
  const players = await getAllPlayers();
  return players.filter((p) => p.league === league);
}

export async function getFeaturedPlayers(): Promise<Player[]> {
  const players = await getAllPlayers();
  return players.filter((p) => p.is_featured);
}

// ---------------------------------------------------------------------------
// Teams
// ---------------------------------------------------------------------------

let _teamsCache: Promise<Team[]> | null = null;

async function loadAllTeamsRaw(): Promise<Team[]> {
  const lists = await Promise.all(
    TEAM_LEAGUES.map((league) => readJsonSafe<Team[]>(join(TEAMS_DIR, `${league}.json`), [])),
  );
  return lists.flat();
}

export function getAllTeams(): Promise<Team[]> {
  if (!_teamsCache) _teamsCache = loadAllTeamsRaw();
  return _teamsCache;
}

export async function getTeamById(id: string): Promise<Team | undefined> {
  const teams = await getAllTeams();
  return teams.find((t) => t.id === id);
}

export async function getTeamsByLeague(league: TeamLeagueKey): Promise<Team[]> {
  const teams = await getAllTeams();
  return teams.filter((t) => t.league === league);
}

/** チームの表示名（name_ja優先、無ければname_en、両方無ければnull）。 */
export function teamDisplayName(team: Team | null | undefined): string | null {
  if (!team) return null;
  return team.name_ja ?? team.name_en ?? null;
}

// ---------------------------------------------------------------------------
// Matches
// ---------------------------------------------------------------------------

let _matchesCache: Promise<Match[]> | null = null;

async function loadAllMatchesRaw(): Promise<Match[]> {
  const files = await readDirSafe(MATCHES_DIR);
  const lists = await Promise.all(
    files
      .filter((f) => f.endsWith(".json"))
      .map((f) => readJsonSafe<Match[]>(join(MATCHES_DIR, f), [])),
  );
  return lists.flat();
}

export function getAllMatches(): Promise<Match[]> {
  if (!_matchesCache) _matchesCache = loadAllMatchesRaw();
  return _matchesCache;
}

export async function getMatchesByLeague(league: LeagueKey): Promise<Match[]> {
  const matches = await getAllMatches();
  return matches.filter((m) => m.league === league);
}

// ---------------------------------------------------------------------------
// Standings
// ---------------------------------------------------------------------------

let _standingsCache: Promise<Standing[]> | null = null;

async function loadAllStandingsRaw(): Promise<Standing[]> {
  const files = await readDirSafe(STANDINGS_DIR);
  const lists = await Promise.all(
    files
      .filter((f) => f.endsWith(".json"))
      .map((f) => readJsonSafe<Standing[]>(join(STANDINGS_DIR, f), [])),
  );
  return lists.flat();
}

export function getAllStandings(): Promise<Standing[]> {
  if (!_standingsCache) _standingsCache = loadAllStandingsRaw();
  return _standingsCache;
}

export async function getStandingByLeague(league: LeagueKey): Promise<Standing | undefined> {
  const standings = await getAllStandings();
  return standings.find((s) => s.league === league);
}

// ---------------------------------------------------------------------------
// Schools（P5-4: 学校ページ + つながりグラフ。10_YOUTH_AGEGRADE.md）
// ---------------------------------------------------------------------------

let _schoolsCache: Promise<School[]> | null = null;

async function loadAllSchoolsRaw(): Promise<School[]> {
  return readJsonSafe<School[]>(SCHOOLS_FILE, []);
}

export function getAllSchools(): Promise<School[]> {
  if (!_schoolsCache) _schoolsCache = loadAllSchoolsRaw();
  return _schoolsCache;
}

let _schoolByIdCache: Promise<Map<string, School>> | null = null;

async function getSchoolByIdIndex(): Promise<Map<string, School>> {
  if (!_schoolByIdCache) {
    _schoolByIdCache = getAllSchools().then((schools) => new Map(schools.map((s) => [s.id, s])));
  }
  return _schoolByIdCache;
}

export async function getSchoolById(id: string): Promise<School | undefined> {
  const index = await getSchoolByIdIndex();
  return index.get(id);
}

/** 学校の表示名（name優先、無ければ null）。将来 name_kana 併記が必要ならここに集約する。 */
export function schoolDisplayName(school: School | null | undefined): string | null {
  return school?.name ?? null;
}

// ---------------------------------------------------------------------------
// Episodes（選手ページ本文の厚み付け。JRFU公式/チーム公式/リーグワン公式/
// 海外メディア公式/ラグビーマガジン・リパブリック等からのスクレイピング結果のみ。
// AIの創作は含まない。data/master/players/episodes/{player.id}.json）
// ---------------------------------------------------------------------------

export interface PlayerEpisodeFact {
  fact: string;
  category: string;
  source_name: string;
  source_url: string;
  date: string | null;
}

export interface PlayerEpisodes {
  player_id: string;
  name: string;
  collected_at: string;
  facts: PlayerEpisodeFact[];
}

export async function getPlayerEpisodes(playerId: string): Promise<PlayerEpisodes | null> {
  return readJsonSafe<PlayerEpisodes | null>(join(EPISODES_DIR, `${playerId}.json`), null);
}

// ---------------------------------------------------------------------------
// テスト用: モジュールキャッシュのリセット（本番コードからは呼ばない）
// ---------------------------------------------------------------------------

export function __resetMasterCacheForTests(): void {
  _playersCache = null;
  _playerBySlugCache = null;
  _teamsCache = null;
  _matchesCache = null;
  _standingsCache = null;
  _schoolsCache = null;
  _schoolByIdCache = null;
}
