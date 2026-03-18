import pandas as pd
import os

CSV_FILE = "/Users/ktamatzmoto/Desktop/rugbypicks/data_sources/final_master_data_v25_integrated.csv"
BACKUP_FILE = CSV_FILE + ".bak"

def deduplicate_master():
    if not os.path.exists(CSV_FILE):
        print("Error: Master CSV not found.")
        return

    # バックアップ作成
    os.rename(CSV_FILE, BACKUP_FILE)
    print(f"Backup created at: {BACKUP_FILE}")

    df = pd.read_csv(BACKUP_FILE, dtype=str).fillna("")
    original_len = len(df)

    # 欠損判定関数
    def get_info_score(row):
        score = 0
        if row["身長"]: score += 1
        if row["体重"]: score += 1
        if row["生年月日"]: score += 1
        if len(row["英語名"]) > 5: score += 1 # フルネーム（Alfie）は A. より長い
        return score

    # キーとなる URL (Scraped_Url または URL)
    # 両方が空の場合は名前をキーにするが、基本はURL優先
    df["merge_key"] = df["Scraped_Url"].where(df["Scraped_Url"] != "", df["URL"])
    # URLも空なら英語名
    df["merge_key"] = df["merge_key"].where(df["merge_key"] != "", df["英語名"])

    # スコア計算
    df["info_score"] = df.apply(get_info_score, axis=1)

    # 重複排除: merge_key でグループ化し、スコアが最大の行を採用
    # 行番号を保持して安定させる
    df = df.sort_values(by=["merge_key", "info_score", "英語名"], ascending=[True, False, False])
    
    # 属性の統合 (A行にあってB行にない情報を補完)
    def merge_group(group):
        if len(group) == 1: return group.iloc[0]
        # 最初の行（最高スコア）をベースにする
        base = group.iloc[0].copy()
        for _, row in group.iterrows():
            for col in group.columns:
                if not base[col] and row[col]:
                    base[col] = row[col]
        return base

    df_merged = df.groupby("merge_key", sort=False).apply(merge_group).reset_index(drop=True)

    # 不要なカラムを削除
    if "merge_key" in df_merged.columns: del df_merged["merge_key"]
    if "info_score" in df_merged.columns: del df_merged["info_score"]

    df_merged.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
    print(f"Deduplication complete.")
    print(f"Original: {original_len} -> Merged: {len(df_merged)}")

if __name__ == "__main__":
    deduplicate_master()
