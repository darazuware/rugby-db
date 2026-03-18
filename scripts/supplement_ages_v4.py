import csv
import os
import time
import requests
from bs4 import BeautifulSoup
import re
import subprocess

CSV_FILE = "/Users/ktamatzmoto/Desktop/rugbypicks/data_sources/final_master_data_v25_integrated.csv"
MISSING_LIST = "/tmp/missing_prem_103.csv"
OUTPUT_SUPPLEMENTED = "/tmp/supplemented_prem_103.csv"
DISCORD_NOTIFY_SCRIPT = "/Users/ktamatzmoto/Desktop/rugbypicks/scripts/discord_notify.py"

def notify_discord(title, message, color=0x3498db):
    try:
        color_hex = hex(color)
        subprocess.run(["python3", DISCORD_NOTIFY_SCRIPT, title, message, color_hex], check=True)
    except Exception as e:
        print(f"Discord notice failed: {e}")

def extract_name_from_url(url):
    """all.rugby URLからスラッグを抽出し、名前に変換する"""
    if not url or 'all.rugby/player/' not in url:
        return None
    # 例: https://all.rugby/player/alfie-barbeary -> alfie-barbeary
    slug = url.split('/')[-1]
    # 数字が入っている場合は除去 (例: tom-cowan-0 -> tom-cowan)
    slug = re.sub(r'-\d+$', '', slug)
    # アルフィー・バーベアリー -> Alfie Barbeary
    parts = slug.split('-')
    name = " ".join(part.capitalize() for part in parts)
    return name

def fetch_birth_date_from_wikipedia(name_en, original_url=None):
    try:
        # 検索クエリ候補の生成
        queries = []
        
        # 1. 直接の名前
        queries.append(name_en.replace(" ", "_"))
        
        # 2. URLスラッグからの復元名 (略称対策)
        url_name = extract_name_from_url(original_url)
        if url_name and url_name != name_en:
            queries.append(url_name.replace(" ", "_"))
            
        # 各クエリに対して (rugby_union) 等のサフィックスを付けて試行
        final_queries = []
        for q in queries:
            final_queries.append(q + "_(rugby_union)")
            final_queries.append(q + "_(rugby_player)")
            final_queries.append(q)
            
        headers = {
            'User-Agent': 'RugbyPicksDataBot/1.0 (contact: rugbypicks.com)'
        }
        
        seen_urls = set()
        for search_query in final_queries:
            url = f"https://en.wikipedia.org/wiki/{search_query}"
            if url in seen_urls: continue
            seen_urls.add(url)
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            infobox = soup.select_one('table.infobox.vcard, table.infobox')
            if not infobox:
                continue
            
            infobox_text = infobox.get_text().lower()
            if 'rugby' not in infobox_text:
                continue
            
            for tr in infobox.find_all('tr'):
                th = tr.find(['th', 'td'], string=re.compile(r'Born', re.I))
                if not th: continue
                td = tr.find_next_sibling('tr') or tr
                text = td.get_text()
                match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
                if match: return match.group(1)
                match_long = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', text)
                if match_long: return match_long.group(1)
                
        return None
    except Exception as e:
        print(f"Error fetching {name_en}: {e}")
        return None

def main():
    # 欠損103名のリスト抽出
    players = []
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            league = row.get('リーグ', '').strip()
            bday = row.get('生年月日', '').strip()
            if league == 'premiership' and (not bday or bday.lower() in ['none', 'unknown', 'nan', '']):
                players.append({
                    'name': row.get('選手名', ''),
                    'name_en': row.get('英語名', ''),
                    'team': row.get('所属チーム', ''),
                    'url': row.get('URL', '')
                })

    total = len(players)
    print(f"Starting supplementation for {total} missing PREM players (v4 slug-based)...")
    notify_discord("🔍 欠損 103 名の再分析", f"名前の略称化が原因で取得できなかった {total} 名に対し、URL スラッグを用いたフルネーム復元検索（v4）を開始します。", 0xe67e22)
    
    results = []
    found_count = 0
    
    for i, p in enumerate(players):
        name_en = p['name_en']
        print(f"[{i+1}/{total}] Fetching: {name_en}...")
        
        birth_date = fetch_birth_date_from_wikipedia(name_en, p['url'])
        if birth_date:
            print(f"  -> Found: {birth_date}")
            p['birth_date'] = birth_date
            found_count += 1
        else:
            p['birth_date'] = ""
        
        results.append(p)
        time.sleep(1)

    fieldnames = ["name", "name_en", "team", "url", "birth_date"]
    with open(OUTPUT_SUPPLEMENTED, mode='w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    notify_discord("✅ 欠損調査完了", f"103 名中 {found_count} 名の生年月日を URL スラッグから特定・補完しました。これから統合します。", 0x2ecc71)
    print(f"Supplemented data saved to: {OUTPUT_SUPPLEMENTED}")

if __name__ == "__main__":
    main()
