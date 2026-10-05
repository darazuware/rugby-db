"""data/master/ 内部整合性の全件監査（読み取り専用）。

03_VALIDATION.md の検証ゲート（checks.py）は「新規スクレイプ結果を通すか」の判定用。
本モジュールは既にコミット済みの data/master/ 全体を横断し、内部矛盾
（重複・欠損・参照切れ・日付/スコア不整合・表記ゆれ）を全件列挙する。

原則:
  - data/master/ には一切書き込まない（読み取りのみ）。
  - 外部知識で値を補完・断定しない。判定根拠は master/manual 内のデータ同士の突合のみ。
    外部確認が必要なものは needs_official=True として列挙する。

CLI:
    python3 -m pipeline.validate.master_audit                       # サマリを標準出力
    python3 -m pipeline.validate.master_audit --json out.json       # 全件JSON
    python3 -m pipeline.validate.master_audit --md out.md           # 全件Markdown
終了コード: severity=error が1件以上なら 1。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

from pydantic import ValidationError

from pipeline.schemas import (
    ALLOWED_DOMAINS, LEAGUE_KEYS, TEAM_LEAGUES, Match, Player, School, Standing, Team,
    normalize_name_en,
)
from pipeline.validate import checks

REPO_ROOT = Path(__file__).resolve().parents[2]
MASTER = REPO_ROOT / "data" / "master"
MANUAL = REPO_ROOT / "data" / "manual"
JST = timezone(timedelta(hours=9))

# 同一データ内で「古い」とみなす scraped_at の乖離（ファイル内最新との差）
STALE_DAYS = 30
# U代表 squad の年齢上限許容（uN: 当該年の年齢 <= N+1 を許容）
AGE_GRADE_SLACK = 1


@dataclass
class Finding:
    check: str
    severity: str  # error / warn / info
    file: str
    target: str
    detail: str
    proposal: str = ""
    needs_official: bool = False
    evidence: dict = field(default_factory=dict)


class Audit:
    def __init__(self, master: Path = MASTER, manual: Path = MANUAL):
        self.master = master
        self.manual = manual
        self.findings: list[Finding] = []
        self._load()

    # ------------------------------------------------------------------ load
    def _read(self, p: Path, default: Any = None) -> Any:
        if not p.exists():
            return default
        with p.open(encoding="utf-8") as f:
            return json.load(f)

    def _load(self) -> None:
        m = self.master
        self.players: dict[str, list[dict]] = {}
        for p in sorted((m / "players").glob("*.json")):
            self.players[p.stem] = self._read(p, [])
        self.teams: dict[str, list[dict]] = {}
        for p in sorted((m / "teams").glob("*.json")):
            self.teams[p.stem] = self._read(p, [])
        self.matches: dict[str, list[dict]] = {}
        for p in sorted((m / "matches").glob("*.json")):
            self.matches[p.stem] = self._read(p, [])
        self.standings: dict[str, dict] = {}
        for p in sorted((m / "standings").glob("*.json")):
            self.standings[p.stem] = self._read(p, {})
        self.callups: dict[str, list[dict]] = {}
        for p in sorted((m / "callups").glob("*.json")):
            self.callups[p.stem] = self._read(p, [])
        self.episodes: dict[str, dict] = {}
        for p in sorted((m / "players" / "episodes").glob("*.json")):
            self.episodes[p.name] = self._read(p, {})
        self.schools: list[dict] = self._read(m / "schools" / "schools.json", [])
        meta = m / "_meta"
        self.merge_candidates = self._read(meta / "merge_candidates.json", [])
        self.last_run = self._read(meta / "last_run.json", {})
        self.redirects = self._read(meta / "redirects.json", {})
        self.retired = self._read(meta / "retired_slugs.json", [])
        self.pending = self._read(meta / "pending_departures.json", {})
        self.player_merges: dict[str, str] = self._read(self.manual / "player_merges.json", {})
        self.kana_overrides: dict[str, str] = self._read(self.manual / "kana_overrides.json", {})

        self.all_ids: dict[str, list[str]] = defaultdict(list)  # id -> leagues
        self.by_id: dict[str, list[tuple[str, dict]]] = defaultdict(list)
        for lg, ps in self.players.items():
            for p in ps:
                pid = p.get("id")
                self.all_ids[pid].append(lg)
                self.by_id[pid].append((lg, p))
        self.team_by_id: dict[str, tuple[str, dict]] = {}
        for lg, ts in self.teams.items():
            for t in ts:
                self.team_by_id.setdefault(t.get("id"), (lg, t))

    # ------------------------------------------------------------- helpers
    def add(self, check: str, severity: str, file: str, target: str, detail: str,
            proposal: str = "", needs_official: bool = False, **evidence: Any) -> None:
        self.findings.append(Finding(check, severity, file, target, detail, proposal,
                                     needs_official, evidence))

    @staticmethod
    def pfile(lg: str) -> str:
        return f"players/{lg}.json"

    def resolve_id(self, pid: str) -> str | None:
        """player_merges を辿って現存 id を返す。"""
        seen = set()
        cur = pid
        while cur not in self.all_ids and cur in self.player_merges and cur not in seen:
            seen.add(cur)
            cur = self.player_merges[cur]
        return cur if cur in self.all_ids else None

    @staticmethod
    def norm_ja(s: str | None) -> str:
        if not s:
            return ""
        s = unicodedata.normalize("NFKC", s)
        return re.sub(r"[\s・=＝]", "", s)

    @staticmethod
    def parse_ts(s: str | None) -> datetime | None:
        if not s:
            return None
        try:
            d = datetime.fromisoformat(s)
        except ValueError:
            return None
        return d if d.tzinfo else d.replace(tzinfo=JST)

    # -------------------------------------------------------------- checks
    def run(self) -> list[Finding]:
        for fn in (
            self.c_schema, self.c_missing_keys, self.c_dup_id, self.c_slug,
            self.c_cross_league_conflict, self.c_dup_person, self.c_same_name_no_birthdate,
            self.c_cross_person, self.c_merges, self.c_team_ref_roster, self.c_teams,
            self.c_standings, self.c_matches, self.c_callups, self.c_episodes,
            self.c_names, self.c_vocab, self.c_source, self.c_career, self.c_age,
            self.c_education_schools, self.c_caps, self.c_meta,
        ):
            fn()
        return self.findings

    def c_schema(self) -> None:
        for lg, ps in self.players.items():
            if lg not in LEAGUE_KEYS:
                self.add("schema", "error", self.pfile(lg), lg, "未定義のリーグキーのファイル")
            for p in ps:
                try:
                    _, warns = Player.parse(p)
                    for w in warns:
                        self.add("schema_range", "warn", self.pfile(lg), p.get("id"), w,
                                 "スクレイパー側で null 化して再取得（推測値で埋めない）")
                except ValidationError as e:
                    self.add("schema", "error", self.pfile(lg), p.get("id"),
                             "; ".join(x["msg"] for x in e.errors())[:300],
                             "スクレイパー/transform を修正して再生成")
                if p.get("league") != lg:
                    self.add("league_mismatch", "error", self.pfile(lg), p.get("id"),
                             f"league={p.get('league')!r} がファイル名 {lg} と不一致")
        for lg, ts in self.teams.items():
            for t in ts:
                try:
                    Team.model_validate(t)
                except ValidationError as e:
                    self.add("schema", "error", f"teams/{lg}.json", t.get("id"),
                             "; ".join(x["msg"] for x in e.errors())[:300])
                if t.get("league") != lg:
                    self.add("league_mismatch", "error", f"teams/{lg}.json", t.get("id"),
                             f"league={t.get('league')!r} がファイル名と不一致")
        for name, ms in self.matches.items():
            for mt in ms:
                try:
                    Match.model_validate(mt)
                except ValidationError as e:
                    self.add("schema", "error", f"matches/{name}.json", mt.get("id"),
                             "; ".join(x["msg"] for x in e.errors())[:300])
        for name, st in self.standings.items():
            try:
                Standing.model_validate(st)
            except ValidationError as e:
                self.add("schema", "error", f"standings/{name}.json", name,
                         "; ".join(x["msg"] for x in e.errors())[:300])
        for s in self.schools:
            try:
                School.model_validate(s)
            except ValidationError as e:
                self.add("schema", "error", "schools/schools.json", s.get("id"),
                         "; ".join(x["msg"] for x in e.errors())[:300])

    def c_missing_keys(self) -> None:
        expected = {f.alias or k for k, f in Player.model_fields.items()}
        for lg, ps in self.players.items():
            miss = Counter()
            ids = defaultdict(list)
            for p in ps:
                for k in expected - set(p):
                    miss[k] += 1
                    ids[k].append(p.get("id"))
            for k, n in miss.items():
                self.add("missing_key", "warn", self.pfile(lg), f"{n}件",
                         f"キー '{k}' 自体が欠落（null ではなく未定義）",
                         "生成元を schemas.Player.model_dump() 経由に統一して全キーを出力",
                         sample_ids=ids[k][:10])

    def c_dup_id(self) -> None:
        r = checks.check_dup_id(self.players)
        for e in r.errors:
            self.add("dup_id", "error", "players/*", e.split()[1], e,
                     "スクレイパーの二重取得を修正し再生成")
        for name, ms in self.matches.items():
            for k, n in Counter(m.get("id") for m in ms).items():
                if n > 1:
                    self.add("dup_id", "error", f"matches/{name}.json", k, f"{n}回出現")
        for lg, ts in self.teams.items():
            for k, n in Counter(t.get("id") for t in ts).items():
                if n > 1:
                    self.add("dup_id", "error", f"teams/{lg}.json", k, f"{n}回出現")
        tleague = defaultdict(list)
        for lg, ts in self.teams.items():
            for t in ts:
                tleague[t["id"]].append(lg)
        for tid, lgs in tleague.items():
            if len(lgs) > 1:
                self.add("dup_id", "error", "teams/*", tid, f"複数リーグに同一 team id: {lgs}")
        for k, n in Counter(s.get("id") for s in self.schools).items():
            if n > 1:
                self.add("dup_id", "error", "schools/schools.json", k, f"{n}回出現")
        for name, cs in self.callups.items():
            for k, n in Counter(c.get("id") for c in cs).items():
                if n > 1:
                    self.add("dup_id", "error", f"callups/{name}.json", k, f"{n}回出現")

    def c_slug(self) -> None:
        slug_ids: dict[str, set[str]] = defaultdict(set)
        for lg, ps in self.players.items():
            seen: dict[str, str] = {}
            for p in ps:
                s = p.get("slug")
                if not s:
                    continue
                slug_ids[s].add(p["id"])
                if s in seen and seen[s] != p["id"]:
                    self.add("dup_slug", "error", self.pfile(lg), s,
                             f"同一リーグ内で slug 衝突: {seen[s]} / {p['id']}",
                             "slug に数値IDサフィックスを付与するよう transform を修正")
                seen.setdefault(s, p["id"])
                pid = p["id"]
                if pid.startswith("ar_") and s != pid[3:]:
                    self.add("slug_id_mismatch", "warn", self.pfile(lg), pid,
                             f"slug={s!r} が id 由来の {pid[3:]!r} と不一致")
                if s.startswith("-") or s.endswith("-") or "--" in s:
                    self.add("slug_format", "warn", self.pfile(lg), pid,
                             f"slug={s!r} に先頭/末尾/連続ハイフン（元ページslug由来の可能性）",
                             "URLとして残すかは all.rugby 側slugを確認のうえ判断", needs_official=True)
                m = re.fullmatch(r"lo_(\d+)", pid)
                if m and not s.endswith("-" + m.group(1)):
                    self.add("slug_id_mismatch", "warn", self.pfile(lg), pid,
                             f"slug={s!r} が数値ID {m.group(1)} で終わらない")
        for s, ids in slug_ids.items():
            if len(ids) > 1:
                resolved = {self.player_merges.get(i, i) for i in ids}
                if len(resolved) > 1:
                    self.add("dup_slug", "error", "players/*", s,
                             f"リーグ横断で別 id が同一 slug を使用: {sorted(ids)}",
                             "同一人物なら player_merges.json に登録、別人なら slug を分離")

    def c_cross_league_conflict(self) -> None:
        fields = ("name_en", "name_ja", "birthdate", "height_cm", "weight_kg")
        for pid, recs in self.by_id.items():
            if len(recs) < 2:
                continue
            diffs = {}
            for f in fields:
                vals = {}
                for lg, p in recs:
                    v = p.get(f)
                    if v is None:
                        continue
                    key = normalize_name_en(v) if f == "name_en" else (
                        self.norm_ja(v) if f == "name_ja" else v)
                    vals.setdefault(key, []).append(f"{lg}:{v}")
                if len(vals) > 1:
                    diffs[f] = [x for vs in vals.values() for x in vs]
            if diffs:
                hard = {"birthdate", "name_en", "name_ja"} & set(diffs)
                self.add("cross_league_conflict", "error" if hard else "warn", "players/*", pid,
                         f"同一 id がリーグ間で値不一致: {', '.join(diffs)}",
                         "fresher な scraped_at 側を正とするルールを transform に実装し再生成。"
                         "身長体重はソース間で異なり得るため公式ページで確認",
                         needs_official=bool(hard), values=diffs)

    def c_dup_person(self) -> None:
        r = checks.check_dup_person(self.players)
        for e in r.errors:
            self.add("dup_person", "error", "players/*", e, e,
                     "同一人物なら一方を除去（スクレイパー修正）")
        # name_ja + birthdate（name_en が無いレコード向け）
        for lg, ps in self.players.items():
            seen: dict[tuple, str] = {}
            for p in ps:
                if not p.get("name_ja") or not p.get("birthdate"):
                    continue
                k = (self.norm_ja(p["name_ja"]), p["birthdate"], p.get("squad"))
                if k in seen and seen[k] != p["id"]:
                    self.add("dup_person", "error", self.pfile(lg), p["id"],
                             f"name_ja+birthdate+squad が {seen[k]} と一致",
                             "同一人物なら一方を除去")
                seen.setdefault(k, p["id"])

    def c_same_name_no_birthdate(self) -> None:
        """birthdate 欠損で dup_person を素通りする同名・同チーム（同校）重複。"""
        for lg, ps in self.players.items():
            groups: dict[tuple, list[str]] = defaultdict(list)
            for p in ps:
                org = p.get("team_id") or ((p.get("education") or [{}])[0].get("name_raw"))
                if p.get("name_en"):
                    groups[("en", normalize_name_en(p["name_en"]), org, p.get("squad"))].append(p["id"])
                if p.get("name_ja"):
                    groups[("ja", self.norm_ja(p["name_ja"]), org, p.get("squad"))].append(p["id"])
            done = set()
            for k, ids in groups.items():
                ids = sorted(set(ids))
                if len(ids) < 2 or tuple(ids) in done:
                    continue
                done.add(tuple(ids))
                self.add("dup_person_same_org", "error", self.pfile(lg), ",".join(ids),
                         f"同リーグ・同所属({k[2]})・同名({k[1]})で id が別",
                         "片方が手動/告知由来(lo_announced_ 等)なら公式名鑑掲載後に除去。"
                         "別人（同姓同名）かは公式名鑑で確認", needs_official=True)

    def c_cross_person(self) -> None:
        r = checks.check_cross_person(self.players, self.player_merges)
        computed = {tuple(sorted(m["id"] for m in c["members"])) for c in r.merge_candidates}
        stored = {tuple(sorted(m["id"] for m in c.get("members", []))) for c in self.merge_candidates}
        for c in r.merge_candidates:
            ids = sorted({m["id"] for m in c["members"]})
            self.add("cross_person", "warn", "players/*", ",".join(ids),
                     f"name_en+birthdate 一致の別 id（{c['name_en_normalized']} {c['birthdate']}）",
                     "公式名鑑で同一人物確認後 data/manual/player_merges.json に登録",
                     needs_official=True)
        for ids in stored - computed:
            self.add("merge_candidates_stale", "warn", "_meta/merge_candidates.json", ",".join(ids),
                     "記録済み候補が現データでは再現しない（解決済み or id消滅）",
                     "次回 run で再生成")
        for ids in computed - stored:
            self.add("merge_candidates_stale", "warn", "_meta/merge_candidates.json", ",".join(ids),
                     "現データの候補が merge_candidates.json に未記録", "次回 run で再生成")
        # name_ja + birthdate の横断一致（name_en 表記が異なる日本人選手向け）
        groups: dict[tuple, set[str]] = defaultdict(set)
        for lg, ps in self.players.items():
            for p in ps:
                if p.get("name_ja") and p.get("birthdate"):
                    groups[(self.norm_ja(p["name_ja"]), p["birthdate"])].add(p["id"])
        for k, ids in groups.items():
            canon = {self.player_merges.get(i, i) for i in ids}
            if len(canon) > 1:
                self.add("cross_person_ja", "warn", "players/*", ",".join(sorted(ids)),
                         f"name_ja+birthdate 一致の別 id（{k[0]} {k[1]}）、player_merges 未登録",
                         "公式名鑑で同一人物確認後 player_merges.json に登録", needs_official=True)

    def c_merges(self) -> None:
        for src, dst in self.player_merges.items():
            if src == dst:
                self.add("merge_ref", "error", "manual/player_merges.json", src, "自己参照")
            if dst not in self.all_ids:
                self.add("merge_ref", "error", "manual/player_merges.json", f"{src}->{dst}",
                         "canonical 側 id が master に存在しない（参照切れ）",
                         "canonical を現存 id に付け替え")
            if dst in self.player_merges:
                self.add("merge_ref", "warn", "manual/player_merges.json", f"{src}->{dst}",
                         f"多段マージ（{dst} もさらに {self.player_merges[dst]} へマージ）",
                         "最終 canonical へ直接向ける")
            if src not in self.all_ids:
                self.add("merge_ref", "info", "manual/player_merges.json", src,
                         "マージ元 id が現 master に無い（既に統合済み or 離脱）")

    def c_team_ref_roster(self) -> None:
        all_players = [p for ps in self.players.values() for p in ps]
        all_teams = [t for ts in self.teams.values() for t in ts]
        for e in checks.check_team_ref(all_players, all_teams).errors:
            self.add("team_ref", "error", "players/*", e.split()[1], e, "teams 側を再取得")
        for e in checks.check_roster_sym(all_players, all_teams).errors:
            self.add("roster_sym", "error", "teams/*", e.split()[1], e,
                     "同一 run で players と teams を同時再生成")
        team_of: dict[str, list[str]] = defaultdict(list)
        for lg, ts in self.teams.items():
            for t in ts:
                for k, n in Counter(t.get("roster_ids", [])).items():
                    if n > 1:
                        self.add("roster_dup", "error", f"teams/{lg}.json", t["id"], f"roster_ids に {k} が{n}回")
                for pid in set(t.get("roster_ids", [])):
                    team_of[pid].append(t["id"])
                    leagues = self.all_ids.get(pid, [])
                    if pid in self.all_ids and lg not in leagues:
                        self.add("roster_league", "error", f"teams/{lg}.json", t["id"],
                                 f"roster の {pid} が players/{lg}.json に無く {leagues} にのみ存在")
        combos = Counter(tuple(sorted(ts)) for ts in team_of.values() if len(ts) > 1)
        for combo, n in combos.most_common():
            if n >= 3:
                self.add("roster_contamination", "error", "teams/*", "+".join(combo),
                         f"{n} 人が同時に {combo} の full roster に重複所属。"
                         "同一組み合わせへの集中はスクレイパーが別クラブのスカッドページを混入させた疑い",
                         "該当クラブの squad ページ取得処理（URL・ページング・キャッシュ）を確認し再取得",
                         needs_official=True)
        for pid, ts in team_of.items():
            if len(ts) > 1:
                self.add("roster_multi_team", "warn", "teams/*", pid,
                         f"複数チームの roster に所属: {ts}", "移籍途中の可能性。公式名鑑で現所属確認",
                         needs_official=True)
        for lg, ps in self.players.items():
            for p in ps:
                tid = p.get("team_id")
                if tid and tid in self.team_by_id and lg in TEAM_LEAGUES:
                    tlg = self.team_by_id[tid][0]
                    if tlg != lg:
                        self.add("team_league_mismatch", "error", self.pfile(lg), p["id"],
                                 f"team_id={tid} は teams/{tlg}.json 所属")

    def c_teams(self) -> None:
        for lg, ts in self.teams.items():
            for t in ts:
                tid = t["id"]
                if t.get("name_en") and t["name_en"] == tid:
                    self.add("team_name_placeholder", "warn", f"teams/{lg}.json", tid,
                             f"name_en={t['name_en']!r} が id slug と同一（正式名未取得）",
                             "公式表記をソースから取得（推測で埋めない）", needs_official=True)
                if not t.get("name_ja") and not (t.get("name_en") and t["name_en"] != tid):
                    self.add("team_name_missing", "warn", f"teams/{lg}.json", tid,
                             "表示可能なチーム名が無い（name_ja=null かつ name_en=slug）")
                u = t.get("source_url", "")
                m = re.search(r"/team/(\d+)", u)
                if m and tid.startswith("lo_team_") and tid != f"lo_team_{m.group(1)}":
                    self.add("team_source_mismatch", "error", f"teams/{lg}.json", tid,
                             f"source_url {u} と id 不一致")
                m = re.search(r"/club/([^/]+)/", u)
                if m and m.group(1) != tid:
                    self.add("team_source_mismatch", "warn", f"teams/{lg}.json", tid,
                             f"source_url の club slug {m.group(1)!r} と id 不一致")
                if not t.get("roster_ids"):
                    self.add("team_empty_roster", "warn", f"teams/{lg}.json", tid, "roster_ids が空")
        # 同名チーム（表記ゆれ）
        names = defaultdict(list)
        for lg, ts in self.teams.items():
            for t in ts:
                for n in (t.get("name_ja"), t.get("name_en")):
                    if n:
                        names[self.norm_ja(n).lower()].append(t["id"])
        for n, ids in names.items():
            if len(set(ids)) > 1:
                self.add("team_name_dup", "warn", "teams/*", ",".join(sorted(set(ids))),
                         f"同一チーム名 {n!r} が複数 id")

    def c_standings(self) -> None:
        for name, st in self.standings.items():
            f = f"standings/{name}.json"
            lg = st.get("league")
            rows = st.get("rows", [])
            league_teams = {t["id"] for t in self.teams.get(lg, [])}
            if st.get("season") in (None, "", "unknown"):
                self.add("standings_season", "error", f, name, f"season={st.get('season')!r}",
                         "ソースページからシーズン表記を取得してファイル名ごと修正", needs_official=True)
            ranks = [r["rank"] for r in rows]
            if len(set(ranks)) != len(ranks):
                self.add("standings_rank", "error", f, name, f"rank 重複: {ranks}")
            exp = list(range(1, len(league_teams) + 1)) if league_teams else []
            missing_ranks = sorted(set(exp) - set(ranks))
            if missing_ranks:
                self.add("standings_rows_missing", "error", f, name,
                         f"rank 欠番 {missing_ranks}（{len(rows)}行 / teams {len(league_teams)}チーム）",
                         "欠落行は数値欠落で除外された可能性（last_run warnings参照）。"
                         "公式順位表で再取得", needs_official=True,
                         missing_teams=sorted(league_teams - {r['team_id'] for r in rows}))
            for r in rows:
                if r["team_id"] not in league_teams:
                    self.add("standings_team_ref", "error", f, r["team_id"], f"teams/{lg}.json に無い team_id")
                if r["played"] != r["won"] + r["drawn"] + r["lost"]:
                    self.add("standings_sum", "error", f, r["team_id"],
                             f"played={r['played']} != W+D+L")
                if r["points"] < 4 * r["won"] + 2 * r["drawn"]:
                    self.add("standings_points", "warn", f, r["team_id"],
                             f"points={r['points']} < 4*won+2*drawn={4*r['won']+2*r['drawn']}"
                             "（勝点4/引分2の一般的方式と矛盾。減点処分等の可能性）",
                             needs_official=True)
            srt = sorted(rows, key=lambda r: r["rank"])
            for a, b in zip(srt, srt[1:]):
                if b["points"] > a["points"]:
                    self.add("standings_order", "warn", f, f"{a['team_id']}>{b['team_id']}",
                             f"rank{a['rank']}({a['points']}pt) < rank{b['rank']}({b['points']}pt)",
                             needs_official=True)
            played = Counter(r["played"] for r in rows)
            if len(played) > 1:
                self.add("standings_played_spread", "info", f, name, f"played の分布 {dict(played)}",
                         "試合消化数が揃わない（延期・未消化）可能性。最終順位なら要確認",
                         needs_official=True)
            if rows and not missing_ranks:
                w = sum(r["won"] for r in rows)
                l = sum(r["lost"] for r in rows)
                d = sum(r["drawn"] for r in rows)
                if w != l or d % 2:
                    self.add("standings_balance", "warn", f, name,
                             f"Σwon={w} Σlost={l} Σdrawn={d}（リーグ内対戦のみなら W=L・D偶数）",
                             needs_official=True)
            ts = self.parse_ts(st.get("scraped_at"))
            tmax = max((self.parse_ts(t.get("scraped_at")) for t in self.teams.get(lg, [])
                        if self.parse_ts(t.get("scraped_at"))), default=None)
            if ts and tmax and tmax - ts > timedelta(days=STALE_DAYS):
                self.add("standings_stale", "warn", f, name,
                         f"scraped_at={st['scraped_at']} が teams 最新 {tmax.isoformat()} より{(tmax-ts).days}日古い",
                         "standings スクレイプが失敗し旧データ残存の可能性。再取得")
        seasons = defaultdict(set)
        for st in self.standings.values():
            seasons[st.get("league")].add(st.get("season"))

    def c_matches(self) -> None:
        all_team_ids = set(self.team_by_id)
        callup_ts = [c for cs in self.callups.values() for c in cs]
        for name, ms in self.matches.items():
            f = f"matches/{name}.json"
            ids_used = Counter()
            pairs = defaultdict(list)
            for m in ms:
                mid = m.get("id")
                for side in ("home_team_id", "away_team_id"):
                    tid = m.get(side)
                    ids_used[tid] += 1
                    if tid not in all_team_ids:
                        self.add("match_team_ref", "error", f, mid,
                                 f"{side}={tid!r} が teams/*.json に存在しない",
                                 f"teams/{m.get('league')}.json（現在 {len(self.teams.get(m.get('league'), []))}件）を整備")
                for e in checks.check_match_sanity([m]).errors:
                    self.add("match_sanity", "error", f, mid, e)
                ko = self.parse_ts(m.get("kickoff_utc"))
                sc = self.parse_ts(m.get("scraped_at"))
                st = m.get("status")
                if st == "finished" and (m.get("home_score") is None or m.get("away_score") is None):
                    self.add("match_score_missing", "error", f, mid, "finished なのにスコア欠損")
                if ko and sc:
                    if st == "finished" and ko > sc:
                        self.add("match_date", "error", f, mid,
                                 f"kickoff {ko.isoformat()} が scraped_at {sc.isoformat()} より未来なのに finished")
                    if st == "scheduled" and ko + timedelta(hours=3) < sc:
                        self.add("match_date", "error", f, mid,
                                 f"kickoff {ko.isoformat()} を過ぎた scraped_at {sc.isoformat()} で scheduled のまま",
                                 needs_official=True)
                if ko and m.get("season") and re.fullmatch(r"\d{4}", m["season"]) and str(ko.year) != m["season"]:
                    self.add("match_season", "warn", f, mid, f"season={m['season']} と kickoff 年 {ko.year} 不一致")
                vr = m.get("venue_raw")
                if st == "finished" and vr in ("未定", "TBD", "TBC", ""):
                    self.add("match_venue", "warn", f, mid, f"finished なのに venue_raw={vr!r}（試合前の取得値が残存）",
                             "試合ページを再スクレイプして会場を更新", needs_official=True)
                if vr and m.get("home_team_id") == "japan" and re.fullmatch(r"[\x00-\x7f]+", vr):
                    ev = [c["id"] for c in callup_ts if c.get("kind") == "tour"]
                    self.add("match_home_away", "warn", f, mid,
                             f"home=japan だが venue_raw={vr!r} は英語表記（日本開催の他試合は日本語表記）。"
                             "JRFU のホーム/アウェイ表記規則か、ホーム/アウェイ逆転の可能性",
                             "公式試合ページでホーム/アウェイ区分を確認", needs_official=True,
                             tour_callups=ev)
                if ko:
                    pairs[(frozenset((m["home_team_id"], m["away_team_id"])), ko.date())].append(mid)
            for k, v in pairs.items():
                if len(v) > 1:
                    self.add("match_dup", "error", f, ",".join(v), "同一カード・同日の試合が複数")
            # 表記ゆれ: 似た team id（japan / japan-xv 等）
            tids = sorted(ids_used)
            for a in tids:
                for b in tids:
                    if a != b and b.startswith(a + "-"):
                        self.add("team_id_variant", "warn", f, f"{a}/{b}",
                                 f"類似 team id が混在（{a}: {ids_used[a]}件, {b}: {ids_used[b]}件）",
                                 "別チーム扱い（例: XV 名義の非テストマッチ）か同一チームの表記ゆれかを公式で確認",
                                 needs_official=True)

    def c_callups(self) -> None:
        nat = {p["id"]: p for p in self.players.get("national", [])}
        for name, cs in self.callups.items():
            f = f"callups/{name}.json"
            hist: dict[str, list[tuple]] = defaultdict(list)
            ordered = sorted((c for c in cs if str(c.get("news_id") or "").isdigit()),
                             key=lambda c: int(c["news_id"]))
            dated = [c for c in ordered if c.get("start_date")]
            for a, b in zip(dated, dated[1:]):
                if b["start_date"] < a["start_date"]:
                    self.add("callup_order", "error", f, f"{a['id']}>{b['id']}",
                             f"news_id 昇順（{a['news_id']}<{b['news_id']}）なのに start_date が逆転 "
                             f"（{a['start_date']} > {b['start_date']}）",
                             "記事の掲載年をスクレイパーで取得し start_date の年補完ロジックを修正",
                             needs_official=True)
            for c in cs:
                cid = c["id"]
                sc = self.parse_ts(c.get("scraped_at"))
                sd = c.get("start_date")
                mt = re.search(r"(\d{1,2})/(\d{1,2})更新", c.get("title", ""))
                if sd and sc:
                    sdd = datetime.fromisoformat(sd).replace(tzinfo=JST)
                    if sdd - sc > timedelta(days=120):
                        self.add("callup_date", "error", f, cid,
                                 f"start_date={sd} が scraped_at={c['scraped_at']} の{(sdd-sc).days}日後"
                                 f"（タイトル『{c.get('title')}』）。日付パース誤りの疑い",
                                 "本文の日付をスクレイパーで再取得", needs_official=True)
                if mt and sc:
                    upd = sc.replace(month=int(mt.group(1)), day=int(mt.group(2)))
                    if upd > sc + timedelta(days=1):
                        upd = upd.replace(year=upd.year - 1)
                    if sd:
                        sdd = datetime.fromisoformat(sd).replace(tzinfo=JST)
                        if c.get("kind") == "camp" and sdd > upd + timedelta(days=120):
                            pass  # callup_date で既出
                if c.get("kind") != "camp" and not sd:
                    self.add("callup_missing", "info", f, cid, f"kind={c.get('kind')} で start_date/venue が null")
                seen = Counter(mb.get("player_id") for mb in c.get("members", []) if mb.get("player_id"))
                for k, n in seen.items():
                    if n > 1:
                        self.add("callup_dup_member", "error", f, cid, f"{k} が {n} 回")
                for mb in c.get("members", []):
                    pid = mb.get("player_id")
                    nj = mb.get("name_ja") or ""
                    if re.search(r"[※＊*]|\d+\.\s*$", nj):
                        self.add("callup_name_annotation", "warn", f, f"{cid}:{pid}",
                                 f"name_ja={nj!r} に注記記号が混入", "スクレイパーで注記（※n.）を除去し別フィールド化")
                    if not pid:
                        self.add("callup_player_ref", "warn", f, cid, f"player_id=null: {mb.get('name_ja')}")
                        continue
                    rid = self.resolve_id(pid)
                    if rid is None:
                        self.add("callup_player_ref", "error", f, f"{cid}:{pid}",
                                 f"player_id が players/* にも player_merges にも無い（{nj}）")
                        continue
                    hist[pid].append((c.get("scraped_at"), c.get("news_id"), mb.get("caps"), cid))
                    for lg, p in self.by_id[rid]:
                        if mb.get("name_en") and p.get("name_en") and \
                                normalize_name_en(mb["name_en"]) != normalize_name_en(p["name_en"]):
                            self.add("callup_name_mismatch", "warn", f, f"{cid}:{pid}",
                                     f"callup name_en={mb['name_en']!r} / players/{lg} name_en={p['name_en']!r}",
                                     needs_official=True)
                        clean = re.sub(r"[※＊*].*$", "", nj)
                        if clean and p.get("name_ja") and self.norm_ja(clean) != self.norm_ja(p["name_ja"]):
                            self.add("callup_name_mismatch", "warn", f, f"{cid}:{pid}",
                                     f"callup name_ja={nj!r} / players/{lg} name_ja={p['name_ja']!r}",
                                     needs_official=True)
            for pid, h in hist.items():
                # 発表順は news_id（記事ID、単調増加）で判定する。scraped_at は再取得日時で発表順ではない
                h.sort(key=lambda x: int(x[1]) if str(x[1] or "").isdigit() else 0)
                caps_seq = [x[2] for x in h if x[2] is not None]
                for (a, b) in zip(h, h[1:]):
                    if a[2] is not None and b[2] is not None and b[2] < a[2]:
                        self.add("callup_caps_decrease", "error", f, pid,
                                 f"news_id 順でキャップが {a[3]}:{a[2]} → {b[3]}:{b[2]} に減少",
                                 "後発 callup のキャップ列パースずれ（列ずれ・注記混入）を疑い再取得",
                                 needs_official=True, sequence=caps_seq)
                latest = h[-1]
                p = nat.get(self.resolve_id(pid) or pid)
                if p and p.get("caps") and latest[2] is not None and p["caps"].get("count") is not None:
                    if p["caps"]["count"] != latest[2]:
                        self.add("callup_caps_vs_player", "warn", f, pid,
                                 f"最新 callup caps={latest[2]}（{latest[3]}）/ players/national caps={p['caps']['count']}"
                                 f"（{p['caps'].get('source_url')}）",
                                 "ソース・時点の差。公式記録で確認", needs_official=True)

    def c_episodes(self) -> None:
        for fn, ep in self.episodes.items():
            f = f"players/episodes/{fn}"
            pid = ep.get("player_id")
            if fn != f"{pid}.json":
                self.add("episode_ref", "warn", f, pid, "ファイル名と player_id 不一致")
            rid = self.resolve_id(pid) if pid else None
            if rid is None:
                self.add("episode_ref", "error", f, pid, "player_id が players/* にも player_merges にも無い",
                         "現存 id に付け替え（player_merges 登録 or ファイル名変更）")
            elif rid != pid:
                self.add("episode_ref", "warn", f, pid, f"マージ元 id を参照（canonical={rid}）",
                         "canonical id にリネーム")
            recs = self.by_id.get(rid or "", [])
            for lg, p in recs:
                if ep.get("name") and p.get("name_ja") and self.norm_ja(ep["name"]) != self.norm_ja(p["name_ja"]):
                    self.add("episode_name", "warn", f, pid, f"name={ep['name']!r} / players/{lg} name_ja={p['name_ja']!r}")
            for i, fact in enumerate(ep.get("facts", [])):
                u = fact.get("source_url") or ""
                host = (urlparse(u).hostname or "").lower()
                if not any(host == d or host.endswith("." + d) for d in ALLOWED_DOMAINS):
                    self.add("episode_source_domain", "info", f, f"{pid}#{i}",
                             f"source_url ドメイン {host} は ALLOWED_DOMAINS 外（03の許可リスト）",
                             "エピソードに許可リストを適用するか運用方針を人間が決定")
                for y, mo, d in re.findall(r"(\d{4})年(\d{1,2})月(\d{1,2})日[^。]{0,20}生まれ", fact.get("fact", "")):
                    bd = f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"
                    for lg, p in recs:
                        if p.get("birthdate") and p["birthdate"] != bd:
                            self.add("episode_birthdate", "error", f, pid,
                                     f"facts の生年月日 {bd} / players/{lg} birthdate={p['birthdate']}",
                                     needs_official=True)
                        if not p.get("birthdate"):
                            self.add("episode_birthdate", "info", f, pid,
                                     f"facts に生年月日 {bd} があるが players/{lg} birthdate=null（補完はしない）",
                                     needs_official=True)

    def c_names(self) -> None:
        kata = re.compile(r"^[\u30A0-\u30FF\u30FC・\s＝=]+$")
        per = defaultdict(lambda: defaultdict(list))
        for lg, ps in self.players.items():
            for p in ps:
                pid = p["id"]
                nj = p.get("name_ja")
                ne = p.get("name_en")
                nk = p.get("name_kana")
                if nj:
                    if nj != nj.strip():
                        per[lg]["name_ja 前後空白"].append(pid)
                    if re.search(r"\s{2,}", nj):
                        per[lg]["name_ja 連続空白"].append(pid)
                    if "\u3000" in nj:
                        per[lg]["name_ja 全角空白"].append(pid)
                    if re.search(r"\s・|・\s", nj):
                        per[lg]["name_ja 空白+中黒（例『ギディオン ・コーヘレンバーグ』）"].append(pid)
                    if re.search(r"[※＊*()（）]", nj):
                        per[lg]["name_ja 注記/括弧混入"].append(pid)
                    if re.search(r"[A-Za-z]", nj):
                        per[lg]["name_ja に英字"].append(pid)
                    if re.search(r"(学部|学科|大学|高校|高等学校|監督|コーチ|マネージャー|トレーナー|主将|部長)", nj):
                        self.add("name_not_person", "error", self.pfile(lg), pid,
                                 f"name_ja={nj!r} は人名でない語を含む（名簿パース時の見出し/所属行の誤取り込み疑い）",
                                 "名簿パーサの行判定を修正し再取得", needs_official=True)
                if ne:
                    if ne != ne.strip() or re.search(r"\s{2,}", ne):
                        per[lg]["name_en 空白異常"].append(pid)
                    if ne.isupper():
                        per[lg]["name_en 全大文字（ソース表記）"].append(pid)
                    if re.search(r"[^\x00-\x7f]", ne) and not re.search(r"[À-ž]", ne):
                        per[lg]["name_en に非ラテン文字"].append(pid)
                if nk is not None:
                    if re.search(r"[ぁ-ゖ]", nk):
                        per[lg]["name_kana がひらがな（他リーグはカタカナ）"].append(pid)
                    elif not kata.match(nk):
                        per[lg]["name_kana にカタカナ以外"].append(pid)
                if nj and ne is None and not nk and lg in TEAM_LEAGUES:
                    per[lg]["name_en/name_kana とも null"].append(pid)
        for lg, d in per.items():
            for k, ids in d.items():
                sev = "info" if "全大文字" in k else "warn"
                self.add("name_format", sev, self.pfile(lg), f"{len(ids)}件", k,
                         "transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形",
                         sample_ids=ids[:15])
        # 中黒/空白の区切り方式が同一リーグ内で混在
        for lg, ps in self.players.items():
            seps = Counter()
            for p in ps:
                nj = p.get("name_ja") or ""
                if re.fullmatch(r"[\u30A0-\u30FF・\s]+", nj) and len(nj) > 3:
                    seps["・" if "・" in nj else ("空白" if re.search(r"\s", nj) else "区切りなし")] += 1
            if len(seps) > 1:
                self.add("name_sep_mixed", "info", self.pfile(lg), lg,
                         f"カタカナ名の区切り記号が混在: {dict(seps)}")
        for oid in self.kana_overrides:
            if oid not in self.all_ids:
                self.add("kana_override_ref", "info", "manual/kana_overrides.json", oid,
                         "対象 id が master に無い（離脱/マージ済み）")
        for oid, v in self.kana_overrides.items():
            for lg, p in self.by_id.get(oid, []):
                if p.get("name_kana") and p["name_kana"] != v:
                    self.add("kana_override_conflict", "warn", self.pfile(lg), oid,
                             f"name_kana={p['name_kana']!r} と overrides={v!r} 不一致")

    def c_vocab(self) -> None:
        pos = defaultdict(Counter)
        nat = defaultdict(Counter)
        for lg, ps in self.players.items():
            for p in ps:
                if p.get("position"):
                    pos[lg][p["position"]] += 1
                for n in p.get("nationality") or []:
                    nat[n][lg] += 1
        for lg, c in pos.items():
            keys = set(c)
            variants = []
            if {"NO8", "NO.8"} <= {re.sub(r"[/・ ].*", "", k) for k in keys} or \
                    any("NO.8" in k for k in keys) and any(re.search(r"NO8", k) for k in keys):
                variants.append("NO8 / NO.8")
            seps = {s for k in keys for s in re.findall(r"[/・ ]", k)}
            if len(seps) > 1:
                variants.append(f"複数ポジション区切り {sorted(seps)}")
            if any(k in ("FW", "BK") for k in keys) and len(keys) > 2:
                variants.append("詳細ポジションと FW/BK 区分が混在")
            if variants:
                self.add("position_variant", "warn", self.pfile(lg), lg, "; ".join(variants),
                         "ポジション正規化表（NO.8→NO8、区切り→'/'）を transform に追加",
                         examples={k: v for k, v in c.items() if re.search(r"NO\.8|[・ ]|^FW$|^BK$", k)})
        styles = defaultdict(list)
        for n, lgs in nat.items():
            styles["ISO2" if re.fullmatch(r"[A-Z]{2}", n) else "英語国名"].append(n)
        if len(styles) > 1:
            self.add("nationality_variant", "warn", "players/*", "nationality",
                     f"国籍コード体系が混在: ISO2={styles['ISO2']}（{ {n: dict(nat[n]) for n in styles['ISO2']} }）",
                     "日本は 'Japan' と 'JP' が併存。どちらかに統一", examples={
                         n: dict(nat[n]) for n in ("JP", "Japan") if n in nat})
        for n in nat:
            if "-" in n:
                self.add("nationality_variant", "info", "players/*", n,
                         f"国名にハイフン（slug由来）: {dict(nat[n])}", "表示名へ変換")

    def c_source(self) -> None:
        latest: dict[str, datetime] = {}
        for lg, ps in self.players.items():
            ts = [self.parse_ts(p.get("scraped_at")) for p in ps]
            ts = [t for t in ts if t]
            if ts:
                latest[lg] = max(ts)
        now = datetime.now(JST)
        src_dom = defaultdict(Counter)
        for lg, ps in self.players.items():
            stale = []
            for p in ps:
                pid = p["id"]
                u = p.get("source_url") or ""
                host = (urlparse(u).hostname or "").lower()
                src_dom[p.get("source")][host.split(".", 1)[-1] if host.count(".") > 1 else host] += 1
                t = self.parse_ts(p.get("scraped_at"))
                if t is None:
                    self.add("scraped_at", "error", self.pfile(lg), pid, f"scraped_at 不正: {p.get('scraped_at')!r}")
                elif t > now + timedelta(hours=1):
                    self.add("scraped_at", "error", self.pfile(lg), pid, f"scraped_at が未来: {p['scraped_at']}")
                elif lg in latest and latest[lg] - t > timedelta(days=STALE_DAYS):
                    stale.append(pid)
                m = re.fullmatch(r"lo_(\d+)", pid)
                if m and not u.rstrip("/").endswith("/" + m.group(1)):
                    self.add("source_url_id", "error", self.pfile(lg), pid, f"source_url={u} と id 不一致")
                if pid.startswith("ar_") and p.get("source") == "all.rugby" and \
                        not u.rstrip("/").endswith("/" + pid[3:]):
                    self.add("source_url_id", "warn", self.pfile(lg), pid, f"source_url={u} と id 不一致")
                if p.get("source") not in ("league-one.jp", "all.rugby", "rugby-japan.jp",
                                           "university-club-site", "highschool-club-site"):
                    self.add("source_kind", "warn", self.pfile(lg), pid,
                             f"source={p.get('source')!r}（スクレイパー以外の由来。00 原則1）",
                             "公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去",
                             source_url=u)
            if stale:
                self.add("scraped_stale", "warn", self.pfile(lg), f"{len(stale)}件",
                         f"scraped_at がファイル内最新 {latest[lg].date()} より{STALE_DAYS}日超古い"
                         "（今回のスクレイプで更新されていない残存レコード）",
                         "離脱判定（pending_departures）との整合を確認", sample_ids=stale[:15])

    def c_career(self) -> None:
        for lg, ps in self.players.items():
            for p in ps:
                seen = Counter()
                for c in p.get("career") or []:
                    fr, to = c.get("from"), c.get("to")
                    if fr is not None and to is not None and fr > to:
                        self.add("career_range", "error", self.pfile(lg), p["id"],
                                 f"career {c.get('team')}: from={fr} > to={to}")
                    for y in (fr, to):
                        if y is not None and not (1980 <= y <= 2035):
                            self.add("career_range", "warn", self.pfile(lg), p["id"],
                                     f"career {c.get('team')}: 年 {y} が想定外")
                    seen[(c.get("team"), fr, to)] += 1
                for k, n in seen.items():
                    if n > 1:
                        self.add("career_dup", "warn", self.pfile(lg), p["id"], f"career 重複 {k} x{n}")
                bd = p.get("birthdate")
                if bd:
                    by = int(bd[:4])
                    for c in p.get("career") or []:
                        if c.get("from") is not None and c["from"] - by < 15:
                            self.add("career_age", "warn", self.pfile(lg), p["id"],
                                     f"career {c.get('team')} from={c['from']} 時点で {c['from']-by} 歳",
                                     needs_official=True)

    def c_age(self) -> None:
        for lg, ps in self.players.items():
            for p in ps:
                bd = p.get("birthdate")
                t = self.parse_ts(p.get("scraped_at"))
                if not bd or not t:
                    if p.get("is_minor") and not bd:
                        pass
                    continue
                b = datetime.fromisoformat(bd)
                age = t.year - b.year - ((t.month, t.day) < (b.month, b.day))
                if "is_minor" in p and bool(p["is_minor"]) != (age < 18):
                    self.add("is_minor", "error", self.pfile(lg), p["id"],
                             f"is_minor={p.get('is_minor')} だが birthdate={bd} から scraped_at 時点 {age} 歳")
                sq = p.get("squad") or ""
                m = re.fullmatch(r"u(\d+)", sq)
                if m:
                    lim = int(m.group(1))
                    age_year = t.year - b.year
                    if age_year > lim + AGE_GRADE_SLACK:
                        self.add("age_grade_age", "error", self.pfile(lg), p["id"],
                                 f"squad={sq} だが birthdate={bd}（{t.year}年に {age_year} 歳）",
                                 "生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認",
                                 needs_official=True, name=p.get("name_ja") or p.get("name_en"),
                                 source_url=p.get("source_url"))
                if lg in TEAM_LEAGUES and age < 17:
                    self.add("age_pro", "warn", self.pfile(lg), p["id"],
                             f"プロリーグ所属で {age} 歳（birthdate={bd}）", needs_official=True)

    def c_education_schools(self) -> None:
        sids = {s["id"] for s in self.schools}
        norm = defaultdict(list)
        for s in self.schools:
            n = unicodedata.normalize("NFKC", s["name"]).replace(" ", "").lower()
            n = n.replace("高等学校", "高校")
            norm[n].append(s["id"])
            if s.get("type") == "univ" and re.search(r"(高校|高等学校|high ?school|grammar|college$)", s["name"], re.I):
                self.add("school_type", "warn", "schools/schools.json", s["id"],
                         f"type=univ だが名称が高校系: {s['name']!r}")
            if s.get("type") == "hs" and re.search(r"大学|university", s["name"], re.I) and \
                    not re.search(r"(附属|付属|高|high)", s["name"], re.I):
                self.add("school_type", "warn", "schools/schools.json", s["id"],
                         f"type=hs だが名称が大学: {s['name']!r}")
        for n, ids in norm.items():
            if len(ids) > 1:
                self.add("school_name_variant", "warn", "schools/schools.json", ",".join(ids),
                         f"正規化後同名（高等学校/高校・空白・全半角）: {n}",
                         "school_aliases.json で統合")
        by_year = defaultdict(list)
        for lg, ps in self.players.items():
            for p in ps:
                for e in p.get("education") or []:
                    if e.get("school_id") and e["school_id"] not in sids:
                        self.add("school_ref", "error", self.pfile(lg), p["id"],
                                 f"education.school_id={e['school_id']!r} が schools.json に無い")
                    gy = e.get("grad_year")
                    t = self.parse_ts(p.get("scraped_at"))
                    if gy and t:
                        if lg == "highschool" and e.get("type") == "hs" and not (t.year <= gy <= t.year + 3):
                            by_year[(lg, "hs")].append((p["id"], gy))
                        if lg == "university" and e.get("type") == "univ" and not (t.year <= gy <= t.year + 4):
                            by_year[(lg, "univ")].append((p["id"], gy))
                    bd = p.get("birthdate")
                    if gy and bd:
                        diff = gy - int(bd[:4])
                        exp = 18 if e.get("type") == "hs" else 22
                        if abs(diff - exp) > 2:
                            self.add("grad_year_age", "warn", self.pfile(lg), p["id"],
                                     f"{e.get('type')} grad_year={gy} と birthdate={bd} の差 {diff}年",
                                     needs_official=True)
                if lg == "university" and p.get("education"):
                    if not any(e.get("type") == "univ" for e in p["education"]):
                        self.add("education_type", "warn", self.pfile(lg), p["id"], "大学レコードに univ education 無し")
                if lg == "highschool" and p.get("education"):
                    if not any(e.get("type") == "hs" for e in p["education"]):
                        self.add("education_type", "warn", self.pfile(lg), p["id"], "高校レコードに hs education 無し")
        for (lg, typ), items in by_year.items():
            self.add("grad_year_range", "warn", self.pfile(lg), f"{len(items)}件",
                     f"{typ} の grad_year が在籍中としてあり得ない範囲（卒業済み/過大）",
                     "名簿の学年→卒業年変換ロジックを確認", needs_official=True, samples=items[:15])
        refs = sum(1 for ps in self.players.values() for p in ps for e in p.get("education") or [] if e.get("school_id"))
        total = sum(1 for ps in self.players.values() for p in ps for e in p.get("education") or [])
        if total and refs == 0:
            self.add("school_ref", "warn", "players/*", f"{total}件",
                     "education.school_id が全件 null（schools.json と未接続）",
                     "migrate_schools の name_raw→school_id 解決を transform に組み込む")

    def c_caps(self) -> None:
        for lg, ps in self.players.items():
            for p in ps:
                c = p.get("caps")
                if not c:
                    continue
                if lg == "national" and p.get("team_id") and c.get("team"):
                    if normalize_name_en(c["team"]).replace(" ", "-") != p["team_id"]:
                        self.add("caps_team", "warn", self.pfile(lg), p["id"],
                                 f"caps.team={c['team']!r} と team_id={p['team_id']!r} 不一致")
                nat = p.get("nationality") or []
                if nat and c.get("team") and c["team"] not in nat and not (c["team"] == "Japan" and "JP" in nat):
                    self.add("caps_nationality", "info", self.pfile(lg), p["id"],
                             f"caps.team={c['team']!r} が nationality={nat} に含まれない")
        # 同一 id のリーグ間で caps 不一致
        for pid, recs in self.by_id.items():
            vals = {(p["caps"]["team"], p["caps"]["count"]) for _, p in recs if p.get("caps")}
            if len(vals) > 1:
                self.add("caps_conflict", "warn", "players/*", pid,
                         f"リーグ間で caps 不一致: {sorted(vals)}", "最新 scraped_at 側を採用",
                         needs_official=True)

    def c_meta(self) -> None:
        for lg, info in self.last_run.items():
            cnt = (info or {}).get("counts", {})
            if "players" in cnt and lg in self.players and cnt["players"] != len(self.players[lg]):
                self.add("last_run_count", "warn", "_meta/last_run.json", lg,
                         f"counts.players={cnt['players']} / 実件数 {len(self.players[lg])}")
            if "teams" in cnt and lg in self.teams and cnt["teams"] != len(self.teams[lg]):
                self.add("last_run_count", "warn", "_meta/last_run.json", lg,
                         f"counts.teams={cnt['teams']} / 実件数 {len(self.teams[lg])}")
        slugs = {p.get("slug") for ps in self.players.values() for p in ps}
        bad = [(k, v) for k, v in self.redirects.items() if v.rsplit("/", 1)[-1] not in slugs]
        if bad:
            self.add("redirect_target", "warn", "_meta/redirects.json", f"{len(bad)}件",
                     "リダイレクト先 slug が現 master に存在しない（404 になる）",
                     "retired 扱いに移すか、現 slug に付け替え", samples=bad[:15])
        src_live = [k for k in self.redirects if k.rsplit("/", 1)[-1] in slugs]
        if src_live:
            self.add("redirect_source_live", "warn", "_meta/redirects.json", f"{len(src_live)}件",
                     "リダイレクト元 slug が現 master の有効 slug と同一（現ページを潰す）",
                     samples=src_live[:15])
        chains = [k for k, v in self.redirects.items() if v in self.redirects]
        if chains:
            self.add("redirect_chain", "warn", "_meta/redirects.json", f"{len(chains)}件",
                     "多段リダイレクト", samples=chains[:15])
        rlive = [s for s in self.retired if s.rsplit("/", 1)[-1] in slugs]
        if rlive:
            self.add("retired_live", "warn", "_meta/retired_slugs.json", f"{len(rlive)}件",
                     "retired 扱いの slug が現 master で有効（復活済み）", "retired_slugs から除外",
                     samples=rlive[:15])
        rdup = set(self.retired) & set(self.redirects)
        if rdup:
            self.add("retired_redirect_both", "warn", "_meta/*", f"{len(rdup)}件",
                     "retired と redirects の両方に登録", samples=sorted(rdup)[:15])
        for lg, d in self.pending.items():
            present = {p["id"] for p in self.players.get(lg, [])}
            alive = [pid for pid in d if pid in present]
            if alive:
                self.add("pending_departure_alive", "warn", "_meta/pending_departures.json", lg,
                         f"離脱保留中の {len(alive)} 件が現 players/{lg}.json に存在",
                         "pending から除去（復帰扱い）", samples=alive[:15])
            for pid, rec in d.items():
                tid = (rec or {}).get("team_id")
                if lg in TEAM_LEAGUES and tid and tid not in self.team_by_id:
                    self.add("pending_team_ref", "info", "_meta/pending_departures.json", pid,
                             f"team_id={tid} が teams に無い")


# ---------------------------------------------------------------------- output
SEV_ORDER = {"error": 0, "warn": 1, "info": 2}


def to_markdown(findings: list[Finding]) -> str:
    out = ["# data/master 整合性監査 全件リスト（自動生成）", "",
           "生成: `python3 -m pipeline.validate.master_audit --md docs/renewal/validation_findings.md`", "",
           "| severity | 件数 |", "|---|---|"]
    sev = Counter(f.severity for f in findings)
    for s in ("error", "warn", "info"):
        out.append(f"| {s} | {sev.get(s, 0)} |")
    out.append("")
    by_check = defaultdict(list)
    for f in findings:
        by_check[f.check].append(f)
    for chk in sorted(by_check, key=lambda c: (min(SEV_ORDER[f.severity] for f in by_check[c]), c)):
        fs = by_check[chk]
        out.append(f"## {chk}（{len(fs)}件）")
        out.append("")
        out.append("| sev | file | target | 内容 | 修正案 | 公式確認 |")
        out.append("|---|---|---|---|---|---|")
        for f in sorted(fs, key=lambda x: (SEV_ORDER[x.severity], x.file, str(x.target))):
            ev = ""
            if f.evidence:
                ev = " / " + json.dumps(f.evidence, ensure_ascii=False)[:400]
            cell = lambda s: str(s).replace("|", "\\|").replace("\n", " ")
            out.append(f"| {f.severity} | {cell(f.file)} | {cell(f.target)} | {cell(f.detail + ev)} | "
                       f"{cell(f.proposal)} | {'要' if f.needs_official else ''} |")
        out.append("")
    return "\n".join(out) + "\n"


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=Path)
    ap.add_argument("--md", type=Path)
    args = ap.parse_args(list(argv) if argv is not None else None)
    for p in (args.json, args.md):
        if p and MASTER in p.resolve().parents:
            print("data/master/ への出力は禁止", file=sys.stderr)
            return 2
    findings = Audit().run()
    if args.json:
        args.json.write_text(json.dumps([asdict(f) for f in findings], ensure_ascii=False, indent=1),
                             encoding="utf-8")
    if args.md:
        args.md.write_text(to_markdown(findings), encoding="utf-8")
    c = Counter((f.severity, f.check) for f in findings)
    for (s, chk), n in sorted(c.items(), key=lambda x: (SEV_ORDER[x[0][0]], x[0][1])):
        print(f"{s:5} {chk:28} {n}")
    return 1 if any(f.severity == "error" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
