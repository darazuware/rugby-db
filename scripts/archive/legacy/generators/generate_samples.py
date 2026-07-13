import json
import os
import random
import re
from generate_player_pages import generate_player_page
from generate_league_pages import generate_league_page_deep, clean_team_name

# Load data
print("Loading data for samples...")
with open('data/unified_player_database_final.json', 'r', encoding='utf-8') as f:
    players = json.load(f)
if isinstance(players, dict):
    players = list(players.values())

with open('data/rugby_leagues.json', 'r', encoding='utf-8') as f:
    leagues = json.load(f)

# Comprehensive Mapping
DIV2_TEAMS = ['浦安D-Rocks', '豊田自動織機シャトルズ愛知', 'NECグリーンロケッツ東葛', '九州電力キューデンヴォルテクス', 'レッドハリケーンズ大阪', '日本製鉄釜石シーウェイブス']
DIV3_TEAMS = ['日野レッドドルフィンズ', '清水建設江東ブルーシャークス', 'クリタウォーターガッシュ昭島', '中国電力レッドレグリオンズ', 'マツダスカイアクティブズ広島', 'ヤクルトレビンズ戸田', 'ルリーロ福岡']

OVERSEAS_TEAM_MAP = {
    # Super Rugby
    'Crusaders': 'スーパーラグビー', 'Blues': 'スーパーラグビー', 'Hurricanes': 'スーパーラグビー', 
    'Chiefs': 'スーパーラグビー', 'Highlanders': 'スーパーラグビー', 'Brumbies': 'スーパーラグビー',
    'Reds': 'スーパーラグビー', 'Waratahs': 'スーパーラグビー', 'Western Force': 'スーパーラグビー', 
    'Melbourne Rebels': 'スーパーラグビー', 'Moana Pasifika': 'スーパーラグビー', 'Fijian Drua': 'スーパーラグビー',
    # Premiership
    'Northampton Saints': 'プレミアシップ', 'Saracens': 'プレミアシップ', 'Bath Rugby': 'プレミアシップ',
    'Sale Sharks': 'プレミアシップ', 'Exeter Chiefs': 'プレミアシップ', 'Harlequins': 'プレミアシップ',
    'Leicester Tigers': 'プレミアシップ', 'Bristol Bears': 'プレミアシップ', 'Gloucester': 'プレミアシップ',
    # URC
    'Leinster': 'URC', 'Munster': 'URC', 'Stormers': 'URC', 'Bulls': 'URC',
    'Glasgow Warriors': 'URC', 'Connacht': 'URC', 'Ulster': 'URC', 'Edinburgh': 'URC',
    'Sharks': 'URC', 'Lions': 'URC', 'Benetton': 'URC', 'Ospreys': 'URC', 'Scarlets': 'URC',
    # Pro D2
    'Béziers': 'プロD2', 'Vannes': 'プロD2', 'Brive': 'プロD2', 'Agen': 'プロD2', 'Mont-de-Marsan': 'プロD2',
    'Nevers': 'プロD2', 'Provence': 'プロD2',
    # Six Nations / National Teams
    'England': 'シックスネーションズ', 'France': 'シックスネーションズ', 'Ireland': 'シックスネーションズ',
    'Scotland': 'シックスネーションズ', 'Wales': 'シックスネーションズ', 'Italy': 'シックスネーションズ',
    'All Blacks': 'ラグビーチャンピオンシップ', 'New Zealand': 'ラグビーチャンピオンシップ',
    'Springboks': 'ラグビーチャンピオンシップ', 'South Africa': 'ラグビーチャンピオンシップ',
    'Wallabies': 'ラグビーチャンピオンシップ', 'Australia': 'ラグビーチャンピオンシップ',
    'Pumas': 'ラグビーチャンピオンシップ', 'Argentina': 'ラグビーチャンピオンシップ'
}

# Helper to normalize league names for matching
def norm_league(name):
    if not name: return ""
    return re.sub(r'[\s\-_]', '', str(name)).lower()

# Group players by league
league_players = {}
for p in players:
    l_raw = p.get('league')
    t_raw = str(p.get('team', ''))
    hist = str(p.get('career_history', ''))
    
    # 1. League One Divisions
    if p.get('source') == 'league_one':
        l_raw = "Japan Rugby League One Division 1"
        for dt in DIV2_TEAMS:
            if dt in t_raw: l_raw = "Japan Rugby League One Division 2"; break
        for dt in DIV3_TEAMS:
            if dt in t_raw: l_raw = "Japan Rugby League One Division 3"; break
    
    # 2. Top 14
    if p.get('source') == 'top_14' or l_raw == 'Top 14':
        l_raw = "TOP 14"

    # 3. Overseas by Team or History
    if not l_raw or l_raw == 'Unknown':
        for team_key, mapped_league in OVERSEAS_TEAM_MAP.items():
            if team_key in t_raw or team_key in hist:
                l_raw = mapped_league
                break
    
    l_norm = norm_league(l_raw)
    if l_norm not in league_players:
        league_players[l_norm] = []
    league_players[l_norm].append(p)

print("Generating samples...")
for l in leagues:
    l_name_ja = l['name_ja']
    l_name_en = l['name']
    l_slug = l['url'].split('/')[-1]
    
    print(f"  League: {l_name_ja} ({l_slug})")
    
    # Matching
    l_norm_ja = norm_league(l_name_ja)
    l_norm_en = norm_league(l_name_en)
    target_players = league_players.get(l_norm_ja, league_players.get(l_norm_en, []))

    if not target_players:
        print(f"    Warning: No players found for league {l_name_ja}")
        continue

    # 1. League Page
    teams_in_league = []
    seen_teams = set()
    for p in target_players:
        t_name = clean_team_name(p.get('team'))
        if t_name and t_name not in seen_teams:
            seen_teams.add(t_name)
            teams_in_league.append({'team_name': t_name, 'division': l_name_ja})
    
    generate_league_page_deep(l_name_ja, teams=teams_in_league, is_top=True, league_slug=l_slug)
    
    # 2. Sample Players (Pick 2 rich)
    rich_players = [p for p in target_players if p.get('height') and str(p.get('height')) != '-' and p.get('weight') and str(p.get('weight')) != '-']
    if len(rich_players) < 2: rich_players = target_players
    
    sample_players = random.sample(rich_players, min(2, len(rich_players)))
    for p in sample_players:
        p_name = p.get('name_ja') or p.get('name_en')
        print(f"    Player: {p_name} ({p.get('id')})")
        generate_player_page(p)

print("\n✓ Sample generation complete!")
