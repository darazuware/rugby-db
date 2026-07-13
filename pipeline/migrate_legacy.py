"""P1-4 レガシーDB → 新スキーマ移行（01_DATA_ARCHITECTURE.md）。

入力（すべて data/legacy・data/ 配下の既存ファイル。AIの知識で事実を補完しない）:
  data/unified_player_database_final.json  … 6018件（all_rugby / league_one / top_14）
  data/legacy/league_one_teams_detailed.json … 26チームの division / host_area / 公式サイト
  data/legacy/top14_teams.json                … 14チームの name_ja→slug

出力:
  data/master/players/league-one-d1|d2|d3.json, top14.json
  data/master/teams/league-one-d1|d2|d3.json, top14.json
  data/master/_meta/redirects.json      … 旧slug→新slug（301対象。/players/{old}→/players/{new}）
  data/master/_meta/retired_slugs.json   … master化しない退避ページ（P2-4が一覧集約 or 410）
  data/master/_meta/migration_report.md  … 件数・null化件数・退避内訳

方針（01）:
  - league_one → league-one-d{1,2,3}（division は detailed.json 由来の事実）
  - top_14 → top14（team_id は top14_teams.json の slug）
  - all_rugby（4040件のインデックス stub。league/team 不明）は master 化しない → 退避集計のみ
  - 旧トップリーグ地域(top-east/kyushu/west)・個別 high-school/university ページは退避
  - 値が欠ける/矛盾は null（補完しない）。件数を migration_report.md に記録
  - 旧league-one個別ページ↔新league_oneレコードは name_en+birthdate で名寄せし旧→新slugを出力
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from pydantic import ValidationError

from pipeline import io
from pipeline.schemas import Player, Team, normalize_name_en

REPO_ROOT = Path(__file__).resolve().parent.parent
LEGACY_DB = REPO_ROOT / "data" / "unified_player_database_final.json"
LO_TEAMS = REPO_ROOT / "data" / "legacy" / "league_one_teams_detailed.json"
T14_TEAMS = REPO_ROOT / "data" / "legacy" / "top14_teams.json"
CONTENT_DIR = REPO_ROOT / "src" / "content" / "players"
JST = timezone(timedelta(hours=9))

DIVISION_KEY = {"Division 1": "league-one-d1", "Division 2": "league-one-d2", "Division 3": "league-one-d3"}
# 旧 src/content/players サブフォルダのうち master 化しないもの（01: 退避）
RETIRED_CATEGORIES = {"top-east", "top-kyushu", "top-west-a", "top-west-b", "top-west-c", "high-school", "university"}


def _now() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")


def _norm_bd(v) -> Optional[str]:
    """'1988.04.25' / '2003年07月25日' / '1994-5-22' → 'YYYY-MM-DD'。不能は None。"""
    if not v:
        return None
    m = re.search(r"(\d{4})\D{1,2}(\d{1,2})\D{1,2}(\d{1,2})", str(v))
    if not m:
        return None
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return None
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _strip_season(team: str) -> str:
    return re.sub(r"（20\d{2}-\d{2}）.*$", "", team or "").strip()


def _season_of(team: str) -> Optional[str]:
    m = re.search(r"（(20\d{2}-\d{2})）", team or "")
    return m.group(1) if m else None


# pandas NaN 等が文字列化した無効値（校名として採用しない）
_NULLISH = {"", "nan", "none", "null", "-", "―", "なし", "不明"}


def _education(raw: dict) -> list[dict]:
    out = []
    for field, typ in (("high_school", "hs"), ("university", "univ")):
        name = str(raw.get(field) or "").strip()
        if name and name.lower() not in _NULLISH:
            out.append({"school_id": None, "name_raw": name, "type": typ,
                        "grad_year": None, "source_url": None, "scraped_at": None})
    return out


def _season_stats(stats: Optional[dict], season: Optional[str]) -> Optional[dict]:
    """all_rugby_stats → SeasonStats dict。season 不明時は None（捏造しない）。"""
    if not stats or not season:
        return None
    matches = stats.get("matches_played", stats.get("matches"))
    return {"season": season, "matches": matches, "tries": stats.get("tries"), "points": stats.get("points")}


_CAREER_RE = re.compile(r"^(.+?)\s*\((\d{4})\s*-\s*(\d{4})?\s*\)\s*$")


def _career(hist) -> list[dict]:
    out = []
    if not isinstance(hist, list):
        return out
    for entry in hist:
        if not isinstance(entry, str) or not entry.strip():
            continue
        m = _CAREER_RE.match(entry.strip())
        if m:
            out.append({"team": m.group(1).strip(),
                        "from": int(m.group(2)), "to": int(m.group(3)) if m.group(3) else None})
        else:
            out.append({"team": entry.strip(), "from": None, "to": None})
    return out


class NullTally:
    """present だが値を採用できず null 化した件数を field 別に集計。"""

    def __init__(self) -> None:
        self.dropped: Counter = Counter()
        self.absent: Counter = Counter()

    def note(self, field: str, present: bool, kept) -> None:
        if kept in (None, [], {}) and present:
            self.dropped[field] += 1
        elif kept in (None, [], {}):
            self.absent[field] += 1


def _build_player(raw: dict, *, league: str, team_id: Optional[str], pid: str,
                  source: str, source_url: str, tally: NullTally) -> tuple[Optional[dict], list[str]]:
    name_en = raw.get("name_en") or None
    name_ja = raw.get("name_ja") or None
    if not (name_en or name_ja):
        return None, [f"{pid}: name_en/name_ja が両方欠落のためスキップ"]

    src_id = pid.split("_", 1)[1] if "_" in pid else pid
    if name_en:
        slug = src_id if not src_id.isdigit() else f"{_slugify(name_en)}-{src_id}"
    else:
        slug = src_id if not src_id.isdigit() else f"{league}-{src_id}"

    season = _season_of(raw.get("team", ""))
    bd = _norm_bd(raw.get("birthdate"))
    tally.note("birthdate", bool(raw.get("birthdate")), bd)
    edu = _education(raw)
    career = _career(raw.get("career_history"))

    data = {
        "id": pid, "source": source, "source_url": source_url, "scraped_at": _now(),
        "name_en": name_en, "name_ja": name_ja, "slug": slug,
        "position": raw.get("position") or None, "team_id": team_id, "league": league,
        "height_cm": raw.get("height"), "weight_kg": raw.get("weight"), "birthdate": bd,
        "league_caps": raw.get("league_one_caps"), "career": career,
        "season_stats": _season_stats(raw.get("all_rugby_stats"), season),
        "education": edu, "image_url": raw.get("image_url") or None,
    }
    try:
        model, w = Player.parse(data)
    except ValidationError as exc:
        return None, [f"{pid}: Player 検証失敗 {exc.error_count()}件 → スキップ ({exc.errors()[0]['msg']})"]
    for f in ("height_cm", "weight_kg"):
        tally.note(f, raw.get({"height_cm": "height", "weight_kg": "weight"}[f]) not in (None, ""),
                   getattr(model, f))
    tally.note("position", bool(raw.get("position")), model.position)
    return model.model_dump(by_alias=True), w


def migrate() -> None:
    db = io.read_json(LEGACY_DB, default={})
    records = list(db.values())
    lo_detail = {d["team_name"]: d for d in io.read_json(LO_TEAMS, default=[])}
    t14_slug = {d["name_ja"]: d for d in io.read_json(T14_TEAMS, default=[])}

    players: dict[str, list[dict]] = defaultdict(list)   # league -> [player]
    roster: dict[str, list[str]] = defaultdict(list)     # team_id -> [player_id]
    lo_team_meta: dict[str, tuple[str, dict]] = {}        # team_id -> (league, detail)
    t14_teams_used: dict[str, dict] = {}                  # team_id -> cfg
    warnings: list[str] = []
    tally = NullTally()
    counts = Counter()
    unmapped_teams: Counter = Counter()

    for raw in records:
        src = raw.get("source")
        counts[f"in_{src}"] += 1

        if src == "league_one":
            base = _strip_season(raw.get("team", ""))
            det = lo_detail.get(base)
            if det is None:
                unmapped_teams[base] += 1
                warnings.append(f"lo {raw.get('id')}: チーム '{base}' が detailed.json 未収載 → スキップ")
                counts["skip_lo_noteam"] += 1
                continue
            league = DIVISION_KEY[det["division"]]
            team_id = f"lo_team_{det['id']}"
            lo_team_meta[team_id] = (league, det)
            p, w = _build_player(raw, league=league, team_id=team_id, pid=raw["id"],
                                 source="league-one.jp",
                                 source_url=f"https://league-one.jp/player/{raw['id'].split('_',1)[1]}",
                                 tally=tally)
            warnings.extend(w)
            if p:
                players[league].append(p)
                roster[team_id].append(p["id"])
                counts["out_league_one"] += 1

        elif src == "top_14":
            cfg = t14_slug.get(raw.get("team"))
            if cfg is None:
                unmapped_teams[raw.get("team")] += 1
                warnings.append(f"top14 {raw.get('id')}: チーム '{raw.get('team')}' 未収載 → スキップ")
                counts["skip_t14_noteam"] += 1
                continue
            team_id = cfg["slug"]
            t14_teams_used[team_id] = cfg
            pid = f"ar_{raw['id']}"
            p, w = _build_player(raw, league="top14", team_id=team_id, pid=pid,
                                 source="all.rugby",
                                 source_url=f"https://all.rugby/player/{raw['id']}", tally=tally)
            warnings.extend(w)
            if p:
                players["top14"].append(p)
                roster[team_id].append(p["id"])
                counts["out_top14"] += 1

        elif src == "all_rugby":
            counts["defer_all_rugby"] += 1  # league/team 不明 → master化しない（P1-5/P1-7で取得）

    # --- Team レコード ---
    teams: dict[str, list[dict]] = defaultdict(list)
    for team_id, (league, det) in lo_team_meta.items():
        stadium = [{"name": det["home_ground"], "source_url": None}] if det.get("home_ground") else []
        data = {
            "id": team_id, "league": league, "name_ja": det["team_name"],
            "source_url": "https://league-one.jp/", "scraped_at": _now(),
            "home_area": det.get("host_area") or None, "home_stadiums": stadium,
            "official_url": det.get("official_site") or None,
            "roster_mode": "full", "roster_ids": sorted(roster[team_id]),
        }
        try:
            teams[league].append(Team.model_validate(data).model_dump(by_alias=True))
        except ValidationError as exc:
            warnings.append(f"team {team_id}: 検証失敗 {exc.error_count()}件")
    for team_id, cfg in t14_teams_used.items():
        data = {
            "id": team_id, "league": "top14", "name_ja": cfg["name_ja"], "name_en": cfg["name"],
            "source_url": cfg["url"], "scraped_at": _now(),
            "roster_mode": "full", "roster_ids": sorted(roster[team_id]),
        }
        try:
            teams["top14"].append(Team.model_validate(data).model_dump(by_alias=True))
        except ValidationError as exc:
            warnings.append(f"team {team_id}: 検証失敗 {exc.error_count()}件")

    # --- master 書き込み ---
    for league, recs in players.items():
        io.write_records(io.players_path(league), recs)
    for league, recs in teams.items():
        io.write_records(io.teams_path(league), recs)

    # --- redirects / retired（旧 src/content/players を走査） ---
    redirects, retired, report_redirect = _build_redirects(players)

    # --- 出力 ---
    io.write_json(io.META_DIR / "redirects.json", redirects)
    io.write_json(io.META_DIR / "retired_slugs.json", retired)
    _write_report(counts, tally, warnings, unmapped_teams, players, teams, redirects, retired, report_redirect)

    print(f"migrated: league_one={counts['out_league_one']} top14={counts['out_top14']} "
          f"deferred all_rugby={counts['defer_all_rugby']}")
    print(f"redirects={len(redirects)} retired={len(retired)} warnings={len(warnings)}")


def _read_frontmatter(path: Path) -> dict:
    txt = path.read_text(encoding="utf-8")
    d = {}
    m = re.search(r"^---\n(.*?)\n---", txt, re.S)
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r'(\w+):\s*"?(.*?)"?\s*$', line)
            if mm:
                d[mm.group(1)] = mm.group(2)
    return d


def _build_redirects(players: dict[str, list[dict]]):
    """旧個別ページ → 新slug を name_en(+birthdate) 名寄せで作成。

    - 旧 league-one ページ → 新 league-one-d* レコード（旧slug≠新slugのみ301）
    - top-east/kyushu/west・個別 high-school/university → 退避
    - master 化されない旧 pro（urc/premiership/super-rugby/未分類）も退避
    戻り: (redirects{old_url:new_url}, retired[old_url], report{カテゴリ別件数})
    """
    # 新 league-one インデックス: 名寄せキー → new_slug
    lo_index: dict[str, str] = {}
    lo_dupe: set = set()
    for league in ("league-one-d1", "league-one-d2", "league-one-d3"):
        for p in players.get(league, []):
            for key in _match_keys(p.get("name_en"), p.get("name_ja"), p.get("birthdate")):
                if key in lo_index and lo_index[key] != p["slug"]:
                    lo_dupe.add(key)
                lo_index.setdefault(key, p["slug"])
    # top14 の新slug集合（旧pro top14 は slug 不変で温存されるので退避不要）
    t14_slugs = {p["slug"] for p in players.get("top14", [])}

    redirects: dict[str, str] = {}
    retired: list[str] = []
    report = Counter()
    if not CONTENT_DIR.exists():
        return redirects, retired, report

    for md in sorted(CONTENT_DIR.rglob("*.md")):
        category = md.parent.name
        fm = _read_frontmatter(md)
        old_slug = fm.get("slug") or md.stem
        old_url = f"/players/{old_slug}"

        if category in RETIRED_CATEGORIES:
            retired.append(old_url)
            report[f"retired:{category}"] += 1
            continue

        league = fm.get("league", "")
        if league == "league-one":
            keys = _match_keys(fm.get("name_en"), fm.get("name_ja"), _norm_bd(fm.get("birth_date")))
            new_slug = next((lo_index[k] for k in keys if k in lo_index and k not in lo_dupe), None)
            if new_slug is None:
                retired.append(old_url)
                report["retired:league-one-unmatched"] += 1
            elif new_slug != old_slug:
                redirects[old_url] = f"/players/{new_slug}"
                report["redirect:league-one"] += 1
            else:
                report["preserved:league-one"] += 1
        elif league == "top14" and old_slug in t14_slugs:
            report["preserved:top14"] += 1  # slug不変で新masterに存在
        else:
            # top14未migrate / urc / premiership / super-rugby / 未分類 → 現状master無し
            retired.append(old_url)
            report[f"retired:pro-{league or 'unknown'}"] += 1

    return redirects, sorted(set(retired)), report


def _match_keys(name_en, name_ja, birthdate) -> list[str]:
    keys = []
    bd = birthdate or ""
    if name_en:
        keys.append(f"en|{normalize_name_en(name_en)}|{bd}")
    if name_ja:
        ja = re.sub(r"\s+", "", name_ja)
        keys.append(f"ja|{ja}|{bd}")
    return keys


def _write_report(counts, tally, warnings, unmapped_teams, players, teams, redirects, retired, report_redirect) -> None:
    L = []
    L.append("# レガシーDB移行レポート（P1-4）\n")
    L.append(f"生成: {_now()}  ソース: `data/unified_player_database_final.json`\n")

    L.append("## 入力→出力（選手）\n")
    L.append("| source | 入力 | master化 | 備考 |")
    L.append("|---|---:|---:|---|")
    L.append(f"| league_one | {counts['in_league_one']} | {counts['out_league_one']} | "
             f"skip(チーム未収載) {counts['skip_lo_noteam']} |")
    L.append(f"| top_14 | {counts['in_top_14']} | {counts['out_top14']} | "
             f"skip(チーム未収載) {counts['skip_t14_noteam']} |")
    L.append(f"| all_rugby | {counts['in_all_rugby']} | 0 | "
             f"league/team不明のstubのため退避（P1-5/P1-7で取得） {counts['defer_all_rugby']} |\n")

    L.append("## master ファイル件数\n")
    for league in sorted(players):
        L.append(f"- players/{league}.json: {len(players[league])}")
    for league in sorted(teams):
        L.append(f"- teams/{league}.json: {len(teams[league])}")
    L.append("")

    L.append("## null 化件数（値はあるが採用不可 → null）\n")
    if tally.dropped:
        for f, c in tally.dropped.most_common():
            L.append(f"- {f}: {c}")
    else:
        L.append("- なし")
    L.append("")
    L.append("補完しない方針（01）のため、上記は捏造せず null で確定。\n")

    if unmapped_teams:
        L.append("## チーム未収載でスキップした選手のチーム\n")
        for t, c in unmapped_teams.most_common():
            L.append(f"- {t}: {c}")
        L.append("")

    L.append("## 旧URL処理（src/content/players 走査）\n")
    L.append(f"- redirects.json（旧slug→新slug 301）: {len(redirects)}")
    L.append(f"- retired_slugs.json（master無し・退避、P2-4で一覧集約 or 410）: {len(retired)}")
    L.append("")
    L.append("内訳:")
    for k, c in sorted(report_redirect.items()):
        L.append(f"- {k}: {c}")
    L.append("")
    L.append("> 退避対象: 旧トップリーグ地域(top-east/kyushu/west)・個別high-school/university、"
             "および現状master未整備の pro(urc/premiership/super-rugby/未分類)。"
             "super-rugby/urc/premiership は該当スクレイパー(P1-6/P4-6)整備後に再移行で301化可能。\n")

    if warnings:
        L.append(f"## warnings（{len(warnings)}件、先頭50）\n")
        for w in warnings[:50]:
            L.append(f"- {w}")
        if len(warnings) > 50:
            L.append(f"- …他 {len(warnings) - 50} 件")
        L.append("")

    io.write_json  # noqa: keep import used
    (io.META_DIR).mkdir(parents=True, exist_ok=True)
    (io.META_DIR / "migration_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    migrate()
