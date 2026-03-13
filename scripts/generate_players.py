import csv
import os
import re
import shutil
import glob
import json
from datetime import datetime
from team_utils import linkify_career, get_team_info, get_team_link

# 設定
CSV_PATH = 'data_sources/final_master_data_v17_consolidated.csv'
# 統合後のファイルが存在すればそちらを優先
INTEGRATED_CSV_PATH = 'data_sources/final_master_data_v17_consolidated_integrated.csv'
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

def format_career_md(career_str, current_team, name_en=""):
    """
    キャリア遍歴を Markdown 箇条書きに整形する。
    """
    if not career_str or str(career_str).lower() == 'nan': return ""
    
    # セパレータで分割
    parts = [p.strip() for p in str(career_str).split('->')]
    
    parsed_entries = []
    for p in parts:
        years = re.findall(r'\d{4}', p)
        start_year = int(years[0]) if years else 0
        parsed_entries.append({'text': p, 'year': start_year})
    
    # 昇順（古い順）に並べ替える
    parsed_entries.sort(key=lambda x: x['year'])
    
    # チーム・期間情報の抽出と正規化
    temp_entries = []
    for entry in parsed_entries:
        p = entry['text']
        match = re.search(r'^(.+?)\s*\(([\d\s\?\*]+)\s*-\s*([\d\s\?\*]*)\)$', p)
        if not match:
            match = re.search(r'^(.+?)\s*\(([\d\s\?\*]+)\)$', p)
        
        if match:
            team = match.group(1).strip()
            start_p = match.group(2).strip()
            end_p = match.group(3).strip() if len(match.groups()) > 2 else ""
            
            # 学歴を除外
            if any(kw in team for kw in ["University", "College", "School", "小学校", "中学校", "高校", "大学", "学園"]):
                continue
            
            temp_entries.append({
                'team': team,
                'start': start_p,
                'end': end_p,
                'year': entry['year']
            })
        else:
            # 形式が合わない場合はそのまま保持（学歴チェックは一応行う）
            if not any(kw in entry['text'] for kw in ["University", "College", "School", "小学校", "中学校", "高校", "大学", "学園"]):
                temp_entries.append({
                    'team': entry['text'].strip(),
                    'start': "",
                    'end': "",
                    'year': entry['year'],
                    'raw': True
                })

    if not temp_entries:
        return ""

    # 同一チームの連続・重複期間を統合
    merged = []
    
    def get_base_team_name(t):
        # リンクがあれば剥がす
        t = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', t)
        # 括弧（全角半角両方）を剥がす
        t = re.sub(r'[\(（].*?[\)）]', '', t)
        t = t.strip()
        
        # 特定のチーム名の名寄せ（より網羅的な正規化）
        # 例: Auckland と Blues が交互にくるケースへの対応
        name_map = {
            'Auckland': 'Auckland Blues',
            'Blues': 'Auckland Blues',
            'Wellington': 'Wellington Lions',
            'Lions': 'Wellington Lions',
            'Canterbury': 'Crusaders',
            'Waikato': 'Chiefs',
            'Otago': 'Highlanders',
            'Taranaki': 'Chiefs'
        }
        for k, v in name_map.items():
            if t == k: return v
        return t

    for entry in temp_entries:
        if not merged:
            merged.append(entry)
            continue
        
        last = merged[-1]
        
        # 生のチーム名ではなく、正規化した名前で比較
        base_last = get_base_team_name(last['team'])
        base_curr = get_base_team_name(entry['team'])

        if base_last == base_curr and not entry.get('raw') and not last.get('raw'):
            # 期間を統合
            # 開始年: 最小値を取る
            if last['start'] and entry['start']:
                try:
                    l_s = int(last['start']) if last['start'].isdigit() else 9999
                    e_s = int(entry['start']) if entry['start'].isdigit() else 9999
                    if e_s < l_s: last['start'] = str(e_s)
                except: pass
            elif entry['start']:
                last['start'] = entry['start']
            
            # 終了年: 最大値を取る、または空（現在進行）
            if not last['end'] or not entry['end']:
                last['end'] = ""
            else:
                try:
                    l_e = int(last['end']) if last['end'].isdigit() else 0
                    e_e = int(entry['end']) if entry['end'].isdigit() else 0
                    last['end'] = str(max(l_e, e_e))
                except: pass
            
            # year (判定用) も最新に更新
            last['year'] = max(last['year'], entry['year'])
        else:
            merged.append(entry)

    lines = []
    max_year = max(e['year'] for e in merged) if merged else 0
    
    for entry in merged:
        if entry.get('raw'):
            linked = get_team_link(entry['team'], include_flag=True)
            lines.append(f"- {linked}")
            continue

        linked_team = get_team_link(entry['team'], include_flag=True)
        start_p = entry['start']
        end_p = entry['end']
        
        # 現在進行形の判定: 終了年が空、または2025年以降であれば現在進行中とみなす。
        # また、最後のエントリ（最新）であることを重視する。
        is_current = (not end_p or (end_p.isdigit() and int(end_p) >= CURRENT_YEAR - 1))
        
        if is_current and entry == merged[-1]:
            period = f"{start_p} - "
        elif end_p and end_p != start_p:
            period = f"{start_p} - {end_p}"
        elif start_p:
            period = start_p
        else:
            period = ""

        if period:
            lines.append(f"- {linked_team} ({period})")
        else:
            lines.append(f"- {linked_team}")

    return "\n".join(lines)

def generate_slug(name_en, player_id, scraped_url=""):
    if scraped_url and 'all.rugby/player/' in scraped_url:
        url_id = scraped_url.split('/')[-1]
        if url_id: return url_id
        
    if not name_en or str(name_en).lower() == 'nan': return f"player-{player_id}"
    slug = str(name_en).lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    return f"{slug}-{player_id}"

def main():
    print(f"Starting player generation from {CSV_PATH}...")
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} not found.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for f in glob.glob(os.path.join(OUTPUT_DIR, '*.md')): os.remove(f)
    
    with open(CSV_PATH, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    generated_count = 0
    skipped_count = 0
    processed_keys = set()
    
    for i, row in enumerate(rows):
        try:
            name_en = (row.get('英語名') or row.get('name_en') or '').strip()
            # 優先順位: 新設カタカナ > 選手名 > name_ja > name_en
            name_ja = (row.get('選手名_カタカナ') or row.get('選手名') or row.get('name_ja') or '').strip() or name_en
            birth_date = (row.get('生年月日') or row.get('birth_date') or '').strip()
            team_raw = (row.get('所属チーム') or row.get('team') or '').strip()
            current_team = clean_team_name(team_raw)
            scraped_url = (row.get('Scraped_Url') or row.get('url') or '').strip()
            
            # 重複排除キー
            dedup_key = scraped_url if scraped_url else (name_en.lower(), birth_date, current_team.lower())
            if dedup_key in processed_keys:
                skipped_count += 1
                continue
            processed_keys.add(dedup_key)
            
            slug = generate_slug(name_en, i + 1, scraped_url)
            
            team_info = get_team_info(current_team)
            if team_info:
                current_team = team_info['jp']
                league = team_info['league']
            else:
                league = ""
            
            # Normalize league name
            if league == 'leagueone': league = 'league-one'
            if not league:
                if 'league-one' in scraped_url: league = 'leagueone'
                elif 'super-rugby' in scraped_url: league = 'super-rugby'
                elif 'unitedrugby' in scraped_url: league = 'urc'
                elif 'top14' in scraped_url: league = 'top14'
                else:
                    league = find_league_by_team(current_team)
                
                if not league and any(t in current_team for t in ['トゥールーズ', 'ボルドー', 'ラ・ロシェル', 'ラシン92', 'トゥーロン', 'モンペリエ', 'リヨン', 'カストル', 'アヴィロン・バイヨンヌ', 'セクション・パロワーズ', 'スタッド・フランセ', 'クレルモン', 'ペルピニャン', 'ヴァンヌ', 'ポー', 'バイヨンヌ']):
                    league = 'top14'
            
            age = calculate_age(birth_date)
            
            # URC はデータとしては保持するが、サイトには掲載しない方針
            if league == 'urc':
                skipped_count += 1
                continue
            
            # リーグ名の正規化 (leagueone -> league-one)
            if league == 'leagueone':
                league = 'league-one'
                
            career_md = format_career_md(row.get('Full_Career') or row.get('キャリア遍歴', ''), current_team, name_en)
            
            l_caps_raw = str(row.get('リーグワンキャップ数', '') or '0')
            l_caps_match = re.search(r'(\d+)', l_caps_raw)
            league_one_caps = l_caps_match.group(1) if l_caps_match else "0"
            
            c_val = str(row.get('代表キャップ数', '') or row.get('International_Caps', '')).strip()
            # もし c_val が URL の形式なら空にする (誤混入対策)
            if c_val.startswith('http'):
                c_val = ""
            
            caps_match = re.search(r'(.+?)代表', c_val)
            country = re.sub(r'[\(（].*$', '', caps_match.group(1).strip()) if caps_match else ""
            if not country:
                country = row.get('International_Caps', '') or row.get('国籍', '')
            
            cat_v = (row.get('カテゴリ', '') or '').strip()
            # カテゴリーは League One 専用の項目であるため、league-one の場合のみ表示する
            if league in ['league-one', 'leagueone'] and cat_v in ['A', 'B', 'C']:
                category = f"カテゴリー{cat_v}"
            else:
                category = ""
            
            # ディビジョンの推論
            division = ""
            if league == 'leagueone':
                division = "Division 1"
            
            has_scores = "true" if league in ['leagueone', 'top14'] else "false"
            
            # Joined Year
            joined_year = "null"
            years = re.findall(r'\((\d{4})', career_md.split('\n')[-1] if career_md else "")
            if years: joined_year = years[-1]

            # 追加属性 (SNSなど)
            instagram = (row.get('SNS_Instagram') or '').strip()
            twitter = (row.get('SNS_Twitter') or '').strip()
            facebook = (row.get('SNS_Facebook') or '').strip()
            nationality = (row.get('国籍') or '').strip()

            content = f"""---
title: "{name_ja}"
name_en: "{name_en}"
position: "{row.get("ポジション", "") or ""}"
team: "{current_team}"
height: "{row.get("身長", "") or ""}"
weight: "{row.get("体重", "") or ""}"
birth_date: "{birth_date}"
age: {age if age is not None else "null"}
high_school: "{row.get("高校", "") or ""}"
university: "{row.get("大学", "") or ""}"
caps: "{c_val}"
league_one_caps: "{league_one_caps}"
country: "{country}"
nationality: "{nationality}"
category: "{category}"
division: "{division}"
league: "{league}"
joined_year: {joined_year}
has_scores: {has_scores}
instagram: "{instagram}"
twitter: "{twitter}"
facebook: "{facebook}"
---

{career_md}
"""
            file_path = os.path.join(OUTPUT_DIR, f"{slug}.md")
            with open(file_path, 'w', encoding='utf-8') as wf: wf.write(content)
            generated_count += 1
            
        except Exception as e:
            print(f"Error processing row {i+1} ({row.get('英語名')}): {e}")

    print(f"SUCCESS: Generated {generated_count} players. (Skipped {skipped_count} duplicates)")

if __name__ == "__main__":
    main()
