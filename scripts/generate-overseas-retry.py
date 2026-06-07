#!/usr/bin/env python3
"""
海外チーム記事の失敗分を再実行 + セコムラガッツ修正
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

# 失敗・未処理チームのみ (league_dir, slug, ja_wiki, en_wiki, league_label, team_display)
TEAMS = [
    # LO: secom-rugguts のみ再実行
    ('league-one', 'secom-rugguts', '狭山セコムラガッツ', '', 'リーグワン', '狭山セコムラガッツ'),

    # SR: Wikipedia名を修正
    ('super-rugby', 'act-brumbies',    '',                           'Brumbies',              'スーパーラグビー・パシフィック', 'ACTブランビーズ'),
    ('super-rugby', 'nsw-waratahs',    'ニューサウスウェールズ・ワラターズ', 'NSW Waratahs',    'スーパーラグビー・パシフィック', 'NSTワラターズ'),

    # Top14: generation failed → 再実行
    ('top14', 'clermont',    '',                       'Clermont Auvergne',        'トップ14', 'クレルモン・オーヴェルニュ'),
    ('top14', 'la-rochelle', 'スタッド・ロシェレ',    'Stade Rochelais',           'トップ14', 'ラ・ロシェル'),
    ('top14', 'lyon',        'リヨンOU',              'Lyon OU',                   'トップ14', 'リヨン'),
    ('top14', 'montpellier', 'モンペリエ・エロー・ラグビー', 'Montpellier Hérault Rugby', 'トップ14', 'モンペリエ'),
    ('top14', 'paris',       'スタッド・フランセ',    'Stade Français',            'トップ14', 'スタッド・フランセ・パリ'),
    ('top14', 'pau',         'セクション・パロワーズ','Section Paloise',            'トップ14', 'セクション・パロワーズ（ポー）'),
    ('top14', 'perpignan',   'USAペルピニャン',       'USA Perpignan',             'トップ14', 'USA・ペルピニャン'),
    ('top14', 'racing-92',   'ラシン92',             'Racing 92',                  'トップ14', 'ラシン92'),
    ('top14', 'toulon',      'RCトゥーロン',          'RC Toulon',                 'トップ14', 'RCトゥーロン'),
    ('top14', 'toulouse',    'スタッド・トゥールーザン', 'Stade Toulousain',        'トップ14', 'スタッド・トゥールーザン'),
    ('top14', 'vannes',      'ラグビー・クラブ・ヴァンヌ', 'Rugby Club Vannes',     'トップ14', 'ヴァンヌ'),

    # URC: generation failed → 再実行
    ('urc', 'benetton-rugby-trevise', 'ベネットン・ラグビー', 'Benetton Rugby',          'URC', 'ベネットン・トレヴィーゾ'),
    ('urc', 'cardiff-rugby',          'カーディフ・ラグビー', 'Cardiff Rugby',            'URC', 'カーディフ・ラグビー'),
    ('urc', 'connacht-rugby',         'コナクト・ラグビー',   'Connacht Rugby',           'URC', 'コナクト'),
    ('urc', 'dhl-stormers',           'ストーマーズ',          'Stormers',                'URC', 'DHL・ストーマーズ'),
    ('urc', 'dragons-rugby',          '',                      'Dragons RFC',             'URC', 'ドラゴンズ'),
    ('urc', 'edinburgh-rugby',        'エジンバラ・ラグビー', 'Edinburgh Rugby',          'URC', 'エジンバラ'),
    ('urc', 'emirates-lions',         'ライオンズ (ラグビー)','Lions (rugby union)',       'URC', 'エミレーツ・ライオンズ'),
    ('urc', 'glasgow-warriors',       'グラスゴー・ウォリアーズ', 'Glasgow Warriors',     'URC', 'グラスゴー・ウォリアーズ'),
    ('urc', 'hollywoodbets-sharks',   'シャークス (ラグビー)','Sharks (rugby union)',      'URC', 'ハリウッドベッツ・シャークス'),
    ('urc', 'leinster-rugby',         'レンスター・ラグビー', 'Leinster Rugby',           'URC', 'レンスター'),
    ('urc', 'munster-rugby',          'マンスター・ラグビー', 'Munster Rugby',            'URC', 'マンスター'),
    ('urc', 'ospreys',                'オスプレイズ (ラグビー)', 'Ospreys (rugby union)', 'URC', 'オスプレイズ'),
    ('urc', 'scarlets',               'スカーレッツ',          'Scarlets',                'URC', 'スカーレッツ'),
    ('urc', 'ulster-rugby',           'アルスター・ラグビー', 'Ulster Rugby',             'URC', 'アルスター'),
    ('urc', 'vodacom-bulls',          'ブルズ (ラグビー)',     'Bulls (rugby union)',      'URC', 'ヴォーダコム・ブルズ'),
    ('urc', 'zebre-parma',            'ゼブレ・ラグビー',     'Zebre Parma',             'URC', 'ゼブレ・パルマ'),

    # Premiership: generation failed + Wikipedia修正
    ('premiership', 'bath-rugby',         'バース・ラグビー',          'Bath Rugby',          'プレミアシップ', 'バース'),
    ('premiership', 'bristol-bears',      'ブリストル・ラグビー',      'Bristol Bears',       'プレミアシップ', 'ブリストル・ベアーズ'),
    ('premiership', 'exeter-chiefs',      'エクセター・チーフス',      'Exeter Chiefs',       'プレミアシップ', 'エクセター・チーフス'),
    ('premiership', 'gloucester-rugby',   'グロスター・ラグビー',      'Gloucester Rugby',    'プレミアシップ', 'グロスター'),
    ('premiership', 'harlequins',         '',                          'Harlequins FC',       'プレミアシップ', 'ハーレクインズ'),
    ('premiership', 'leicester-tigers',   'レスター・タイガース',      'Leicester Tigers',    'プレミアシップ', 'レスター・タイガース'),
    ('premiership', 'newcastle-falcons',  '',                          'Newcastle Falcons',   'プレミアシップ', 'ニューカッスル・ファルコンズ'),
    ('premiership', 'northampton-saints', 'ノーサンプトン・セインツ',  'Northampton Saints',  'プレミアシップ', 'ノーサンプトン・セインツ'),
    ('premiership', 'sale-sharks',        'セール・シャークス',        'Sale Sharks',         'プレミアシップ', 'セール・シャークス'),
    ('premiership', 'saracens',           'サラセンズFC',              'Saracens F.C.',       'プレミアシップ', 'サラセンズ'),
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

LO_PROMPT = """以下はWikipediaから取得した「{team}」に関する情報です。

---
{wiki_text}
---

この情報のみを使い、以下の3セクションをMarkdownで生成してください。
Wikipedia未記載の事実は書かない。推測・補完も禁止。情報が不足する項目は「不明」と書く。

## チーム概要・基本データ

| 項目 | 詳細 |
| :--- | :--- |
| リーグ | リーグワン |
| 創設年 | （Wikipedia記載の創設年） |
| 本拠地 | （スタジアム名・都市） |
| 母体企業 | （スポンサー企業名） |
| タイトル歴 | （主要タイトルのみ、なければ「なし」） |

## チームの歴史

（Wikipedia情報のみで3〜5文）

## ホストエリアとの繋がり

（Wikipedia記載の地域情報のみで2〜3文。不明なら「公式サイトを参照」とだけ書く）
"""

def fetch_wikipedia(page_name, lang='ja'):
    if not page_name:
        return None, lang
    encoded = urllib.parse.quote(page_name)
    url = (f'https://{lang}.wikipedia.org/w/api.php?action=query&prop=extracts'
           f'&explaintext=true&titles={encoded}&format=json&exsectionformat=plain')
    req = urllib.request.Request(url, headers={'User-Agent': 'rugbypicks-bot/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10, context=SSL_CTX) as resp:
            data = json.loads(resp.read())
        pages = data['query']['pages']
        page = next(iter(pages.values()))
        if 'missing' in page:
            return None, lang
        text = page.get('extract', '')[:3000]
        return (text if text.strip() else None), lang
    except Exception:
        return None, lang

def get_wiki_text(ja_name, en_name):
    if ja_name:
        text, lang = fetch_wikipedia(ja_name, 'ja')
        if text:
            return text, 'Japanese'
    if en_name:
        text, lang = fetch_wikipedia(en_name, 'en')
        if text:
            return text, 'English'
    return None, None

def generate(prompt_text):
    result = subprocess.run(
        ['claude', '-p', prompt_text],
        capture_output=True, text=True, timeout=90
    )
    if result.returncode != 0 or not result.stdout.strip():
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
    return content[idx:] if idx != -1 else ''

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

        if league_dir == 'league-one':
            prompt = LO_PROMPT.format(team=team_display, wiki_text=wiki_text)
        else:
            prompt = PROMPT_TEMPLATE.format(
                team=team_display, lang=wiki_lang,
                wiki_text=wiki_text, league=league_label
            )

        sections = generate(prompt)
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
        time.sleep(1.5)  # rate limit対策を強化

    print(f'\n完了: {ok}件成功、{len(ng)}件失敗')
    if ng:
        print('失敗:', ng)

if __name__ == '__main__':
    main()
