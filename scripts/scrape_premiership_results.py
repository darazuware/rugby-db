import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# デーディレクトリの定義
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TEAM_NAMES_JP_PATH = os.path.join(DATA_DIR, 'team_names_jp.json')
RESULTS_JSON_PATH = os.path.join(DATA_DIR, 'results_2026.json')

# チーム名日本語化マッピングの読み込み
with open(TEAM_NAMES_JP_PATH, 'r', encoding='utf-8') as f:
    TEAM_NAMES_JP = json.load(f).get('premiership', {})

def normalize_team(name):
    """チーム名を日本語名とフラグに変換"""
    name = name.strip().upper()
    
    # 1. マッピングから検索（正式名、キー、またはエイリアス）
    for main_name, data in TEAM_NAMES_JP.items():
        if name == main_name.upper() or name == data['jp'].upper() or name in [a.upper() for a in data.get('aliases', [])]:
            return data['jp'], data['flag']
    
    # 2. 部分一致
    for main_name, data in TEAM_NAMES_JP.items():
        if name in main_name.upper() or any(name in a.upper() for a in data.get('aliases', [])):
            return data['jp'], data['flag']
            
    return name, "🏴󠁧󠁢󠁥󠁮󠁧󠁿"

def parse_date(date_text):
    """
    'JANUARY 25, 2026' または '25 JANUARY' などの形式を YYYY-MM-DD に変換
    ブラウザのロケールによって '1月25日' となる可能性も考慮
    """
    months_en = {
        'JANUARY': '01', 'FEBRUARY': '02', 'MARCH': '03', 'APRIL': '04',
        'MAY': '05', 'JUNE': '06', 'JULY': '07', 'AUGUST': '08',
        'SEPTEMBER': '09', 'OCTOBER': '10', 'NOVEMBER': '11', 'DECEMBER': '12'
    }
    date_text = date_text.upper()
    
    # 年が含まれていない場合は推測 (9-12月なら2025, 1-6月なら2026)
    year = "2026"
    
    # 英語形式のチェック
    for m_en, m_num in months_en.items():
        if m_en in date_text:
            if int(m_num) >= 9: year = "2025"
            else: year = "2026"
            
            day_match = re.search(r'(\d{1,2})', date_text)
            if day_match:
                day = day_match.group(1).zfill(2)
                return f"{year}-{m_num}-{day}"
                
    # 日本語形式のチェック ('1月25日' 等)
    jp_match = re.search(r'(\d{1,2})月(\d{1,2})日', date_text)
    if jp_match:
        m_num = jp_match.group(1).zfill(2)
        day = jp_match.group(2).zfill(2)
        if int(m_num) >= 9: year = "2025"
        else: year = "2026"
        return f"{year}-{m_num}-{day}"

    return date_text

def scrape_premiership_results():
    """プレミアシップの戦績を取得"""
    url = "https://www.premiershiprugby.com/fixtures-results"
    print(f"Scraping Premiership results from {url}...")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        # 各節のデータを取得 (現在は最新表示分のみが取得される想定)
        # より広範囲に取得するには、動的なボタンクリック等が必要だが、
        # まずは表示されている分を取得する
        
        # 試合カードの取得
        # セレクターはブラウザ subagent の調査に基づく
        match_containers = soup.select('div.flex.items-center.justify-center.gap-2.xl\:w-full')
        
        # 節（Round）の特定
        round_btn = soup.select_one('button.bg-primary-100.text-primary-600')
        current_round = "0"
        if round_btn:
            round_text = round_btn.get_text(strip=True)
            round_match = re.search(r'(\d+)', round_text)
            if round_match:
                current_round = round_match.group(1)
        
        print(f"Detected Round: {current_round}")

        for container in match_containers:
            # 親要素を遡って日付を探すか、近傍の日付要素を取得
            # 日付要素は .basis-full.text-center.font-condensed.text-body-3 にある
            parent = container.find_parent('div', class_='flex-col')
            date_el = None
            if parent:
                date_el = parent.select_one('.basis-full.text-center.font-condensed.text-body-3')
            
            raw_date = date_el.get_text(strip=True) if date_el else ""
            formatted_date = parse_date(raw_date)
            
            # チーム名とスコア
            # ホームとアウェイは div 内の順序で決まる
            teams = container.select('span.text-h2.font-ultracondensed.uppercase')
            scores = container.select('div.text-h1.font-ultracondensed')
            
            if len(teams) >= 2 and len(scores) >= 2:
                home_raw = teams[0].get_text(strip=True)
                away_raw = teams[1].get_text(strip=True)
                score_home = scores[0].get_text(strip=True)
                score_away = scores[1].get_text(strip=True)
                
                home_jp, home_flag = normalize_team(home_raw)
                away_jp, away_flag = normalize_team(away_raw)
                
                # 詳細リンク
                detail_url = ""
                link_el = container.find_parent('a')
                if link_el and 'href' in link_el.attrs:
                    detail_url = f"https://www.premiershiprugby.com{link_el['href']}"

                results.append({
                    "round": int(current_round),
                    "date": formatted_date,
                    "home": home_jp,
                    "away": away_jp,
                    "score": f"{score_home}-{score_away}",
                    "home_flag": home_flag,
                    "away_flag": away_flag,
                    "detail_url": detail_url
                })
        
        return results
    except Exception as e:
        print(f"Error scraping Premiership results: {e}")
        return []

def main():
    # 1. 既存データの読み込み
    if os.path.exists(RESULTS_JSON_PATH):
        with open(RESULTS_JSON_PATH, 'r', encoding='utf-8') as f:
            all_results = json.load(f)
    else:
        all_results = {}

    # 2. プレミアシップ戦績の取得
    new_results = scrape_premiership_results()
    
    if new_results:
        # 重複排除とマージ
        existing_prem = all_results.get("premiership", [])
        
        # 簡易的な重複排除 (日付 + チーム名)
        seen_keys = set()
        for r in existing_prem:
            seen_keys.add(f"{r['date']}-{r['home']}-{r['away']}")
            
        merged_count = 0
        for nr in new_results:
            key = f"{nr['date']}-{nr['home']}-{nr['away']}"
            if key not in seen_keys:
                existing_prem.append(nr)
                seen_keys.add(key)
                merged_count += 1
        
        # 日付順、Round順にソート (任意だがRound順を優先)
        existing_prem.sort(key=lambda x: (x.get('round', 0), x.get('date', '')))
        
        all_results["premiership"] = existing_prem
        
        with open(RESULTS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully added {merged_count} new matches to Premiership (Total: {len(existing_prem)})")
    else:
        print("No new results found or error occurred.")

if __name__ == "__main__":
    main()
