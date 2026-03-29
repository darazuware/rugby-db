import csv
import os

# プロジェクトルートの設定
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'data_sources/top_west_players.csv')

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

    # 1. 中部電力 (Chubu Electric) - top-west-a
    chubu_players = [
        # FW
        {"name_ja": "内田 康介", "position": "PR", "height": "176", "weight": "104", "university": "筑波大学", "team": "中部電力"},
        {"name_ja": "安藤 良太", "position": "HO", "height": "178", "weight": "98", "university": "東海大学", "team": "中部電力"},
        {"name_ja": "池上 玲央", "position": "FL", "height": "173", "weight": "83", "university": "帝京大学", "team": "中部電力"},
        {"name_ja": "佐藤 健斗", "position": "FL", "height": "178", "weight": "86", "university": "中部大学", "team": "中部電力"},
        {"name_ja": "長江 有祐", "position": "PR", "height": "", "weight": "", "university": "", "team": "中部電力"},
        {"name_ja": "本間 優", "position": "PR", "height": "", "weight": "", "university": "", "team": "中部電力"},
        {"name_ja": "辻 龍哉", "position": "PR", "height": "", "weight": "", "university": "", "team": "中部電力"},
        {"name_ja": "六車 高寧", "position": "PR", "height": "", "weight": "", "university": "", "team": "中部電力"},
        {"name_ja": "真山 文一", "position": "PR", "height": "", "weight": "", "university": "", "team": "中部電力"},
        {"name_ja": "鈴木 天良", "position": "PR", "height": "", "weight": "", "university": "", "team": "中部電力"},
        {"name_ja": "紀伊 遼平", "position": "HO", "height": "", "weight": "", "university": "", "team": "中部電力"},
        {"name_ja": "三枝 優介", "position": "LO", "height": "", "weight": "", "university": "", "team": "中部電力"},
        {"name_ja": "長田 拓真", "position": "LO", "height": "", "weight": "", "university": "", "team": "中部電力"},
        # BK
        {"name_ja": "西川 敢太", "position": "SH", "height": "", "weight": "", "university": "京都産業大学", "team": "中部電力"},
        {"name_ja": "松山 将輝", "position": "SH", "height": "", "weight": "", "university": "近畿大学", "team": "中部電力"},
        {"name_ja": "津田 貫汰", "position": "SO", "height": "", "weight": "", "university": "中央大学", "team": "中部電力"},
        {"name_ja": "笠原 浩史", "position": "SO", "height": "", "weight": "", "university": "同志社大学", "team": "中部電力"},
        {"name_ja": "藤本 凌聖", "position": "CTB", "height": "", "weight": "", "university": "京都産業大学", "team": "中部電力"},
        {"name_ja": "井上 正規", "position": "CTB", "height": "", "weight": "", "university": "福岡大学", "team": "中部電力"},
        {"name_ja": "棚橋 優大", "position": "CTB", "height": "", "weight": "", "university": "天理大学", "team": "中部電力"},
        {"name_ja": "小椋 統平", "position": "CTB", "height": "", "weight": "", "university": "明治大学", "team": "中部電力"},
        {"name_ja": "神田 永遠", "position": "CTB", "height": "", "weight": "", "university": "大東文化大学", "team": "中部電力"},
        {"name_ja": "鶴田 桂樹", "position": "WTB", "height": "", "weight": "", "university": "同志社大学", "team": "中部電力"},
        {"name_ja": "谷川 司", "position": "WTB", "height": "", "weight": "", "university": "同志社大学", "team": "中部電力"},
        {"name_ja": "芦塚 仁", "position": "WTB", "height": "178", "weight": "93", "university": "同志社大学", "team": "中部電力"},
        {"name_ja": "中村 海斗", "position": "WTB", "height": "", "weight": "", "university": "帝京大学", "team": "中部電力"},
        {"name_ja": "高比良 隼輝", "position": "WTB", "height": "", "weight": "", "university": "明治大学", "team": "中部電力"},
        {"name_ja": "林 哲平", "position": "FB", "height": "176", "weight": "81", "university": "明治大学", "team": "中部電力"},
        {"name_ja": "野々山 紘旨", "position": "FB", "height": "", "weight": "", "university": "中部大学", "team": "中部電力"},
        {"name_ja": "長野 成貴", "position": "FB", "height": "", "weight": "", "university": "帝京大学", "team": "中部電力"},
        {"name_ja": "鬼木 秀一", "position": "FB", "height": "", "weight": "", "university": "帝京大学", "team": "中部電力"},
    ]
    for p in chubu_players:
        p.update({"name_en": "", "league": "top-west-a", "category": "top-west-a", "url": "https://www.chuden.co.jp/energy/p_sports/rugby/", "age": ""})
        players.append(p)

    # 2. Daigas Struggers (Osaka Gas) - top-west-a
    daigas_players = [
        {"name_ja": "依藤 駿之介", "position": "PR", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "三木 陽平", "position": "PR", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "山中 翔太", "position": "PR", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "鈴木 将大", "position": "HO", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "山田 裕大", "position": "HO", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "鈴木 隆文", "position": "LO", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "半田 歩夢", "position": "LO", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "後藤 康成", "position": "FL", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "後藤 龍馬", "position": "FL", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "佃 大輝", "position": "No.8", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "福岡 壮太郎", "position": "SH", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "間森 涼太", "position": "SO", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "阿部 慎太郎", "position": "CTB", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "金子 隆洋", "position": "CTB", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "河波 風太", "position": "CTB", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "畑中 進吾", "position": "CTB", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "南野 仁", "position": "WTB", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "本田 飛翔", "position": "WTB", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "大鳥 勢太", "position": "WTB", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
        {"name_ja": "小松 頼斗", "position": "FB", "height": "", "weight": "", "university": "", "team": "Daigas Struggers"},
    ]
    for p in daigas_players:
        p.update({"name_en": "", "league": "top-west-a", "category": "top-west-a", "url": "https://www.osakagas.co.jp/company/efforts/sports/rugby/", "age": ""})
        players.append(p)

    # 3. 大阪府警察 (Osaka Police) - top-west-a
    police_players = [
        {"name_ja": "半田 晃大", "position": "PR", "team": "大阪府警察"},
        {"name_ja": "宮脇 颯太", "position": "PR", "team": "大阪府警察"},
        {"name_ja": "加覽 和成", "position": "PR", "team": "大阪府警察"},
        {"name_ja": "小林 大介", "position": "PR", "team": "大阪府警察"},
        {"name_ja": "野崎 睦馬", "position": "PR", "team": "大阪府警察"},
        {"name_ja": "谷井 連太郎", "position": "HO", "team": "大阪府警察"},
        {"name_ja": "山口 翼", "position": "HO", "team": "大阪府警察"},
        {"name_ja": "小泉 友一郎", "position": "HO", "team": "大阪府警察"},
        {"name_ja": "栗本 勘司", "position": "LO", "team": "大阪府警察"},
        {"name_ja": "中庭 由尋", "position": "LO", "team": "大阪府警察"},
        {"name_ja": "上辻 佑磨", "position": "LO", "team": "大阪府警察"},
        {"name_ja": "駒井 凌太", "position": "LO", "team": "大阪府警察"},
        {"name_ja": "蔵守 俊介", "position": "LO", "team": "大阪府警察"},
        {"name_ja": "高橋 稔貴", "position": "FL", "team": "大阪府警察"},
        {"name_ja": "篠澤 輝", "position": "FL", "team": "大阪府警察"},
        {"name_ja": "岡本 流星", "position": "FL", "team": "大阪府警察"},
        {"name_ja": "宮本 学武", "position": "FL", "team": "大阪府警察"},
        {"name_ja": "照井 悠一郎", "position": "FL", "team": "大阪府警察"},
        {"name_ja": "吉田 周平", "position": "No.8", "team": "大阪府警察"},
        {"name_ja": "廣田 瞬", "position": "SH", "team": "大阪府警察"},
        {"name_ja": "武井 陽昌", "position": "SH", "team": "大阪府警察"},
        {"name_ja": "星野 玄太", "position": "SH", "team": "大阪府警察"},
        {"name_ja": "志和池 豊馬", "position": "SO", "team": "大阪府警察"},
        {"name_ja": "高部 勇", "position": "CTB", "team": "大阪府警察"},
        {"name_ja": "川島 俊亮", "position": "CTB", "team": "大阪府警察"},
        {"name_ja": "星野 大紀", "position": "CTB", "team": "大阪府警察"},
        {"name_ja": "堀田 恒司", "position": "CTB", "team": "大阪府警察"},
        {"name_ja": "白國 亮大", "position": "WTB", "team": "大阪府警察"},
        {"name_ja": "松田 信夫", "position": "WTB", "team": "大阪府警察"},
        {"name_ja": "村田 佳翼", "position": "WTB", "team": "大阪府警察"},
        {"name_ja": "勝又 佑介", "position": "FB", "team": "大阪府警察"},
        {"name_ja": "楠本 航己", "position": "FB", "team": "大阪府警察"},
    ]
    for p in police_players:
        p.update({"name_en": "", "league": "top-west-a", "category": "top-west-a", "url": "https://www.police.pref.osaka.lg.jp/soshiki/taiiku/rugby/index.html", "age": "", "height": "", "weight": "", "university": ""})
        players.append(p)

    # 4. 島津製作所 Breakers - top-west-a
    shimadzu_players = [
        {"name_ja": "絹川 誠吾", "position": "PR", "team": "島津製作所 Breakers"},
        {"name_ja": "坂本 匠", "position": "PR", "team": "島津製作所 Breakers"},
        {"name_ja": "中島 悠太", "position": "PR", "team": "島津製作所 Breakers"},
        {"name_ja": "長谷川 翔舞", "position": "PR", "team": "島津製作所 Breakers"},
        {"name_ja": "稲田 竜一", "position": "PR", "team": "島津製作所 Breakers"},
        {"name_ja": "高松 悠天", "position": "HO", "team": "島津製作所 Breakers"},
        {"name_ja": "西村 優希", "position": "HO", "team": "島津製作所 Breakers"},
        {"name_ja": "中川 将弥", "position": "LO", "team": "島津製作所 Breakers"},
        {"name_ja": "小池 健雄", "position": "LO", "team": "島津製作所 Breakers"},
        {"name_ja": "河野 圭太朗", "position": "LO", "team": "島津製作所 Breakers"},
        {"name_ja": "完山 汰成", "position": "LO", "team": "島津製作所 Breakers"},
        {"name_ja": "羽田 匠之介", "position": "FL", "team": "島津製作所 Breakers"},
        {"name_ja": "大澤 俊介", "position": "FL", "team": "島津製作所 Breakers"},
        {"name_ja": "李 翔太", "position": "SH", "team": "島津製作所 Breakers"},
        {"name_ja": "秦 陽太", "position": "SO", "team": "島津製作所 Breakers"},
        {"name_ja": "片岡 祐二", "position": "CTB", "team": "島津製作所 Breakers"},
        {"name_ja": "生駒 創大郎", "position": "CTB", "team": "島津製作所 Breakers"},
        {"name_ja": "澤田 壮太郎", "position": "WTB", "team": "島津製作所 Breakers"},
        {"name_ja": "外山 翔平", "position": "WTB", "team": "島津製作所 Breakers"},
        {"name_ja": "山崎 来夢", "position": "WTB", "team": "島津製作所 Breakers"},
        {"name_ja": "山下 慶輔", "position": "FB", "team": "島津製作所 Breakers"},
    ]
    for p in shimadzu_players:
        p.update({"name_en": "", "league": "top-west-a", "category": "top-west-a", "url": "https://www.shimadzu.co.jp/rugby/", "age": "", "height": "", "weight": "", "university": ""})
        players.append(p)

    # 5. JR西日本レイラーズ - top-west-a
    jr_players = [
        {"name_ja": "橋詰 学", "position": "SH", "team": "JR西日本レイラーズ"},
        {"name_ja": "多賀 慈綺", "position": "SH", "team": "JR西日本レイラーズ"},
        {"name_ja": "池上 琉生", "position": "SH", "team": "JR西日本レイラーズ"},
        {"name_ja": "坂口 由純", "position": "SH", "team": "JR西日本レイラーズ"},
        {"name_ja": "土田 修也", "position": "SO", "team": "JR西日本レイラーズ"},
        {"name_ja": "山内 凌雅", "position": "SO", "team": "JR西日本レイラーズ"},
        {"name_ja": "一口 隼人", "position": "FL", "team": "JR西日本レイラーズ"},
        {"name_ja": "人見 太基", "position": "CTB", "team": "JR西日本レイラーズ"},
        {"name_ja": "北平 陽成", "position": "CTB", "team": "JR西日本レイラーズ"},
        {"name_ja": "金 成志", "position": "CTB", "team": "JR西日本レイラーズ"},
        {"name_ja": "伴井 亮太", "position": "WTB", "team": "JR西日本レイラーズ"},
        {"name_ja": "亀井 郁弥", "position": "WTB", "team": "JR西日本レイラーズ"},
        {"name_ja": "齊藤 瑠海奈", "position": "FB", "team": "JR西日本レイラーズ"},
        {"name_ja": "森本 蒼", "position": "FB", "team": "JR西日本レイラーズ"},
    ]
    for p in jr_players:
        p.update({"name_en": "", "league": "top-west-a", "category": "top-west-a", "url": "https://www.westjr.co.jp/company/action/sports/rugby/", "age": "", "height": "", "weight": "", "university": ""})
        players.append(p)

    # 6. MARUWA LOGISTAR’Z KYOTO - top-west-a
    maruwa_players = [
        {"name_ja": "山内 開斗", "position": "FW", "team": "MARUWA LOGISTAR’Z KYOTO"},
        {"name_ja": "平野 佑馬", "position": "FW", "team": "MARUWA LOGISTAR’Z KYOTO"},
        {"name_ja": "田中 大喜", "position": "BK", "team": "MARUWA LOGISTAR’Z KYOTO"},
    ]
    for p in maruwa_players:
        p.update({"name_en": "", "league": "top-west-a", "category": "top-west-a", "url": "https://www.maruwa-logi.jp/sports/", "age": "", "height": "", "weight": "", "university": ""})
        players.append(p)

    # 7. 豊田通商BLUE WING - top-west-a
    toyotsutsu_players = [
        {"name_ja": "小野 貴大", "position": "FW", "team": "豊田通商BLUE WING"},
        {"name_ja": "松岡 航平", "position": "BK", "team": "豊田通商BLUE WING"},
    ]
    for p in toyotsutsu_players:
        p.update({"name_en": "", "league": "top-west-a", "category": "top-west-a", "url": "https://www.toyota-tsusho.com/rugby/", "age": "", "height": "", "weight": "", "university": ""})
        players.append(p)

    save_players_to_csv(players, OUTPUT_PATH)
    print(f"Saved {len(players)} players to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
