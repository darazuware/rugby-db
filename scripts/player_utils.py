import json
import os
import re

def slugify(text):
    if not text: return "unknown"
    text = str(text).lower()
    # Replace spaces and underscores with hyphens
    text = text.replace(' ', '-').replace('_', '-')
    # Remove non-alphanumeric except hyphens
    text = re.sub(r'[^a-z0-9\-]', '', text)
    # Remove duplicate hyphens
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def clean_team_name(name):
    if not name: return ""
    return re.sub(r'[（(]\s*\d{4}.*?[）)]', '', str(name)).strip()

TEAM_SLUG_MAP = {
    "静岡ブルーレヴズ": "shizuoka-bluerevs",
    "東京サントリーサンゴリアス": "tokyo-suntory-sungoliath",
    "東京サンゴリアス": "tokyo-suntory-sungoliath",
    "サンゴリアス": "tokyo-suntory-sungoliath",
    "浦安D-Rocks": "urayasu-d-rocks",
    "コベルコ神戸スティーラーズ": "kobelco-kobe-steelers",
    "神戸スティーラーズ": "kobelco-kobe-steelers",
    "埼玉パナソニックワイルドナイツ": "saitama-panasonic-wildknights",
    "埼玉ワイルドナイツ": "saitama-panasonic-wildknights",
    "東芝ブレイブルーパス東京": "toshiba-brave-lupus-tokyo",
    "BL東京": "toshiba-brave-lupus-tokyo",
    "トヨタヴェルブリッツ": "toyota-verblitz",
    "三重ホンダヒート": "mie-honda-heat",
    "三菱重工相模原ダイナボアーズ": "mitsubishi-sagamihara-dynaboars",
    "相模原DB": "mitsubishi-sagamihara-dynaboars",
    "ダイナボアーズ": "mitsubishi-sagamihara-dynaboars",
    "横浜キヤノンイーグルス": "yokohama-canon-eagles",
    "横浜イーグルス": "yokohama-canon-eagles",
    "リコーブラックラムズ東京": "ricoh-blackrams-tokyo",
    "ブラックラムズ東京": "ricoh-blackrams-tokyo",
    "リコー": "ricoh-blackrams-tokyo",
    "キヤノン": "yokohama-canon-eagles",
    "NECグリーンロケッツ東葛": "nec-green-rockets-tokatsu",
    "グリーンロケッツ東葛": "nec-green-rockets-tokatsu",
    "九州電力キューデンヴォルテクス": "kyushu-electric-kyuden-voltex",
    "キューデンヴォルテクス": "kyushu-electric-kyuden-voltex",
    "清水建設江東ブルーシャークス": "shimizu-koto-blue-sharks",
    "江東ブルーシャークス": "shimizu-koto-blue-sharks",
    "豊田自動織機シャトルズ愛知": "toyota-shokki-shuttles-aichi",
    "日本製鉄釜石シーウェイブス": "kamaishi-seawaves",
    "釜石シーウェイブス": "kamaishi-seawaves",
    "花園近鉄ライナーズ": "hanazono-kintetsu-liners",
    "日野レッドドルフィンズ": "hino-reddolphins",
    "NTTドコモレッドハリケーンズ大阪": "red-hurricanes-osaka",
    "レッドハリケーンズ大阪": "red-hurricanes-osaka",
    "クリタウォーターガッシュ昭島": "kurita-watergush-akishima",
    "狭山セコムラガッツ": "secom-rugguts",
    "中国電力レッドレグリオンズ": "chugoku-electric-red-regulions",
    "マツダスカイアクティブズ広島": "mazda-skyactivs-hiroshima",
    "Skyactivs Hiroshima": "mazda-skyactivs-hiroshima",
    "Mazda Skyactivs Hiroshima": "mazda-skyactivs-hiroshima",
    "ヤクルトレビンズ戸田": "yakult-levins",
    "Yakult Levins": "yakult-levins",
    "ルリーロ福岡": "leriro-fukuoka",
    "LeRIRO Fukuoka": "leriro-fukuoka",
    "九州電力キューデンヴォルテクス": "kyushu-electric-kyuden-voltex",
    "Kyushu Electric Kyuden Voltex": "kyushu-electric-kyuden-voltex",
    "Kyuden Voltex": "kyushu-electric-kyuden-voltex",
    "浦安D-Rocks": "urayasu-d-rocks",
    "Urayasu D-Rocks": "urayasu-d-rocks",
    "トヨタヴェルブリッツ": "toyota-verblitz",
    "Toyota Verblitz": "toyota-verblitz",
    "クボタスピアーズ船橋・東京ベイ": "kubota-spears-funabashi-tokyo-bay",
    "Kubota Spears": "kubota-spears-funabashi-tokyo-bay",
    "Suntory Sungoliath": "tokyo-suntory-sungoliath",
    "Sungoliath": "tokyo-suntory-sungoliath",
    "Wild Knights": "saitama-panasonic-wildknights",
    "Panasonic Wild Knights": "saitama-panasonic-wildknights",
    "Toshiba Brave Lupus": "toshiba-brave-lupus-tokyo",
    "Brave Lupus": "toshiba-brave-lupus-tokyo",
    "Canon Eagles": "yokohama-canon-eagles",
    "Eagles": "yokohama-canon-eagles",
    "Black Rams": "ricoh-blackrams-tokyo",
    "Ricoh Black Rams": "ricoh-blackrams-tokyo",
    "Steelers": "kobelco-kobe-steelers",
    "Kobe Steelers": "kobelco-kobe-steelers",
    "Blue Revs": "shizuoka-bluerevs",
    "Yamaha Jubilo": "shizuoka-bluerevs",
}

SCHOOL_ORTHO_MAP = {
    "天理高校?U部": "天理高校Ⅱ部",
    "東海大学付属大阪仰星高校": "東海大大阪仰星高校",
    "東海大学仰星高校": "東海大大阪仰星高校",
    "東海大仰星高校": "東海大大阪仰星高校",
    "東海大仰星": "東海大大阪仰星高校",
    "中部大学春日丘高校": "中部大春日丘高校",
    "中部大春日ヶ丘高校": "中部大春日丘高校",
    "春日丘高校": "中部大春日丘高校",
    "春日ヶ丘高校": "中部大春日丘高校",
    "國學院大學久我山高校": "國學院久我山高校",
    "國學院久我山高校": "國學院久我山高校",
    "日本航空高校石川": "日本航空石川高校",
    "日本航空石川高校": "日本航空石川高校",
    "流通経済大学付属柏高校": "流経大柏高校",
    "流通経済大柏高校": "流経大柏高校",
    "輝翔館中等教育高校": "輝翔館高校",
    "桐蔭学園中等教育学校": "桐蔭学園高校",
    "秋田工高校": "秋田工業高校",
    "盛岡工": "盛岡工業高校",
    "流経大学": "流通経済大学",
    "大阪朝鮮高校": "大阪朝鮮高級学校",
    "ロトルアボーイズハイスクール": "ロトルアボーイズ",
    "DeLaSalleCollege": "デラセラ",
    "天理大学高校": "天理高校",
    "帝京大学高校": "帝京高校",
    "国学院栃木高校": "國學院栃木高校",
    "国学院大学栃木高校": "國學院栃木高校",
    "ウエリントンカレッジ": "ウェリントンカレッジ",
    "正平高校": "昌平高校",
    "関東学院大学六浦高校": "関東学院六浦高校",
}

SCHOOL_NAME_CHANGES = {
    "江の川高校": "石見智翠館高校",
    "伏見工業高校": "京都工学院高校",
    "東海大仰星高校": "東海大大阪仰星高校", # 厳密には名称変更に近いのでこちらにも含める
}

def get_normalized_school_name(name):
    """
    表記揺れを吸収した「名寄せ後の名前」を返す。
    名称変更は反映しない（卒業時の名前を維持するため）。
    """
    if not name or name == '-' or str(name).lower() == 'nan': return None
    name = str(name).strip()
    return SCHOOL_ORTHO_MAP.get(name, name)

def get_canonical_school_name(name):
    """
    名称変更も考慮した「現在の正式名称」を返す。
    統合ページのリンク先やスラッグ生成に使用する。
    """
    norm = get_normalized_school_name(name)
    if not norm: return None
    return SCHOOL_NAME_CHANGES.get(norm, norm)

def get_enrolment_year(player):
    """
    Calculate enrolment year based on career history.
    """
    current_team_slug = get_team_slug(player.get('team', ''))
    if not current_team_slug: return None
    
    career = player.get('career_history', [])
    first_year = None
    
    if isinstance(career, list):
        for entry in career:
            # Assuming list entries are like "Team (Year)" or dicts
            t_entry_slug = ""
            y_entry = None
            if isinstance(entry, dict):
                t_entry_slug = get_team_slug(entry.get('team', ''))
                y_entry = entry.get('year')
            else:
                raw_entry = str(entry)
                t_entry_slug = get_team_slug(raw_entry)
                match = re.search(r'\((\d{4})', raw_entry)
                if match: y_entry = match.group(1)
            
            if t_entry_slug == current_team_slug and y_entry:
                if not first_year or int(y_entry) < int(first_year):
                    first_year = y_entry
                    
    elif isinstance(career, str):
        parts = career.split(' -> ')
        for part in parts:
            t_part_slug = get_team_slug(part)
            if t_part_slug == current_team_slug:
                match = re.search(r'\((\d{4})', part)
                if match:
                    y_part = match.group(1)
                    if not first_year or int(y_part) < int(first_year):
                        first_year = y_part
                        
    return first_year

def get_team_slug(name):
    clean = clean_team_name(name)
    return TEAM_SLUG_MAP.get(clean, slugify(clean))


def process_career_history(career_history):
    """
    チーム遍歴を古い順にソートし、同じチームの期間を重複なくまとめる。
    """
    if not career_history or career_history == '-':
        return []
    
    entries = []
    # 柔軟な正規表現: スペースや全角ハイフンなどに対応
    pattern = r'^(.*?)\s*\(\s*(\d{4})\s*[-－]?\s*(\d{4}|)?\s*\)$'
    
    raw_list = []
    if isinstance(career_history, str):
        raw_list = career_history.split(' -> ')
    elif isinstance(career_history, list):
        raw_list = career_history

    for item in raw_list:
        if isinstance(item, dict):
            team = item.get('team', '')
            year_val = item.get('year', '')
            try:
                # 辞書形式の場合、yearを数値として扱う。
                start = int(year_val)
                entries.append({'team': team, 'start': start, 'end': None})
            except:
                entries.append({'team': team, 'start': 9999, 'end': None})
        elif isinstance(item, str):
            match = re.match(pattern, item.strip())
            if match:
                team = match.group(1).strip()
                start = int(match.group(2))
                end = int(match.group(3)) if match.group(3) else None
                entries.append({'team': team, 'start': start, 'end': end})
            else:
                # 正規表現にマッチしない場合はそのまま
                entries.append({'team': item.strip(), 'start': 9999, 'end': None})

    if not entries:
        return []

    # 1. チーム名ごとに期間を集約
    team_summary = {} # team_ja -> {team, start, end}
    for e in entries:
        team_ja = translate_team_name(e['team'])
        if team_ja not in team_summary:
            team_summary[team_ja] = {
                'team': team_ja, 
                'start': e['start'], 
                'end': e['end']
            }
        else:
            if e['start'] != 9999:
                team_summary[team_ja]['start'] = min(team_summary[team_ja]['start'], e['start'])
            if e['end']:
                team_summary[team_ja]['end'] = max(team_summary[team_ja]['end'] or 0, e['end'])
            # e['start']が9999でなくe['end']がない（現在進行形）場合は、endも無期限扱い（None）にすべきだが、
            # すでに終了年がある場合はそれを維持するのが安全か。
            # ただし「まとめる」要件なので、期間の最大値を取る。

    # 2. リスト化して開始年順にソート
    merged = list(team_summary.values())
    merged.sort(key=lambda x: (x['start'], x['end'] or 9999))

    return merged

OVERSEAS_TEAM_MAP = {
    'Crusaders': 'super-rugby-pacific', 'Blues': 'super-rugby-pacific', 'Hurricanes': 'super-rugby-pacific', 
    'Chiefs': 'super-rugby-pacific', 'Highlanders': 'super-rugby-pacific', 'Brumbies': 'super-rugby-pacific',
    'Reds': 'super-rugby-pacific', 'Waratahs': 'super-rugby-pacific', 'Western Force': 'super-rugby-pacific',
    'Northampton Saints': 'premiership-rugby', 'Saracens': 'premiership-rugby', 'Bath Rugby': 'premiership-rugby',
    'Harlequins': 'premiership-rugby', 'Leicester Tigers': 'premiership-rugby', 'Sale Sharks': 'premiership-rugby',
    'Exeter Chiefs': 'premiership-rugby', 'Bristol Bears': 'premiership-rugby', 'Gloucester': 'premiership-rugby',
    'Newcastle Falcons': 'premiership-rugby',
    'Leinster': 'united-rugby-championship', 'Munster': 'united-rugby-championship', 'Stormers': 'united-rugby-championship',
    'Bulls': 'united-rugby-championship', 'Glasgow Warriors': 'united-rugby-championship', 'Sharks': 'united-rugby-championship',
    'Vannes': 'top-14', 'Provence': 'pro-d2', 'Béziers': 'pro-d2', 'Brive': 'pro-d2', 'Oyonnax': 'pro-d2', 'Aurillac': 'pro-d2',
    'Blue Bulls': 'currie-cup', 'Free State Cheetahs': 'currie-cup', 'Golden Lions': 'currie-cup', 
    'Western Province': 'currie-cup', 'Pumas': 'currie-cup', 'Griquas': 'currie-cup', 'Griffons': 'currie-cup',
    'Leopards': 'currie-cup', 'Valke': 'currie-cup', 'Boland Cavaliers': 'currie-cup', 
    'Eastern Province Elephants': 'currie-cup', 'Border Bulldogs': 'currie-cup', 'SWD Eagles': 'currie-cup', 'Cheetahs': 'currie-cup'
}

def get_league_slug_for_team(t_name_ja, t_name_en=''):
    if not t_name_ja: t_name_ja = ''
    if not t_name_en: t_name_en = ''
    
    # Priority: League One Check
    jrlo_keywords = ['浦安', '豊田自動', 'NEC', '九州電力', '日本製鉄', 'レッドハリケーンズ', '日野', '清水', 'クリタ', '中国電力', 'マツダ', 'ヤクルト', 'ルリーロ', 'ブルーレヴズ', 'サンゴリアス', 'D-Rocks', 'スティーラーズ', 'ワイルドナイツ', 'ブレイブルーパス', 'ヴェルブリッツ', 'ヒート', 'ダイナボアーズ', 'イーグルス', 'ブラックラムズ', 'スピアーズ', 'ライナーズ', '花園', '近鉄']
    if any(x in t_name_ja for x in jrlo_keywords):
        return 'leagueone'
        
    # Top 14
    t14_teams = ['トゥールーズ', 'ボルドー・ベグル', 'スタッド・フランセ', 'トゥーロン', 'ラ・ロシェル', 'ラシン92', 'リヨン', 'カストル', 'ポー', 'ペルピニャン', 'バイヨンヌ', 'クレルモン', 'モンペリエ', 'ヴァンヌ']
    if t_name_ja in t14_teams:
        return 'top-14'
        
    # Overseas Map
    for k, v in OVERSEAS_TEAM_MAP.items():
        if k == 'Sharks' and ('Blue Sharks' in t_name_ja or 'Blue Sharks' in t_name_en):
            continue
        if k == 'Saracens' and ('Lelo' in t_name_ja or 'Lelo' in t_name_en):
            continue
            
        if k in t_name_ja or (t_name_en and k in t_name_en):
            return v
            
    return None

def get_player_name_key(p):
    name_en = str(p.get('name_en') or p.get('en_name', '')).lower()
    # Aggressive cleaning to match generate_player_pages.py
    return name_en.replace(' ', '').replace('-', '').replace('\'', '').replace('’', '')

def load_unified_players():
    sources = [
        'data/unified_player_database_final.json',
        'data/unified_player_database_full.json',
        'data/top14_players_enriched.json'
    ]
    
    combined = {}
    for path in sources:
        if not os.path.exists(path): continue
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            p_list = data if isinstance(data, list) else data.values()
            for p in p_list:
                key = get_player_name_key(p)
                if not key: continue
                
                if key not in combined:
                    combined[key] = p
                else:
                    existing = combined[key]
                    # Merge missing fields
                    for k, v in p.items():
                        if v and (not existing.get(k) or existing.get(k) in ['-', '', '不明', 'nan', []]):
                            if k == 'id' and 'lo_' in str(existing.get('id')): continue
                            existing[k] = v
                    
                    # Career history priority
                    new_h = p.get('career_history', [])
                    old_h = existing.get('career_history', [])
                    
                    # If existing has a list and new has a string, don't overwrite with string unless list is empty
                    if isinstance(new_h, list) and isinstance(old_h, list):
                        if len(new_h) > len(old_h):
                            existing['career_history'] = new_h
                    elif isinstance(new_h, list) and not isinstance(old_h, list):
                        existing['career_history'] = new_h
                    elif not isinstance(new_h, list) and isinstance(old_h, list):
                        # If existing is a list (could be empty) and new is a string,
                        # take the string if it's longer than what we have or if list is empty
                        if not old_h or len(str(new_h)) > len(str(old_h)):
                            existing['career_history'] = new_h
                    elif not isinstance(new_h, list) and not isinstance(old_h, list):
                        if len(str(new_h)) > len(str(old_h)):
                            existing['career_history'] = new_h
                        
    return list(combined.values())

def get_player_team_link_path(player):
    from player_utils import get_team_slug, get_league_slug_for_team, clean_team_name
    t_raw = player.get('team', '')
    if not t_raw or t_raw == '-': return None
    
    t_clean = clean_team_name(t_raw)
    t_slug = get_team_slug(t_raw)
    l_slug = get_league_slug_for_team(t_clean, player.get('team_en', ''))
    
    if not l_slug:
        # Fallback to source
        src = player.get('source', '')
        if src == 'league_one': l_slug = 'leagueone'
        elif src == 'Top 14' or src == 'top_14': l_slug = 'top-14'
        else: l_slug = 'unknown'
        
    if l_slug == 'unknown':
        return f"/teams/{t_slug}.html" # Fallback to flat if league unknown
    
    return f"/teams/{l_slug}/{t_slug}/"

NATIONALITY_JA = {
    'Japan': '日本', 'New Zealand': 'ニュージーランド', 'Australia': 'オーストラリア',
    'South Africa': '南アフリカ', 'Fiji': 'フィジー', 'Tonga': 'トンガ', 'Samoa': 'サモア',
    'England': 'イングランド', 'Scotland': 'スコットランド', 'Wales': 'ウェールズ',
    'Ireland': 'アイルランド', 'France': 'フランス', 'Argentina': 'アルゼンチン',
    'USA': 'アメリカ', 'Canada': 'カナダ', 'Namibia': 'ナミビア', 'Uruguay': 'ウルグアイ',
    'Korea': '韓国', 'Italy': 'イタリア', 'Georgia': 'ジョージア'
}

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
    'Mitsubishi Sagamihara Dynaboars': '三菱重工相模原ダイナボアーズ',
    'Kyushu Electric Kyuden Voltex': '九州電力キューデンヴォルテクス',
    'Kyūshu キューデンヴォルテクス': '九州電力キューデンヴォルテクス',
    'Kyushu Kyuden Voltex': '九州電力キューデンヴォルテクス',
    'Coca Cola West Red Sparks': 'コカ・コーラウエストレッドスパークス',
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

def translate_team_name(text):
    if not isinstance(text, str): return text
    clean_text = re.sub(r'\(.*?\)', '', text).strip()
    
    # Sort translations by length to match longest first
    for eng, jap in sorted(TEAM_TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True):
        if eng in clean_text or eng in text:
            return jap
    return clean_text if clean_text else text

def translate_nationality(nat_str):
    if not nat_str or nat_str == '-': return '-'
    parts = str(nat_str).split('/')
    translated_parts = []
    for p in parts:
        p = p.strip()
        translated_parts.append(NATIONALITY_JA.get(p, p))
    return ' / '.join(translated_parts)

def get_player_score(p):
    score = 0
    if p.get('height') and str(p.get('height')) not in ['nan', '-', '', '不明']: score += 1
    if p.get('weight') and str(p.get('weight')) not in ['nan', '-', '', '不明']: score += 1
    
    bdate = str(p.get('birthdate', '')).strip()
    if bdate and bdate not in ['nan', '-', '', '不明']:
        score += 1
        
    img = p.get('image_url')
    if img and 'placeholder' not in img and str(img) not in ['nan', '']: score += 1
    if p.get('rep_caps') and str(p.get('rep_caps')) not in ['nan', '-', '', '不明']: score += 1
    
    return score

POSITION_MAP = {
    'プロップ': 'PR', 'フッカー': 'HO', 'セカンドロー': 'LO', 'フランカー': 'FL',
    'ナンバーエイト': 'No8', 'スクラムハーフ': 'SH', 'フライハーフ': 'SO',
    'センター': 'CTB', 'ウィング': 'WTB', 'フルバック': 'FB',
    'バックロー': 'FL', 'Prop': 'PR', 'Hooker': 'HO', 'Second Row': 'LO',
    'Flanker': 'FL', 'Number 8': 'No8', 'Scrum-half': 'SH', 'Fly-half': 'SO',
    'Center': 'CTB', 'Wing': 'WTB', 'Fullback': 'FB',
    '右プロップ': 'PR', '左プロップ': 'PR', '右PR': 'PR', '左PR': 'PR',
    'No.8': 'No8', 'No8': 'No8', 'NO8': 'No8'
}

def normalize_position(pos):
    if not pos or pos == '-' or str(pos) == 'nan': return '-'
    clean_pos = str(pos).strip().replace('　', ' ')
    if clean_pos in POSITION_MAP:
        return POSITION_MAP[clean_pos]
    
    for k, v in POSITION_MAP.items():
        if k in clean_pos:
            return v
            
    return clean_pos

POSITION_ORDER = {
    'PR': 1, 'HO': 2, 'LO': 3, 'FL': 4, 'No.8': 5, 'NO8': 5,
    'SH': 6, 'SO': 7, 'CTB': 8, 'WTB': 9, 'FB': 10
}

def get_pos_rank(pos):
    if not pos: return 100
    norm = normalize_position(pos)
    return POSITION_ORDER.get(norm, 100)

import hashlib
from pykakasi import kakasi

# Initialize pykakasi
kks = kakasi()

MAJOR_SCHOOL_SLUGS = {
    # Universities
    "帝京大学": "univ-teikyo", "早稲田大学": "univ-waseda", "明治大学": "univ-meiji",
    "慶應義塾大学": "univ-keio", "東海大学": "univ-tokai", "天理大学": "univ-tenri",
    "京都産業大学": "univ-kyosan", "筑波大学": "univ-tsukuba", "日本大学": "univ-nichidai",
    "立命館大学": "univ-rits", "同志社大学": "univ-doshisha", "関西学院大学": "univ-kwansei",
    "大東文化大学": "univ-daito", "流通経済大学": "univ-ryukei", "近畿大学": "univ-kindai",
    "法政大学": "univ-hosei", "東洋大学": "univ-toyo", "専修大学": "univ-senshu",
    "日本体育大学": "univ-nittai", "摂南大学": "univ-setsunan", "立正大学": "univ-rissho",
    "山梨学院大学": "univ-yamanashi", "拓殖大学": "univ-takushoku", "関東学院大学": "univ-kanto",
    "中央大学": "univ-chuo", "福岡大学": "univ-fukuoka", "九州共立大学": "univ-kyukyo",
    "朝日大学": "univ-asahi", "大阪体育大学": "univ-daitai", "関西大学": "univ-kandai",
    "花園大学": "univ-hanazono", "福岡工業大学": "univ-fukukodai", "立教大学": "univ-rikkyo",
    "青山学院大学": "univ-aoyama", "中京大学": "univ-chukyo", "日本文理大学": "univ-bunri",

    # High Schools
    "天理高校": "hs-tenri",
    "流経大柏高校": "hs-ryukei-kashiwa", "桐蔭学園高校": "hs-toin", "東福岡高校": "hs-higashifukuoka",
    "大阪桐蔭高校": "hs-osakatoin", "報徳学園高校": "hs-hotoku", "國學院久我山高校": "hs-kugayama",
    "京都成章高校": "hs-kyotoseisho", "常翔学園高校": "hs-josho", "御所実業高校": "hs-gose",
    "佐賀工業高校": "hs-sagakogyo", "長崎北陽台高校": "hs-hokuyodai", "秋田工業高校": "hs-akitakogyo",
    "石見智翠館高校": "hs-chisuikan", "伏見工業高校": "hs-fushimikogyo", "京都工学院高校": "hs-kyotokogakuin",
    "東海大大阪仰星高校": "hs-gyosei", "東海大仰星高校": "hs-gyosei", "國學院栃木高校": "hs-kokutochi",
    "目黒学院高校": "hs-meguro", "中部大春日丘高校": "hs-harugaoka", "東京高校": "hs-tokyo",
    "日川高校": "hs-hikawa", "札幌山の手高校": "hs-yamanote", "大分舞鶴高校": "hs-maizuru",
    "日本航空石川高校": "hs-ja-ishikawa", "日本航空高校石川": "hs-ja-ishikawa", "深谷高校": "hs-fukaya",
    "尾道高校": "hs-onomichi", "常翔啓光学園高校": "hs-keiko", "高鍋高校": "hs-takanabe",
    "東海大相模高校": "hs-sagami", "鹿児島実業高校": "hs-kajitsu", "仙台育英高校": "hs-sendai-ikuei"
}

def get_school_slug(name):
    if not name or name == '-': return ""
    canonical = get_canonical_school_name(name) or name
    
    # 1. Check major mapping
    if canonical in MAJOR_SCHOOL_SLUGS:
        return MAJOR_SCHOOL_SLUGS[canonical]
    
    # Pre-process for better romaji
    # 「大」を dai、「高」を kou と読むように変換
    processed_name = str(canonical).replace("大", "ダイ").replace("高", "コウ")
    
    # 2. Automated Romaji conversion using pykakasi
    result = kks.convert(processed_name)
    romaji = "".join([item['hepburn'] for item in result]).lower()
    
    # 冗長なキーワードを削除
    romaji = romaji.replace('daigaku', '').replace('koukou', '').replace('fuzoku', '').replace('koto', '')
    
    # Cleanup romaji for URL
    romaji = re.sub(r'[^a-z0-9]', '-', romaji)
    romaji = re.sub(r'-+', '-', romaji).strip('-')
    
    prefix = "s"
    if "高校" in str(canonical) or "高" in str(canonical): prefix = "hs"
    elif "大学" in str(canonical): prefix = "univ"
    
    return f"{prefix}-{romaji}"

def get_attribute_slug(text):
    if not text or text == '-': return ""
    return slugify(text)

def calculate_age(birthdate):
    if not birthdate or str(birthdate) in ['nan', '-', '', '不明']:
        return "-"
    m = re.search(r'(\d{4})', str(birthdate))
    if m:
        birth_year = m.group(1)
        try:
            # Based on 2026 current year
            return str(2026 - int(birth_year))
        except:
            return "-"
    return "-"
