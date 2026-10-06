"""TOP14 公式（top14.lnr.fr = LNR）順位表スクレイパー。一次情報。

列順: Pts, M, G, N, P, Bonus, Pts M., Pts E., Diff。
"""
from __future__ import annotations

import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

URL = "https://top14.lnr.fr/classement"
SLUG_MAP = {"bordeaux-begles": "bordeaux"}  # LNR URL slug → master team id


def _txt(node) -> str:
    # <template> 内は TemplateString で get_text に含まれないため string=True で全文字列を拾う
    return " ".join(t.strip() for t in node.find_all(string=True) if t.strip())


def parse_ranking(html: str) -> tuple[Optional[str], list[dict]]:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text() if soup.title else ""
    m = re.search(r"(\d{4})-(\d{4})", title)
    season = f"{m.group(1)}-{m.group(2)[2:]}" if m else None
    root = soup.select_one(".ranking--full")
    if root is None:
        return season, []
    ranks = [int(m.group(1)) for x in root.select(".table-line--ranking-fixed")
             if (m := re.search(r"cell-wrapper--rank-(\d+)", " ".join(
                 c for w in x.select(".table-line__cell-wrapper") for c in w.get("class", []))))]
    rows = []
    lines = [(ln, ln.select_one("a[href*='/club/']")) for ln in root.select(".table-line--ranking-scrollable")]
    lines = [(ln, a) for ln, a in lines if a is not None]
    for i, (line, a) in enumerate(lines):
        if i >= len(ranks):
            break
        cells = [_txt(c) for c in line.select(".table-line__cell-wrapper")][1:10]
        if len(cells) < 9:
            continue
        slug = a["href"].rstrip("/").rsplit("/", 1)[-1]
        rows.append({
            "rank": ranks[i], "team_id": SLUG_MAP.get(slug, slug),
            "points": cells[0], "played": cells[1], "won": cells[2], "drawn": cells[3],
            "lost": cells[4], "bonus": cells[5], "pf": cells[6], "pa": cells[7], "diff": cells[8],
        })
    return season, rows


def fetch() -> tuple[Optional[str], list[dict]]:
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    r.raise_for_status()
    return parse_ranking(r.text)
