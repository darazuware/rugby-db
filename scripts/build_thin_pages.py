"""薄いページ（noindex対象）を data/manual/thin_pages.json に生成する（T6修正）。
選手: 独自本文が少ない（エピソード事実<3 かつ 公式IG無し）→ noindex。
チーム: docs/adsense/06_audit_textlen.tsv で本文800字未満だった /teams/{league}/{slug}/。
"""
import json, os, urllib.parse
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
players = json.load(open(f"{R}/data/manual/player_pages.json"))["players"]
ig = json.load(open(f"{R}/data/manual/instagram_embeds.json"))
pn = []
for p in players:
    f = f"{R}/data/master/players/episodes/{p['id']}.json"
    k = len(json.load(open(f)).get("facts", [])) if os.path.exists(f) else 0
    if k < 3 and p["slug"] not in ig:
        pn.append(p["slug"])
tn = []
for l in open(f"{R}/docs/adsense/06_audit_textlen.tsv"):
    u, n = l.split("\t")[:2]
    path = urllib.parse.unquote(u.replace("https://rugbypick.com", ""))
    if path.startswith("/teams/") and path.count("/") == 4 and int(n) < 800:
        tn.append(path)
json.dump({"players": sorted(pn), "teams": sorted(tn)}, open(f"{R}/data/manual/thin_pages.json", "w"), ensure_ascii=False, indent=1)
print(len(pn), len(tn))
