import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import os
import re

# --- 設定 ---
INPUT_FILE = "final_master_data_v6_cleaned (1).csv" # または最新のCSV
OUTPUT_FILE = "final_master_data_v9_complete.csv"
BASE_URL = "https://all.rugby"

def get_soup(url):
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    try:
        time.sleep(1.5) # サーバー負荷対策
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            return BeautifulSoup(response.content, "html.parser")
    except:
        pass
    return None

def scrape_full_profile(player_url):
    soup = get_soup(player_url)
    if not soup: return "", ""
    
    intl_parts = []
    career_parts = []

    # 1. 代表歴 (National Team Stats)
    # class="stat-team" を探す (各代表チームごとのブロック)
    # 構造: チーム名(h2) -> Statsテーブル
    stat_blocks = soup.select(".stat-team")
    if not stat_blocks:
        # 見つからない場合のバックアップ: 全テーブルから "Caps" を探す
        for tbl in soup.find_all("table"):
            if "Caps" in tbl.get_text():
                # 行解析 (簡易版)
                for row in tbl.find_all("tr")[1:]:
                    cols = row.find_all("td")
                    if len(cols) >= 4:
                        team = cols[0].get_text(strip=True)
                        caps = cols[2].get_text(strip=True)
                        tries = cols[3].get_text(strip=True)
                        if team and caps.isdigit():
                            intl_parts.append(f"{team}({caps}CAP/{tries}T)")
    else:
        # 正確なクラス指定による抽出
        for block in stat_blocks:
            team_name_tag = block.select_one(".title-stat-team")
            if team_name_tag:
                team_name = team_name_tag.get_text(strip=True)
                # テーブルを探す
                rows = block.select("table tr")
                for row in rows:
                    cols = row.find_all("td")
                    # Total行などを探す、あるいは最新シーズンの合計
                    # ここでは "Total" 行または単純に数値がある行を取得
                    if len(cols) >= 4 and cols[2].get_text(strip=True).isdigit():
                         caps = cols[2].get_text(strip=True)
                         tries = cols[3].get_text(strip=True)
                         intl_parts.append(f"{team_name}({caps}CAP/{tries}T)")
                         break # 1チームにつき1行(Total)だけでOKならbreak

    # 2. クラブ遍歴 (Club Career)
    # class="cartouche-club" を持つテーブルを特定
    career_table = soup.select_one("table.cartouche-club")
    
    if career_table:
        # 行を走査 (ヘッダーを除く)
        for row in career_table.find_all("tr")[1:]:
            cols = row.find_all("td")
            # 構造: Year | Logo | Club | Country | Games | Starts | Tries | Points ...
            # index: 0    1      2      3         4       5        6       7
            if len(cols) >= 7:
                year = cols[0].get_text(strip=True)
                club = cols[2].get_text(strip=True)
                games = cols[4].get_text(strip=True)
                tries = cols[6].get_text(strip=True)
                
                # データ整形: "2024-25 Kyuden Voltex (3G/2T)"
                # ゴミデータ(空白など)を除去
                if year and club:
                     stats_str = ""
                     if games and games != "-":
                         stats_str = f"({games}G"
                         if tries and tries != "-":
                             stats_str += f"/{tries}T"
                         stats_str += ")"
                     
                     career_parts.append(f"{year} {club} {stats_str}")

    return "、".join(list(set(intl_parts))), " -> ".join(career_parts) # 重複排除

def main():
    df = pd.read_csv(INPUT_FILE)
    if "Full_Career" not in df.columns: df["Full_Career"] = ""
    
    print(f"Starting precise scraping for {len(df)} players...")

    for idx, row in df.iterrows():
        eng_name = str(row["英語名"])
        if not eng_name or eng_name == "nan": continue
        
        # 検索URL生成
        search_url = f"{BASE_URL}/search?q={urllib.parse.quote_plus(eng_name)}"
        soup = get_soup(search_url)
        
        player_link = None
        if soup:
            # 検索結果リスト (.list-search-player) からリンクを取得
            link_tag = soup.select_one(".list-search-player a")
            if link_tag: player_link = BASE_URL + link_tag.get("href")

        if player_link:
            print(f"[{idx+1}] Processing: {eng_name}")
            intl, career = scrape_full_profile(player_link)
            
            # データ更新
            if intl:
                current = str(row["代表キャップ数"]) if pd.notna(row["代表キャップ数"]) else ""
                # 既存データとマージ (重複しないように)
                if intl not in current:
                    df.at[idx, "代表キャップ数"] = f"{current}、{intl}".strip("、")
            
            # キャリアは上書き (最新情報のため)
            if career:
                df.at[idx, "Full_Career"] = career
                print(f"      -> Career Updated: {career[:60]}...")
            else:
                print("      -> No career data found.")
        else:
            print(f"[{idx+1}] Not found: {eng_name}")

        if (idx + 1) % 10 == 0:
            df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print("All Finished!")

if __name__ == "__main__":
    main()