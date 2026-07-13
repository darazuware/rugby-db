import csv
import os
import sys
import re
from datetime import datetime

# scripts ディレクトリをパスに追加して player_utils をインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from player_utils import PlayerDataProcessor

# プレミアシップ専用のCSVをターゲットにする
PREM_CSV = "/Users/ktamatzmoto/Desktop/rugbypicks/data_sources/gallagher_premiership_players.csv"
SUPPLEMENT_CSV = "/tmp/supplemented_prem_players.csv"
BACKUP_CSV = PREM_CSV + ".bak_" + datetime.now().strftime("%Y%m%d%H%M%S")

import subprocess

DISCORD_NOTIFY_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "discord_notify.py")

def notify_discord(title, message, color=0x3498db):
    try:
        color_hex = hex(color)
        subprocess.run(["python3", DISCORD_NOTIFY_SCRIPT, title, message, color_hex], check=True)
    except Exception as e:
        print(f"Discord notice failed: {e}")

def format_date_to_dot(date_str):
    """YYYY-MM-DD や Month DD, YYYY を YYYY.MM.DD に変換"""
    if not date_str:
        return ""
    
    # すでに YYYY.MM.DD の場合はそのまま
    if re.match(r'^\d{4}\.\d{2}\.\d{2}$', date_str):
        return date_str

    for fmt in ("%Y-%m-%d", "%B %d, %Y", "%d %B %Y"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y.%m.%d")
        except ValueError:
            continue
    return date_str

def main():
    if not os.path.exists(SUPPLEMENT_CSV):
        print(f"Error: {SUPPLEMENT_CSV} not found.")
        return

    if not os.path.exists(PREM_CSV):
        print(f"Error: {PREM_CSV} not found.")
        return

    # 補完データの読み込み
    supplement_data = {}
    with open(SUPPLEMENT_CSV, mode='r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('birth_date'):
                # キーを strip して保存
                supplement_data[row['name_en'].strip()] = row['birth_date'].strip()

    if not supplement_data:
        print("No new birth dates to merge.")
        return

    print(f"Loaded {len(supplement_data)} new birth dates from supplement CSV.")
    print(f"DEBUG: 'AJ MacGinty' in supplement_data: {'AJ MacGinty' in supplement_data}")

    # 既存データの読み込みと更新
    updated_count = 0
    rows = []
    
    # バックアップ作成
    import shutil
    shutil.copy2(PREM_CSV, BACKUP_CSV)
    print(f"Backup created at: {BACKUP_CSV}")

    with open(PREM_CSV, mode='r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for i, row in enumerate(reader):
            # gallagher_premiership_players.csv は name_en カラムを持つ
            name_en_raw = row.get('name_en')
            name_en = name_en_raw.strip() if name_en_raw else ""
            
            if name_en in supplement_data:
                raw_birth_date = supplement_data[name_en]
                
                if i < 10 or "AJ MacGinty" in name_en:
                    print(f"MATCH FOUND: {name_en} -> {raw_birth_date}")
                
                # 年齢計算
                age = PlayerDataProcessor.calculate_age(raw_birth_date)
                
                # 形式変換
                formatted_birth_date = format_date_to_dot(raw_birth_date)
                
                # 更新 (このファイルのカラム名は birthday と age)
                row['birthday'] = formatted_birth_date
                if age:
                    row['age'] = str(age)
                
                updated_count += 1
                if i < 10 or "AJ MacGinty" in name_en:
                    print(f"DEBUG After Update: {name_en} -> birthday=[{row['birthday']}], age=[{row.get('age')}]")
                
                print(f"Updated: {name_en} -> {formatted_birth_date} (Age: {age})")
            
            rows.append(row)

    # 書き戻し
    with open(PREM_CSV, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Successfully updated {updated_count} players in {PREM_CSV}.")
    
    if updated_count > 0:
        notify_discord("🆙 補完データマージ完了", f"Wikipedia から取得した {updated_count} 名分の生年月日情報を Premiership 選手データに反映しました。", 0x9b59b6)

if __name__ == "__main__":
    main()
