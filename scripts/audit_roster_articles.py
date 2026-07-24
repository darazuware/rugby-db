#!/usr/bin/env python3.11
"""src/content/news の海外リーグ・ロースター記事(*-2025-26.md)を監査する読み取り専用ツール。

data/master/players/{league}.json + data/master/teams/{league}.json を正とし、
記事内のロースター表と突合して以下を検出する（03_VALIDATION.md方針: 事実はAIの
知識で書かない/補わない。masterと矛盾する記事側を疑う）:

  1. stale: 記事にいるが master の現ロースターに居ない選手（移籍・引退・誤記の疑い）
  2. katakana_conflict: 同一選手(name_en正規化一致)がサイト内で複数のカタカナ表記
     を持つ（表記ゆれ）

master に無い記事側選手は自動削除しない（03: 自動確定しない）。一覧を出すだけ。
このスクリプトはdata/masterを一切書き換えない。

    python3.11 scripts/audit_roster_articles.py
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASTER_PLAYERS = ROOT / "data" / "master" / "players"
MASTER_TEAMS = ROOT / "data" / "master" / "teams"
NEWS_DIR = ROOT / "src" / "content" / "news"
PLAYERS_DIR = ROOT / "src" / "content" / "players"

# ファイルslugがteam_idと文字列一致しない例外（改名・スポンサー名等）
SLUG_OVERRIDES = {
    "stade-francais": "paris",
}
SKIP_SLUGS = {"league-guide", "how-to-watch", "pacific-team-guide"}

LEAGUE_FILE_PREFIX = {
    "top14": "top14",
    "premiership": "premiership",
    "urc": "urc",
    "super-rugby": "super-rugby",
}

ROW_RE = re.compile(r"^\|\s*([A-ZÀ-Ýa-zà-ÿ0-9'.\- ]+?)\s*\|\s*([^\|]+?)\s*\|")


def normalize_name(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    name = re.sub(r"[^A-Za-z ]", " ", name)
    return " ".join(name.upper().split())


def load_master_roster_names(league: str) -> tuple[dict[str, set[str]], dict[str, str]]:
    """team_id -> set(normalized name_en), team_id -> roster_mode を返す。

    premiership/urc は roster_mode="partial"（masterが全選手を捕捉していない）
    なので、不在=移籍/誤記とは断定できない。roster_mode="full" のチームだけが
    stale判定の対象になる。
    """
    players_path = MASTER_PLAYERS / f"{league}.json"
    teams_path = MASTER_TEAMS / f"{league}.json"
    players = {p["id"]: p for p in json.loads(players_path.read_text())}
    teams = json.loads(teams_path.read_text())
    out: dict[str, set[str]] = {}
    modes: dict[str, str] = {}
    for t in teams:
        names = set()
        for pid in t.get("roster_ids", []):
            p = players.get(pid)
            if p and p.get("name_en"):
                names.add(normalize_name(p["name_en"]))
        out[t["id"]] = names
        modes[t["id"]] = t.get("roster_mode")
    return out, modes


def guess_team_id(filename_slug: str, team_ids: list[str]) -> str | None:
    if filename_slug in SLUG_OVERRIDES:
        return SLUG_OVERRIDES[filename_slug]
    candidates = [tid for tid in team_ids if tid in filename_slug or filename_slug in tid]
    if len(candidates) == 1:
        return candidates[0]
    # サブ文字列一致が複数/0件なら、より長い一致を優先
    if candidates:
        return max(candidates, key=len)
    return None


def extract_roster_rows(md_path: Path) -> list[tuple[str, str]]:
    """記事から (name_en, katakana) の行を全部抜く。"""
    rows = []
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        if "---" in line or "選手名" in line:
            continue
        m = ROW_RE.match(line)
        if not m:
            continue
        name_en, kana = m.group(1).strip(), m.group(2).strip()
        if not name_en or not kana:
            continue
        if not re.search(r"[A-Za-z]", name_en):
            continue
        if not re.search(r"[゠-ヿ぀-ゟ]", kana):
            continue
        rows.append((name_en, kana))
    return rows


FRONTMATTER_RE = re.compile(
    r'^name_en:\s*"([^"]+)"\s*$.*?^name_ja:\s*"([^"]+)"\s*$',
    re.MULTILINE | re.DOTALL,
)


def index_player_pages(kana_index: dict[str, dict[str, list[str]]]) -> None:
    for md_path in PLAYERS_DIR.rglob("*.md"):
        text = md_path.read_text(encoding="utf-8")
        fm = text.split("---", 2)
        if len(fm) < 3:
            continue
        m = FRONTMATTER_RE.search(fm[1])
        if not m:
            continue
        name_en, name_ja = m.group(1).strip(), m.group(2).strip()
        if not re.search(r"[A-Za-z]", name_en) or not re.search(r"[゠-ヿ぀-ゟ]", name_ja):
            continue
        norm = normalize_name(name_en)
        rel = str(md_path.relative_to(ROOT))
        kana_index[norm][name_ja].append(rel)


def main() -> int:
    stale_report: list[str] = []
    kana_index: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    for league, prefix in LEAGUE_FILE_PREFIX.items():
        roster_by_team, modes_by_team = load_master_roster_names(prefix)
        team_ids = list(roster_by_team.keys())
        news_files = sorted(NEWS_DIR.glob(f"{prefix}-*-2025-26.md"))
        for md_path in news_files:
            slug = md_path.stem[len(prefix) + 1: -len("-2025-26")]
            if slug in SKIP_SLUGS:
                continue
            team_id = guess_team_id(slug, team_ids)
            rows = extract_roster_rows(md_path)
            master_names = roster_by_team.get(team_id, set()) if team_id else set()
            is_full = team_id and modes_by_team.get(team_id) == "full"
            for name_en, kana in rows:
                norm = normalize_name(name_en)
                kana_index[norm][kana].append(md_path.name)
                if is_full and norm not in master_names:
                    stale_report.append(
                        f"[{league}/{md_path.name}] team_id={team_id}: "
                        f"'{name_en}' が master ロースター(full)に見当たらない"
                    )
            if not team_id:
                stale_report.append(f"[{league}/{md_path.name}] team_id 特定不能 (slug={slug})")

    index_player_pages(kana_index)

    print("=== A. stale / unmatched roster entries ===")
    for line in stale_report:
        print(line)
    print(f"\n合計 {len(stale_report)} 件")

    print("\n=== B. katakana表記ゆれ (同一選手が複数カタカナ) ===")
    conflict_count = 0
    for norm, variants in sorted(kana_index.items()):
        if len(variants) > 1:
            conflict_count += 1
            print(f"{norm}:")
            for kana, files in variants.items():
                print(f"   {kana}  <- {', '.join(files)}")
    print(f"\n合計 {conflict_count} 件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
