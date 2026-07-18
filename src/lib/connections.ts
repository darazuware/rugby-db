/**
 * connections.ts
 * 学校ベースの「つながりグラフ」— 同期/先輩後輩ラベル・年代別/セブンズ代表バッジ（P5-4, 10）。
 *
 * 10_YOUTH_AGEGRADE.md:
 * - 判定基準は education.grad_year（未成年は生年月日を持たないため）
 * - 「学校→選手」インデックスを一度だけ構築し、各ページはそれを引く（O(N²)を避ける）
 * - 事実は Player.education / Player.squad / Player.caps からのみ導出する。
 *   選手個人のバッジは自分自身のレコードの値のみを根拠にし、他リーグの同一人物への
 *   推測突合は行わない（player_merges.json で確定していない限り、AIが人物を跨いで
 *   事実を創作することになるため）。
 */
import { getAllPlayers, type Player } from "./master";

// ---------------------------------------------------------------------------
// バッジ（選手個人の squad / caps に基づく。他選手との突合は行わない）
// ---------------------------------------------------------------------------

export interface Badge {
  key: string;
  label: string;
}

const SQUAD_LABEL: Readonly<Record<string, string>> = Object.freeze({
  u17: "U17代表",
  u18: "U18代表",
  u19: "U19代表",
  u20: "U20代表",
  u23: "U23代表",
  sevens_m: "セブンズ代表(男子)",
  sevens_w: "セブンズ代表(女子)",
});

/** 選手個人のバッジ（年代別代表・セブンズ代表・代表キャップ）。値が無い項目は出さない。 */
export function playerBadges(player: Player): Badge[] {
  const badges: Badge[] = [];
  if (player.squad && SQUAD_LABEL[player.squad]) {
    badges.push({ key: `squad-${player.squad}`, label: SQUAD_LABEL[player.squad] });
  }
  if (player.caps && player.caps.team) {
    badges.push({ key: "caps", label: `${player.caps.team}代表` });
  }
  return badges;
}

// ---------------------------------------------------------------------------
// 学校→選手インデックス（ビルド中一度だけ構築）
// ---------------------------------------------------------------------------

function buildSchoolPlayerIndex(players: Player[]): Map<string, Player[]> {
  const index = new Map<string, Player[]>();
  for (const player of players) {
    for (const edu of player.education) {
      if (!edu.school_id) continue;
      const list = index.get(edu.school_id);
      if (list) list.push(player);
      else index.set(edu.school_id, [player]);
    }
  }
  return index;
}

let _schoolPlayerIndexCache: Promise<Map<string, Player[]>> | null = null;

/** 学校ID → 在籍/出身が確認できる選手一覧のインデックス（キャッシュ済み、10の性能要件）。 */
export function getSchoolPlayerIndex(): Promise<Map<string, Player[]>> {
  if (!_schoolPlayerIndexCache) {
    _schoolPlayerIndexCache = getAllPlayers().then(buildSchoolPlayerIndex);
  }
  return _schoolPlayerIndexCache;
}

/** 指定した学校IDに紐づく選手一覧（education.school_id が一致するもの）。 */
export async function getPlayersBySchool(schoolId: string): Promise<Player[]> {
  const index = await getSchoolPlayerIndex();
  return index.get(schoolId) ?? [];
}

// ---------------------------------------------------------------------------
// 同期/先輩後輩ラベル（grad_year ベース、10「判定基準を education.grad_year に移行」）
// ---------------------------------------------------------------------------

export type SchoolmateRelation = "senior" | "junior" | "sync" | "unknown";

export interface Schoolmate {
  player: Player;
  relation: SchoolmateRelation;
}

export interface SchoolmateGroup {
  schoolId: string;
  gradYear: number | null;
  mates: Schoolmate[];
}

/**
 * 基準選手 (baseGradYear) から見た相手 (mateGradYear) の関係。
 * grad_year が小さい = 卒業が早い = 先輩（senior）。どちらか null なら判定不能（unknown）。
 */
export function relationOf(
  baseGradYear: number | null,
  mateGradYear: number | null,
): SchoolmateRelation {
  if (baseGradYear == null || mateGradYear == null) return "unknown";
  if (baseGradYear === mateGradYear) return "sync";
  return mateGradYear < baseGradYear ? "senior" : "junior";
}

const RELATION_SORT_ORDER: Readonly<Record<SchoolmateRelation, number>> = Object.freeze({
  sync: 0,
  senior: 1,
  junior: 2,
  unknown: 3,
});

/**
 * player の各出身校（education の school_id ごと）について、同校の他選手を
 * 関係ラベル付きで返す。同一人物は education を複数（hs/univ 等）持ちうるため
 * 学校単位でグループ化する。
 */
export async function getSchoolmates(
  player: Player,
  limitPerSchool = 12,
): Promise<SchoolmateGroup[]> {
  const index = await getSchoolPlayerIndex();
  const groups: SchoolmateGroup[] = [];

  for (const edu of player.education) {
    if (!edu.school_id) continue;
    const candidates = index.get(edu.school_id) ?? [];
    const mates: Schoolmate[] = [];
    for (const other of candidates) {
      if (other.id === player.id) continue;
      const otherEdu = other.education.find((e) => e.school_id === edu.school_id);
      if (!otherEdu) continue;
      mates.push({ player: other, relation: relationOf(edu.grad_year, otherEdu.grad_year) });
    }
    mates.sort((a, b) => RELATION_SORT_ORDER[a.relation] - RELATION_SORT_ORDER[b.relation]);
    groups.push({ schoolId: edu.school_id, gradYear: edu.grad_year, mates: mates.slice(0, limitPerSchool) });
  }
  return groups;
}

// ---------------------------------------------------------------------------
// テスト用: モジュールキャッシュのリセット（本番コードからは呼ばない）
// ---------------------------------------------------------------------------

export function __resetConnectionsCacheForTests(): void {
  _schoolPlayerIndexCache = null;
}
