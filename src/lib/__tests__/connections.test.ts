import { describe, expect, it } from "vitest";
import {
  getPlayersBySchool,
  getSchoolPlayerIndex,
  getSchoolmates,
  playerBadges,
  relationOf,
  type Badge,
} from "../connections";
import { getAllPlayers, type Education, type Player } from "../master";

function makeEducation(overrides: Partial<Education> = {}): Education {
  return {
    school_id: null,
    name_raw: null,
    type: "hs",
    grad_year: null,
    source_url: null,
    scraped_at: null,
    ...overrides,
  };
}

function makePlayer(overrides: Partial<Player> = {}): Player {
  return {
    id: "x",
    source: "league-one.jp",
    source_url: "https://league-one.jp/player/1",
    scraped_at: "2026-07-14T00:00:00+09:00",
    name_en: "Test Player",
    name_ja: null,
    name_kana: null,
    slug: "test-player",
    position: null,
    team_id: null,
    league: "league-one-d1",
    height_cm: null,
    weight_kg: null,
    birthdate: null,
    nationality: [],
    caps: null,
    league_caps: null,
    career: [],
    season_stats: null,
    education: [],
    instagram: null,
    image_url: null,
    squad: null,
    is_featured: false,
    is_minor: false,
    merged_from: [],
    ...overrides,
  };
}

describe("relationOf（grad_year ベースの同期/先輩後輩判定）", () => {
  it("grad_year が同じなら sync", () => {
    expect(relationOf(2024, 2024)).toBe("sync");
  });

  it("相手の grad_year が小さい（卒業が早い）なら senior", () => {
    expect(relationOf(2024, 2022)).toBe("senior");
  });

  it("相手の grad_year が大きい（卒業が遅い）なら junior", () => {
    expect(relationOf(2022, 2024)).toBe("junior");
  });

  it("どちらかが null なら unknown", () => {
    expect(relationOf(null, 2024)).toBe("unknown");
    expect(relationOf(2024, null)).toBe("unknown");
    expect(relationOf(null, null)).toBe("unknown");
  });
});

describe("playerBadges（squad/caps 由来。他選手との突合はしない）", () => {
  it("squad が無ければバッジも無い", () => {
    expect(playerBadges(makePlayer())).toEqual([]);
  });

  it("squad が既知なら年代別/セブンズ代表バッジを返す", () => {
    const badges: Badge[] = playerBadges(makePlayer({ squad: "u20" }));
    expect(badges).toEqual([{ key: "squad-u20", label: "U20代表" }]);
  });

  it("未知の squad 値はバッジ化しない（保守的）", () => {
    expect(playerBadges(makePlayer({ squad: "unknown-squad" }))).toEqual([]);
  });

  it("caps があれば代表バッジを追加する", () => {
    const badges = playerBadges(
      makePlayer({ squad: "sevens_m", caps: { team: "日本", count: 3, source_url: null } }),
    );
    expect(badges).toEqual([
      { key: "squad-sevens_m", label: "セブンズ代表(男子)" },
      { key: "caps", label: "日本代表" },
    ]);
  });
});

// data/master の実データに対するスモークテスト（P1〜P5で投入済みの学校・選手のみ存在）
describe("getSchoolPlayerIndex / getPlayersBySchool / getSchoolmates（実データ読み込み）", () => {
  it("学校インデックスを例外なく構築できる", async () => {
    const index = await getSchoolPlayerIndex();
    expect(index.size).toBeGreaterThan(0);
  });

  it("school_id が既知の学校は選手が引ける", async () => {
    const index = await getSchoolPlayerIndex();
    const [schoolId] = Array.from(index.keys());
    const players = await getPlayersBySchool(schoolId);
    expect(players.length).toBeGreaterThan(0);
    for (const p of players) {
      expect(p.education.some((e) => e.school_id === schoolId)).toBe(true);
    }
  });

  it("未知の school_id は空配列を返す", async () => {
    expect(await getPlayersBySchool("__no_such_school__")).toEqual([]);
  });

  it("school_id を持つ選手の getSchoolmates は例外なく動作し、自分自身は含まない", async () => {
    const players = await getAllPlayers();
    const withSchool = players.find((p) => p.education.some((e) => e.school_id));
    expect(withSchool).toBeDefined();
    if (!withSchool) return;

    const groups = await getSchoolmates(withSchool);
    for (const group of groups) {
      expect(group.mates.every((m) => m.player.id !== withSchool.id)).toBe(true);
      for (const mate of group.mates) {
        expect(["senior", "junior", "sync", "unknown"]).toContain(mate.relation);
      }
    }
  });
});
