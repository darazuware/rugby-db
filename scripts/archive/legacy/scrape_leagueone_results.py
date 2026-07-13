import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# データの保存先
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TEAM_NAMES_JP_PATH = os.path.join(DATA_DIR, 'team_names_jp.json')
RESULTS_JSON_PATH = os.path.join(DATA_DIR, 'results_2026.json')

# チーム名日本語化マッピングの読み込み
with open(TEAM_NAMES_JP_PATH, 'r', encoding='utf-8') as f:
    TEAM_NAMES_DATA = json.load(f)
    LEAGUE_ONE_NAMES = TEAM_NAMES_DATA.get('league-one', {})

def normalize_team(name):
    name = name.strip()
    # 既に日本語名ならそのまま
    for team_data in LEAGUE_ONE_NAMES.values():
        if team_data['jp'] == name:
            return team_data['jp'], team_data['flag']
    
    # マッピングから検索（キーまたはエイリアス）
    for main_name, data in LEAGUE_ONE_NAMES.items():
        if name == main_name or name in data.get('aliases', []):
            return data['jp'], data['flag']
    
    # 部分一致
    for main_name, data in LEAGUE_ONE_NAMES.items():
        if name in main_name or any(name in alias for alias in data.get('aliases', [])):
            return data['jp'], data['flag']
            
    return name, "🇯🇵"

def scrape_leagueone_results():
    url = "https://league-one.jp/schedule/"
    print(f"Scraping League One results from {url}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        all_matches = []
        
        # ディビジョンごとにタブが分かれている (#tab1, #tab2, #tab3)
        for div_num in range(1, 4):
            division_label = f"D{div_num}"
            tab_id = f"tab{div_num}"
            tab_content = soup.find('div', id=tab_id)
            if not tab_content:
                print(f"Tab {tab_id} not found.")
                continue
                
            # 節ごとのアコーディオン/コンテナ
            # 構造: .c-schedule が各試合のコンテナ
            schedule_items = tab_content.select('.c-schedule')
            print(f"Found {len(schedule_items)} matches for Division {div_num}")
            
            for item in schedule_items:
                # 1. 節(Round)情報の取得
                # 構造が変更されている可能性があるため、複数の方法で試行
                round_num = 0
                
                # A. 親セクションの見出しから取得 (既存)
                parent_section = item.find_parent('section')
                if parent_section:
                    round_el = parent_section.select_one('.ttl')
                    if not round_el:
                        # 見出しクラス名が変わっている可能性
                        round_el = parent_section.find(['h2', 'h3', 'h4'])
                    
                    if round_el:
                        round_text = round_el.get_text()
                        match = re.search(r'第(\d+)節', round_text)
                        if match:
                            round_num = int(match.group(1))
                
                # B. 見つからない場合、要素自体から順に遡って探索
                if round_num == 0:
                    prev = item.find_previous(['h2', 'h3', 'h4', 'section'])
                    while prev:
                        text = prev.get_text()
                        match = re.search(r'第(\d+)節', text)
                        if match:
                            round_num = int(match.group(1))
                            break
                        # さらに前を探索
                        prev = prev.find_previous(['h2', 'h3', 'h4', 'section'])

                # 2. 日付の取得
                date_el = item.select_one('.datetime .date')
                date_iso = ""
                if date_el:
                    date_text = date_el.get_text(strip=True)
                    date_match = re.search(r'(\d{1,2})\.(\d{1,2})', date_text)
                    if date_match:
                        year = "2025"
                        if parent_section:
                            ttl_text = parent_section.select_one('.ttl').get_text() if parent_section.select_one('.ttl') else ""
                            year_match = re.search(r'(\d{4})', ttl_text)
                            if year_match:
                                year = year_match.group(1)
                        elif int(date_match.group(1)) <= 6: # 1-6月は2026年と推測
                            year = "2026"
                        
                        month = date_match.group(1).zfill(2)
                        day = date_match.group(2).zfill(2)
                        date_iso = f"{year}-{month}-{day}"

                # 3. チーム名（クレンジング: 略称・地名重複・ノイズ除去）
                def clean_lo_team(name):
                    # 1. 括弧やノイズを除去
                    name = re.sub(r'\(.*?\)|（.*?）|　.*$', '', name).strip()
                    name = re.sub(r'第\d+節.*$', '', name).strip()
                    name = re.sub(r'(準決勝|決勝|プレーオフ|交流戦|入れ替え戦|入替戦).*$', '', name).strip()
                    name = re.sub(r'D\d+リーグ戦\d+位$', '', name).strip() # 順位情報のノイズ
                    
                    # 2. 末尾の英文字・略称（ＢＲ東京、東京ＳＧなど）の除去
                    name = re.sub(r'^[A-Z\dＡ-Ｚ０-９]+', '', name).strip() # 文頭の略称
                    name = re.sub(r'[A-Z\dＡ-Ｚ０-９]+$', '', name).strip() # 文末の略称
                    
                    # 3. 地名の重複（トヨタヴェルブリッツトヨタ 等）
                    for city in ['東京', '横浜', '埼玉', '三重', '静岡', '神戸', '船橋', '相模原', '浦安', '大阪', 'トヨタ', '釜石', '日野', '九州']:
                        if name.endswith(city) and name.count(city) >= 2:
                            name = name[:name.rindex(city)].strip()
                            
                    # 4. 特殊なケースのハードコードクレンジング
                    clean_map = {
                        "トヨタヴェルブリッツトヨタ": "トヨタヴェルブリッツ",
                        "コベルコ神戸スティーラーズ神戸": "コベルコ神戸スティーラーズ",
                        "クボタスピアーズ船橋・東京ベイ船橋・": "クボタスピアーズ船橋・東京ベイ",
                        "三菱重工相模原ダイナボアーズ相模原": "三菱重工相模原ダイナボアーズ",
                        "釜石シーウェイブス釜石": "釜石シーウェイブス",
                        "中国電力レッドレグリオンズ中国": "中国電力レッドレグリオンズ"
                    }
                    if name in clean_map:
                        name = clean_map[name]
                            
                    return name

                home_li = item.select_one('li.home')
                home_raw = clean_lo_team(home_li.select_one('.team').get_text(strip=True)) if (home_li and home_li.select_one('.team')) else ""
                
                away_li = item.select_one('li.away')
                away_raw = clean_lo_team(away_li.select_one('.team').get_text(strip=True)) if (away_li and away_li.select_one('.team')) else ""
                
                score = "VS"
                if home_li and away_li:
                    hs_el = home_li.select_one('.score')
                    as_el = away_li.select_one('.score')
                    if hs_el and as_el:
                        hs = hs_el.get_text(strip=True)
                        as_val = as_el.get_text(strip=True)
                        if hs and as_val:
                            score = f"{hs}-{as_val}"

                # 4. 詳細リンク
                detail_url = ""
                detail_btn = item.select_one('a.btn-match-detail')
                if detail_btn and 'href' in detail_btn.attrs:
                    detail_url = detail_btn['href']
                    if not detail_url.startswith('http'):
                        detail_url = f"https://league-one.jp{detail_url}"

                if not home_raw or not away_raw:
                    continue
                    
                home_jp, home_flag = normalize_team(home_raw)
                away_jp, away_flag = normalize_team(away_raw)

                # 追加のクレンジング（日本語名）
                def final_clean_lo(name):
                    # 1. 既知の特定のノイズ（Ｓ愛知, ＷＧ昭島 等）を削除
                    # 全角・半角英数＋地名
                    name = re.sub(r'([A-ZＡ-Ｚ0-9]{1,4}[一-龠ぁ-んァ-ヶー]+)$', '', name).strip()
                    name = re.sub(r'([A-ZＡ-Ｚ0-9]{1,4})$', '', name).strip()
                    
                    # 2. 末尾の地名重複を徹底削除
                    # チーム名の前半部分に地名が含まれている場合、末尾の地名は余計
                    cities = ['東京', '横浜', '埼玉', '三重', '静岡', '神戸', '船橋', '相模原', '浦安', '大阪', 'トヨタ', '釜石', '日野', '九州', '花園', '愛知', '昭島', '江東', '狭山', '戸田', '福岡', '広島']
                    for city in cities:
                        if name.endswith(city) and (name[:-len(city)].find(city) != -1):
                            name = name[:-len(city)].strip()
                    
                    # 3. 特定の残存パターンをピンポイント削除
                    name = re.sub(r'(ＢＬ|ＢＲ|ＳＧ|Ｅ|Ｄ|Ｓ|ＲＨ|ＤＢ|ＶＢ|Ｓベイ|ＷＧ|Ｓ|Ｄ２|Ｄ１|Ｄ３)$', '', name).strip()
                    
                    return name
                
                home_jp = final_clean_lo(home_jp)
                away_jp = final_clean_lo(away_jp)
                
                all_matches.append({
                    "division": division_label,
                    "date": date_iso,
                    "round": round_num,
                    "home": home_jp,
                    "away": away_jp,
                    "score": score,
                    "home_flag": home_flag,
                    "away_flag": away_flag,
                    "detail_url": detail_url
                })
        
        return all_matches
    except Exception as e:
        print(f"Error scraping League One: {e}")
        return []

def main():
    # 1. 既存データの読み込み
    if os.path.exists(RESULTS_JSON_PATH):
        try:
            with open(RESULTS_JSON_PATH, 'r', encoding='utf-8') as f:
                all_results = json.load(f)
        except:
            all_results = {"league-one": [], "super-rugby": [], "top14": [], "urc": []}
    else:
        all_results = {"league-one": [], "super-rugby": [], "top14": [], "urc": []}

    # 2. League One の取得
    new_lo_results = scrape_leagueone_results()
    
    if new_lo_results:
        # 重複排除: (date, home, away, division) をユニークキーとする
        seen = set()
        unique_results = []
        for m in new_lo_results:
            key = (m['date'], m['home'], m['away'], m['division'])
            if key not in seen:
                seen.add(key)
                unique_results.append(m)
        
        all_results["league-one"] = unique_results
        
        with open(RESULTS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"Successfully updated {len(unique_results)} unique matches for League One.")
    else:
        print("No League One results found.")

if __name__ == "__main__":
    main()
