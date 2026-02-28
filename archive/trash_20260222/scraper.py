import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import os

# --- 設定 ---
INPUT_FILE = "final_master_data_v6_cleaned (1).csv"
OUTPUT_FILE = "final_master_data_v8_full_career.csv"
BASE_URL = "https://all.rugby"

def get_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        time.sleep(1.5) # サーバーに優しく（BAN防止）
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        print(f"      [Error] Access failed: {e}")
    return None

def search_player(name):
    print(f"   Searching: {name}...")
    query = urllib.parse.quote_plus(name)
    search_url = f"{BASE_URL}/search?q={query}"
    
    soup = get_soup(search_url)
    if not soup: return None

    # 検索結果の一番上のリンクを取得
    # all.rugbyの検索結果は .list-search-player などのクラスに入っている
    link_tag = soup.select_one("a[href*='/player/']")
    if link_tag:
        path = link_tag.get("href")
        return f"{BASE_URL}{path}" if path.startswith("/") else path
    return None

def scrape_stats(player_url):
    soup = get_soup(player_url)
    if not soup: return "", ""
    
    # 1. 代表歴 (International Stats)
    caps_list = []
    # 国旗アイコンがあるテーブルや "National Team" のセクションを探す
    sections = soup.select("div.block-stat")
    for sec in sections:
        header = sec.select_one("h2")
        if header and ("National" in header.text or "International" in header.text or "代表" in header.text):
            rows = sec.select("table tr")
            for row in rows[1:]: # ヘッダー以外
                cols = row.find_all("td")
                if len(cols) >= 3:
                    team = cols[0].get_text(strip=True)
                    caps = cols[2].get_text(strip=True) # 通常3列目がCaps
                    caps_list.append(f"{team}({caps}CAP)")

    # 2. クラブ歴 (Club Career)
    career_list = []
    career_table = soup.select_one("table.cartouche-club") # クラブ遍歴テーブルの推測
    if not career_table:
        # 見つからない場合は全テーブルから探す
        for tbl in soup.find_all("table"):
            if "Saison" in tbl.text or "Club" in tbl.text:
                career_table = tbl
                break

    if career_table:
        for row in career_table.select("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) >= 2:
                year = cols[0].get_text(strip=True)
                club = cols[1].get_text(strip=True)
                career_list.append(f"{year} {club}")

    return "、".join(caps_list), " -> ".join(career_list)

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} が見つかりません。")
        return

    df = pd.read_csv(INPUT_FILE)
    print(f"Starting processing for {len(df)} players...")

    # 新しい列の準備
    if "Full_Career" not in df.columns:
        df["Full_Career"] = ""

    # テストとして最初の10人、または英語名がある選手を優先して回す
    # (全件やる場合は df.iterrows() に戻してください)
    count = 0
    for idx, row in df.iterrows():
        eng_name = str(row["英語名"])
        if not eng_name or eng_name == "nan": continue
        
        print(f"[{idx+1}/{len(df)}] Processing {row['選手名']} ({eng_name})")
        
        player_url = search_player(eng_name)
        if player_url:
            print(f"      Found URL: {player_url}")
            intl_caps, career = scrape_stats(player_url)
            
            # 代表キャップの更新 (B案: 追記)
            if intl_caps:
                current = str(row["代表キャップ数"]) if pd.notna(row["代表キャップ数"]) else ""
                df.at[idx, "代表キャップ数"] = f"{current}、{intl_caps}".strip("、")
            
            # キャリア履歴の保存
            df.at[idx, "Full_Career"] = career
            print(f"      Success: {intl_caps}")
        else:
            print(f"      [Skip] Player not found on all.rugby")
        
        count += 1
        # 5分おきに保存して、万が一の停止に備える
        if count % 10 == 0:
            df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
            print("--- Intermediate save completed ---")

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"Finished! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()