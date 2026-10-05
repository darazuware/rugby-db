"""自動生成ニュース（週次加入/キャップ更新・月次まとめ・招集）の掲載前検証。

data/master を読み取り専用で突合し、機械的に裏付けが取れる行だけを掲載する（03_VALIDATION 原則2）。
- キャップ更新: 1週間での増分が MAX_WEEKLY_CAPS_DELTA を超えるものは、試合出場ではなく
  ソース側の数え直し（基準値の変化）とみなし掲載しない。減少・同値も掲載しない。
- 加入: 現 master の所属が記事の加入先と一致し、他リーグの master に重複登録が無く、
  career の最新エントリが今季（SEASON_FROM 年）以降開始かつ直前エントリと別チームで、
  その最新エントリのチーム名が加入先チームと一致するものだけを「加入」として掲載する。
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "master"

MAX_WEEKLY_CAPS_DELTA = 2
SEASON_FROM = 2026
CLUB_LEAGUES = ("top14", "urc", "premiership", "super-rugby", "mlr", "nrl",
                "league-one-d1", "league-one-d2", "league-one-d3")

COUNTRY_JA: dict[str, str] = {
    "South Africa": "南アフリカ", "Ireland": "アイルランド", "New Zealand": "ニュージーランド",
    "France": "フランス", "England": "イングランド", "Scotland": "スコットランド",
    "Argentina": "アルゼンチン", "Italy": "イタリア", "Fiji": "フィジー",
    "Australia": "オーストラリア", "Wales": "ウェールズ", "Georgia": "ジョージア",
    "Samoa": "サモア", "Japan": "日本", "Portugal": "ポルトガル",
    "Tonga": "トンガ", "Uruguay": "ウルグアイ", "Spain": "スペイン",
    "USA": "アメリカ", "Usa": "アメリカ", "Romania": "ルーマニア", "Canada": "カナダ",
    "Chile": "チリ", "Namibia": "ナミビア", "Hong Kong": "香港", "Hong Kong China": "香港",
    "Netherlands": "オランダ", "Belgium": "ベルギー", "Germany": "ドイツ",
    "Zimbabwe": "ジンバブエ", "Kenya": "ケニア",
}

_FOOTNOTE = re.compile(r"\s*※\s*\d+.*$")
_TRAILING_EN = re.compile(r"(?<=[\u3040-\u30ff\u4e00-\u9fff])\s+[A-Z][A-Za-z'\-]+\s+[A-Z][A-Z'\-]+$")


def country_ja(name: str) -> str:
    return COUNTRY_JA.get(name, name)


def strip_footnote(name: Optional[str]) -> Optional[str]:
    """JRFU 発表ページの注記記号（例: 「稲場 巧 ※1.」）を氏名から除く。"""
    if not name:
        return name
    name = _FOOTNOTE.sub("", name).strip()
    # 「佐藤 健次 Kenji SATO」のように日本語名の後ろに英字表記が続く場合は日本語名だけ残す
    return _TRAILING_EN.sub("", name).strip()


def caps_delta_plausible(frm, to) -> bool:
    return isinstance(frm, int) and isinstance(to, int) and 0 < to - frm <= MAX_WEEKLY_CAPS_DELTA


def _read(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


@lru_cache(maxsize=1)
def _club_players() -> dict[str, dict[str, dict]]:
    return {lg: {p["id"]: p for p in _read(MASTER / "players" / f"{lg}.json")} for lg in CLUB_LEAGUES}


@lru_cache(maxsize=1)
def _club_teams() -> dict[str, dict[str, dict]]:
    return {lg: {t["id"]: t for t in _read(MASTER / "teams" / f"{lg}.json")} for lg in CLUB_LEAGUES}


@lru_cache(maxsize=1)
def _leagues_by_id() -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    for lg, ps in _club_players().items():
        for pid in ps:
            out[pid].add(lg)
    return out


_STOP = {"rugby", "club", "rfc", "union", "football", "sport", "stade", "the", "and"}


def _tokens(s: str) -> set[str]:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return {w for w in re.split(r"[^a-z0-9]+", s) if len(w) >= 4 and w not in _STOP}


def _same_team(career_team: str, team: dict) -> bool:
    want = _tokens(team.get("id", "").replace("-", " ")) | _tokens(team.get("name_en") or "")
    return bool(want & _tokens(career_team))


def join_verified(league: str, pid: str, team_id: Optional[str]) -> bool:
    lg_key = league if league in _club_players() else None
    if not lg_key or not team_id:
        return False
    p = _club_players()[lg_key].get(pid)
    team = _club_teams()[lg_key].get(team_id)
    if not p or not team or p.get("team_id") != team_id:
        return False
    if len(_leagues_by_id().get(pid, ())) > 1:
        return False
    car = [c for c in (p.get("career") or []) if isinstance(c.get("from"), int) and c.get("team")]
    if len(car) < 2 or car[-1]["from"] < SEASON_FROM or car[-2]["team"] == car[-1]["team"]:
        return False
    return _same_team(car[-1]["team"], team)


def previous_team(league: str, pid: str) -> Optional[str]:
    """career の直前エントリのチーム名（join_verified を通った選手に対してのみ使う）。"""
    p = _club_players().get(league, {}).get(pid)
    car = [c for c in ((p or {}).get("career") or []) if isinstance(c.get("from"), int) and c.get("team")]
    return car[-2]["team"] if len(car) >= 2 else None


# --- 月次まとめ（rollup）の行検証 ---------------------------------------------
_CAPS_LINE = re.compile(r"(\d+)→(\d+)キャップ")
_JOIN_LINE = re.compile(r"^- (?:\[(?P<n1>[^\]]+)\]\([^)]*\)|(?P<n2>.+?))が(?:\[(?P<t1>[^\]]+)\]\([^)]*\)|(?P<t2>[^（]+?))（")
_KANA = re.compile(r"（[^）]*）$")


@lru_cache(maxsize=1)
def _players_by_name() -> dict[str, list[tuple[str, dict]]]:
    out: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    for lg, ps in _club_players().items():
        for p in ps.values():
            for nm in (p.get("name_ja"), p.get("name_en")):
                if nm:
                    out[nm].append((lg, p))
    return out


def _team_names(lg: str, tid: str) -> set[str]:
    t = _club_teams().get(lg, {}).get(tid) or {}
    return {x for x in (t.get("name_ja"), t.get("name_en"), tid) if x}


def rollup_line_ok(entry: dict) -> bool:
    """rollup_YYYY-MM.json の1エントリを掲載してよいか。"""
    kind, text = entry.get("kind"), entry.get("text", "")
    if kind == "caps":
        m = _CAPS_LINE.search(text)
        return bool(m) and caps_delta_plausible(int(m.group(1)), int(m.group(2)))
    if kind == "join":
        m = _JOIN_LINE.match(text)
        if not m:
            return False
        name = _KANA.sub("", m.group("n1") or m.group("n2") or "").strip()
        team = (m.group("t1") or m.group("t2") or "").strip()
        for lg, p in _players_by_name().get(name, []):
            if team in _team_names(lg, p.get("team_id")):
                # 国内（リーグワン）は名簿掲載＝公式発表ベースのため所属一致で可。海外は career 裏付け必須。
                if lg.startswith("league-one") or join_verified(lg, p["id"], p.get("team_id")):
                    return True
        return False
    return True
