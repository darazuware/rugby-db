import requests
from bs4 import BeautifulSoup
import time
import re
import pandas as pd
import os

CSV_PATH = 'data_sources/final_master_data_v27_normalized.csv'

def scrape_player_data(player_url):
    """リーグワン公式サイトからキャップ数と代表キャップ数を取得"""
    if not player_url or 'league-one.jp' not in player_url: return None, None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        
        # 429対策
        retries = 2
        for i in range(retries + 1):
            resp = requests.get(player_url, headers=headers, timeout=10)
            if resp.status_code == 200:
                break
            if resp.status_code == 429:
                print(f"  Got 429 for {player_url}. Sleeping 60s (Attempt {i+1})...")
                time.sleep(60)
            else:
                print(f"  Status {resp.status_code} for {player_url}")
                return None, None
        else:
            return None, None

        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text()
        
        l1_caps = None
        rep_caps = None
        
        # 1. リーグワンキャップ数 (出場試合数)
        l1_match = re.search(r'リーグワンキャップ数[：:\s]*(\d+)', text)
        if l1_match:
            l1_caps = l1_match.group(1)
            
        # 2. 日本代表キャップ数
        rep_match = re.search(r'日本代表キャップ数[：:\s]*(\d+)', text)
        if rep_match:
            rep_caps = f"Japan ({rep_match.group(1)})"
            
        return l1_caps, rep_caps
    except Exception as e:
        print(f"Error scraping {player_url}: {e}")
        return None, None

def main():
    print(f"Starting Robust League One caps update for {CSV_PATH}...")
    if not os.path.exists(CSV_PATH): return

    try:
        df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
    except Exception as e:
        print(f"Error reading CSV: {e}"); return

    if 'League_One_Caps' not in df.columns:
        df['League_One_Caps'] = ""
    else:
        df['League_One_Caps'] = df['League_One_Caps'].fillna('').astype(str)
    df['Representative_Caps'] = df['Representative_Caps'].fillna('').astype(str)

    # リーグワン所属選手を抽出
    l1_players = df[df['League'].fillna('').str.lower() == 'league-one'].copy()
    
    # 優先度：Division 1チーム 
    d1_teams = [
        "埼玉パナソニックワイルドナイツ", "東京サントリーサンゴリアス", "横浜キヤノンイーグルス",
        "クボタスピアーズ船橋・東京ベイ", "東芝ブレイブルーパス東京", "トヨタヴェルブリッツ",
        "コベルコ神戸スティーラーズ", "静岡ブルーレヴズ", "三菱重工相模原ダイナボアーズ",
        "リコーブラックラムズ東京", "浦安D-Rocks", "三重ホンダヒート"
    ]
    
    # 全リーグワン選手を対象にする
    target_players = l1_players
    print(f"Total League One players to update: {len(target_players)}")

    updated_count = 0
    checked_count = 0
    
    for idx, row in target_players.iterrows():
        url = str(row['Scraped_Url'])
        if 'league-one.jp/player/' not in url: continue
        
        checked_count += 1
        l1_caps, rep_caps = scrape_player_data(url)
        
        needs_update = False
        if l1_caps and str(l1_caps) != str(row['League_One_Caps']):
            df.at[idx, 'League_One_Caps'] = str(l1_caps)
            needs_update = True
        
        if rep_caps:
            old_caps = str(row['Representative_Caps'])
            if 'Japan' in old_caps:
                old_val = re.search(r'\((\d+)\)', old_caps)
                new_val = re.search(r'\((\d+)\)', rep_caps)
                if old_val and new_val and int(new_val.group(1)) > int(old_val.group(1)):
                    df.at[idx, 'Representative_Caps'] = rep_caps
                    needs_update = True
            elif not old_caps or old_caps in ['0', '0.0', 'nan']:
                df.at[idx, 'Representative_Caps'] = rep_caps
                needs_update = True
        
        if needs_update:
            updated_count += 1
            print(f"[{checked_count}/{len(target_players)}] Updated {row['Player_Name']}: L1={l1_caps}, Rep={rep_caps}")
        
        if checked_count % 10 == 0:
            print(f"Checked {checked_count} players (Updated {updated_count})...")
            # 定期的に保存
            df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')

        time.sleep(1.5) # 429回避のため1.5秒待機
        
    df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')
    print(f"Successfully updated {updated_count} players.")

if __name__ == "__main__":
    main()
