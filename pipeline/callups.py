"""gap B: 代表招集・合宿メンバー発表イベントの突合・差分・マスタ化（純関数）。

pipeline.scrape.jrfu.collect_call_ups() が返すイベント（news記事1本＝1イベント）を、
1) メンバーに master players 上の player_id を突合し（選手ページへのリンク用）、
2) master `data/master/callups/{league}.json` に news_id 単位で永続化し、
3) 前回までに記録の無い新規イベントを検知して、前回イベントからの「新たに選出された選手」
   を計算し、news_gen が記事化できる diff セクションを組み立てる、ための純関数群。

「新たに選出」は前回イベントのメンバー集合との機械的な差分であり、AIの推測ではない
（03_VALIDATION 原則2: 事実の創作禁止）。「復帰」等の含意は付けず「前回招集外→今回選出」
という検証可能な事実のみを news_gen 側でテンプレ化する。
"""
from __future__ import annotations

from typing import Optional

from pipeline.schemas import japan_name_keys


def _member_keys(member: dict) -> list[str]:
    """メンバー行の氏名突合キー（愛称/正式名・アポストロフィの表記ゆれを吸収）。"""
    name_en = member.get("name_en")
    return japan_name_keys(name_en) if name_en else []


def _player_index(national_players: list[dict]) -> dict[str, str]:
    """氏名突合キー → player_id。all.rugby "Mike STOLBERG" と JRFU "Michael STOLBERG"
    のような愛称ゆれも別名展開して両表記で引けるようにする。同キー重複時は先勝ち。"""
    index: dict[str, str] = {}
    for p in national_players:
        name_en = p.get("name_en")
        if not name_en:
            continue
        for key in japan_name_keys(name_en):
            index.setdefault(key, p["id"])
    return index


def assign_member_ids(events: list[dict], national_players: list[dict]) -> list[dict]:
    """各イベントメンバーに master national の player_id を突合してセットした新イベント列を返す。"""
    index = _player_index(national_players)
    out: list[dict] = []
    for ev in events:
        members = []
        for m in ev.get("members", []):
            pid = next((index[k] for k in _member_keys(m) if k in index), None)
            members.append({**m, "player_id": pid})
        out.append({**ev, "members": members})
    return out


def event_id(league: str, news_id: Optional[str]) -> Optional[str]:
    return f"callup_{league}_{news_id}" if news_id else None


def build_event_records(events: list[dict], *, league: str, scraped_at: str) -> list[dict]:
    """イベント列 → master callups レコード列（news_id昇順）。"""
    records: list[dict] = []
    for ev in events:
        eid = event_id(league, ev.get("news_id"))
        if eid is None:
            continue
        records.append({
            "id": eid,
            "league": league,
            "source": "rugby-japan.jp",
            "source_url": ev.get("source_url"),
            "scraped_at": scraped_at,
            "news_id": ev.get("news_id"),
            "kind": ev.get("kind"),
            "title": ev.get("title"),
            "venue": ev.get("venue"),
            "start_date": ev.get("start_date"),
            "members": [
                {
                    "player_id": m.get("player_id"),
                    "name_ja": m.get("name_ja"),
                    "name_en": m.get("name_en"),
                    "position_group": m.get("position_group"),
                    "club_raw": m.get("club_raw"),
                    "caps": m.get("caps"),
                }
                for m in ev.get("members", [])
            ],
        })
    records.sort(key=lambda r: int(r["news_id"]) if (r.get("news_id") or "").isdigit() else 0)
    return records


def merge_event_master(prev_records: list[dict], new_records: list[dict]) -> list[dict]:
    """既存master に新イベントを id 単位でマージ（同idは新しい内容で上書き）。news_id昇順。"""
    by_id: dict[str, dict] = {r["id"]: r for r in prev_records}
    for r in new_records:
        by_id[r["id"]] = r
    return sorted(by_id.values(),
                  key=lambda r: int(r["news_id"]) if (r.get("news_id") or "").isdigit() else 0)


def _member_summary(m: dict) -> dict:
    return {"id": m.get("player_id"), "name_ja": m.get("name_ja"), "name_en": m.get("name_en"),
            "position_group": m.get("position_group"), "club_raw": m.get("club_raw"),
            "caps": m.get("caps")}


def diff_new_events(events: list[dict], prev_records: list[dict], *, league: str) -> list[dict]:
    """master に無い新規イベントのみ、前回イベントからの新規選出を添えて diff 化する。

    events は assign_member_ids 済み（player_id 付き）を想定。前回イベントは、同一masterの
    中で news_id がその新規イベントより小さい最大のもの（＝直近の1つ前の招集）を用いる。
    """
    prev_ids = {r.get("id") for r in prev_records}
    # 突合対象の「過去イベント」は master 既存 + 今回スクレイプで既知の全イベント。
    known_by_nid: dict[int, dict] = {}
    for r in prev_records:
        nid = r.get("news_id")
        if (nid or "").isdigit():
            known_by_nid[int(nid)] = r
    for ev in events:
        nid = ev.get("news_id")
        if (nid or "").isdigit():
            known_by_nid.setdefault(int(nid), ev)

    out: list[dict] = []
    for ev in sorted(events, key=lambda e: int(e["news_id"]) if (e.get("news_id") or "").isdigit() else 0):
        eid = event_id(league, ev.get("news_id"))
        if eid is None or eid in prev_ids:
            continue  # 既知イベントは記事化しない（冪等）
        nid = int(ev["news_id"]) if (ev.get("news_id") or "").isdigit() else None
        prev_nids = [n for n in known_by_nid if nid is not None and n < nid]
        prev_ev = known_by_nid[max(prev_nids)] if prev_nids else None

        prev_keys: set[str] = set()
        if prev_ev:
            for pm in prev_ev.get("members", []):
                prev_keys.update(_member_keys(pm))

        members = ev.get("members", [])
        new_members = []
        if prev_ev is not None:
            for m in members:
                if not any(k in prev_keys for k in _member_keys(m)):
                    new_members.append(_member_summary(m))

        out.append({
            "id": eid,
            "news_id": ev.get("news_id"),
            "title": ev.get("title"),
            "kind": ev.get("kind"),
            "venue": ev.get("venue"),
            "start_date": ev.get("start_date"),
            "source_url": ev.get("source_url"),
            "member_count": len(members),
            "members": [_member_summary(m) for m in members],
            "new_members": new_members,
            "has_previous": prev_ev is not None,
        })
    return out
