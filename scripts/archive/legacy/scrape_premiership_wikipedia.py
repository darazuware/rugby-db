import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 各チームのWikipediaページURL
TEAM_PAGES = {
    "Bath Rugby": "https://en.wikipedia.org/wiki/Bath_Rugby",
    "Bristol Bears": "https://en.wikipedia.org/wiki/Bristol_Bears",
    "Exeter Chiefs": "https://en.wikipedia.org/wiki/Exeter_Chiefs",
    "Gloucester Rugby": "https://en.wikipedia.org/wiki/Gloucester_Rugby",
    "Harlequins": "https://en.wikipedia.org/wiki/Harlequins_F.C.",
    "Leicester Tigers": "https://en.wikipedia.org/wiki/Leicester_Tigers",
    "Newcastle Falcons": "https://en.wikipedia.org/wiki/Newcastle_Falcons",
    "Northampton Saints": "https://en.wikipedia.org/wiki/Northampton_Saints",
    "Sale Sharks": "https://en.wikipedia.org/wiki/Sale_Sharks",
    "Saracens": "https://en.wikipedia.org/wiki/Saracens_F.C."
}

def clean_name(name):
    # [1], [2] などの文献参照や (on loan) などのカッコ書きを削除
    name = re.sub(r'\[.*?\]', '', name)
    name = re.sub(r'\(.*?\)', '', name)
    # 改行や余分な空白を削除
    return name.strip()

def scrape_team_squad(team_name, url):
    print(f"Scraping {team_name} from {url}...")
    players = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # "Senior squad" または "Current squad" という見出しを探す
        squad_headline = None
        for tag in soup.find_all(['h2', 'h3']):
            id_attr = tag.get('id', '')
            text = tag.get_text().lower()
            if ('squad' in text and ('senior' in text or 'current' in text)) or \
               ('squad' in id_attr.lower() and ('senior' in id_attr.lower() or 'current' in id_attr.lower())):
                squad_headline = tag
                break
        
        if not squad_headline:
            for span in soup.select('span.mw-headline'):
                text = span.get_text().lower()
                if 'squad' in text and ('senior' in text or 'current' in text):
                    squad_headline = span.parent
                    break

        if not squad_headline:
            print(f"Could not find squad section for {team_name}")
            return []

        # 見出しの直後にあるテーブルを取得
        table = None
        # セクション階層に関わらず、次のH2が現れるまで、または複数の兄弟要素を走査
        # Vector 2022では mw-heading div の場合もある
        start_node = squad_headline
        if squad_headline.parent and 'mw-heading' in str(squad_headline.parent.get('class', [])):
            start_node = squad_headline.parent

        curr = start_node.find_next_sibling()
        # 探索範囲を広げる（最大20要素先まで）
        count = 0
        while curr and count < 20:
            # 次の大きな見出し(H2)が現れたら終了
            if curr.name == 'h2' or ('mw-heading' in str(curr.get('class', [])) and curr.name != 'div'): 
                break
            
            # wikitableを探す
            if curr.name == 'table' and 'wikitable' in curr.get('class', []):
                table = curr
                break
            
            # divの中にテーブルが入っている場合がある（特にモバイル表示や特定のテンプレート）
            nested_table = curr.select_one('table.wikitable')
            if nested_table:
                table = nested_table
                break
                
            curr = curr.find_next_sibling()
            count += 1
        
        if not table:
            print(f"Could not find wikitable after squad section for {team_name}")
            return []

        # テーブル内の全リスト項目(li)とリンク(a)を走査
        for li in table.select('li'):
            # 国籍取得
            nat = ""
            flag = li.select_one('.flagicon a')
            if flag and flag.has_attr('title'):
                nat = flag['title'].replace('national rugby union team', '').strip()
            
            # 選手名取得（最後のリンクを優先）
            links = li.select('a')
            target_link = None
            for a in reversed(links):
                # フラグアイコンや画像リンクを除外
                if 'flagicon' not in str(a.parent) and 'image' not in str(a.get('class', [])) and \
                   'Captain (sports)' not in a.get('title', ''):
                    target_link = a
                    break
            
            if target_link:
                name = clean_name(target_link.get_text())
                if name and name != team_name and len(name) > 3:
                    players.append({"name_en": name, "nationality": nat, "team": team_name})

        # 重複排除
        seen = set()
        unique_players = []
        for p in players:
            if p['name_en'] not in seen:
                seen.add(p['name_en'])
                unique_players.append(p)

        print(f"Found {len(unique_players)} players for {team_name}.")
        return unique_players
    except Exception as e:
        print(f"Error scraping {team_name}: {e}")
        return []

def main():
    all_players = []
    for team, url in TEAM_PAGES.items():
        all_players.extend(scrape_team_squad(team, url))
        time.sleep(1) # Wikipediaへの負荷軽減
    
    if all_players:
        df = pd.DataFrame(all_players)
        output_path = "data_sources/premiership_wikipedia_fullnames.csv"
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Saved {len(all_players)} players to {output_path}")
    else:
        print("No players found.")

if __name__ == "__main__":
    main()
