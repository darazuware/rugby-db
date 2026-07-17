import { describe, expect, it } from "vitest";
import type { Player } from "../master";
import {
  birthPhysicalSentence,
  buildPlayerBio,
  buildPlayerBioSentences,
  calcAge,
  capsSentence,
  careerSentence,
  educationSentence,
  introSentence,
  leagueCapsSentence,
  seasonStatsSentence,
} from "../playerText";

/** 全項目 null の最小選手データ。各テストで必要な項目だけ上書きする。 */
function makePlayer(overrides: Partial<Player> = {}): Player {
  return {
    id: "lo_1",
    source: "league-one.jp",
    source_url: "https://league-one.jp/player/1",
    scraped_at: "2026-07-14T00:00:00+09:00",
    name_en: null,
    name_ja: null,
    name_kana: null,
    slug: "test-1",
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

describe("calcAge", () => {
  it("null の birthdate は null を返す", () => {
    expect(calcAge(null)).toBeNull();
    expect(calcAge(undefined)).toBeNull();
  });

  it("誕生日前は年齢を1引く", () => {
    const asOf = new Date("2026-07-18T00:00:00+09:00");
    expect(calcAge("1991-10-19", asOf)).toBe(34);
  });

  it("誕生日を過ぎていればそのまま", () => {
    const asOf = new Date("2026-07-18T00:00:00+09:00");
    expect(calcAge("1991-01-01", asOf)).toBe(35);
  });
});

describe("introSentence — null 値は文を出さない", () => {
  it("name_ja が null なら null", () => {
    const p = makePlayer({ name_ja: null, position: "PR", team_id: "t1" });
    expect(introSentence(p, "浦安D-Rocks")).toBeNull();
  });

  it("team・position 両方 null なら null", () => {
    const p = makePlayer({ name_ja: "田中真一" });
    expect(introSentence(p, null)).toBeNull();
  });

  it("team・position 揃っていれば文を出し、'null' という文字列を含まない", () => {
    const p = makePlayer({ name_ja: "田中真一", name_kana: "タナカシンイチ", position: "FL" });
    const s = introSentence(p, "浦安D-Rocks");
    expect(s).toBe("田中真一（タナカシンイチ）は浦安D-Rocks所属のフランカー。");
    expect(s).not.toContain("null");
    expect(s).not.toContain("undefined");
  });

  it("name_kana が null なら括弧を出さない", () => {
    const p = makePlayer({ name_ja: "田中真一", name_kana: null, position: "FL" });
    const s = introSentence(p, "浦安D-Rocks");
    expect(s).toBe("田中真一は浦安D-Rocks所属のフランカー。");
  });

  it("position が未知コードでもそのまま通す（既に日本語の生値を想定）", () => {
    const p = makePlayer({ name_ja: "選手A", position: "ウィング" });
    const s = introSentence(p, null);
    expect(s).toBe("選手Aはウィング。");
  });
});

describe("birthPhysicalSentence — null 値は文を出さない", () => {
  it("すべて null なら null", () => {
    expect(birthPhysicalSentence(makePlayer())).toBeNull();
  });

  it("身長体重のみあれば身長体重だけの文", () => {
    const p = makePlayer({ height_cm: 186, weight_kg: 102 });
    expect(birthPhysicalSentence(p)).toBe("186cm・102kg。");
  });

  it("身長のみ、体重は出さない", () => {
    const p = makePlayer({ height_cm: 186, weight_kg: null });
    const s = birthPhysicalSentence(p);
    expect(s).toBe("186cm。");
    expect(s).not.toContain("null");
  });

  it("生年月日と体格が揃えば両方入る", () => {
    const p = makePlayer({ birthdate: "1991-10-19", height_cm: 172, weight_kg: 88 });
    const asOf = new Date("2026-07-18T00:00:00+09:00");
    expect(birthPhysicalSentence(p, asOf)).toBe("1991年10月19日生まれ34歳、172cm・88kg。");
  });
});

describe("capsSentence", () => {
  it("caps が null なら null", () => {
    expect(capsSentence(makePlayer())).toBeNull();
  });

  it("caps があれば文を出す", () => {
    const p = makePlayer({ caps: { team: "日本", count: 12, source_url: null } });
    expect(capsSentence(p)).toBe("日本代表キャップ12。");
  });
});

describe("leagueCapsSentence", () => {
  it("league_caps が null なら null", () => {
    expect(leagueCapsSentence(makePlayer())).toBeNull();
  });

  it("league-one 所属ならリーグワン表記", () => {
    const p = makePlayer({ league: "league-one-d1", league_caps: 34 });
    expect(leagueCapsSentence(p)).toBe("リーグワン通算34キャップ。");
  });

  it("top14 所属なら Top14 表記（ハードコードの誤表記を避ける）", () => {
    const p = makePlayer({ league: "top14", league_caps: 20 });
    expect(leagueCapsSentence(p)).toBe("Top14通算20キャップ。");
  });
});

describe("educationSentence", () => {
  it("education が空なら null", () => {
    expect(educationSentence(makePlayer())).toBeNull();
  });

  it("type=='univ' の要素が無ければ null（高校のみは対象外）", () => {
    const p = makePlayer({
      education: [{ school_id: null, name_raw: "○○高校", type: "hs", grad_year: null, source_url: null, scraped_at: null }],
    });
    expect(educationSentence(p)).toBeNull();
  });

  it("univ の name_raw があれば文を出す", () => {
    const p = makePlayer({
      education: [{ school_id: null, name_raw: "早稲田大学", type: "univ", grad_year: null, source_url: null, scraped_at: null }],
    });
    expect(educationSentence(p)).toBe("早稲田大学出身。");
  });

  it("is_minor=true なら univ 情報があっても出さない（10のポリシー）", () => {
    const p = makePlayer({
      is_minor: true,
      education: [{ school_id: null, name_raw: "○○高校", type: "univ", grad_year: null, source_url: null, scraped_at: null }],
    });
    expect(educationSentence(p)).toBeNull();
  });
});

describe("careerSentence", () => {
  it("career が空なら null", () => {
    expect(careerSentence(makePlayer())).toBeNull();
  });

  it("career があればチーム名を列挙", () => {
    const p = makePlayer({
      career: [
        { team: "パナソニック", from: 2018, to: 2022, source_url: null },
        { team: "浦安D-Rocks", from: 2022, to: null, source_url: null },
      ],
    });
    expect(careerSentence(p)).toBe("これまでパナソニック、浦安D-Rocksでプレー。");
  });
});

describe("seasonStatsSentence", () => {
  it("season_stats が null なら null", () => {
    expect(seasonStatsSentence(makePlayer())).toBeNull();
  });

  it("matches のみあれば matches だけ", () => {
    const p = makePlayer({ season_stats: { season: "2025-26", matches: 10, tries: null, points: null } });
    const s = seasonStatsSentence(p);
    expect(s).toBe("2025-26シーズンは10試合出場。");
    expect(s).not.toContain("null");
  });

  it("matches・tries 両方あれば両方", () => {
    const p = makePlayer({ season_stats: { season: "2025-26", matches: 10, tries: 3, points: null } });
    expect(seasonStatsSentence(p)).toBe("2025-26シーズンは10試合出場、3トライ。");
  });

  it("matches・tries とも null なら文自体を出さない", () => {
    const p = makePlayer({ season_stats: { season: "2025-26", matches: null, tries: null, points: null } });
    expect(seasonStatsSentence(p)).toBeNull();
  });
});

describe("buildPlayerBioSentences / buildPlayerBio", () => {
  it("全項目 null の選手は空配列・空文字（'null'を含む文が一切出ない）", () => {
    const p = makePlayer();
    expect(buildPlayerBioSentences(p, { teamName: null })).toEqual([]);
    expect(buildPlayerBio(p, { teamName: null })).toBe("");
  });

  it("一部だけ値がある選手は該当する文だけを含み、'null'を含む文は出ない", () => {
    const p = makePlayer({
      name_ja: "田中真一",
      position: "PR",
      height_cm: 186,
      weight_kg: null,
      birthdate: null,
      caps: null,
      league_caps: 5,
    });
    const sentences = buildPlayerBioSentences(p, { teamName: "浦安D-Rocks" });
    expect(sentences.length).toBe(3); // intro, physical(身長のみ), league_caps
    for (const s of sentences) {
      expect(s).not.toContain("null");
      expect(s).not.toContain("undefined");
    }
    expect(buildPlayerBio(p, { teamName: "浦安D-Rocks" })).toBe(sentences.join(""));
  });

  it("フル項目が埋まっている選手は7文すべてを含む", () => {
    const p = makePlayer({
      name_ja: "田中真一",
      name_kana: "タナカシンイチ",
      position: "FL",
      birthdate: "1998-04-02",
      height_cm: 186,
      weight_kg: 102,
      caps: { team: "日本", count: 12, source_url: null },
      league_caps: 34,
      education: [{ school_id: null, name_raw: "早稲田大学", type: "univ", grad_year: null, source_url: null, scraped_at: null }],
      career: [{ team: "パナソニック", from: 2018, to: 2022, source_url: null }],
      season_stats: { season: "2025-26", matches: 10, tries: 3, points: null },
    });
    const sentences = buildPlayerBioSentences(p, {
      teamName: "浦安D-Rocks",
      asOf: new Date("2026-07-18T00:00:00+09:00"),
    });
    expect(sentences.length).toBe(7);
    for (const s of sentences) {
      expect(s).not.toContain("null");
      expect(s).not.toContain("undefined");
    }
  });
});
