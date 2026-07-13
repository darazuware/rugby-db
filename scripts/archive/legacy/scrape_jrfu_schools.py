import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
from datetime import datetime
import time

# 設定
PROJECT_ROOT = '/Users/ktamatzmoto/Desktop/rugbypicks'
HS_CSV = os.path.join(PROJECT_ROOT, 'data_sources/high_school_players.csv')
UNI_CSV = os.path.join(PROJECT_ROOT, 'data_sources/university_players.csv')

def get_match_ids(tournament_url):
    """大会スケジュールページから試合IDのリストを取得"""
    print(f"Fetching match IDs from: {tournament_url}")
    try:
        res = requests.get(tournament_url)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, 'html.parser')
        
        # 試合詳細へのリンクを抽出 (e.g., /match/30008)
        match_links = soup.find_all('a', href=re.compile(r'/match/\d+'))
        match_ids = []
        for a in match_links:
            match_id = re.search(r'/match/(\d+)', a['href']).group(1)
            if match_id not in match_ids:
                match_ids.append(match_id)
        
        return match_ids
    except Exception as e:
        print(f"Error fetching match IDs: {e}")
        return []

def scrape_match_players(match_id, league='High School'):
    """試合ページから両チームの選手情報を取得"""
    url = f"https://www.rugby-japan.jp/match/{match_id}"
    print(f"Scraping match: {url}")
    players = []
    
    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, 'html.parser')
        
        member_div = soup.find('div', class_='member')
        if not member_div:
            print(f"No player info found for match {match_id}")
            return []
            
        # Home/Away チーム
        for side in ['home', 'away']:
            team_section = member_div.find('div', class_=side)
            if not team_section: continue
            
            team_name = team_section.find('h3').get_text(strip=True)
            
            # Starting/Reserve メンバー
            for category in ['starting', 'reserve']:
                table_div = team_section.find('div', class_=category)
                if not table_div: continue
                
                rows = table_div.find_all('tr')
                for row in rows:
                    tds = row.find_all('td')
                    if len(tds) < 3: continue
                    
                    pos = tds[0].get_text(strip=True)
                    num = tds[1].get_text(strip=True)
                    
                    # 3番目のTDに名前と属性が入っている
                    info_td = tds[2]
                    name_raw = info_td.contents[0].strip()
                    # 2行目の属性 (180cm / 100kg / 16歳 などの形式)
                    attr_text = ""
                    for content in info_td.contents:
                        if isinstance(content, str) and ('cm' in content or 'kg' in content):
                            attr_text = content.strip()
                            break
                    
                    height = ""
                    weight = ""
                    age = ""
                    if attr_text:
                        parts = [p.strip() for p in attr_text.split('/')]
                        for p in parts:
                            if 'cm' in p: height = p.replace('cm', '')
                            elif 'kg' in p: weight = p.replace('kg', '')
                            elif '歳' in p: age = p.replace('歳', '')
                    
                    # 出身中学や学年情報は詳細ページにある場合があるが、まずはスタメン表から
                    # ※現状のJRFUスタメン表には学年や中学は直接出ていないことが多い
                    # 必要に応じて選手名で検索するか、あるいは別ソースを検討する
                    
                    players.append({
                        'Full_Name': name_raw,
                        'Position': pos,
                        'Number': num,
                        'Height': height,
                        'Weight': weight,
                        'Age': age,
                        'Current_Team': team_name,
                        'League': league,
                        'Junior_High_School': '', # 将来用
                        'Rugby_School': '',       # 将来用
                        'Grade': '',              # 将来用
                        'Tournament_Name': soup.find('h1').get_text(strip=True) if soup.find('h1') else '',
                        'Scraped_Url': url,
                        'Last_Updated': datetime.now().strftime('%Y-%m-%d')
                    })
        return players
    except Exception as e:
        print(f"Error scraping match {match_id}: {e}")
        return []

def save_to_csv(players, csv_path):
    if not players: return
    
    df_new = pd.DataFrame(players)
    
    if os.path.exists(csv_path):
        df_old = pd.read_csv(csv_path)
        # 既存選手とのマージ（名前とチームで重複排除）
        df_combined = pd.concat([df_old, df_new]).drop_duplicates(subset=['Full_Name', 'Current_Team'], keep='last')
        df_combined.to_csv(csv_path, index=False, encoding='utf-8-sig')
    else:
        df_new.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print(f"Saved {len(players)} players to {csv_path}")

def main():
    # 高校選抜大会
    hs_tournament_url = "https://www.rugby-japan.jp/schedule/highschool"
    hs_match_ids = get_match_ids(hs_tournament_url)
    
    # 最近の試合（2回戦以降など）に絞ることも可能だが、一旦全部取得を試みる
    # ただし多すぎると時間がかかるので、第27回選抜大会のID範囲を確認
    # 先ほど調査したところでは 30005-30008 (準々決勝) が明日。
    # 29845-29880 が1, 2回戦あたり。
    
    all_hs_players = []
    # 準々決勝・2回戦の一部をサンプル取得
    target_ids = ['30005', '30006', '30007', '30008', '29874', '29880', '29876', '29878'] 
    
    for mid in target_ids:
        ps = scrape_match_players(mid, league='High School')
        all_hs_players.extend(ps)
        time.sleep(1) # マナー
        
    save_to_csv(all_hs_players, HS_CSV)

    # 大学選手権（第62回）
    # 決勝: 29527, 準決勝: 29526, 29525
    uni_target_ids = ['29527', '29526', '29525']
    all_uni_players = []
    for mid in uni_target_ids:
        ps = scrape_match_players(mid, league='University')
        all_uni_players.extend(ps)
        time.sleep(1)
        
    save_to_csv(all_uni_players, UNI_CSV)

if __name__ == "__main__":
    main()
