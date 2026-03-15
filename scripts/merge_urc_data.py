import pandas as pd
import os

# パス設定
DATA_DIR = 'data_sources'
MASTER_CSV = os.path.join(DATA_DIR, 'final_master_data_v25.csv')
URC_CSV = os.path.join(DATA_DIR, 'urc_full.csv')
OUTPUT_CSV = os.path.join(DATA_DIR, 'final_master_data_v25_integrated.csv')

def merge_csv():
    print(f"Loading master data: {MASTER_CSV}")
    master_df = pd.read_csv(MASTER_CSV)
    
    print(f"Loading URC data: {URC_CSV}")
    urc_df = pd.read_csv(URC_CSV)
    
    # 重複排除のキーとして Scraped_Url を使用
    # Scraped_Url が無い場合は英語名+生年月日などで補完することも検討するが、
    # 今回は Scraped_Url がカノニカルな ID なのでこれを優先
    
    # URC側にしかない列をマスターに合わせる
    # マスターの列を確認
    master_cols = master_df.columns.tolist()
    
    # 新規追加用DF
    new_players = []
    
    # 既存選手の更新
    print("Processing URC data for integration...")
    for idx, urc_row in urc_df.iterrows():
        url = urc_row['Scraped_Url']
        
        # マスター内で検索
        match = master_df[master_df['Scraped_Url'] == url]
        
        if not match.empty:
            # 既存選手の情報を補完（リーグが空ならURCを入れるなど）
            match_idx = match.index[0]
            if pd.isna(master_df.at[match_idx, 'リーグ']):
                master_df.at[match_idx, 'リーグ'] = 'urc'
        else:
            # 新規選手として追加候補
            new_row = {col: None for col in master_cols}
            for col in urc_df.columns:
                if col in new_row:
                    new_row[col] = urc_row[col]
            
            # デフォルト値の設定
            new_row['リーグ'] = 'urc'
            new_row['選手名'] = urc_row.get('選手名', urc_row.get('英語名'))
            new_players.append(new_row)
            
    if new_players:
        print(f"Adding {len(new_players)} new players from URC data.")
        new_players_df = pd.DataFrame(new_players)
        final_df = pd.concat([master_df, new_players_df], ignore_index=True)
    else:
        final_df = master_df
        
    print(f"Total players after merge: {len(final_df)}")
    final_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"Integrated CSV saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    merge_csv()
