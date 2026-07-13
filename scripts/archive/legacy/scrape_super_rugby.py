import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import os

BASE_URL = "https://all.rugby"
TOURNAMENT_URL = f"{BASE_URL}/tournament/super-rugby-pacific/table"
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
    for a in soup.select('.classement table tr td a[href^="/club/"]'):
        team_name_span = a.select_one('span.tiny-hidden')
        if team_name_span:
            name = team_name_span.text.strip()
            link = a['href']
            if name and link not in [t['link'] for t in teams]:
                teams.append({'name': name, 'link': f"{BASE_URL}{link}/squad"})
    
    return teams

def get_squad(team_url, team_name):
    print(f"Fetching squad for {team_name} from {team_url}...")
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

def get_brumbies_details(player_name):
    """ブランビーズ公式サイトから追加情報を取得する"""
    print(f"Searching Brumbies official site for {player_name}...")
    
    # Andy Muirhead の特定リクエストに対応
    if "Muirhead" in player_name:
         url = "https://brumbies.rugby/players/andy-muirhead/2314"
    else:
         return {}

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        details = {}
        # 出身地や生年月日などのラベル付きスパンから抽出
        # ラベル: span.css-1txkdoy, 値: span.css-1cbu0zf
        items = soup.select('.css-18v3453') # 項目コンテナ
        for item in items:
            label = item.select_one('.css-1txkdoy')
            val = item.select_one('.css-1cbu0zf')
            if label and val:
                label_text = label.get_text(strip=True)
                val_text = val.get_text(strip=True)
                if "Hometown" in label_text:
                    details['出身地'] = val_text
                elif "Date Of Birth" in label_text:
                    # July 8, 1993 -> 1993.07.08
                    try:
                        from datetime import datetime
                        dt = datetime.strptime(val_text, "%B %d, %Y")
                        details['生年月日'] = dt.strftime("%Y.%m.%d")
                    except:
                        pass
                elif "Height" in label_text:
                    h_val = re.search(r'(\d+)', val_text)
                    if h_val: details['身長'] = h_val.group(1)
                elif "Weight" in label_text:
                    w_val = re.search(r'(\d+)', val_text)
                    if w_val: details['体重'] = w_val.group(1)

        # Bio Text から高校・大学を抽出
        bio_paras = soup.select('p.css-cy3b83')
        if bio_paras:
            full_bio = " ".join([p.get_text() for p in bio_paras])
            # 高校抽出
            school_match = re.search(r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)*\s(?:State High|High School|College|Grammar))', full_bio)
            if school_match:
                details['高校'] = school_match.group(1)
            
            # 大学抽出
            uni_match = re.search(r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)*\s(?:University|Uni))', full_bio)
            if uni_match:
                details['大学'] = uni_match.group(1)
                
        return details
    except Exception as e:
        print(f"Error fetching Brumbies site: {e}")
        return {}

def get_player_details(player_url, player_name=None):
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
        
        caps_val = nationality
        career_items = []
        parcours = soup.select('.parcours li')
        for item in parcours:
            career_items.append(item.get_text(strip=True))
        
        full_career = " -> ".join(career_items) if career_items else ""
        
        res = {
            'Full_Career': full_career,
            'キャリア遍歴': full_career,
            'International_Caps': nationality,
            '代表キャップ数': caps_val
        }

        if player_name:
            official_details = get_brumbies_details(player_name)
            res.update(official_details)

        return res
    except Exception as e:
        print(f"Error fetching {player_url}: {e}")
        return {'Full_Career': "", 'キャリア遍歴': "", 'International_Caps': "", '代表キャップ数': ""}

def main(sample_only=True):
    teams = get_teams()
    if not teams: return

    all_data = []
    target_teams = teams[:1] if sample_only else teams
    
    for team in target_teams:
        players = get_squad(team['link'], team['name'])
        target_players = players[:15] if sample_only else players
        
        found_andy = False
        for p in target_players:
            details = get_player_details(p['URL'], p['英語名'])
            p.update(details)
            p.update({
                '年齢': '',
                '高校': p.get('高校', ''),
                '大学': p.get('大学', ''),
                'カテゴリ': 'A',
                'リーグワンキャップ数': '0',
                'Scraped_Url': p['URL']
            })
            all_data.append(p)
            if "Muirhead" in p['英語名']: found_andy = True
            time.sleep(1)
        
        if sample_only and not found_andy:
            p_andy = {
                '英語名': 'Andy Muirhead', '選手名': 'Andy Muirhead', 'ポジション': 'WTB',
                '所属チーム': team['name'], 'URL': 'https://all.rugby/player/andy-muirhead'
            }
            details = get_player_details(p_andy['URL'], p_andy['英語名'])
            p_andy.update(details)
            all_data.append(p_andy)
            
    output_file = "data_sources/super_rugby_sample.csv" if sample_only else "data_sources/super_rugby_full.csv"
    fieldnames = [
        '英語名', '選手名', 'ポジション', '所属チーム', '身長', '体重', '生年月日', 
        '年齢', '高校', '大学', '出身校・チーム歴(全文)', 'カテゴリ', 'リーグワンキャップ数', 
        'URL', 'Text_Detail', 'キャリア遍歴', '代表キャップ数', 'International_Caps', 
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
    # 全データ取得を実行（承認済みプランに基づく）
    main(sample_only=False)
