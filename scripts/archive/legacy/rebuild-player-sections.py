#!/usr/bin/env python3
"""
Rebuild player sections in all 77 team articles using CSV as authoritative source.
Keeps frontmatter + non-player sections intact, replaces player sections with CSV data.
"""
import csv
import os
import re
from collections import defaultdict

CSV_PATH = '/Users/ktamatzmoto/Desktop/rugbypicks/data_sources/final_master_data_v27_normalized.csv'
TEAMS_DIR = '/Users/ktamatzmoto/Desktop/rugbypicks/src/content/teams'

# article slug -> CSV Current_Team value(s)
TEAM_MAP = {
    # League One (match Current_Team containing team name)
    ('league-one', 'chugoku-electric-red-regulions'): ['中国電力レッドレグリオンズ（2025-26）'],
    ('league-one', 'hanazono-kintetsu-liners'): ['花園近鉄ライナーズ（2025-26）'],
    ('league-one', 'hino-red-dolphins'): ['日野レッドドルフィンズ（2025-26）'],
    ('league-one', 'hurricanes'): ['レッドハリケーンズ大阪（2025-26）'],
    ('league-one', 'kamaishi-seawaves'): ['日本製鉄釜石シーウェイブス（2025-26）'],
    ('league-one', 'kobelco-kobe-steelers'): ['コベルコ神戸スティーラーズ（2025-26）'],
    ('league-one', 'kubota-spears-funabashi-tokyo-bay'): ['クボタスピアーズ船橋・東京ベイ（2025-26）'],
    ('league-one', 'kurita-water-gush-akishima'): ['クリタウォーターガッシュ昭島（2025-26）'],
    ('league-one', 'kyuden-voltex'): ['九州電力キューデンヴォルテクス（2025-26）'],
    ('league-one', 'mazda-skyactivs-hiroshima'): ['マツダスカイアクティブズ広島（2025-26）'],
    ('league-one', 'mie-honda-heat'): ['三重ホンダヒート（2025-26）'],
    ('league-one', 'mitsubishi-sagamihara-dynaboars'): ['三菱重工相模原ダイナボアーズ（2025-26）'],
    ('league-one', 'nec-green-rockets-tokatsu'): ['NECグリーンロケッツ東葛（2025-26）'],
    ('league-one', 'ricoh-black-rams-tokyo'): ['リコーブラックラムズ東京（2025-26）'],
    ('league-one', 'ruriro-fukuoka'): ['ルリーロ福岡（2025-26）'],
    ('league-one', 'saitama-panasonic-wild-knights'): ['埼玉パナソニックワイルドナイツ（2025-26）'],
    ('league-one', 'secom-rugguts'): ['狭山セコムラガッツ（2025-26）'],
    ('league-one', 'shimizu-koto-blue-sharks'): ['清水建設江東ブルーシャークス（2025-26）'],
    ('league-one', 'shizuoka-blue-revs'): ['静岡ブルーレヴズ（2025-26）'],
    ('league-one', 'tokyo-suntory-sungoliath'): ['東京サントリーサンゴリアス（2025-26）', '東京サントリーサンゴリアス'],
    ('league-one', 'toyota-shuttles-aichi'): ['豊田自動織機シャトルズ愛知（2025-26）'],
    ('league-one', 'toyota-verblitz'): ['トヨタヴェルブリッツ（2025-26）'],
    ('league-one', 'toshiba-brave-lupus-tokyo'): ['東芝ブレイブルーパス東京（2025-26）'],
    ('league-one', 'urayasu-d-rocks'): ['浦安D-Rocks（2025-26）'],
    ('league-one', 'yakult-levins'): ['ヤクルトレビンズ戸田（2025-26）'],
    ('league-one', 'yokohama-canon-eagles'): ['横浜キヤノンイーグルス（2025-26）'],
    # Super Rugby
    ('super-rugby', 'act-brumbies'): ['Brumbies'],
    ('super-rugby', 'blues'): ['Blues'],
    ('super-rugby', 'chiefs'): ['Chiefs'],
    ('super-rugby', 'crusaders'): ['Crusaders'],
    ('super-rugby', 'fijian-drua'): ['Fijian Drua'],
    ('super-rugby', 'highlanders'): ['Highlanders'],
    ('super-rugby', 'hurricanes'): ['Hurricanes'],
    ('super-rugby', 'moana-pasifika'): ['Moana Pasifika'],
    ('super-rugby', 'nsw-waratahs'): ['Waratahs'],
    ('super-rugby', 'queensland-reds'): ['Reds'],
    ('super-rugby', 'western-force'): ['Western Force'],
    # Top14
    ('top14', 'bayonne'): ['バイヨンヌ'],
    ('top14', 'bordeaux'): ['ボルドー・ベグル'],
    ('top14', 'castres'): ['カストル'],
    ('top14', 'clermont'): ['クレルモン'],
    ('top14', 'la-rochelle'): ['ラ・ロシェル'],
    ('top14', 'lyon'): ['リヨン'],
    ('top14', 'montpellier'): ['モンペリエ'],
    ('top14', 'paris'): ['スタッド・フランセ'],
    ('top14', 'pau'): ['ポー'],
    ('top14', 'perpignan'): ['ペルピニャン'],
    ('top14', 'racing-92'): ['ラシン92'],
    ('top14', 'toulon'): ['トゥーロン'],
    ('top14', 'toulouse'): ['Stade Toulousain', 'トゥールーズ'],
    ('top14', 'vannes'): ['ヴァンヌ'],
    # URC
    ('urc', 'benetton-rugby-trevise'): ['Trévise'],
    ('urc', 'cardiff-rugby'): ['Cardiff'],
    ('urc', 'connacht-rugby'): ['Connacht'],
    ('urc', 'dhl-stormers'): ['Stormers'],
    ('urc', 'dragons-rugby'): ['Dragons'],
    ('urc', 'edinburgh-rugby'): ['Edimbourg'],
    ('urc', 'emirates-lions'): ['Lions'],
    ('urc', 'glasgow-warriors'): ['Glasgow'],
    ('urc', 'hollywoodbets-sharks'): ['Sharks'],
    ('urc', 'leinster-rugby'): ['Leinster'],
    ('urc', 'munster-rugby'): ['Munster'],
    ('urc', 'ospreys'): ['Ospreys'],
    ('urc', 'scarlets'): ['Scarlets'],
    ('urc', 'ulster-rugby'): ['Ulster'],
    ('urc', 'vodacom-bulls'): ['Bulls'],
    ('urc', 'zebre-parma'): ['Zebre'],
    # Premiership
    ('premiership', 'bath-rugby'): ['Bath Rugby'],
    ('premiership', 'bristol-bears'): ['Bristol Bears'],
    ('premiership', 'exeter-chiefs'): ['Exeter Chiefs'],
    ('premiership', 'gloucester-rugby'): ['Gloucester Rugby'],
    ('premiership', 'harlequins'): ['Harlequins'],
    ('premiership', 'leicester-tigers'): ['Leicester Tigers'],
    ('premiership', 'newcastle-falcons'): ['Newcastle Falcons'],
    ('premiership', 'northampton-saints'): ['Northampton Saints'],
    ('premiership', 'sale-sharks'): ['Sale Sharks'],
    ('premiership', 'saracens'): ['Saracens'],
}

# Headings that mark the start of player sections (replace from here onwards)
PLAYER_HEADING_RE = re.compile(
    r'^## (?:'
    r'[4-9][\.　 ]'        # ## 4. ## 5. etc (LO style, section 4+)
    r'|チームを牽引'
    r'|チームを支える'
    r'|日本との関わり'
    r'|リーグワンゆかりの選手'
    r'|各国代表'
    r'|期待の新星'
    r'|歴代レジェンド'
    r'|今シーズン'
    r'|現役選手'
    r')'
)

POS_ORDER = ['PR', 'HO', 'LO', 'FL/No8', 'FL', 'No8', 'SH', 'SO', 'CTB', 'UTB', 'WTB', 'FB']

def pos_key(pos):
    for i, p in enumerate(POS_ORDER):
        if pos == p or pos.startswith(p):
            return i
    return 99

def build_player_section(players, is_lo):
    players = sorted(players, key=lambda p: pos_key(p['Position']))
    rep = [p for p in players if p['Representative_Caps'].strip()]
    others = [p for p in players if not p['Representative_Caps'].strip()]

    lines = ['## 現役選手（2025-26シーズン）', '']

    def fmt(p):
        name = p['Full_Name'].strip() or p['Player_Name'].strip()
        pos = p['Position'].strip()
        caps = p['Representative_Caps'].strip()
        lo_caps = p['League_One_Caps'].strip()
        parts = [f'**{name}**（{pos}）']
        if caps:
            parts.append(caps)
        if is_lo and lo_caps and lo_caps not in ('', '0', '0.0'):
            parts.append(f'リーグワン{int(float(lo_caps))}試合')
        return '、'.join(parts)

    if rep:
        lines += ['### 代表経験あり', '']
        lines += [fmt(p) for p in rep]
        lines.append('')
    if others:
        lines += ['### その他在籍選手', '']
        lines += [fmt(p) for p in others]
        lines.append('')

    return '\n'.join(lines)

def find_split_idx(lines):
    for i, line in enumerate(lines):
        if PLAYER_HEADING_RE.match(line.rstrip()):
            return i
    return None

# Load CSV: build lookup (team_name -> [players])
players_by_team = defaultdict(list)
with open(CSV_PATH, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        tm = row['Current_Team'].strip()
        if tm:
            players_by_team[tm].append(row)

updated = 0
no_players = []

for (league_dir, slug), csv_names in TEAM_MAP.items():
    filepath = os.path.join(TEAMS_DIR, league_dir, f'{slug}.md')
    if not os.path.exists(filepath):
        print(f'MISSING: {filepath}')
        continue

    # Gather players for this team
    players = []
    for name in csv_names:
        players.extend(players_by_team.get(name, []))

    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines()
    split_idx = find_split_idx(lines)

    if split_idx is None:
        print(f'NO SPLIT POINT: {filepath}')
        continue

    keep = lines[:split_idx]
    # Remove trailing blank lines from kept section
    while keep and keep[-1].strip() == '':
        keep.pop()

    is_lo = league_dir == 'league-one'

    if players:
        new_section = build_player_section(players, is_lo)
    else:
        no_players.append(f'{league_dir}/{slug}')
        new_section = '## 現役選手（2025-26シーズン）\n\nデータなし\n'

    new_content = '\n'.join(keep) + '\n\n' + new_section
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    updated += 1

print(f'\n完了: {updated}件更新')
if no_players:
    print(f'選手データなし ({len(no_players)}件):')
    for t in no_players:
        print(f'  {t}')
