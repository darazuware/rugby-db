"""data/master（SSOT）の実データ検証: スキーマ（pydantic）・整合性チェック（03）・参照整合性。

data/master は読み取りのみ（書き換え禁止）。期待値は master 自身と pipeline のスキーマ/
チェックから導く（AI知識由来の値は書かない: 03）。
"""
from __future__ import annotations

import json
from collections import Counter
from functools import lru_cache
from pathlib import Path

import pytest

from pipeline import io, schemas
from pipeline.validate import checks

MASTER = io.MASTER_DIR


def _load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _files(sub: str) -> list[Path]:
    return sorted((MASTER / sub).glob("*.json"))


@lru_cache(maxsize=None)
def players_by_league() -> dict[str, list[dict]]:
    return {p.stem: _load(p) for p in _files("players")}


@lru_cache(maxsize=None)
def all_players() -> list[dict]:
    return [p for ps in players_by_league().values() for p in ps]


@lru_cache(maxsize=None)
def all_teams() -> list[dict]:
    return [t for f in _files("teams") for t in _load(f)]


@lru_cache(maxsize=None)
def all_matches() -> list[dict]:
    return [m for f in _files("matches") for m in _load(f)]


@lru_cache(maxsize=None)
def all_standings() -> list[dict]:
    return [_load(f) for f in _files("standings")]


def _ids(name: str) -> list[str]:
    return [p.name for p in _files(name)]


# ---------------------------------------------------------------------------
# 構成
# ---------------------------------------------------------------------------
def test_master_dirs_exist_and_not_empty():
    for sub in ("players", "teams", "standings", "schools"):
        assert _files(sub), f"data/master/{sub}/ に JSON が無い"


@pytest.mark.parametrize("sub", ["players", "teams"])
def test_file_names_are_known_league_keys(sub):
    unknown = [f.stem for f in _files(sub) if f.stem not in schemas.LEAGUE_KEYS]
    assert unknown == []


# ---------------------------------------------------------------------------
# スキーマ（03 第1層）
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("fname", _ids("players"))
def test_players_schema(fname):
    league = fname[:-5]
    errors = []
    for raw in players_by_league()[league]:
        try:
            player, _warn = schemas.Player.parse(raw)
        except Exception as e:  # pydantic.ValidationError 他
            errors.append(f"{raw.get('id')}: {str(e).splitlines()[:3]}")
            continue
        if player.league != league:
            errors.append(f"{player.id}: league={player.league} がファイル {fname} と不一致")
        if not raw.get("slug"):
            errors.append(f"{player.id}: slug が空")
    assert errors == [], "\n".join(errors[:30])


@pytest.mark.parametrize("fname", _ids("teams"))
def test_teams_schema(fname):
    errors = []
    for raw in _load(MASTER / "teams" / fname):
        try:
            team = schemas.Team.model_validate(raw)
        except Exception as e:
            errors.append(f"{raw.get('id')}: {str(e).splitlines()[:3]}")
            continue
        if team.league != fname[:-5]:
            errors.append(f"{team.id}: league={team.league} がファイル {fname} と不一致")
    assert errors == [], "\n".join(errors[:30])


@pytest.mark.parametrize("fname", _ids("matches"))
def test_matches_schema(fname):
    errors = []
    for raw in _load(MASTER / "matches" / fname):
        try:
            m = schemas.Match.model_validate(raw)
        except Exception as e:
            errors.append(f"{raw.get('id')}: {str(e).splitlines()[:3]}")
            continue
        if not fname.startswith(f"{m.league}_{m.season}"):
            errors.append(f"{m.id}: {m.league}_{m.season} がファイル {fname} と不一致")
    assert errors == [], "\n".join(errors[:30])


@pytest.mark.parametrize("fname", _ids("standings"))
def test_standings_schema(fname):
    raw = _load(MASTER / "standings" / fname)
    st = schemas.Standing.model_validate(raw)
    assert fname == f"{st.league}_{st.season}.json"
    ranks = [r.rank for r in st.rows]
    team_ids = [r.team_id for r in st.rows]
    assert len(set(team_ids)) == len(team_ids), f"{fname}: team_id 重複"
    assert len(set(ranks)) == len(ranks), f"{fname}: rank 重複"


def test_schools_schema():
    schools = _load(io.schools_path())
    errors = []
    for raw in schools:
        try:
            schemas.School.model_validate(raw)
        except Exception as e:
            errors.append(f"{raw.get('id')}: {str(e).splitlines()[:3]}")
    assert errors == [], "\n".join(errors[:30])
    ids = Counter(s["id"] for s in schools)
    assert [k for k, n in ids.items() if n > 1] == []


def test_callups_structure():
    for f in _files("callups"):
        callups = _load(f)
        ids = Counter(c["id"] for c in callups)
        assert [k for k, n in ids.items() if n > 1] == [], f"{f.name}: id 重複"
        for c in callups:
            assert schemas._check_domain(c["source_url"]), f"{c['id']}: 許可外ドメイン {c['source_url']}"
            assert c.get("scraped_at"), f"{c['id']}: scraped_at 欠落"
            assert isinstance(c.get("members"), list)


# ---------------------------------------------------------------------------
# 整合性チェック（03 第2層: checks.run_all を実データに適用）
# ---------------------------------------------------------------------------
def test_checks_run_all_has_no_errors():
    merges = io.read_manual("player_merges.json", default={}) or {}
    corrections = io.read_manual("caps_corrections.json", default={}) or {}
    result = checks.run_all(
        players_by_league(), all_teams(), all_matches(), all_standings(),
        prev_players_by_league=None, player_merges=merges, caps_corrections=corrections,
    )
    assert result.errors == [], "\n".join(result.errors[:30])


# ---------------------------------------------------------------------------
# 参照整合性
# ---------------------------------------------------------------------------
def test_team_ids_unique_across_leagues():
    c = Counter(t["id"] for t in all_teams())
    assert [k for k, n in c.items() if n > 1] == []


def test_club_matches_reference_existing_teams():
    # 代表戦（national 等の NO_TEAM_LEAGUES）は teams/ に代表チームを持たないため対象外
    tids = {t["id"] for t in all_teams()}
    bad = [
        (m["id"], side)
        for m in all_matches() if m["league"] in schemas.TEAM_LEAGUES
        for side in (m["home_team_id"], m["away_team_id"]) if side not in tids
    ]
    assert bad == []


def test_match_ids_unique():
    c = Counter(m["id"] for m in all_matches())
    assert [k for k, n in c.items() if n > 1] == []


def test_standings_reference_existing_teams_of_same_league():
    team_league = {t["id"]: t["league"] for t in all_teams()}
    bad = [
        (st["league"], r["team_id"])
        for st in all_standings() for r in st["rows"]
        if team_league.get(r["team_id"]) != st["league"]
    ]
    assert bad == []


def test_education_school_ids_exist():
    school_ids = {s["id"] for s in _load(io.schools_path())}
    bad = [
        (p["id"], e["school_id"])
        for p in all_players() for e in (p.get("education") or [])
        if e.get("school_id") and e["school_id"] not in school_ids
    ]
    assert bad == []


def test_player_merges_reference_existing_players():
    merges = io.read_manual("player_merges.json", default={}) or {}
    ids = {p["id"] for p in all_players()}
    bad = [(src, dst) for src, dst in merges.items() if dst not in ids]
    assert bad == []
    assert [src for src, dst in merges.items() if src == dst] == []


def test_player_pages_reference_existing_players():
    """個別ページ対象（data/manual/player_pages.json）の id/slug が master に存在する。"""
    rows = (io.read_manual("player_pages.json", default={}) or {}).get("players", [])
    by_id = {}
    for p in all_players():
        by_id.setdefault(p["id"], set()).add(p["slug"])
    bad = [r for r in rows if r["id"] not in by_id or r["slug"] not in by_id[r["id"]]]
    assert bad == [], bad[:10]


def test_episodes_file_name_matches_player_id():
    for f in sorted((MASTER / "players" / "episodes").glob("*.json")):
        d = _load(f)
        assert d["player_id"] == f.stem
        for fact in d.get("facts", []):
            assert fact.get("source_url"), f"{f.name}: source_url の無い fact"


def test_redirects_have_no_chains_or_self_loops():
    redirects = _load(io.META_DIR / "redirects.json")
    assert [k for k, v in redirects.items() if k == v] == []
    assert [k for k, v in redirects.items() if v in redirects] == []


# --- 既知のデータ不整合（2026-10-05 時点）。xfail(strict=False): 解消されれば XPASS で通知 ---
@pytest.mark.xfail(strict=False, reason="既知: callups の一部 member.player_id が players/ に未収録（jrfu_national_*）")
def test_callup_members_reference_existing_players():
    ids = {p["id"] for p in all_players()}
    bad = [
        (c["id"], m["player_id"])
        for f in _files("callups") for c in _load(f) for m in c["members"]
        if m.get("player_id") and m["player_id"] not in ids
    ]
    assert bad == []


@pytest.mark.xfail(strict=False, reason="既知: episodes/jrfu_callup_ruan-botha.json の player_id が players/ に未収録")
def test_episodes_reference_existing_players():
    ids = {p["id"] for p in all_players()}
    bad = [f.stem for f in (MASTER / "players" / "episodes").glob("*.json") if f.stem not in ids]
    assert bad == []


@pytest.mark.xfail(strict=False, reason="既知: redirects.json の行き先16件が master の選手 slug に存在しない")
def test_redirect_targets_exist():
    slugs = {p["slug"] for p in all_players()}
    redirects = _load(io.META_DIR / "redirects.json")
    bad = [v for v in redirects.values() if v.startswith("/players/") and v.split("/")[2] not in slugs]
    assert bad == []
