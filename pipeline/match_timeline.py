"""日本代表戦の「得点経過・交代」を、日本(左)/相手(右)の2列タイムラインHTMLにする。

情報源は協会 game.php の info.timelines（得点・交代・カード）のみ。創作しない。
Markdown に埋め込む HTML なので、ブロック内に空行・4スペース以上のインデントを入れない。
新しい順（後半→前半）。T と直後の TG は1枚のカードにまとめる。
"""
from __future__ import annotations

from html import escape
from typing import Optional


def _name(p: Optional[dict]) -> str:
    if not p:
        return ""
    return f"{p.get('last_name', '')}{p.get('first_name', '')}".strip()


def _card_label(ev: dict, remark: str) -> tuple[str, str]:
    """(クラス, 表示)。協会の備考にRC/YCがあればそれに従う。"""
    if "RC" in remark or "レッド" in remark:
        return "sc-rc", "レッドカード"
    if "YC" in remark:
        return "sc-yc", "イエローカード"
    return "sc-yc", "カード"


def _merge_points(events: list[dict]) -> list[dict]:
    """同チーム・同ハーフで T の直後に G が続くものを1件(T+G)にする。"""
    out: list[dict] = []
    for ev in events:
        if (ev["type"] == "point" and ev.get("point_kind") == "G" and out
                and out[-1]["type"] == "point" and out[-1].get("point_kind") == "T"
                and out[-1]["team_id"] == ev["team_id"] and out[-1]["half_kind"] == ev["half_kind"]):
            out[-1] = {**out[-1], "point_kind": "TG", "points": out[-1]["points"] + ev["points"],
                       "goal_player": ev.get("player"), "home_points": ev["home_points"],
                       "away_points": ev["away_points"], "goal_min": ev["time_min"]}
            continue
        out.append(ev)
    return out


def _card_html(ev: dict, remark: str) -> str:
    kind = ev["point_kind"]
    who = escape(_name(ev.get("player")))
    if kind == "TG":
        g = escape(_name(ev.get("goal_player")))
        return (f'<div class="mt-ev mt-score"><div class="mt-pts"><span class="sc sc-t">T</span>'
                f'<span class="sc sc-tg">TG</span><b>+{ev["points"]}</b></div>'
                f'<div class="mt-who">{who}<small>トライ</small></div>'
                f'<div class="mt-who">{g}<small>ゴール</small></div></div>')
    cls = {"T": "sc-t", "PG": "sc-pg", "DG": "sc-dg", "G": "sc-tg"}.get(kind, "sc-t")
    label = {"T": "T", "PG": "PG", "DG": "DG", "G": "TG"}.get(kind, kind)
    jp = {"T": "トライ", "PG": "", "DG": "", "G": "ゴール"}.get(kind, "")
    small = f'<small>{jp}</small>' if jp else ''
    return (f'<div class="mt-ev mt-score"><div class="mt-pts"><span class="sc {cls}">{label}</span>'
            f'<b>+{ev["points"]}</b></div><div class="mt-who">{who}{small}</div></div>')


def _sub_html(ev: dict) -> str:
    return (f'<div class="mt-ev mt-sub"><div><span class="mt-in">IN</span>{escape(_name(ev.get("in_player")))}</div>'
            f'<div><span class="mt-out">OUT</span>{escape(_name(ev.get("out_player")))}</div></div>')


def _event_html(ev: dict, remark: str) -> str:
    if ev["type"] == "point":
        return _card_html(ev, remark)
    if ev["type"] == "change":
        return _sub_html(ev)
    if ev["type"] == "card":
        cls, label = _card_label(ev, remark)
        who = escape(_name(ev.get("player")))
        why = escape(ev.get("content") or "")
        return (f'<div class="mt-ev mt-card"><div><span class="sc {cls}">{label}</span></div>'
                f'<div class="mt-who">{who}<small>{why}</small></div></div>')
    return ""


def build_timeline_html(g: dict, jp_side: str, jp_name: str, opp_name: str) -> str:
    """g: game.php の1試合, jp_side: 'home'|'away'。イベントが無ければ空文字。"""
    info = g.get("info") or {}
    tl = info.get("timelines") or []
    if not tl:
        return ""
    jp_team_id = ((g.get(f"{jp_side}_team2") or {}).get("team_id"))
    remark = g.get("new_remark") or ""
    events = _merge_points([e for e in tl if e.get("type") in ("point", "change", "card")])
    h1 = (g.get(f"{jp_side}_team_first_points"), g.get(f"{'away' if jp_side == 'home' else 'home'}_team_first_points"))
    h2 = (g.get(f"{jp_side}_team_second_points"), g.get(f"{'away' if jp_side == 'home' else 'home'}_team_second_points"))

    def score(ev: dict) -> str:
        hp, ap = ev.get("home_points"), ev.get("away_points")
        if hp is None or ap is None:
            return ""
        j, o = (hp, ap) if jp_side == "home" else (ap, hp)
        return f"{j}-{o}"

    lines = ['<details class="mt">',
             f'<summary class="mt-sum"><span class="mt-arrow">▶</span><span>得点経過・交代を見る</span>'
             f'<small>日本 vs {escape(opp_name)}・タップで開閉</small></summary>',
             '<div class="mt-body">',
             f'<div class="mt-head"><span>🇯🇵 {escape(jp_name)}</span><span>時間</span><span>{escape(opp_name)}</span></div>']
    for half, band_cls, icon, name, pts in ((1, "mt-h2", "🌙", "後半", h2), (0, "mt-h1", "☀️", "前半", h1)):
        evs = [e for e in events if e.get("half_kind") == half]
        if not evs:
            continue
        ps = f"{pts[0]}-{pts[1]}" if None not in pts else ""
        lines.append(f'<div class="mt-band {band_cls}"><span>{icon} {name}</span><span>{name}の得点 {ps}</span></div>')
        # 新しい順。同じ分は1行にまとめ、左=日本・右=相手
        by_min: dict[int, list[dict]] = {}
        for e in sorted(evs, key=lambda x: (x["time_min"], x.get("point_sort", 0)), reverse=True):
            by_min.setdefault(e["time_min"], []).append(e)
        for minute, group in by_min.items():
            left = "".join(_event_html(e, remark) for e in group if e["team_id"] == jp_team_id)
            right = "".join(_event_html(e, remark) for e in group if e["team_id"] != jp_team_id)
            sc = next((score(e) for e in group if score(e)), "")
            lines.append(f'<div class="mt-row"><div class="mt-side mt-l">{left}</div>'
                         f'<div class="mt-min"><b>{minute}\'</b><small>{sc}</small></div>'
                         f'<div class="mt-side mt-r">{right}</div></div>')
    lines += ['</div>', '</details>']
    return "\n".join(lines)
