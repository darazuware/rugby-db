"""ソース生 dict → 01 スキーマ dict への変換（transform 層）。

各関数は (schema_dict | None, warnings) を返す。検証を通らないレコードは None を返し
warning を積む（02: 例外で全体を止めない）。返す dict は master にそのまま書ける形。
"""
from __future__ import annotations

import re
from datetime import datetime, timezone, timedelta
from typing import Optional

from pydantic import ValidationError

from pipeline.schemas import Player, Team, Standing

JST = timezone(timedelta(hours=9))


def _now() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s


def player(raw: dict, *, league: str, team_id: Optional[str]) -> tuple[Optional[dict], list[str]]:
    """league-one.jp の生選手 dict → Player dict。"""
    warnings: list[str] = []
    pid = raw.get("player_id")
    if not pid:
        return None, ["player: player_id 欠落のためスキップ"]

    name_en = raw.get("name_en")
    name_ja = raw.get("name_ja")
    if name_en:
        slug = f"{_slugify(name_en)}-{pid}"
    elif name_ja:
        slug = f"lo-{pid}"
    else:
        return None, [f"lo_{pid}: name_en/name_ja が両方欠落のためスキップ"]

    data = {
        "id": f"lo_{pid}",
        "source": "league-one.jp",
        "source_url": f"https://league-one.jp/player/{pid}",
        "scraped_at": _now(),
        "name_en": name_en,
        "name_ja": name_ja,
        "slug": slug,
        "position": raw.get("position"),
        "team_id": team_id,
        "league": league,
        "height_cm": raw.get("height_cm"),
        "weight_kg": raw.get("weight_kg"),
        "birthdate": raw.get("birthdate"),
        "league_caps": raw.get("league_caps"),
        "image_url": raw.get("image_url"),
    }
    try:
        model, w = Player.parse(data)
    except ValidationError as exc:
        return None, [f"lo_{pid}: Player 検証失敗 {exc.error_count()} 件のためスキップ"]
    warnings.extend(w)
    return model.model_dump(by_alias=True), warnings


def team(raw: dict, *, league: str) -> tuple[Optional[dict], list[str]]:
    tid = raw.get("team_id")
    if not tid:
        return None, ["team: team_id 欠落のためスキップ"]
    data = {
        "id": f"lo_team_{tid}",
        "league": league,
        "name_ja": raw.get("name_ja"),
        "source_url": f"https://league-one.jp/team/{tid}",
        "scraped_at": _now(),
        "roster_mode": "full",
        "roster_ids": raw.get("roster_ids", []),
    }
    try:
        model = Team.model_validate(data)
    except ValidationError as exc:
        return None, [f"lo_team_{tid}: Team 検証失敗 {exc.error_count()} 件のためスキップ"]
    return model.model_dump(by_alias=True), []


def _to_int(v) -> Optional[int]:
    if v is None:
        return None
    s = str(v).strip()
    return int(s) if re.fullmatch(r"-?\d+", s) else None


def standing(rows_raw: list[dict], *, league: str, season: str) -> tuple[Optional[dict], list[str]]:
    """順位表の行リスト → Standing dict。played≠W+D+L の行は落として warning。"""
    warnings: list[str] = []
    rows = []
    for r in rows_raw:
        tid = r.get("team_id")
        vals = {k: _to_int(r.get(k)) for k in ("rank", "played", "won", "drawn", "lost", "points")}
        if tid is None or any(vals[k] is None for k in ("rank", "played", "won", "drawn", "lost", "points")):
            warnings.append(f"{league} standings: team={tid} の数値欠落のため行を除外")
            continue
        if vals["played"] != vals["won"] + vals["drawn"] + vals["lost"]:
            warnings.append(f"{league} standings: team={tid} の played≠W+D+L のため行を除外")
            continue
        rows.append({
            "rank": vals["rank"],
            "team_id": f"lo_team_{tid}",
            "played": vals["played"],
            "won": vals["won"],
            "drawn": vals["drawn"],
            "lost": vals["lost"],
            "points": vals["points"],
        })
    if not rows:
        return None, warnings
    data = {
        "league": league,
        "season": season or "unknown",
        "scraped_at": _now(),
        "source_url": "https://league-one.jp/standings/",
        "rows": rows,
    }
    try:
        model = Standing.model_validate(data)
    except ValidationError as exc:
        return None, warnings + [f"{league} standings: 検証失敗 {exc.error_count()} 件"]
    return model.model_dump(by_alias=True), warnings
