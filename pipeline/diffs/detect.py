"""P1-8: 移籍・キャップ差分検知（02 run.py 手順4 / 05 差分検知）。

入力は検証済みレコードの plain dict（players_by_league と同じ形）。
本モジュールは純粋関数のみで、ファイルI/Oは行わない（読み書きは io.py / run.py 側）。

検知する差分（05の表に対応）:
  - signings: 新idが出現（真の新規追加）
  - transfers: 既存idの team_id が変化（移籍）
  - departures: idがロスターから消失。**2回連続で消失が確認されたときのみ確定**。
    1回目は pending（呼び出し側が `_meta/pending_departures.json` として永続化）に積み、
    2回目の実行で同じidが再度消失していれば確定イベントにして pending から外す。
    途中で再出現したら pending から除去（誤検知キャンセル）。
  - first_caps: caps.count が 0/null → 1以上
  - caps_updates: caps.count が増加（初キャップ以外の増分。週次まとめは news_gen 側の仕事）
  - newly_finished_rounds: matches の status が finished に変わった試合を節単位でまとめる

pending_departures の型: `{league: {player_id: {id, name_en, name_ja, team_id}}}`。
呼び出し側は run 前に読み込み、run_all() の戻り値をそのまま書き戻す。
"""
from __future__ import annotations

from typing import Any, Optional


def _summary(p: dict) -> dict:
    return {"id": p["id"], "name_en": p.get("name_en"), "name_ja": p.get("name_ja")}


def diff_players(new_players: list[dict], prev_players: list[dict],
                 pending: Optional[dict[str, dict]] = None) -> tuple[dict, dict[str, dict]]:
    """1リーグ分の選手差分。戻り値は (差分dict, 更新後pending)。"""
    pending = dict(pending or {})
    prev_by_id = {p["id"]: p for p in prev_players}
    new_by_id = {p["id"]: p for p in new_players}
    prev_ids, new_ids = set(prev_by_id), set(new_by_id)

    signings = [
        {**_summary(new_by_id[pid]), "team_id": new_by_id[pid].get("team_id")}
        for pid in sorted(new_ids - prev_ids)
    ]

    transfers: list[dict] = []
    first_caps: list[dict] = []
    caps_updates: list[dict] = []
    for pid in sorted(new_ids & prev_ids):
        prev_p, new_p = prev_by_id[pid], new_by_id[pid]
        prev_team, new_team = prev_p.get("team_id"), new_p.get("team_id")
        if new_team is not None and prev_team != new_team:
            transfers.append({**_summary(new_p), "from_team_id": prev_team, "to_team_id": new_team})

        prev_caps: dict[str, Any] = prev_p.get("caps") or {}
        new_caps: dict[str, Any] = new_p.get("caps") or {}
        prev_count = prev_caps.get("count") or 0
        new_count = new_caps.get("count")
        if new_count is None:
            continue
        if prev_count == 0 and new_count >= 1:
            first_caps.append({**_summary(new_p), "team": new_caps.get("team"), "count": new_count})
        elif new_count > prev_count:
            caps_updates.append({**_summary(new_p), "team": new_caps.get("team"),
                                  "from_count": prev_count, "to_count": new_count})

    # 再出現した id は pending から外す（誤検知キャンセル）
    for pid in new_ids:
        pending.pop(pid, None)

    departures: list[dict] = []
    for pid in sorted(prev_ids - new_ids):
        prev_p = prev_by_id[pid]
        entry = {**_summary(prev_p), "team_id": prev_p.get("team_id")}
        if pid in pending:
            departures.append(entry)
            pending.pop(pid, None)
        else:
            pending[pid] = entry

    section = {
        "signings": signings,
        "transfers": transfers,
        "departures": departures,
        "first_caps": first_caps,
        "caps_updates": caps_updates,
        "pending_departures": [pending[pid] for pid in sorted(pending)],
    }
    return section, pending


def diff_matches(new_matches: list[dict], prev_matches: list[dict]) -> list[dict]:
    """status が finished に変わった試合を (season, round) でまとめる。"""
    prev_status = {m["id"]: m.get("status") for m in prev_matches}
    rounds: dict[tuple[Optional[str], Optional[int]], list[str]] = {}
    for m in new_matches:
        if m.get("status") != "finished":
            continue
        if prev_status.get(m["id"]) == "finished":
            continue
        key = (m.get("season"), m.get("round"))
        rounds.setdefault(key, []).append(m["id"])
    return [
        {"season": season, "round": rnd, "match_ids": sorted(ids)}
        for (season, rnd), ids in sorted(
            rounds.items(), key=lambda kv: (kv[0][0] or "", kv[0][1] or 0))
    ]


def build_league_diff(league: str, new_players: list[dict], prev_players: list[dict],
                      pending: Optional[dict[str, dict]] = None,
                      new_matches: Optional[list[dict]] = None,
                      prev_matches: Optional[list[dict]] = None) -> tuple[dict, dict[str, dict]]:
    """1リーグ分の選手差分＋試合差分をまとめる。"""
    new_matches = new_matches or []
    prev_matches = prev_matches or []
    section, updated_pending = diff_players(new_players, prev_players, pending)
    rounds = diff_matches(
        [m for m in new_matches if m.get("league") == league],
        [m for m in prev_matches if m.get("league") == league],
    )
    diff = {"league": league, **section, "newly_finished_rounds": rounds}
    return diff, updated_pending


def run_all(players_by_league: dict[str, list[dict]],
           prev_players_by_league: dict[str, list[dict]],
           pending_departures: Optional[dict[str, dict]] = None,
           matches: Optional[list[dict]] = None,
           prev_matches: Optional[list[dict]] = None) -> tuple[dict[str, dict], dict[str, dict]]:
    """全リーグ分をまとめて計算する（run.py から1回呼ぶ想定）。

    戻り値: (league -> diff dict, league -> 更新後 pending)。
    後者はそのまま `_meta/pending_departures.json` として永続化する。
    """
    matches = matches or []
    prev_matches = prev_matches or []
    pending_departures = pending_departures or {}
    diffs_by_league: dict[str, dict] = {}
    updated_pending: dict[str, dict[str, dict]] = {}
    for league, new_players in players_by_league.items():
        prev_players = prev_players_by_league.get(league, [])
        league_pending = pending_departures.get(league, {})
        diff, new_league_pending = build_league_diff(
            league, new_players, prev_players, league_pending,
            new_matches=matches, prev_matches=prev_matches,
        )
        diffs_by_league[league] = diff
        updated_pending[league] = new_league_pending
    return diffs_by_league, updated_pending
