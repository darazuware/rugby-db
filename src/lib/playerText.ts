/**
 * playerText.ts
 * 選手ページ本文のテンプレ生成（04）。自由記述禁止＝AIが経歴・成績を創作しない。
 *
 * すべて「値のJSONからテンプレへの穴埋め」のみ。値が null の文（節）は丸ごと出さない。
 * 各関数は入力が null/未知でも例外を投げず、対象データが無ければ null を返す。
 */
import type { Player, CareerEntry, SeasonStats, LeagueKey } from "./master";
import { positionJa } from "./positions";

/** リーグキー → 表示用リーグ名（キャップ実績の文言に使用）。 */
const LEAGUE_LABEL_JA: Readonly<Record<LeagueKey, string>> = Object.freeze({
  "league-one-d1": "リーグワン",
  "league-one-d2": "リーグワン",
  "league-one-d3": "リーグワン",
  top14: "Top14",
  "super-rugby": "スーパーラグビー",
  urc: "URC",
  premiership: "プレミアシップ",
  nrl: "NRL",
  national: "代表",
  "sevens-national": "セブンズ代表",
  "age-grade": "年代別代表",
  university: "大学",
  highschool: "高校",
});

function leagueLabelJa(league: LeagueKey | null | undefined): string | null {
  if (!league) return null;
  return LEAGUE_LABEL_JA[league] ?? null;
}

// ---------------------------------------------------------------------------
// 年齢・生年月日
// ---------------------------------------------------------------------------

/** YYYY-MM-DD から満年齢を計算する。パース不能/null は null。 */
export function calcAge(birthdate: string | null | undefined, asOf: Date = new Date()): number | null {
  if (!birthdate) return null;
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(birthdate);
  if (!m) return null;
  const [, yStr, moStr, dStr] = m;
  const y = Number(yStr);
  const mo = Number(moStr);
  const d = Number(dStr);
  let age = asOf.getFullYear() - y;
  const hadBirthdayThisYear =
    asOf.getMonth() + 1 > mo || (asOf.getMonth() + 1 === mo && asOf.getDate() >= d);
  if (!hadBirthdayThisYear) age -= 1;
  return age;
}

function formatBirthdateJa(birthdate: string): string | null {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(birthdate);
  if (!m) return null;
  const [, y, mo, d] = m;
  return `${y}年${Number(mo)}月${Number(d)}日`;
}

// ---------------------------------------------------------------------------
// 文（センテンス）ビルダー — 各関数は単体でテスト可能。null 入力は null を返す。
// ---------------------------------------------------------------------------

/** {name_ja}（{name_kana}）は{team_name}所属の{position_ja}。 */
export function introSentence(player: Player, teamName: string | null | undefined): string | null {
  const name = player.name_ja;
  if (!name) return null;

  const kana = player.name_kana ? `（${player.name_kana}）` : "";
  const posJa = positionJa(player.position);
  const team = teamName ?? null;

  if (team && posJa) return `${name}${kana}は${team}所属の${posJa}。`;
  if (team && !posJa) return `${name}${kana}は${team}所属。`;
  if (!team && posJa) return `${name}${kana}は${posJa}。`;
  return null; // 所属・ポジションどちらも無ければ出さない
}

/** {birthdate}生まれ{age}歳、{height_cm}cm・{weight_kg}kg。 */
export function birthPhysicalSentence(player: Player, asOf: Date = new Date()): string | null {
  let birthClause: string | null = null;
  if (player.birthdate) {
    const dateJa = formatBirthdateJa(player.birthdate);
    if (dateJa) {
      const age = calcAge(player.birthdate, asOf);
      birthClause = age != null ? `${dateJa}生まれ${age}歳` : `${dateJa}生まれ`;
    }
  }

  const sizeParts: string[] = [];
  if (player.height_cm != null) sizeParts.push(`${player.height_cm}cm`);
  if (player.weight_kg != null) sizeParts.push(`${player.weight_kg}kg`);
  const sizeClause = sizeParts.length > 0 ? sizeParts.join("・") : null;

  if (!birthClause && !sizeClause) return null;
  if (birthClause && sizeClause) return `${birthClause}、${sizeClause}。`;
  return `${birthClause ?? sizeClause}。`;
}

/** {caps.team}代表キャップ{caps.count}。 */
export function capsSentence(player: Player): string | null {
  const caps = player.caps;
  if (!caps || !caps.team) return null;
  return `${caps.team}代表キャップ${caps.count}。`;
}

/** {league}通算{league_caps}キャップ。（04テンプレの「リーグワン」を所属リーグに応じて出し分け） */
export function leagueCapsSentence(player: Player): string | null {
  if (player.league_caps == null) return null;
  const label = leagueLabelJa(player.league);
  if (!label) return null;
  return `${label}通算${player.league_caps}キャップ。`;
}

/**
 * grad_year（卒業年、西暦）から在学中かどうかを判定する。
 * 卒業は3月なので、grad_year の4月1日を迎えていなければ在学中とみなす。
 * grad_year が null（未取得）の場合は判定不能として false（従来通り「出身」表記）。
 */
export function isEnrolled(gradYear: number | null | undefined, asOf: Date = new Date()): boolean {
  if (gradYear == null) return false;
  const cutoff = new Date(gradYear, 3, 1); // gradYear年4月1日
  return asOf < cutoff;
}

/** {education で type=="univ" の name}出身/在学中。is_minor=true は出さない（10のポリシー）。 */
export function educationSentence(player: Player, asOf: Date = new Date()): string | null {
  if (player.is_minor) return null;
  const univ = player.education.find((e) => e.type === "univ");
  if (!univ) return null;
  const name = univ.name_raw; // school_id 解決（P5: schools.json）は未実装のため原文を使用
  if (!name) return null;
  return isEnrolled(univ.grad_year, asOf) ? `${name}在学中。` : `${name}出身。`;
}

/** これまで{career各チーム名の列挙}でプレー。 */
export function careerSentence(player: Player): string | null {
  const teams = player.career
    .map((c: CareerEntry) => c.team)
    .filter((t): t is string => !!t);
  if (teams.length === 0) return null;
  return `これまで${teams.join("、")}でプレー。`;
}

/** {season}シーズンは{matches}試合出場、{tries}トライ。 */
export function seasonStatsSentence(player: Player): string | null {
  const stats: SeasonStats | null = player.season_stats;
  if (!stats || !stats.season) return null;
  const parts: string[] = [];
  if (stats.matches != null) parts.push(`${stats.matches}試合出場`);
  if (stats.tries != null) parts.push(`${stats.tries}トライ`);
  if (parts.length === 0) return null;
  return `${stats.season}シーズンは${parts.join("、")}。`;
}

// ---------------------------------------------------------------------------
// 組み立て
// ---------------------------------------------------------------------------

export interface PlayerBioOptions {
  /** 所属チーム表示名（master.ts の teamDisplayName で解決した値を渡す） */
  teamName?: string | null;
  /** テスト用に年齢計算の基準日を固定する */
  asOf?: Date;
}

/** 適用可能な文だけを配列で返す（null文は含まない）。 */
export function buildPlayerBioSentences(player: Player, options: PlayerBioOptions = {}): string[] {
  const { teamName = null, asOf } = options;
  const sentences = [
    introSentence(player, teamName),
    birthPhysicalSentence(player, asOf),
    capsSentence(player),
    leagueCapsSentence(player),
    educationSentence(player, asOf),
    careerSentence(player),
    seasonStatsSentence(player),
  ];
  return sentences.filter((s): s is string => s != null && s.length > 0);
}

/** 選手ページ本文（1段落）を組み立てる。書ける事実が無ければ空文字を返す。 */
export function buildPlayerBio(player: Player, options: PlayerBioOptions = {}): string {
  return buildPlayerBioSentences(player, options).join("");
}
