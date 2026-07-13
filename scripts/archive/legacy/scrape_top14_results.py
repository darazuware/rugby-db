import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# チーム名日本語化マッピングの読み込み
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TEAM_NAMES_JP_PATH = os.path.join(DATA_DIR, 'team_names_jp.json')
RESULTS_JSON_PATH = os.path.join(DATA_DIR, 'results_2026.json')

with open(TEAM_NAMES_JP_PATH, 'r', encoding='utf-8') as f:
    TEAM_NAMES_JP = json.load(f).get('top14', {})

def normalize_team(name):
    name = name.strip()
    # 既に日本語名ならそのまま
    for team_data in TEAM_NAMES_JP.values():
        if team_data['jp'] == name:
            return team_data['jp'], team_data['flag']
    
    # マッピングから検索（キーまたはエイリアス）
    for main_name, data in TEAM_NAMES_JP.items():
        if name == main_name or name in data.get('aliases', []):
            return data['jp'], data['flag']
    
    # 部分一致（"Toulouse" が "Stade Toulousain" に含まれる場合など）
    for main_name, data in TEAM_NAMES_JP.items():
        if name in main_name or any(name in alias for alias in data.get('aliases', [])):
            return data['jp'], data['flag']
            
    return name, "🇫🇷"

def parse_french_date(date_text):
    """samedi 24 janvier 2026 などの形式を YYYY-MM-DD に変換試行"""
    months = {
        'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
        'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
        'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
    }
    date_text = date_text.lower()
    # 年が含まれていない場合は推測 (9-12月なら2025, 1-6月なら2026)
    year = "2026"
    for m_fr, m_num in months.items():
        if m_fr in date_text:
            if int(m_num) >= 9:
                year = "2025"
            else:
                year = "2026"
            
            # 日にちを探す
            day_match = re.search(r'(\d{1,2})', date_text)
            if day_match:
                day = day_match.group(1).zfill(2)
                return f"{year}-{m_num}-{day}"
    return date_text

def scrape_round(round_num):
    url = f"https://top14.lnr.fr/calendrier-et-resultats/2025-2026/j{round_num}"
    print(f"Scraping Round {round_num}: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        matches = []
        inner_container = soup.find('div', class_='calendar-results__inner')
        if not inner_container:
            # 代わりのコンテナを探す
            inner_container = soup.select_one('.calendar-results')
            
        if not inner_container:
            print(f"Could not find container for Round {round_num}")
            return []

        current_date_iso = ""
        
        # 直下の子要素をイテレート
        for child in inner_container.find_all(recursive=False):
            classes = child.get('class', [])
            
            # 日付見出し
            if any('calendar-results__fixture-date' in c for c in classes):
                date_raw = child.get_text(strip=True)
                current_date_iso = parse_french_date(date_raw)
                continue
                
            # 試合行
            if any('calendar-results__line' in c for c in classes):
                match_line = child.find('div', class_='match-line')
                if not match_line: continue
                
                # チーム名抽出 (より堅牢な方法)
                # 左側(Home): club-line--reversed
                # 右側(Away): club-line (reversedなし)
                home_el = match_line.select_one('.club-line--reversed .club-line__name')
                away_el = match_line.select_one('.club-line:not(.club-line--reversed) .club-line__name')
                score_el = match_line.select_one('.match-line__score')
                
                if home_el and away_el and score_el:
                    home_raw = home_el.get_text(strip=True)
                    away_raw = away_el.get_text(strip=True)
                    score = score_el.get_text(strip=True).replace('\n', ' ').strip()
                    score = re.sub(r'\s+', ' ', score) # 余計な空白を除去
                    
                    # 詳細リンク (score_el 自体が <a> タグの場合がある)
                    detail_url = ""
                    if score_el.name == 'a' and 'href' in score_el.attrs:
                        detail_url = score_el['href']
                        if not detail_url.startswith('http'):
                            detail_url = f"https://top14.lnr.fr{detail_url}"
                    else:
                        link_el = match_line.select_one('a.match-links__link')
                        if link_el and 'href' in link_el.attrs:
                            detail_url = f"https://top14.lnr.fr{link_el['href']}"
                    
                    home_jp, home_flag = normalize_team(home_raw)
                    away_jp, away_flag = normalize_team(away_raw)
                    
                    matches.append({
                        "round": round_num,
                        "date": current_date_iso,
                        "home": home_jp,
                        "away": away_jp,
                        "score": score,
                        "home_flag": home_flag,
                        "away_flag": away_flag,
                        "detail_url": detail_url
                    })
        
        return matches
    except Exception as e:
        print(f"Error scraping Round {round_num}: {e}")
        return []

def main():
    # 1. 既存データのバックアップ/読み込み
    if os.path.exists(RESULTS_JSON_PATH):
        with open(RESULTS_JSON_PATH, 'r', encoding='utf-8') as f:
            all_results = json.load(f)
    else:
        all_results = {"league-one": [], "super-rugby": [], "top14": [], "urc": []}

    # 2. Top 14 の全節をループ
    new_top14_results = []
    for r in range(1, 27): # 通常26節
        round_matches = scrape_round(r)
        if round_matches:
            new_top14_results.extend(round_matches)
        else:
            # 1節も取れなかったら、その節以降はまだ日程がない可能性があるが、
            # Top 14は日程が出ていることが多いので続ける
            pass
        time.sleep(1) # マナー
    
    # 取得できたデータがあれば更新
    if new_top14_results:
        # 重複排除をしつつマージするのが理想だが、今回は全件洗い替えの方が確実
        # ただし日付が文字列なので正規化しておきたい
        all_results["top14"] = new_top14_results
        
        with open(RESULTS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"Successfully updated {len(new_top14_results)} matches for Top 14.")
    else:
        print("No TOP 14 results found. Check selectors.")

if __name__ == "__main__":
    main()
