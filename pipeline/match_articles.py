"""日本代表戦（テストマッチ）のプレビュー／レビュー記事の自動生成。

情報源は日本協会（www.rugby-japan.jp）のみ:
  - 試合索引  : jrfu._SCHEDULE_INDEX_URL（日本代表が絡む試合の game_id と日付）
  - 試合詳細  : /v1.0/game.php?game_id={id}（会場・放送・審判・両チーム登録メンバー・スコア）
  - キャップ数: /news/category/national/ の「試合登録メンバーのお知らせ」記事の表
                （game.php の cap_num は更新が遅れるため日本側の値には使わない）

03_VALIDATION 原則: 事実の創作禁止。記事に書くのは上記ページにある値と、そこからの機械的な
差分（前回戦からの先発入替など）のみ。読み物としての論評は付けない（必要なら人/Claudeが後から加筆）。

  プレビュー: 両チームの登録メンバー(23名)が出揃い、キックオフ前 → 公開(draft: false)
  レビュー  : game_status == 2 かつスコア確定 → 得点経過が機械取得できないため draft: true で出力

冪等: 同じ slug のファイルが既にあれば何もしない（人が加筆した記事を上書きしない）。

CLI:
  python3 -m pipeline.match_articles            # 生成して記事を書く
  python3 -m pipeline.match_articles --dry-run  # 書かずに対象を表示
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

from pipeline import io
from pipeline.news_gen import NEWS_DIR, Article
from pipeline.scrape import jrfu

JST = timezone(timedelta(hours=9))
_NEWS_CATEGORY_URL = f"{jrfu.BASE}/news/category/national/"
NATIONAL_CONFIG = io.REPO_ROOT / "data" / "national_teams_config.json"

# 試合日の何日前から／何日後まで監視するか（メンバー発表は試合の2日前が通例）
LOOKAHEAD_DAYS = 10
LOOKBACK_DAYS = 3

_BOX = "日本代表"


# ---------------------------------------------------------------------------
# 取得
# ---------------------------------------------------------------------------

def _get_text(url: str) -> Optional[str]:
    for _ in range(3):
        try:
            r = requests.get(url, headers=jrfu._HEADERS, timeout=jrfu._TIMEOUT)
            r.raise_for_status()
            return r.text
        except Exception:  # noqa: BLE001
            time.sleep(1.0)
    return None


def fetch_game(game_id) -> Optional[dict]:
    d = jrfu._get_json(f"{jrfu.BASE}/v1.0/game.php?game_id={game_id}")
    gl = d.get("game_list") if isinstance(d, dict) else None
    return gl[0] if gl else None


def index_date(entry: dict) -> Optional[date]:
    """索引 entry の link '/braveblossoms/match/20261024/' から開催日を得る。"""
    m = re.search(r"/(\d{8})/?$", entry.get("link") or "")
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%Y%m%d").date()
    except ValueError:
        return None


def target_entries(index: list[dict], today: date) -> list[dict]:
    """日本代表(男子15人制)が絡み、監視窓に入る試合の索引 entry。"""
    out = []
    for e in index:
        if _BOX not in (e.get("home"), e.get("away")):
            continue
        d = index_date(e)
        if d is None or not (today - timedelta(days=LOOKBACK_DAYS) <= d <= today + timedelta(days=LOOKAHEAD_DAYS)):
            continue
        out.append(e)
    return out


def fetch_japan_roster(opponent_short: str) -> dict[str, dict]:
    """「試合登録メンバーのお知らせ」記事の表 → {英字氏名(大文字): 行dict}。見つからなければ空。

    協会が正式発表した値（氏名表記・所属・出身校・体格・キャップ数・◎共同主将）を持つ。
    game.php の同項目は更新が遅れる／主将フラグが1名分しか立たないため、あれば表を優先する。
    """
    html = _get_text(_NEWS_CATEGORY_URL)
    if not html:
        return {}
    soup = BeautifulSoup(html, "html.parser")
    href = None
    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)
        if "試合登録メンバー" in text and opponent_short in text and re.search(r"/news/\d+", a["href"]):
            href = a["href"]
            break
    if not href:
        return {}
    page = _get_text(href if href.startswith("http") else jrfu.BASE + href)
    return parse_roster_table(page) if page else {}


def _first_line(td) -> str:
    ps = [p.get_text(" ", strip=True) for p in td.find_all("p")]
    return (ps[0] if ps else td.get_text(" ", strip=True)).strip()


def parse_roster_table(html: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    soup = BeautifulSoup(html, "html.parser")
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 8:
            continue
        cells = [td.get_text(" ", strip=True) for td in tds]
        if not cells[0].isdigit() or not cells[-1].isdigit():
            continue
        name_ps = [p.get_text(" ", strip=True) for p in tds[1].find_all("p")]
        ja = name_ps[0] if name_ps else cells[1]
        en = name_ps[1] if len(name_ps) > 1 else (re.search(r"([A-Za-z][A-Za-z'.\- ]+)$", cells[1]) or [None, ""])[1]
        if not en:
            continue
        captain = "◎" in ja
        ja = ja.replace("◎", "").strip()
        out[_norm_en(en)] = {
            "number": int(cells[0]),
            "name": ja if re.search(r"[・ー]", ja) else ja.replace(" ", ""),
            "club": _first_line(tds[2]),
            "school": re.sub(r"\[[A-Z]{2,3}\]$", "", _first_line(tds[3])).strip(),
            "height": cells[4], "weight": cells[5], "caps": int(cells[-1]), "captain": captain,
        }
    return out


def _norm_en(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().upper()


# ---------------------------------------------------------------------------
# 整形（純関数）
# ---------------------------------------------------------------------------

def _clean_team_name(name: str) -> str:
    """'フィジー代表（LDCC2026）' → 'フィジー代表'、'日本代表 （別府合宿参加メンバー）' → '日本代表'。"""
    return re.sub(r"\s*[（(].*?[）)]\s*", "", name or "").strip()


def sides(g: dict) -> Optional[tuple[dict, dict, str]]:
    """(日本側 team2, 相手 team2, 'home'|'away') を返す。日本代表が居なければ None。"""
    home, away = g.get("home_team2") or {}, g.get("away_team2") or {}
    if _BOX in (home.get("name") or ""):
        return home, away, "home"
    if _BOX in (away.get("name") or ""):
        return away, home, "away"
    return None


def jp_dt(epoch) -> datetime:
    return datetime.fromtimestamp(int(epoch), tz=JST)


def entries(g: dict, side: str) -> list[dict]:
    """背番号順の登録メンバー（先発15+リザーブ）。"""
    rows = (g.get("info") or {}).get(f"{side}_entry_list") or []
    rows = [r for r in rows if str(r.get("shirt_number") or "").isdigit() and not r.get("unentried")]
    return sorted(rows, key=lambda r: int(r["shirt_number"]))


def lineup_ready(g: dict) -> bool:
    return (len(entries(g, "home")) >= 23 and len(entries(g, "away")) >= 23)


def _jp_name(p: dict) -> str:
    return f"{p.get('last_name', '')}{p.get('first_name', '')}".strip()


def _jp_name_spaced(p: dict) -> str:
    return " ".join(x for x in (p.get("last_name"), p.get("first_name")) if x)


def _en(p: dict) -> str:
    return _norm_en(p.get("english_name") or "")


def _player_name(r: dict, *, japan: bool) -> str:
    """日本側は姓名連結、相手側は協会表記のカタカナ（'ペニ'+'・ラヴァイ' → 'ペニ・ラヴァイ'）。"""
    p = r["player"]
    return _jp_name(p) if japan else f"{p.get('last_name', '')}{p.get('first_name', '')}".strip()


def _br(s: Optional[str]) -> str:
    return (s or "").replace("&#12316;", "〜").strip()


def lineup_table(rows: list[dict], *, japan: bool, roster: dict[str, dict]) -> str:
    head = "| 番号 | 選手 | 所属 | 出身校 | 身長/体重 | キャップ |\n|:--:|:---|:---|:---|:---|:--:|"
    lines = [head]
    for r in rows:
        p = r["player"]
        ro = roster.get(_en(p)) if japan else None
        if ro:
            name, club, school, cap = ro["name"], ro["club"], ro["school"], ro["caps"]
            hw = f"{ro['height']}cm/{ro['weight']}kg"
            is_cap = ro["captain"]
        else:
            name, club, school = _player_name(r, japan=japan), _br(p.get("in_team")), _br(p.get("descent_college"))
            cap = None if japan else _int(p.get("cap_num"))
            hw = f"{p['height']}cm/{p['weight']}kg" if p.get("height") and p.get("weight") else "-"
            is_cap = bool(r.get("captain"))
        cap_s = "-" if cap is None else (f"**{cap}**" if cap == 0 else str(cap))
        lines.append(f"| {r['shirt_number']} | {name}{' ◎' if is_cap else ''} | {club or '-'} | {school or '-'} | {hw} | {cap_s} |")
    return "\n".join(lines)


def _int(v) -> Optional[int]:
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return None


def starters(rows):  # 1〜15
    return [r for r in rows if int(r["shirt_number"]) <= 15]


def reserves(rows):  # 16〜
    return [r for r in rows if int(r["shirt_number"]) > 15]


def broadcast_lines(text: str) -> list[str]:
    """broadcast_text '日本テレビ系全国ネット,URL\\r\\n／\\r\\nJ SPORTS 1,URL ...' → ['日本テレビ系全国ネット', ...]。"""
    out = []
    for chunk in re.split(r"\s*／\s*", text or ""):
        name = chunk.strip().split(",")[0].strip()
        if name:
            out.append(name)
    return out


def starter_changes(prev: dict, cur: dict) -> Optional[dict]:
    """前回戦→今回の日本側先発の機械的な差分（氏名集合の比較のみ）。"""
    ps = {_en(r["player"]): _player_name(r, japan=True) for r in starters(prev)}
    cs = {_en(r["player"]): _player_name(r, japan=True) for r in starters(cur)}
    if not ps or not cs:
        return None
    return {
        "changed": len(set(cs) - set(ps)),
        "in": [cs[k] for k in cs if k not in ps],
        "out": [ps[k] for k in ps if k not in cs],
    }


def _national_links() -> dict[str, str]:
    try:
        return {t["name"]: f"/national-teams/{t['slug']}/" for t in json.loads(NATIONAL_CONFIG.read_text(encoding="utf-8"))
                if t.get("name") and t.get("slug")}
    except (OSError, ValueError):
        return {}


def _team_md(name: str, links: dict[str, str]) -> str:
    return f"[{name}]({links[name]})" if name in links else name


def _slug_opp(opp_team: dict, opp_name: str) -> str:
    en = (opp_team.get("name_eng") or "").strip().lower()
    if en:
        return re.sub(r"[^a-z0-9]+", "-", en).strip("-")
    return re.sub(r"[^a-z0-9]+", "-", opp_name).strip("-") or "opponent"


# ---------------------------------------------------------------------------
# 記事ビルダー
# ---------------------------------------------------------------------------

def _overview(g: dict, entry: dict, jp_name: str, opp_name: str, links: dict[str, str]) -> list[str]:
    ko = jp_dt(g.get("start_time_plan") or g["start_time"])
    wd = "月火水木金土日"[ko.weekday()]
    comp = ((g.get("games") or {}).get("name") or entry.get("competition_title") or "").strip()
    rows = [
        ("大会", comp),
        ("日時", f"{ko.year}年{ko.month}月{ko.day}日（{wd}）{ko:%H:%M}キックオフ"),
        ("会場", (g.get("stadium") or {}).get("name") or entry.get("place") or ""),
    ]
    bc = broadcast_lines(g.get("broadcast_text") or "")
    if bc:
        rows.append(("放送・配信", "／".join(bc)))
    elif entry.get("broadcast") or entry.get("live"):
        rows.append(("放送・配信", "／".join(x for x in (entry.get("broadcast"), entry.get("live")) if x)))
    if g.get("referee"):
        rows.append(("レフェリー", g["referee"]))
    ars = [x for x in (g.get("judge1"), g.get("judge2"), g.get("judge3")) if x]
    if ars:
        rows.append(("アシスタントレフェリー", "、".join(ars)))
    if g.get("tmo"):
        rows.append(("TMO", g["tmo"]))
    if g.get("weather"):
        rows.append(("天候", f"{g['weather']}（グラウンド状態: {g.get('pitch') or '-'}）"))
    out = ["| 項目 | 内容 |", "|:---|:---|"]
    out += [f"| {k} | {v} |" for k, v in rows if v]
    return out


def _title_date(ko: datetime) -> str:
    return f"{ko.month}.{ko.day}"


def build_preview(g: dict, entry: dict, *, roster: dict[str, dict], prev_game: Optional[dict],
                  links: dict[str, str]) -> Optional[Article]:
    s = sides(g)
    if s is None or not lineup_ready(g):
        return None
    jp_t, opp_t, jp_side = s
    opp_side = "away" if jp_side == "home" else "home"
    jp_name, opp_name = _clean_team_name(jp_t["name"]), _clean_team_name(opp_t["name"])
    ko = jp_dt(g.get("start_time_plan") or g["start_time"])
    jp_rows, opp_rows = entries(g, jp_side), entries(g, opp_side)
    comp = ((g.get("games") or {}).get("name") or entry.get("competition_title") or "").strip()
    slug = f"japan-vs-{_slug_opp(opp_t, opp_name)}-{ko:%Y-%m-%d}-preview"
    venue = (g.get("stadium") or {}).get("name") or ""
    title = f"【プレビュー】日本代表 vs {opp_name} {_title_date(ko)}{venue} ― 先発・リザーブ全23名、放送・キックオフ時刻"
    desc = (f"{ko.year}年{ko.month}月{ko.day}日、{venue}で行われる{comp}・日本代表対{opp_name}。"
            f"両チームの先発とリザーブ全23名、キックオフ時刻、テレビ放送・配信、レフェリーをまとめました。")

    body: list[str] = []
    body.append(f"{ko.year}年{ko.month}月{ko.day}日（{'月火水木金土日'[ko.weekday()]}）{ko:%H:%M}、{venue}。"
                f"{_team_md(jp_name, links)}が{_team_md(opp_name, links)}と対戦します。")
    body += ["", "---", "", "## 試合概要", ""] + _overview(g, entry, jp_name, opp_name, links)
    body += ["", "※ 放送開始時刻は変更される場合があります。", ""]

    caps_cols_ok = bool(roster)
    body += ["---", "", f"## {jp_name}メンバー（登録23名）", ""]
    prev_s = sides(prev_game) if prev_game else None
    ch = starter_changes(entries(prev_game, prev_s[2]), jp_rows) if prev_s else None
    if ch is not None and prev_game is not None and prev_s:
        if True:
            pk = jp_dt(prev_game.get("start_time_plan") or prev_game["start_time"])
            pn = _clean_team_name(prev_s[1]["name"])
            line = f"前回の{pn}戦（{pk.month}月{pk.day}日）から先発を **{ch['changed']}人** 入れ替えました。"
            if ch["in"]:
                line += f"新たに先発に入ったのは{'、'.join(ch['in'])}。"
            body += [line, ""]
    cap = [ro["name"] for ro in sorted(roster.values(), key=lambda x: x["number"]) if ro["captain"]] or \
        [_jp_name(r["player"]) for r in jp_rows if r.get("captain")]
    if cap:
        body += [f"{'共同' if len(cap) > 1 else ''}キャプテン: {'、'.join(cap)}", ""]
    body += ["### 先発", "", lineup_table(starters(jp_rows), japan=True, roster=roster), "",
             "### リザーブ", "", lineup_table(reserves(jp_rows), japan=True, roster=roster), ""]
    debut = [roster[_en(r["player"])]["name"] for r in jp_rows if _en(r["player"]) in roster and roster[_en(r["player"])]["caps"] == 0]
    if debut:
        body += [f"**初キャップ候補**: {'、'.join(debut)}（キャップ数0。出場すれば代表デビュー）", ""]
    if not caps_cols_ok:
        body += ["※ キャップ数は協会の登録メンバー発表の確認が取れ次第追記します。", ""]
    body += ["◎＝キャプテン", "", "---", "", f"## {opp_name}メンバー（登録23名）", ""]
    ocap = [r["player"] for r in opp_rows if r.get("captain")]
    if ocap:
        body += [f"キャプテン: {'、'.join(_player_name({'player': p}, japan=False) for p in ocap)}", ""]
    body += ["### 先発", "", _opp_table(starters(opp_rows)), "",
             "### リザーブ", "", _opp_table(reserves(opp_rows)), "",
             "※ キャップ数は協会掲載値（確定次第更新）。カタカナ表記は日本協会の掲載に準拠しています。", ""]
    body += ["---", "", "試合結果は、終了後にレビュー記事でお届けします。選手のプロフィールは"
             "RUGBY PICKSの[選手名鑑](/players/)から。", "",
             "*※ 本記事のメンバー・日時・放送情報は日本ラグビーフットボール協会の公式発表に基づいています。*"]
    art = Article(slug=slug, title=title, body="\n".join(body), tags=["日本代表", opp_name, comp, "テストマッチ", "プレビュー", f"{ko.year}年"],
                  pub_date=ko.strftime("%Y-%m-%d"), source_diff=f"jrfu_game_{g.get('game_id')}")
    art.description = desc  # type: ignore[attr-defined]
    return art


def _opp_table(rows: list[dict]) -> str:
    lines = ["| 番号 | 選手 | 所属 | キャップ |", "|:--:|:---|:---|:--:|"]
    for r in rows:
        p = r["player"]
        mark = " ◎" if r.get("captain") else ""
        cap = _int(p.get("cap_num"))
        lines.append(f"| {r['shirt_number']} | {_player_name(r, japan=False)}{mark} | {_br(p.get('in_team')) or '-'} "
                     f"| {'-' if cap is None else cap} |")
    return "\n".join(lines)


def build_review(g: dict, entry: dict, *, links: dict[str, str]) -> Optional[Article]:
    s = sides(g)
    if s is None or g.get("game_status") != 2:
        return None
    jp_t, opp_t, jp_side = s
    opp_side = "away" if jp_side == "home" else "home"
    jp_pts, opp_pts = _int(g.get(f"{jp_side}_team_points")), _int(g.get(f"{opp_side}_team_points"))
    if jp_pts is None or opp_pts is None:
        return None
    jp_name, opp_name = _clean_team_name(jp_t["name"]), _clean_team_name(opp_t["name"])
    ko = jp_dt(g.get("start_time_plan") or g["start_time"])
    venue = (g.get("stadium") or {}).get("name") or ""
    comp = ((g.get("games") or {}).get("name") or entry.get("competition_title") or "").strip()
    result = "勝利" if jp_pts > opp_pts else ("敗戦" if jp_pts < opp_pts else "引き分け")
    slug = f"japan-vs-{_slug_opp(opp_t, opp_name)}-{ko:%Y-%m-%d}-review"
    title = f"日本代表 {jp_pts}-{opp_pts} {opp_name} レビュー ― {venue}で{result}"
    h1 = (_int(g.get(f"{jp_side}_team_first_points")), _int(g.get(f"{opp_side}_team_first_points")))
    body = [f"{ko.year}年{ko.month}月{ko.day}日、{venue}。{comp}で{_team_md(jp_name, links)}は{_team_md(opp_name, links)}と対戦し、"
            f"**{jp_pts}-{opp_pts}** で{result}しました。", "", "---", "", "## 試合結果サマリー", "",
            "| 項目 | 内容 |", "|:---|:---|", f"| 大会 | {comp} |",
            f"| 日時 | {ko.year}年{ko.month}月{ko.day}日（{'月火水木金土日'[ko.weekday()]}）{ko:%H:%M}キックオフ |",
            f"| 会場 | {venue} |", f"| スコア | 日本代表 {jp_pts}-{opp_pts} {opp_name} |"]
    if None not in h1:
        body.append(f"| 前半 | 日本代表 {h1[0]}-{h1[1]} {opp_name} |")
    if g.get("referee"):
        body.append(f"| レフェリー | {g['referee']} |")
    if _int(g.get("audience_num")):
        body.append(f"| 観衆 | {_int(g['audience_num']):,}人 |")
    if g.get("mom"):
        body.append(f"| プレーヤー・オブ・ザ・マッチ | {g['mom']} |")
    body += ["", "<!-- TODO: 得点経過（トライ・ゴール・PG）と試合の流れは協会の試合レポートで確認して追記。公開前に draft: false にする -->",
             "", "---", "", "*※ 本記事の試合結果・スコアは日本ラグビーフットボール協会の公式発表に基づいています。*"]
    return Article(slug=slug, title=title, body="\n".join(body),
                   tags=["日本代表", opp_name, comp, "テストマッチ", "レビュー", f"{ko.year}年"],
                   pub_date=ko.strftime("%Y-%m-%d"), source_diff=f"jrfu_game_{g.get('game_id')}", draft=True)


# ---------------------------------------------------------------------------
# 実行
# ---------------------------------------------------------------------------

def _front(art: Article) -> str:
    md = art.to_markdown()
    desc = getattr(art, "description", None)
    if desc:
        md = md.replace(f'title: "{art.title}"\n', f'title: "{art.title}"\ndescription: "{desc}"\n', 1)
    return md


def run(*, dry_run: bool = False, today: Optional[date] = None, news_dir: Path = NEWS_DIR) -> list[tuple[str, Article]]:
    """新規に作った (kind, Article) を返す。既存 slug はスキップ。"""
    today = today or datetime.now(JST).date()
    index = jrfu._get_json(jrfu._SCHEDULE_INDEX_URL)
    if not isinstance(index, list):
        print("match_articles: 試合索引の取得失敗", file=sys.stderr)
        return []
    links = _national_links()
    made: list[tuple[str, Article]] = []
    all_japan = sorted((e for e in index if _BOX in (e.get("home"), e.get("away")) and index_date(e)),
                       key=lambda e: index_date(e))
    for e in target_entries(index, today):
        g = fetch_game(e["id"])
        time.sleep(jrfu._SLEEP)
        if not g or not sides(g):
            continue
        opp_short = _clean_team_name(sides(g)[1]["name"]).replace("代表", "")
        ko_date = index_date(e)
        for kind in ("preview", "review"):
            if kind == "preview":
                if g.get("game_status") == 2 or not lineup_ready(g):
                    continue
                prev = next((x for x in reversed(all_japan) if index_date(x) < ko_date
                             and x.get("home") != "JAPAN XV" and x.get("away") != "JAPAN XV"), None)
                prev_g = fetch_game(prev["id"]) if prev else None
                art = build_preview(g, e, roster=fetch_japan_roster(opp_short), prev_game=prev_g, links=links)
            else:
                art = build_review(g, e, links=links)
            if art is None:
                continue
            path = news_dir / art.filename()
            if path.exists():
                continue
            if not dry_run:
                path.write_text(_front(art), encoding="utf-8")
            made.append((kind, art))
    return made


def notify(made: list[tuple[str, Article]]) -> None:
    from pipeline import telegram_notify as tg
    for kind, art in made:
        if kind == "preview":
            tg.send(f"日本代表戦プレビューを自動生成・公開しました（協会の公式データのみ）。\n{art.title}")
        else:
            tg.send(f"日本代表戦レビューの<b>下書き</b>を作りました（draft）。得点経過の追記が必要です。\n{art.title}")


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="日本代表戦プレビュー/レビュー自動生成")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-notify", action="store_true")
    args = ap.parse_args(argv)
    made = run(dry_run=args.dry_run)
    for kind, art in made:
        print(f"{'(dry) ' if args.dry_run else ''}{kind}: {art.filename()}")
    if not made:
        print("対象なし")
    elif not args.dry_run and not args.no_notify:
        notify(made)
    return 0


if __name__ == "__main__":
    sys.exit(main())
