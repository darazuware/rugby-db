import json

with open('unified_player_database_full.json', 'r') as f:
    players = json.load(f)

for p in players:
    if p.get('name_ja') == '繁松 哲大' or 'Shigematsu' in str(p.get('name_en')):
        print(json.dumps(p, indent=2, ensure_ascii=False))
