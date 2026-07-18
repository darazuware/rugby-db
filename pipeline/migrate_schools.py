"""P5-1 学校データ移行（10_YOUTH_AGEGRADE.md / 01_DATA_ARCHITECTURE.md）。

既存 Player.education の name_raw（P1-4移行時に school_id=null で入った出身校名）を
data/master/schools/schools.json に正規化して登録し、各 education entry に school_id を埋める。

方針（00原則1-3、10）:
  - 学校名という「事実」は既存 name_raw（スクレイパー/レガシーDBが実際に取得した値）を
    そのまま採用する。AIの知識で校名・ローマ字表記・かな・都道府県を補完しない。
  - id はソース表記（name_raw）をNFKC正規化＋空白畳み込みしたものをkebab化して生成する。
    日本語校名をローマ字化すると「AIによる翻訳＝未確認の事実」になるため行わない
    （公式サイトのローマ字表記が別途取得できた時点＝P5-5/P5-6以降で置き換える）。
  - 表記ゆれ（同一校の別表記）の吸収は data/manual/school_aliases.json
    （人手管理: 正規化後の name_raw → canonical名）のみで行う。このスクリプト自体は
    Unicode正規化以上の自動名寄せをしない（誤統合防止）。
  - pref・name_kana・source_url・scraped_at は本タスクの入力に無いため null のまま
    （schemas.School 参照）。
  - type(hs/univ) が異なれば同名でも別レコード（高校/大学の校名衝突を分離）。
  - 対象は school_id が未設定(None)の education entry のみ。学校未登録が無いファイルは
    書き戻さない（対象外リーグの無関係な作業中差分に触れないため）。

出力:
  data/master/schools/schools.json
  data/master/players/*.json（school_id を新規に埋めたファイルのみ更新）
  data/master/_meta/school_migration_report.md
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

from pydantic import ValidationError

from pipeline import io
from pipeline.schemas import Player, School

JST = timezone(timedelta(hours=9))
PLAYERS_DIR = io.MASTER_DIR / "players"


def _now() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def normalize_school_name(name: str) -> str:
    """NFKC正規化＋前後/連続空白の畳み込みのみ（表記の正規化。事実の変更ではない）。"""
    s = unicodedata.normalize("NFKC", name or "")
    return re.sub(r"\s+", " ", s).strip()


def slugify_school(name: str) -> str:
    """英数字・かな・漢字を保持したままkebab化。ローマ字化はしない（本ファイル冒頭の方針）。"""
    s = normalize_school_name(name).lower()
    slug = re.sub(r"[^\w]+", "-", s, flags=re.UNICODE).strip("-")
    return slug or "school"


class SchoolRegistry:
    """(canonical_name, type) → school_id。既存 schools.json を引き継いで冪等に動く。"""

    def __init__(self, existing: list[dict]):
        self.records: dict[str, dict] = {r["id"]: r for r in existing}
        self.by_key: dict[tuple[str, str], str] = {(r["name"], r["type"]): r["id"] for r in existing}
        self._used_ids: set[str] = set(self.records.keys())

    def resolve(self, canonical_name: str, type_: str) -> tuple[str, bool]:
        key = (canonical_name, type_)
        if key in self.by_key:
            return self.by_key[key], False
        base = slugify_school(canonical_name)
        sid = base
        n = 2
        while sid in self._used_ids:
            sid = f"{base}-{n}"
            n += 1
        self._used_ids.add(sid)
        self.by_key[key] = sid
        self.records[sid] = {
            "id": sid, "name": canonical_name, "name_kana": None,
            "type": type_, "pref": None, "source_url": None, "scraped_at": None,
        }
        return sid, True


def migrate() -> dict:
    aliases: dict[str, str] = io.read_manual("school_aliases.json", default={})
    registry = SchoolRegistry(io.read_records(io.schools_path()))

    stats: Counter = Counter()
    warnings: list[str] = []
    updated_files: list[str] = []
    new_schools_by_file: dict[str, int] = {}

    for path in sorted(PLAYERS_DIR.glob("*.json")):
        players = io.read_json(path, default=[])
        if not players:
            continue
        file_changed = False
        file_new = 0
        for p in players:
            for edu in p.get("education") or []:
                if edu.get("school_id") is not None:
                    continue
                name_raw = edu.get("name_raw")
                if not name_raw:
                    continue
                stats["unresolved_seen"] += 1
                canonical = aliases.get(normalize_school_name(name_raw), normalize_school_name(name_raw))
                sid, is_new = registry.resolve(canonical, edu["type"])
                edu["school_id"] = sid
                file_changed = True
                stats["resolved"] += 1
                if is_new:
                    file_new += 1
                    stats["new_schools"] += 1

        if not file_changed:
            continue

        revalidated: list[dict] = []
        for p in players:
            try:
                model = Player.model_validate(p)
            except ValidationError as exc:
                warnings.append(
                    f"{p.get('id', '?')}: school_id付与後の再検証失敗 → 元データのまま保持 "
                    f"({exc.errors()[0]['msg']})"
                )
                revalidated.append(p)
                continue
            revalidated.append(model.model_dump(by_alias=True))

        io.write_records(path, revalidated)
        updated_files.append(path.stem)
        new_schools_by_file[path.stem] = file_new

    school_list: list[dict] = []
    for sid, rec in sorted(registry.records.items()):
        try:
            model = School.model_validate(rec)
        except ValidationError as exc:
            warnings.append(f"school {sid}: 検証失敗 → スキップ ({exc.errors()[0]['msg']})")
            continue
        school_list.append(model.model_dump(by_alias=True))
    io.write_records(io.schools_path(), school_list)

    report = {
        "schools_total": len(school_list),
        "new_schools": stats["new_schools"],
        "resolved_education_entries": stats["resolved"],
        "updated_player_files": updated_files,
        "new_schools_by_file": new_schools_by_file,
        "warnings": warnings,
    }
    _write_report(report)
    return report


def _write_report(report: dict) -> None:
    L = ["# 学校データ移行レポート（P5-1）\n", f"生成: {_now()}\n"]
    L.append(f"- schools.json 総数: {report['schools_total']}")
    L.append(f"- 今回新規追加した学校: {report['new_schools']}")
    L.append(f"- school_id を付与した education entry 数: {report['resolved_education_entries']}\n")
    L.append("## 更新した players/*.json\n")
    if report["updated_player_files"]:
        for f in report["updated_player_files"]:
            L.append(f"- {f}.json: 新規学校 {report['new_schools_by_file'].get(f, 0)} 件")
    else:
        L.append("- なし（school_id 未設定の education entry を持つファイルが無かった）")
    L.append("")
    if report["warnings"]:
        L.append(f"## warnings（{len(report['warnings'])}件）\n")
        for w in report["warnings"][:50]:
            L.append(f"- {w}")
    io.META_DIR.mkdir(parents=True, exist_ok=True)
    (io.META_DIR / "school_migration_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    r = migrate()
    print(
        f"schools={r['schools_total']} (+{r['new_schools']}) "
        f"resolved_education={r['resolved_education_entries']} "
        f"updated_files={r['updated_player_files']}"
    )
    for w in r["warnings"][:20]:
        print(f"[warn] {w}")
