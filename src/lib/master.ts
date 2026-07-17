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

// ---------------------------------------------------------------------------
// パス
// ---------------------------------------------------------------------------

const MASTER_DIR = join(process.cwd(), "data", "master");
const PLAYERS_DIR = join(MASTER_DIR, "players");
const TEAMS_DIR = join(MASTER_DIR, "teams");
const MATCHES_DIR = join(MASTER_DIR, "matches");
const STANDINGS_DIR = join(MASTER_DIR, "standings");
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
  }

  return players.filter((p) => !dupIds.has(p.id));
}

async function loadAllPlayersRaw(): Promise<Player[]> {
  const lists = await Promise.all(
    LEAGUE_KEYS.map((league) =>
      readJsonSafe<Player[]>(join(PLAYERS_DIR, `${league}.json`), []),
    ),
  );
  return lists.flat();
}

/** 全リーグの選手を結合し、人物重複マージを適用したリストを返す（キャッシュ済み）。 */
export function getAllPlayers(): Promise<Player[]> {
  if (!_playersCache) {
    _playersCache = (async () => {
      const [raw, merges] = await Promise.all([loadAllPlayersRaw(), loadPlayerMerges()]);
      return applyPlayerMerges(raw, merges);
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
// テスト用: モジュールキャッシュのリセット（本番コードからは呼ばない）
// ---------------------------------------------------------------------------

export function __resetMasterCacheForTests(): void {
  _playersCache = null;
  _playerBySlugCache = null;
  _teamsCache = null;
  _matchesCache = null;
  _standingsCache = null;
}
