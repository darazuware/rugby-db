"""日本代表戦記事の内部リンク。試合データ(game.php)の全選手を、サイト内の選手ページ/名簿アンカーへ解決する。

- 英語名(協会 english_name) → master選手 → player_links.player_href（個別ページ or チーム名簿アンカー）
- 協会の日本語/カタカナ表記 → URL の対応表を作り、本文の最初の出現だけリンクする（link_first）
- 解決できない選手は平文のまま（誤リンクしない）
"""
from __future__ import annotations

import re
from functools import lru_cache
from typing import Optional

from pipeline import player_links as PL


def _norm(s: str) -> str:
    return " ".join((s or "").upper().replace("-", " ").split())


@lru_cache(maxsize=1)
def _by_en() -> dict[str, Optional[str]]:
    """正規化した英語名 -> href。同名が複数人（別人）なら None（リンクしない）。"""
    cand: dict[str, dict[str, dict]] = {}
    for pid, p in PL.master_players().items():
        en = _norm(p.get("name_en") or "")
        if en:
            cp = PL.master_players().get(PL.canon(pid), p)
            cand.setdefault(en, {})[PL.canon(pid)] = cp
    out: dict[str, Optional[str]] = {}
    for en, ps in cand.items():
        out[en] = PL.player_href(next(iter(ps.values()))) if len(ps) == 1 else None
    return out


def href_for(player: dict) -> Optional[str]:
    return _by_en().get(_norm(player.get("english_name") or ""))


def jp_name(p: dict) -> str:
    return f"{p.get('last_name', '')}{p.get('first_name', '')}".strip()


def name_map(g: dict) -> dict[str, str]:
    """協会表記の氏名 -> href（両チームの登録メンバー全員）。"""
    out: dict[str, str] = {}
    for side in ("home", "away"):
        for e in (g.get("info") or {}).get(f"{side}_entry_list") or []:
            p = e.get("player") or {}
            nm, h = jp_name(p), href_for(p)
            if nm and h:
                out[nm] = h
    return out


_PROTECT = re.compile(r"!?\[[^\]]*\]\([^)]*\)|<[^>]+>|`[^`]*`|https?://\S+")


def link_first(body: str, names: dict[str, str]) -> str:
    """本文(Markdown)の各氏名の最初の出現だけをリンクにする。既存リンク・HTMLタグ内は触らない。
    HTMLブロック内(<details>…)は対象外（タイムライン側で全出現をリンク済み）。"""
    # <details> ブロックは除外して処理
    m = re.search(r"<details class=\"mt\">.*?</details>", body, flags=re.S)
    head, tl, tail = (body[:m.start()], m.group(0), body[m.end():]) if m else (body, "", "")

    def process(text: str) -> str:
        for nm in sorted(names, key=len, reverse=True):
            spans = [(x.start(), x.end()) for x in _PROTECT.finditer(text)]
            for hit in re.finditer(re.escape(nm), text):
                if any(s <= hit.start() < e for s, e in spans):
                    continue
                text = text[:hit.start()] + f"[{nm}]({names[nm]})" + text[hit.end():]
                break
        return text

    return process(head) + tl + process(tail)
