#!/usr/bin/env python3
"""
Wikipedia情報を基に海外51チームの記事前半（概要・歴史）を再生成する。
フロントマター + Wikipedia生成セクション + 既存の現役選手セクション（CSV由来）を結合。
"""
import subprocess
import urllib.request
import urllib.parse
import json
import os
import time
import ssl

SSL_CTX = ssl._create_unverified_context()
TEAMS_DIR = '/Users/ktamatzmoto/Desktop/rugbypicks/src/content/teams'

# (league_dir, slug, ja_wiki_name, en_wiki_name, league_label, team_display)
TEAMS = [
    # Super Rugby
    ('super-rugby', 'act-brumbies',       'ブランビーズ',               'Brumbies (rugby union)',        'スーパーラグビー・パシフィック', 'ACTブランビーズ'),
    ('super-rugby', 'blues',              'ブルーズ (ラグビーユニオン)', 'Blues (Super Rugby)',           'スーパーラグビー・パシフィック', 'ブルーズ'),
    ('super-rugby', 'chiefs',             'チーフス (ラグビー)',         'Chiefs (Super Rugby)',          'スーパーラグビー・パシフィック', 'チーフス'),
    ('super-rugby', 'crusaders',          'クルセイダーズ (ラグビー)',   'Crusaders (rugby union)',       'スーパーラグビー・パシフィック', 'クルセイダーズ'),
    ('super-rugby', 'fijian-drua',        'フィジアン・ドルア',          'Fijian Drua',                  'スーパーラグビー・パシフィック', 'フィジアン・ドルア'),
    ('super-rugby', 'highlanders',        'ハイランダーズ (ラグビー)',   'Highlanders (rugby union)',    'スーパーラグビー・パシフィック', 'ハイランダーズ'),
    ('super-rugby', 'hurricanes',         'ハリケーンズ (ラグビー)',     'Hurricanes (rugby union)',     'スーパーラグビー・パシフィック', 'ハリケーンズ'),
    ('super-rugby', 'moana-pasifika',     'モアナ・パシフィカ',          'Moana Pasifika',               'スーパーラグビー・パシフィック', 'モアナ・パシフィカ'),
    ('super-rugby', 'nsw-waratahs',       'NSTワラターズ',              'NSW Waratahs',                 'スーパーラグビー・パシフィック', 'NSTワラターズ'),
    ('super-rugby', 'queensland-reds',    'クイーンズランド・レッズ',    'Queensland Reds',              'スーパーラグビー・パシフィック', 'クイーンズランド・レッズ'),
    ('super-rugby', 'western-force',      'ウエスタン・フォース',        'Western Force',                'スーパーラグビー・パシフィック', 'ウエスタン・フォース'),
    # Top14
    ('top14', 'bayonne',     'アビロン・バイヨンヌ',         'Aviron Bayonnais',          'トップ14', 'バイヨンヌ'),
    ('top14', 'bordeaux',    'ユニオン・ボルドー・ベグル',   'Union Bordeaux Bègle',     'トップ14', 'ボルドー・ベグル'),
    ('top14', 'castres',     'カストル・オリンピック',       'Castres Olympique',         'トップ14', 'カストル・オリンピック'),
    ('top14', 'clermont',    'クレルモン・オーヴェルニュ',   'Clermont Auvergne',         'トップ14', 'クレルモン・オーヴェルニュ'),
    ('top14', 'la-rochelle', 'スタッド・ロシェレ',           'Stade Rochelais',           'トップ14', 'ラ・ロシェル'),
    ('top14', 'lyon',        'リヨンOU',                    'Lyon OU',                   'トップ14', 'リヨン'),
    ('top14', 'montpellier', 'モンペリエ・エロー・ラグビー', 'Montpellier Hérault Rugby', 'トップ14', 'モンペリエ'),
    ('top14', 'paris',       'スタッド・フランセ',           'Stade Français',            'トップ14', 'スタッド・フランセ・パリ'),
    ('top14', 'pau',         'セクション・パロワーズ',       'Section Paloise',           'トップ14', 'セクション・パロワーズ（ポー）'),
    ('top14', 'perpignan',   'USAペルピニャン',              'USA Perpignan',             'トップ14', 'USA・ペルピニャン'),
    ('top14', 'racing-92',   'ラシン92',                    'Racing 92',                 'トップ14', 'ラシン92'),
    ('top14', 'toulon',      'RCトゥーロン',                'RC Toulon',                 'トップ14', 'RCトゥーロン'),
    ('top14', 'toulouse',    'スタッド・トゥールーザン',     'Stade Toulousain',          'トップ14', 'スタッド・トゥールーザン'),
    ('top14', 'vannes',      'ラグビー・クラブ・ヴァンヌ',   'Rugby Club Vannes',         'トップ14', 'ヴァンヌ'),
    # URC
    ('urc', 'benetton-rugby-trevise', 'ベネットン・ラグビー', 'Benetton Rugby',          'URC（ユナイテッド・ラグビー・チャンピオンシップ）', 'ベネットン・トレヴィーゾ'),
    ('urc', 'cardiff-rugby',          'カーディフ・ラグビー', 'Cardiff Rugby',            'URC', 'カーディフ・ラグビー'),
    ('urc', 'connacht-rugby',         'コナクト・ラグビー',   'Connacht Rugby',           'URC', 'コナクト'),
    ('urc', 'dhl-stormers',           'ストーマーズ',         'Stormers',                 'URC', 'DHL・ストーマーズ'),
    ('urc', 'dragons-rugby',          'ドラゴンズ (ラグビー)','Newport Gwent Dragons',    'URC', 'ドラゴンズ'),
    ('urc', 'edinburgh-rugby',        'エジンバラ・ラグビー', 'Edinburgh Rugby',          'URC', 'エジンバラ'),
    ('urc', 'emirates-lions',         'ライオンズ (ラグビー)','Lions (rugby union)',       'URC', 'エミレーツ・ライオンズ'),
    ('urc', 'glasgow-warriors',       'グラスゴー・ウォリアーズ','Glasgow Warriors',      'URC', 'グラスゴー・ウォリアーズ'),
    ('urc', 'hollywoodbets-sharks',   'シャークス (ラグビー)','Sharks (rugby union)',      'URC', 'ハリウッドベッツ・シャークス'),
    ('urc', 'leinster-rugby',         'レンスター・ラグビー', 'Leinster Rugby',           'URC', 'レンスター'),
    ('urc', 'munster-rugby',          'マンスター・ラグビー', 'Munster Rugby',            'URC', 'マンスター'),
    ('urc', 'ospreys',                'オスプレイズ (ラグビー)','Ospreys (rugby union)',  'URC', 'オスプレイズ'),
    ('urc', 'scarlets',               'スカーレッツ',          'Scarlets',                'URC', 'スカーレッツ'),
    ('urc', 'ulster-rugby',           'アルスター・ラグビー', 'Ulster Rugby',             'URC', 'アルスター'),
    ('urc', 'vodacom-bulls',          'ブルズ (ラグビー)',     'Bulls (rugby union)',      'URC', 'ヴォーダコム・ブルズ'),
    ('urc', 'zebre-parma',            'ゼブレ・ラグビー',     'Zebre Parma',             'URC', 'ゼブレ・パルマ'),
    # Premiership
    ('premiership', 'bath-rugby',          'バース・ラグビー',           'Bath Rugby',           'プレミアシップ', 'バース'),
    ('premiership', 'bristol-bears',       'ブリストル・ラグビー',       'Bristol Bears',        'プレミアシップ', 'ブリストル・ベアーズ'),
    ('premiership', 'exeter-chiefs',       'エクセター・チーフス',       'Exeter Chiefs',        'プレミアシップ', 'エクセター・チーフス'),
    ('premiership', 'gloucester-rugby',    'グロスター・ラグビー',       'Gloucester Rugby',     'プレミアシップ', 'グロスター'),
    ('premiership', 'harlequins',          'ハーレクインズFC',           'Harlequins F.C.',      'プレミアシップ', 'ハーレクインズ'),
    ('premiership', 'leicester-tigers',    'レスター・タイガース',       'Leicester Tigers',     'プレミアシップ', 'レスター・タイガース'),
    ('premiership', 'newcastle-falcons',   'ニューカッスル・ファルコンズ','Newcastle Falcons',   'プレミアシップ', 'ニューカッスル・ファルコンズ'),
    ('premiership', 'northampton-saints',  'ノーサンプトン・セインツ',   'Northampton Saints',   'プレミアシップ', 'ノーサンプトン・セインツ'),
    ('premiership', 'sale-sharks',         'セール・シャークス',         'Sale Sharks',          'プレミアシップ', 'セール・シャークス'),
    ('premiership', 'saracens',            'サラセンズFC',               'Saracens F.C.',        'プレミアシップ', 'サラセンズ'),
]

PROMPT_TEMPLATE = """以下はラグビーチーム「{team}」に関するWikipedia情報です（{lang}版）。

---
{wiki_text}
---

この情報のみを使い、日本語で以下のMarkdownを生成してください。
Wikipedia未記載の情報・推測・補完は禁止。不明な項目は「不明」と書く。

## チーム概要・基本データ

| 項目 | 詳細 |
| :--- | :--- |
| リーグ | {league} |
| 創設年 | （Wikipedia記載の年） |
| 本拠地 | （スタジアム名・都市・国） |
| タイトル歴 | （主要タイトルのみ。なければ「なし」） |

## チームの歴史と特徴

（Wikipedia情報のみで3〜5文。創設経緯・重要な歴史・強みや特徴など。日本語で。）
"""

def fetch_wikipedia(page_name, lang='ja'):
    encoded = urllib.parse.quote(page_name)
    base = f'https://{lang}.wikipedia.org'
    url = (f'{base}/w/api.php?action=query&prop=extracts&explaintext=true'
           f'&titles={encoded}&format=json&exsectionformat=plain')
    req = urllib.request.Request(url, headers={'User-Agent': 'rugbypicks-bot/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10, context=SSL_CTX) as resp:
            data = json.loads(resp.read())
        pages = data['query']['pages']
        page = next(iter(pages.values()))
        if 'missing' in page:
            return None, lang
        text = page.get('extract', '')[:3000]
        return text if text.strip() else None, lang
    except Exception as e:
        return None, lang

def get_wiki_text(ja_name, en_name):
    """ja優先、なければen"""
    text, lang = fetch_wikipedia(ja_name, 'ja')
    if text:
        return text, 'Japanese'
    text, lang = fetch_wikipedia(en_name, 'en')
    if text:
        return text, 'English'
    return None, None

def generate_sections(team, wiki_text, wiki_lang, league):
    prompt = PROMPT_TEMPLATE.format(
        team=team, lang=wiki_lang, wiki_text=wiki_text, league=league
    )
    result = subprocess.run(
        ['claude', '-p', prompt],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()

def get_frontmatter(filepath):
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            return content[:end+3]
    return ''

def get_player_section(filepath):
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    idx = content.find('## 現役選手')
    if idx == -1:
        return ''
    return content[idx:]

def main():
    ok, ng = 0, []
    total = len(TEAMS)

    for i, (league_dir, slug, ja_wiki, en_wiki, league_label, team_display) in enumerate(TEAMS, 1):
        filepath = os.path.join(TEAMS_DIR, league_dir, f'{slug}.md')
        if not os.path.exists(filepath):
            print(f'[{i}/{total}] {team_display} ... MISSING')
            continue

        print(f'[{i}/{total}] {team_display}', end=' ... ', flush=True)

        wiki_text, wiki_lang = get_wiki_text(ja_wiki, en_wiki)
        if not wiki_text:
            print('Wikipedia not found → skip')
            ng.append(slug)
            continue

        sections = generate_sections(team_display, wiki_text, wiki_lang, league_label)
        if not sections:
            print('generation failed → skip')
            ng.append(slug)
            continue

        frontmatter = get_frontmatter(filepath)
        player_section = get_player_section(filepath)

        new_content = frontmatter + '\n\n' + sections + '\n\n' + player_section
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f'OK ({wiki_lang})')
        ok += 1
        time.sleep(1)

    print(f'\n完了: {ok}件成功、{len(ng)}件失敗')
    if ng:
        print('失敗:', ng)

if __name__ == '__main__':
    main()
