/**
 * age.ts — 年齢計算（クライアント/サーバー共用の軽量モジュール）。
 * age 固定値は持たず、常に birthdate から計算する（docs/adsense/01_DESIGN.md §3）。
 */

/** YYYY-MM-DD（YYYY.MM.DD / YYYY/MM/DD も可）から満年齢を計算する。パース不能/null は null。 */
export function calcAge(birthdate: string | null | undefined, asOf: Date = new Date()): number | null {
  if (!birthdate) return null;
  const m = /^(\d{4})[-./](\d{1,2})[-./](\d{1,2})$/.exec(birthdate.trim());
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
