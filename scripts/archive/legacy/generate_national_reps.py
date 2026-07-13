import pandas as pd
import os

# パス設定
RAW_REP_CSV = "data_sources/international_representatives_raw_v2.csv"
V25_CSV = "data_sources/final_master_data_v25.csv"
OUTPUT_CSV = "data_sources/national_representatives.csv"

def main():
    if not os.path.exists(RAW_REP_CSV):
        print(f"Missing {RAW_REP_CSV}")
        return

    df_raw = pd.read_csv(RAW_REP_CSV)
    
    # 既存のv25データを読み込み（名寄せ用）
    if os.path.exists(V25_CSV):
        df_v25 = pd.read_csv(V25_CSV)
        # 英語名->カタカナ名/タイトルのマッピング作成
        name_map = {}
        for _, row in df_v25.iterrows():
            en = str(row.get('name_en', '')).strip()
            if en:
                name_map[en.upper()] = {
                    'title': row.get('title', ''),
                    'katakana': row.get('name_jp', '')
                }
    else:
        name_map = {}

    print(f"Processing {len(df_raw)} representative records...")

    # 選手ごとに集約（最新のキャップ数と所属チーム、トーナメントを取得）
    # rawデータは既にソートされている前提（大会が新しい順など）
    # ここでは単純に選手名と代表チームのペアで集約
    
    summary = []
    # 選手名、代表チームでグループ化
    grouped = df_raw.groupby(['name_en', 'representative_team'])
    
    for (name, rep), group in grouped:
        # キャップ数は最大値、トーナメントはリスト、クラブは最新（最初の行）を取得
        latest_row = group.iloc[0]
        max_caps = group['caps'].max()
        tournaments = ", ".join(group['tournament'].unique())
        
        # v25からのマッピング
        mapping = name_map.get(name.upper(), {})
        
        summary.append({
            "name_en": name,
            "name_jp": mapping.get('katakana', ''),
            "title": mapping.get('title', name),
            "representative_team": rep,
            "latest_caps": max_caps,
            "last_club": latest_row['club'],
            "tournaments": tournaments,
            "league": mapping.get('league', 'international')
        })

    df_output = pd.DataFrame(summary)
    df_output.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    
    print(f"Generated {len(df_output)} unique representative records to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
