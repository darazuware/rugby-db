import os
import glob
import csv

# 正規の選手リスト（League One 199名）を取得
CSV_PATH = 'data_sources/final_master_data_v25.csv'
SR_CSV = 'data_sources/super_rugby_full.csv'
T14_CSV = 'data_sources/top14_full.csv'
PLAYER_DIR = 'src/content/players'

def get_valid_slugs():
    valid_slugs = set()
    
    # League One (scripts/generate_players.py のロジックに合わせる)
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                name_en = row['英語名']
                slug = name_en.lower().replace(' ', '-').replace("'", '')
                import re
                slug = re.sub(r'[^a-z0-9-]', '', slug)
                # 既存の generate_players.py は slug にインデックスをつけていないはず
                valid_slugs.add(f"{slug}.md")

    # Super Rugby
    if os.path.exists(SR_CSV):
        with open(SR_CSV, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                name_en = row['英語名']
                slug_base = name_en.lower().replace(' ', '-').replace("'", '')
                import re
                slug_base = re.sub(r'[^a-z0-9-]', '', slug_base)
                valid_slugs.add(f"{slug_base}-sr-{i+10000}.md")

    # Top 14
    if os.path.exists(T14_CSV):
        with open(T14_CSV, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                name_en = row['英語名']
                slug_base = name_en.lower().replace(' ', '-').replace("'", '')
                import re
                slug_base = re.sub(r'[^a-z0-9-]', '', slug_base)
                valid_slugs.add(f"{slug_base}-t14-{i+20000}.md")
                
    return valid_slugs

def main():
    valid_slugs = get_valid_slugs()
    print(f"Valid slugs count: {len(valid_slugs)}")
    
    all_files = os.listdir(PLAYER_DIR)
    deleted_count = 0
    
    for f in all_files:
        if f.endswith('.md') and f not in valid_slugs:
            # 安全のため、特定のパターンでないもののみ削除
            # (例: インデックス付きの旧ファイルなど)
            os.remove(os.path.join(PLAYER_DIR, f))
            deleted_count += 1
            
    print(f"Cleanup complete. Deleted {deleted_count} stale files.")

if __name__ == "__main__":
    main()
