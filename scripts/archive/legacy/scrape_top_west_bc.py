import csv
import os

# プロジェクトルートの設定
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'data_sources/top_west_players_bc.csv')

def save_players_to_csv(players, output_path):
    # PlayerDataProcessor.get_safe_attr の mapping に合わせる
    fieldnames = ['name_ja', 'name_en', 'position', 'age', 'height', 'weight', 'university', 'team', 'league', 'category', 'url']
    with open(output_path, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for player in players:
            writer.writerow(player)

def main():
    players = []

    # --- Top West B Teams ---

    # 1. リコージャパンBLACK AEGIS (Ricoh Japan)
    ricoh_j_players = [
        {"name_ja": "成宮 銀次郎", "position": "FW", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "小山 康太", "position": "FW", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "植松 海翔", "position": "FW", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "南 優多", "position": "FW", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "岡田 澄空", "position": "FW", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "亀田 聖", "position": "FW", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "大野 雄太", "position": "FW", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "毛利 虎之介", "position": "FW", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "大西 康平", "position": "FW", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "馬場 大樹", "position": "FW", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "丸山 泰史", "position": "FW", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "城戸 慎平", "position": "BK", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "横尾 瑛", "position": "BK", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "島津 雄斗", "position": "BK", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "中村 優太", "position": "BK", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "久保 元臣", "position": "BK", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "冨山 拓朗", "position": "BK", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "水谷 哲至", "position": "BK", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "松本 将希", "position": "BK", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "高田 清太郎", "position": "BK", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "押海 雄人", "position": "BK", "team": "リコージャパンBLACK AEGIS"},
        {"name_ja": "山﨑 海生", "position": "BK", "team": "リコージャパンBLACK AEGIS"},
    ]
    for p in ricoh_j_players:
        p.update({"name_en": "", "league": "top-west-b", "category": "top-west-b", "url": "https://rj-rugby.jp/", "age": "", "height": "", "weight": "", "university": ""})
        players.append(p)

    # 2. 三菱自動車倉敷キングフィッシャーズ
    kurashiki_players = [
        {"name_ja": "石井 祐次郎", "position": "LO", "team": "三菱自動車倉敷キングフィッシャーズ"},
        {"name_ja": "坂本 修司", "position": "CTB", "team": "三菱自動車倉敷キングフィッシャーズ"},
        {"name_ja": "大崎 恩慶", "position": "PR", "team": "三菱自動車倉敷キングフィッシャーズ"},
        {"name_ja": "藤原 健照", "position": "PR", "team": "三菱自動車倉敷キングフィッシャーズ"},
        {"name_ja": "富山 尚", "position": "PR/HO", "team": "三菱自動車倉敷キングフィッシャーズ"},
        {"name_ja": "松下 秀斗", "position": "PR", "university": "九州共立大学", "team": "三菱自動車倉敷キングフィッシャーズ"},
        {"name_ja": "渡邊 敬太", "position": "PR", "university": "立命館大学", "team": "三菱自動車倉敷キングフィッシャーズ"},
        {"name_ja": "森元 康平", "position": "HO", "university": "甲南大学", "team": "三菱自動車倉敷キングフィッシャーズ"},
        {"name_ja": "大間 歩", "position": "", "team": "三菱自動車倉敷キングフィッシャーズ"},
    ]
    for p in kurashiki_players:
        p.update({"name_en": "", "league": "top-west-b", "category": "top-west-b", "url": "https://www.mitsubishi-motors.com/jp/innovation/sports/rugby/kurashiki/", "age": "", "height": "", "weight": ""})
        players.append(p)

    # 3. 三菱自動車京都レッドエボリューションズ
    kyoto_re_players = [
        {"name_ja": "谷村 竜輝", "age": "18", "height": "173", "weight": "100", "university": "東山高校", "team": "三菱自動車京都レッドエボリューションズ"},
        {"name_ja": "木屋 暁貴", "age": "28", "height": "185", "weight": "105", "university": "摂南大学", "team": "三菱自動車京都レッドエボリューションズ"},
        {"name_ja": "センダナキム", "age": "19", "height": "174", "weight": "113", "university": "八幡工業高校", "team": "三菱自動車京都レッドエボリューションズ"},
        {"name_ja": "森田 圭亮", "age": "30", "height": "180", "weight": "90", "university": "龍谷大学", "team": "三菱自動車京都レッドエボリューションズ"},
        {"name_ja": "長縄 天翼", "age": "21", "height": "169", "weight": "93", "university": "関商工高校", "team": "三菱自動車京都レッドエボリューションズ"},
        {"name_ja": "山本 一歩", "age": "19", "height": "160", "weight": "60", "university": "創志学園高校", "team": "三菱自動車京都レッドエボリューションズ"},
        {"name_ja": "長井 一史", "age": "33", "height": "168", "weight": "80", "university": "同志社大学", "team": "三菱自動車京都レッドエボリューションズ"},
        {"name_ja": "大村 亮介", "age": "22", "height": "176", "weight": "85", "university": "京都産業大学", "team": "三菱自動車京都レッドエボリューションズ"},
        {"name_ja": "大崎 旭彦", "position": "WTB/FB", "team": "三菱自動車京都レッドエボリューションズ"},
        {"name_ja": "岩永 典晃", "position": "LO", "team": "三菱自動車京都レッドエボリューションズ"},
        {"name_ja": "清見 将之", "position": "SH", "team": "三菱自動車京都レッドエボリューションズ"},
        {"name_ja": "市原 淳平", "position": "CTB", "team": "三菱自動車京都レッドエボリューションズ"},
    ]
    for p in kyoto_re_players:
        p.update({"name_en": "", "league": "top-west-b", "category": "top-west-b", "url": "http://mitsubishi-kyoto-rugby.1web.jp/", "position": p.get("position", "")})
        players.append(p)

    # 4. きんでんトライデントブリッツ
    kinden_players = [
        {"name_ja": "今里 慧", "position": "CTB", "team": "きんでんトライデントブリッツ"},
        {"name_ja": "津田 剛希", "position": "CTB", "team": "きんでんトライデントブリッツ"},
        {"name_ja": "髙橋 雄太郎", "position": "CTB", "team": "きんでんトライデントブリッツ"},
        {"name_ja": "野村 成", "position": "CTB", "team": "きんでんトライデントブリッツ"},
        {"name_ja": "岩井 亮介", "position": "SH", "team": "きんでんトライデントブリッツ"},
        {"name_ja": "黒谷 淳", "position": "SH", "team": "きんでんトライデントブリッツ"},
        {"name_ja": "垣本 大誠", "position": "SH", "team": "きんでんトライデントブリッツ"},
        {"name_ja": "小嶋 遼平", "position": "No.8", "team": "きんでんトライデントブリッツ"},
        {"name_ja": "古橋 啓太", "position": "No.8", "team": "きんでんトライデントブリッツ"},
        {"name_ja": "高井 杏輔", "position": "No.8", "team": "きんでんトライデントブリッツ"},
    ]
    for p in kinden_players:
        p.update({"name_en": "", "league": "top-west-b", "category": "top-west-b", "url": "https://www.kinden-sports.jp/rugby/", "age": "", "height": "", "weight": "", "university": ""})
        players.append(p)

    # --- Top West C Teams ---

    # 1. 日本新薬OWLSTARS
    shinyaku_players = [
        {"name_ja": "西原 康平", "position": "PR", "team": "日本新薬OWLSTARS"},
        {"name_ja": "高木 佳也", "position": "HO", "team": "日本新薬OWLSTARS"},
        {"name_ja": "平野 佑馬", "position": "LO", "team": "日本新薬OWLSTARS"},
        {"name_ja": "中島 勇輝", "position": "FL", "team": "日本新薬OWLSTARS"},
        {"name_ja": "松本 健奨", "position": "SH", "team": "日本新薬OWLSTARS"},
        {"name_ja": "河合 泰輝", "position": "SO", "team": "日本新薬OWLSTARS"},
    ]
    for p in shinyaku_players:
        p.update({"name_en": "", "league": "top-west-c", "category": "top-west-c", "url": "https://www.nippon-shinyaku.co.jp/owlstars/", "age": "", "height": "", "weight": "", "university": ""})
        players.append(p)

    # 2. K-POWERS
    kpowers_players = [
        {"name_ja": "井上 拓也", "position": "SH", "team": "K-POWERS"},
        {"name_ja": "田中 大喜", "position": "SO", "team": "K-POWERS"},
        {"name_ja": "村田 雄志", "position": "CTB", "team": "K-POWERS"},
    ]
    for p in kpowers_players:
        p.update({"name_en": "", "league": "top-west-c", "category": "top-west-c", "url": "http://www.k-powers.co.jp/rugby/", "age": "", "height": "", "weight": "", "university": ""})
        players.append(p)

    save_players_to_csv(players, OUTPUT_PATH)
    print(f"Saved {len(players)} players to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
