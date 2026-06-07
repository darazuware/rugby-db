#!/usr/bin/env python3
"""
Wikipedia情報を基にLO26チームの記事前半（概要・歴史・地域）を生成し、
既存のCSV由来選手セクションと結合して保存する。
"""
import subprocess
import urllib.request
import urllib.parse
import json
import os
import time
import ssl

# macOS SSL証明書問題の回避
SSL_CTX = ssl._create_unverified_context()

TEAMS_DIR = '/Users/ktamatzmoto/Desktop/rugbypicks/src/content/teams/league-one'

# slug -> (Wikipediaページ名, frontmatterのtitle)
TEAMS = [
    ('chugoku-electric-red-regulions', '中国電力レッドレグリオンズ',    '中国電力レッドレグリオンズ'),
    ('hanazono-kintetsu-liners',       '花園近鉄ライナーズ',            '花園近鉄ライナーズ'),
    ('hino-red-dolphins',              '日野レッドドルフィンズ',         '日野レッドドルフィンズ'),
    ('hurricanes',                     'レッドハリケーンズ大阪',         'レッドハリケーンズ大阪'),
    ('kamaishi-seawaves',              '日本製鉄釜石シーウェイブス',     '日本製鉄釜石シーウェイブス'),
    ('kobelco-kobe-steelers',          'コベルコ神戸スティーラーズ',     'コベルコ神戸スティーラーズ'),
    ('kubota-spears-funabashi-tokyo-bay', 'クボタスピアーズ船橋・東京ベイ', 'クボタスピアーズ船橋・東京ベイ'),
    ('kurita-water-gush-akishima',     'クリタウォーターガッシュ昭島',   'クリタウォーターガッシュ昭島'),
    ('kyuden-voltex',                  '九州電力キューデンヴォルテクス', '九州電力キューデンヴォルテクス'),
    ('mazda-skyactivs-hiroshima',      'マツダスカイアクティブズ広島',   'マツダスカイアクティブズ広島'),
    ('mie-honda-heat',                 '三重ホンダヒート',               '三重ホンダヒート'),
    ('mitsubishi-sagamihara-dynaboars','三菱重工相模原ダイナボアーズ',   '三菱重工相模原ダイナボアーズ'),
    ('nec-green-rockets-tokatsu',      'NECグリーンロケッツ東葛',        'NECグリーンロケッツ東葛'),
    ('ricoh-black-rams-tokyo',         'リコーブラックラムズ東京',       'リコーブラックラムズ東京'),
    ('ruriro-fukuoka',                 'ルリーロ福岡',                   'ルリーロ福岡'),
    ('saitama-panasonic-wild-knights', '埼玉パナソニックワイルドナイツ', '埼玉パナソニックワイルドナイツ'),
    ('secom-rugguts',                  '狭山セコムラガッツ',             '狭山セコムラガッツ'),
    ('shimizu-koto-blue-sharks',       '清水建設江東ブルーシャークス',   '清水建設江東ブルーシャークス'),
    ('shizuoka-blue-revs',             '静岡ブルーレヴズ',               '静岡ブルーレヴズ'),
    ('tokyo-suntory-sungoliath',       '東京サントリーサンゴリアス',     '東京サントリーサンゴリアス'),
    ('toyota-shuttles-aichi',          '豊田自動織機シャトルズ愛知',     '豊田自動織機シャトルズ愛知'),
    ('toyota-verblitz',                'トヨタヴェルブリッツ',           'トヨタヴェルブリッツ'),
    ('toshiba-brave-lupus-tokyo',      '東芝ブレイブルーパス東京',       '東芝ブレイブルーパス東京'),
    ('urayasu-d-rocks',                '浦安D-Rocks',                    '浦安D-Rocks'),
    ('yakult-levins',                  'ヤクルトレビンズ戸田',           'ヤクルトレビンズ戸田'),
    ('yokohama-canon-eagles',          '横浜キヤノンイーグルス',         '横浜キヤノンイーグルス'),
]

PROMPT_TEMPLATE = """以下はWikipediaから取得した「{team}」に関する情報です。

---
{wiki_text}
---

この情報のみを使い、以下の3セクションをMarkdownで生成してください。
Wikipedia未記載の事実は書かない。推測・補完も禁止。情報が不足する項目は「不明」と書く。

出力形式（この形式を厳守）:

## チーム概要・基本データ

| 項目 | 詳細 |
| :--- | :--- |
| リーグ | リーグワン |
| 創設年 | （Wikipedia記載の創設年） |
| 本拠地 | （スタジアム名・都市） |
| 母体企業 | （スポンサー企業名） |
| タイトル歴 | （主要タイトルのみ、なければ「なし」） |

## チームの歴史

（Wikipedia情報のみで3〜5文。創設背景・重要な出来事・リーグワン参入経緯など）

## ホストエリアとの繋がり

（Wikipedia記載の地域情報のみで2〜3文。不明なら「公式サイトを参照」とだけ書く）
"""

def fetch_wikipedia(page_name):
    """Wikipedia APIからplaintextを取得"""
    encoded = urllib.parse.quote(page_name)
    url = (
        f'https://ja.wikipedia.org/w/api.php'
        f'?action=query&prop=extracts&explaintext=true'
        f'&titles={encoded}&format=json&exsectionformat=plain'
    )
    req = urllib.request.Request(url, headers={'User-Agent': 'rugbypicks-bot/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10, context=SSL_CTX) as resp:
            data = json.loads(resp.read())
        pages = data['query']['pages']
        page = next(iter(pages.values()))
        if 'missing' in page:
            return None
        text = page.get('extract', '')
        # 先頭3000文字に絞る（十分な情報量）
        return text[:3000]
    except Exception as e:
        print(f'  Wikipedia fetch error: {e}')
        return None

def generate_sections(team_name, wiki_text):
    """claude CLIで記事セクションを生成"""
    prompt = PROMPT_TEMPLATE.format(team=team_name, wiki_text=wiki_text)
    result = subprocess.run(
        ['claude', '-p', prompt],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        print(f'  claude error: {result.stderr[:200]}')
        return None
    return result.stdout.strip()

def get_player_section(filepath):
    """既存ファイルから選手セクション（## 現役選手 以降）を取得"""
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    idx = content.find('## 現役選手')
    if idx == -1:
        return ''
    return content[idx:]

def get_frontmatter(filepath):
    """frontmatterを取得"""
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    # ---で囲まれたfrontmatterを抽出
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            return content[:end+3]
    return ''

def main():
    ok, ng = 0, []

    for slug, wiki_name, team_display in TEAMS:
        filepath = os.path.join(TEAMS_DIR, f'{slug}.md')
        if not os.path.exists(filepath):
            print(f'[SKIP] {slug} - file not found')
            continue

        print(f'[{ok+1+len(ng)}/26] {team_display}', end=' ... ', flush=True)

        # 1. Wikipedia取得
        wiki_text = fetch_wikipedia(wiki_name)
        if not wiki_text:
            print(f'Wikipedia not found → skip')
            ng.append(slug)
            continue

        # 2. 記事セクション生成
        sections = generate_sections(team_display, wiki_text)
        if not sections:
            print('generation failed → skip')
            ng.append(slug)
            continue

        # 3. frontmatter + 生成セクション + 選手セクションを結合
        frontmatter = get_frontmatter(filepath)
        # frontmatterのtitleは更新しない（既存を維持）
        player_section = get_player_section(filepath)

        new_content = frontmatter + '\n\n' + sections + '\n\n' + player_section
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print('OK')
        ok += 1
        time.sleep(1)  # rate limit対策

    print(f'\n完了: {ok}件成功、{len(ng)}件失敗')
    if ng:
        print('失敗:', ng)

if __name__ == '__main__':
    main()
