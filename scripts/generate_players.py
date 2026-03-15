import csv
import os
import re
import shutil
import glob
import json
import sys
from datetime import datetime
from team_utils import linkify_career, get_team_info, get_team_link

# CSVフィールドの制限を緩和
csv.field_size_limit(1000000)

# 設定
CSV_PATH = 'data_sources/final_master_data_v25.csv'
# 統合後のファイルが存在すればそちらを優先
INTEGRATED_CSV_PATH = 'data_sources/final_master_data_v25_integrated.csv'
if os.path.exists(INTEGRATED_CSV_PATH):
    CSV_PATH = INTEGRATED_CSV_PATH

OUTPUT_DIR = 'src/content/players'
CURRENT_YEAR = 2026 

# teams.json をロードしてチーム名からのリーグ逆引き用辞書を作成
TEAMS_DATA = []
if os.path.exists('data/teams.json'):
    try:
        with open('data/teams.json', 'r', encoding='utf-8') as f:
            TEAMS_DATA = json.load(f)
    except: pass

# チーム名と改称履歴の辞書をグローバルで作成
TEAM_HISTORY_MAP = {}
for t in TEAMS_DATA:
    if 'renamed_year' in t and 'former_name' in t:
        TEAM_HISTORY_MAP[t['team_name']] = {
            'year': int(t['renamed_year']),
            'former': t['former_name']
        }

def find_league_by_team(team_name):
    if not team_name: return ""
    # 完全一致
    for team in TEAMS_DATA:
        if team.get('team_name') == team_name or team.get('team_name_jp') == team_name or team.get('team_en_name') == team_name:
            return team['league']
    # 部分一致
    for team in TEAMS_DATA:
        if team_name in team.get('team_name', '') or (team.get('team_name_jp') and team_name in team['team_name_jp']):
            return team['league']
    return ""

def clean_team_name(team_name):
    if not team_name or str(team_name).lower() == 'nan': return ""
    return re.sub(r'[\(（].*?[\)）]', '', team_name).strip()

def calculate_age(birth_date_str):
    if not birth_date_str or str(birth_date_str).lower() == 'nan': return None
    b_str = str(birth_date_str).strip()
    try:
        # YYYY.MM.DD or YYYY-MM-DD or YYYY
        date_sep = '-' if '-' in b_str else '.'
        if len(b_str) == 4 and b_str.isdigit():
            return CURRENT_YEAR - int(b_str)
        
        # 2004.. のような不完全な形式への対応
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

def get_base_team_name(t):
    # リンクがあれば剥がす
    t = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', t)
    # 括弧（全角半角両方）を剥がす
    t = re.sub(r'[\(（].*?[\)）]', '', t)
    t = t.strip()
    
    # 特定のチーム名の名寄せ
    name_map = {
        'Auckland': 'Auckland Blues',
        'Blues': 'Auckland Blues',
        'Wellington': 'Wellington Lions',
        'Lions': 'Wellington Lions',
        'Canterbury': 'Crusaders',
        'Waikato': 'Chiefs',
        'Otago': 'Highlanders',
        'Taranaki': 'Chiefs',
        
        'サントリー': '東京サントリーサンゴリアス',
        'サンゴリアス': '東京サントリーサンゴリアス',
        'パナソニック': '埼玉パナソニックワイルドナイツ',
        'ワイルドナイツ': '埼玉パナソニックワイルドナイツ',
        'トヨタ': 'トヨタヴェルブリッツ',
        'トヨタ自動車': 'トヨタヴェルブリッツ',
        '神戸製鋼': 'コベルコ神戸スティーラーズ',
        'コベルコ': 'コベルコ神戸スティーラーズ',
        'ヤマハ': '静岡ブルーレヴズ',
        'ヤマハ発動機': '静岡ブルーレヴズ',
        '東芝': '東芝ブレイブルーパス東京',
        'ブレイブルーパス': '東芝ブレイブルーパス東京',
        'キヤノン': '横浜キヤノンイーグルス',
        'リコー': 'リコーブラックラムズ東京',
        'クボタ': 'クボタスピアーズ船橋・東京ベイ',
        'スピアーズ': 'クボタスピアーズ船橋・東京ベイ',
        'NTTコム': '浦安D-Rocks',
        'NTTコミュニケーションズ': '浦安D-Rocks',
        'シャイニングアークス': '浦安D-Rocks',
        'NTTドコモ': 'レッドハリケーンズ大阪',
        'ドコモ': 'レッドハリケーンズ大阪',
        '日野': '日野レッドドルフィンズ',
        '日野自動車': '日野レッドドルフィンズ',
        '三菱重工': '三菱重工相模原ダイナボアーズ',
        '三菱重工相模原': '三菱重工相模原ダイナボアーズ',
        'ホンダ': '三重ホンダヒート',
        '近鉄': '花園近鉄ライナーズ',
        'NEC': 'NECグリーンロケッツ東葛',
        'グリーンロケッツ': 'NECグリーンロケッツ東葛',
        '九州電力': '九州電力キューデンヴォルテクス',
        '清水建設': '清水建設江東ブルーシャークス',
        '豊田自動織機': '豊田自動織機シャトルズ愛知',
        '釜石': '日本製鉄釜石シーウェイブス',
        '日本製鉄釜石': '日本製鉄釜石シーウェイブス',
        '栗田工業': 'クリタウォーターガッシュ昭島',
        'セコム': '狭山セコムラガッツ',
        '中国電力': '中国電力レッドレグリオンズ',
        'マツダ': 'マツダスカイアクティブズ広島',
        'ヤクルト': 'ヤクルトレビンズ戸田',
        'ルリーロ': 'ルリーロ福岡'
    }
    for k, v in name_map.items():
        if t == k: return v
    for current_name, history in TEAM_HISTORY_MAP.items():
        if t == history['former']:
            return current_name
    return t

def normalize_school_name(name):
    if not name or str(name).lower() == 'nan' or name == '---': return ""
    name = name.strip()
    
    # 1. 一般的な「大」「高」の補完
    if name.endswith('大') and not name.endswith('大学'):
        name = name + '学'
    elif name.endswith('高') and not name.endswith('高校'):
        name = name + '校'
    
    # 2. 名称変更履歴付きの正規化
    # 伏見工業・京都工学院グループ
    if any(x in name for x in ['伏見工業', '伏見工']):
        return "伏見工業高校（現：京都工学院高校）"
    if '京都工学院' in name:
        return "京都工学院高校（旧：伏見工業高校）"
        
    # 江の川・石見智翠館グループ
    if '江の川' in name:
        return "江の川高校（現：石見智翠館高校）"
    if '石見智翠館' in name:
        return "石見智翠館高校（旧：江の川高校）"

    # 3. その他の特定の校名変更/正規化
    school_map = {
        '東海大仰星高校': '東海大大阪仰星高校',
        '東海大仰星': '東海大大阪仰星高校',
        '大阪仰星': '東海大大阪仰星高校',
        '日本航空高校石川': '日本航空石川高校',
        '日本航空高校': '日本航空石川高校',
    }
    
    if name in school_map:
        return school_map[name]
        
    return name

def format_career_md(career_str, current_team, name_en=""):
    if not career_str or str(career_str).lower() == 'nan': return ""
    parts = [p.strip() for p in str(career_str).split('->')]
    parsed_entries = []
    for p in parts:
        years = re.findall(r'\d{4}', p)
        start_year = int(years[0]) if years else 0
        parsed_entries.append({'text': p, 'year': start_year})
    parsed_entries.sort(key=lambda x: x['year'])
    
    temp_entries = []
    for entry in parsed_entries:
        p = entry['text']
        match = re.search(r'^(.+?)\s*\(([\d\s\?\*]+)\s*-\s*([\d\s\?\*]*)\)$', p)
        if not match: match = re.search(r'^(.+?)\s*\(([\d\s\?\*]+)\)$', p)
        if match:
            team = match.group(1).strip()
            start_p = match.group(2).strip()
            end_p = match.group(3).strip() if len(match.groups()) > 2 else ""
            if any(kw in team for kw in ["University", "College", "School", "小学校", "中学校", "高校", "大学", "学園"]): continue
            temp_entries.append({'team': team, 'start': start_p, 'end': end_p, 'year': entry['year']})
        else:
            if not any(kw in entry['text'] for kw in ["University", "College", "School", "小学校", "中学校", "高校", "大学", "学園"]):
                temp_entries.append({'team': entry['text'].strip(), 'start': "", 'end': "", 'year': entry['year'], 'raw': True})

    if not temp_entries: return ""
    
    merged = []
    for entry in temp_entries:
        if not merged:
            merged.append(entry)
            continue
        last = merged[-1]
        if get_base_team_name(last['team']) == get_base_team_name(entry['team']) and not entry.get('raw') and not last.get('raw'):
            if last['start'] and entry['start']:
                try:
                    l_s, e_s = int(last['start']), int(entry['start'])
                    if e_s < l_s: last['start'] = str(e_s)
                except: pass
            elif entry['start']: last['start'] = entry['start']
            if not last['end'] or not entry['end']: last['end'] = ""
            else:
                try:
                    l_e, e_e = int(last['end']), int(entry['end'])
                    last['end'] = str(max(l_e, e_e))
                except: pass
            last['year'] = max(last['year'], entry['year'])
        else: merged.append(entry)

    lines = []
    for entry in merged:
        linked_team = get_team_link(entry['team'], include_flag=True)
        if entry.get('raw'):
            lines.append(f"- {linked_team}")
            continue
        start_p, end_p = entry['start'], entry['end']
        is_current = (not end_p or (end_p.isdigit() and int(end_p) >= CURRENT_YEAR - 1))
        
        info_icon = ""
        base_name = get_base_team_name(entry['team'])
        if base_name in TEAM_HISTORY_MAP:
            h = TEAM_HISTORY_MAP[base_name]
            try:
                s_yr = int(start_p) if start_p and start_p.isdigit() else 9999
                if s_yr < h['year']:
                    svg_icon = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" style="width:1.2em;height:1.2em;display:inline;vertical-align:-0.2em;"><path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" /></svg>'
                    info_icon = f' <span class="team-info-icon" tabindex="0" data-tooltip="{h["year"]}年から「{base_name}」に改称&#10;（旧称：{h["former"]}）">{svg_icon}</span>'
            except: pass

        period = f"{start_p} - " if is_current and entry == merged[-1] else (f"{start_p} - {end_p}" if end_p and end_p != start_p else start_p)
        if period: lines.append(f"- {linked_team}{info_icon} ({period})")
        else: lines.append(f"- {linked_team}{info_icon}")
    return "\n".join(lines)

def generate_slug(name_en, player_id, scraped_url=""):
    if scraped_url and 'all.rugby/player/' in scraped_url:
        url_id = scraped_url.split('/')[-1]
        if url_id: return url_id
    if not name_en or str(name_en).lower() == 'nan': return f"player-{player_id}"
    slug = re.sub(r'[^a-z0-9]+', '-', str(name_en).lower()).strip('-')
    return f"{slug}-{player_id}"

def main():
    print(f"Starting player generation from {CSV_PATH}...")
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for f in glob.glob(os.path.join(OUTPUT_DIR, '*.md')): os.remove(f)
    
    with open(CSV_PATH, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers, header_map = None, {}
        generated_count, skipped_count, processed_keys = 0, 0, set()
        
        for i, row in enumerate(reader):
            if not row or not any(row): continue
            if '英語名' in row[0] or 'English Name' in row[0]:
                headers = [h.strip().lstrip('\ufeff') for h in row]
                header_map = {name: idx for idx, name in enumerate(headers)}
                continue
            if not headers: continue

            def get_val(key_list):
                for k in key_list:
                    if k in header_map:
                        idx = header_map[k]
                        if idx < len(row):
                            val = row[idx].strip()
                            if val: return val
                return ""

            try:
                name_en = get_val(['英語名', 'name_en', 'English Name'])
                if name_en in ['英語名', 'English Name', '']: continue
                name_ja = get_val(['選手名_カタカナ', '選手名', 'name_ja']) or name_en
                birth_date = get_val(['生年月日', 'birth_date'])
                team_raw = get_val(['所属チーム', 'team', 'Team'])
                if team_raw in ['所属チーム', 'Team', '']: continue
                
                current_team = clean_team_name(team_raw)
                scraped_url = get_val(['Scraped_Url', 'URL', 'url'])
                dedup_key = scraped_url if scraped_url else (name_en.lower(), birth_date, current_team.lower())
                if dedup_key in processed_keys:
                    skipped_count += 1
                    continue
                processed_keys.add(dedup_key)
                
                slug = generate_slug(name_en, i + 1, scraped_url)
                team_info = get_team_info(current_team)
                if team_info:
                    current_team, league = team_info['jp'], team_info['league']
                else: league = ""
                
                if league == 'leagueone': league = 'league-one'
                if not league:
                    if scraped_url:
                        if 'league-one.jp' in scraped_url: league = 'league-one'
                        elif 'super.rugby' in scraped_url: league = 'super-rugby'
                        elif 'top14.lnr.fr' in scraped_url: league = 'top14'
                    if not league: league = find_league_by_team(current_team)
                    if not league and any(t in current_team for t in ['トゥールーズ', 'ボルドー', 'ラ・ロシェル', 'ラシン92', 'トゥーロン', 'モンペリエ', 'リヨン', 'カストル', 'アヴィロン・バイヨンヌ', 'セクション・パロワーズ', 'スタッド・フランセ', 'クレルモン', 'ペルピニャン', 'ヴァンヌ', 'ポー', 'バイヨンヌ']): league = 'top14'
                    if not league and any(t in current_team for t in ['ブルーズ', 'チーフス', 'ハリケーンズ', 'クルセイダーズ', 'ハイランダーズ', 'ブランビーズ', 'ワラターズ', 'レッズ', 'フォース', 'フィジアン・ドゥルア', 'モアナ・パシフィカ']): league = 'super-rugby'
                
                # URC 選手も生成対象に含める
                # if league == 'urc':
                #     skipped_count += 1
                #     continue
                
                # 海外選手名（SR, Top 14, URC）のハイフンを中黒に置換
                if league in ['super-rugby', 'top14', 'urc']:
                    name_ja = name_ja.replace('-', '・').replace('－', '・')
                
                career_md = format_career_md(get_val(['Full_Career', 'キャリア遍歴']), current_team, name_en)
                l_caps_raw = str(get_val(['リーグワンキャップ数']) or '0')
                l_caps_match = re.search(r'(\d+)', l_caps_raw)
                league_one_caps = l_caps_match.group(1) if l_caps_match else "0"
                c_val = str(get_val(['代表キャップ数', 'International_Caps'])).strip()
                if c_val.startswith('http'): c_val = ""
                caps_match = re.search(r'(.+?)代表', c_val)
                country = re.sub(r'[\(（].*$', '', caps_match.group(1).strip()) if caps_match else ""
                if not country: 
                    country_raw = get_val(['International_Caps', '国籍'])
                    # 'Italy (15 caps)' などの形式から国名を抽出
                    country = re.sub(r'\s*\(.*?\)', '', country_raw).strip()
                
                cat_v = get_val(['カテゴリ']).strip()
                category = f"カテゴリー{cat_v}" if league == 'league-one' and cat_v in ['A', 'B', 'C'] else ""
                division = team_info.get('division', "Division 1") if team_info else ("Division 1" if league == 'league-one' else "")
                has_scores = "true" if league in ['league-one', 'top14'] else "false"
                joined_year = "null"
                years = re.findall(r'\((\d{4})', career_md.split('\n')[-1] if career_md else "")
                if years: joined_year = years[-1]

                content = f"""---
title: "{name_ja}"
name_en: "{name_en}"
position: "{get_val(["ポジション"])}"
team: "{current_team}"
height: "{get_val(["身長"])}"
weight: "{get_val(["体重"])}"
birth_date: "{birth_date}"
age: {calculate_age(birth_date) or "null"}
high_school: "{normalize_school_name(get_val(["高校"]))}"
university: "{normalize_school_name(get_val(["大学"]))}"
caps: "{c_val}"
league_one_caps: "{league_one_caps}"
country: "{country}"
nationality: "{get_val(['国籍']).strip()}"
category: "{category}"
division: "{division}"
league: "{league}"
joined_year: {joined_year}
has_scores: {has_scores}
instagram: "{get_val(['SNS_Instagram']).strip()}"
twitter: "{get_val(['SNS_Twitter']).strip()}"
facebook: "{get_val(['SNS_Facebook']).strip()}"
---

{career_md}
"""
                with open(os.path.join(OUTPUT_DIR, f"{slug}.md"), 'w', encoding='utf-8') as wf: wf.write(content)
                generated_count += 1
                if generated_count % 200 == 0:
                    print(f"Generated {generated_count} players...")
            except Exception as e:
                print(f"Error processing row {i+1}: {e}")

    print(f"SUCCESS: Generated {generated_count} players. (Skipped {skipped_count} duplicates)")

if __name__ == "__main__":
    main()
