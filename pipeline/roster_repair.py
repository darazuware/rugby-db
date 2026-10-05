"""all.rugby の squad ページ混入で誤ったチームに割り当てられた選手を検査・是正する
（master は io 経由で書く。是正は移籍ではないので diff＝ニュース生成元は作らない）。

背景（2026-10-05 確認）: all.rugby の squad ページには他クラブの選手が混入する
（Super Rugby 全11クラブのページに共通の約20名、blues に Brumbies の選手、
bath に Bayonne の選手、glasgow に Bath の選手 等）。旧 all_rugby.collect は複数ページに
載る選手を「最初のクラブ」に割り当てていたため blues に Brumbies 選手が入った。

判定（選手個別ページの career＝現所属で突合。career が無い選手は個別ページを取得）:
1. 複数クラブのページ（全リーグ横断）に載る選手: 現所属と名前が一致するページが
   1つだけならそこへ（同リーグなら付け替え、他リーグならこのリーグから除外）。
   一致なし・複数一致は所属を決められないので除外。
2. 1ページだけに載る選手: career のどの時期にもそのチームが現れず、かつ現所属が
   別クラブなら混入として除外（現所属が同リーグの別クラブなら付け替え）。
   ローン・二重登録（career に親クラブが残る）や career 不明は触らない。
チーム名は squad ページの title と、所属選手の現所属で最頻の名前（例: edinburgh の
'Edimbourg Rugby'）の両方で照合する。1チームで所属の半数超が除外判定になる場合は
照合ミスとみなしそのチームは変更しない。

実行: python3.11 -m pipeline.roster_repair [--league super-rugby ...] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from typing import Callable, Optional

from pipeline import io
from pipeline.scrape import all_rugby
from pipeline.scrape.all_rugby import club_name_matches, current_club
from pipeline.validate import checks

LEAGUES = ("super-rugby", "top14", "urc", "premiership", "mlr")
SELF_NAME_SHARE = 0.4
MAX_DROP_SHARE = 0.5


def team_names(team_id: str, page_name: Optional[str], roster_careers: list[list[dict]]) -> list[str]:
    """チームの照合名: ページ title 名 ＋ 所属選手の現所属で最頻の名前（40%以上を占める場合）。"""
    names = [page_name] if page_name else []
    curs = [c for c in (current_club(cr) for cr in roster_careers) if c]
    if curs:
        name, n = Counter(curs).most_common(1)[0]
        if n / len(roster_careers) >= SELF_NAME_SHARE:
            names.append(name)
    return names or [team_id]


def _matches(names: list[str], club: Optional[str]) -> bool:
    return any(club_name_matches(n, club) for n in names)


def plan(players: list[dict], *, league_clubs: set[str], pages_of: dict[str, list[str]],
         names: dict[str, list[str]], career_of: Callable[[str], list[dict]],
         club_league: Optional[dict[str, str]] = None) -> dict:
    """{'move': {pid: (old, new)}, 'relocate': {pid: (old, club, league)}, 'drop': {pid: (old, 理由)}}
    を返す（純関数）。

    pages_of: 選手 slug → 掲載クラブ（全リーグ横断）。names: クラブ → 照合名リスト。
    club_league: 対象全リーグのクラブ → リーグ。除外判定になった選手でも、在籍中のクラブが
    対象リーグのクラブに一意に一致すればそこへ付け替え/他リーグへ移す（記事で言及される
    実在選手のページを消さないため。根拠は選手個別ページの career）。
    """
    move: dict = {}
    drop: dict = {}
    for p in players:
        pid, team = p["id"], p.get("team_id")
        if not pid.startswith("ar_") or not team:
            continue
        slug = pid[3:]
        pages = pages_of.get(slug, [])
        career = career_of(slug) or []
        cur = current_club(career)
        if len(pages) >= 2:
            hit = all_rugby.pick_club(pages, names, career)
            if hit is None and len(pages) <= 2:
                # 2クラブ間で決められない（例: exeter/northampton 両方に載る二重登録の若手）
                # ＝判断材料不足なので現状維持（原則3: 推測で動かさない）。
                # 3ページ以上に載り在籍先がどれとも一致しない（在籍情報なしを含む）選手は
                # 混入の典型（例: bath/pau/dragons に同じ5人）なので除外する。
                continue
            if hit is None:
                drop[pid] = (team, f"複数ページ{pages}に掲載・在籍中{all_rugby.active_clubs(career)}で決められない")
            elif hit in league_clubs:
                if hit != team:
                    move[pid] = (team, hit)
            else:
                drop[pid] = (team, f"在籍中 {all_rugby.active_clubs(career)} は他リーグ {hit}")
            continue
        if not cur or _matches(names.get(team, [team]), cur):
            continue
        if any(_matches(names.get(team, [team]), c.get("team")) for c in career):
            continue  # 過去/並行してこのチームに在籍（ローン・二重登録等）→触らない
        other = [c for c in league_clubs if c != team and _matches(names.get(c, [c]), cur)]
        if len(other) == 1:
            move[pid] = (team, other[0])
        else:
            drop[pid] = (team, f"在籍歴なし・現所属 {cur!r}")
    # 照合ミス対策: 半数超が除外判定のチームは変更しない
    roster = Counter(p.get("team_id") for p in players)
    lost = Counter(old for old, _ in list(drop.values()) + list(move.values()))
    bad = {t for t, n in lost.items() if roster[t] and n / roster[t] > MAX_DROP_SHARE}
    move = {k: v for k, v in move.items() if v[0] not in bad}
    drop = {k: v for k, v in drop.items() if v[0] not in bad}
    relocate: dict = {}
    if club_league:
        all_clubs = sorted(club_league)
        by_id = {p["id"]: p for p in players}
        for pid in list(drop):
            career = career_of(pid[3:]) or []
            if not all_rugby.active_clubs(career):
                continue
            home = all_rugby.pick_club(all_clubs, names, career)
            if home is None:
                continue
            old = drop[pid][0]
            if home in league_clubs:
                del drop[pid]
                if home != by_id[pid].get("team_id"):
                    move[pid] = (old, home)
            else:
                del drop[pid]
                relocate[pid] = (old, home, club_league[home])
    return {"move": move, "relocate": relocate, "drop": drop, "skipped_teams": sorted(bad)}


def apply_plan(players: list[dict], teams: list[dict], pl: dict) -> list[dict]:
    teams_by_id = {t["id"]: t for t in teams}
    out = []
    for p in players:
        pid = p["id"]
        if pid in pl["drop"] or pid in pl.get("relocate", {}):
            t = teams_by_id.get(p["team_id"])
            if t and pid in t.get("roster_ids", []):
                t["roster_ids"].remove(pid)
            continue
        if pid in pl["move"]:
            old, new = pl["move"][pid]
            if new not in teams_by_id:
                continue
            t_old = teams_by_id.get(old)
            if t_old and pid in t_old.get("roster_ids", []):
                t_old["roster_ids"].remove(pid)
            p = {**p, "team_id": new}
            if pid not in teams_by_id[new].setdefault("roster_ids", []):
                teams_by_id[new]["roster_ids"].append(pid)
        out.append(p)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--league", action="append", choices=LEAGUES)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--career-cache", default=None, help="個別ページ career の JSON キャッシュ（再実行時の再取得を省く）")
    args = ap.parse_args(argv)
    targets = args.league or list(LEAGUES)

    data = {lg: (io.read_records(io.teams_path(lg)), io.read_records(io.players_path(lg))) for lg in LEAGUES}
    # 全リーグのページを取得（他リーグ選手の混入も検出するため）
    pages_of: dict[str, list[str]] = {}
    page_name: dict[str, Optional[str]] = {}
    for lg in LEAGUES:
        for t in data[lg][0]:
            html = all_rugby._get(f"{all_rugby.BASE}/club/{t['id']}/squad")
            all_rugby.time.sleep(all_rugby._SLEEP)
            if html is None:
                print(f"{t['id']} squad 取得失敗。安全のため中止")
                return 1
            page_name[t["id"]] = all_rugby.parse_club_name(html)
            for r in all_rugby.parse_squad(html):
                pages_of.setdefault(r["slug"], [])
                if t["id"] not in pages_of[r["slug"]]:
                    pages_of[r["slug"]].append(t["id"])

    cache: dict[str, list[dict]] = {}
    for lg in LEAGUES:
        for p in data[lg][1]:
            if p["id"].startswith("ar_") and p.get("career"):
                cache[p["id"][3:]] = p["career"]

    from pathlib import Path
    cache_path = Path(args.career_cache) if args.career_cache else None
    if cache_path and cache_path.exists():
        cache.update({k: v for k, v in io.read_json(cache_path, {}).items() if k not in cache})

    def career_of(slug: str) -> list[dict]:
        if slug not in cache:
            cache[slug] = all_rugby._career_from_page(slug)
            if cache_path and len(cache) % 50 == 0:
                io.write_json(cache_path, cache)
        return cache[slug]

    names: dict[str, list[str]] = {}
    for lg in LEAGUES:
        teams, players = data[lg]
        for t in teams:
            careers = [career_of(pid[3:]) for pid in t.get("roster_ids", []) if pid.startswith("ar_")] \
                if lg in targets else []
            names[t["id"]] = team_names(t["id"], page_name.get(t["id"]), careers)

    if cache_path:
        io.write_json(cache_path, cache)
    rc = 0
    club_league = {t["id"]: lg for lg in LEAGUES for t in data[lg][0]}
    new_data = {lg: ([dict(t, roster_ids=list(t.get("roster_ids", []))) for t in data[lg][0]],
                     list(data[lg][1])) for lg in LEAGUES}
    incoming: dict[str, list[tuple[dict, str]]] = {lg: [] for lg in LEAGUES}
    corrections: dict[str, dict] = {}
    for lg in targets:
        teams, players = new_data[lg]
        pl = plan(players, league_clubs={t["id"] for t in teams}, pages_of=pages_of,
                  names=names, career_of=career_of, club_league=club_league)
        print(f"{lg}: 付け替え {len(pl['move'])} / 他リーグへ {len(pl['relocate'])} / 除外 {len(pl['drop'])}"
              f" / 変更見送りチーム {pl['skipped_teams']}")
        for pid, (o, n) in sorted(pl["move"].items()):
            print(f"  move {pid}: {o} -> {n}")
        for pid, (o, n, nl) in sorted(pl["relocate"].items()):
            print(f"  relocate {pid}: {o} -> {nl}/{n}")
        for pid, (o, why) in sorted(pl["drop"].items()):
            print(f"  drop {pid}: {o} ({why})")
        for pid, (_, n) in pl["move"].items():
            corrections[pid[3:]] = {"club": n, "reason": "付け替え"}
        for pid, (_, n, nl) in pl["relocate"].items():
            corrections[pid[3:]] = {"club": n, "reason": f"{nl} へ移動"}
        for pid, (_, why) in pl["drop"].items():
            # 他リーグ側で所属クラブが確定していればそちらを優先（None で上書きしない）
            corrections.setdefault(pid[3:], {"club": None, "reason": why})
        by_id = {p["id"]: p for p in players}
        for pid, (_, n, nl) in pl["relocate"].items():
            incoming[nl].append(({**by_id[pid], "league": nl, "team_id": n}, n))
        new_data[lg] = (teams, apply_plan(players, teams, pl))
    for lg, recs in incoming.items():
        teams, players = new_data[lg]
        ids = {p["id"] for p in players}
        tb = {t["id"]: t for t in teams}
        for rec, club in recs:
            if rec["id"] in ids:
                continue  # 既にそのリーグに居る（重複を作らない）
            players.append(rec)
            ids.add(rec["id"])
            if rec["id"] not in tb[club]["roster_ids"]:
                tb[club]["roster_ids"].append(rec["id"])
    for lg in LEAGUES:
        teams, players = new_data[lg]
        errs = checks.check_team_ref(players, teams).errors + checks.check_roster_sym(players, teams).errors
        errs += checks.check_dup_id({lg: players}).errors
        if errs:
            print(f"{lg}: 検証エラーのため全体を書き込まない: {errs[:5]}")
            return 1
    if not args.dry_run:
        for lg in LEAGUES:
            if new_data[lg][1] != data[lg][1] or new_data[lg][0] != data[lg][0]:
                io.write_records(io.players_path(lg), new_data[lg][1])
                io.write_records(io.teams_path(lg), new_data[lg][0])
        prune_player_pages()
        path = io.MANUAL_DIR / all_rugby.ROSTER_CORRECTIONS
        prev = io.read_json(path, {}).get("players", {})
        prev.update(corrections)
        io.write_json(path, {
            "_note": "pipeline/roster_repair.py が生成。all.rugby squad ページへの他クラブ選手混入の是正結果。"
                     "club=null は対象リーグのどのクラブにも採らない。根拠は https://all.rugby/player/{slug} の在籍歴。",
            "players": dict(sorted(prev.items())),
        })
        print(f"roster_corrections: {len(corrections)} 件を記録")
    return rc


def prune_player_pages() -> list[str]:
    """除外した選手を data/manual/player_pages.json（build_player_pages.py の生成物）から外す。
    次回の daily_update 再生成を待たずに、存在しない選手への個別ページ参照を残さないため。"""
    import glob
    ids = set()
    for f in glob.glob(str(io.MASTER_DIR / "players" / "*.json")):
        ids |= {p["id"] for p in io.read_records(io.Path(f))}
    path = io.MANUAL_DIR / "player_pages.json"
    pages = io.read_json(path, {})
    rows = pages.get("players", [])
    gone = [r["id"] for r in rows if r["id"] not in ids]
    if gone:
        pages["players"] = [r for r in rows if r["id"] in ids]
        # 生成元 scripts/build_player_pages.py と同じ書式（indent=1）で差分を最小にする
        path.write_text(json.dumps(pages, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"player_pages: 存在しない選手 {len(gone)} 件を除外 {gone}")
    return gone


if __name__ == "__main__":
    raise SystemExit(main())
