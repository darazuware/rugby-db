import requests
from bs4 import BeautifulSoup
import csv
import os
import re
import time

# 設定
CSV_PATH = 'data_sources/top_east_players.csv'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(os.path.dirname(BASE_DIR), CSV_PATH)

def save_to_csv(players, mode='a'):
    headers = ['title','name_ja','name_en','position','height','weight','age','birth_date','birth_place_scraped','league','team','high_school','university','junior_high_school','rugby_school','caps','league_one_caps','scraped_url','category']
    file_exists = os.path.isfile(CSV_FILE)
    
    with open(CSV_FILE, mode, encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists or mode == 'w':
            writer.writeheader()
        for p in players:
            # デフォルト値の補完
            row = {h: p.get(h, '---') for h in headers}
            writer.writerow(row)

def scrape_az_momotaros():
    print("Scraping AZ-COM Maruwa MOMOTARO'S...")
    url = "https://www.momotaros.jp/player"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, 'html.parser')
        
        players = []
        # セレクタは Step 582 の read_url_content 結果から推測
        # <h5 class="p-member-list__name"> などの構造を想定
        member_links = soup.select('h5 a')
        for link in member_links:
            href = link.get('href')
            name_text = link.get_text(strip=True)
            
            # 個別ページのクロール
            p_data = {
                'title': name_text,
                'name_ja': name_text,
                'league': 'top-east-a',
                'team': 'AZ-COM丸和MOMOTARO\'S',
                'scraped_url': href,
                'category': 'top-east'
            }
            
            try:
                p_res = requests.get(href, timeout=10)
                if p_res.status_code == 200:
                    p_soup = BeautifulSoup(p_res.content, 'html.parser')
                    # AZ-COMの個別ページでは、選手名はh1.entry-titleにある
                    name_tag = p_soup.find('h1', class_='entry-title')
                    if name_tag:
                        # "PR 五十嵐 優" のような形式から名前を抽出
                        full_name = name_tag.get_text(strip=True)
                        name_parts = full_name.split()
                        pos = name_parts[0] if len(name_parts) > 1 else ""
                        player_name = "".join(name_parts[1:]) if len(name_parts) > 1 else full_name
                        
                        # スタッフ除外フィルタ (ブラックリスト)
                        staff_keywords = ["監督", "コーチ", "スタッフ", "部長", "顧問", "事務局", "主務", "副部長", "採用", "広報", "映像", "Manager", "Coach", "Advisor", "Trainer", "S&C", "アスレティック", "テクニカル", "アドバイザー", "吹奏楽", "事務", "リーダー補佐", "分析", "担当"]
                        if any(k in pos or k in player_name for k in staff_keywords):
                            print(f"Skipping staff: {full_name} ({pos})")
                            continue

                        print(f"Scraping AZ Player: {player_name}")
                        p_data['title'] = player_name
                        p_data['name_ja'] = player_name
                        p_data['position'] = pos
                    
                    # .member-prof-ttl と .member-prof-txt のペアを探す
                    ttls = p_soup.select('.member-prof-ttl')
                    txts = p_soup.select('.member-prof-txt')
                    for t, v in zip(ttls, txts):
                        key = t.get_text(strip=True)
                        val = v.get_text(strip=True)
                        if "身長 / 体重" in key:
                            # 172cm / 102kg
                            hw_match = re.search(r'(\d+)cm\s*/\s*(\d+)kg', val)
                            if hw_match:
                                p_data['height'] = hw_match.group(1)
                                p_data['weight'] = hw_match.group(2)
                        elif "生年月日" in key:
                            p_data['birth_date'] = val.replace('年','-').replace('月','-').replace('日','')
                        elif "経歴" in key:
                            # 東海大学/東海大相模高校
                            p_data['university'] = val.split('/')[0] if '/' in val else val
                            p_data['high_school'] = val.split('/')[1] if '/' in val else ""
                        elif "出身地" in key:
                            p_data['birth_place_scraped'] = val
                time.sleep(0.5)
            except: pass
            
            players.append(p_data)
        
        return players
    except Exception as e:
        print(f"Error scraping AZ-COM: {e}")
        return []

def scrape_jrfu_match_reports(match_ids):
    print(f"Scraping {len(match_ids)} match reports from JRFU...")
    jrfu_players = {} # name -> {height, weight, position, team}
    
    for mid in match_ids:
        url = f"https://www.rugby-japan.jp/match/{mid}/print/"
        try:
            res = requests.get(url, timeout=10)
            if res.status_code != 200: continue
            soup = BeautifulSoup(res.content, 'html.parser')
            
            # メンバー表の抽出 (JRFU Print ページのテーブル構造)
            # <table> 内の <tr> をループ
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 5:
                        # 名前, 身長, 体重 などの列を探す
                        # 通常: 番号, ポジション, 名前, 身長, 体重, 生年月日...
                        # テキストベースでマッチング
                        text = row.get_text()
                        match = re.search(r'([^\d\s]+)\s+(\d{3})cm\s+(\d{1,3})kg', text)
                        if match:
                            name = match.group(1).strip()
                            height = match.group(2)
                            weight = match.group(3)
                            
                            # チーム名の特定（テーブルの見出しなどから）
                            # 簡易版：見つかったら保存（重複は上書きまたは無視）
                            if name not in jrfu_players:
                                jrfu_players[name] = {
                                    'height': height,
                                    'weight': weight,
                                }
            time.sleep(1) # 負荷軽減
        except Exception as e:
            print(f"Error scraping Match {mid}: {e}")
            
    return jrfu_players

def scrape_secom():
    # ... (既存のコード)
    print("Scraping Secom Rugguts...")
    url = "https://www.rugguts.secom.co.jp/player-staff/"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.content, 'html.parser')
        
        players = []
        # Step 670 の chunk から推測される構造
        # 実際は各ポジションセクションの下に選手リスト
        
        # セコムのサイトは <h5> ではなく <h4> や別タグの可能性
        # read_url_content で 髙野 悠斗 などが並んでいた
        items = soup.find_all('h5') # 推定
        if not items:
            items = soup.select('.p-player-list__name, .name') # 代替セレクタ
            
        for item in items:
            name = item.get_text(strip=True)
            link = item.find('a')
            href = link.get('href') if link else ""
            
            # 親要素からポジションを推測
            pos_section = item.find_parent('section')
            pos_title = pos_section.find(['h2', 'h3']).get_text(strip=True) if pos_section else ""
            
            players.append({
                'title': name,
                'name_ja': name,
                'position': pos_title,
                'league': 'top-east-a',
                'team': 'セコムラガッツ',
                'scraped_url': href,
                'category': 'top-east'
            })
        return players
    except Exception as e:
        print(f"Error scraping Secom: {e}")
        return []

def get_match_ids(standings_url):
    print(f"Fetching match IDs from {standings_url}...")
    try:
        res = requests.get(standings_url, timeout=10)
        res.raise_for_status()
        # ID形式: /match/(\d+)/print/
        ids = re.findall(r'/match/(\d+)/', res.text)
        return sorted(list(set(ids)))
    except Exception as e:
        print(f"Error fetching match IDs: {e}")
        return []

def jrfu_match_id_to_players(match_ids, league_label):
    jrfu_players = {}
    print(f"Scraping {len(match_ids)} JRFU match reports for {league_label}...")
    for i, mid in enumerate(match_ids):
        if i % 10 == 0: print(f"Progress: {i}/{len(match_ids)}")
        url = f"https://www.rugby-japan.jp/match/{mid}/print/"
        try:
            res = requests.get(url, timeout=10)
            if res.status_code != 200: continue
            soup = BeautifulSoup(res.content, 'html.parser')
            
            tables = soup.find_all('table')
            current_team = "---"
            for table in tables:
                prev_text = table.find_previous(text=True)
                if prev_text and "（" in prev_text:
                    current_team = prev_text.split('（')[0].strip()
                elif prev_text and " vs " in prev_text:
                    # スコアボードの見出しなど
                    pass

                rows = table.find_all('tr')
                for row in rows:
                    text = row.get_text(separator=' ', strip=True)
                    # 名前 + 身長 + 体重 + 年齢 の抽出 (JRFUの並び順に合わせる)
                    # 例: "1 PR 五十嵐 優 172 102 32" または "五十嵐 優 172cm 102kg"
                    match = re.search(r'([^\d\s\(\)]+)\s+(\d{3})\s+(\d{1,3})\s+\d+', text)
                    if not match:
                        match = re.search(r'([^\d\s\(\)]+)\s+(\d{3})cm\s+(\d{1,3})kg', text)
                    
                    if match:
                        name = match.group(1).strip()
                        if len(name) < 2: continue # ゴミ排除
                        
                        p_info = {
                            'height': match.group(2),
                            'weight': match.group(3),
                            'team': current_team,
                            'league': league_label
                        }
                        # 既存データがあればマージ
                        if name not in jrfu_players:
                            jrfu_players[name] = p_info
            time.sleep(0.2)
        except: pass
    return jrfu_players

def scrape_all_top_east():
    # 1. 公式サイトから取得 (高品質 - Aリーグ中心)
    print("Scraping official team sites...")
    official_players = []
    official_players.extend(scrape_az_momotaros())
    official_players.extend(scrape_secom())
    
    # 辞書化 (name -> data)
    merged_data = {}
    for p in official_players:
        merged_data[p['name_ja']] = p

    # 2. JRFU から体格データを補完 (Div A/B/C)
    leagues = [
        ("top-east-a", "https://www.rugby.or.jp/senior/sheet/2800/"),
        ("top-east-b", "https://www.rugby.or.jp/senior/result/2801/"),
        ("top-east-c", "https://www.rugby.or.jp/senior/result/2802/"),
    ]
    
    for label, url in leagues:
        match_ids = get_match_ids(url)
        jrfu_players = jrfu_match_id_to_players(match_ids, label)
        
        # 3. マージ
        for name, j_data in jrfu_players.items():
            if name in merged_data:
                # 公式サイトにない項目を補完
                if not merged_data[name].get('height'):
                    merged_data[name]['height'] = j_data['height']
                if not merged_data[name].get('weight'):
                    merged_data[name]['weight'] = j_data['weight']
                # リーグ情報を上書き（具体的な A/B/C ラベルへ）
                merged_data[name]['league'] = j_data['league']
            else:
                # 新規選手として追加
                merged_data[name] = {
                    'title': name,
                    'name_ja': name,
                    'height': j_data['height'],
                    'weight': j_data['weight'],
                    'team': j_data['team'],
                    'league': j_data['league'],
                    'category': 'top-east'
                }

    return list(merged_data.values())

if __name__ == "__main__":
    final_players = scrape_all_top_east()
    if final_players:
        save_to_csv(final_players, mode='w')
        print(f"Total Top East players integrated: {len(final_players)}")
