"""master/players/national.json（all.rugbyの現役代表スカッド）から
data/national_players_map.json を再生成する。
所属クラブは各リーグファイルへ slug（all.rugby系）→氏名（league-one）で突合して補完。
data/master は pipeline 以外書き換え禁止だが、本スクリプトは master を「読むだけ」で
表示用の派生ファイル national_players_map.json のみを書く。"""
import json, glob, os, re, collections

def norm(s):
    s = (s or "").lower()
    for a, b in [("'",""),("’",""),("-"," "),("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u"),("ñ","n")]:
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()

# 1) クラブ id -> 日本語表示名（teams master）
club_name = {}
for tf in glob.glob("data/master/teams/*.json"):
    data = json.load(open(tf))
    recs = data if isinstance(data, list) else list(data.values())
    for t in recs:
        if isinstance(t, dict) and t.get("id"):
            club_name[t["id"]] = t.get("name_ja") or t.get("name_en") or t["id"]

LEAGUE_JA = {"top14":"トップ14","urc":"URC","premiership":"プレミアシップ",
             "super-rugby":"スーパーラグビー","mlr":"MLR","league-one":"リーグワン",
             "nrl":"NRL"}

# 2) 選手 slug/氏名 -> (club_id, base_league, name_ja, name_kana)
by_slug, by_name = {}, {}
for fp in glob.glob("data/master/players/*.json"):
    lg = os.path.basename(fp)[:-5]
    if lg in ("national","sevens-national","age-grade","highschool"):
        continue
    base = "league-one" if lg.startswith("league-one") else lg
    for p in json.load(open(fp)):
        info = (p.get("team_id"), base, p.get("name_ja"), p.get("name_kana"))
        by_slug[p["slug"]] = info
        n = norm(p.get("name_en"))
        if n and n not in by_name:
            by_name[n] = info

# 3) national を国別に整形
nat = json.load(open("data/master/players/national.json"))
out = collections.defaultdict(list)
for p in nat:
    country = p.get("team_id")
    if not country:
        continue
    join = by_slug.get(p["slug"]) or by_name.get(norm(p.get("name_en")))
    club_id = base = jp = kana = None
    if join:
        club_id, base, jp, kana = join
    team_disp = club_name.get(club_id) if club_id else None
    if team_disp and team_disp == club_id:
        # teams master に和名が無いクラブ（super-rugby等）は slug を Title Case 表示
        team_disp = club_id.replace("-", " ").title()
    if not team_disp:
        team_disp = LEAGUE_JA.get(base, "—") if base else "—"
    caps = p.get("caps") or {}
    cnt = caps.get("count") if isinstance(caps, dict) else None
    out[country].append({
        "name_ja": jp or p.get("name_ja") or p.get("name_en") or p["slug"],
        "name_en": p.get("name_en") or "",
        "slug": p["slug"],
        "position": p.get("position") or "",
        "team": team_disp,
        "league": base or "national",
        "caps": f"代表({cnt})" if cnt is not None else "代表",
        "caps_display": str(cnt) if cnt is not None else "",
        "age": None,
        "height": str(p["height_cm"]) if p.get("height_cm") else "",
        "weight": str(p["weight_kg"]) if p.get("weight_kg") else "",
    })

# キャップ数の多い順に並べる
for c in out:
    out[c].sort(key=lambda x: int(x["caps_display"] or 0), reverse=True)

json.dump(out, open("data/national_players_map.json","w"), ensure_ascii=False, indent=1)
print("countries:", len(out), "| total:", sum(len(v) for v in out.values()))
# 突合率
joined = sum(1 for c in out for x in out[c] if x["team"] != "—")
print("club/league resolved:", joined, "/", sum(len(v) for v in out.values()))
for c in ["japan","fiji","zimbabwe","france"]:
    print(c, len(out[c]), "e.g.", [(x["name_ja"], x["team"], x["caps"]) for x in out[c][:2]])
