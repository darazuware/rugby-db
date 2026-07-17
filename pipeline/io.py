"""master 読み書きと _meta 更新（01のディレクトリ規約）。

master への書き込みはこのモジュール経由のみ。id 昇順で書き、diff を安定させる。
"""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
MASTER_DIR = REPO_ROOT / "data" / "master"
MANUAL_DIR = REPO_ROOT / "data" / "manual"
META_DIR = MASTER_DIR / "_meta"
JST = timezone(timedelta(hours=9))


def players_path(league: str) -> Path:
    return MASTER_DIR / "players" / f"{league}.json"


def teams_path(league: str) -> Path:
    return MASTER_DIR / "teams" / f"{league}.json"


def matches_path(league: str, season: str) -> Path:
    return MASTER_DIR / "matches" / f"{league}_{season}.json"


def standings_path(league: str, season: str) -> Path:
    return MASTER_DIR / "standings" / f"{league}_{season}.json"


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def read_records(path: Path) -> list[dict]:
    return read_json(path, default=[])


def write_records(path: Path, records: list[dict]) -> None:
    write_json(path, sorted(records, key=lambda r: r.get("id", "")))


def read_manual(name: str, default: Any = None) -> Any:
    return read_json(MANUAL_DIR / name, default=default if default is not None else {})


def update_last_run(league: str, *, counts: dict[str, int], warnings: list[str]) -> None:
    path = META_DIR / "last_run.json"
    data = read_json(path, default={})
    data[league] = {
        "run_at": datetime.now(JST).isoformat(timespec="seconds"),
        "counts": counts,
        "warnings": warnings,
    }
    write_json(path, data)


def write_diff_report(league: str, diff: dict) -> Path:
    date = datetime.now(JST).strftime("%Y-%m-%d")
    path = META_DIR / "diff" / f"{date}_{league}.json"
    write_json(path, diff)
    return path


def read_pending_departures() -> dict:
    """P1-8: league -> {player_id: entry} の退団保留リスト（05: 2回連続確認ロジック）。"""
    return read_json(META_DIR / "pending_departures.json", default={})


def write_pending_departures(data: dict) -> None:
    write_json(META_DIR / "pending_departures.json", data)
