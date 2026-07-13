"""03_VALIDATION.md の整合性チェック。

入力は検証済みレコードの plain dict（Player.model_dump() 相当）。
エラー1件でも呼び出し側（run.py）は exit 1 し、master を更新しない。
caps_monotonic だけは new 側の dict を書き換えて前回値を維持する（03）。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from pipeline.schemas import TEAM_LEAGUES, normalize_name_en

SHRINK_THRESHOLD = 0.30
SCORE_MAX = 150


@dataclass
class CheckResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    merge_candidates: list[dict] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def extend(self, other: "CheckResult") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.merge_candidates.extend(other.merge_candidates)


def check_dup_id(players: list[dict]) -> CheckResult:
    r = CheckResult()
    seen: set[str] = set()
    for p in players:
        if p["id"] in seen:
            r.errors.append(f"dup_id: {p['id']}")
        seen.add(p["id"])
    return r


def check_dup_person(players_by_league: dict[str, list[dict]]) -> CheckResult:
    """同一リーグ内で name_en+birthdate が両方非nullで重複 → エラー。"""
    r = CheckResult()
    for league, players in players_by_league.items():
        seen: dict[tuple[str, str], str] = {}
        for p in players:
            if not p.get("name_en") or not p.get("birthdate"):
                continue
            key = (normalize_name_en(p["name_en"]), p["birthdate"])
            if key in seen:
                r.errors.append(f"dup_person: {league} で {p['id']} と {seen[key]} が同一人物")
            else:
                seen[key] = p["id"]
    return r


def check_cross_person(players_by_league: dict[str, list[dict]],
                       player_merges: dict[str, str] | None = None) -> CheckResult:
    """ファイル横断で同一人物らしき別ID → warning + merge_candidates（自動マージしない）。"""
    r = CheckResult()
    merges = player_merges or {}
    groups: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for league, players in players_by_league.items():
        for p in players:
            if not p.get("name_en") or not p.get("birthdate"):
                continue
            key = (normalize_name_en(p["name_en"]), p["birthdate"])
            groups.setdefault(key, []).append((league, p["id"]))
    for key, members in groups.items():
        ids = {pid for _, pid in members}
        if len(ids) < 2:
            continue
        # merges で解決済み（重複側が全て canonical に紐づく）なら除外
        unresolved = {pid for pid in ids if pid not in merges and pid not in merges.values()}
        resolved_dups = {pid for pid in ids if pid in merges and merges[pid] in ids}
        if ids - resolved_dups - {merges[d] for d in resolved_dups} == set() or not unresolved:
            continue
        r.warnings.append(f"cross_person: {sorted(ids)} が同一人物候補（name_en+birthdate一致）")
        r.merge_candidates.append({
            "name_en_normalized": key[0],
            "birthdate": key[1],
            "members": [{"league": lg, "id": pid} for lg, pid in sorted(members)],
        })
    return r


def check_team_ref(players: list[dict], teams: list[dict]) -> CheckResult:
    r = CheckResult()
    team_ids = {t["id"] for t in teams}
    for p in players:
        if p.get("league") not in TEAM_LEAGUES:
            continue  # team_id=null の学校/代表レコードは対象外（03）
        if p.get("team_id") not in team_ids:
            r.errors.append(f"team_ref: {p['id']} の team_id={p.get('team_id')!r} が teams に無い")
    return r


def check_roster_sym(players: list[dict], teams: list[dict]) -> CheckResult:
    """team.roster_ids と players の相互参照一致。partial チームは免除（03）。"""
    r = CheckResult()
    players_by_team: dict[str, set[str]] = {}
    for p in players:
        if p.get("team_id"):
            players_by_team.setdefault(p["team_id"], set()).add(p["id"])
    for t in teams:
        if t.get("roster_mode") == "partial":
            continue
        roster = set(t.get("roster_ids", []))
        actual = players_by_team.get(t["id"], set())
        for pid in sorted(roster - actual):
            r.errors.append(f"roster_sym: {t['id']} の roster_ids にある {pid} が players に無い")
        for pid in sorted(actual - roster):
            r.errors.append(f"roster_sym: {pid} (team_id={t['id']}) が roster_ids に無い")
    return r


def check_shrink(new_players: list[dict], prev_players: list[dict], league: str) -> CheckResult:
    r = CheckResult()
    if prev_players and len(new_players) < len(prev_players) * (1 - SHRINK_THRESHOLD):
        r.errors.append(
            f"shrink: {league} の選手数が {len(prev_players)} → {len(new_players)} "
            f"(30%以上減。サイト構造変化の疑い)")
    return r


def check_caps_monotonic(new_players: list[dict], prev_players: list[dict],
                         caps_corrections: dict[str, dict] | None = None) -> CheckResult:
    """キャップ減少 → warning + new 側 dict を前回値に書き戻す。corrections 登録選手は免除。"""
    r = CheckResult()
    corrections = caps_corrections or {}
    prev_by_id = {p["id"]: p for p in prev_players}
    for p in new_players:
        if p["id"] in corrections:
            continue
        prev = prev_by_id.get(p["id"])
        if not prev or not prev.get("caps") or not p.get("caps"):
            continue
        if p["caps"]["count"] < prev["caps"]["count"]:
            r.warnings.append(
                f"caps_monotonic: {p['id']} のキャップが {prev['caps']['count']} → "
                f"{p['caps']['count']} に減少。前回値を維持")
            p["caps"] = prev["caps"]
    return r


def check_match_sanity(matches: list[dict]) -> CheckResult:
    r = CheckResult()
    for m in matches:
        has_score = m.get("home_score") is not None or m.get("away_score") is not None
        if m.get("status") != "finished" and has_score:
            r.errors.append(f"match_sanity: {m['id']} は status={m.get('status')} なのにスコアがある")
        for side in ("home_score", "away_score"):
            s = m.get(side)
            if s is not None and not (0 <= s <= SCORE_MAX):
                r.errors.append(f"match_sanity: {m['id']} の {side}={s} が 0-{SCORE_MAX} 外")
    return r


def check_standings_sum(standings: list[dict]) -> CheckResult:
    r = CheckResult()
    for st in standings:
        for row in st.get("rows", []):
            if row["played"] != row["won"] + row["drawn"] + row["lost"]:
                r.errors.append(
                    f"standings_sum: {st['league']} {st['season']} {row['team_id']}: "
                    f"played={row['played']} != won+drawn+lost="
                    f"{row['won'] + row['drawn'] + row['lost']}")
    return r


def check_kana_coverage(players: list[dict]) -> CheckResult:
    r = CheckResult()
    n = sum(1 for p in players
            if p.get("name_kana") is None and p.get("nationality") and "JP" not in p["nationality"])
    if n:
        r.warnings.append(f"kana_coverage: name_kana 未設定の外国人選手 {n} 件")
    return r


def run_all(players_by_league: dict[str, list[dict]],
            teams: list[dict],
            matches: list[dict],
            standings: list[dict],
            prev_players_by_league: dict[str, list[dict]] | None = None,
            player_merges: dict[str, str] | None = None,
            caps_corrections: dict[str, dict] | None = None) -> CheckResult:
    result = CheckResult()
    all_players = [p for ps in players_by_league.values() for p in ps]
    result.extend(check_dup_id(all_players))
    result.extend(check_dup_person(players_by_league))
    result.extend(check_cross_person(players_by_league, player_merges))
    result.extend(check_team_ref(all_players, teams))
    result.extend(check_roster_sym(all_players, teams))
    prev = prev_players_by_league or {}
    for league, players in players_by_league.items():
        result.extend(check_shrink(players, prev.get(league, []), league))
        result.extend(check_caps_monotonic(players, prev.get(league, []), caps_corrections))
    result.extend(check_match_sanity(matches))
    result.extend(check_standings_sum(standings))
    result.extend(check_kana_coverage(all_players))
    return result
