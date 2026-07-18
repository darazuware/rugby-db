"""P5-6: 高校ラグビー部員名簿スクレイパー（10_YOUTH_AGEGRADE.md 高校スコープ / 02_SCRAPERS.md）。

収集対象校は data/manual/hs_target_schools.json で人手管理する（AIの知識で強豪校を
選定しない）。同ファイルの選定基準は「第105回全国高等学校ラグビーフットボール大会
出場校のうち激戦区18都道府県の代表校」で、出場校一覧の出典（大会公式）URLも同
ファイルに記録している。名簿の取得元は各校ラグビー部の公式サイトのみ
（02: 「大会公式 + 各校/各支部公式の登録名簿」。大会公式サイト側は出場校紹介のみで
選手名簿を公開していないことを 2026-07-19 に実ページで確認したため、各校公式の
部員名簿ページを使う）。

未成年ポリシー（10、絶対）:
  - 高校生は全員 is_minor=true（normalize.player_highschool が設定）
  - 収集するのは 氏名・かな・学年・ポジション のみ。生年月日・身長体重・出身中学・
    SNS・写真は名簿ページに記載があっても収集しない（掲載可フィールド以外は
    収集段階で捨てる）。

実データで確認済みのページ形式（2026-07-19）。_extract_records() はこの4形式を
カバーする汎用行スキャナ:
  - r-cms系（名古屋・関西学院高等部）: かな行→漢字氏名行→学年行。?pageID= で
    ページ送り（本文中のリンクから自動発見）。名古屋は中高一貫の1〜6年生表記
    （grade_scheme="unified6"）で、1〜3年生=中学部員は収集対象外として捨てる。
  - bukatsunavi系（目黒学院）: 漢字氏名行→ポジション行(「PR、LO」)→学年行。
    かな無し。スタッフは氏名直後に肩書行が来る。
  - 学年別ページ系（流経大柏=cp932・御所実業=Wix）: ページ見出しに学年
    （「３年生の選手紹介」等）があり、各選手行は「PR 石村 ビシャル」のような
    ポジション+氏名の複合行、または漢字氏名行+「ポジション WTB FB」行。
    学年はページ見出しから補完する（ソース記載の事実の機械的読み取り）。
  - WordPress系（慶應志木）: 「3年生 /」行→ポジション行→漢字氏名行→かな行。

十分な件数（_MIN_CONFIDENT件）が正規表現で拾えた学校はそのまま採用し、拾えなかった
学校のみ pipeline.llm_fallback.extract_roster_members() に本文プレーンテキストを渡す
（02:「抽出失敗時のみSonnetに粗抽出ブロックだけ渡す」の踏襲）。

roster_urls が空の学校（公式名簿が未公開・JS描画のみ・画像のみ等）は偽データを
作らず warning でスキップして報告に残す（00原則3/5）。
"""
from __future__ import annotations

import re
import time
import unicodedata
from typing import Optional
from urllib.parse import urljoin

from pipeline import io, llm_fallback
from pipeline.scrape.university import _KANA_STOPWORDS  # スタッフ肩書・ポジション名かな（実データ由来）
from pipeline.scrape.university import _get_html  # 同一パッケージ内の共通GETヘルパ
from pipeline.transform import normalize

_SLEEP = 1.5
_MIN_CONFIDENT = 5  # これ未満なら regex 結果を信頼せず LLM フォールバックに回す
_MAX_PAGES = 20  # ?pageID= ページ送りの安全上限

MANUAL_FILE = "hs_target_schools.json"

# --- 抽出用パターン（行は事前に NFKC 正規化される） -------------------------
_POS_TOKENS = ("PR", "HO", "LO", "FL", "NO8", "NO.8", "N8", "SH", "SO", "CTB", "WTB", "FB")
_POS_SPLIT_RE = re.compile(r"[\s/,、・･]+")
_KANA_RE = re.compile(r"^[ぁ-んァ-ヶー\s]{3,20}$")
_KANJI_NAME_RE = re.compile(r"^[一-龥々ヶ]{1,4}[ ][一-龥々ぁ-んァ-ヶー]{1,8}$")
# 「PR 石村 ビシャル」「FL ナモア・フェレティリキ」等のポジション+氏名複合行
_COMBINED_RE = re.compile(
    r"^(?P<pos>(?:PR|HO|LO|FL|NO\.?8|N8|SH|SO|CTB|WTB|FB)(?:[\s/,、・]+(?:PR|HO|LO|FL|NO\.?8|N8|SH|SO|CTB|WTB|FB))*)"
    r"[\s]+(?P<name>[一-龥々ぁ-んァ-ヶー・]{2,12}(?:[\s][一-龥々ぁ-んァ-ヶー・]{1,10})?)$",
    re.I,
)
# 学年: 「3年生」「4年生」（中高一貫は1〜6）。「2025年U17…」等の年号を誤検出しない
# よう、行頭の1桁+「年生」のみ受け付ける（実データ4形式すべてこの表記）。
_GRADE_RE = re.compile(r"^([1-6])\s*年生")
# ページ見出しの学年（流経大柏「３年生の選手紹介」/御所実業「3年生 | …」。NFKC後）
_PAGE_GRADE_RE = re.compile(r"([1-3])年生")
_HEIGHT_RE = re.compile(r"\b1\d{2}\s*cm")
_WEIGHT_RE = re.compile(r"\b\d{2,3}\s*kg")
# 氏名直後（次行〜+3行）にこれらの肩書があればスタッフ/マネージャーとして除外。
# 「主務」「副務」は部員が務める役職のため含めない（実データ: 慶應志木・目黒学院）。
_STAFF_RE = re.compile(
    r"監督|コーチ|スタッフ|マネージャー|顧問|トレーナー|部長|寮監|ドクター|栄養士|先生|アナリスト")
_NAME_STOPWORDS = {"部員 紹介", "部員 一覧", "選手 一覧", "メンバー 紹介", "学年 別", "試合 結果"}

_WINDOW = 4  # かな/学年/ポジション探索の近傍幅
_STAFF_FWD = 3  # スタッフ肩書の前方探索幅（氏名行の後に肩書が来るのを実データで確認）


def _flatten_nfkc(html: str) -> list[str]:
    """HTML -> NFKC正規化済みテキスト行（script/style除去、空行除去）。

    NFKC は全角英数字・全角空白の正規化のみで、漢字・かなの字体は変えない
    （表記の正規化であり事実の変更ではない。migrate_schools と同方針）。
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text("\n")
    out = []
    for l in text.split("\n"):
        s = unicodedata.normalize("NFKC", l)
        # ゼロ幅スペース等の不可視文字を除去（Wixサイトが名前とかなの間に挿入して
        # くるのを実データで確認。残すと空でない偽の行になり近傍探索の距離が狂う）
        s = re.sub("[​‌‍‎‏⁠﻿]", "", s).strip()
        s = re.sub(r"[ \t]+", " ", s)
        if s:
            out.append(s)
    return out


def _parse_pos_line(line: str) -> Optional[str]:
    """「PR、LO」「WTB FB」「ポジション: SH」等の行 -> "PR/LO" 形式。該当なしはNone。"""
    s = line.upper()
    s = re.sub(r"^ポジション[:：]?\s*", "", s)
    if not s:
        return None
    tokens = [t for t in _POS_SPLIT_RE.split(s) if t]
    if not tokens:
        return None
    norm = []
    for t in tokens:
        t = t.replace("NO.8", "NO8").replace("N8", "NO8")
        if t not in _POS_TOKENS and t != "NO8":
            return None
        norm.append("NO8" if t in ("NO8", "NO.8", "N8") else t)
    return "/".join(dict.fromkeys(norm))


def _page_grade(lines: list[str]) -> Optional[int]:
    """ページ見出し（先頭数行）から学年を読む（学年別ページ用フォールバック）。"""
    for l in lines[:5]:
        m = _PAGE_GRADE_RE.search(l)
        if m and "年生" in l and len(l) <= 40:
            return int(m.group(1))
    return None


def _map_grade(g: Optional[int], scheme: str) -> tuple[Optional[int], bool]:
    """生の学年表記 -> (高校の学年1-3 or None, 中学部員として除外すべきか)。"""
    if g is None:
        return None, False
    if scheme == "unified6":
        if 4 <= g <= 6:
            return g - 3, False
        return None, True  # 1-3年生 = 中学部員（収集対象外）
    if 1 <= g <= 3:
        return g, False
    return None, False  # hs スキームで4以上は不明として null（00原則3）


# ひらがな断片のみ結合対象にする（カタカナ行は「リーダー」等の役職語や
# 名古屋のカタカナ読み1行と衝突するため結合しない。実データで確認）
_KANA_FRAG_RE = re.compile(r"^[ぁ-んー ]{1,20}$")


def _merge_kana_fragments(lines: list[str]) -> list[str]:
    """連続するひらがな断片行を1行に結合する（実データ: 御所実業のWixページで
    「おし」「の こたろう」のように1人のかなが複数行に割れているのを確認）。"""
    out: list[str] = []
    for l in lines:
        if out and _KANA_FRAG_RE.match(l) and _KANA_FRAG_RE.match(out[-1]) \
                and len((out[-1] + l).replace(" ", "")) <= 20:
            out[-1] = f"{out[-1]} {l}"
        else:
            out.append(l)
    return out


def _extract_records(lines: list[str], *, scheme: str, direction: str = "after") -> list[dict]:
    """行リストから {kanji, kana, grade(1-3|None), position} を抽出する。

    direction は学年・ポジション行が氏名行の後に来るか（"after"、御所実業・
    関西学院高等部・目黒学院・名古屋・流経大柏で実ページ確認）前に来るか
    （"before"、慶應志木で実ページ確認）のページレイアウト。逆方向の値を拾うと
    隣の選手の値を誤借用する（実データで確認）ため方向を限定する。かな行は
    レイアウトが混在する（名古屋はかなが氏名の前、他は後）ため両方向から
    最近傍を採る。

    信頼度: 学年・ポジションのどちらも無い候補は、身長cm+体重kg が近傍に揃う場合
    （名簿の表組みで学年列が空の行。関西学院高等部で実データ確認）のみ採用する。
    身長体重は信頼度判定にのみ使い、値は収集しない（10: 高校生は身長体重禁止）。
    """
    lines = _merge_kana_fragments(lines)
    page_g = _page_grade(lines)

    def _is_anchor(line: str) -> bool:
        """氏名行（レコードの起点）か。肩書入りの行（「中学部 監督」等、実データで
        氏名パターンに一致する誤検出を確認）は氏名として扱わない。"""
        if _STAFF_RE.search(line):
            return False
        if _COMBINED_RE.match(line):
            return True
        return bool(_KANJI_NAME_RE.match(line)) and line not in _NAME_STOPWORDS

    anchor_idx = {i for i, l in enumerate(lines) if _is_anchor(l)}
    records: list[dict] = []
    for i in sorted(anchor_idx):
        l = lines[i]
        kanji = kana = pos = None
        raw_grade: Optional[int] = None

        cm = _COMBINED_RE.match(l)
        if cm:
            kanji = re.sub(r"\s+", " ", cm.group("name")).strip()
            pos = _parse_pos_line(cm.group("pos"))
            raw_grade = page_g
        else:
            kanji = l

        lo, hi = max(0, i - _WINDOW), min(len(lines), i + _WINDOW + 1)
        window = sorted(range(lo, hi), key=lambda j: abs(j - i))
        has_h = has_w = False
        is_staff = False
        for j in window:
            if j == i:
                continue
            # 別の氏名行を跨いだ先の値は見ない（隣接レコードからの誤借用防止）
            step = 1 if j > i else -1
            if any(k in anchor_idx for k in range(i + step, j, step)):
                continue
            w = lines[j]
            right_dir = (j > i) if direction == "after" else (j < i)
            if i < j <= i + _STAFF_FWD and len(w) <= 14 and _STAFF_RE.search(w):
                is_staff = True
            if raw_grade is None and right_dir:
                gm = _GRADE_RE.match(w)
                if gm:
                    raw_grade = int(gm.group(1))
            if pos is None and right_dir:
                pos = _parse_pos_line(w)
            if (kana is None and _KANA_RE.match(w)
                    and len(w.replace(" ", "")) >= 3
                    and w.replace(" ", "") not in _KANA_STOPWORDS
                    and not _STAFF_RE.search(w)):
                kana = re.sub(r"\s+", "", w)
            if _HEIGHT_RE.search(w):
                has_h = True
            if _WEIGHT_RE.search(w):
                has_w = True
        if is_staff:
            continue
        grade, is_junior = _map_grade(raw_grade, scheme)
        if is_junior:
            continue  # 中高一貫の中学部員は収集対象外（10: 高校スコープ）
        if grade is None and scheme == "hs" and page_g is not None:
            grade = page_g
        if not (grade or pos or (has_h and has_w)):
            continue  # 信頼度不足（00原則3: 迷ったらスキップ）
        records.append({"kanji": kanji, "kana": kana, "grade": grade, "position": pos})

    # 同一氏名の重複統合（流経大柏はポジション別一覧と読み順一覧に同じ選手が
    # 2回現れる）。後続レコードの値で欠損を補完する。
    merged: dict[str, dict] = {}
    for r in records:
        cur = merged.get(r["kanji"])
        if cur is None:
            merged[r["kanji"]] = r
        else:
            for k in ("kana", "grade", "position"):
                if cur[k] is None and r[k] is not None:
                    cur[k] = r[k]
    return list(merged.values())


def _discover_pages(base_url: str, html: str) -> list[str]:
    """r-cms member_list の ?pageID=N リンクを本文から発見する（実データ確認済み）。"""
    ids = sorted({int(m) for m in re.findall(r"\?pageID=(\d+)", html)})
    urls = []
    for n in ids[:_MAX_PAGES]:
        if n <= 1:
            continue
        urls.append(urljoin(base_url, f"?pageID={n}"))
    return urls


def _collect_school(school: dict) -> dict:
    """1校分の名簿収集 -> {records, warnings, used_llm}。"""
    name = school["name"]
    warnings: list[str] = []
    urls: list[str] = list(school.get("roster_urls") or [])
    if not urls:
        note = school.get("note") or "公式名簿ページ未確認"
        warnings.append(f"highschool {name}: 公式の部員名簿ページが無いためスキップ（{note}）")
        return {"records": [], "warnings": warnings, "used_llm": False}

    scheme = school.get("grade_scheme") or "hs"
    direction = school.get("field_direction") or "after"
    all_records: list[dict] = []
    first_text: Optional[str] = None
    seen_urls: set[str] = set()
    queue = list(urls)
    while queue:
        url = queue.pop(0)
        if url in seen_urls or len(seen_urls) >= _MAX_PAGES:
            continue
        seen_urls.add(url)
        html = _get_html(url)
        time.sleep(_SLEEP)
        if html is None:
            warnings.append(f"highschool {name}: {url} 取得失敗（接続不可/404）、当該ページをスキップ")
            continue
        if "member_list" in url:
            for pu in _discover_pages(url, html):
                if pu not in seen_urls:
                    queue.append(pu)
        lines = _flatten_nfkc(html)
        if first_text is None:
            first_text = "\n".join(lines)
        for r in _extract_records(lines, scheme=scheme, direction=direction):
            r["_source_url"] = url
            all_records.append(r)

    used_llm = False
    if len(all_records) < _MIN_CONFIDENT and first_text:
        llm_hits = llm_fallback.extract_roster_members(first_text, f"{name}ラグビー部")
        if llm_hits:
            used_llm = True
            src = urls[0]
            all_records = []
            for h in llm_hits:
                m = re.search(r"([1-6])", h.get("grade") or "")
                grade, is_junior = _map_grade(int(m.group(1)) if m else None, scheme)
                if is_junior:
                    continue
                all_records.append({
                    "kanji": h["name"], "kana": h.get("kana") or None,
                    "grade": grade, "position": h.get("position"),
                    "_source_url": src,
                })
    if not all_records:
        warnings.append(
            f"highschool {name}: 名簿抽出0件（regex/Sonnetいずれも不可。"
            f"JS描画・画像名簿の可能性）、スキップ")
    return {"records": all_records, "warnings": warnings, "used_llm": used_llm}


def _dedupe_players(players: list[dict], warnings: list[str]) -> list[dict]:
    seen: set[str] = set()
    out = []
    for p in players:
        if p["id"] in seen:
            warnings.append(f"highschool: id重複 {p['id']} を検出、2件目以降を除外")
            continue
        seen.add(p["id"])
        out.append(p)
    return out


def collect_all() -> dict:
    """hs_target_schools.json の全対象校を収集する（run.py の league="highschool" 用）。"""
    manual = io.read_manual(MANUAL_FILE, default={})
    schools = manual.get("schools") or []
    warnings: list[str] = []
    players: list[dict] = []
    if not schools:
        warnings.append(f"highschool: data/manual/{MANUAL_FILE} が空/未作成のため収集対象なし")
    for school in schools:
        res = _collect_school(school)
        warnings.extend(res["warnings"])
        for rec in res["records"]:
            player, pw = normalize.player_highschool(
                rec, school_name=school["name"],
                source_url=rec.get("_source_url") or (school.get("roster_urls") or [""])[0])
            warnings.extend(pw)
            if player is not None:
                players.append(player)
    players = _dedupe_players(players, warnings)
    return {"players": players, "teams": [], "matches": [], "standings": [], "warnings": warnings}
