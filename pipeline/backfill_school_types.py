"""league-one 選手の出身校 education を再取得して補完する（type未判定の取りこぼし復旧）。

背景: scrape/league_one.py は type を判定できなかった出身校を education から落とす。
ANTHROPIC_API_KEY 未設定で llm_fallback が常に空を返していたため、league-one d1/d2/d3
で計375件の出身校が master に入らなかった。pipeline/school_types.py（ローカル辞書）を
追加したので、選手ページを再取得して education を作り直す。

使い方（2段階。fetch は 1400件超のGETで30分程度かかる）:
    python3.11 -m pipeline.backfill_school_types fetch --cache /path/segments.json
    python3.11 -m pipeline.backfill_school_types apply --cache /path/segments.json

fetch: 選手ページの「出身校・チーム歴」生セグメントだけを cache に保存（masterは触らない）。
apply: cache を分類して data/master/players/league-one-d*.json の education を更新する。
       既存 entry の school_id は name_raw 一致で引き継ぐ。判定できない表記は入れない
       （00原則3: 不明はnull）。選手の氏名・所属等の他フィールドは一切変更しない。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from pipeline import io, school_types
from pipeline.scrape import league_one as lo

LEAGUES = ("league-one-d1", "league-one-d2", "league-one-d3")


def _pid(player_id: str) -> str:
    return player_id.replace("lo_", "")


def cmd_fetch(cache: Path, sleep: float) -> int:
    data: dict = json.loads(cache.read_text()) if cache.exists() else {}
    targets: list[tuple[str, str]] = []
    for league in LEAGUES:
        for p in io.read_records(io.players_path(league)):
            targets.append((_pid(p["id"]), league))
    todo = [(pid, lg) for pid, lg in targets if pid not in data]
    print(f"{len(todo)} 件取得（済 {len(data)}）", flush=True)
    for i, (pid, league) in enumerate(todo, 1):
        html = lo._get(f"{lo.BASE}/player/{pid}")
        time.sleep(sleep)
        if html is None:
            data[pid] = {"league": league, "segments": None}
        else:
            raw = lo.parse_player_page(html, pid)
            data[pid] = {"league": league, "segments": raw.get("education_segments_raw")}
        if i % 25 == 0:
            cache.write_text(json.dumps(data, ensure_ascii=False))
            print(f"  {i}/{len(todo)}", flush=True)
    cache.write_text(json.dumps(data, ensure_ascii=False))
    failed = sum(1 for v in data.values() if v["segments"] is None)
    print(f"完了: {len(data)} 件（取得失敗 {failed} 件）")
    return 0


def _schools_index() -> dict[str, str]:
    """schools.json の name -> type（typeが一意に決まる名前のみ）。

    既存の学校マスタを表記辞書として使う。AIの知識で type を決めない
    （03_VALIDATION.md）。
    """
    types: dict[str, set[str]] = {}
    for s in io.read_records(io.schools_path()):
        name = (s.get("name") or "").strip()
        if name and s.get("type"):
            types.setdefault(name, set()).add(s["type"])
    return {n: t.pop() for n, t in types.items() if len(t) == 1}


def cmd_apply(cache: Path, dry_run: bool) -> int:
    data: dict = json.loads(cache.read_text())
    schools = _schools_index()
    unresolved: set[str] = set()
    added = changed_players = 0

    for league in LEAGUES:
        path = io.players_path(league)
        players = io.read_records(path)
        touched = 0
        for p in players:
            entry = data.get(_pid(p["id"]))
            if entry is None or entry.get("segments") is None:
                continue
            old = p.get("education") or []
            by_name = {e.get("name_raw"): e for e in old}
            education = []
            for seg in entry["segments"]:
                t = (lo._classify_school_regex(seg) or school_types.classify(seg)
                     or schools.get(seg.strip()))
                if t is None:
                    unresolved.add(seg)
                    continue
                prev = by_name.get(seg, {})
                education.append({
                    "school_id": prev.get("school_id"),
                    "name_raw": seg,
                    "type": t,
                    "grad_year": prev.get("grad_year"),
                    "source_url": prev.get("source_url"),
                    "scraped_at": prev.get("scraped_at"),
                })
            if education != old:
                added += max(0, len(education) - len(old))
                touched += 1
                p["education"] = education
        changed_players += touched
        print(f"{league}: {touched} 選手更新")
        if not dry_run:
            io.write_records(path, players)

    print(f"合計 {changed_players} 選手 / education +{added} 件"
          f"{'（dry-run: 書き込みなし）' if dry_run else ''}")
    if unresolved:
        print(f"未判定のまま {len(unresolved)} 表記: {sorted(unresolved)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--cache", required=True, type=Path)
    f.add_argument("--sleep", type=float, default=1.2)
    a = sub.add_parser("apply")
    a.add_argument("--cache", required=True, type=Path)
    a.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "fetch":
        return cmd_fetch(args.cache, args.sleep)
    return cmd_apply(args.cache, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
