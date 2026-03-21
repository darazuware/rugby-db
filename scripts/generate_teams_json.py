import csv
import json
import os
import re
import unicodedata
from team_utils import get_team_info

def slugify(text):
    if not text: return ""
    # 日本語（ひらがな、カタカナ、漢字）が含まれているかチェック
    try:
        for char in text:
            name = unicodedata.name(char)
            if any(x in name for x in ['HIRAGANA', 'KATAKANA', 'CJK UNIFIED']):
                return "" # 日本語が含まれる場合は空を返す
    except:
        pass

    # アクセント除去 (NFD分解して結合文字を除く)
    text = unicodedata.normalize('NFD', text)
    text = "".join([c for c in text if not unicodedata.combining(c)])
    # 記号置換
    text = text.lower().replace(' ', '-').replace("'", '').replace('&', 'and')
    # アルファベット、数字、ハイフン以外を除去
    text = re.sub(r'[^a-z0-9-]', '', text)
    return text.strip('-')

def main():
    all_teams = []
    
    # 手動スラッグマッピング (アクセント記号や特殊な命名規則用)
    top14_slug_map = {
        "トゥールーズ": "toulouse",
        "ボルドー・ベグル": "bordeaux",
        "スタッド・フランセ": "paris",
        "トゥーロン": "toulon",
        "ラ・ロシェル": "la-rochelle",
        "ラシン92": "racing-92",
        "リヨン": "lyon",
        "カストル": "castres",
        "ポー": "pau",
        "ペルピニャン": "perpignan",
        "バイヨンヌ": "bayonne",
        "クレルモン": "clermont",
        "モンペリエ": "montpellier",
        "ヴァンヌ": "vannes"
    }
    
    prem_slug_map = {
        "ノーサンプトン・セインツ": "northampton-saints",
        "バース・ラグビー": "bath-rugby",
        "ブリストル・ベアーズ": "bristol-bears",
        "レスター・タイガーズ": "leicester-tigers",
        "エクセター・チーフス": "exeter-chiefs",
        "サラセンズ": "saracens",
        "セール・シャークス": "sale-sharks",
        "グロスター・ラグビー": "gloucester-rugby",
        "ハーレクインズ": "harlequins",
        "ニューカッスル・ファルコンズ": "newcastle-falcons"
    }

    # V27 Master CSV から全リーグのチームを抽出
    MASTER_CSV = 'data_sources/final_master_data_v27_normalized.csv'
    print(f"Extracting all teams from {MASTER_CSV}...")
    
    # リーグごとのチーム辞書
    leagues_teams = {
        'league-one': {},
        'super-rugby': {},
        'urc': {},
        'top14': {},
        'premiership': {}
    }

    if os.path.exists(MASTER_CSV):
        with open(MASTER_CSV, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                league = str(row.get('League', '')).strip().lower()
                if league == 'leagueone': league = 'league-one'
                if league not in leagues_teams: continue
                
                t_name = row.get('Current_Team')
                if not t_name or t_name.lower() == 'nan': continue
                
                if t_name not in leagues_teams[league]:
                    info = get_team_info(t_name)
                    jp_name = info.get('jp', t_name) if info else t_name
                    en_name = info.get('name_en', t_name) if info else t_name
                    
                    # スラッグ決定
                    slug = info['slug'] if info else slugify(en_name)
                    # 手動マッピング優先
                    if league == 'top14' and jp_name in top14_slug_map:
                        slug = top14_slug_map[jp_name]
                    elif league == 'premiership' and jp_name in prem_slug_map:
                        slug = prem_slug_map[jp_name]
                    
                    # 万が一スラッグが空の場合は名前から生成
                    if not slug:
                        slug = re.sub(r'[^a-z0-9-]+', '-', t_name.lower()).strip('-')

                    leagues_teams[league][t_name] = {
                        "team_name": jp_name,
                        "team_en_name": en_name,
                        "slug": slug,
                        "league": league
                    }

    # League One の詳細情報をマージ
    if os.path.exists('data/league_one_teams_detailed.json'):
        with open('data/league_one_teams_detailed.json', 'r', encoding='utf-8') as f:
            l1_details = json.load(f)
            for d in l1_details:
                for t_name, t_data in leagues_teams['league-one'].items():
                    if t_name == d['team_name'] or t_data['team_name'] == d['team_name']:
                        t_data.update({
                            "division": d.get('division'),
                            "host_area": d.get('host_area'),
                            "legal_entity": d.get('legal_entity'),
                            "official_site": d.get('official_site'),
                            "practice_ground": d.get('practice_ground')
                        })
                        break
    
    # 全チームをリスト化
    for league in leagues_teams:
        all_teams.extend(leagues_teams[league].values())

    # 重複排除 (名前 + リーグ + スラッグベース)
    unique_teams = []
    seen = set()
    for t in all_teams:
        key = f"{t['league']}-{t['team_name']}-{t['slug']}"
        if key not in seen:
            unique_teams.append(t)
            seen.add(key)

    with open('data/teams.json', 'w', encoding='utf-8') as f:
        json.dump(unique_teams, f, ensure_ascii=False, indent=2)
    
    print(f"Generated data/teams.json with {len(unique_teams)} teams.")

if __name__ == "__main__":
    main()
