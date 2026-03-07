import csv
import json
import os

import unicodedata

from team_utils import get_team_info

def slugify(text):
    if not text: return ""
    # アクセント除去
    text = unicodedata.normalize('NFD', text)
    text = "".join([c for c in text if not unicodedata.combining(c)])
    # 英語名以外（日本語など）が残っている場合は、既存のマッピングに頼るべきだが、
    # 最小限の処理として記号置換のみ行う
    return text.lower().replace(' ', '-').replace("'", '').replace('&', 'and').replace('é', 'e').replace('è', 'e').strip('-')

def extract_teams_from_csv(csv_path, league):
    teams = set()
    if not os.path.exists(csv_path):
        return []
    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('所属チーム'):
                teams.add(row['所属チーム'])
    
    unique_teams = []
    for t in sorted(list(teams)):
        info = get_team_info(t)
        if info:
            unique_teams.append({
                "team_name": info.get('jp', t),
                "slug": info['slug'],
                "league": info['league']
            })
        else:
            unique_teams.append({"team_name": t, "slug": slugify(t), "league": league})
    return unique_teams

def main():
    all_teams = []

    # League One (既存の詳細 JSON を利用)
    if os.path.exists('data/league_one_teams_detailed.json'):
        with open('data/league_one_teams_detailed.json', 'r', encoding='utf-8') as f:
            l1_raw = json.load(f)
            for t in l1_raw:
                info = get_team_info(t['team_name'])
                if info:
                    all_teams.append({
                        "team_name": t['team_name'],
                        "slug": info['slug'],
                        "league": info['league'],
                        "division": t.get('division'),
                        "host_area": t.get('host_area'),
                        "legal_entity": t.get('legal_entity')
                    })
                else:
                    all_teams.append({
                        "team_name": t['team_name'],
                        "slug": slugify(t['team_name']),
                        "league": "league-one",
                        "division": t.get('division'),
                        "host_area": t.get('host_area'),
                        "legal_entity": t.get('legal_entity')
                    })

    # Super Rugby
    all_teams.extend(extract_teams_from_csv('data_sources/super_rugby_full.csv', 'super-rugby'))

    # URC (サイトには掲載しないため除外)
    # all_teams.extend(extract_teams_from_csv('data_sources/urc_full.csv', 'urc'))

    # Top 14
    if os.path.exists('data/top14_teams.json'):
        with open('data/top14_teams.json', 'r', encoding='utf-8') as f:
            top14_raw = json.load(f)
            for t in top14_raw:
                all_teams.append({
                    "team_name": t['name_ja'],
                    "team_en_name": t['name'],
                    "slug": t['slug'],
                    "league": "top14"
                })

    # 重複排除 (名前ベース)
    seen = set()
    unique_teams = []
    for t in all_teams:
        league = t['league']
        if league == 'leagueone': league = 'league-one'
        
        key = f"{league}-{t['team_name']}"
        if key not in seen:
            t['league'] = league
            unique_teams.append(t)
            seen.add(key)

    with open('data/teams.json', 'w', encoding='utf-8') as f:
        json.dump(unique_teams, f, ensure_ascii=False, indent=2)
    
    print(f"Generated data/teams.json with {len(unique_teams)} teams.")

if __name__ == "__main__":
    main()
