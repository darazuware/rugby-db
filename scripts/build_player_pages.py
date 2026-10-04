#!/usr/bin/env python3
"""個別ページを残す選手リスト data/manual/player_pages.json を生成する（docs/adsense/01_DESIGN.md §1）。

基準（いずれか）:
  K1 日本代表・代表候補: team_id==japan / caps.team==Japan かつ count>0 / callups/national.json の members
  K2 独自素材あり: players/episodes/{id}.json / data/manual/instagram_embeds.json の slug
  K3 公開済みニュース2本以上が言及（/players/{slug}/ リンク or 一意な name_ja(4文字以上)）
  手動: 既存ファイルの force_include / force_exclude を引き継ぐ（ここだけ手編集可）

data/master は読み取りのみ。player_merges.json（dup→canonical）は適用済みとして扱う。
  python3 scripts/build_player_pages.py                 # 生成
  python3 scripts/build_player_pages.py --merge-candidates   # ar_→lo_ 統合候補を一覧表示
  python3 scripts/build_player_pages.py --write-merges        # 候補（生年月日一致のみ）を player_merges.json に追加
"""
import collections
import datetime
import glob
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MASTER = ROOT / "data/master"
MANUAL = ROOT / "data/manual"
OUT = MANUAL / "player_pages.json"
MENTION_MIN = 2
# 機械生成の週次キャップ一覧（*-caps-weekly-*）は同じ選手の数字を毎週並べるだけで独自の言及にならないため K3 から除外
# （含めると約467人に膨らむ。設計書の想定約315人に近づけるための補正）
EXCLUDE_NEWS = re.compile(r"-caps-weekly-")


def load_players():
    """id 重複はクラブ側(league!=national)を優先して1件に畳む（master.ts dedupePlayersById 相当）。"""
    by_id = {}
    for f in sorted(glob.glob(str(MASTER / "players/*.json"))):
        for p in json.load(open(f, encoding="utf-8")):
            ex = by_id.get(p["id"])
            if ex is None or (ex.get("league") == "national" and p.get("league") != "national"):
                merged = dict(ex or {})
                merged.update(p)
                for k in ("caps", "name_ja", "birthdate"):
                    if merged.get(k) is None and ex and ex.get(k) is not None:
                        merged[k] = ex[k]
                by_id[p["id"]] = merged
            else:
                for k in ("caps", "name_ja", "birthdate"):
                    if ex.get(k) is None and p.get(k) is not None:
                        ex[k] = p[k]
    return by_id


def norm_name(s):
    return " ".join(sorted(re.sub(r"[^a-z ]", " ", (s or "").lower()).split()))


def merge_candidates(players):
    """team_id==japan の ar_* と、英名一致で一意な lo_* の組。"""
    lo = collections.defaultdict(list)
    for p in players.values():
        if p["id"].startswith("lo_") and p.get("name_en"):
            lo[norm_name(p["name_en"])].append(p)
    out = []
    for p in players.values():
        if not p["id"].startswith("ar_") or not p.get("name_en"):
            continue
        if p.get("team_id") != "japan" and (p.get("caps") or {}).get("team") != "Japan":
            continue
        m = lo.get(norm_name(p["name_en"]), [])
        if len(m) == 1:
            out.append((p, m[0]))
    return out


def load_merges():
    f = MANUAL / "player_merges.json"
    return json.load(open(f, encoding="utf-8")) if f.exists() else {}


def resolve(pid, merges):
    seen = set()
    while pid in merges and pid not in seen:
        seen.add(pid)
        pid = merges[pid]
    return pid


def news_articles():
    """公開済み（draft除外）ニュースの (生本文, 空白除去済み本文)。"""
    res = []
    for fp in sorted(glob.glob(str(ROOT / "src/content/news/*.md"))):
        if EXCLUDE_NEWS.search(pathlib.Path(fp).name):
            continue
        text = pathlib.Path(fp).read_text(encoding="utf-8")
        body = text
        if text.startswith("---"):
            i = text.find("\n---", 3)
            if i != -1:
                fm, body = text[:i], text[i + 4:]
                if re.search(r"^draft:\s*true", fm, re.M):
                    continue
        res.append((body, re.sub(r"[ 　]", "", body)))
    return res


def main():
    players = load_players()
    cands = merge_candidates(players)
    merges = load_merges()

    if "--merge-candidates" in sys.argv or "--write-merges" in sys.argv:
        add = {}
        for ar, lo in cands:
            ok = ar.get("birthdate") and ar.get("birthdate") == lo.get("birthdate")
            state = "既存" if ar["id"] in merges else ("OK" if ok else "要確認(生年月日不一致)")
            print(f"{state:8} {ar['id']:32} {ar.get('birthdate')} -> {lo['id']:28} {lo.get('birthdate')} {lo.get('name_ja')} {lo.get('league')}")
            if ok and ar["id"] not in merges:
                add[ar["id"]] = lo["id"]
        print(f"新規 {len(add)} 件 / 候補 {len(cands)} 件")
        if "--write-merges" in sys.argv and add:
            merges.update(add)
            (MANUAL / "player_merges.json").write_text(
                json.dumps(merges, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print("player_merges.json に追加しました")
        return

    # 統合後の人物集合
    persons = {pid: p for pid, p in players.items() if pid not in merges or merges[pid] not in players}
    slug_to_pid = {}
    for pid, p in players.items():
        slug_to_pid[p["slug"]] = resolve(pid, merges) if resolve(pid, merges) in players else pid
    persons = {pid: p for pid, p in persons.items() if p.get("league") != "highschool"}

    reasons = collections.defaultdict(set)

    # K1
    for pid, p in persons.items():
        if p.get("team_id") == "japan":
            reasons[pid].add("K1")
        c = p.get("caps") or {}
        if c.get("team") == "Japan" and (c.get("count") or 0) > 0:
            reasons[pid].add("K1")
    cu = json.load(open(MASTER / "callups/national.json", encoding="utf-8"))
    for cup in cu if isinstance(cu, list) else []:
        for m in cup.get("members", []):
            pid = resolve(m.get("player_id"), merges)
            if pid in persons:
                reasons[pid].add("K1")

    # K2
    for f in glob.glob(str(MASTER / "players/episodes/*.json")):
        pid = resolve(pathlib.Path(f).stem, merges)
        if pid in persons:
            reasons[pid].add("K2")
    ig = json.load(open(MANUAL / "instagram_embeds.json", encoding="utf-8"))
    for slug in ig:
        pid = slug_to_pid.get(slug)
        if pid in persons:
            reasons[pid].add("K2")

    # K3: 人物ごとの言及記事数
    name_pids = collections.defaultdict(set)
    for pid, p in persons.items():
        nm = re.sub(r"[ 　]", "", p.get("name_ja") or "")
        if len(nm) >= 4:
            name_pids[nm].add(pid)
    unique_names = {nm: next(iter(s)) for nm, s in name_pids.items() if len(s) == 1}
    slugs_of = collections.defaultdict(set)
    for slug, pid in slug_to_pid.items():
        slugs_of[pid].add(slug)
    mention = collections.Counter()
    for raw, ns in news_articles():
        hit = set()
        # 個別ページ化していない選手へのリンク書換え後（link_news.py --fix-dead）の #p-{slug} も言及として数える
        for m in re.finditer(r"/players/([^/)\s]+)/|\(/[^)\s]*#p-([^)\s]+)\)", raw):
            pid = slug_to_pid.get(m.group(1) or m.group(2))
            if pid in persons:
                hit.add(pid)
        for nm, pid in unique_names.items():
            if nm in ns:
                hit.add(pid)
        for pid in hit:
            mention[pid] += 1
    for pid, n in mention.items():
        if n >= MENTION_MIN:
            reasons[pid].add("K3")

    # 手動
    prev = json.load(open(OUT, encoding="utf-8")) if OUT.exists() else {}
    force_in = prev.get("force_include", [])
    force_out = set(prev.get("force_exclude", []))
    for pid in force_in:
        pid = resolve(pid, merges)
        if pid in persons:
            reasons[pid].add("force")
    for pid in force_out:
        reasons.pop(pid, None)

    rows = []
    for pid in sorted(reasons):
        rows.append({"id": pid, "slug": persons[pid]["slug"], "reasons": sorted(reasons[pid])})

    # slug 衝突（別人物が同一 slug）は個別ページのパスが重複するため、ar_ 以外を優先して1件に絞る
    rows.sort(key=lambda r: (r["id"].startswith("ar_"), r["id"]))
    seen, uniq = set(), []
    for r in rows:
        if r["slug"] in seen:
            print("slug衝突で除外:", r["id"])
            continue
        seen.add(r["slug"])
        uniq.append(r)
    rows = sorted(uniq, key=lambda r: r["id"])

    OUT.write_text(json.dumps({
        "_note": "scripts/build_player_pages.py が生成。force_include/force_exclude のみ手編集可",
        "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "criteria": f"K1|K2|K3(mention>={MENTION_MIN})",
        "force_include": force_in,
        "force_exclude": sorted(force_out),
        "players": rows,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    by_league = collections.Counter(persons[r["id"]]["league"] for r in rows)
    by_reason = collections.Counter(x for r in rows for x in r["reasons"])
    print(f"indexable {len(rows)} / persons {len(persons)}")
    print("league:", dict(by_league.most_common()))
    print("reason:", dict(by_reason))


if __name__ == "__main__":
    main()
