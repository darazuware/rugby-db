import csv
import os
import sys
import re
from datetime import datetime
import pandas as pd

# scripts ディレクトリをパスに追加して player_utils をインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from player_utils import PlayerDataProcessor

MASTER_CSV = "/Users/ktamatzmoto/Desktop/rugbypicks/data_sources/final_master_data_v25_integrated.csv"
SUPPLEMENT_CSV = "/tmp/supplemented_prem_103.csv"
DISCORD_NOTIFY_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "discord_notify.py")

# 各リーグのソースCSV (必要に応じて更新するため)
SOURCE_CSVS = {
    'premiership': "/Users/ktamatzmoto/Desktop/rugbypicks/data_sources/gallagher_premiership_players.csv",
    'urc': "/Users/ktamatzmoto/Desktop/rugbypicks/data_sources/urc_players.csv", # 仮
}

def notify_discord(title, message, color=0x3498db):
    try:
        color_hex = hex(color)
        import subprocess
        subprocess.run(["python3", DISCORD_NOTIFY_SCRIPT, title, message, color_hex], check=True)
    except Exception as e:
        print(f"Discord notice failed: {e}")

def format_date_to_dot(date_str):
    if not date_str: return ""
    if re.match(r'^\d{4}\.\d{2}\.\d{2}$', date_str): return date_str
    for fmt in ("%Y-%m-%d", "%B %d, %Y", "%d %B %Y"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y.%m.%d")
        except ValueError: continue
    return date_str

def merge_to_csv(target_path, supplement_dict, name_col, bday_col, age_col):
    if not os.path.exists(target_path):
        print(f"Skip: {target_path} not found.")
        return 0

    print(f"Updating {target_path}...")
    df = pd.read_csv(target_path, dtype=str).fillna("")
    updated_count = 0

    for idx, row in df.iterrows():
        name_en = str(row.get(name_col, "")).strip()
        if name_en in supplement_dict:
            raw_bday = supplement_dict[name_en]
            formatted_bday = format_date_to_dot(raw_bday)
            age = PlayerDataProcessor.calculate_age(raw_bday)
            
            df.at[idx, bday_col] = formatted_bday
            if age:
                df.at[idx, age_col] = str(age)
            updated_count += 1

    if updated_count > 0:
        df.to_csv(target_path, index=False, encoding='utf-8-sig')
        print(f"  -> Updated {updated_count} players.")
    return updated_count

def main():
    if not os.path.exists(SUPPLEMENT_CSV):
        print("Error: Supplement CSV not found.")
        return

    # 補完データの読み込み
    supplement_dict = {}
    with open(SUPPLEMENT_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('birth_date'):
                supplement_dict[row['name_en'].strip()] = row['birth_date'].strip()

    if not supplement_dict:
        print("No birth dates found in supplement CSV.")
        return

    print(f"Loaded {len(supplement_dict)} new birth dates.")

    # 1. マスターデータへのマージ
    master_updated = merge_to_csv(MASTER_CSV, supplement_dict, '英語名', '生年月日', '年齢')

    # 2. 各ソースCSVへのマージ (反映できるものだけ)
    # Premiership
    merge_to_csv(SOURCE_CSVS['premiership'], supplement_dict, 'title_en', 'birthday', 'age')
    
    # URC (もし /data_sources/ 内にあれば)
    # ※ URC のソースファイル名が正しいか未確認ですが、一旦定義に従って試行
    
    notify_discord("🎉 全リーグ統合補完完了", 
                   f"Wikipedia から取得したデータをマスターに統合しました。\n" \
                   f"マスター更新数: {master_updated} 名\n" \
                   f"取得成功総数: {len(supplement_dict)} 名", 
                   0x2ecc71)

if __name__ == "__main__":
    main()
