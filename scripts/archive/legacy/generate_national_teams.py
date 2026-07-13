import pandas as pd
import json
import os
import re
from player_utils import PlayerDataProcessor

# 設定
CSV_PATH = 'data_sources/final_master_data_v27_normalized.csv'
CONFIG_PATH = 'data/national_teams_config.json'
OUTPUT_PATH = 'data/national_players_map.json'

def main():
    print(f"Loading config from {CONFIG_PATH}...")
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # マッピング辞書の構築
    country_to_id = {}
    for team in config:
        tid = team['id']
        name_clean = team['name'].replace('代表', '')
        country_to_id[name_clean.lower()] = tid
        country_to_id[tid.lower()] = tid
        if 'en_name' in team:
            country_to_id[team['en_name'].lower()] = tid

    # 追加の国名エイリアス
    aliases = {
        "nz": "new-zealand", "new zealand": "new-zealand", "ニュージーランド": "new-zealand",
        "sa": "south-africa", "south africa": "south-africa", "南アフリカ": "south-africa",
        "aus": "australia", "オーストラリア": "australia",
        "usa": "usa", "united states": "usa", "アメリカ": "usa",
        "ire": "ireland", "ireland": "ireland", "アイルランド": "ireland",
        "eng": "england", "england": "england", "イングランド": "england",
        "fra": "france", "french": "france", "française": "france", "français": "france", "フランス": "france",
        "jpn": "japan", "japan": "japan", "日本": "japan"
    }
    country_to_id.update(aliases)

    print(f"Loading CSV from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
    
    national_players = {team['id']: [] for team in config}
    processed_count = 0

    for i, row in df.iterrows():
        caps_str = str(row.get('Representative_Caps', '')).strip()
        if not caps_str or caps_str == 'nan':
            continue
            
        # 複数の代表歴がある可能性を考慮 (改行やカンマで区切られている場合)
        # 例: "日本代表(5)\nセブンズ日本(3)"
        lines = re.split(r'[\n,]', caps_str)
        
        target_ids = set()
        for line in lines:
            line = line.strip().lower()
            if not line: continue
            
            # 直接一致
            tid = country_to_id.get(line)
            if tid:
                target_ids.add(tid)
                continue
                
            # 部分一致 (例: "日本代表(5)" -> "日本" -> "japan")
            # 括弧内の数字を除去してクリーンアップ
            clean_line = re.sub(r'\(.*?\)', '', line).strip()
            # 絵文字や特殊記号を除去 (Python 3の\wはデフォルトでUnicode文字を含む)
            clean_line = re.sub(r'[^\w\s]', '', clean_line).strip()
            
            # 再度直接一致を確認
            tid = country_to_id.get(clean_line)
            if tid:
                target_ids.add(tid)
                continue
                
            # それでもダメならキーが含まれているか確認
            for key, val in country_to_id.items():
                if key in line:
                    target_ids.add(val)
                    break
        
        if not target_ids: continue
        
        for target_id in target_ids:
            name_en = str(row.get('Player_Name', ''))
            scraped_url = str(row.get('Scraped_Url', ''))
            
            # 共通スラッグ生成
            slug = PlayerDataProcessor.generate_player_slug(name_en, i + 1, scraped_url)
            
            # データの安全な取得
            name_ja = PlayerDataProcessor.get_safe_attr(row, 'Full_Name')
            if not name_ja:
                name_ja = name_en

            # 年齢の取得 (欠落していれば生年月日から算出)
            age = PlayerDataProcessor.get_safe_attr(row, 'Age')
            if not age or age == '':
                dob = PlayerDataProcessor.get_safe_attr(row, 'Birth_Date')
                if dob:
                    calculated_age = PlayerDataProcessor.calculate_age(dob)
                    if calculated_age:
                        age = f"{calculated_age}.0"

            # マップ用のデータ構造
            player_entry = {
                "name_ja": name_ja,
                "name_en": name_en,
                "slug": slug,
                "position": PlayerDataProcessor.get_safe_attr(row, 'Position'),
                "team": PlayerDataProcessor.get_safe_attr(row, 'Current_Team'),
                "league": PlayerDataProcessor.get_safe_attr(row, 'League'),
                "caps": PlayerDataProcessor.get_safe_attr(row, 'Representative_Caps', '0'),
                "age": age,
                "height": PlayerDataProcessor.get_safe_attr(row, 'Height'),
                "weight": PlayerDataProcessor.get_safe_attr(row, 'Weight')
            }
            
            national_players[target_id].append(player_entry)
            processed_count += 1

    # 重複排除とソート (キャップ数順)
    for tid in national_players:
        # スラッグベースで重複排除
        seen_slugs = set()
        unique_list = []
        for p in national_players[tid]:
            if p['slug'] not in seen_slugs:
                unique_list.append(p)
                seen_slugs.add(p['slug'])
        
        # ソート: キャップ数順 (数値化して降順)
        unique_list.sort(key=lambda x: int(re.search(r'(\d+)', str(x['caps'])).group(1)) if re.search(r'(\d+)', str(x['caps'])) else 0, reverse=True)
        national_players[tid] = unique_list

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(national_players, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully mapped {processed_count} instances to {len(seen_slugs)} unique players in {OUTPUT_PATH}.")

if __name__ == "__main__":
    main()
