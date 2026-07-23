"""予約公開の検知 & Telegram 報告（rugbypicks）。

`src/content/news/*.md` の frontmatter（pubDate / publishAt / draft / title）を読み、
公開時刻を跨いだ記事を「公開完了」として Telegram に通知する。あわせて本日・明日の
公開予定を報告する。URL は https://rugbypick.com/news/<slug>/ 。

公開判定の時刻:
  publishAt があればその日時（naive の場合 JST とみなす）。
  無ければ pubDate（日付）の JST 当日 0:00。

状態ファイル data/master/_meta/publish_state.json に「通知済み slug」を保存し、
同じ記事を二重通知しない。初回は現時点で公開済みの記事を無言でシードする。

このスクリプトが状態ファイルを書き換える＝新規公開があった時だけ、CI が commit/push し、
Vercel 再ビルドで prerender ページが生成される（状態変化そのものが再ビルドのトリガー）。

CLI:
  python3 -m pipeline.publish_report                # 検知＋差分あれば通知
  python3 -m pipeline.publish_report --daily        # 予定が無くても本日/明日の予定を必ず送る
  python3 -m pipeline.publish_report --dry-run      # 通知せず内容を表示
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from pipeline import telegram_notify

JST = ZoneInfo("Asia/Tokyo")
ROOT = Path(__file__).resolve().parent.parent
NEWS_DIR = ROOT / "src" / "content" / "news"
STATE_PATH = ROOT / "data" / "master" / "_meta" / "publish_state.json"
BASE_URL = "https://rugbypick.com/news"


class Article:
    def __init__(self, slug: str, title: str, live_ts: float, draft: bool):
        self.slug = slug
        self.title = title
        self.live_ts = live_ts  # epoch 秒（公開時刻）
        self.draft = draft

    @property
    def url(self) -> str:
        return f"{BASE_URL}/{self.slug}/"

    @property
    def live_dt(self) -> dt.datetime:
        return dt.datetime.fromtimestamp(self.live_ts, JST)


def _parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}


def _to_ts(fm: dict) -> float | None:
    """公開時刻を epoch 秒で返す。"""
    pa = fm.get("publishAt")
    if isinstance(pa, dt.datetime):
        if pa.tzinfo is None:
            pa = pa.replace(tzinfo=JST)
        return pa.timestamp()
    pd = fm.get("pubDate")
    if isinstance(pd, dt.datetime):
        if pd.tzinfo is None:
            pd = pd.replace(tzinfo=JST)
        return pd.timestamp()
    if isinstance(pd, dt.date):
        # publishAt 未指定は JST 当日 12:00 公開（深夜0:00を避ける既定）。
        return dt.datetime(pd.year, pd.month, pd.day, 12, 0, tzinfo=JST).timestamp()
    return None


def load_articles() -> list[Article]:
    out: list[Article] = []
    for p in sorted(NEWS_DIR.glob("*.md")):
        fm = _parse_frontmatter(p.read_text(encoding="utf-8"))
        ts = _to_ts(fm)
        if ts is None:
            print(f"[publish] 公開日不明のためスキップ: {p.name}", file=sys.stderr)
            continue
        out.append(Article(
            slug=p.stem,
            title=str(fm.get("title", p.stem)),
            live_ts=ts,
            draft=bool(fm.get("draft", False)),
        ))
    return out


def load_state() -> set[str]:
    if STATE_PATH.exists():
        try:
            return set(json.loads(STATE_PATH.read_text(encoding="utf-8")).get("reported", []))
        except (json.JSONDecodeError, OSError):
            return set()
    return set()


def save_state(reported: set[str]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps({"reported": sorted(reported)}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_report(articles: list[Article], reported: set[str], now: float,
                 *, seeded: bool):
    """(message or None, new_published:list, changed:bool) を返す。"""
    published_now: list[Article] = []
    today_upcoming: list[Article] = []
    tomorrow_upcoming: list[Article] = []

    today = dt.datetime.fromtimestamp(now, JST).date()
    tomorrow = today + dt.timedelta(days=1)

    for a in articles:
        if a.draft:
            continue
        if a.live_ts <= now:
            if a.slug not in reported:
                published_now.append(a)
                reported.add(a.slug)
        else:
            d = a.live_dt.date()
            if d == today:
                today_upcoming.append(a)
            elif d == tomorrow:
                tomorrow_upcoming.append(a)

    if seeded:
        # 初回シード: 既に公開済みは無言で登録、これから公開ぶんだけ予定として案内。
        published_now = []

    today_upcoming.sort(key=lambda x: x.live_ts)
    tomorrow_upcoming.sort(key=lambda x: x.live_ts)

    lines: list[str] = []
    if published_now:
        t = dt.datetime.fromtimestamp(now, JST).strftime("%H:%M")
        lines.append(f"✅ <b>公開完了</b>（{t} JST）")
        for a in published_now:
            lines.append(f"・<a href=\"{a.url}\">{a.title}</a>")
        lines.append("")
    if today_upcoming:
        lines.append("🕒 <b>本日の公開予定</b>")
        for a in today_upcoming:
            lines.append(f"・{a.live_dt.strftime('%H:%M')} {a.title}")
        lines.append("")
    if tomorrow_upcoming:
        lines.append("📅 <b>明日の公開予定</b>")
        for a in tomorrow_upcoming:
            lines.append(f"・{a.live_dt.strftime('%H:%M')} {a.title}")
        lines.append("")

    changed = bool(published_now) or seeded
    msg = "\n".join(lines).strip() if lines else None
    return msg, published_now, changed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pipeline.publish_report")
    ap.add_argument("--daily", action="store_true",
                    help="公開・予定が無くても本日/明日の予定を必ず送る")
    ap.add_argument("--dry-run", action="store_true", help="通知せず内容を表示")
    args = ap.parse_args(argv)

    seeded = not STATE_PATH.exists()
    reported = load_state()
    articles = load_articles()
    now = dt.datetime.now(tz=JST).timestamp()

    msg, published_now, changed = build_report(articles, reported, now, seeded=seeded)

    if seeded:
        # 現時点で公開済みの記事を通知済みとして登録（初回スパム防止）。
        for a in articles:
            if not a.draft and a.live_ts <= now:
                reported.add(a.slug)

    should_send = bool(published_now) or (args.daily and msg)

    if args.dry_run:
        print("=== dry-run ===")
        print(msg or "(送信対象なし)")
        print(f"changed={changed} published_now={[a.slug for a in published_now]} seeded={seeded}")
        return 0

    if should_send and msg:
        telegram_notify.send(msg, disable_preview=True)

    if changed:
        save_state(reported)
        print(f"[publish] 状態更新 published={[a.slug for a in published_now]} seeded={seeded}")
    else:
        print("[publish] 変化なし")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
