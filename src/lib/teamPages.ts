/**
 * チームページ（/teams/{league}/{slug}）の存在確認つきリンク生成。
 * ページは data/teams.json から生成されるため、それに無い slug へはリンクしない（404回避）。
 * slug が一致しない場合はチーム名の完全一致のみで解決し、推測はしない。
 */
import teamsData from "../../data/teams.json";

type TeamRow = { league: string; slug?: string; team_name?: string; team_en_name?: string };

const teams = (teamsData as TeamRow[]).filter((t) => t.slug);
const pageSet = new Set(teams.map((t) => `${t.league}/${t.slug}`));

export function teamPageHref(
  league: string,
  slug?: string | null,
  names: (string | null | undefined)[] = [],
): string | null {
  if (slug && pageSet.has(`${league}/${slug}`)) return `/teams/${league}/${slug}`;
  const wanted = new Set(names.filter((n): n is string => !!n));
  if (wanted.size === 0) return null;
  const hit = teams.find(
    (t) => t.league === league && ((t.team_name && wanted.has(t.team_name)) || (t.team_en_name && wanted.has(t.team_en_name))),
  );
  return hit ? `/teams/${league}/${hit.slug}` : null;
}

/** 順位表の各行に href（ページが無ければ null）を付与する。 */
export function withTeamHref<T extends { slug?: string | null; team_name?: string; team_name_jp?: string; display_name?: string }>(
  league: string,
  rows: T[],
): (T & { href: string | null })[] {
  return rows.map((r) => ({
    ...r,
    href: teamPageHref(league, r.slug, [r.team_name, r.team_name_jp, r.display_name]),
  }));
}
