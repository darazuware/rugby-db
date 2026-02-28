
import json
import re

DB_PATH = 'data/unified_player_database_final.json'
OUTPUT_PATH = 'data/unified_player_database_final.json'

# Normalization Maps
SCHOOL_MAP = {
    # High Schools
    '佐野日大高校': '佐野日本大学高校',
    '国学院栃木': '國學院大學栃木高校',
    '国学院栃木高校': '國學院大學栃木高校',
    '國學院栃木高校': '國學院大學栃木高校',
    '國學院大學栃木高校': '國學院大學栃木高校',
    '大阪朝鮮高校': '大阪朝鮮中高級学校',
    '大阪朝鮮高級学校': '大阪朝鮮中高級学校',
    '大阪産業大学付属高校': '大阪産業大学附属高校',
    '東海大仰星高校': '東海大学付属大阪仰星高校',
    '東海大学付属仰星高校': '東海大学付属大阪仰星高校',
    '東海大大阪仰星高校': '東海大学付属大阪仰星高校',
    '東海大学付属大阪仰星高校': '東海大学付属大阪仰星高校',
    '東海大相模高校': '東海大学付属相模高校',
    '東海大相模原高校': '東海大学付属相模高校',
    '流経大柏高校': '流通経済大学付属柏高校',
    '流経大柏高高校': '流通経済大学付属柏高校',
    '流通経済大学附属柏高校': '流通経済大学付属柏高校',
    '流通経済大柏高校': '流通経済大学付属柏高校',
    '茗渓学園高校': '茗溪学園高校',
    '近大付属高校': '近畿大学附属高校',
    '鹿児島工高校': '鹿児島工業高校',
    '黒沢尻工高校': '黒沢尻工業高校',
    '秋田工高校': '秋田工業高校',
    '名護商工業高校': '名護商工高校',
    '日体大柏高校': '日本体育大学柏高校',
    '関東学院六浦高校': '関東学院六浦高校',
    '関東学院大学六浦高校': '関東学院六浦高校',
    '天理大学高校': '天理高校', # Assumption
    '帝京大学高校': '帝京大学高校', # Keep distinctive
    '帝京高校': '帝京高校',
    '早稲田実業高校': '早稲田実業学校高等部',
    '早稲田実業学校': '早稲田実業学校高等部',
    '國學院大學久我山高校': '國學院大學久我山高校',
    '國學院久我山高校': '國學院大學久我山高校',
    '国学院久我山高校': '國學院大學久我山高校',
    '大阪桐蔭高校': '大阪桐蔭高校',
    '桐蔭学園高校': '桐蔭学園高校',
    '茗溪学園高校': '茗溪学園高校',
    '茗渓学園高校': '茗溪学園高校',
    '佐野日本大学高校': '佐野日本大学高校',
    '佐野日大高校': '佐野日本大学高校',
    '京都成章高校': '京都成章高校',
    '京都工学院高校': '京都工学院高校', # Keep distinct from Fushimi for now? Or merge?
    '伏見工業高校': '伏見工業高校',
    
    # Universities
    '流経大学': '流通経済大学',
    '関東学院大大学': '関東学院大学',
    '國學院大大学': '國學院大學',
    '國學院大学': '國學院大學',
    '国学院大学': '國學院大學',
    '同志社大大学': '同志社大学',
    '関西学院大大学': '関西学院大学',
    'オタゴ大大学': 'オタゴ大学',
    'ジョンマクガラシャン大大学': 'ジョンマクガラシャンカレッジ',
    '大東大': '大東文化大学',
    '日体大': '日本体育大学',
    '慶応義塾大学': '慶應義塾大学',
    '慶應大学': '慶應義塾大学',
    '帝京大': '帝京大学',
    '明治大': '明治大学',
    '早稲田大': '早稲田大学',
}

def normalize_school(name):
    if not name: return name
    name = str(name).strip()
    return SCHOOL_MAP.get(name, name)

def fix_career_history(history):
    if isinstance(history, str):
        if ' -> ' in history:
            return history # It's our valid format
        try:
            # Try to parse if it looks like JSON
            if history.startswith('['):
                return json.loads(history.replace("'", '"').replace('None', 'null'))
            return [] 
        except:
            return []
    return history

def main():
    print("--- Starting Data Normalization ---")
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("DB not found")
        return

    # Handle list vs dict
    is_list = isinstance(data, list)
    players = data if is_list else data.values()

    count = 0
    for p in players:
        # Normalize Schools
        hs = p.get('high_school')
        univ = p.get('university')
        
        new_hs = normalize_school(hs)
        new_univ = normalize_school(univ)
        
        if new_hs != hs:
            p['high_school'] = new_hs
            count += 1
        if new_univ != univ:
            p['university'] = new_univ
            count += 1

        # Fix Career History
        ch = p.get('career_history')
        if isinstance(ch, str):
            p['career_history'] = fix_career_history(ch)
            count += 1

    # Save
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Normalization complete. Updated {count} fields.")

if __name__ == "__main__":
    main()
