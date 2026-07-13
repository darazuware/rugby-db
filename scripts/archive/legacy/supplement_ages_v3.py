import csv
import os
import time
import requests
from bs4 import BeautifulSoup
import re
import subprocess

CSV_FILE = "/Users/ktamatzmoto/Desktop/rugbypicks/data_sources/final_master_data_v25_integrated.csv"
MISSING_LIST = "/tmp/missing_all_players.csv"
OUTPUT_SUPPLEMENTED = "/tmp/supplemented_all_players.csv"
DISCORD_NOTIFY_SCRIPT = "/Users/ktamatzmoto/Desktop/rugbypicks/scripts/discord_notify.py"

def notify_discord(title, message, color=0x3498db):
    try:
        color_hex = hex(color)
        subprocess.run(["python3", DISCORD_NOTIFY_SCRIPT, title, message, color_hex], check=True)
    except Exception as e:
        print(f"Discord notice failed: {e}")

def fetch_birth_date_from_wikipedia(name_en):
    try:
        if not name_en:
            return None
            
        name_queries = [
            name_en.replace(" ", "_") + "_(rugby_union)",
            name_en.replace(" ", "_") + "_(rugby_player)",
            name_en.replace(" ", "_")
        ]
        
        headers = {
            'User-Agent': 'RugbyPicksDataBot/1.0 (contact: rugbypicks.com)'
        }
        
        for search_query in name_queries:
            url = f"https://en.wikipedia.org/wiki/{search_query}"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            infobox = soup.select_one('table.infobox.vcard, table.infobox')
            if not infobox:
                continue
            
            # ラグビー関連のキーワードが含まれているかチェック
            infobox_text = infobox.get_text().lower()
            if 'rugby' not in infobox_text:
                # 汎用的な名前のページでラグビーの記述がない場合はスキップ
                continue
            
            for tr in infobox.find_all('tr'):
                th = tr.find(['th', 'td'], string=re.compile(r'Born', re.I))
                if not th:
                    th_text = tr.get_text()
                    if 'Born' not in th_text:
                        continue
                
                td = tr.find('td')
                if td:
                    bday = td.find('span', {'class': 'bday'})
                    if bday:
                        return bday.get_text()
                    text = td.get_text()
                    match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
                    if match:
                        return match.group(1)
                    # Month DD, YYYY
                    match_long = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', text)
                    if match_long:
                        return match_long.group(1)
        return None
    except Exception as e:
        print(f"Error fetching {name_en}: {e}")
        return None

def main():
    if not os.path.exists(MISSING_LIST):
        print("Error: Missing list not found. Extracting first...")
        # 必要に応じて再抽出（今回はすでにある前提）
        return

    players = []
    with open(MISSING_LIST, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        players = list(reader)

    total = len(players)
    print(f"Starting supplementation for {total} players...")
    notify_discord("🚀 全リーグ・データ補完開始", f"PREM, URC, その他を含む全欠損選手 {total} 名に対し、Wikipedia からの年齢データ補完を開始します。", 0xe67e22)
    
    results = []
    found_count = 0
    
    for i, p in enumerate(players):
        name_en = p['name_en']
        print(f"[{i+1}/{total}] Fetching: {name_en}...")
        
        birth_date = fetch_birth_date_from_wikipedia(name_en)
        if birth_date:
            print(f"  -> Found: {birth_date}")
            p['birth_date'] = birth_date
            found_count += 1
        else:
            p['birth_date'] = ""
        
        results.append(p)
        
        if (i + 1) % 50 == 0:
            notify_discord("📊 進捗報告 (Age Supplement)", f"{i+1}/{total} 名の処理が完了しました。\n現在までの取得成功数: {found_count}")
        
        time.sleep(1) # Wikipediaのマナー

    fieldnames = ["name", "name_en", "team", "url", "birth_date"]
    with open(OUTPUT_SUPPLEMENTED, mode='w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    notify_discord("✅ データ再取得完了", f"全 {total} 名の再取得が完了しました。\n取得成功: {found_count} 名\nこれからマスターデータ（v25）へマージします。", 0x2ecc71)
    print(f"Supplemented data saved to: {OUTPUT_SUPPLEMENTED}")

if __name__ == "__main__":
    main()
