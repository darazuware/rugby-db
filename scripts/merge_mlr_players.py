import pandas as pd
import os
import re

def clean_height(h):
    if not h or pd.isna(h): return ""
    m = re.search(r"(\d)m(\d+)", str(h))
    if m:
        return int(m.group(1)) * 100 + int(m.group(2))
    return h

def clean_weight(w):
    if not w or pd.isna(w): return ""
    m = re.search(r"(\d+)", str(w))
    if m:
        return m.group(1)
    return w

def merge_mlr():
    master_path = "data_sources/final_master_data_v25_integrated.csv"
    mlr_raw_path = "data_sources/mlr_players_allrugby_2024.csv"
    
    if not os.path.exists(master_path) or not os.path.exists(mlr_raw_path):
        print("Missing files.")
        return
        
    df_master = pd.read_csv(master_path)
    df_mlr = pd.read_csv(mlr_raw_path)
    
    print(f"Master: {len(df_master)} rows, MLR Raw: {len(df_mlr)} rows")
    
    new_players = []
    
    current_max_id = 0
    if "Player_ID" in df_master.columns:
        current_max_id = df_master["Player_ID"].max()
        if pd.isna(current_max_id): current_max_id = 10000
    else:
        current_max_id = 10000
        
    for _, row in df_mlr.iterrows():
        url = row["Source_URL"]
        full_name = row["Full_Name"]
        
        # 重複チェック (URL優先)
        existing = df_master[df_master["Scraped_Url"] == url]
        
        if not existing.empty:
            idx = existing.index[0]
            # 既存選手のリーグ情報を更新または追加
            # 既に別リーグがある場合はカンマ区切りにするなどの処理も考えられるが、
            # 今回は MLR 所属として更新（または追記）
            df_master.at[idx, "League"] = "MLR"
            df_master.at[idx, "Current_Team"] = row["Team"]
        else:
            # 新規追加
            current_max_id += 1
            names = full_name.split(" ", 1)
            first = names[0]
            last = names[1] if len(names) > 1 else ""
            
            new_players.append({
                "Player_ID": current_max_id,
                "First_Name": first,
                "Last_Name": last,
                "Full_Name": full_name,
                "Position": row["Position"],
                "Height": clean_height(row["Height"]),
                "Weight": clean_weight(row["Weight"]),
                "Birth_Date": "", # 後で補完される可能性
                "Age": row["Age"],
                "Nationality": "", # 不明な場合が多い
                "Current_Team": row["Team"],
                "League": "MLR",
                "Scraped_Url": url,
                "Representative_Caps": ""
            })
            
    if new_players:
        df_new = pd.DataFrame(new_players)
        df_master = pd.concat([df_master, df_new], ignore_index=True)
        print(f"Added {len(new_players)} new MLR players.")
        
    # 保存 (v26として保存するか、上書きするか)
    # ユーザーの指示は「推論して統合」なので上書きまたは新バージョン
    output_path = "final_master_data_v26_mlr_integrated.csv"
    df_master.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Saved integrated data to {output_path}")

if __name__ == "__main__":
    merge_mlr()
