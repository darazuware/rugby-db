import pandas as pd
import os

# 設定
MASTER_CSV = 'data_sources/final_master_data_v17_consolidated.csv'
NEW_DATA_CSV = 'data_sources/latest_scraped_data.csv'  # 新しく取得したデータのパス（例）

def update_master_data():
    if not os.path.exists(MASTER_CSV):
        print(f"Master CSV not found at {MASTER_CSV}")
        return

    # 既存データの読み込み
    df_master = pd.read_csv(MASTER_CSV)
    
    if os.path.exists(NEW_DATA_CSV):
        # 新規データの読み込み
        df_new = pd.read_csv(NEW_DATA_CSV)
        
        # 選手名をキーにして外部結合（既存にない選手を追加）
        # ※実際にはURLやIDなどのユニークなキーを使用するのが望ましい
        df_updated = pd.concat([df_master, df_new]).drop_duplicates(subset=['選手名', '英語名'], keep='first')
        
        # 更新後の保存
        df_updated.to_csv(MASTER_CSV, index=False)
        print(f"Updated {MASTER_CSV} with new data from {NEW_DATA_CSV}")
    else:
        print("No new data to merge.")

    # 更新したCSVを元にMarkdownを再生成する
    print("Next step: Run 'python3 scripts/generate_players.py' to reflect changes in the website.")

if __name__ == "__main__":
    # pandasが必要なため、環境に合わせてインストールまたは実行
    try:
        update_master_data()
    except ImportError:
        print("Please install pandas: pip install pandas")
