import pandas as pd

# 1. 読み込み（文字化けに強い設定）
try:
    df = pd.read_csv("final_master_data_v4.csv", encoding="utf-8")
except:
    df = pd.read_csv("final_master_data_v4.csv", encoding="cp932")

# 2. セミ・ラドラドラのキャップ数を 7 に修正
mask_semi = df['選手名'].str.contains('セミ ・ラドラドラ', na=False)
if mask_semi.any():
    df.loc[mask_semi, 'リーグワンキャップ数'] = 7
    print("Fixed Semi Radradra Caps to 7")

# 3. 学校名の名寄せ（御所 -> 御所実業高校 など）
school_map = {
    "御所": "御所実業高校", "御所実": "御所実業高校",
    "帝京": "帝京大学", "明治": "明治大学", "早稲田": "早稲田大学",
    "筑波": "筑波大学", "東海": "東海大学", "天理": "天理大学",
    "慶応": "慶應義塾大学", "慶應": "慶應義塾大学", "同志社": "同志社大学",
    "立命館": "立命館大学", "法政": "法政大学", "中央": "中央大学",
    "東福岡": "東福岡高校", "桐蔭学園": "桐蔭学園高校", "大阪桐蔭": "大阪桐蔭高校",
    "Endeavorsportshighschool": "エンデバースポーツ高校",
    "SaintJoseph’sCollegeHuntersHill": "セントジョセフ・カレッジ"
}

def normalize(val, is_high=True):
    if pd.isna(val) or val == "": return val
    val = str(val).strip()
    if val in school_map: return school_map[val]
    # 末尾に高校・大学がなければ付与（2文字以上の漢字の場合）
    if is_high and not any(s in val for s in ["高校", "カレッジ", "学校", "学院"]):
        return val + "高校"
    if not is_high and not any(s in val for s in ["大学", "カレッジ"]):
        return val + "大学"
    return val

df['高校'] = df['高校'].apply(lambda x: normalize(x, True))
df['大学'] = df['大学'].apply(lambda x: normalize(x, False))

# 4. エクセル専用形式 (BOM付きUTF-8) で保存
# これで保存すると、エクセルでダブルクリックしても文字化けしません
df.to_csv("final_master_data_v5_excel.csv", index=False, encoding="utf-8-sig")
print("Successfully saved to final_master_data_v5_excel.csv")
