import pandas as pd

# 1. 出来上がったファイルを読み込む（文字化け対策で、エラーを無視して読み込む設定）
try:
    df = pd.read_csv("final_master_data_v5.csv", encoding="utf-8")
except:
    df = pd.read_csv("final_master_data_v5.csv", encoding="cp932") # 日本語Windows標準

# 2. 保存時に「BOM付きUTF-8」という形式にする
# これをすると、Excelでダブルクリックしても文字化けしなくなります
df.to_csv("final_master_data_v5_fixed.csv", index=False, encoding="utf-8-sig")

print("文字化けを修正した『final_master_data_v5.csv』を作成しました。")