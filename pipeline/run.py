"""パイプライン CLI（02の run.py 挙動）。

    python3 -m pipeline.run --league top14 [--dry-run]
    python3 -m pipeline.run --all [--dry-run]

scrape → transform → validate（03）→ diff → master 書き込み の順。
検証エラーは exit 1 で master を書き換えない。
個々のリーグ scrape/transform は P1-3 以降で実装（未実装リーグは NotImplementedError）。
"""
from __future__ import annotations

import argparse
import sys

from pipeline import io
from pipeline.diffs import detect as diffs_detect
from pipeline.scrape import all_rugby, league_one
from pipeline.validate import checks

# league key → (scrape+transform を行う callable)。P1-3 以降で埋める。
SCRAPERS: dict[str, object] = {
    "league-one-d1": lambda: league_one.collect("d1"),
    "league-one-d2": lambda: league_one.collect("d2"),
    "league-one-d3": lambda: league_one.collect("d3"),
    "top14": lambda: all_rugby.collect("top14"),
    "super-rugby": lambda: all_rugby.collect("super-rugby-pacific"),
    "national": lambda: all_rugby.collect_national(),
}
ALL_LEAGUES = [
    "league-one-d1", "league-one-d2", "league-one-d3",
    "top14", "super-rugby", "national",
]


def _load_manual():
    return (
        io.read_manual("player_merges.json", default={}),
        io.read_manual("caps_corrections.json", default={}),
    )


def run_leagues(leagues: list[str], *, dry_run: bool) -> int:
    players_by_league: dict[str, list[dict]] = {}
    prev_by_league: dict[str, list[dict]] = {}
    teams: list[dict] = []
    matches: list[dict] = []
    standings: list[dict] = []
    all_warnings: list[str] = []

    for league in leagues:
        scraper = SCRAPERS.get(league)
        if scraper is None:
            print(f"[skip] {league}: スクレイパー未実装（P1-3以降）", file=sys.stderr)
            continue
        result = scraper()  # -> {players, teams, matches, standings, warnings}
        players_by_league[league] = result.get("players", [])
        teams.extend(result.get("teams", []))
        matches.extend(result.get("matches", []))
        standings.extend(result.get("standings", []))
        all_warnings.extend(result.get("warnings", []))
        prev_by_league[league] = io.read_records(io.players_path(league))

    if not players_by_league:
        print("取得0件。exit 1", file=sys.stderr)
        return 1

    merges, corrections = _load_manual()
    check = checks.run_all(
        players_by_league, teams, matches, standings,
        prev_players_by_league=prev_by_league,
        player_merges=merges, caps_corrections=corrections,
    )
    for w in all_warnings + check.warnings:
        print(f"[warn] {w}", file=sys.stderr)
    if check.merge_candidates:
        io.write_json(io.META_DIR / "merge_candidates.json", check.merge_candidates)
    if not check.ok:
        for e in check.errors:
            print(f"[error] {e}", file=sys.stderr)
        print(f"検証失敗 {len(check.errors)} 件。master は更新しない。", file=sys.stderr)
        return 1

    # 4. diffs.detect（02）: 前回masterとの差分 → _meta/diff/{date}_{league}.json
    #    pending_departures（05: 2回連続確認）も併せて更新する。
    matches_by_key: dict[tuple[str, str], list[dict]] = {}
    for m in matches:
        matches_by_key.setdefault((m["league"], m["season"]), []).append(m)
    prev_matches: list[dict] = []
    for key in matches_by_key:
        prev_matches.extend(io.read_records(io.matches_path(*key)))

    pending = io.read_pending_departures()
    diffs_by_league, pending = diffs_detect.run_all(
        players_by_league, prev_by_league, pending,
        matches=matches, prev_matches=prev_matches,
    )
    for league, diff in diffs_by_league.items():
        io.write_diff_report(league, diff)
        n = (len(diff["signings"]) + len(diff["transfers"]) + len(diff["departures"])
             + len(diff["first_caps"]) + len(diff["caps_updates"]))
        if n:
            print(f"[diff] {league}: signings={len(diff['signings'])} "
                  f"transfers={len(diff['transfers'])} departures={len(diff['departures'])} "
                  f"first_caps={len(diff['first_caps'])} caps_updates={len(diff['caps_updates'])}")
    io.write_pending_departures(pending)

    if dry_run:
        for league, players in players_by_league.items():
            print(f"{league}: 選手 {len(players)} 件")
        if matches:
            print(f"matches: {len(matches)} 件")
        print("--dry-run: master は書き込まない")
        return 0

    teams_by_league: dict[str, list[dict]] = {}
    for t in teams:
        teams_by_league.setdefault(t["league"], []).append(t)
    for league, players in players_by_league.items():
        io.write_records(io.players_path(league), players)
        io.write_records(io.teams_path(league), teams_by_league.get(league, []))
        io.update_last_run(
            league,
            counts={"players": len(players), "teams": len(teams_by_league.get(league, []))},
            warnings=[w for w in check.warnings + all_warnings if league in w],
        )
    for st in standings:
        io.write_json(io.standings_path(st["league"], st["season"]), st)
    for (league, season), ms in matches_by_key.items():
        io.write_records(io.matches_path(league, season), ms)
    print("master 更新完了")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pipeline.run")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--league", choices=ALL_LEAGUES)
    g.add_argument("--all", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    leagues = ALL_LEAGUES if args.all else [args.league]
    return run_leagues(leagues, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
