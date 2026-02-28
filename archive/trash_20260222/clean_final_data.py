import pandas as pd
import re

# ファイル名の設定
input_file = "final_master_data_v5_excel_ready.csv"
output_file = "final_master_data_v6_cleaned.csv"

def main():
    # 1. データ読み込み
    try:
        df = pd.read_csv(input_file)
        print(f"Loaded {input_file}")
    except FileNotFoundError:
        print(f"Error: {input_file} が見つかりません。")
        return

    # ---------------------------------------------------------
    # 2. ポジション名寄せ (No8への統一)
    # ---------------------------------------------------------
    def normalize_position(pos):
        if pd.isna(pos):
            return pos
        pos = str(pos).strip()
        
        # "NO8", "NO.8", "Number 8" などを "No8" に統一
        # 大文字小文字を無視して置換
        pos = re.sub(r'NO\.?8', 'No8', pos, flags=re.IGNORECASE)
        pos = re.sub(r'Number\s*8', 'No8', pos, flags=re.IGNORECASE)
        
        # 全角を半角に
        pos = pos.replace('ＮＯ８', 'No8').replace('Ｎｏ８', 'No8')
        return pos

    print("Normalizing Positions (No8)...")
    df['ポジション'] = df['ポジション'].apply(normalize_position)

    # ---------------------------------------------------------
    # 3. 高校名クリーニング
    # ---------------------------------------------------------
    def clean_high_school(name):
        if pd.isna(name) or name == "":
            return name
        name = str(name).strip()

        # A. 都道府県立・市立などの削除
        # 例: "県立浦和高校" -> "浦和高校", "市立船橋高校" -> "船橋高校"
        prefixes = [
            '県立', '都立', '府立', '道立', '市立', '町立', '村立', 
            '国立', '私立'
        ]
        for p in prefixes:
            if name.startswith(p):
                name = name[len(p):]
                break

        # B. カタカナ・英語名の末尾「高校」削除
        # 例: "エンデバースポーツ高校" -> "エンデバースポーツ"
        # 条件: 「高校」を除いた部分に「漢字」が含まれていなければ、カタカナ校とみなす
        if name.endswith("高校"):
            stem = name[:-2] # "高校" を取った名前
            
            # 漢字が含まれているかチェック (正規表現: 一文字でも漢字があればTrue)
            has_kanji = bool(re.search(r'[\u4e00-\u9faf]', stem))
            
            if not has_kanji:
                # 漢字がない（カタカナ、英語、数字のみ）なら "高校" を削除して返す
                return stem
        
        return name

    print("Cleaning High School names...")
    df['高校'] = df['高校'].apply(clean_high_school)

    # ---------------------------------------------------------
    # 4. 保存 (BOM付きUTF-8)
    # ---------------------------------------------------------
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"Done! Cleaned data saved to: {output_file}")

    # 確認用表示
    print("\n--- Check: Position No8 ---")
    print(df[df['ポジション'].astype(str).str.contains('No8', na=False)]['ポジション'].unique())
    
    print("\n--- Check: Katakana High Schools ---")
    # カタカナのみ（高校なし）になったものを一部表示
    kana_schools = df[~df['高校'].astype(str).str.contains('高校|大学|カレッジ', na=False) & df['高校'].notna()]
    print(kana_schools[['選手名', '高校']].head())

if __name__ == "__main__":
    main()