import pandas as pd
import os
import re

CSV_PATH = '/Users/ktamatzmoto/Desktop/rugbypicks/data_sources/final_master_data_v25.csv'
CLEAN_CSV_PATH = '/Users/ktamatzmoto/Desktop/rugbypicks/data_sources/final_master_data_v25.csv'

# 主要な名前のマッピング
NAME_MAP = {
    'Aaron': 'アーロン', 'Adam': 'アダム', 'Andrew': 'アンドリュー', 'Ben': 'ベン',
    'Chris': 'クリス', 'Daniel': 'ダニエル', 'David': 'デイヴィッド', 'Gareth': 'ガレス',
    'Jack': 'ジャック', 'James': 'ジェームズ', 'John': 'ジョン', 'Josh': 'ジョシュ',
    'Luke': 'ルーク', 'Mark': 'マーク', 'Matthew': 'マシュー', 'Michael': 'マイケル',
    'Paul': 'ポール', 'Richard': 'リチャード', 'Robert': 'ロバート', 'Sam': 'サム',
    'Scott': 'スコット', 'Simon': 'サイモン', 'Thomas': 'トーマス', 'Tom': 'トム',
    'William': 'ウィリアム', 'Ryan': 'ライアン', 'Liam': 'リアム', 'Sean': 'ショーン',
    'Cian': 'キアン', 'Eoin': 'オーウェン', 'Conor': 'コナー', 'Darragh': 'ダラ',
    'Niall': 'ナイル', 'Finlay': 'フィンレイ', 'Zander': 'ザンダー', 'Hamish': 'ヘイミッシュ',
    'Finn': 'フィン', 'Darcy': 'ダーシー', 'Blair': 'ブレア', 'Grant': 'グラント',
    'Jamie': 'ジェイミー', 'Dave': 'デイヴ', 'Ross': 'ロス', 'Garry': 'ギャリー',
    'Peter': 'ピーター', 'Tadhg': 'タイグ', 'Bundee': 'バンディ', 'Mack': 'マック',
    'Hugo': 'ヒューゴ', 'Jamison': 'ジェイミソン', 'Gibson': 'ギブソン', 'Park': 'パーク',
    'Dan': 'ダン', 'Ronan': 'ロナン', 'Caelan': 'ケーラン', 'Doris': 'ドリス',
    'Josh': 'ジョシュ', 'Van': 'ヴァン', 'Der': 'デル', 'Flier': 'フライヤー',
    'Siya': 'シヤ', 'Kolisi': 'コリシ', 'Eben': 'エベン', 'Etzebeth': 'エツベス',
    'Damian': 'ダミアン', 'Willemse': 'ヴィレムセ', 'De': 'デ', 'Allende': 'アレンデ',
    'Lukhanyo': 'ルカニョ', 'Am': 'アム', 'Makazole': 'マカゾレ', 'Mapimpi': 'マピンピ',
    'Manie': 'マニー', 'Libbok': 'リボック', 'Handre': 'ハンドレ', 'Pollard': 'ポラード',
    'Jasper': 'ジャスパー', 'Wiese': 'ヴィーセ', 'Pieter-Steph': 'ピーターステフ', 'Du': 'デュ', 'Toit': 'トイ',
    'Steven': 'スティーブン', 'Kitshoff': 'キッツォフ', 'Malcolm': 'マルコム', 'Marx': 'マークス',
    'Ox': 'オクス', 'Nche': 'ンチェ', 'Bongi': 'ボンギ', 'Mbonambi': 'ンボナンビ',
    'Frans': 'フランス', 'Malherbe': 'マルハーバ', 'Franco': 'フランコ', 'Mostert': 'モスタート',
    'RG': 'RG', 'Snyman': 'スナイマン', 'Kwagga': 'クワッガ', 'Smith': 'スミス',
    'Marco': 'マルコ', 'Van': 'ファン', 'Staden': 'スターデン', 'Vincent': 'ヴィンセント', 'Koch': 'コッホ',
    'Willie': 'ウィリー', 'Le': 'ル', 'Roux': 'ルー', 'Jesse': 'ジェシー', 'Kriel': 'クリエル',
    'Cheslin': 'チェスリン', 'Kolbe': 'コルビ', 'Kurt-Lee': 'カートリー', 'Arendse': 'アレンゼ',
    'Grant': 'グラント', 'Williams': 'ウィリアムズ', 'Cobus': 'コーバス', 'Reinach': 'レイナック',
    'Faf': 'ファフ', 'Klerk': 'デクラーク',
}

def transliterate_name(english_name):
    if not english_name or pd.isna(english_name):
        return ""
    
    # 既にカタカナが含まれている場合はそのまま
    if re.search(r'[\u30A0-\u30FF]', str(english_name)):
        return str(english_name)
    
    tokens = re.findall(r'[A-Z\']+[a-z\']*', str(english_name))
    if not tokens:
        tokens = str(english_name).split()
        
    katakana_tokens = []
    for token in tokens:
        # 完全一致マッピング
        t_clean = token.capitalize()
        if t_clean in NAME_MAP:
            katakana_tokens.append(NAME_MAP[t_clean])
        else:
            # 簡易的な翻字ルール（ここでは必要最低限のみ。AIとしての知識で補完するのが理想だがスクリプト内では限界がある）
            # 代替案として、tokenのまま返すか、既知のパターンを適用
            katakana_tokens.append(token)
            
    return " ・ ".join(katakana_tokens)

def update_csv():
    print(f"Reading and cleaning {CSV_PATH}")
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    
    header = lines[0].strip()
    clean_lines = [lines[0]]
    for i in range(1, len(lines)):
        line = lines[i].strip()
        if not line or line == header or line.startswith('\ufeff英語名'):
            continue
        clean_lines.append(lines[i])
        
    with open('/tmp/final_master_v25_temp.csv', 'w', encoding='utf-8-sig') as f:
        f.writelines(clean_lines)
    
    df = pd.read_csv('/tmp/final_master_v25_temp.csv')
    
    # 欠落列の追加
    if '選手名_カタカナ' not in df.columns:
        df['選手名_カタカナ'] = ""
    if 'リーグ' not in df.columns:
        df['リーグ'] = ""

    urc_keywords = ['Glasgow', 'Connacht', 'Leinster', 'Munster', 'Ulster', 'Edinburgh', 
                    'Ospreys', 'Scarlets', 'Cardiff', 'Dragons', 'Stormers', 'Bulls', 
                    'Sharks', 'Lions', 'Benetton', 'Zebre', 'Hollywoodbets', 'Vodacom', 'DHL']

    def process_row(row):
        team = str(row.get('所属チーム', ''))
        is_urc = str(row.get('リーグ', '')).lower() == 'urc' or any(kw in team for kw in urc_keywords)
        
        if is_urc:
            row['リーグ'] = 'urc'
            # カタカナ名が英語のまま、または空の場合
            katakana = row.get('選手名_カタカナ', '')
            if pd.isna(katakana) or katakana == "" or katakana == row['英語名']:
                row['選手名_カタカナ'] = transliterate_name(row['英語名'])
            
            # 選手名もカタカナに統一（他と合わせる）
            row['選手名'] = row['選手名_カタカナ']
            
        return row

    df = df.apply(process_row, axis=1)
    
    # 保存
    df.to_csv(CLEAN_CSV_PATH, index=False, encoding='utf-8-sig')
    print(f"Updated CSV saved to {CLEAN_CSV_PATH}")

if __name__ == "__main__":
    update_csv()
