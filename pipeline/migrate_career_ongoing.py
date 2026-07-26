"""career配列の末尾要素が「在籍中」なのに to=scraped_at年で終了扱いになっている
データ品質バグの既存データ修正（2026-07-25 データ品質バグ報告 問題1b）。

原因: all.rugby は在籍中チームにも "present" マーカーを出さず、取得時点の年を
そのまま to に表示する（pipeline/scrape/all_rugby.py の parse_player_bio 参照。
同ファイルの新規取得分は問題1aの修正で to=null になる）。

対象: career配列の最後の要素で to が、そのレコード自身の scraped_at の年と
一致するもの（career は取得元ページで時系列順のため、末尾要素=直近所属）。
team名とteam_idの突合はteam名表記ゆれ（"Stade Toulousain" vs team_id "toulouse"）
のため行わず、末尾要素という位置情報のみで判定する（scrape側の新規ロジックと同一基準）。

出力: data/master/_meta/career_ongoing_migration_report.md
"""
from __future__ import annotations

from datetime import datetime

from pipeline import io

ALL_LEAGUES = [
    "league-one-d1", "league-one-d2", "league-one-d3",
    "top14", "super-rugby", "mlr", "urc", "premiership", "national",
    "sevens-national", "age-grade", "university", "highschool",
]


def _scraped_year(scraped_at: str | None) -> int | None:
    if not scraped_at:
        return None
    try:
        return datetime.fromisoformat(scraped_at).year
    except ValueError:
        return None


def migrate_league(league: str) -> tuple[int, int]:
    """1リーグを移行。(対象レコード数, 総career件数中の書き換え数) を返す。"""
    path = io.players_path(league)
    records = io.read_records(path)
    changed_records = 0
    changed_entries = 0
    for rec in records:
        career = rec.get("career") or []
        if not career:
            continue
        last = career[-1]
        year = _scraped_year(rec.get("scraped_at"))
        if year is not None and last.get("to") == year:
            last["to"] = None
            changed_records += 1
            changed_entries += 1
    if changed_records:
        io.write_records(path, records)
    return changed_records, changed_entries


def main() -> None:
    lines = ["# career在籍中マイグレーションレポート", "", "| league | 書き換えレコード数 |", "|---|---|"]
    total = 0
    for league in ALL_LEAGUES:
        changed, _ = migrate_league(league)
        total += changed
        lines.append(f"| {league} | {changed} |")
    lines.append("")
    lines.append(f"合計: {total} 件の career 末尾要素の to を null化（在籍中扱い）")
    report = "\n".join(lines) + "\n"
    out_path = io.META_DIR / "career_ongoing_migration_report.md"
    out_path.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
