import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random

# --- 設定 ---
INPUT_FILE = "final_master_data_v4.csv"
OUTPUT_FILE = "final_master_data_v5_complete.csv"

# 強力な名寄せ辞書
school_map = {
    # 英語 -> カタカナ
    "Endeavorsportshighschool": "エンデバースポーツ高校",
    "SaintJoseph’sCollegeHuntersHill": "セントジョセフ・カレッジ",
    "Saint Joseph's": "セントジョセフ・カレッジ",
    "Tupou College": "トゥポウカレッジ",
    "TUPOU COLLEGE": "トゥポウカレッジ",
    "Hamilton Boys": "ハミルトンボーイズ高校",
    "Brisbane State High": "ブリスベンステート高校",
    "Wesley College": "ウェズリーカレッジ",
    "Marist Brothers": "マリストブラザーズ高校",
    "University of Technology Sydney": "シドニー工科大学",
    "Auckland": "オークランド大学",
    "Canterbury": "カンタベリー大学",
    
    # 略称 -> 正式名称 (高校)
    "御所": "御所実業高校", "御所実": "御所実業高校",
    "東海大仰星": "東海大大阪仰星高校",
    "桐蔭学園": "桐蔭学園高校", "大阪桐蔭": "大阪桐蔭高校",
    "京都成章": "京都成章高校", "天理": "天理高校",
    "報徳学園": "報徳学園高校", "石見智翠館": "石見智翠館高校",
    "佐賀工": "佐賀工業高校", "長崎北陽台": "長崎北陽台高校",
    "流経大柏": "流通経済大柏高校", "國學院久我山": "國學院久我山高校",
    "茗溪学園": "茗溪学園高校", "秋田工": "秋田工業高校",
    "東福岡": "東福岡高校", "筑紫": "筑紫高校", "熊本西": "熊本西高校",
    
    # 略称 -> 正式名称 (大学)
    "帝京": "帝京大学", "明治": "明治大学", "早稲田": "早稲田大学",
    "慶應": "慶應義塾大学", "同志社": "同志社大学", "天理大": "天理大学",
    "京産": "京都産業大学", "日体": "日本体育大学", "流通経済": "流通経済大学",
    "筑波": "筑波大学", "東海": "東海大学", "近畿": "近畿大学",
    "法政": "法政大学", "中央": "中央大学", "大東文化": "大東文化大学",
    "関東学院": "関東学院大学", "拓殖": "拓殖大学", "摂南": "摂南大学",
    "関西学院": "関西学院大学", "立命館": "立命館大学", "日本": "日本大学",
}

def normalize_school_name(name, category="高校"):
    if pd.isna(name): return name
    name = str(name).strip()
    
    # 辞書にあるものを変換
    if name in school_map:
        return school_map[name]
    
    # 漢字のみで「高校」「大学」がつかない場合の補完
    if category == "高校" and not name.endswith(("高校", "カレッジ", "学校")):
        if name.endswith(("工", "実")): return name + "業高校"
        return name + "高校"
    elif category == "大学" and not name.endswith(("大学", "カレッジ")):
        return name + "大学"
        
    return name

def scrape_player_data(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200: return None
        
        soup = BeautifulSoup(resp.content, "html.parser")
        
        data = {}
        
        # 1. リーグワンキャップ数 (例: "7" Caps)
        # クラス名や構造はサイトに合わせて調整が必要
        caps_elem = soup.find("div", class_="caps-count") # 仮のクラス名
        if caps_elem:
            data['caps'] = caps_elem.get_text(strip=True)
            
        # 2. 年齢
        age_elem = soup.find("span", class_="age") # 仮
        if age_elem:
            data['age'] = age_elem.get_text(strip=True).replace("歳", "")
            
        # 3. 学校名 (プロフィール表から取得)
        # 表の構造から「出身校」を探す
        rows = soup.find_all("tr")
        for row in rows:
            th = row.find("th")
            if th and "出身校" in th.get_text():
                td = row.find("td")
                if td:
                    data['school'] = td.get_text(strip=True)
                    
        return data

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def main():
    print("Loading data...")
    df = pd.read_csv(INPUT_FILE)
    
    # 1. 学校名の正規化 (ローカル辞書適用)
    print("Normalizing school names...")
    df['高校'] = df['高校'].apply(lambda x: normalize_school_name(x, "高校"))
    df['大学'] = df['大学'].apply(lambda x: normalize_school_name(x, "大学"))
    
    # 2. Webスクレイピング (全件ループ)
    print("Starting Web Scraping for stats update...")
    total = len(df)
    
    for index, row in df.iterrows():
        url = row.get('URL')
        if pd.isna(url): continue
        
        print(f"[{index+1}/{total}] Processing: {row['選手名']} ...", end="\r")
        
        # 実際のアクセス (サーバー負荷考慮して待機)
        new_data = scrape_player_data(url)
        time.sleep(1.0 + random.random()) # 1〜2秒待機
        
        if new_data:
            if 'caps' in new_data:
                df.at[index, 'リーグワンキャップ数'] = new_data['caps']
            if 'age' in new_data:
                df.at[index, '年齢'] = new_data['age']
            if 'school' in new_data:
                # 学校名が取得できたら、高校・大学に分割して保存するロジックが必要
                # ここでは単純な上書きではなく、補完に留める等の調整が可能
                pass

    print("\nSaving updated data...")
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Done! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()