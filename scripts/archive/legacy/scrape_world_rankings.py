import requests
import json
import os
import sys

# 国名マッピング (English -> Japanese)
COUNTRY_MAP = {
    "South Africa": "南アフリカ",
    "Ireland": "アイルランド",
    "New Zealand": "ニュージーランド",
    "France": "フランス",
    "England": "イングランド",
    "Scotland": "スコットランド",
    "Argentina": "アルゼンチン",
    "Italy": "イタリア",
    "Fiji": "フィジー",
    "Australia": "オーストラリア",
    "Wales": "ウェールズ",
    "Georgia": "ジョージア",
    "Samoa": "サモア",
    "Japan": "日本",
    "Portugal": "ポルトガル",
    "Tonga": "トンガ",
    "Uruguay": "ウルグアイ",
    "Spain": "スペイン",
    "USA": "アメリカ",
    "Romania": "ルーマニア",
    "Canada": "カナダ",
    "Chile": "チリ",
    "Namibia": "ナミビア",
    "Hong Kong China": "香港",
    "Netherlands": "オランダ",
    "Russia": "ロシア",
    "Brazil": "ブラジル",
    "Belgium": "ベルギー",
    "Switzerland": "スイス",
    "Germany": "ドイツ",
    "Zimbabwe": "ジンバブエ",
    "Kenya": "ケニア",
    "Algeria": "アルジェリア",
    "Uganda": "ウガンダ",
    "Côte d'Ivoire": "コートジボワール",
    "Paraguay": "パラグアイ",
    "Madagascar": "マダガスカル",
    "Tunisia": "チュニジア",
    "Senegal": "セネガル",
    "Mauritius": "モーリシャス",
    "Morocco": "モロッコ",
    "Nigeria": "ナイジェリア",
    "Colombia": "コロンビア",
    "Kazakhstan": "カザフスタン",
    "Sri Lanka": "スリランカ",
    "Philippines": "フィリピン",
    "Malaysia": "マレーシア",
    "South Korea": "韓国",
    "China": "中国",
    "Cook Islands": "クック諸島",
    "Papua New Guinea": "パプアニューギニア",
}

# 旗マッピング (Japanese/English -> Emoji)
FLAG_MAP = {
    '日本': '🇯🇵',
    'オーストラリア': '🇦🇺',
    'ニュージーランド': '🇳🇿',
    '南アフリカ': '🇿🇦',
    'フィジー': '🇫🇯',
    'トンガ': '🇹🇴',
    'サモア': '🇼🇸',
    'フランス': '🇫🇷',
    'イングランド': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
    'ウェールズ': '🏴󠁧󠁢󠁷󠁬󠁳󠁿',
    'スコットランド': '🏴󠁧󠁢󠁳󠁣󠁴󠁿',
    'アイルランド': '🇮🇪',
    'イタリア': '🇮🇹',
    'アルゼンチン': '🇦🇷',
    'アメリカ': '🇺🇸',
    'カナダ': '🇨🇦',
    'ジョージア': '🇬🇪',
    'ウルグアイ': '🇺🇾',
    'ポルトガル': '🇵🇹',
    'ルーマニア': '🇷🇴',
    'ナミビア': '🇳🇦',
    'チリ': '🇨🇱',
    '韓国': '🇰🇷',
    '中国': '🇨🇳',
    '香港': '🇭🇰',
    'オランダ': '🇳🇱',
    'スペイン': '🇪🇸',
    'ロシア': '🇷🇺',
    'ブラジル': '🇧🇷',
    'ベルギー': '🇧🇪',
    'スイス': '🇨🇭',
    'ドイツ': '🇩🇪',
    'ジンバブエ': '🇿🇼',
    'ケニア': '🇰🇪',
    'アルジェリア': '🇩🇿',
    'ウガンダ': '🇺🇬',
    'コートジボワール': '🇨🇮',
    'パラグアイ': '🇵🇾',
    'マダガスカル': '🇲🇬',
    'チュニジア': '🇹🇳',
    'セネガル': '🇸🇳',
    'モーリシャス': '🇲🇺',
    'モロッコ': '🇲🇦',
    'ナイジェリア': '🇳🇬',
    'コロンビア': '🇨🇴',
    'カザフスタン': '🇰🇿',
    'スリランカ': '🇱🇰',
    'フィリピン': '🇵🇭',
    'マレーシア': '🇲🇾',
    'クック諸島': '🇨🇰',
    'パプアニューギニア': '🇵🇬',
}

def fetch_rankings(category):
    # category: 'mru' for mens, 'wru' for womens
    url = f"https://api.wr-rims-prod.pulselive.com/rugby/v3/rankings/{category}?language=en"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        effective_date = data.get("effective", {}).get("label", "Unknown")
        entries = data.get("entries", [])
        
        rankings = []
        for entry in entries:
            team = entry.get("team", {})
            en_name = team.get("name")
            jp_name = COUNTRY_MAP.get(en_name, en_name)
            
            # 旗の取得 (マッピングにない場合は国コードから推測を試みるが、基本は空にする)
            flag = FLAG_MAP.get(jp_name, FLAG_MAP.get(en_name, ""))
            
            rankings.append({
                "rank": entry.get("pos"),
                "previousRank": entry.get("previousPos"),
                "points": entry.get("pts"),
                "team_en": en_name,
                "team_jp": jp_name,
                "abbreviation": team.get("abbreviation"),
                "flag": flag
            })
            
        return effective_date, rankings
    except Exception as e:
        print(f"Error fetching {category} rankings: {e}")
        return None, []

def main():
    print("Fetching World Rugby Rankings...")
    
    m_date, m_rankings = fetch_rankings("mru")
    w_date, w_rankings = fetch_rankings("wru")
    
    if not m_rankings and not w_rankings:
        print("Failed to fetch any rankings.")
        sys.exit(1)
        
    result = {
        "updated_at": m_date if m_date else w_date,
        "mens": m_rankings,
        "womens": w_rankings
    }
    
    output_path = "/Users/ktamatzmoto/Desktop/rugbypicks/data/world_rankings.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
        
    print(f"Rankings saved to {output_path}")
    print(f"Men's: {len(m_rankings)} teams, Women's: {len(w_rankings)} teams")

if __name__ == "__main__":
    main()
