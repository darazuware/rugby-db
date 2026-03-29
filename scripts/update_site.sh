#!/bin/bash
# RUGBY PICKS データ更新・同期用スクリプト

# このスクリプトは、CSVファイルを更新した後に実行してください。
# 役割: CSVデータをサイト用のMarkdownに変換し、Astroのキャッシュをクリアします。

echo "--- RUGBY PICKS データの再生成を開始します ---"

# 1. 試合結果・キャップ数の更新
echo "最新の試合結果を取得中..."
python3 scripts/scrape_urc_results.py
python3 scripts/scrape_leagueone_results.py
python3 scripts/scrape_sr_results.py
python3 scripts/scrape_top14_results.py
python3 scripts/scrape_premiership_results.py

echo "リーグワン選手のキャップ数を更新中..."
python3 scripts/scrape_leagueone_caps.py

echo "高校・大学の選手情報を取得中..."
python3 scripts/scrape_jrfu_schools.py

# 2. 順位情報の更新 (all.rugby および各公式から最新取得)
echo "最新の順位情報を取得中..."
python3 scripts/scrape_standings.py

# 2. 選手情報の Markdown 再生成 (統合スクリプト：全リーグ対応)
echo "重複排除を実行中..."
python3 scripts/deduplicate_master.py

echo "全選手情報を生成中 (League One, SR, Top 14, URC)..."
python3 scripts/generate_players.py
if [ $? -ne 0 ]; then
    echo "❌ エラー: 選手情報の Markdown 生成に失敗しました。"
    exit 1
fi

echo "代表チーム情報を生成中..."
python3 scripts/generate_national_teams.py

# 3. チーム情報の更新 (Slug マッピング等)
echo "チーム情報を更新中..."
python3 scripts/generate_teams_json.py

# 4. Astro の型定義とコレクションを同期
echo "Astro コンテンツを同期中..."
npx astro sync

# 5. キャッシュのリセット (確実な反映のため)
echo "ビルドキャッシュをクリア中..."
rm -rf .astro node_modules/.vite

echo ""
echo "✅ --- すべての更新が完了しました！ ---"
echo "ローカルで確認する場合は 'npm run dev' を実行してください。"
