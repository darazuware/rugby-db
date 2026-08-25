/**
 * masterAdapters.ts
 * data/master (SSOT, master.ts) の Player/Team を、既存UI（PlayerList / TeamList /
 * TeamPlayerList など）が期待する旧 content-collection 互換の形へ変換する（04: P2-3）。
 *
 * 新規ページを一から作るのではなく、既存UI（デザイン維持）への「差し込み口」として使う。
 * 対応リーグは LEGACY_LEAGUE_MASTER_KEYS に列挙したものだけ。未対応リーグはこのモジュールを
 * 経由せず、呼び出し側が既存の legacy JSON / content collection にフォールバックすること。
 *
 * 注意（scope決定の記録）:
 * - top14 / super-rugby / urc / premiership の master position は all.rugby 由来で
 *   「バックロー」「センター」等の日本語フルテキスト（positions.ts のコメント参照）であり、
 *   既存UIの略号ベース（PR/HO/LO/FL/No8/SH/SO/CTB/WTB/FB）のポジション絞り込みと非互換。
 *   そのため P2-3 時点では league-one (d1-d3) のみ対象とする。position が略号化され次第、
 *   LEGACY_LEAGUE_MASTER_KEYS に追加すれば自動的に対象が広がる。
 * - data/master/standings, data/master/matches, data/master/players/national.json は
 *   本セッション時点で空/未生成（pipeline 未実行）。このアダプタは選手・チームの roster 用途のみ。
 */
import {
  getPlayersByLeague,
  getPlayersByTeam,
  getTeamById,
  getTeamsByLeague,
  teamDisplayName,
  type LeagueKey,
  type Player,
  type Team,
  type TeamLeagueKey,
} from "./master";
import { calcAge } from "./playerText";
import { getTeamSlug } from "../utils/team_utils";

/** 旧URL/レガシーUIの league パラメータ → master の league キー群。 */
export const LEGACY_LEAGUE_MASTER_KEYS: Record<string, TeamLeagueKey[]> = {
  "league-one": ["league-one-d1", "league-one-d2", "league-one-d3"],
};

const DIVISION_LABEL: Partial<Record<LeagueKey, string>> = {
  "league-one-d1": "Division 1",
  "league-one-d2": "Division 2",
  "league-one-d3": "Division 3",
};

export function divisionLabelForLeague(league: LeagueKey): string {
  return DIVISION_LABEL[league] ?? "";
}

/** 旧 content-collection 互換の選手データ形（PlayerList / TeamPlayerList 共通）。 */
export interface LegacyPlayerData {
  title: string;
  name_en: string;
  name_ja: string;
  position: string;
  team: string;
  age: number | null;
  birth_date: string;
  height: string;
  weight: string;
  caps: string;
  league_one_caps: string;
  category: string;
  country: string;
  division: string;
  league: string;
  high_school: string;
  university: string;
  junior_high_school: string;
  rugby_school: string;
  joined_year: number | null;
  tries?: number;
  matches?: number;
  has_scores?: boolean;
}

export interface LegacyPlayerEntry {
  slug: string;
  data: LegacyPlayerData;
}

/**
 * master.Player → 旧UI互換の {slug, data} 形へ変換する。
 * teamNameOverride を渡さない場合は player.team_id から master.Team を解決する。
 */
export async function playerToLegacyShape(
  player: Player,
  teamNameOverride?: string | null,
): Promise<LegacyPlayerEntry> {
  let teamName = teamNameOverride ?? null;
  if (teamName == null && player.team_id) {
    const team = await getTeamById(player.team_id);
    teamName = teamDisplayName(team);
  }

  const hs = player.education.find((e) => e.type === "hs")?.name_raw ?? "";
  const univ = player.education.find((e) => e.type === "univ")?.name_raw ?? "";
  const careerAtTeam = teamName ? player.career.find((c) => c.team === teamName) : undefined;

  return {
    slug: player.slug,
    data: {
      title: player.name_ja || player.name_en || player.slug,
      name_en: player.name_en ?? "",
      name_ja: player.name_ja ?? "",
      position: player.position ?? "",
      team: teamName ?? "",
      age: calcAge(player.birthdate),
      birth_date: player.birthdate ?? "",
      height: player.height_cm != null ? String(player.height_cm) : "",
      weight: player.weight_kg != null ? String(player.weight_kg) : "",
      caps: player.caps ? `${player.caps.team}(${player.caps.count})` : "",
      league_one_caps: player.league_caps != null ? String(player.league_caps) : "",
      category: "",
      country: player.nationality[0] ?? "",
      division: divisionLabelForLeague(player.league),
      // 旧UIは league-one を分割せず単一キーで扱う（04: P2-2 のチーム遷移コメント準拠）
      league: player.league.startsWith("league-one") ? "league-one" : player.league,
      high_school: hs,
      university: univ,
      junior_high_school: "",
      rugby_school: "",
      joined_year: careerAtTeam?.from ?? null,
      tries: player.season_stats?.tries ?? undefined,
      matches: player.season_stats?.matches ?? undefined,
      has_scores: player.season_stats != null,
    },
  };
}

/** legacyLeague（例: "league-one"）に対応する master の選手一覧を旧UI互換形で返す。未対応なら []。 */
export async function getMasterPlayersLegacyShape(legacyLeague: string): Promise<LegacyPlayerEntry[]> {
  const keys = LEGACY_LEAGUE_MASTER_KEYS[legacyLeague];
  if (!keys) return [];
  const lists = await Promise.all(keys.map((k) => getPlayersByLeague(k)));
  const players = lists.flat();
  if (players.length === 0) return [];
  return Promise.all(players.map((p) => playerToLegacyShape(p)));
}

/** master 対応済みの legacyLeague キー一覧（呼び出し側の除外フィルタ用）。 */
export function masterCoveredLegacyLeagues(): string[] {
  return [...Object.keys(LEGACY_LEAGUE_MASTER_KEYS), "university"];
}

/**
 * university（team_id を持たない NO_TEAM_LEAGUES）の選手一覧を旧UI互換形で返す。
 * team は education の type="univ" の name_raw を代用する（master に Team実体が無いため）。
 * highschool は 10 のポリシー（高校生の個別ページ禁止）に抵触するため対象外
 * （既存 UI は選手カードを常に /players/{slug} へリンクするため、個別ページ非生成の
 * highschool を混ぜるとリンク切れになる。学校ページ /schools/{id}/ 側で提供済み）。
 */
export async function getMasterUniversityPlayersLegacyShape(): Promise<LegacyPlayerEntry[]> {
  const players = await getPlayersByLeague("university");
  if (players.length === 0) return [];
  return Promise.all(
    players.map((p) => {
      const univName = p.education.find((e) => e.type === "univ")?.name_raw ?? "";
      return playerToLegacyShape(p, univName);
    }),
  );
}

/**
 * master 側のチームID（team.id）で厳密に絞り込んだ、あるチームの所属選手一覧を旧UI互換形で返す。
 * 既存の「文字列部分一致」によるロースター判定（表記揺れで誤爆しうる）を廃止し、
 * roster_ids ベースの正確な突合に置き換えるためのもの（01/04 の SSOT 原則）。
 */
export async function getTeamRosterLegacyShape(team: Team): Promise<LegacyPlayerEntry[]> {
  const players = await getPlayersByTeam(team.id);
  if (players.length === 0) return [];
  const teamName = teamDisplayName(team);
  return Promise.all(players.map((p) => playerToLegacyShape(p, teamName)));
}

/**
 * legacyLeague（例: "league-one"）配下の master チームから、既存slug体系（utils/team_utils
 * getTeamSlug、name_ja優先）と一致するチームを探す。既存URL（/teams/[league]/[slug]）を
 * 変更せずに master 側チームへ橋渡しするための関数。見つからなければ undefined（呼び出し側は
 * 既存 legacy JSON にフォールバックする）。
 */
export async function findMasterTeamBySlug(
  legacyLeague: string,
  slug: string,
): Promise<Team | undefined> {
  const keys = LEGACY_LEAGUE_MASTER_KEYS[legacyLeague];
  if (!keys) return undefined;
  const lists = await Promise.all(keys.map((k) => getTeamsByLeague(k)));
  const teams = lists.flat();
  return teams.find((t) => {
    const name = t.name_ja || t.name_en;
    return name != null && getTeamSlug(name) === slug;
  });
}
