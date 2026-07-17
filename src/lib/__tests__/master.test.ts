import { describe, expect, it } from "vitest";
import { applyPlayerMerges, getAllPlayers, getAllTeams, type Player } from "../master";

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

describe("applyPlayerMerges", () => {
  it("merges が空なら元の配列をそのまま返す", () => {
    const players = [makePlayer({ id: "a" })];
    expect(applyPlayerMerges(players, {})).toBe(players);
  });

  it("dup を除外し canonical に merged_from を追記する", () => {
    const dup = makePlayer({ id: "ar_1", nationality: ["Japan"] });
    const canonical = makePlayer({ id: "lo_1" });
    const result = applyPlayerMerges([dup, canonical], { ar_1: "lo_1" });

    expect(result.map((p) => p.id)).toEqual(["lo_1"]);
    expect(result[0].merged_from).toContain("ar_1");
  });

  it("canonical が null の代表情報のみ dup から補う（既存値は上書きしない）", () => {
    const dup = makePlayer({
      id: "ar_1",
      caps: { team: "日本", count: 5, source_url: null },
      nationality: ["Japan"],
    });
    const canonicalWithCaps = makePlayer({
      id: "lo_1",
      caps: { team: "日本", count: 99, source_url: null },
      nationality: [],
    });
    const result = applyPlayerMerges([dup, canonicalWithCaps], { ar_1: "lo_1" });
    expect(result[0].caps?.count).toBe(99); // 既存値を上書きしない
    expect(result[0].nationality).toEqual(["Japan"]); // 空だったので補われる
  });

  it("canonical が dup 側の caps を持たなければ補う", () => {
    const dup = makePlayer({ id: "ar_1", caps: { team: "日本", count: 5, source_url: null } });
    const canonicalNoCaps = makePlayer({ id: "lo_1", caps: null });
    const result = applyPlayerMerges([dup, canonicalNoCaps], { ar_1: "lo_1" });
    expect(result[0].caps?.count).toBe(5);
  });

  it("canonical が players に存在しなければ何もしない（保守的）", () => {
    const dup = makePlayer({ id: "ar_1" });
    const result = applyPlayerMerges([dup], { ar_1: "missing_canonical" });
    expect(result.map((p) => p.id)).toEqual(["ar_1"]); // 除外されない
  });
});

// data/master の実データに対するスモークテスト（P1で投入済みのリーグのみ存在）
describe("getAllPlayers / getAllTeams（実データ読み込み）", () => {
  it("master の選手データを例外なく読み込める", async () => {
    const players = await getAllPlayers();
    expect(Array.isArray(players)).toBe(true);
    expect(players.length).toBeGreaterThan(0);
    for (const p of players.slice(0, 20)) {
      expect(typeof p.id).toBe("string");
      expect(typeof p.slug).toBe("string");
    }
  });

  it("slug が重複しない（getStaticPaths の前提）", async () => {
    const players = await getAllPlayers();
    const slugs = players.map((p) => p.slug);
    expect(new Set(slugs).size).toBe(slugs.length);
  });

  it("master のチームデータを例外なく読み込める", async () => {
    const teams = await getAllTeams();
    expect(Array.isArray(teams)).toBe(true);
    expect(teams.length).toBeGreaterThan(0);
  });
});
