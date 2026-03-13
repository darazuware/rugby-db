import json
import os
import re

# チーム名からスラッグとリーグを特定するためのマッピング
# 本来は JSON から読み込むのが理想的だが、まずは主要なものをハードコードし、
# 段階的に JSON 連携に移行する。

# チーム名日本語化マッピングの読み込み
TEAM_NAMES_JP = {}
json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'team_names_jp.json')
if os.path.exists(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        TEAM_NAMES_JP = json.load(f)

TEAM_MAPPING = {
    # League One (主要)
    "埼玉パナソニックワイルドナイツ": {"league": "league-one", "slug": "saitama-panasonic-wildknights"},
    "東京サントリーサンゴリアス": {"league": "league-one", "slug": "tokyo-suntory-sungoliath"},
    "横浜キヤノンイーグルス": {"league": "league-one", "slug": "yokohama-canon-eagles"},
    "東芝ブレイブルーパス東京": {"league": "league-one", "slug": "toshiba-brave-lupus-tokyo"},
    "クボタスピアーズ船橋・東京ベイ": {"league": "league-one", "slug": "kubota-spears-funabashi-tokyo-bay"},
    "静岡ブルーレヴズ": {"league": "league-one", "slug": "shizuoka-bluerevs"},
    "トヨタヴェルブリッツ": {"league": "league-one", "slug": "toyota-verblitz"},
    "コベルコ神戸スティーラーズ": {"league": "league-one", "slug": "kobelco-kobe-steelers"},
    "花園近鉄ライナーズ": {"league": "league-one", "slug": "hanazono-kintetsu-liners"},
    "三菱重工相模原ダイナボアーズ": {"league": "league-one", "slug": "mitsubishi-sagamihara-dynaboars"},
    "リコーブラックラムズ東京": {"league": "league-one", "slug": "ricoh-blackrams-tokyo"},
    "三重ホンダヒート": {"league": "league-one", "slug": "mie-honda-heat"},
}

# JSONマッピングを TEAM_MAPPING に統合
for league, teams in TEAM_NAMES_JP.items():
    # リーグ名の正規化
    normalized_league = league
    if league == 'leagueone': normalized_league = 'league-one'
    
    for en_name, data in teams.items():
        # 英語名ベースのスラッグ生成
        slug = en_name.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
        # 特殊な固有名詞や既存のスラッグがある場合はそちらを優先
        if en_name == "Racing 92": slug = "racing-92"
        if en_name == "Stade Français Paris": slug = "paris"
        if "Benetton" in en_name: slug = "benetton"
        if "Toulousain" in en_name: slug = "toulouse"
        if "Rochelais" in en_name: slug = "la-rochelle"
        if "Bordeaux" in en_name: slug = "bordeaux"
        if "Toulonnais" in en_name: slug = "toulon"
        if "Paloise" in en_name: slug = "pau"
        if "Clermont" in en_name: slug = "clermont"
        if "Highlanders" in en_name: slug = "highlanders"
        if "Hurricanes" in en_name: slug = "hurricanes"
        if "Crusaders" in en_name: slug = "crusaders"
        if "Chiefs" in en_name: slug = "chiefs"
        if "Blues" in en_name: slug = "blues"
        if "Ospreys" in en_name: slug = "ospreys"
        if "Montpellier" in en_name: slug = "montpellier"
        if "Lyon" in en_name: slug = "lyon"
        if "Racing 92" in en_name: slug = "racing-92"
        if "Stade Français" in en_name: slug = "paris"
        if "Castres" in en_name: slug = "castres"
        if "Perpignan" in en_name: slug = "perpignan"
        if "Bayonne" in en_name: slug = "bayonne"
        if "Vannes" in en_name: slug = "vannes"
        
        mapping_data = {"league": normalized_league, "slug": slug, "jp": data['jp'], "flag": data['flag'], "country": data['country']}
        TEAM_MAPPING[en_name] = mapping_data
        TEAM_MAPPING[data['jp']] = mapping_data
        
        # エイリアス（スクレイピング名など）を登録
        for alias in data.get('aliases', []):
            TEAM_MAPPING[alias] = mapping_data
            
        # カッコ内の名前でも引けるようにする（例：ポー）
        if "（" in data['jp']:
            short_jp = data['jp'].split('（')[0]
            TEAM_MAPPING[short_jp] = mapping_data

def get_team_info(team_name):
    """チーム名からメタ情報（リーグ、スラッグ、日本語名等）を取得する"""
    for key, data in TEAM_MAPPING.items():
        if key == team_name or key in team_name or team_name in key:
            return data
    return None

def get_team_link(team_name, include_flag=False):
    """チーム名を Markdown リンクに変換する。日本語名を優先表示。URCは除外。include_flag=Trueで国旗を付与"""
    info = get_team_info(team_name)
    if info:
        # URC や Rebels (活動休止) はリンクしない
        display_name = info.get('jp', team_name)
        
        # 国旗の付与
        flag = info.get('flag', '') if include_flag else ''
        prefix = f"{flag} " if flag else ""
        
        if info.get('league') == 'urc' or info.get('slug') == 'melbourne-rebels':
            return f"{prefix}{display_name}"
            
        return f"{prefix}[{display_name}](/teams/{info['league']}/{info['slug']})"
    return team_name

def linkify_career(career_text):
    """キャリア遍歴のテキスト内のチーム名をリンク化する"""
    if not career_text:
        return ""
    
    # 箇条書きの各行を処理
    lines = career_text.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('- '):
            content = line[2:]
            # チーム名 (期間) の形式を想定
            match = re.search(r'^(.+?) \((.+)\)$', content)
            if match:
                team = match.group(1).strip()
                period = match.group(2).strip()
                linked_team = get_team_link(team)
                new_lines.append(f"- {linked_team} ({period})")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines)
