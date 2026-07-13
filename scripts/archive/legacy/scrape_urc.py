import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import os

BASE_URL = "https://all.rugby"
TOURNAMENT_URL = f"{BASE_URL}/tournament/urc/table"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

POS_MAP = {
    'Prop': 'PR',
    'Hooker': 'HO',
    'Lock': 'LO',
    'Flanker': 'FL',
    'Number 8': 'No8',
    'Number8': 'No8',
    'Scrum-half': 'SH',
    'Fly-half': 'SO',
    'Center': 'CTB',
    'Centre': 'CTB',
    'Wing': 'WTB',
    'Full-back': 'FB',
    'Fullback': 'FB'
}

def get_teams():
    print(f"Fetching teams from {TOURNAMENT_URL}...")
    response = requests.get(TOURNAMENT_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    teams = []
    # URCの順位表テーブルからチームリンクを取得
    for a in soup.select('.classement table tr td a[href^="/club/"]'):
        team_name_span = a.select_one('span.tiny-hidden')
        if team_name_span:
            name = team_name_span.text.strip()
            link = a['href']
            # 重複排除
            if name and link not in [t['link'] for t in teams]:
                teams.append({'name': name, 'link': f"{BASE_URL}{link}/squad"})
    
    return teams

def get_squad(team_url, team_name):
    print(f"Fetching squad for {team_name} from {team_url}...")
    try:
        response = requests.get(team_url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        players = []
        rows = soup.select('table tbody tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 7:
                continue
                
            name_link = cols[1].find('a')
            if not name_link:
                continue
                
            player_name = name_link.text.strip()
            player_url = f"{BASE_URL}{name_link['href']}"
            position_raw = cols[2].text.strip()
            position = POS_MAP.get(position_raw, position_raw)
            
            birth_date = cols[4].text.strip()
            height = cols[5].text.strip()
            weight = cols[6].text.strip()
            
            formatted_birth = ""
            if birth_date and '/' in birth_date:
                parts = birth_date.split('/')
                if len(parts) == 3:
                    formatted_birth = f"{parts[2]}.{parts[1]}.{parts[0]}"
            elif birth_date.isdigit() and len(birth_date) == 4:
                formatted_birth = f"{birth_date}.01.01"
            
            height_num = re.search(r'(\d+\.?\d*)', height)
            height_val = str(int(float(height_num.group(1)) * 100)) if height_num and 'm' in height else (height_num.group(1) if height_num else "")
            
            weight_num = re.search(r'(\d+)', weight)
            weight_val = weight_num.group(1) if weight_num else ""

            players.append({
                '英語名': player_name,
                '選手名': player_name,
                'ポジション': position,
                '所属チーム': team_name,
                '身長': height_val,
                '体重': weight_val,
                '生年月日': formatted_birth,
                'URL': player_url
            })
            
        return players
    except Exception as e:
        print(f"Error fetching squad for {team_name}: {e}")
        return []

def get_player_details(player_url):
    print(f"Fetching details for player: {player_url}")
    try:
        response = requests.get(player_url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        nationality = ""
        bio_items = soup.select('.bio div')
        for i, item in enumerate(bio_items):
            if "Nationality" in item.text:
                if i + 1 < len(bio_items):
                    nationality = bio_items[i+1].get_text(strip=True)
                    nationality = re.sub(r'Nationality\s*#\d+\s*', '', nationality).strip()
                break
        
        career_items = []
        parcours = soup.select('.parcours li')
        for item in parcours:
            career_items.append(item.get_text(strip=True))
        
        full_career = " -> ".join(career_items) if career_items else ""
        
        return {
            'Full_Career': full_career,
            'キャリア遍歴': full_career,
            'International_Caps': nationality,
            '代表キャップ数': nationality
        }
    except Exception as e:
        print(f"Error fetching player details: {e}")
        return {'Full_Career': "", 'キャリア遍歴': "", 'International_Caps': "", '代表キャップ数': ""}

def main(sample_only=True):
    teams = get_teams()
    if not teams:
        print("No teams found.")
        return

    all_data = []
    target_teams = teams[:2] if sample_only else teams
    
    for team in target_teams:
        players = get_squad(team['link'], team['name'])
        target_players = players[:10] if sample_only else players
        
        for p in target_players:
            details = get_player_details(p['URL'])
            p.update(details)
            p.update({
                '年齢': '',
                '高校': '',
                '大学': '',
                'カテゴリ': 'A',
                'Scraped_Url': p['URL']
            })
            all_data.append(p)
            time.sleep(1)
            
    output_file = "data_sources/urc_full.csv"
    if sample_only:
        output_file = "data_sources/urc_sample.csv"

    fieldnames = [
        '英語名', '選手名', 'ポジション', '所属チーム', '身長', '体重', '生年月日', 
        '年齢', '高校', '大学', '出身校・チーム歴(全文)', 'カテゴリ', 
        'URL', 'キャリア遍歴', '代表キャップ数', 'International_Caps', 
        'Scraped_Url', 'Full_Career'
    ]
    
    with open(output_file, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for data in all_data:
            row = {fn: data.get(fn, '') for fn in fieldnames}
            writer.writerow(row)
            
    print(f"Successfully saved {len(all_data)} players to {output_file}")

if __name__ == "__main__":
    # 本番実行
    main(sample_only=False)
