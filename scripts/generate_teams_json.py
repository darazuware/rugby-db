import csv
import json
import os

import unicodedata

from team_utils import get_team_info

def slugify(text):
    if not text: return ""
    # 日本語（ひらがな、カタカナ、漢字）が含まれているかチェック
    if any(unicodedata.name(c).startswith(('HIRAGANA', 'KATAKANA', 'CJK UNIFIED IDEOGRAPH')) for c in text if ' ' <= c <= '~' or ord(c) > 127):
        # 日本語が含まれる場合は、slugify せず、呼び出し側での処理に任せる（または空を返す）
        # ただし unicodedata.name は一部の文字でエラーになる可能性があるため慎重に
        try:
            for char in text:
                name = unicodedata.name(char)
                if any(x in name for x in ['HIRAGANA', 'KATAKANA', 'CJK UNIFIED']):
                    return "" # 日本語が含まれる場合は空を返す
        except:
            pass

    # アクセント除去 (NFD分解して結合文字を除く)
    text = unicodedata.normalize('NFD', text)
    text = "".join([c for c in text if not unicodedata.combining(c)])
    # 記号置換
    text = text.lower().replace(' ', '-').replace("'", '').replace('&', 'and')
    # アルファベット、数字、ハイフン以外を除去
    import re
    text = re.sub(r'[^a-z0-9-]', '', text)
    return text.strip('-')

def extract_teams_from_csv(csv_path, league):
    teams = set()
    if not os.path.exists(csv_path):
        return []
    
    # リーグごとのデフォルト名マッピング（スラッグ生成に失敗した場合用）
    # URC用の最低限のマッピング
    fallback_slugs = {
        "ドラゴンズ・ラグビー": "dragons",
        "ルースターズ": "ulster",
        "グラスゴー・ウォリアーズ": "glasgow",
        "ヴォーダコム・ブルズ": "bulls",
        "レンスター・ラグビー": "leinster",
        "スカーレッツ": "scarlets",
        "ゼブレ・パルマ": "zebre",
        "マンスター・ラグビー": "munster",
        "カーディフ・ラグビー": "cardiff",
        "エディンバラ・ラグビー": "edinburgh",
        "ベネットン・ラグビー": "benetton",
        "オスプリーズ": "ospreys",
        "DHLストーマーズ": "stormers",
        "ハリウッドベッツ・シャークス": "sharks",
        "エミレーツ・ライオンズ": "lions"
    }

    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('所属チーム'):
                teams.add(row['所属チーム'])
    
    unique_teams = []
    for t in sorted(list(teams)):
        info = get_team_info(t)
        if info:
            unique_teams.append({
                "team_name": info.get('jp', t),
                "slug": info['slug'],
                "league": info['league']
            })
        else:
            slug = slugify(t)
            if not slug and t in fallback_slugs:
                slug = fallback_slugs[t]
            if not slug:
                # 最終的なフォールバック
                slug = re.sub(r'[^a-z0-9-]+', '-', t.lower()).strip('-') # 記号だけ抜く
            unique_teams.append({"team_name": t, "slug": slug, "league": league})
    return unique_teams

def main():
    all_teams = []

    # League One (既存の詳細 JSON を利用)
    if os.path.exists('data/league_one_teams_detailed.json'):
        with open('data/league_one_teams_detailed.json', 'r', encoding='utf-8') as f:
            l1_raw = json.load(f)
            for t in l1_raw:
                info = get_team_info(t['team_name'])
                if info:
                    all_teams.append({
                        "team_name": t['team_name'],
                        "slug": info['slug'],
                        "league": info['league'],
                        "division": t.get('division'),
                        "host_area": t.get('host_area'),
                        "legal_entity": t.get('legal_entity')
                    })
                else:
                    all_teams.append({
                        "team_name": t['team_name'],
                        "slug": slugify(t['team_name']),
                        "league": "league-one",
                        "division": t.get('division'),
                        "host_area": t.get('host_area'),
                        "legal_entity": t.get('legal_entity')
                    })

    # Super Rugby
    all_teams.extend(extract_teams_from_csv('data_sources/super_rugby_full.csv', 'super-rugby'))

    # URC
    all_teams.extend(extract_teams_from_csv('data_sources/urc_full.csv', 'urc'))

    # Top 14 チームの手動マッピング（アクセント記号問題を完全に回避）
    top14_slug_map = {
        "トゥールーズ": "toulouse",
        "ボルドー・ベグル": "bordeaux",
        "スタッド・フランセ": "paris",
        "トゥーロン": "toulon",
        "ラ・ロシェル": "la-rochelle",
        "ラシン92": "racing-92",
        "リヨン": "lyon",
        "カストル": "castres",
        "ポー": "pau",
        "ペルピニャン": "perpignan",
        "バイヨンヌ": "bayonne",
        "クレルモン": "clermont",
        "モンペリエ": "montpellier",
        "ヴァンヌ": "vannes"
    }

    # Top 14
    if os.path.exists('data/top14_teams.json'):
        with open('data/top14_teams.json', 'r', encoding='utf-8') as f:
            top14_raw = json.load(f)
            for t in top14_raw:
                slug = t['slug']
                # 手動マッピングがあれば上書き
                if t['name_ja'] in top14_slug_map:
                    slug = top14_slug_map[t['name_ja']]
                
                all_teams.append({
                    "team_name": t['name_ja'],
                    "team_en_name": t['name'],
                    "slug": slug,
                    "league": "top14"
                })

    # Premiership (Master CSV から抽出)
    # リーグ名が 'premiership' のものを対象とする
    prem_slug_map = {
        "ノーサンプトン・セインツ": "northampton-saints",
        "バース・ラグビー": "bath-rugby",
        "ブリストル・ベアーズ": "bristol-bears",
        "レスター・タイガーズ": "leicester-tigers",
        "エクセター・チーフス": "exeter-chiefs",
        "サラセンズ": "saracens",
        "セール・シャークス": "sale-sharks",
        "グロスター・ラグビー": "gloucester-rugby",
        "ハリクインズ": "harlequins",
        "ニューカッスル・ファルコンズ": "newcastle-falcons"
    }

    print("Extracting Premiership teams from master CSV...")
    if os.path.exists('data_sources/final_master_data_v25.csv'):
        # チーム名をキー、情報を値とする辞書で一意性を保つ
        prem_teams_dict = {}
        with open('data_sources/final_master_data_v25.csv', mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('リーグ') == 'premiership':
                    t_name = row.get('所属チーム')
                    if t_name and t_name not in prem_teams_dict:
                        info = get_team_info(t_name)
                        slug = info['slug'] if info else slugify(t_name)
                        # 手動マッピング優先
                        jp_name = info.get('jp', t_name) if info else t_name
                        if jp_name in prem_slug_map:
                            slug = prem_slug_map[jp_name]
                        
                        prem_teams_dict[t_name] = {
                            "team_name": jp_name,
                            "team_en_name": info.get('name_en', t_name) if info else t_name,
                            "slug": slug,
                            "league": "premiership"
                        }
        all_teams.extend(prem_teams_dict.values())

    # MLR (Master CSV から抽出)
    print("Extracting MLR teams from master CSV...")
    if os.path.exists(CSV_PATH := 'data_sources/final_master_data_v27_normalized.csv'):
        mlr_teams_dict = {}
        with open(CSV_PATH, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('League') == 'mlr':
                    t_name = row.get('Current_Team')
                    if t_name and t_name not in mlr_teams_dict:
                        info = get_team_info(t_name)
                        # 強制的に英語名からスラッグ生成
                        en_name = info.get('name_en', t_name) if info else t_name
                        slug = slugify(en_name)
                        
                        mlr_teams_dict[t_name] = {
                            "team_name": info.get('jp', t_name) if info else t_name,
                            "team_en_name": en_name,
                            "slug": slug,
                            "league": "mlr"
                        }
        all_teams.extend(mlr_teams_dict.values())

    # 重複排除 (名前 + リーグ + スラッグベース)
    # 同じチーム名でもリーグやスラッグが違う場合は別物として扱う
    unique_teams = []
    seen = set()
    for t in all_teams:
        league = t['league']
        if league == 'leagueone': league = 'league-one'
        
        # キーにスラッグも含めることで、手動更新したものが正しく残るようにする
        key = f"{league}-{t['team_name']}-{t['slug']}"
        if key not in seen:
            t['league'] = league
            unique_teams.append(t)
            seen.add(key)

    with open('data/teams.json', 'w', encoding='utf-8') as f:
        json.dump(unique_teams, f, ensure_ascii=False, indent=2)
    
    print(f"Generated data/teams.json with {len(unique_teams)} teams.")

if __name__ == "__main__":
    main()
