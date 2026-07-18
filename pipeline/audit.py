"""P3-3: 週次監査（05 自動更新 / weekly_audit.yml）。

kana未設定リスト・null率レポート・リンク切れチェックを行い、Markdownレポートを生成する。
GitHub Issue の起票自体は weekly_audit.yml 側で `gh issue create` を使う（本モジュールはレポート生成のみ）。

CLI:
    python3 -m pipeline.audit --out audit_report.md
    python3 -m pipeline.audit --out audit_report.md --skip-link-check   # ネットワーク不使用（テスト/オフライン用）

保守的な設計判断（00 の原則5「判断に迷ったら最も保守的」に従い明記）:
  - data/master/ への書き込みは一切行わない（本タスク実行時点で別セッションが
    data/master/ に実データ投入中のため、読み取り専用に徹する）。レポートは
    `--out` で指定した任意パス（data/ 配下ではないデフォルト）にのみ書く。
  - リンク切れチェックは選手ページ約3400件全件を毎週たたくと対象サイト
    （league-one.jp / all.rugby）への負荷・アクセスブロックのリスクが大きいため、
    チーム(38件、全件)＋リーグごとに固定シードでサンプリングした選手ページのみ
    チェックする。誤検知（一時的なタイムアウト等）を「壊れている」と断定しないよう、
    レポート上は「疑い」として扱う。
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Optional

from pipeline import io

ALL_LEAGUES = [
    "league-one-d1", "league-one-d2", "league-one-d3",
    "top14", "super-rugby", "national",
]

# null率を追跡するフィールド（03/01 のスキーマで Optional のもの中心）
NULL_RATE_FIELDS = ["name_kana", "position", "height_cm", "weight_kg", "birthdate", "image_url"]

PLAYER_LINK_SAMPLE_PER_LEAGUE = 15
LINK_CHECK_TIMEOUT = 8
MAX_LIST_ITEMS = 20


def load_players_by_league(leagues: Optional[list[str]] = None) -> dict[str, list[dict]]:
    leagues = leagues or ALL_LEAGUES
    return {league: io.read_records(io.players_path(league)) for league in leagues}


def load_teams(leagues: Optional[list[str]] = None) -> list[dict]:
    leagues = leagues or ALL_LEAGUES
    teams: list[dict] = []
    for league in leagues:
        teams.extend(io.read_records(io.teams_path(league)))
    return teams


def kana_missing(players_by_league: dict[str, list[dict]],
                  overrides: dict[str, str]) -> dict[str, list[dict]]:
    """外国籍選手で name_kana が未設定 かつ kana_overrides.json にも未登録のもの。"""
    result: dict[str, list[dict]] = {}
    for league, players in players_by_league.items():
        missing = [
            {"id": p["id"], "name": p.get("name_en") or p.get("name_ja") or p["id"]}
            for p in players
            if p.get("name_kana") is None
            and p.get("nationality")
            and "JP" not in p["nationality"]
            and p["id"] not in overrides
        ]
        if missing:
            result[league] = missing
    return result


def null_rate(players_by_league: dict[str, list[dict]]) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}
    for league, players in players_by_league.items():
        if not players:
            continue
        n = len(players)
        result[league] = {
            field: round(sum(1 for p in players if p.get(field) is None) / n, 3)
            for field in NULL_RATE_FIELDS
        }
    return result


def sample_urls(players_by_league: dict[str, list[dict]], teams: list[dict], *,
                 sample_per_league: int = PLAYER_LINK_SAMPLE_PER_LEAGUE,
                 seed: int = 0) -> list[tuple[str, str]]:
    """(label, url) のリスト。teams は全件、players はリーグごとに固定シードでサンプル。"""
    rng = random.Random(seed)
    urls: list[tuple[str, str]] = []
    seen: set[str] = set()
    for t in teams:
        u = t.get("source_url")
        if u and u not in seen:
            urls.append((f"team:{t['id']}", u))
            seen.add(u)
    for league in sorted(players_by_league):
        candidates = [p for p in players_by_league[league] if p.get("source_url")]
        candidates.sort(key=lambda p: p["id"])
        sample = rng.sample(candidates, k=min(sample_per_league, len(candidates)))
        for p in sample:
            u = p["source_url"]
            if u not in seen:
                urls.append((f"player:{p['id']}", u))
                seen.add(u)
    return urls


def check_links(urls: list[tuple[str, str]], *, timeout: int = LINK_CHECK_TIMEOUT) -> list[str]:
    """疑わしい（4xx/5xx または例外） URL を 'label: url (reason)' 形式で返す。"""
    import requests

    broken: list[str] = []
    for label, url in urls:
        try:
            resp = requests.head(url, timeout=timeout, allow_redirects=True)
            if resp.status_code in (405, 501):  # HEAD未対応サイト向けフォールバック
                resp = requests.get(url, timeout=timeout, allow_redirects=True)
            if resp.status_code >= 400:
                broken.append(f"{label}: {url} (status={resp.status_code})")
        except requests.RequestException as e:
            broken.append(f"{label}: {url} (error={e.__class__.__name__})")
    return broken


def build_markdown(*, kana: dict[str, list[dict]], nulls: dict[str, dict[str, float]],
                    broken: list[str], link_checked: int) -> str:
    total_kana = sum(len(v) for v in kana.values())
    total_broken = len(broken)
    status = "OK" if total_kana == 0 and total_broken == 0 else "要確認"

    lines = [f"# 週次監査レポート（{status}）", ""]

    lines.append(f"## kana未設定（外国籍選手・kana_overrides未登録、合計 {total_kana} 件）")
    if kana:
        for league in sorted(kana):
            items = [f"{it['id']} {it['name']}" for it in kana[league]]
            lines.append(f"\n**{league}**（{len(items)}件）")
            lines += [f"- {item}" for item in items[:MAX_LIST_ITEMS]]
            if len(items) > MAX_LIST_ITEMS:
                lines.append(f"...ほか {len(items) - MAX_LIST_ITEMS} 件")
    else:
        lines.append("なし")
    lines.append("")

    lines.append("## null率レポート")
    if nulls:
        for league in sorted(nulls):
            rates = nulls[league]
            lines.append(f"- {league}: " + ", ".join(f"{k}={v:.0%}" for k, v in rates.items()))
    else:
        lines.append("対象データなし")
    lines.append("")

    lines.append(f"## リンク切れチェック（サンプル{link_checked}件、疑い{total_broken}件）")
    if broken:
        lines += [f"- {b}" for b in broken[:MAX_LIST_ITEMS]]
        if len(broken) > MAX_LIST_ITEMS:
            lines.append(f"...ほか {len(broken) - MAX_LIST_ITEMS} 件")
    else:
        lines.append("なし")

    return "\n".join(lines) + "\n"


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="pipeline.audit")
    ap.add_argument("--out", default="audit_report.md",
                     help="レポート出力先（data/ 配下は不可。デフォルトはリポジトリ直下）")
    ap.add_argument("--skip-link-check", action="store_true",
                     help="リンク切れチェックをスキップ（ネットワーク不使用、テスト/オフライン用）")
    ap.add_argument("--sample-per-league", type=int, default=PLAYER_LINK_SAMPLE_PER_LEAGUE)
    args = ap.parse_args(argv)

    players_by_league = load_players_by_league()
    teams = load_teams()
    overrides = io.read_manual("kana_overrides.json", default={})

    kana = kana_missing(players_by_league, overrides)
    nulls = null_rate(players_by_league)

    broken: list[str] = []
    link_checked = 0
    if not args.skip_link_check:
        urls = sample_urls(players_by_league, teams, sample_per_league=args.sample_per_league)
        link_checked = len(urls)
        broken = check_links(urls)

    md = build_markdown(kana=kana, nulls=nulls, broken=broken, link_checked=link_checked)
    out_path = Path(args.out)
    out_path.write_text(md, encoding="utf-8")

    total_kana = sum(len(v) for v in kana.values())
    has_findings = bool(total_kana or broken)
    print(f"[audit] レポート出力: {out_path}")
    print(f"[audit] kana未設定合計: {total_kana}件 / リンク切れ疑い: {len(broken)}件")
    # 監査は検証ゲートではなく通知目的のジョブのため、findings があっても exit 1 にはしない。
    # Issue 起票の要否は weekly_audit.yml 側がこの行を grep して判断する（GITHUB_OUTPUT へ反映）。
    print(f"[audit] has_findings={'true' if has_findings else 'false'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
