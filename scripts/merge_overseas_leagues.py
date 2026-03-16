import pandas as pd
import re
import os

def normalize_name(name):
    if not name or pd.isna(name): return ""
    return str(name).strip().upper()

def merge_leagues():
    master_v25_path = 'data_sources/final_master_data_v25.csv'
    prem_path = 'data_sources/gallagher_premiership_players.csv'
    top14_path = 'data_sources/top14_full.csv'
    output_path = 'data_sources/final_master_data_v25_integrated.csv'

    print(f"Loading master data: {master_v25_path}")
    df_master = pd.read_csv(master_v25_path)
    
    # 既存のキーを作成 (英語名 + 所属) または (Scraped_Url)
    # 英語名はスペースやケースを無視
    df_master['norm_name'] = df_master['英語名'].apply(normalize_name)
    
    # Premiership
    print(f"Merging Premiership: {prem_path}")
    df_prem = pd.read_csv(prem_path)
    # カラムマッピング (Prem -> Master)
    prem_map = {
        'title_en': '英語名',
        'name_jp': '選手名',
        'position': 'ポジション',
        'team_name': '所属チーム',
        'height': '身長',
        'weight': '体重',
        'birthday': '生年月日',
        'age': '年齢',
        'school': '高校',
        'shusshin': '大学',
        'url': 'URL',
        'career_history': 'キャリア遍歴',
        'caps': '代表キャップ数',
        'scraped_url': 'Scraped_Url',
        'career_history_en': 'Full_Career',
        'league': 'リーグ'
    }
    
    prem_added = 0
    prem_updated = 0
    
    new_rows = []
    for _, row in df_prem.iterrows():
        name_en = normalize_name(row['title_en'])
        s_url = str(row['scraped_url']).strip()
        
        # マッチング
        mask = (df_master['Scraped_Url'] == s_url) | (df_master['norm_name'] == name_en)
        match = df_master[mask]
        
        if not match.empty:
            # 更新 (ここでは所属とリーグを優先的に更新)
            idx = match.index[0]
            df_master.at[idx, '所属チーム'] = row['team_name']
            df_master.at[idx, 'リーグ'] = 'premiership'
            # Wikipediaのフルネームがあれば更新
            if len(str(row['title_en'])) > len(str(df_master.at[idx, '英語名'])):
                df_master.at[idx, '英語名'] = row['title_en']
            prem_updated += 1
        else:
            # 新規追加用データを準備
            nr = {col: "" for col in df_master.columns if col != 'norm_name'}
            for prem_col, master_col in prem_map.items():
                if prem_col in row:
                    nr[master_col] = row[prem_col]
            nr['選手名_カタカナ'] = row.get('name_jp', '')
            new_rows.append(nr)
            prem_added += 1

    if new_rows:
        df_master = pd.concat([df_master, pd.DataFrame(new_rows)], ignore_index=True)

    # Top 14
    print(f"Merging Top 14: {top14_path}")
    df_top14 = pd.read_csv(top14_path)
    
    top14_added = 0
    top14_updated = 0
    
    new_rows_top14 = []
    for _, row in df_top14.iterrows():
        name_en = normalize_name(row['英語名'])
        s_url = str(row['Scraped_Url']).strip()
        
        mask = (df_master['Scraped_Url'] == s_url) | (df_master['norm_name'] == name_en)
        match = df_master[mask]
        
        if not match.empty:
            idx = match.index[0]
            df_master.at[idx, '所属チーム'] = row['所属チーム']
            df_master.at[idx, 'リーグ'] = 'top14'
            top14_updated += 1
        else:
            nr = row.to_dict()
            nr['リーグ'] = 'top14'
            new_rows_top14.append(nr)
            top14_added += 1

    if new_rows_top14:
        df_master = pd.concat([df_master, pd.DataFrame(new_rows_top14)], ignore_index=True)

    # 不要なカラムを削除
    if 'norm_name' in df_master.columns: df_master = df_master.drop(columns=['norm_name'])
    
    # 重複排除の最終確認 (英語名 + 生年月日 が一致すれば重複とみなす)
    # df_master = df_master.drop_duplicates(subset=['英語名', '生年月日'], keep='first')

    print(f"Final Count: {len(df_master)}")
    print(f"Premiership: Added {prem_added}, Updated {prem_updated}")
    print(f"Top 14: Added {top14_added}, Updated {top14_updated}")
    
    df_master.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Saved integrated data to {output_path}")

if __name__ == "__main__":
    merge_leagues()
