"""Premiership 公式（premrugby.com）順位表。公式サイトが使う incrowdsports の JSON フィードを取得。

season=202601 は 2026-27 シーズン（公式ページの通信で確認）。
"""
from __future__ import annotations

import requests

COMP_ID = 1011
PAGE_URL = "https://www.premrugby.com/standings?competition=gallagher-prem"
SOURCE_URL = "https://www.premrugby.com/standings"
_NAME_MAP = {
    "Bath Rugby": "bath", "Bristol Bears": "bristol", "Exeter Chiefs": "exeter",
    "Gloucester Rugby": "gloucester", "Harlequins": "harlequins", "Leicester Tigers": "leicester",
    "Newcastle Red Bulls": "newcastle", "Northampton Saints": "northampton",
    "Sale Sharks": "sale", "Saracens": "saracens",
}


def parse_table(data: dict) -> list[dict]:
    teams = data["data"]["groups"][0]["teams"]
    out = []
    for t in teams:
        tid = _NAME_MAP.get(t["name"])
        if tid is None:
            raise ValueError(f"未知のチーム名: {t['name']}")
        out.append({
            "rank": t["position"], "team_id": tid, "played": t["played"], "won": t["won"],
            "drawn": t["drawn"], "lost": t["lost"], "points": t["points"], "bonus": t["bonus"],
            "points_for": t["pointsFor"], "points_against": t["pointsAgainst"], "diff": t["pointsDiff"],
        })
    return out


def fetch(season_code: str = "202601") -> list[dict]:
    r = requests.get(
        f"https://rugby-union-feeds.incrowdsports.com/v1/tables/{COMP_ID}",
        params={"provider": "rugbyviz", "season": season_code},
        headers={"User-Agent": "Mozilla/5.0"}, timeout=30,
    )
    r.raise_for_status()
    return parse_table(r.json())
