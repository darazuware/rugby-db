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


def _height_cm(raw: Optional[str]) -> Optional[str]:
    """all.rugby の '1.82 m' → '182'（cm 文字列）。'-'/欠落は None。"""
    if not raw:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)\s*m", raw)
    if not m:
        return None
    return str(round(float(m.group(1)) * 100))


def _weight_kg(raw: Optional[str]) -> Optional[str]:
    """all.rugby の '122 kg' → '122'。'-'/欠落は None。"""
    if not raw:
        return None
    m = re.search(r"(\d+)\s*kg", raw)
    return m.group(1) if m else None


def player_allrugby(raw: dict, *, league: str, team_id: str) -> tuple[Optional[dict], list[str]]:
    """all.rugby の squad 行（＋任意で個別ページ enrich）→ Player dict。"""
    slug = raw.get("slug")
    if not slug:
        return None, ["all.rugby player: slug 欠落のためスキップ"]
    name_en = raw.get("name_en")
    if not name_en:
        return None, [f"ar_{slug}: name_en 欠落のためスキップ"]

    career = [
        {"team": c["team"], "from": c.get("from"), "to": c.get("to")}
        for c in raw.get("career", []) if c.get("team")
    ]
    data = {
        "id": f"ar_{slug}",
        "source": "all.rugby",
        "source_url": f"https://all.rugby/player/{slug}",
        "scraped_at": _now(),
        "name_en": name_en,
        "slug": slug,
        "position": raw.get("position") or None,
        "team_id": team_id,
        "league": league,
        "height_cm": _height_cm(raw.get("height_raw")),
        "weight_kg": _weight_kg(raw.get("weight_raw")),
        "nationality": raw.get("nationality", []),
        "career": career,
    }
    try:
        model, w = Player.parse(data)
    except ValidationError as exc:
        return None, [f"ar_{slug}: Player 検証失敗 {exc.error_count()} 件のためスキップ"]
    return model.model_dump(by_alias=True), w


def team_allrugby(raw: dict, *, league: str) -> tuple[Optional[dict], list[str]]:
    """all.rugby のクラブ → Team dict。id はクラブ slug（migrate_legacy と一致）。"""
    slug = raw.get("slug")
    if not slug:
        return None, ["all.rugby team: slug 欠落のためスキップ"]
    data = {
        "id": slug,
        "league": league,
        "name_ja": raw.get("name_ja"),
        "name_en": raw.get("name_en") or (None if raw.get("name_ja") else slug),
        "source_url": f"https://all.rugby/club/{slug}/squad",
        "scraped_at": _now(),
        "roster_mode": "full",
        "roster_ids": raw.get("roster_ids", []),
    }
    try:
        model = Team.model_validate(data)
    except ValidationError as exc:
        return None, [f"{slug}: Team 検証失敗 {exc.error_count()} 件のためスキップ"]
    return model.model_dump(by_alias=True), []


def standing_allrugby(rows_raw: list[dict], *, league: str, season: str,
                      source_url: str) -> tuple[Optional[dict], list[str]]:
    """all.rugby 順位表の行リスト → Standing dict。team_id はクラブ slug。

    列順（all.rugby）: PTS, PL, W, D, L。played≠W+D+L や数値欠落の行は落とす。
    """
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
            "rank": vals["rank"], "team_id": tid, "played": vals["played"],
            "won": vals["won"], "drawn": vals["drawn"], "lost": vals["lost"],
            "points": vals["points"],
        })
    if not rows:
        return None, warnings
    data = {
        "league": league, "season": season or "unknown", "scraped_at": _now(),
        "source_url": source_url, "rows": rows,
    }
    try:
        model = Standing.model_validate(data)
    except ValidationError as exc:
        return None, warnings + [f"{league} standings: 検証失敗 {exc.error_count()} 件"]
    return model.model_dump(by_alias=True), warnings


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
