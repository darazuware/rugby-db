import json

teams_data = [
  {"id": 98, "team_name": "静岡ブルーレヴズ", "legal_entity": "静岡ブルーレヴズ株式会社", "host_area": "静岡県", "practice_ground": "静岡県磐田市大久保891-106", "official_site": "https://www.shizuoka-bluerevs.com", "division": "Division 1"},
  {"id": 99, "team_name": "東京サントリーサンゴリアス", "legal_entity": "サントリーホールディングス株式会社", "host_area": "東京都、港区、府中市、調布市、三鷹市", "practice_ground": "東京都府中市是政6-22サントリー府中スポーツセンター", "official_site": "https://www.suntory.co.jp/culture-sports/sungoliath/", "division": "Division 1"},
  {"id": 100, "team_name": "浦安D-Rocks", "legal_entity": "株式会社NTT Sports X", "host_area": "千葉県浦安市", "practice_ground": "千葉県浦安市高洲８−２−１浦安Dパーク", "official_site": "https://urayasu-d-rocks.com", "division": "Division 1"},
  {"id": 101, "team_name": "コベルコ神戸スティーラーズ", "legal_entity": "株式会社神戸製鋼所", "host_area": "兵庫県、神戸市", "practice_ground": "兵庫県神戸市東灘区御影浜町４　神戸製鋼灘浜グラウンド", "official_site": "https://www.kobesteelers.com/", "division": "Division 1"},
  {"id": 102, "team_name": "埼玉パナソニックワイルドナイツ", "legal_entity": "パナソニック ホールディングス株式会社", "host_area": "埼玉県", "practice_ground": "埼玉県熊谷市上川上", "official_site": "https://panasonic.co.jp/sports/wildknights/", "division": "Division 1"},
  {"id": 103, "team_name": "東芝ブレイブルーパス東京", "legal_entity": "東芝ブレイブルーパス東京株式会社", "host_area": "東京都、府中市、調布市、三鷹市", "practice_ground": "東京都府中市東芝町１", "official_site": "https://www.bravelupus.com/", "division": "Division 1"},
  {"id": 104, "team_name": "トヨタヴェルブリッツ", "legal_entity": "トヨタ自動車株式会社", "host_area": "愛知県、豊田市、名古屋市、みよし市", "practice_ground": "愛知県豊田市保見町井ノ向57-230トヨタスポーツセンター", "official_site": "https://verblitz.toyotatimes-sports.toyota/", "division": "Division 1"},
  {"id": 105, "team_name": "三重ホンダヒート", "legal_entity": "本田技研工業株式会社", "host_area": "三重県", "practice_ground": "三重県鈴鹿市住吉町6731-2", "official_site": "http://www.honda-heat.jp/", "division": "Division 1"},
  {"id": 106, "team_name": "三菱重工相模原ダイナボアーズ", "legal_entity": "三菱重工業株式会社", "host_area": "神奈川県、相模原市", "practice_ground": "神奈川県相模原市中央区田名3000番地", "official_site": "https://dynaboars.mhi.com/", "division": "Division 1"},
  {"id": 107, "team_name": "横浜キヤノンイーグルス", "legal_entity": "キヤノン株式会社", "host_area": "神奈川県横浜市", "practice_ground": "東京都町田市小野路町5290-1", "official_site": "https://www.canon-eagles.jp/", "division": "Division 1"},
  {"id": 108, "team_name": "リコーブラックラムズ東京", "legal_entity": "株式会社リコー", "host_area": "東京都、世田谷区", "practice_ground": "東京都世田谷区宇奈根1−5−1", "official_site": "https://blackrams-tokyo.com/", "division": "Division 1"},
  {"id": 109, "team_name": "NECグリーンロケッツ東葛", "legal_entity": "日本電気株式会社", "host_area": "千葉県我孫子市、柏市、松戸市、流山市、野田市、鎌ケ谷市、白井市、印西市", "practice_ground": "千葉県我孫子市日の出1131", "official_site": "https://green.necrockets.net/", "division": "Division 1"},
  {"id": 110, "team_name": "九州電力キューデンヴォルテクス", "legal_entity": "九州電力株式会社", "host_area": "福岡市", "practice_ground": "福岡県福岡市東区松香台1-10-15", "official_site": "https://www.kyudenvoltex.com/", "division": "Division 2"},
  {"id": 111, "team_name": "清水建設江東ブルーシャークス", "legal_entity": "清水建設株式会社", "host_area": "東京都江東区", "practice_ground": "神奈川県横浜市都筑区荏田南町741番地", "official_site": "https://blue-sharks.jp/", "division": "Division 2"},
  {"id": 112, "team_name": "豊田自動織機シャトルズ愛知", "legal_entity": "株式会社豊田自動織機", "host_area": "愛知県", "practice_ground": "愛知県刈谷市逢妻町1-59-1", "official_site": "https://shuttles-aichi.com/", "division": "Division 2"},
  {"id": 113, "team_name": "日本製鉄釜石シーウェイブス", "legal_entity": "一般社団法人釜石シーウェイブスRFC", "host_area": "釜石市、岩手県", "practice_ground": "岩手県釜石市甲子町10-159-4", "official_site": "https://kamaishi-seawaves.com/", "division": "Division 2"},
  {"id": 114, "team_name": "花園近鉄ライナーズ", "legal_entity": "近鉄グループホールディングス株式会社", "host_area": "東大阪市、大阪府", "practice_ground": "大阪府東大阪市松原南1-1-1　東大阪市花園ラグビー場", "official_site": "https://hanazono-liners.jp/", "division": "Division 2"},
  {"id": 115, "team_name": "日野レッドドルフィンズ", "legal_entity": "日野自動車株式会社", "host_area": "東京都日野市、八王子市および周辺地域", "practice_ground": "東京都日野市新町5丁目18-1", "official_site": "https://hino-reddolphins.com/", "division": "Division 2"},
  {"id": 116, "team_name": "レッドハリケーンズ大阪", "legal_entity": "株式会社ＮＴＴドコモ", "host_area": "大阪府大阪市", "practice_ground": "大阪府大阪市住之江区南港北一丁目９−９", "official_site": "https://docomo-rugby.jp/", "division": "Division 3"},
  {"id": 117, "team_name": "クリタウォーターガッシュ昭島", "legal_entity": "栗田工業株式会社", "host_area": "東京都昭島市", "practice_ground": "東京都昭島市拝島町3990-3", "official_site": "https://www.kurita-watergush.jp/", "division": "Division 3"},
  {"id": 118, "team_name": "狭山セコムラガッツ", "legal_entity": "セコム株式会社ラグビー部", "host_area": "狭山市", "practice_ground": "埼玉県狭山市柏原富士塚308-1", "official_site": "https://www.rugguts.secom.co.jp/", "division": "Division 3"},
  {"id": 119, "team_name": "中国電力レッドレグリオンズ", "legal_entity": "中国電力株式会社", "host_area": "広島県", "practice_ground": "広島県広島県安芸郡坂町鯛尾2-6", "official_site": "https://rrrfc.red/", "division": "Division 3"},
  {"id": 120, "team_name": "マツダスカイアクティブズ広島", "legal_entity": "マツダ株式会社", "host_area": "広島県", "practice_ground": "広島県広島県安芸郡坂町鯛尾2-6", "official_site": "https://www.skyactivs.com/", "division": "Division 3"},
  {"id": 121, "team_name": "ヤクルトレビンズ戸田", "legal_entity": "株式会社ヤクルト本社", "host_area": "埼玉県戸田市", "practice_ground": "埼玉県戸田市美女木4638-1", "official_site": "https://www.yakult.co.jp/sports/rugby/", "division": "Division 3"}
]

with open('league_one_teams_detailed.json', 'w', encoding='utf-8') as f:
    json.dump(teams_data, f, ensure_ascii=False, indent=2)

print(f"Successfully consolidated {len(teams_data)} teams.")
