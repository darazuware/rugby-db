"""JRFU 代表戦日程スクレイパー（02: 「JRFU（jrfu.jp）」日本代表の試合日程・会場）。

02 は "jrfu.jp" と表記するが、その名前は解決不可能（実在しないドメイン）。
日本代表応援サイトの実ドメインは www.rugby-japan.jp（2026-07-18 に実ページで確認、
schemas.ALLOWED_DOMAINS に追加済み）。

試合一覧の索引は www.rugby-japan.jp/braveblossoms/ が読み込む静的JSON
（S3ホスト。rugby-japan.jp ドメイン外のため source_url には使わず、match_id の
列挙にのみ使う）から取得する。各試合の詳細（開催日時・会場・スコア・ステータス）
は同ドメイン自身のAPI /v1.0/game.php?game_id={id} から取得する（これは
公式サイト自身が提供するエンドポイントで rugby-japan.jp ドメイン内）。

公開関数:
    collect_matches(year=None) -> {"matches": [...], "opponent_slugs": [...], "warnings": [...]}
      opponent_slugs は all.rugby のクラブslug相当（02: national.json のスコッド
      取得対象国の絞り込みに scrape.all_rugby.collect_national() が使う）。
"""
from __future__ import annotations

import time
from typing import Optional

import requests

from pipeline.transform import normalize

BASE = "https://www.rugby-japan.jp"
# 試合一覧の索引用JSON（S3配信、rugby-japan.jp ドメイン外なので source_url には使わない）。
_SCHEDULE_INDEX_URL = (
    "https://rugby-japan.s3.ap-northeast-1.amazonaws.com/"
    "static-assets/wbb/js/data/match-schedule.json"
)
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
_SLEEP = 1.5
_TIMEOUT = 15
_RETRIES = 2

# JRFU上のチーム表記 → all.rugby クラブslug相当（実ページで確認、2026-07-18時点の
# 15人制男子代表スケジュールに登場する範囲のみ登録。原則3: 未登録表記は突合しない）。
TEAM_SLUGS = {
    "日本代表": "japan",
    "JAPAN XV": "japan-xv",
    "フランス代表": "france",
    "イタリア代表": "italy",
    "アイルランド代表": "ireland",
    "オーストラリア代表": "australia",
    "カナダ代表": "canada",
    "スコットランド代表": "scotland",
    "マオリ・オールブラックス": "maori-all-blacks",
}
# JAPAN XV・マオリ・オールブラックスは主権国代表ではないため、
# national.json のスコッド取得対象（対戦"国"）からは除外する（02）。
NON_COUNTRY_SLUGS = {"japan-xv", "maori-all-blacks"}
_JAPAN_SIDE_NAMES = {"日本代表", "JAPAN XV"}


def _get_json(url: str) -> Optional[object]:
    """GET→JSON（timeout=15、指数バックオフ最大2回、失敗はNone）。"""
    delay = 1.0
    for attempt in range(_RETRIES + 1):
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            if attempt >= _RETRIES:
                return None
            time.sleep(delay)
            delay *= 2
    return None


def process_entry(entry: dict, g: dict) -> tuple[Optional[dict], Optional[str], list[str]]:
    """索引1件(entry) + game.php詳細(g) → (Match dict|None, 対戦国slug|None, warnings)。

    ネットワークを伴わない純粋関数（テスト容易性のため collect_matches から分離）。
    対戦国slug は home が日本側（日本代表/JAPAN XV）なら away 側、そうでなければ
    home 側を採用する。NON_COUNTRY_SLUGS（JAPAN XV・マオリ・オールブラックス）は
    「対戦国」としては返さない（02の絞り込み対象外）。
    """
    game_id = entry.get("id")
    home_raw = (entry.get("home") or "").strip()
    away_raw = (entry.get("away") or "").strip()
    home_slug = TEAM_SLUGS.get(home_raw)
    away_slug = TEAM_SLUGS.get(away_raw)
    if home_slug is None or away_slug is None:
        return None, None, [
            f"jrfu: game_id={game_id} の未登録チーム表記 home={home_raw!r} "
            f"away={away_raw!r} のためスキップ"]

    opp_slug = away_slug if home_raw in _JAPAN_SIDE_NAMES else home_slug
    opponent = opp_slug if opp_slug not in NON_COUNTRY_SLUGS else None

    match, warnings = normalize.match_jrfu(g, home_slug=home_slug, away_slug=away_slug, game_id=game_id)
    return match, opponent, warnings


def collect_matches(year: Optional[int] = None) -> dict:
    """試合索引→詳細を辿って Match レコードと対戦国スラッグ一覧を組み立てる。

    year は現状未使用（索引JSONが常に直近シーズン分のみを返すため）。
    将来的にシーズンを跨いだ絞り込みが必要になった場合に備えて引数だけ残す。
    """
    warnings: list[str] = []
    index = _get_json(_SCHEDULE_INDEX_URL)
    if not isinstance(index, list):
        warnings.append("jrfu: 試合スケジュール索引の取得失敗")
        return {"matches": [], "opponent_slugs": [], "warnings": warnings}

    matches_out: list[dict] = []
    opponent_slugs: list[str] = []
    seen_opponents: set[str] = set()

    for entry in index:
        game_id = entry.get("id")
        if not game_id:
            continue
        detail = _get_json(f"{BASE}/v1.0/game.php?game_id={game_id}")
        time.sleep(_SLEEP)
        game_list = detail.get("game_list") if isinstance(detail, dict) else None
        if not game_list:
            warnings.append(f"jrfu: game_id={game_id} 詳細取得失敗、スキップ")
            continue

        match, opponent, ew = process_entry(entry, game_list[0])
        warnings.extend(ew)
        if match is not None:
            matches_out.append(match)
        if opponent is not None and opponent not in seen_opponents:
            seen_opponents.add(opponent)
            opponent_slugs.append(opponent)

    return {"matches": matches_out, "opponent_slugs": opponent_slugs, "warnings": warnings}
