"""学校名文字列 -> "hs"（高校相当）/"univ"（大学相当）のローカル分類器。

llm_fallback.classify_school_names() は ANTHROPIC_API_KEY が無いと常に空を返すため、
API に依存せず判定できる分だけをここで吸収する。判定するのは「この学校名表記が
高校相当か大学相当か」だけで、学校名そのものの補完・創作は行わない
（03_VALIDATION.md / llm_fallback.py と同方針）。判断できない表記は None を返し、
呼び出し側が warning を積む（00原則3: 不明はnull）。

海外表記の扱い:
    NZ/豪/南ア/フィジー/トンガ等の "College" は中等教育（日本の高校相当）を指すため
    hs に分類する。"University"/"大学" のみ univ。判断に迷う表記（例: "WesternSydney"）
    は None のまま残す。
"""
from __future__ import annotations

import re
from typing import Optional

# 末尾の「（日本語訳・国名等）」括弧はサフィックス判定の邪魔になるので判定時のみ除去。
_TRAILING_PAREN_RE = re.compile(r"[（(][^）)]*[）)]?\s*$")

# league-one.jp / rugby-japan.jp の表記ゆれで規則化しづらいものだけを明示。
_EXPLICIT: dict[str, str] = {
    "常翔学園": "hs",
    "目黒学院": "hs",
    "石見智翠館": "hs",
    "日本航空石川": "hs",
    "日本航空高校石川": "hs",
    "日本航空高等学校石川": "hs",
    "大阪朝鮮高級学校": "hs",
    "東京朝鮮中高級学校": "hs",
    "PalmerstonNorthBoys": "hs",
    "OtagoBoysH.S.": "hs",
    "PaarlGymnasium": "hs",
    "FalstedSchool": "hs",
    "OakhamSchool": "hs",
    "SwamiVivekanadaCallege": "hs",
    "伏見工業": "hs",
    "御所実業": "hs",
    "荒尾": "hs",
    "ケルストンボーイズ": "hs",
}

# 高校相当を示す語（英語・カタカナ）。College は海外中等教育を指すため hs。
_HS_TOKENS = (
    r"high\s*school",
    r"grammar",
    r"boys\s*h\.?\s*s\.?",
    r"boys\s*high",
    r"collegiate\s*school",
    r"c[ao]llege",
    r"gymnasium",
    r"hoerskool",
    r"hoërskool",
    r"memorial\s*school",
    r"secondary\s*school",
)
_HS_EN_RE = re.compile(r"(?:%s)" % "|".join(_HS_TOKENS), re.IGNORECASE)
_HS_KANA_RE = re.compile(r"(カレッジ|ハイスクール|グラマースクール|スクール|ジムナジアム)")
_HS_JA_RE = re.compile(r"(高等学校|高等科|高等部|高校|高級学校|高級校|中等教育学校|高$)")

_UNIV_EN_RE = re.compile(r"(university|universit|univ\.?)", re.IGNORECASE)
_UNIV_JA_RE = re.compile(r"(大学校|大学|大$)")
_UNIV_KANA_RE = re.compile(r"(ユニバーシティ)")


def classify(name: str) -> Optional[str]:
    """学校名表記 -> "hs"/"univ"/None。判断できない表記は None。"""
    if not name:
        return None
    s = name.strip()
    for key in (s, s.replace(" ", "")):
        if key in _EXPLICIT:
            return _EXPLICIT[key]
    # 括弧内の日本語訳に「高校/大学」が入る表記（例: "TheSouthportSchool（サウスポート高校）"）
    if _HS_JA_RE.search(s) and not _UNIV_JA_RE.search(s):
        return "hs"
    s = _TRAILING_PAREN_RE.sub("", s).strip()
    for key in (s, s.replace(" ", "")):
        if key in _EXPLICIT:
            return _EXPLICIT[key]
    # 大学表記が含まれていれば univ を優先（"UniversityofPretoria（プレトリ" 等の途中切れ対応）
    if _UNIV_EN_RE.search(s) or _UNIV_JA_RE.search(s) or _UNIV_KANA_RE.search(s):
        return "univ"
    if _HS_EN_RE.search(s) or _HS_KANA_RE.search(s) or _HS_JA_RE.search(s):
        return "hs"
    return None


def classify_all(names: list[str]) -> dict[str, str]:
    """名前リスト -> 判定できたものだけの dict（llm_fallback と同じ戻り値形式）。"""
    out: dict[str, str] = {}
    for n in names:
        t = classify(n)
        if t is not None:
            out[n] = t
    return out
