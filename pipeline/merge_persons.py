"""P1-4b 人物同一性突合（01_DATA_ARCHITECTURE.md / 03_VALIDATION.md）。

master/players/*.json を横断し、`lo_`×`ar_national` のような同一人物が別IDで
入っている候補を検出して `data/master/_meta/merge_candidates.json` に列挙する
（**自動確定はしない**。01 の canonical_id 運用）。確定は人が
`data/manual/player_merges.json`（`{"ar_12345": "lo_483678"}` = 重複ID→canonical）
に記録する。本モジュールはそれを読み、canonical へ統合（merged_from 追記・
代表情報マージ・重複レコード除外）して master を更新する。

突合キーは 03 の cross_person と同一（`normalize_name_en(name_en)` + `birthdate`）で、
候補検出は checks.check_cross_person をそのまま用いて連動させる。

    python3 -m pipeline.merge_persons                    # 候補を merge_candidates.json に出力（master 不変）
    python3 -m pipeline.merge_persons --apply            # player_merges を master に適用して書き戻す
    python3 -m pipeline.merge_persons --scrape-national  # master に national.json が無いとき scrape 結果で突合

方針（原則1〜5 に沿う最も保守的な選択）:
  - 自動マージしない。player_merges.json に無い候補は master を一切変えない。
  - 統合時に canonical の既存値は上書きしない。dup 側にしか無い代表情報
    （caps / nationality）だけを canonical が null/空のときに補う（01 L89）。
  - master に national.json が未コミットの場合、突合対象に national を含めるには
    all_rugby.collect_national() のスクレイプ結果を用いる（--scrape-national）。
    ただし --apply で master に書き戻すのは既存の master ファイルがあるリーグのみ
    （P1-7 未コミットの national.json を本タスクで新規作成しない）。
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field

from pipeline import io
from pipeline.validate import checks


@dataclass
class ApplyReport:
    applied: list[str] = field(default_factory=list)          # "ar_x -> lo_y"
    missing_canonical: list[str] = field(default_factory=list)  # canonical が master に無い
    missing_dup: list[str] = field(default_factory=list)        # 重複側が既に存在しない
    changed_leagues: set[str] = field(default_factory=set)


def load_players_by_league(*, scrape_national: bool = False) -> dict[str, list[dict]]:
    """master/players/*.json を全リーグ読み込む。league キーはファイル名 stem。

    national.json が master に無く scrape_national=True のときのみ、突合用に
    all_rugby.collect_national() の結果（in-memory）を national として足す。
    master には書き込まない。
    """
    by_league: dict[str, list[dict]] = {}
    players_dir = io.MASTER_DIR / "players"
    if players_dir.exists():
        for path in sorted(players_dir.glob("*.json")):
            by_league[path.stem] = io.read_records(path)
    if scrape_national and "national" not in by_league:
        from pipeline.scrape import all_rugby
        result = all_rugby.collect_national()
        by_league["national"] = result.get("players", [])
    return by_league


def find_candidates(players_by_league: dict[str, list[dict]],
                    player_merges: dict[str, str] | None = None) -> list[dict]:
    """未解決の同一人物候補を列挙（03 cross_person と連動）。"""
    return checks.check_cross_person(players_by_league, player_merges).merge_candidates


def apply_merges(players_by_league: dict[str, list[dict]],
                 player_merges: dict[str, str]) -> ApplyReport:
    """player_merges を players_by_league に適用（in-place）して統合する。

    dup_id → canonical_id ごとに:
      - dup レコードを所属リーグの配列から除外
      - canonical.merged_from に dup_id（と dup の merged_from）を追加
      - canonical が持たない代表情報（caps / nationality）を dup から補う（01 L89）
    """
    report = ApplyReport()
    index: dict[str, tuple[str, dict]] = {}
    for league, players in players_by_league.items():
        for p in players:
            index[p["id"]] = (league, p)

    for dup_id, canonical_id in player_merges.items():
        can = index.get(canonical_id)
        if can is None:
            report.missing_canonical.append(f"{dup_id} -> {canonical_id}")
            continue
        dup = index.get(dup_id)
        if dup is None:
            report.missing_dup.append(dup_id)
            continue
        _, can_player = can
        dup_league, dup_player = dup

        merged_from = can_player.setdefault("merged_from", [])
        for mid in [dup_id, *dup_player.get("merged_from", [])]:
            if mid not in merged_from and mid != canonical_id:
                merged_from.append(mid)

        # 代表情報のマージ（canonical が null/空のときのみ。既存値は上書きしない）
        if not can_player.get("caps") and dup_player.get("caps"):
            can_player["caps"] = dup_player["caps"]
        if not can_player.get("nationality") and dup_player.get("nationality"):
            can_player["nationality"] = dup_player["nationality"]

        players_by_league[dup_league] = [
            p for p in players_by_league[dup_league] if p["id"] != dup_id
        ]
        del index[dup_id]
        report.applied.append(f"{dup_id} -> {canonical_id}")
        report.changed_leagues.add(dup_league)
        report.changed_leagues.add(can[0])
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pipeline.merge_persons")
    ap.add_argument("--apply", action="store_true",
                    help="player_merges.json を master に適用して書き戻す")
    ap.add_argument("--scrape-national", action="store_true",
                    help="master に national.json が無いとき scrape 結果で突合")
    args = ap.parse_args(argv)

    merges: dict[str, str] = io.read_manual("player_merges.json", default={})
    by_league = load_players_by_league(scrape_national=args.scrape_national)
    if not by_league:
        print("master/players に選手データが無い。exit 1", file=sys.stderr)
        return 1

    # 1) 候補列挙（自動確定しない）→ merge_candidates.json
    candidates = find_candidates(by_league, merges)
    io.write_json(io.META_DIR / "merge_candidates.json", candidates)
    nat_candidates = [c for c in candidates
                      if any(m["league"] == "national" for m in c["members"])]
    print(f"同一人物候補 {len(candidates)} 組（うち代表を含む {len(nat_candidates)} 組）"
          f" → _meta/merge_candidates.json")
    for c in nat_candidates:
        ids = [m["id"] for m in c["members"]]
        print(f"  代表候補: {c['name_en_normalized']} {c['birthdate']} {ids}")

    if not args.apply:
        print("（--apply 指定なし: master は変更しない。確定は player_merges.json へ）")
        return 0

    if not merges:
        print("player_merges.json が空。適用する統合なし。", file=sys.stderr)
        return 0

    report = apply_merges(by_league, merges)
    for line in report.applied:
        print(f"[merge] {line}")
    for mid in report.missing_canonical:
        print(f"[warn] canonical が master に無い: {mid}", file=sys.stderr)
    for mid in report.missing_dup:
        print(f"[warn] 重複側が既に存在しない（適用済みか）: {mid}", file=sys.stderr)

    # 適用後に候補が0であることを確認（03: cross_person 連動）
    residual = find_candidates(by_league, merges)
    residual_nat = [c for c in residual
                    if any(m["league"] == "national" for m in c["members"])]
    if residual_nat:
        print(f"[error] 適用後も代表の重複候補が {len(residual_nat)} 組残存", file=sys.stderr)
        return 1

    # master に書き戻す（既存 master ファイルがあるリーグのみ。未コミットの national は作らない）
    existing = {p.stem for p in (io.MASTER_DIR / "players").glob("*.json")}
    for league in sorted(report.changed_leagues):
        if league not in existing:
            print(f"[skip-write] {league}: master 未コミットのため書き戻さない", file=sys.stderr)
            continue
        io.write_records(io.players_path(league), by_league[league])
        print(f"[write] players/{league}.json")
    io.write_json(io.META_DIR / "merge_candidates.json", residual)
    print("merges 適用完了。適用後の代表重複候補: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
