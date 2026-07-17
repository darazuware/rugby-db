import { describe, expect, it } from "vitest";
import { positionJa } from "../positions";

describe("positionJa", () => {
  it("null/undefined/空文字は null", () => {
    expect(positionJa(null)).toBeNull();
    expect(positionJa(undefined)).toBeNull();
    expect(positionJa("")).toBeNull();
    expect(positionJa("  ")).toBeNull();
  });

  it("既知の略号を日本語に変換する", () => {
    expect(positionJa("PR")).toBe("プロップ");
    expect(positionJa("HO")).toBe("フッカー");
    expect(positionJa("LO")).toBe("ロック");
    expect(positionJa("FL")).toBe("フランカー");
    expect(positionJa("No8")).toBe("ナンバーエイト");
    expect(positionJa("SH")).toBe("スクラムハーフ");
    expect(positionJa("SO")).toBe("スタンドオフ");
    expect(positionJa("CTB")).toBe("センター");
    expect(positionJa("WTB")).toBe("ウィング");
    expect(positionJa("FB")).toBe("フルバック");
  });

  it("未知のコード（既に日本語の生値を含む）はそのまま返す", () => {
    expect(positionJa("ウィング")).toBe("ウィング");
    expect(positionJa("XYZ")).toBe("XYZ");
  });
});
