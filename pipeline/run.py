"""パイプライン CLI（02の run.py 挙動）。

    python3 -m pipeline.run --league top14 [--dry-run]
    python3 -m pipeline.run --all [--dry-run]
    python3 -m pipeline.run --all --only matches,standings [--dry-run]

scrape → transform → validate（03）→ diff → master 書き込み の順。
検証エラーは exit 1 で master を書き換えない。
個々のリーグ scrape/transform は P1-3 以降で実装（未実装リーグは NotImplementedError）。

`--only matches,standings`（05: 試合日の軽量ジョブ、23:30 JST 追加実行用）:
  個別リーグごとの matches/standings 専用スクレイパーは未実装のため、既存スクレイパーは
  そのまま呼ぶ（players/teams も取得はされる）。ただし書き込み・差分・ニュース生成の対象を
  matches/standings のみに絞る。理由（00 原則5: 判断に迷ったら保守的に）:
    - 同日内に signings/departures/caps の差分検知を2回走らせると、
      pending_departures の「2回連続確認」が同日中の2回の実行で成立してしまい、
      本来「日をまたいで2回」を意図した誤検知防止ロジックが壊れる。
    - よって --only 指定時は players/teams の master 書き込みと pending_departures の
      更新・player系diff（signings/transfers/departures/first_caps/caps_updates）の生成を
      スキップし、matches/standings の書き込みと newly_finished_rounds diff のみ行う。
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime

from pipeline import callups, io
from pipeline.diffs import detect as diffs_detect
from pipeline.scrape import all_rugby, highschool, jrfu, league_one, university
from pipeline.validate import checks

# league key → (scrape+transform を行う callable)。P1-3 以降で埋める。
SCRAPERS: dict[str, object] = {
    "league-one-d1": lambda: league_one.collect("d1"),
    "league-one-d2": lambda: league_one.collect("d2"),
    "league-one-d3": lambda: league_one.collect("d3"),
    "top14": lambda: all_rugby.collect("top14"),
    "super-rugby": lambda: all_rugby.collect("super-rugby-pacific"),
    "mlr": lambda: all_rugby.collect("mlr"),
    # 2026-07-26: フルスコッド化（旧 P4-6 部分収集を廃止）。with_caps=True で
    # national.json（日本代表＋直近対戦国のみ）がカバーしない国の代表キャップも取得する。
    "urc": lambda: all_rugby.collect("urc", with_caps=True),
    "premiership": lambda: all_rugby.collect("premiership", with_caps=True),
    "national": lambda: all_rugby.collect_national(),
    "sevens-national": lambda: jrfu.collect_sevens(),
    "age-grade": lambda: jrfu.collect_age_grade(),
    "university": university.collect_all,
    "highschool": highschool.collect_all,
}
ALL_LEAGUES = [
    "league-one-d1", "league-one-d2", "league-one-d3",
    "top14", "super-rugby", "mlr", "urc", "premiership", "national",
    "sevens-national", "age-grade", "university", "highschool",
]


def _load_manual():
    return (
        io.read_manual("player_merges.json", default={}),
        io.read_manual("caps_corrections.json", default={}),
    )


VALID_ONLY = {"matches", "standings"}


def _merge_announced_transfers(league: str, players: list[dict]) -> list[dict]:
    """gap C: 公式に加入発表済みだが、現行ロースターページには未反映の選手を補完する。

    data/manual/announced_transfers.json（人力キュレーション。league-one.jp等の
    ALLOWED_DOMAINS 一次ソースのみを根拠に手動追加）を対象リーグにマージする。
    既にスクレイパーが同名選手をそのチームで取得済みなら（＝公式ロースターに反映済み）
    重複を避けて手動分をスキップする（保守的: 判断に迷ったら重複させない）。
    """
    announced = io.read_manual("announced_transfers.json", default=[])
    if not announced:
        return players
    existing_names = {
        (p.get("name_en") or "").strip().lower()
        for p in players
        if p.get("name_en")
    }
    merged = list(players)
    for entry in announced:
        if entry.get("league") != league:
            continue
        name_en = (entry.get("name_en") or "").strip().lower()
        if name_en and name_en in existing_names:
            continue  # 公式ロースターに反映済み。手動分は不要。
        rec = {k: v for k, v in entry.items() if k != "note"}
        rec.setdefault("source", "manual-curated")
        rec.setdefault("scraped_at", datetime.now(io.JST).isoformat(timespec="seconds"))
        merged.append(rec)
    return merged


def run_leagues(leagues: list[str], *, dry_run: bool, only: set[str] | None = None) -> int:
    players_by_league: dict[str, list[dict]] = {}
    prev_by_league: dict[str, list[dict]] = {}
    teams: list[dict] = []
    matches: list[dict] = []
    standings: list[dict] = []
    all_warnings: list[str] = []
    national_call_ups: list[dict] = []  # gap B: 招集・合宿イベント（national のみ）

    for league in leagues:
        scraper = SCRAPERS.get(league)
        if scraper is None:
            print(f"[skip] {league}: スクレイパー未実装（P1-3以降）", file=sys.stderr)
            continue
        result = scraper()  # -> {players, teams, matches, standings, warnings}
        players_by_league[league] = _merge_announced_transfers(
            league, result.get("players", []),
        )
        if league == "national":
            national_call_ups = result.get("call_ups", [])
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
    #    --only 指定時は player系diff / pending 更新をスキップする（理由は本ファイル冒頭参照）。
    matches_by_key: dict[tuple[str, str], list[dict]] = {}
    for m in matches:
        matches_by_key.setdefault((m["league"], m["season"]), []).append(m)
    prev_matches: list[dict] = []
    for key in matches_by_key:
        prev_matches.extend(io.read_records(io.matches_path(*key)))

    if only:
        diffs_by_league = {
            league: {
                "league": league,
                "signings": [], "transfers": [], "departures": [],
                "first_caps": [], "caps_updates": [], "pending_departures": [],
                "newly_finished_rounds": diffs_detect.diff_matches(
                    [m for m in matches if m.get("league") == league],
                    [m for m in prev_matches if m.get("league") == league],
                ),
            }
            for league in players_by_league
        }
    else:
        pending = io.read_pending_departures()
        diffs_by_league, pending = diffs_detect.run_all(
            players_by_league, prev_by_league, pending,
            matches=matches, prev_matches=prev_matches,
        )
        io.write_pending_departures(pending)

    # gap B: 招集・合宿イベントの突合→差分→マスタ化。
    # call_ups は pending_departures の「2回連続確認」ロジックと無関係（別state file）
    # なので --only 時もスキップしない（速報性優先。Yahoo/Google砲は発表当日中の記事化が鍵）。
    # 新規イベントは national diff に "call_ups" として注入し news_gen が記事化する。
    callup_master: list[dict] | None = None
    if national_call_ups and "national" in diffs_by_league:
        now_iso = datetime.now(io.JST).isoformat(timespec="seconds")
        evs = callups.assign_member_ids(national_call_ups, players_by_league.get("national", []))
        prev_callups = io.read_records(io.callups_path("national"))
        new_events = callups.diff_new_events(evs, prev_callups, league="national")
        diffs_by_league["national"]["call_ups"] = new_events
        new_recs = callups.build_event_records(evs, league="national", scraped_at=now_iso)
        callup_master = callups.merge_event_master(prev_callups, new_recs)
        if new_events:
            print(f"[callup] national: 新規イベント {len(new_events)} 件 "
                  f"（{', '.join(e.get('title') or e['id'] for e in new_events)}）")

    for league, diff in diffs_by_league.items():
        io.write_diff_report(league, diff)
        n = (len(diff["signings"]) + len(diff["transfers"]) + len(diff["departures"])
             + len(diff["first_caps"]) + len(diff["caps_updates"]) + len(diff["newly_finished_rounds"]))
        if n:
            print(f"[diff] {league}: signings={len(diff['signings'])} "
                  f"transfers={len(diff['transfers'])} departures={len(diff['departures'])} "
                  f"first_caps={len(diff['first_caps'])} caps_updates={len(diff['caps_updates'])} "
                  f"rounds={len(diff['newly_finished_rounds'])}")

    if dry_run:
        for league, players in players_by_league.items():
            print(f"{league}: 選手 {len(players)} 件")
        if matches:
            print(f"matches: {len(matches)} 件")
        print(f"--dry-run: master は書き込まない{'（--only=' + ','.join(sorted(only)) + '）' if only else ''}")
        return 0

    teams_by_league: dict[str, list[dict]] = {}
    for t in teams:
        teams_by_league.setdefault(t["league"], []).append(t)
    if not only:
        for league, players in players_by_league.items():
            io.write_records(io.players_path(league), players)
            new_teams = teams_by_league.get(league, [])
            # discover_official_urls（team_sites.py）が書いた official_url/home_area は
            # このスクレイパーの出力に含まれないため、上書きで消えないよう前回値を引き継ぐ。
            prev_teams = {t["id"]: t for t in io.read_records(io.teams_path(league))}
            for t in new_teams:
                prev = prev_teams.get(t["id"])
                if prev:
                    t["official_url"] = t.get("official_url") or prev.get("official_url")
                    t["home_area"] = t.get("home_area") or prev.get("home_area")
            io.write_records(io.teams_path(league), new_teams)
            io.update_last_run(
                league,
                counts={"players": len(players), "teams": len(teams_by_league.get(league, []))},
                warnings=[w for w in check.warnings + all_warnings if league in w],
            )
        if callup_master is not None:
            io.write_records(io.callups_path("national"), callup_master)
    if not only or "standings" in only:
        for st in standings:
            io.write_json(io.standings_path(st["league"], st["season"]), st)
    if not only or "matches" in only:
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
    ap.add_argument("--only", default=None,
                    help="matches,standings のみ更新する軽量モード（05: 23:30 JST 追加実行用）")
    args = ap.parse_args(argv)
    leagues = ALL_LEAGUES if args.all else [args.league]
    only: set[str] | None = None
    if args.only:
        only = {s.strip() for s in args.only.split(",") if s.strip()}
        invalid = only - VALID_ONLY
        if invalid:
            ap.error(f"--only に無効な値: {sorted(invalid)}（有効値: {sorted(VALID_ONLY)}）")
    return run_leagues(leagues, dry_run=args.dry_run, only=only)


if __name__ == "__main__":
    raise SystemExit(main())
