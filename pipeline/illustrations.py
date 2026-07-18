"""P4-4: AIイラスト「生成待ちリスト」の自動管理（06 ②）。

    python3 -m pipeline.illustrations

対象: is_featured かつ Instagram 未登録（data/manual/instagram_accounts.json に無い）
かつ 完成イラストが未配置（public/illustrations/{player_id}.webp が無い）の選手。
data/master は読み取りのみ。出力は data/manual/illustrations_todo.json（human/Antigravity が
画像生成に使うプロンプト付きリスト）。イラスト画像自体の生成はスコープ外（06）。

実在選手の顔に似せる指定は禁止（肖像権リスク）。プロンプトは「ポジション・体格・
チームカラーの汎用イラスト」のみを指示する文言に固定する（06）。
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

from pipeline import io
from pipeline.schemas import LEAGUE_KEYS, TEAM_LEAGUES

ILLUSTRATIONS_DIR = io.REPO_ROOT / "public" / "illustrations"
TODO_PATH = io.MANUAL_DIR / "illustrations_todo.json"

PROMPT_TEMPLATE = (
    "ラグビー選手のフラットなベクター風イラスト、{position}、"
    "ユニフォームは{team_color}、顔は特定人物に似せない、背景単色"
)

# positions.ts (04) の対訳表のうち、イラスト指示に使う体格・役割の短い日本語表現のみ。
# 対訳表に無いポジションコードはそのまま使う（事実の書き換え禁止）。
POSITION_JA: dict[str, str] = {
    "PR": "プロップ", "LH": "プロップ", "TH": "プロップ",
    "HO": "フッカー",
    "LO": "ロック", "SR": "ロック",
    "FL": "フランカー", "BR": "バックロー",
    "No8": "ナンバーエイト", "N8": "ナンバーエイト", "NO8": "ナンバーエイト",
    "SH": "スクラムハーフ", "HB": "スクラムハーフ",
    "SO": "スタンドオフ", "FH": "スタンドオフ",
    "CTB": "センター", "CE": "センター", "IC": "インサイドセンター", "OC": "アウトサイドセンター",
    "WTB": "ウィング", "WG": "ウィング",
    "FB": "フルバック", "FBK": "フルバック",
    "UTB": "ユーティリティバック",
}


def position_label(position: Optional[str]) -> Optional[str]:
    if not position:
        return None
    code = position.strip()
    if not code:
        return None
    return POSITION_JA.get(code, code)


def _load_all_players() -> list[dict]:
    players: list[dict] = []
    for league in sorted(LEAGUE_KEYS):
        players.extend(io.read_records(io.players_path(league)))
    return players


def _load_team_colors() -> dict[str, dict]:
    """team_id -> colors（primary優先、無ければ最初の値）。league-one等は colors={} の場合が多い。"""
    teams_by_id: dict[str, dict] = {}
    for league in sorted(TEAM_LEAGUES):
        for t in io.read_records(io.teams_path(league)):
            teams_by_id[t["id"]] = t
    return teams_by_id


def team_color_hex(team: Optional[dict]) -> Optional[str]:
    if not team:
        return None
    colors = team.get("colors") or {}
    return colors.get("primary") or colors.get("main") or (next(iter(colors.values()), None))


def illustration_exists(player_id: str) -> bool:
    return (ILLUSTRATIONS_DIR / f"{player_id}.webp").exists()


def build_todo_items(
    players: list[dict],
    *,
    instagram_accounts: dict,
    teams_by_id: dict[str, dict],
    illustration_check=illustration_exists,
) -> list[dict]:
    """is_featured かつ Instagram未登録かつイラスト未配置の選手 → todoエントリ一覧（id昇順）。"""
    items: list[dict] = []
    for p in players:
        if not p.get("is_featured"):
            continue
        pid = p["id"]
        if pid in instagram_accounts:
            continue
        if illustration_check(pid):
            continue

        name = p.get("name_ja") or p.get("name_en")
        pos_label = position_label(p.get("position"))
        team = teams_by_id.get(p.get("team_id") or "")
        color = team_color_hex(team)

        prompt = PROMPT_TEMPLATE.format(
            position=pos_label or "ポジション不明",
            team_color=color or "チームカラー不明（登録なし）",
        )

        items.append(
            {
                "player_id": pid,
                "name": name,
                "position": p.get("position"),
                "position_ja": pos_label,
                "team_id": p.get("team_id"),
                "team_color": color,
                "league": p.get("league"),
                "prompt": prompt,
            }
        )
    return sorted(items, key=lambda it: it["player_id"])


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="pipeline.illustrations")
    ap.add_argument("--dry-run", action="store_true", help="ファイルに書かず件数のみ表示")
    args = ap.parse_args(argv)

    players = _load_all_players()
    instagram_accounts = io.read_manual("instagram_accounts.json", default={})
    teams_by_id = _load_team_colors()

    items = build_todo_items(players, instagram_accounts=instagram_accounts, teams_by_id=teams_by_id)

    output = {
        "generated_at": datetime.now(io.JST).isoformat(timespec="seconds"),
        "prompt_template": PROMPT_TEMPLATE,
        "note": "実在選手の顔に似せる指定は禁止（肖像権リスク）。生成後は public/illustrations/{player_id}.webp に配置する（06）。",
        "count": len(items),
        "items": items,
    }

    print(f"[illustrations] 対象 {len(items)} 件")
    if args.dry_run:
        return 0

    io.write_json(TODO_PATH, output)
    print(f"[illustrations] {TODO_PATH.relative_to(io.REPO_ROOT)} を書き出しました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
