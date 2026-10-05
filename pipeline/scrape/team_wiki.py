"""チームの創設年・本拠地・主なタイトル歴を Wikipedia（MediaWiki API）から取得する。

出力は data/manual/team_facts.json（チームid → 値＋出典URL）。master への適用は
pipeline/team_facts.py が行う（この取得処理は master を書かない）。

方針（03_VALIDATION 準拠）:
- 値は全てページ本文（infobox / Honours・タイトル節）から機械抽出し、AIの知識で補わない。
- 出典URLは版固定の permalink（index.php?title=...&oldid=REVID）で各値に保持する。
- 曖昧なもの（創設年が複数併記、本拠地に期間注記つき、回数と年の数が不一致）は捨てる。
- 7人制・リザーブ・地域カップ等の小区分は「主なタイトル」から除外する。

実行: python3.11 -m pipeline.scrape.team_wiki
"""
from __future__ import annotations

import re
import time
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import quote

import requests

from pipeline import io

JST = timezone(timedelta(hours=9))
_HEADERS = {"User-Agent": "rugbypicks-bot/1.0 (team facts; https://rugbypicks.com)"}
OUTPUT = "team_facts.json"

# master のチーム id → Wikipedia ページ（言語:タイトル）。対応付けの同定のみで、値は含まない。
# 2026-10-05 に infobox のリーグ欄が各リーグと一致することを確認済み。
WIKI_PAGES: dict[str, str] = {
    # リーグワン D1
    "lo_team_97": "ja:クボタスピアーズ船橋・東京ベイ", "lo_team_98": "ja:静岡ブルーレヴズ",
    "lo_team_99": "ja:東京サントリーサンゴリアス", "lo_team_100": "ja:浦安D-Rocks",
    "lo_team_101": "ja:コベルコ神戸スティーラーズ", "lo_team_102": "ja:埼玉パナソニックワイルドナイツ",
    "lo_team_103": "ja:東芝ブレイブルーパス東京", "lo_team_104": "ja:トヨタヴェルブリッツ",
    "lo_team_105": "ja:三重ホンダヒート", "lo_team_106": "ja:三菱重工相模原ダイナボアーズ",
    "lo_team_107": "ja:横浜キヤノンイーグルス", "lo_team_108": "ja:リコーブラックラムズ東京",
    # リーグワン D2
    "lo_team_109": "ja:NECグリーンロケッツ東葛", "lo_team_110": "ja:九州電力キューデンヴォルテクス",
    "lo_team_111": "ja:清水建設江東ブルーシャークス", "lo_team_112": "ja:豊田自動織機シャトルズ愛知",
    "lo_team_113": "ja:日本製鉄釜石シーウェイブス", "lo_team_114": "ja:花園近鉄ライナーズ",
    "lo_team_115": "ja:日野レッドドルフィンズ", "lo_team_116": "ja:レッドハリケーンズ大阪",
    # リーグワン D3
    "lo_team_117": "ja:クリタウォーターガッシュ昭島", "lo_team_118": "ja:狭山セコムラガッツ",
    "lo_team_119": "ja:中国電力レッドレグリオンズ", "lo_team_120": "ja:マツダスカイアクティブズ広島",
    "lo_team_121": "ja:ヤクルトレビンズ戸田", "lo_team_122": "ja:ルリーロ福岡",
    # Top14
    "bayonne": "en:Aviron Bayonnais", "bordeaux": "en:Union Bordeaux Bègles",
    "castres": "en:Castres Olympique", "clermont": "en:ASM Clermont Auvergne",
    "la-rochelle": "en:Stade Rochelais", "lyon": "en:Lyon OU", "montpellier": "en:Montpellier Hérault Rugby",
    "paris": "en:Stade Français", "pau": "en:Section Paloise", "perpignan": "en:USA Perpignan",
    "racing-92": "en:Racing 92", "toulon": "en:RC Toulon", "toulouse": "en:Stade Toulousain",
    "vannes": "en:RC Vannes",
    # Premiership
    "bath": "en:Bath Rugby", "bristol": "en:Bristol Bears", "exeter": "en:Exeter Chiefs",
    "gloucester": "en:Gloucester Rugby", "harlequins": "en:Harlequin F.C.",
    "leicester": "en:Leicester Tigers", "newcastle": "en:Newcastle Red Bulls",
    "northampton": "en:Northampton Saints", "sale": "en:Sale Sharks", "saracens": "en:Saracens F.C.",
    # URC
    "benetton": "en:Benetton Rugby", "bulls": "en:Bulls (rugby union)", "cardiff": "en:Cardiff Rugby",
    "connacht": "en:Connacht Rugby", "dragons": "en:Dragons RFC", "edinburgh": "en:Edinburgh Rugby",
    "glasgow": "en:Glasgow Warriors", "leinster": "en:Leinster Rugby",
    "lions": "en:Lions (United Rugby Championship)", "munster": "en:Munster Rugby",
    "ospreys": "en:Ospreys (rugby union)", "scarlets": "en:Scarlets", "sharks": "en:Sharks (rugby union)",
    "stormers": "en:Stormers", "ulster": "en:Ulster Rugby", "zebre": "en:Zebre Parma",
    # Super Rugby
    "blues": "en:Blues (Super Rugby)", "brumbies": "en:ACT Brumbies", "chiefs": "en:Chiefs (rugby union)",
    "crusaders": "en:Crusaders (rugby union)", "fijian-drua": "en:Fijian Drua",
    "highlanders": "en:Highlanders (rugby union)", "hurricanes": "en:Hurricanes (rugby union)",
    "moana-pasifika": "en:Moana Pasifika", "reds": "en:Queensland Reds",
    "waratahs": "en:New South Wales Waratahs", "western-force": "en:Western Force",
}

# Wikipedia 側が改称後の名称（例: 三重→栃木ホンダヒート）にリダイレクトされるチーム。
# 本拠地が移転済み・移転予定の記述になっている可能性があり master（league-one.jp）と
# 時点がずれうるため、本拠地スタジアムは採用しない（創設年・タイトル歴は同一クラブとして採用）。
STADIUM_SKIP = {"lo_team_103", "lo_team_105", "lo_team_109", "lo_team_118"}

_EXCLUDE_SECTION = re.compile(
    r"reserve|united|sevens|7s\b|women|academy|local|friendly|youth|under|a team|other|minor|"
    r"10s\b|tens\b|7人制|その他|女子|ジュニア", re.I)
_EXCLUDE_COMP = re.compile(
    r"sevens|7s\b|10s\b|tens\b|7人制|seven|county|counties|senior cup|junior cup|tiers? \d|"
    r"premiership rugby shield|merit table|masters|derbies", re.I)


# --------------------------------------------------------------------------
# 取得
# --------------------------------------------------------------------------

def fetch_pages(pages: dict[str, str]) -> dict[str, dict]:
    """{team_id: 'lang:title'} → {team_id: {lang,title,revid,text}}（20件ずつ一括取得）。"""
    out: dict[str, dict] = {}
    for lang in ("ja", "en"):
        items = {v.split(":", 1)[1]: k for k, v in pages.items() if v.startswith(lang + ":")}
        titles = list(items)
        for i in range(0, len(titles), 20):
            chunk = titles[i:i + 20]
            resp = None
            for attempt in range(5):
                resp = requests.get(
                    f"https://{lang}.wikipedia.org/w/api.php",
                    params=dict(action="query", prop="revisions", rvprop="content|ids",
                                rvslots="main", format="json", formatversion=2,
                                redirects=1, titles="|".join(chunk)),
                    headers=_HEADERS, timeout=30)
                if resp.status_code == 200 and resp.text.startswith("{"):
                    break
                time.sleep(10 * (attempt + 1))
            q = resp.json()["query"]
            back: dict[str, str] = {}
            for n in q.get("normalized", []):
                back[n["to"]] = n["from"]
            for n in q.get("redirects", []):
                back[n["to"]] = back.get(n["from"], n["from"])
            for p in q["pages"]:
                tid = items.get(back.get(p["title"], p["title"]))
                if tid is None or "missing" in p:
                    continue
                rev = p["revisions"][0]
                out[tid] = {"lang": lang, "title": p["title"], "revid": rev["revid"],
                            "text": rev["slots"]["main"]["content"]}
            time.sleep(2)
    return out


def permalink(lang: str, title: str, revid: int) -> str:
    return (f"https://{lang}.wikipedia.org/w/index.php?"
            f"title={quote(title.replace(' ', '_'))}&oldid={revid}")


# --------------------------------------------------------------------------
# wikitext 整形
# --------------------------------------------------------------------------

def _strip_templates(s: str, names: tuple[str, ...]) -> str:
    """{{name ...}}（入れ子対応）を除去。"""
    out, i = [], 0
    low = s.lower()
    while i < len(s):
        if s.startswith("{{", i) and any(low.startswith("{{" + n, i) for n in names):
            depth, j = 0, i
            while j < len(s):
                if s.startswith("{{", j):
                    depth += 1; j += 2; continue
                if s.startswith("}}", j):
                    depth -= 1; j += 2
                    if depth == 0:
                        break
                    continue
                j += 1
            i = j
            continue
        out.append(s[i]); i += 1
    return "".join(out)


def clean(s: str) -> str:
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<ref[^>]*/>", "", s)
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = _strip_templates(s, ("efn", "refn", "cite", "sfn", "flagicon", "flag"))
    s = re.sub(r"\{\{\s*(?:nowrap|nobr|small)\s*\|(.*?)\}\}", r"\1", s, flags=re.S | re.I)
    s = re.sub(r"\{\{\s*start date(?: and age)?\s*\|([^}]*)\}\}",
               lambda m: next((x for x in m.group(1).split("|") if re.fullmatch(r"\s*\d{4}\s*", x)), ""),
               s, flags=re.I)
    s = re.sub(r"\[\[(?:File|Image|ファイル|画像):[^\]]*\]\]", "", s)
    s = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[https?://\S+\s([^\]]*)\]", r"\1", s)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</?(?:small|span|sup|b|i)[^>]*>", "", s)
    s = s.replace("'''", "").replace("''", "")
    return s.strip()


def infobox(text: str) -> dict[str, str]:
    m = re.search(r"\{\{\s*(?:Infobox[^|\n]*|ラグビーチーム)", text)
    if not m:
        return {}
    depth, j = 0, m.start()
    while j < len(text):
        if text.startswith("{{", j):
            depth += 1; j += 2; continue
        if text.startswith("}}", j):
            depth -= 1; j += 2
            if depth == 0:
                break
            continue
        j += 1
    body = text[m.start() + 2:j - 2]
    parts, depth, cur, k = [], 0, "", 0
    while k < len(body):
        two = body[k:k + 2]
        if two in ("{{", "[["):
            depth += 1; cur += two; k += 2; continue
        if two in ("}}", "]]"):
            depth -= 1; cur += two; k += 2; continue
        if body[k] == "|" and depth == 0:
            parts.append(cur); cur = ""; k += 1; continue
        cur += body[k]; k += 1
    parts.append(cur)
    out = {}
    for p in parts[1:]:
        if "=" in p:
            a, b = p.split("=", 1)
            out[a.strip()] = b.strip()
    return out


# --------------------------------------------------------------------------
# 項目抽出
# --------------------------------------------------------------------------

def parse_founded(ib: dict[str, str]) -> Optional[int]:
    raw = ib.get("founded") or ib.get("創設") or ib.get("設立")
    if not raw:
        return None
    years = set(re.findall(r"(?<!\d)(1[89]\d{2}|20[0-2]\d)(?!\d)", clean(raw)))
    return int(years.pop()) if len(years) == 1 else None  # 複数併記は曖昧として捨てる


def parse_stadiums(ib: dict[str, str]) -> list[str]:
    raw = ib.get("ground") or ib.get("ホームスタジアム")
    if not raw:
        return []
    names = []
    for line in clean(raw).split("\n"):
        line = re.sub(r"^(?:main|secondary) ground\s*:\s*", "", line.strip(), flags=re.I)
        line = re.sub(r"\s*\([^)]*(?:capacity|収容)[^)]*\)?", "", line, flags=re.I)
        if re.search(r"\(\s*\d{4}", line):
            return []  # 期間注記つき（移転中）は時点が曖昧なため不採用
        line = re.split(r",\s|、", line)[0].strip(" ()")
        if not line or not re.search(r"[A-Za-z぀-ヿ一-鿿]", line) or line[0].isdigit():
            continue
        if line.lower().startswith(("c.", "capacity")):
            continue
        names.append(line)
    return names


def parse_location(ib: dict[str, str]) -> Optional[str]:
    raw = ib.get("location")
    if not raw:
        return None
    s = re.sub(r"\s+", " ", clean(raw).replace("\n", " ")).strip(" ,")
    return s or None


_SEASON = re.compile(r"(?<!\d)(1[89]\d{2}|20[0-2]\d)(?:\s*[–\-/]\s*(\d{2,4}))?(?!\d)")
_EN_RESULT = re.compile(r"^(?:champions|winners)\s*[:：]?\s*\(?\s*(\d{1,3}(?!\d))?\s*\)?\s*[:：]?\s*(.*)$", re.I)
# 「* '''Champions (13)'''」「* '''Super Rugby Aotearoa Champions (2)'''」形式（年は同じ行の後ろか次の行）
_EN_BULLET = re.compile(r"^(.*?)\s*(?:champions|winners?)\s*\((\d{1,3})\)\s*:?\s*(.*)$", re.I)
_JA_RESULT = re.compile(r"(?<!準)優勝\s*[：:]\s*(\d+)\s*回\s*[（(](.*)[）)]")


def _seasons(s: str) -> list[str]:
    out = []
    for m in _SEASON.finditer(s):
        out.append(m.group(0).replace(" ", ""))
    return out


def _honours_section(text: str, lang: str) -> Optional[str]:
    names = (r"タイトル|主なタイトル|獲得タイトル" if lang == "ja"
             else r"Honours|Club honours|Honors|Club honors")
    m = re.search(r"^(==+)\s*(?:%s)\s*\1\s*$" % names, text, re.M)
    if not m:
        return None
    lvl = len(m.group(1))
    rest = text[m.end():]
    e = re.search(r"^={2,%d}[^=].*?=+\s*$" % lvl, rest, re.M)
    return rest[:e.start()] if e else rest


def _make(comp: str, count: Optional[int], tail: str) -> Optional[dict]:
    comp = re.sub(r"\s*\((?:\d{1,3}|founded[^)]*)\)\s*$", "", clean(comp).replace(":", ""))
    comp = re.sub(r"\s+", " ", comp).strip(" :：-–")
    if not comp or _EXCLUDE_COMP.search(comp):
        return None
    seasons = _seasons(clean(tail))
    if count is None:
        count = len(seasons) or None
    if not count:
        return None
    if seasons and len(seasons) != count:
        return None  # 回数と年の数が不一致（両チーム優勝の注記・抽出漏れ等）→ 曖昧として捨てる
    return {"competition": comp, "count": count, "seasons": seasons}


_ATTR = re.compile(r'^\s*(?:[a-z\-]+\s*=\s*(?:"[^"]*"|[^\s|]+)\s*)+\|(?!\|)', re.I)


def _cells(line: str, sep: str) -> list[str]:
    out = []
    for c in line[1:].split(sep * 2):
        out.append(_ATTR.sub("", c).strip())
    return out


def _parse_table(block: str) -> list[dict]:
    """wikitable（列: Competition / Titles|Winners|Championships / Season(s) ...）。"""
    out: list[dict] = []
    cols: list[str] = []
    for row in re.split(r"\n\|-[^\n]*", block):
        lines = [ln.strip() for ln in row.strip().split("\n") if ln.strip()]
        lines = [ln for ln in lines if not ln.startswith(("{|", "|}", "|+"))]
        if not lines:
            continue
        if all(ln.startswith("!") for ln in lines):
            hdr = [c for ln in lines for c in _cells(ln, "!")]
            if any(re.search(r"competition", clean(h), re.I) for h in hdr):
                cols = [clean(h) for h in hdr]
            continue
        if not cols:
            continue
        cells = [c for ln in lines if ln.startswith("|") for c in _cells(ln, "|")]
        if len(cells) != len(cols):
            continue
        ci = next((i for i, h in enumerate(cols) if re.search(r"competition", h, re.I)), None)
        wi = next((i for i, h in enumerate(cols)
                   if re.search(r"^(?:titles?(?: won)?|winners?|championships)$", h, re.I)), None)
        if ci is None or wi is None:
            continue
        win = clean(cells[wi])
        tail = win
        count = None
        m = re.match(r"^\(?\s*(\d{1,3})(?!\d)\s*\)?\s*(.*)$", win, re.S)
        if m:
            count, tail = int(m.group(1)), m.group(2)
            if count == 0:
                continue
            if not tail.strip() and wi + 1 < len(cols) and re.search(r"season", cols[wi + 1], re.I):
                tail = cells[wi + 1]
        t = _make(cells[ci], count, tail)
        if t:
            out.append(t)
    return out


def parse_titles(text: str, lang: str) -> list[dict]:
    sec = _honours_section(text, lang)
    if not sec:
        return []
    titles: list[dict] = []
    for tbl in re.findall(r"\{\|.*?\n\|\}", sec, re.S):
        titles.extend(_parse_table(tbl))
    sec = re.sub(r"\{\|.*?\n\|\}", "", sec, flags=re.S)

    def add(c: Optional[str], n: Optional[int], tail: str) -> None:
        t = _make(c or "", n, tail)
        if t:
            titles.append(t)

    skip = False
    heading: Optional[str] = None   # 直近の見出し（=== X === / '''X'''）
    comp: Optional[str] = None      # 直近の「* 大会名」行
    pending: Optional[tuple[str, int]] = None  # 年が次行に来る「* Champions (n)」
    for raw in sec.split("\n"):
        line = raw.strip().lstrip(":").strip()
        if not line or line.startswith(("{{col", "[[File", "[[ファイル")):
            continue
        if pending and not line.startswith(("*", "=", "'''")):
            add(pending[0], pending[1], line)
            pending = None
            continue
        pending = None
        h = re.match(r"^=+\s*(.*?)\s*=+$", line) or re.match(r"^(?:'''(.+?)'''|;(.+))\s*(?:-.*)?$", line)
        if h:
            name = clean(next(g for g in h.groups() if g))
            skip = bool(_EXCLUDE_SECTION.search(name))
            heading, comp = name, None
            continue
        if skip:
            continue
        if line.startswith("*") and not line.startswith("**"):
            body = clean(line.lstrip("*").strip())
            if lang == "ja":
                jm = _JA_RESULT.search(body)
                if jm:
                    add(body[:jm.start()], int(jm.group(1)), jm.group(2))
                    comp = None
                else:
                    comp = body
                continue
            bm = _EN_BULLET.match(body)
            if bm:  # 「* [X] Champions (n) [年...]」
                c = bm.group(1).strip(" :") or heading
                if bm.group(3).strip():
                    add(c, int(bm.group(2)), bm.group(3))
                elif c:
                    pending = (c, int(bm.group(2)))
                comp = None
                continue
            dm = re.match(r"^(.*?)\s+[–-]\s+(.*\d{4}.*)$", body)
            if dm and not re.search(r"runner|semi|final|third", dm.group(2), re.I):
                # 「* [[X]] (2) – 2009–10, 2017–18」形式（準優勝等の注記がある行は除外）
                cm = re.match(r"^(.*?)\s*\((\d{1,3})\)\s*$", dm.group(1))
                if cm:
                    add(cm.group(1), int(cm.group(2)), dm.group(2))
                else:
                    add(dm.group(1), None, dm.group(2))
                comp = None
                continue
            em = re.search(r"^(.*?)[:：]\s*((?:champions|winners)\b.*)$", body, re.I)
            if em:  # 「* [[X]]: Champions (n) ...」
                r = _EN_RESULT.match(em.group(2))
                if r:
                    add(em.group(1), int(r.group(1)) if r.group(1) else None, r.group(2))
                comp = None
                continue
            comp = body
            continue
        if line.startswith("**") and comp:
            body = clean(line.lstrip("*").strip())
            if lang == "ja":
                jm = _JA_RESULT.search(body)
                if jm:
                    add(comp, int(jm.group(1)), jm.group(2))
            else:
                r = _EN_RESULT.match(body)
                if r:
                    add(comp, int(r.group(1)) if r.group(1) else None, r.group(2))
    # 同一大会の重複行は最初のものを採用
    seen, uniq = set(), []
    for t in titles:
        if t["competition"] not in seen:
            seen.add(t["competition"]); uniq.append(t)
    return uniq


def build_facts(pages: dict[str, dict]) -> dict[str, dict]:
    facts: dict[str, dict] = {}
    for tid, p in sorted(pages.items()):
        url = permalink(p["lang"], p["title"], p["revid"])
        ib = infobox(p["text"])
        entry: dict = {"wiki_title": p["title"], "source_url": url}
        founded = parse_founded(ib)
        if founded:
            entry["founded"] = {"value": founded, "source_url": url}
        if p["lang"] == "en":  # リーグワンの home_area は league-one.jp 由来の値が既にある
            loc = parse_location(ib)
            if loc:
                entry["home_area"] = {"value": loc, "source_url": url}
        if tid not in STADIUM_SKIP:
            st = parse_stadiums(ib)
            if st:
                entry["home_stadiums"] = [{"name": n, "source_url": url} for n in st]
        titles = parse_titles(p["text"], p["lang"])
        if titles:
            entry["titles"] = [dict(t, source_url=url) for t in titles]
        facts[tid] = entry
    return facts


def main() -> int:
    pages = fetch_pages(WIKI_PAGES)
    facts = build_facts(pages)
    missing = sorted(set(WIKI_PAGES) - set(pages))
    io.write_json(io.MANUAL_DIR / OUTPUT, {
        "_note": "pipeline/scrape/team_wiki.py が Wikipedia から機械抽出。手で値を足さないこと。",
        "fetched_at": datetime.now(JST).isoformat(timespec="seconds"),
        "teams": facts,
    })
    print(f"team_facts: {len(facts)} チーム取得 / 未取得 {missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
