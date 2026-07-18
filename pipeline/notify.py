"""P3-2: Discord Webhook 通知（05 自動更新 / 通知）。

`scripts/discord_notify.py` を移植。Webhook URL は環境変数 `DISCORD_WEBHOOK`
（GitHub Secrets 経由でジョブに渡す。.env やコードに直接書かない）から読む。

CLI:
    python3 -m pipeline.notify --status success --title "daily_update 成功" \
        --detail "top14: 選手1106件" --detail "super-rugby: 選手545件" \
        --news "top14-join-ar_1-2026-07-18.md" \
        --warning "top14 standings: team=bayonne の数値欠落のため行を除外"

    python3 -m pipeline.notify --status failure --title "daily_update 検証失敗" \
        --detail "dup_id: a"

    # ワークフロー用: pipeline.run / pipeline.news_gen の標準出力を tee したログファイルと、
    # 生成ニュースのファイル名一覧（1行1ファイル名）から自動で detail/news/warning を組み立てる。
    python3 -m pipeline.notify --status success --title "daily_update 成功" \
        --log pipeline_run.log --log pipeline_news.log --news-list news_changed.txt

Webhook 未設定・送信失敗時は stderr にログを出すだけで exit 0 を返す
（通知の失敗でパイプライン全体のジョブを失敗扱いにしない）。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import requests

WEBHOOK_ENV = "DISCORD_WEBHOOK"

COLOR_SUCCESS = 0x2ECC71
COLOR_FAILURE = 0xE74C3C

MAX_LIST_ITEMS = 20
MAX_DESCRIPTION_LEN = 4000


def _bulleted(label: str, items: list[str]) -> list[str]:
    if not items:
        return []
    lines = [f"**{label}**"]
    lines.extend(f"- {item}" for item in items[:MAX_LIST_ITEMS])
    if len(items) > MAX_LIST_ITEMS:
        lines.append(f"...ほか {len(items) - MAX_LIST_ITEMS} 件")
    return lines


def build_payload(*, status: str, title: str, details: list[str],
                  news: list[str], warnings: list[str]) -> dict:
    """通知内容: 成功/失敗、リーグ別件数、生成ニュース一覧、warning（05）。"""
    color = COLOR_SUCCESS if status == "success" else COLOR_FAILURE
    lines: list[str] = []
    lines += _bulleted("リーグ別件数", details)
    lines += _bulleted("生成ニュース", news)
    lines += _bulleted(f"warning ({len(warnings)}件)", warnings)
    description = "\n".join(lines) if lines else "(詳細なし)"
    return {
        "embeds": [
            {
                "title": title,
                "description": description[:MAX_DESCRIPTION_LEN],
                "color": color,
                "footer": {"text": "rugbypicks daily_update"},
            }
        ]
    }


def parse_log(text: str) -> tuple[list[str], list[str]]:
    """pipeline.run / pipeline.news_gen の標準出力(+stderr)から detail/warning 行を抽出する。

    `[diff] ...` 行 → detail（リーグ別件数）。`[warn] ...` / `[error] ...` 行 → warning。
    それ以外の行（`[skip]` 等）は通知が長大化するため無視する。
    """
    details: list[str] = []
    warnings: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("[diff] "):
            details.append(line[len("[diff] "):])
        elif line.startswith("[warn] "):
            warnings.append(line[len("[warn] "):])
        elif line.startswith("[error] "):
            warnings.append(line[len("[error] "):])
    return details, warnings


def read_news_list(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def send(payload: dict, webhook_url: Optional[str] = None, *, timeout: int = 10) -> bool:
    import os

    webhook_url = webhook_url or os.getenv(WEBHOOK_ENV)
    if not webhook_url:
        print(f"[notify] {WEBHOOK_ENV} 未設定のため送信をスキップ", file=sys.stderr)
        return False
    try:
        resp = requests.post(webhook_url, json=payload, timeout=timeout)
        resp.raise_for_status()
        print(f"[notify] Discord通知送信 (status={resp.status_code})")
        return True
    except Exception as e:  # noqa: BLE001 - 通知失敗はジョブを落とさない
        print(f"[notify] Discord通知に失敗しました: {e}", file=sys.stderr)
        return False


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="pipeline.notify")
    ap.add_argument("--status", choices=["success", "failure"], required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--detail", action="append", default=[],
                    help="リーグ別件数などの行（複数指定可）")
    ap.add_argument("--news", action="append", default=[],
                    help="生成されたニュース記事のファイル名（複数指定可）")
    ap.add_argument("--warning", action="append", default=[],
                    help="warningメッセージ（複数指定可）")
    ap.add_argument("--log", action="append", default=[],
                    help="pipeline.run/news_gen のログファイル（[diff]/[warn]/[error] 行を自動抽出、複数指定可）")
    ap.add_argument("--news-list", default=None,
                    help="生成ニュースのファイル名一覧ファイル（1行1ファイル名）")
    args = ap.parse_args(argv)

    details = list(args.detail)
    warnings = list(args.warning)
    for log_path in args.log:
        p = Path(log_path)
        if p.exists():
            d, w = parse_log(p.read_text(encoding="utf-8"))
            details += d
            warnings += w
        else:
            print(f"[notify] ログファイルが見つかりません: {log_path}", file=sys.stderr)

    news = list(args.news)
    if args.news_list:
        news += read_news_list(Path(args.news_list))

    payload = build_payload(status=args.status, title=args.title, details=details,
                            news=news, warnings=warnings)
    send(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
