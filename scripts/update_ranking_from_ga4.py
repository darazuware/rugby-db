import os
import json
import re
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    OrderBy,
)

# GA4 プロパティ ID
PROPERTY_ID = os.getenv('GA4_PROPERTY_ID', 'YOUR_PROPERTY_ID')
# サービスアカウントキーのパス (Google Cloud Console で生成)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'config/ga4-key.json'

def fetch_top_players():
    """GA4 から過去7日間の選手ページ閲覧数を取得し、ランキングを更新する"""
    client = BetaAnalyticsDataClient()

    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        # 選手ページ(/players/[slug])のみをフィルタリング
        dimension_filter={
            "field_name": "pagePath",
            "string_filter": {"match_type": "BEGINS_WITH", "value": "/players/"}
        },
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=20
    )

    response = client.run_report(request)
    
    ranking = []
    rank_count = 1
    
    # 選手データのマスター（スラッグ確認用）
    # ※ 本来は src/content/players/ から全スラッグを取得するのが理想的
    
    for row in response.rows:
        path = row.dimension_values[0].value
        views = row.metric_values[0].value
        
        # スラッグの抽出 (/players/antoine-dupont/ -> antoine-dupont)
        match = re.search(r'/players/([^/]+)/?', path)
        if match:
            slug = match.group(1)
            # 既にリストにあるか確認 (クエリパラメータ等による重複回避)
            if any(item['id'] == slug for item in ranking):
                continue
            
            ranking.append({
                "id": slug,
                "rank": rank_count
            })
            rank_count += 1
            if rank_count > 10: break

    return ranking

import pandas as pd

def update_ranking_json(new_ranking):
    """取得したスラッグに日本語名等を追加して data/access_ranking.json を保存"""
    output_path = 'data/access_ranking.json'
    csv_path = 'data_sources/final_master_data_v27_normalized.csv'
    
    # マスターCSVの読み込み
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    final_ranking = []
    for item in new_ranking:
        slug = item['id']
        # スラッグに合致する選手を検索 (URLの末尾がスラッグと一致)
        player_row = df[df['Scraped_Url'].str.endswith(slug, na=False)].head(1)
        
        if not player_row.empty:
            row = player_row.iloc[0]
            final_ranking.append({
                "id": slug,
                "name": str(row.get('Player_Name', '')),
                "name_jp": str(row.get('選手名_カタカナ', row.get('Full_Name', ''))).replace('-', ' '),
                "team_jp": str(row.get('Current_Team', '')),
                "rank": item['rank']
            })
        else:
            # 見つからなかった場合はIDのみ（後部でフィルタリングされる可能性あり）
            final_ranking.append({
                "id": slug,
                "name": slug.replace('-', ' ').title(),
                "name_jp": "データ準備中",
                "team_jp": "---",
                "rank": item['rank']
            })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_ranking, f, ensure_ascii=False, indent=2)
    
    print(f"Updated {output_path} with {len(final_ranking)} players.")

if __name__ == "__main__":
    try:
        data = fetch_top_players()
        if data:
            update_ranking_json(data)
    except Exception as e:
        print(f"Error fetching GA4 data: {e}")
        print("Note: credentials and property ID are required for real execution.")
