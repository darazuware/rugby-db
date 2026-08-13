/**
 * 人名で頻出する異体字（旧字体/新字体・IME変換違い）のペア。
 * 検索・IME変換ミスによる表記ゆれ流入を拾うため、meta descriptionに両表記を併記する用途。
 * 事実の創作ではなく、同一文字の別字形なので原則2に抵触しない。
 */
const VARIANT_PAIRS: [string, string][] = [
  ["龍", "竜"],
  ["髙", "高"],
  ["﨑", "崎"],
  ["澤", "沢"],
  ["廣", "広"],
  ["邊", "辺"],
  ["邉", "辺"],
  ["齋", "斎"],
  ["齊", "斎"],
  ["櫻", "桜"],
  ["濵", "浜"],
  ["實", "実"],
  ["惠", "恵"],
  ["德", "徳"],
  ["彌", "弥"],
];

/** name中の異体字を置換候補ごとに展開し、元と異なる表記のみ返す（重複除去）。 */
export function kanjiVariants(name: string): string[] {
  const results = new Set<string>();
  for (const [a, b] of VARIANT_PAIRS) {
    if (name.includes(a)) {
      const swapped = name.split(a).join(b);
      if (swapped !== name) results.add(swapped);
    }
    if (name.includes(b)) {
      const swapped = name.split(b).join(a);
      if (swapped !== name) results.add(swapped);
    }
  }
  results.delete(name);
  return [...results];
}
