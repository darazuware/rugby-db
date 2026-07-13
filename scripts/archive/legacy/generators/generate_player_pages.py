import json
import os
import re
import hashlib
from player_utils import slugify, clean_team_name, load_unified_players, get_player_score, get_team_slug, get_league_slug_for_team, get_canonical_school_name, get_enrolment_year, get_school_slug



# League Mapping
with open('data/rugby_leagues.json', 'r', encoding='utf-8') as f:
    LEAGUES_DATA = json.load(f)

LEAGUE_NAME_TO_SLUG = {}
for l in LEAGUES_DATA:
    slug = l['url'].split('/')[-1]
    LEAGUE_NAME_TO_SLUG[l['name']] = slug
    LEAGUE_NAME_TO_SLUG[l['name_ja']] = slug
    # Standardized normalized keys
    LEAGUE_NAME_TO_SLUG[re.sub(r'[\s\-_]', '', l['name']).lower()] = slug
    LEAGUE_NAME_TO_SLUG[re.sub(r'[\s\-_]', '', l['name_ja']).lower()] = slug

def get_league_info(p):
    t_name = clean_team_name(p.get('team', ''))
    t_en = p.get('team_en', '')
    slug = get_league_slug_for_team(t_name, t_en)
    
    # Fallback to source/league field
    if not slug:
        l_raw = p.get('league') or p.get('source', 'Unknown')
        l_norm = re.sub(r'[\s\-_]', '', str(l_raw)).lower()
        slug = LEAGUE_NAME_TO_SLUG.get(l_raw, LEAGUE_NAME_TO_SLUG.get(l_norm, 'unknown'))
    else:
        l_raw = p.get('league') or p.get('source', 'Unknown')
    
    # Get original names from data
    l_ja, l_en = l_raw, l_raw
    for l in LEAGUES_DATA:
        if l['url'].endswith(slug):
            l_ja, l_en = l['name_ja'], l['name']
            break
            
    return slug, l_ja, l_en

# Load de-duplicated players from shared utility
print("Loading data via player_utils...")
players = load_unified_players()

# Load team details for Division lookup (though primarily for links here)
try:
    with open('data/league_one_teams_detailed.json', 'r', encoding='utf-8') as f:
        teams_detailed = json.load(f)
except:
    teams_detailed = []

# Create output directory
os.makedirs('dist/player', exist_ok=True)
# --- Dictionaries & Helpers ---

NATIONALITY_JA = {
    'Japan': '日本', 'New Zealand': 'ニュージーランド', 'Australia': 'オーストラリア',
    'South Africa': '南アフリカ', 'Fiji': 'フィジー', 'Tonga': 'トンガ', 'Samoa': 'サモア',
    'England': 'イングランド', 'Scotland': 'スコットランド', 'Wales': 'ウェールズ',
    'Ireland': 'アイルランド', 'France': 'フランス', 'Argentina': 'アルゼンチン',
    'USA': 'アメリカ', 'Canada': 'カナダ', 'Namibia': 'ナミビア', 'Uruguay': 'ウルグアイ',
    'Korea': '韓国', 'Italy': 'イタリア', 'Georgia': 'ジョージア'
}

# Additional Overseas Mapping for Links

# Load Top 14 teams for EN mapping
try:
    with open('data/top14_teams.json', 'r', encoding='utf-8') as f:
        TOP14_DATA = json.load(f)
    TEAM_EN_MAP = {t['name_ja']: t['name'] for t in TOP14_DATA}
except Exception as e:
    # print(f"ERROR: Failed to load top14_teams.json: {e}")
    TEAM_EN_MAP = {}

def get_team_en_name(ja_name, current_raw=''):
    # If the raw name contains Roman characters, use it as the source of English name
    if current_raw and re.search(r'[a-zA-Z]', str(current_raw)):
        clean_raw = re.sub(r'[（(]\d{4}.*?[）)]', '', str(current_raw)).strip()
        if re.search(r'[a-zA-Z]', clean_raw):
            return clean_raw
    # Otherwise look up in JA -> EN map
    return TEAM_EN_MAP.get(ja_name, '')

TEAM_TRANSLATIONS = {
    'Sunwolves': 'サンウルブズ',
    'Sanix Blues': '宗像サニックスブルース',
    'Urayasu D-Rocks': '浦安D-Rocks',
    'Red Hurricanes Osaka': 'レッドハリケーンズ大阪',
    'NTT Docomo Red Hurricanes': 'NTTドコモレッドハリケーンズ',
    'NTT Docomo Red Hurricanes Osaka': 'NTTドコモレッドハリケーンズ大阪',
    'Shizuoka Blue Revs': '静岡ブルーレヴズ',
    'Yamaha Jubilo': 'ヤマハ発動機ジュビロ',
    'Toyota Verblitz': 'トヨタヴェルブリッツ',
    'Toyota Jidosha Verblitz': 'トヨタ自動車ヴェルブリッツ',
    'Tokyo Sungoliath': '東京サンゴリアス',
    'Suntory Sungoliath': 'サントリーサンゴリアス',
    'Toshiba Brave Lupus Tokyo': '東芝ブレイブルーパス東京',
    'Toshiba Brave Lupus': '東芝ブレイブルーパス',
    'Saitama Wild Knights': '埼玉ワイルドナイツ',
    'Panasonic Wild Knights': 'パナソニックワイルドナイツ',
    'Kubota Spears Funabashi Tokyo-Bay': 'クボタスピアーズ船橋・東京ベイ',
    'Kubota Spears': 'クボタスピアーズ',
    'Kobelco Kobe Steelers': 'コベルコ神戸スティーラーズ',
    'Kobelco Steelers': '神戸製鋼コベルコスティーラーズ',
    'Yokohama Canon Eagles': '横浜キヤノンイーグルス',
    'Canon Eagles': 'キヤノンイーグルス',
    'BlackRams Tokyo': 'リコーブラックラムズ東京',
    'Ricoh Black Rams': 'リコーブラックラムズ',
    'Green Rockets Tokatsu': 'NECグリーンロケッツ東葛',
    'NEC Green Rockets': 'NECグリーンロケッツ',
    'Hanazono Kintetsu Liners': '花園近鉄ライナーズ',
    'Kintetsu Liners': '近鉄ライナーズ',
    'Mie Honda Heat': '三重ホンダヒート',
    'Honda Heat': 'ホンダヒート',
    'Kyushu Kyuden Voltex': '九州電力キューデンヴォルテクス',
    'Kyuden Voltex': 'キューデンヴォルテクス',
    'Toyota Industries Shuttles Aichi': '豊田自動織機シャトルズ愛知',
    'Toyota Industries Shuttles': '豊田自動織機シャトルズ',
    'Shimizu Corporation Blue Sharks': '清水建設江東ブルーシャークス',
    'Shimizu Blue Sharks': '清水建設ブルーシャークス',
    'Hino Red Dolphins': '日野レッドドルフィンズ',
    'Kamaishi Seawaves': '日本製鉄釜石シーウェイブス',
    'Kurita Water Gush Akishima': 'クリタウォーターガッシュ昭島',
    'Kurita Water Gush': 'クリタウォーターガッシュ',
    'Yakult Levins Toda': 'ヤクルトレビンズ戸田',
    'Yakult Levins': 'ヤクルトレビンズ',
    'LeRIRO Fukuoka': 'ルリーロ福岡',
    'Secom Rugguts': '狭山セコムラガッツ',
    'Chugoku Electric Power Red Regulions': '中国電力レッドレグリオンズ',
    'Mazda Skyactivs Hiroshima': 'マツダスカイアクティブズ広島',
    'Mazda Blue Zoomers': 'マツダブルーズーマーズ',
    # Super Rugby / NPD
    'Canterbury': 'カンタベリー',
    'Crusaders': 'クルセイダーズ',
    'Hurricanes': 'ハリケーンズ',
    'Blues': 'ブルーズ',
    'Chiefs': 'チーフス',
    'Highlanders': 'ハイランダーズ',
    'Brumbies': 'ブランビーズ',
    'Queensland Reds': 'レッズ',
    'Reds': 'レッズ',
    'NSW Waratahs': 'ワラターズ',
    'Waratahs': 'ワラターズ',
    'Melbourne Rebels': 'レベルズ',
    'Rebels': 'レベルズ',
    'Western Force': 'フォース',
    'Force': 'フォース',
    'Moana Pasifika': 'モアナ・パシフィカ',
    'Fijian Drua': 'フィジアン・ドゥルア',
    'Drua': 'フィジアン・ドゥルア',
    'Sunwolves': 'サンウルブズ',
    'Mitsubishi Sagamihara Dynaboars': '三菱重工相模原ダイナボアーズ',
    'Kyushu Electric Kyuden Voltex': '九州電力キューデンヴォルテクス',
    'Kyūshu キューデンヴォルテクス': '九州電力キューデンヴォルテクス',
    'Kyushu Kyuden Voltex': '九州電力キューデンヴォルテクス',
    'Mie Honda Heat': '三重ホンダヒート',
    'Mie Honda Heat RFC': '三重ホンダヒート',
    'Yakult Levins': 'ヤクルトレビンズ戸田',
    'Yakult Levins Toda': 'ヤクルトレビンズ戸田',
    'Kurita Water Gush': 'クリタウォーターガッシュ昭島',
    'Kurita Water Gush Akishima': 'クリタウォーターガッシュ昭島',
    'Yagult Levins': 'ヤクルトレビンズ戸田', # Typo catch
    'Secom Rugguts': '狭山セコムラガッツ',
    'LeRIRO Fukuoka': 'ルリーロ福岡',
    'LeRIRO Fukuoka': 'ルリーロ福岡',
    'Coca Cola West Red Sparks': 'コカ・コーラウエストレッドスパークス',
    # Top 14 / French
    'Stade Rochelais': 'ラ・ロシェル',
    'Stade Toulousain': 'トゥールーズ',
    'Union Bordeaux Bègles': 'ボルドー・ベグル',
    'Stade Français': 'スタッド・フランセ',
    'Rugby Club Toulonnais': 'トゥーロン',
    'Racing 92': 'ラシン92',
    'Lyon OU': 'リヨン',
    'Castres Olympique': 'カストル',
    'Section Paloise': 'ポー',
    'Pau Béarn Pyrénées': 'ポー',
    'Pau': 'ポー',
    'USA Perpignan': 'ペルピニャン',
    'Aviron Bayonnais': 'バイヨンヌ',
    'ASM Clermont Auvergne': 'クレルモン',
    'ASM Clermont': 'クレルモン',
    'Clermont Auvergne': 'クレルモン',
    'Montpellier Hérault Rugby': 'モンペリエ',
    'RC Vannes': 'ヴァンヌ',
    'Stade Bordelais': 'スタッド・ボルドライ',
    'Clermont': 'クレルモン',
    'Toulon': 'トゥーロン',
    'Toulouse': 'トゥールーズ',
    'La Rochelle': 'ラ・ロシェル',
    'Union Bordeaux Bègles': 'ボルドー・ベグル',
    'Union Bordeaux-Bègles': 'ボルドー・ベグル',
    'Bordeaux': 'ボルドー・ベグル',
    'Stade Français Paris': 'スタッド・フランセ',
    'Stormers': 'ストーマーズ',
    'The Sharks': 'シャークス',
    'Sharks': 'シャークス',
    'Bulls': 'ブルズ',
}


def translate_nationality(nat_str):
    if not nat_str or nat_str == '-': return '-'
    # Handle multiple nationalities "New Zealand / Japan"
    parts = str(nat_str).split('/')
    translated_parts = []
    for p in parts:
        p = p.strip()
        translated_parts.append(NATIONALITY_JA.get(p, p)) # Default to original if not found
    return ' / '.join(translated_parts)

def translate_team_name(text):
    if not isinstance(text, str): return text
    # Clean up common suffixes
    clean_text = re.sub(r'\(.*?\)', '', text)
    clean_text = clean_text.replace('Béarn Pyrénées', '').replace('Auvergne', '').strip()
    
    # Sort translations by length
    for eng, jap in sorted(TEAM_TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True):
        if eng in clean_text or eng in text:
            # If the text already has the Japanese translation partially (e.g. from previous runs), avoid duplication
            if jap in text and eng in text:
                return text.replace(eng, '').strip() # Remove English version if Japanese is already there
            return jap
            
    return clean_text if clean_text else text

def consolidate_career_history(career_string):
    """Consolidate interleaved career history entries."""
    if not career_string or career_string == '-': return []
    
    if isinstance(career_string, list):
        parts = []
        for x in career_string:
            if isinstance(x, str): parts.append(x)
            elif isinstance(x, dict): 
                # If already a dict, convert back to string for standard processing or handle directly
                parts.append(f"{x.get('team')} ({x.get('start')}-{x.get('end') if x.get('end')!=9999 else ''})")
    else:
        parts = career_string.split(' -> ')
        
    raw_entries = []
    # Improved regex for (2020), (2020-2022), (2020-), (2020-22)
    # Group 1: Start Year, Group 2: End Year (4 or 2 digits)
    year_re = r'\(\s*(\d{4})\s*[\-–‐—]?\s*(\d{4}|\d{2})?\s*\)'
    
    for part in parts:
        part = part.strip()
        year_match = re.search(year_re, part)
        if year_match:
            team_name = part[:year_match.start()].strip()
            start_year = int(year_match.group(1))
            end_year_raw = year_match.group(2)
            
            if end_year_raw:
                if len(end_year_raw) == 2:
                    end_year = 2000 + int(end_year_raw)
                else:
                    end_year = int(end_year_raw)
            else:
                # If matches (YYYY-) or (YYYY - ), it's 9999
                if any(h in part[year_match.start():] for h in ['-', '–', '‐', '—']):
                    end_year = 9999
                else:
                    end_year = start_year
            
            raw_entries.append({'team': team_name, 'start': start_year, 'end': end_year})
        else:
            raw_entries.append({'team': part, 'start': 0, 'end': 0})
            
    # Merge logic
    merged_map = {}
    for entry in raw_entries:
        t = entry['team']
        # Translate team name HERE to key by Japanese name
        t_ja = translate_team_name(t)
        
        if t_ja not in merged_map:
            merged_map[t_ja] = {'start': entry['start'], 'end': entry['end']}
        else:
            if entry['start'] < merged_map[t_ja]['start'] and entry['start'] != 0:
                merged_map[t_ja]['start'] = entry['start']
            if entry['end'] > merged_map[t_ja]['end']:
                merged_map[t_ja]['end'] = entry['end']
                
    final_list = []
    for team, span in merged_map.items():
        final_list.append({'team': team, 'start': span['start'], 'end': span['end']})
        
    final_list.sort(key=lambda x: x['start'])
    return final_list

# CSS Definition (Standard String)
CSS_STYLES = """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Noto Sans JP', sans-serif;
            background-color: #f5f7f9;
            color: #484848;
            font-size: 16px;
            line-height: 1.6;
        }
        a { color: #0097B2; text-decoration: none; }
        a:hover { text-decoration: underline; }
        
        .header-container {
            background-color: #0097B2;
            padding: 15px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        .site-title {
            color: #ffffff;
            font-size: 24px;
            font-weight: 700;
        }
        .nav-container {
            background-color: #0097B2;
            border-top: 1px solid rgba(255,255,255,0.2);
        }
        .nav-menu {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            gap: 30px;
            list-style: none;
        }
        .nav-menu a {
            color: #ffffff;
            font-size: 14px;
            padding: 12px 0;
            display: block;
        }
        
        .container {
            max-width: 1000px;
            margin: 40px auto;
            padding: 0 20px;
        }
        
        /* Player Header */
        .player-header {
            background: linear-gradient(135deg, #0097B2 0%, #00b8d4 100%);
            color: #ffffff;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            position: relative;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .player-name {
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .player-name-en {
            font-size: 20px;
            opacity: 0.9;
            margin-bottom: 0px;
            font-weight: 500;
        }
        .header-team-link {
            position: absolute;
            bottom: 20px;
            right: 20px;
            background-color: rgba(255,255,255,0.95);
            padding: 10px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            color: #0097B2;
            font-weight: 700;
            font-size: 18px;
        }
        .current-team-label {
            font-size: 10px;
            color: #666;
            text-transform: uppercase;
            display: block;
            margin-bottom: 2px;
        }

        .header-position {
            font-size: 18px;
            font-weight: 700;
            background: rgba(255,255,255,0.2);
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            margin-top: 10px;
            color: #ffffff;
            text-decoration: none;
            transition: background 0.2s;
        }
        .header-position:hover {
            background: rgba(255,255,255,0.3);
            text-decoration: underline;
        }
        
        /* Info Grid */
        .info-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 40px;
            background: #fff;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .info-item {
            margin-bottom: 10px;
            padding: 8px;
            border-radius: 4px;
            transition: background-color 0.2s;
        }
        .info-item:hover {
            background-color: #f0f4f8;
        }
        .info-label {
            font-size: 12px;
            color: #888;
            margin-bottom: 4px;
        }
        .info-value {
            font-size: 18px;
            font-weight: 700;
            color: #333;
        }
        .bio-link {
            color: #0097B2;
            border-bottom: 1px dotted #0097B2;
            text-decoration: none;
        }
        .bio-link:hover {
            background-color: #e6f7f9;
        }
        
        /* Flexible school names */
        .school-name {
            word-break: break-word;
            line-height: 1.3;
        }

        .section-title {
            font-size: 24px;
            font-weight: 700;
            color: #333;
            margin: 40px 0 20px;
            border-bottom: 2px solid #0097B2;
            padding-bottom: 10px;
        }
        
        /* Career List */
        .career-row {
            padding: 12px 15px;
            background: #f8f9fa;
            border-radius: 6px;
            margin-bottom: 10px;
            display: flex;
            justify-content: flex-start;
            gap: 15px;
            align-items: center;
        }
        .career-link-item {
            font-weight: 700;
            color: #333;
            text-decoration: none;
        }
        .career-link-item:hover {
            text-decoration: underline;
            color: #0097B2;
        }
        .career-date {
            color: #666;
            font-size: 14px;
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }
        .stat-box {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 28px;
            font-weight: 700;
            color: #0097B2;
        }
        .stat-label {
            font-size: 14px;
            color: #666;
        }
        
        @media (max-width: 768px) {
            .info-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .header-team-link {
                position: static;
                margin-top: 20px;
                display: inline-block;
                width: 100%;
                text-align: center;
            }
        }
"""

# Load team metadata
try:
    with open('teams_enriched.json', 'r', encoding='utf-8') as f:
        team_metadata = json.load(f)
except:
    team_metadata = {}

# Helper to look up team data by name (fuzzy match)
def get_team_data(team_name):
    # team_name is English or Japanese. keys in team_metadata are Japanese.
    # Try direct match
    if team_name in team_metadata:
        return team_metadata[team_name]
    
    # Try translation
    name_ja = translate_team_name(team_name)
    if name_ja in team_metadata:
        return team_metadata[name_ja]
        
    return None

# Valid League One Teams & Division Mapping (for linking)
VALID_LEAGUE_ONE_TEAMS = set()
TEAM_DIV_MAP = {} # team_name (JA) -> div_slug

for t in teams_detailed:
    t_name = t['team_name']
    VALID_LEAGUE_ONE_TEAMS.add(t_name)
    div = t.get('division', '')
    div_slug = "leagueone-div1"
    if "Division 2" in div: div_slug = "leagueone-div2"
    elif "Division 3" in div: div_slug = "leagueone-div3"
    TEAM_DIV_MAP[t_name] = div_slug

# Reverse map for English names -> Div Slug via Translation
# (Ideally we translate FIRST then look up)

POSITION_MAP = {
    'プロップ': 'PR', 'フッカー': 'HO', 'セカンドロー': 'LO', 'フランカー': 'FL',
    'ナンバーエイト': 'No8', 'スクラムハーフ': 'SH', 'フライハーフ': 'SO',
    'センター': 'CTB', 'ウィング': 'WTB', 'フルバック': 'FB',
    'バックロー': 'FL', 'Prop': 'PR', 'Hooker': 'HO', 'Second Row': 'LO',
    'Flanker': 'FL', 'Number 8': 'No8', 'Scrum-half': 'SH', 'Fly-half': 'SO',
    'Center': 'CTB', 'Wing': 'WTB', 'Fullback': 'FB',
    '右プロップ': 'PR', '左プロップ': 'PR', '右PR': 'PR', '左PR': 'PR'
}

def normalize_position(pos):
    if not pos or pos == '-' or str(pos) == 'nan': return '-'
    # Normalize space and extract text
    clean_pos = str(pos).strip().replace('　', ' ') # Handle full-width space
    if clean_pos in POSITION_MAP:
        return POSITION_MAP[clean_pos]
    
    # Try partial match or word-by-word
    for k, v in POSITION_MAP.items():
        if k in clean_pos:
            return v
            
    return clean_pos

def generate_player_page(player):
    # --- RICH CHECK ---
    score = get_player_score(player)
    
    # Extract Birth Year for later
    birthdate = str(player.get('birthdate', '')).strip()
    birth_year = ''
    if birthdate and birthdate != 'nan':
        match = re.search(r'(\d{4})', birthdate)
        if match: birth_year = match.group(1)

    if score < 2: return None

    player_id = player.get('id', 'unknown')
    name_ja = player.get('name_ja') or player.get('name_en', '不明')
    name_en = player.get('name_en', 'Unknown')
    slug = f"{slugify(name_en)}_{player_id}"
    
    # --- Data Processing ---
    # Age calculation
    age_val = player.get('age')
    if (not age_val or age_val == '不明') and birth_year:
        try:
            age_val = 2025 - int(birth_year)
        except:
            pass
    age_display = f"{age_val}歳" if age_val and age_val != '不明' else '不明'
    
    # 2. Height/Weight
    height = player.get('height', '-')
    weight = player.get('weight', '-')
    
    # 3. Position (Normalized)
    pos = normalize_position(player.get('position', '-'))
    
    # 4. Schools (With Links)
    high_school = str(player.get('high_school', '-'))
    if high_school.lower() == 'nan': high_school = '-'
    hs_link = f'<a href="../../schools/index.html?s={high_school}">{high_school}</a>' if high_school != '-' else '-'
    
    university = str(player.get('university', '-'))
    if university.lower() == 'nan': university = '-'
    univ_link = f'<a href="../../schools/index.html?s={university}">{university}</a>' if university != '-' else '-'
    
    # 5. Stats
    stats = player.get('all_rugby_stats', {})
    l1_caps = player.get('league_one_caps', '-')
    matches_stat = str(stats.get('matches_played', l1_caps))
    tries = stats.get('tries', '-')
    points = stats.get('points', '-')

    # 6. Current Team & Design
    current_team = player.get('team', '不明')
    current_team_clean = re.sub(r'[（(]\d{4}.*?[）)]', '', str(current_team)).strip()
    
    t_name_ja_lookup = translate_team_name(current_team_clean)
    div_slug = TEAM_DIV_MAP.get(t_name_ja_lookup, 'leagueone-div1')
    team_slug_dir = get_team_slug(current_team_clean)
    
    team_data = get_team_data(current_team_clean)
    team_color = team_data.get('color', '#0097B2') if team_data else '#0097B2'
    team_logo_url = team_data.get('logo') if team_data else None
    
    # 7. Nationality
    nat1 = player.get('nationality_1')
    nat2 = player.get('nationality_2')
    
    # Validation/Heuristics
    # If missing, manual fix (e.g. Shigematsu)
    if not nat1 and name_ja == '繁松 哲大': nat1 = 'Japan'
    
    # Fallback: If no nationality but has Japan Rep Caps, assume Japan (or at least capped)
    rep_caps_val = player.get('representative_caps')
    if not nat1 and rep_caps_val and '日本代表' in str(rep_caps_val):
        nat1 = 'Japan'
    
    nat_disp_ja = translate_nationality(nat1)
    if nat2: nat_disp_ja += f" / {translate_nationality(nat2)}"

    # 8. Category
    # New Field
    category_val = player.get('category', '-')
    
    # 9. Socials & Image
    socials = player.get('socials', {})
    image_url = player.get('image_url')

    # --- PERMANENT FLAT URL GENERATION (SEO) ---
    BASE_DIR = 'dist/player'
    os.makedirs(BASE_DIR, exist_ok=True)
    filename = os.path.join(BASE_DIR, f"{slug}.html")
    rel_root = "../"
    
    # Still determine league/division for content/breading
    source = player.get('source', '')
    league = player.get('league', '')

    # Shared Career History Generation (Pre-sorted)
    career_list = consolidate_career_history(player.get('career_history'))
    if not career_list: career_list = []
    if current_team_clean and current_team_clean != '不明' and current_team_clean != '-':
        found = False
        if career_list:
             last = career_list[-1]
             c_norm = translate_team_name(current_team_clean)
             l_norm = translate_team_name(last['team'])
             if c_norm == l_norm:
                 found = True
                 last['end'] = 9999
        if not found:
            # Re-enable parsing start year from raw team name if present
            # If (2024-26) exists, we want 2024.
            current_team_raw = player.get('team', '')
            match = re.search(r'[（(]([0-9]{4})', str(current_team_raw))
            start_year = int(match.group(1)) if match else 9999
            career_list.append({'team': current_team_clean, 'start': start_year, 'end': 9999})
    
    filtered_career = [i for i in career_list if i['team'] not in [high_school, university] and not any(k in i['team'] for k in ['University','College','大学','高校','School'])]
    filtered_career.sort(key=lambda x: x['start'])

    # Dynamic CSS
    team_css = f"""
        .header-container {{ background-color: {team_color}; }}
        .nav-container {{ background-color: {team_color}; }}
        .player-header {{ background: linear-gradient(135deg, {team_color} 0%, {team_color}bb 100%); }}
        .section-title {{ border-bottom: 2px solid {team_color}; }}
        .bio-link {{ color: {team_color}; border-bottom: 1px dotted {team_color}; }}
        . career-link-item a:hover {{ color: {team_color}; }}
        .stat-value {{ color: {team_color}; }}
    """

    # Helper: Generate HTML with specific Depth
    def get_html(rel_root):
        logo_img_local = f'<img src="{rel_root}images/logo.png" alt="RugbyPick" style="height:40px; vertical-align:middle;">'
        
        def make_link_local(text, folder="misc", suffix=""):
            if not text or text == '-': return text
            s = slugify(text)
            return f'<a href="{rel_root}{folder}/{s}.html" class="bio-link">{text}{suffix}</a>'

        def make_school_link(text):
            if not text or str(text).lower() in ['-', 'none', 'nan', '不明']: return '-'
            s = get_school_slug(text)
            if not s: return text
            return f'<a href="{rel_root}schools/{s}.html" class="bio-link">{text}</a>'

        def format_birth_date(bdate):
            if not bdate or bdate == '-': return '-'
            # Handle //2005 case
            clean_b = str(bdate).strip('/')
            if len(clean_b) == 4 and clean_b.isdigit():
                return "" # Just show birth_year link alone if no month/day
            # Normalize for display
            norm = bdate.replace('年', '.').replace('月', '.').replace('日', '.')
            parts = [p for p in norm.split('.') if p]
            return f"{parts[1]}.{parts[2]}" if len(parts) >= 3 else clean_b

        pos_norm = normalize_position(pos)
        birth_html_local = (make_link_local(birth_year, "dates", "年") if birth_year else "") + f" {format_birth_date(birthdate)}"
        age_html_local = make_link_local(age_display, "age")
        height_html_local = make_link_local(height, "height", "cm")
        pos_html_local = make_link_local(pos, "positions")
        hs_html_local = make_school_link(high_school)
        univ_html_local = make_school_link(university)
        
        formatted_career_local = []
        for item in filtered_career:
            start, end, t_name = item['start'], item['end'], item['team']
            if start == 9999 and end == 9999:
                date_str = "(現在)"
            elif start != 9999 and end == 9999:
                date_str = f"({start} - )"
            elif start != 0 and start != 9999 and end != 9999:
                date_str = f"({start} - {end})"
            else:
                date_str = ""
                
            t_name_ja = translate_team_name(t_name)
            t_name_en_career = get_team_en_name(t_name_ja, t_name)
            
            # Bilingual display for career
            t_disp_career = t_name_ja
            if t_name_en_career and t_name_en_career != t_name_ja:
                t_disp_career += f' <span style="font-size: 0.8em; opacity: 0.7;">({t_name_en_career})</span>'
            
            # Master Structure: /teams/{league}/{team}/index.html
            target_league_dir = get_league_slug_for_team(t_name_ja, t_name)
            target_team_slug = get_team_slug(t_name)
            
            if target_league_dir and target_team_slug:
                t_link = f"{rel_root}teams/{target_league_dir}/{target_team_slug}/index.html"
                formatted_career_local.append(f'<div class="career-row"><a href="{t_link}" class="career-link-item">{t_disp_career}</a> <span class="career-date">{date_str}</span></div>')
            else:
                formatted_career_local.append(f'<div class="career-row"><span class="career-link-item" style="color: {team_color};">{t_disp_career}</span> <span class="career-date">{date_str}</span></div>')
        
        rep_caps_html_local = f"<div class='info-value'>{rep_caps_val}</div>" if rep_caps_val and str(rep_caps_val) != 'nan' else "<div class='info-value'>-</div>"
        
        # Breadcrumbs
        nav_prefix = f"{rel_root}pages/"
        breadcrumbs = f'<a href="{rel_root}index.html">ホーム</a> &gt; '
        breadcrumbs += f'<a href="{nav_prefix}leagues.html">リーグ一覧</a> &gt; '
        
        target_league_slug, l_name_ja, l_name_en = get_league_info(player)
        
        team_dir_slug = get_team_slug(current_team_clean)
        t_link = f"{rel_root}teams/{target_league_slug}/{team_dir_slug}/index.html"
        
        if target_league_slug == 'unknown':
            breadcrumbs += f'{l_name_ja} <span style="font-size: 0.8em; opacity: 0.7;">({l_name_en})</span> &gt; '
        else:
            breadcrumbs += f'<a href="{rel_root}leagues/{target_league_slug}/index.html">{l_name_ja} <span style="font-size: 0.8em; opacity: 0.7;">({l_name_en})</span></a> &gt; '
        
        # Get team English name if possible
        t_name_en = team_data.get('name_en', team_data.get('team_name_en', '')) if team_data else ''
        if not t_name_en:
             t_name_en = get_team_en_name(t_name_ja_lookup, current_team_clean)

        t_disp = t_name_ja_lookup
        if t_name_en and t_name_en != t_name_ja_lookup:
            # Strip start years from English name if present (e.g. "Team (2025)")
            t_name_en_clean = re.sub(r'[（(]\s*\d{4}.*?[）)]', '', t_name_en).strip()
            if t_name_en_clean != t_name_ja_lookup:
                t_disp += f' <span style="font-size: 0.8em; opacity: 0.7;">({t_name_en_clean})</span>'
            
        if target_league_slug == 'unknown':
            breadcrumbs += f'<span>{t_disp}</span> &gt; '
            header_team_block_local = f'<span class="header-team-link"><span class="current-team-label">所属チーム</span>{t_disp}</span>'
        else:
            breadcrumbs += f'<a href="{t_link}">{t_disp}</a> &gt; '
            header_team_block_local = f'<a href="{t_link}" class="header-team-link"><span class="current-team-label">所属チーム</span>{t_disp}</a>'
        
        breadcrumbs += f'<span>{name_ja}</span>'

        # Conditional L1 Caps
        l1_caps_html_local = ""
        if source == 'league_one':
            l1_caps_html_local = f"""
             <div class="info-item hover-effect">
                <div class="info-label">リーグワンキャップ</div>
                <div class="info-value">{l1_caps if l1_caps != '-' else '-'}</div>
            </div>"""

        rep_caps_html_local = f"<div class='info-value'>{rep_caps_val}</div>" if rep_caps_val and str(rep_caps_val) != 'nan' else "<div class='info-value'>-</div>"
        
        social_html_local = ""
        if socials:
            social_html_local += '<div class="social-links" style="margin-top: 15px;">'
            if 'instagram' in socials: social_html_local += f'<a href="{socials["instagram"]}" target="_blank" style="color: white; margin-right: 15px; font-size: 24px; text-decoration: none;">Instagram</a>'
            if 'twitter' in socials: social_html_local += f'<a href="{socials["twitter"]}" target="_blank" style="color: white; margin-right: 15px; font-size: 24px; text-decoration: none;">X (Twitter)</a>'
            social_html_local += '</div>'

        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name_ja} | RugbyPick</title>
    <link rel="canonical" href="https://rugbypick.com/player/{slug}.html">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
{CSS_STYLES}
{team_css}
    </style>
</head>
<body>
    <header class="header-container">
        <div class="header-content">
            <a href="{rel_root}index.html" class="site-title">{logo_img_local}</a>
        </div>
    </header>
    <nav class="nav-container">
        <ul class="nav-menu">
            <li><a href="{rel_root}index.html">ホーム</a></li>
            <li><a href="{nav_prefix}leagues.html">リーグ一覧</a></li>
            <li><a href="{nav_prefix}teams.html">チーム一覧</a></li>
            <li><a href="{nav_prefix}players.html">選手一覧</a></li>
        </ul>
    </nav>

    <div class="container">
        <div class="breadcrumbs" style="margin-bottom: 20px; font-size: 14px; color: #666;">
            {breadcrumbs}
        </div>
        <div class="player-header">
            <div class="player-name">{name_ja}</div>
            <div class="player-name-en">{name_en}</div>
            <a class="header-position" href="{rel_root}pages/players.html?pos={pos_norm}">ポジション {pos}</a>
            {social_html_local}
            {header_team_block_local}
        </div>

        <div class="info-grid">
            <div class="info-item hover-effect">
                <div class="info-label">生年月日</div>
                <div class="info-value">{birth_html_local}</div>
            </div>
             <div class="info-item hover-effect">
                <div class="info-label">年齢</div>
                <div class="info-value">{age_html_local}</div>
            </div>
            <div class="info-item hover-effect">
                <div class="info-label">身長</div>
                <div class="info-value">{height_html_local}</div>
            </div>
            <div class="info-item hover-effect">
                <div class="info-label">体重</div>
                <div class="info-value">{weight} kg</div>
            </div>
            <div class="info-item hover-effect">
                <div class="info-label">出身高校</div>
                <div class="info-value school-name">{hs_html_local}</div>
            </div>
            <div class="info-item hover-effect">
                <div class="info-label">出身大学</div>
                <div class="info-value school-name">{univ_html_local}</div>
            </div>
            {l1_caps_html_local}
            <div class="info-item hover-effect">
                <div class="info-label">登録区分</div>
                <div class="info-value">{category_val}</div>
            </div>
        </div>

        <h2 class="section-title">チーム遍歴</h2>
        <div class="career-section">{"".join(formatted_career_local)}</div>

        <h2 class="section-title">代表キャップ</h2>
        <div class="info-card">{rep_caps_html_local}</div>

        <h2 class="section-title">キャリア統計</h2>
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-value">{matches_stat}</div>
                <div class="stat-label">出場試合数</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{tries}</div>
                <div class="stat-label">トライ数</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{points}</div>
                <div class="stat-label">総得点</div>
            </div>
        </div>
    </div>
</body>
</html>"""

    # Write single canonical path
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(get_html(rel_root))

    return filename

if __name__ == "__main__":
    # Generate pages (No Limit)
    print(f"Generating all player pages ({len(players)})...")
    count = 0
    for i, player in enumerate(players):
        if i % 500 == 0: print(f"  ... {i}/{len(players)}")
        res = generate_player_page(player)
        if res:
            count += 1

    print(f"\n✓ Generation complete! Generated {count} rich player pages in dual paths.")
