/**
 * positions.ts
 * ポジション略号 → 日本語対訳表（04）。
 *
 * data/master の position フィールドはソースの生値（league-one.jp は英語略号、
 * all.rugby 系はソースによって略号または日本語の場合がある）。
 * ここに無いキーはそのまま返す（＝既に日本語の値をそのまま通す。事実の書き換え禁止）。
 */

export const POSITION_JA: Readonly<Record<string, string>> = Object.freeze({
  // プロップ
  PR: "プロップ",
  LH: "プロップ（左PR）",
  TH: "プロップ（右PR）",
  // フッカー
  HO: "フッカー",
  // ロック
  LO: "ロック",
  SR: "ロック",
  // フランカー / バックロー
  FL: "フランカー",
  BR: "バックロー",
  // ナンバーエイト
  No8: "ナンバーエイト",
  N8: "ナンバーエイト",
  NO8: "ナンバーエイト",
  // スクラムハーフ
  SH: "スクラムハーフ",
  HB: "スクラムハーフ",
  // スタンドオフ
  SO: "スタンドオフ",
  FH: "スタンドオフ",
  // センター
  CTB: "センター",
  CE: "センター",
  IC: "インサイドセンター",
  OC: "アウトサイドセンター",
  // ウィング
  WTB: "ウィング",
  WG: "ウィング",
  // フルバック
  FB: "フルバック",
  FBK: "フルバック",
  // ユーティリティバック
  UTB: "ユーティリティバック",
});

/**
 * position コードを日本語表記に変換する。
 * null/undefined/空文字は null を返す（04: null 項目の文は出さない）。
 * 対訳表に無いコード（既に日本語の値を含む）はそのまま返す。
 */
export function positionJa(position: string | null | undefined): string | null {
  if (position == null) return null;
  const code = position.trim();
  if (code === "") return null;
  return POSITION_JA[code] ?? code;
}
