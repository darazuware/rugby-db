import json
import os
import re
import unicodedata

# チーム名からスラッグとリーグを特定するためのマッピング
# 本来は JSON から読み込むのが理想的だが、まずは主要なものをハードコードし、
# 段階的に JSON 連携に移行する。

# チーム名日本語化マッピングの読み込み
TEAM_NAMES_JP = {}
json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'team_names_jp.json')
if os.path.exists(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        TEAM_NAMES_JP = json.load(f)

# ディビジョン情報の読み込み
TEAMS_DATA = []
teams_json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'teams.json')
if os.path.exists(teams_json_path):
    with open(teams_json_path, 'r', encoding='utf-8') as f:
        TEAMS_DATA = json.load(f)

def get_division_from_teams(team_name):
    """teams.json からチームの Division を取得する"""
    for t in TEAMS_DATA:
        if t.get('team_name') == team_name:
            div = t.get('division', '')
            # "Division 1" -> "D1"
            match = re.search(r'Division (\d+)', div)
            if match:
                return f"D{match.group(1)}"
            return div
    return ""

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
        def slugify_canonical(text):
            if not text: return ""
            # Normalize unicode to remove accents
            text = unicodedata.normalize('NFD', str(text)).encode('ascii', 'ignore').decode('utf-8')
            text = text.lower()
            text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
            # Overrides for consistency
            overrides = {
                "racing-92": "racing-92",
                "stade-francais": "paris",
                "toulousain": "toulouse",
                "rochelais": "la-rochelle",
                "bordeaux": "bordeaux",
                "toulonnais": "toulon",
                "paloise": "pau",
                "clermont": "clermont",
                "montpellier": "montpellier",
                "highlanders": "highlanders",
                "hurricanes": "hurricanes",
                "crusaders": "crusaders",
                "chiefs": "chiefs",
                "blues": "blues",
                "red-hurricanes": "hurricanes",
                "wild-knights": "saitama-panasonic-wild-knights",
                "sungoliath": "tokyo-suntory-sungoliath",
                "brave-lupus": "toshiba-brave-lupus-tokyo",
                "verblitz": "toyota-verblitz"
            }
            for k, v in overrides.items():
                if k in text: return v
            return text

        slug = slugify_canonical(en_name)
        
        div = get_division_from_teams(data['jp'])
        mapping_data = {
            "league": normalized_league, 
            "slug": slug, 
            "jp": data['jp'], 
            "flag": data['flag'], 
            "country": data['country'],
            "division": div
        }
        TEAM_MAPPING[en_name] = mapping_data
        TEAM_MAPPING[data['jp']] = mapping_data
        
        # エイリアス（スクレイピング名など）を登録
        for alias in data.get('aliases', []):
            TEAM_MAPPING[alias] = mapping_data
            
        # カッコ内の名前でも引けるようにする（例：ポー）
        if "（" in data['jp']:
            short_jp = data['jp'].split('（')[0]
            TEAM_MAPPING[short_jp] = mapping_data

TEAM_INFO_CACHE = {}

def get_team_info(team_name):
    """チーム名からメタ情報（リーグ、スラッグ、日本語名等）を取得する"""
    if not team_name: return None
    
    # 前後の空白を除去
    team_name = team_name.strip()
    
    if team_name in TEAM_INFO_CACHE:
        return TEAM_INFO_CACHE[team_name]
    
    # 1. 完全一致を優先 (TEAM_MAPPING は辞書なので O(1))
    if team_name in TEAM_MAPPING:
        res = TEAM_MAPPING[team_name]
        TEAM_INFO_CACHE[team_name] = res
        return res
    
    # 2. 括弧（全角半角）を外して再試行
    short_name = re.sub(r'[\(（].*?[\)）]', '', team_name).strip()
    if short_name != team_name and short_name in TEAM_MAPPING:
        res = TEAM_MAPPING[short_name]
        TEAM_INFO_CACHE[team_name] = res
        return res

    # 3. 既知の英語名・日本語名のエイリアスを考慮しても見つからない場合は None
    # 以前のループによる「部分一致」は、長いキャリア履歴文字列に対して非常に遅いため削除
    TEAM_INFO_CACHE[team_name] = None
    return None

def get_team_link(team_name, include_flag=False):
    """チーム名を Markdown リンクに変換する。日本語名を優先表示。include_flag=Trueで国旗を付与"""
    info = get_team_info(team_name)
    if info:
        # Rebels (活動休止) はリンクしない
        display_name = info.get('jp', team_name)
        
        # 国旗の付与
        flag = info.get('flag', '') if include_flag else ''
        prefix = f"{flag} " if flag else ""
        
        # Division 表記の追加 (League One のみ)
        div_suffix = ""
        if info.get('league') == 'league-one' and info.get('division'):
            div_suffix = f" [{info['division']}]"
            
        if info.get('slug') == 'melbourne-rebels':
            return f"{prefix}{display_name}{div_suffix}"
            
        return f"{prefix}[{display_name}](/teams/{info['league']}/{info['slug']}){div_suffix}"
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
