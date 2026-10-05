"""data/manual/team_facts.json（pipeline/scrape/team_wiki.py の出力）を teams master に適用する。

- null / 空の項目だけを埋める（スクレイプ由来の値は上書きしない）。
- 埋めた値の出典は field_sources（founded/home_area/titles）と Stadium.source_url に残す。
- 適用後に Team スキーマで検証し、通らないチームは書き込まない。

実行: python3.11 -m pipeline.team_facts
"""
from __future__ import annotations

from pydantic import ValidationError

from pipeline import io
from pipeline.schemas import Team

FACTS_FILE = "team_facts.json"
LEAGUES = ("league-one-d1", "league-one-d2", "league-one-d3",
           "top14", "premiership", "urc", "super-rugby")


def load_facts() -> dict[str, dict]:
    return io.read_manual(FACTS_FILE, default={}).get("teams", {})


def apply(team: dict, facts: dict[str, dict]) -> list[str]:
    """team を破壊的に補完し、埋めたフィールド名を返す。"""
    f = facts.get(team["id"])
    if not f:
        return []
    filled: list[str] = []
    sources = team.setdefault("field_sources", {})
    if team.get("founded") is None and f.get("founded"):
        team["founded"] = f["founded"]["value"]
        sources["founded"] = f["founded"]["source_url"]
        filled.append("founded")
    if not team.get("home_area") and f.get("home_area"):
        team["home_area"] = f["home_area"]["value"]
        sources["home_area"] = f["home_area"]["source_url"]
        filled.append("home_area")
    if not team.get("home_stadiums") and f.get("home_stadiums"):
        team["home_stadiums"] = [dict(s) for s in f["home_stadiums"]]
        filled.append("home_stadiums")
    if not team.get("titles") and f.get("titles"):
        team["titles"] = [dict(t) for t in f["titles"]]
        sources["titles"] = f["titles"][0]["source_url"]
        filled.append("titles")
    return filled


def apply_all(teams: list[dict], facts: dict[str, dict] | None = None) -> list[str]:
    """teams を補完。検証に落ちたチームは補完前に戻して warning を返す。"""
    facts = load_facts() if facts is None else facts
    warnings: list[str] = []
    for i, t in enumerate(teams):
        before = {k: v for k, v in t.items()}
        apply(t, facts)
        try:
            teams[i] = Team.model_validate(t).model_dump(by_alias=True)
        except ValidationError as exc:
            teams[i] = before
            warnings.append(f"{t['id']}: team_facts 適用後の検証失敗 {exc.error_count()} 件のため未適用")
    return warnings


def main() -> int:
    facts = load_facts()
    total = 0
    for league in LEAGUES:
        path = io.teams_path(league)
        teams = io.read_records(path)
        counts = {}
        for t in teams:
            for k in apply({**t, "field_sources": dict(t.get("field_sources", {}))}, facts):
                counts[k] = counts.get(k, 0) + 1
        warnings = apply_all(teams, facts)
        io.write_records(path, teams)
        total += sum(counts.values())
        print(f"{league}: {counts or '変更なし'}" + (f" warnings={warnings}" if warnings else ""))
    print(f"team_facts: {total} 項目を補完")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
