import json
import os

PROJECT_ROOT = '/Users/ktamatzmoto/Desktop/rugbypicks'
L1_DETAILED_JSON = os.path.join(PROJECT_ROOT, 'data/league_one_teams_detailed.json')

# Data scraped from league-one.jp
L1_STADIUM_DATA = {
    # Division 1
    "浦安D-Rocks": ("駒沢オリンピック公園総合運動場陸上競技場", "東京都世田谷区駒沢公園１−１"),
    "埼玉パナソニックワイルドナイツ": ("熊谷スポーツ文化公園ラグビー場", "埼玉県熊谷市上川上８１０"),
    "静岡ブルーレヴズ": ("ヤマハスタジアム", "静岡県ヤマハスタジアム（磐田）"),
    "東芝ブレイブルーパス東京": ("味の素スタジアム", "東京都調布市西町376-3"),
    "三菱重工相模原ダイナボアーズ": ("相模原ギオンスタジアム", "神奈川県相模原市南区下溝４１６９"),
    "横浜キヤノンイーグルス": ("ニッパツ三ツ沢球技場", "神奈川県横浜市神奈川区三ツ沢西町3-1"), # 日産スタジアムも使われるがニッパツが主
    "クボタスピアーズ船橋・東京ベイ": ("スピアーズえどりくフィールド", "東京都江戸川区清新町２丁目１−１"),
    "コベルコ神戸スティーラーズ": ("神戸総合運動公園ユニバー記念競技場", "兵庫県神戸市須磨区緑台"),
    "東京サントリーサンゴリアス": ("味の素スタジアム", "東京都調布市西町376-3"),
    "トヨタヴェルブリッツ": ("豊田スタジアム", "愛知県豊田市千石町７丁目２"),
    "三重ホンダヒート": ("三重交通G スポーツの杜 鈴鹿", "三重県鈴鹿市御薗町１６６９"),
    "リコーブラックラムズ東京": ("駒沢オリンピック公園総合運動場陸上競技場", "東京都世田谷区駒沢公園１−１"),
    
    # Division 2
    "NECグリーンロケッツ東葛": ("柏の葉公園総合競技場", "千葉県柏市柏の葉４−１"),
    "九州電力キューデンヴォルテクス": ("ベスト電器スタジアム", "福岡県福岡市博多区東平尾公園２丁目１−１"),
    "清水建設江東ブルーシャークス": ("江東区夢の島競技場", "東京都江東区夢の島１−１−２"),
    "豊田自動織機シャトルズ愛知": ("ウェーブスタジアム刈谷", "愛知県刈谷市築地町荒田1番地"),
    "日本製鉄釜石シーウェイブス": ("釜石鵜住居復興スタジアム", "岩手県釜石市鵜住居町第１８地割５−１"),
    "花園近鉄ライナーズ": ("東大阪市花園ラグビー場", "大阪府東大阪市松原南1-1-1"),
    "日野レッドドルフィンズ": ("AGFフィールド", "東京都調布市西町２９０"),
    "レッドハリケーンズ大阪": ("ヨドコウ桜スタジアム", "大阪府大阪市東住吉区長居公園１−１"),
    
    # Division 3
    "クリタウォーターガッシュ昭島": ("昭島市陸上競技場", "東京都昭島市東町5-11-43"),
    "狭山セコムラガッツ": ("セコムラグビーフィールド", "埼玉県狭山市柏原３１３"),
    "中国電力レッドレグリオンズ": ("Balcom BMW Rugby Stadium", "広島県広島市西区観音新町2-11-124"),
    "マツダスカイアクティブズ広島": ("Balcom BMW Stadium", "広島県広島市西区観音新町2-11-124"),
    "ヤクルトレビンズ戸田": ("ヤクルト戸田グラウンド", "埼玉県戸田市美女木4638-1"),
    "ルリーロ福岡": ("久留米総合スポーツセンター陸上競技場", "福岡県久留米市東櫛原町１７３")
}

def update_l1_stadiums():
    print(f"Loading {L1_DETAILED_JSON}...")
    with open(L1_DETAILED_JSON, 'r', encoding='utf-8') as f:
        teams = json.load(f)
    
    updated_count = 0
    for team in teams:
        name = team.get('team_name')
        if name in L1_STADIUM_DATA:
            stadium_name, address = L1_STADIUM_DATA[name]
            team['home_ground'] = stadium_name
            team['home_ground_address'] = address
            updated_count += 1
        else:
            print(f"Warning: Team {name} not found in stadium data.")

    print(f"Updated {updated_count} League One teams with official stadiums.")
    with open(L1_DETAILED_JSON, 'w', encoding='utf-8') as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)
    print("Saved detailed JSON.")

if __name__ == "__main__":
    update_l1_stadiums()
