import csv
import json
import os
import re
from datetime import datetime

# 設定
CSV_PATH = 'data_sources/final_master_data_v25_integrated.csv'
CONFIG_PATH = 'data/national_teams_config.json'
OUTPUT_PATH = 'data/national_players_map.json'
CURRENT_YEAR = 2026

def calculate_age(birth_date_str):
    if not birth_date_str or str(birth_date_str).lower() == 'nan': return None
    b_str = str(birth_date_str).strip()
    try:
        date_sep = '-' if '-' in b_str else '.'
        if len(b_str) == 4 and b_str.isdigit():
            return CURRENT_YEAR - int(b_str)
        
        if '..' in b_str:
            year_match = re.match(r'^(\d{4})', b_str)
            if year_match: return CURRENT_YEAR - int(year_match.group(1))
            
        birth_date = datetime.strptime(b_str[:10], f'%Y{date_sep}%m{date_sep}%d')
        today = datetime.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except (ValueError, Exception):
        match = re.match(r'^(\d{4})', b_str)
        if match: return CURRENT_YEAR - int(match.group(1))
        return None

def parse_numeric(val):
    if not val: return 0
    match = re.search(r'(\d+)', str(val))
    return int(match.group(1)) if match else 0

def parse_caps(caps_str):
    if not caps_str: return 0
    s_val = str(caps_str).strip()
    
    # 英語併用（例: Japan代表 (57 caps)）は異常データとして無視する二重ガード
    if 'caps' in s_val.lower() or 'Japan' in s_val:
        # ただし "日本代表(51)" のような正規形式は通したい
        if not re.search(r'[ぁ-んァ-ヶー一-龠]+代表', s_val):
            return 0

    match = re.search(r'\((\d+)\s*caps\)', s_val)
    if match: return int(match.group(1))
    match = re.search(r'(\d+)', s_val)
    return int(match.group(1)) if match else 0

def generate_slug(name_en, player_id, scraped_url=""):
    if scraped_url and 'all.rugby/player/' in scraped_url:
        url_id = scraped_url.split('/')[-1]
        if url_id: return url_id
    if not name_en: return f"player-{player_id}"
    slug = re.sub(r'[^a-z0-9]+', '-', str(name_en).lower()).strip('-')
    return f"{slug}-{player_id}"

def main():
    print(f"Loading config from {CONFIG_PATH}...")
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    country_to_id = {}
    for team in config:
        name_clean = team['name'].replace('代表', '')
        country_to_id[name_clean] = team['id']
        country_to_id[team['id']] = team['id']
        if 'en_name' in team:
            country_to_id[team['en_name']] = team['id']

    # 名寄せ強化
    mapping_extension = {
        "NZ": "new-zealand", "ニュージーランド": "new-zealand", "New Zealand": "new-zealand",
        "SA": "south-africa", "South Africa": "south-africa", "南アフリカ": "south-africa", "Springboks": "south-africa",
        "AUS": "australia", "Australia": "australia", "オーストラリア": "australia", "Wallabies": "australia",
        "ENG": "england", "England": "england", "イングランド": "england",
        "FRA": "france", "France": "france", "フランス": "france", "Française": "france",
        "IRE": "ireland", "Ireland": "ireland", "アイルランド": "ireland",
        "SCO": "scotland", "Scotland": "scotland", "スコットランド": "scotland",
        "WAL": "wales", "Wales": "wales", "ウェールズ": "wales",
        "ARG": "argentina", "Argentina": "argentina", "アルゼンチン": "argentina", "Pumas": "argentina",
        "FIJ": "fiji", "Fiji": "fiji", "フィジー": "fiji", "Fidjien": "fiji",
        "ITA": "italy", "Italy": "italy", "イタリア": "italy",
        "GEO": "georgia", "Georgia": "georgia", "ジョージア": "georgia",
        "SAM": "samoa", "Samoa": "samoa", "サモア": "samoa",
        "TON": "tonga", "Tonga": "tonga", "トンガ": "tonga",
        "NAM": "namibia", "Namibia": "namibia", "ナミビア": "namibia",
        "USA": "usa", "United States": "usa", "アメリカ": "usa",
        "CAN": "canada", "Canada": "canada", "カナダ": "canada",
        "URU": "uruguay", "Uruguay": "uruguay", "ウルグアイ": "uruguay",
        "CHI": "chile", "Chile": "chile", "チリ": "chile",
        "POR": "portugal", "Portugal": "portugal", "ポルトガル": "portugal", "Portugaise": "portugal",
        "ESP": "spain", "Spain": "spain", "スペイン": "spain", "Español": "spain",
        "HKG": "hong-kong", "Hong Kong": "hong-kong", "HongKong": "hong-kong", "香港": "hong-kong",
        "ROU": "romania", "Romania": "romania", "ルーマニア": "romania",
        "JPN": "japan", "Japan": "japan", "日本": "japan"
    }
    country_to_id.update(mapping_extension)

    # チーム名変換用データのロード
    TEAM_NAMES_PATH = 'data/team_names_jp.json'
    team_name_map = {}
    if os.path.exists(TEAM_NAMES_PATH):
        with open(TEAM_NAMES_PATH, 'r', encoding='utf-8') as f:
            team_name_data = json.load(f)
            # 検索しやすいようにフラットな辞書に変換 {English: JP}
            for league in team_name_data:
                for en_name, info in team_name_data[league].items():
                    team_name_map[en_name.lower()] = info['jp']
                    if 'aliases' in info:
                        for alias in info['aliases']:
                            team_name_map[alias.lower()] = info['jp']

    national_players = {team['id']: [] for team in config}
    processed_players = set()

    print(f"Reading CSV from {CSV_PATH}...")
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # 複数のフィールドから代表情報を探す
            caps_field = row.get('International_Caps') or row.get('代表キャップ数') or ""
            nationality_field = row.get('国籍') or row.get('nationality') or ""
            
            # 代表キャップ数がある場合は最優先
            target_id = None
            caps_raw = 0
            
            if caps_field and not caps_field.startswith('http'):
                country_match = re.search(r'^(.+?)(代表)?\s*\(', caps_field)
                country_raw = country_match.group(1).strip() if country_match else caps_field.replace('代表', '').strip()
                target_id = country_to_id.get(country_raw)
                caps_raw = parse_caps(caps_field)

            # キャップ数がない場合でも、国籍フィールドから代表ページ掲載候補を探す
            if not target_id and nationality_field:
                target_id = country_to_id.get(nationality_field.strip())

            if not target_id: continue

            name_ja = row.get('選手名_カタカナ') or row.get('選手名') or row.get('name_en')
            name_en = row.get('name_en')
            scraped_url = row.get('Scraped_Url')
            
            # デッド重複排除 (URL or 名前+誕生日)
            player_key = scraped_url if scraped_url else f"{name_en}-{row.get('生年月日')}"
            if player_key in processed_players: continue
            processed_players.add(player_key)
            
            # --- チーム名の和英併記化 ---
            raw_team = row.get('所属チーム', '')
            league_val = row.get('リーグ') or row.get('league', '')
            
            final_team_name = raw_team
            if league_val in ['urc', 'top14', 'premiership', 'super-rugby']:
                if ' / ' not in raw_team:
                    clean_team = re.sub(r'\（.*?\）', '', raw_team).strip()
                    jp_name = team_name_map.get(clean_team.lower())
                    if jp_name and jp_name != clean_team:
                        final_team_name = f"{clean_team} / {jp_name}"
                    elif "(" in raw_team and ")" in raw_team:
                        final_team_name = raw_team.replace('(', ' / ').replace(')', '')

            player_data = {
                "name_ja": name_ja,
                "name_en": name_en,
                "slug": generate_slug(name_en, i + 1, scraped_url),
                "position": row.get('ポジション', ''),
                "team": final_team_name,
                "league": league_val,
                "caps": caps_raw,
                "age": calculate_age(row.get('生年月日')),
                "height": parse_numeric(row.get('身長')),
                "weight": parse_numeric(row.get('体重')),
                "caps_display": caps_field if caps_raw > 0 else ""
            }
            
            national_players[target_id].append(player_data)

    for tid in national_players:
        # キャップ数順、次に年齢順でソート
        national_players[tid].sort(key=lambda x: (x['caps'], x['age'] or 0), reverse=True)
        print(f"Target {tid}: {len(national_players[tid])} players found.")

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(national_players, f, ensure_ascii=False, indent=2)
    
    print(f"Total {len(processed_players)} representative players processed.")
    print("Generation complete!")

if __name__ == "__main__":
    main()
