# 05 自動更新 — GitHub Actions

## ワークフロー再編
既存 `.github/workflows/scrape_and_deploy.yml` / `update_data.yml` は削除し、以下2本に統合。

### 1) `daily_update.yml`（毎日 06:00 JST = cron `0 21 * * *`）
```
jobs:
  update:
    - checkout
    - setup-python 3.11 + pip install -r requirements.txt
    - python3 -m pipeline.run --all          # scrape→validate→diff→master更新
    - python3 -m pipeline.news_gen           # 差分→ニュース記事生成（下記）
    - 検証失敗(exit≠0)なら: コミットせず、Discord通知して終了
    - 成功なら: git add data/master src/content/news && commit && push
      （pushでVercelが自動デプロイ）
    - Discord通知: 取得件数・差分サマリ・warning数
```
試合日はシーズン中の結果反映が遅れるため、`matches/standings のみ`を対象にした軽量ジョブを
同ファイル内で 23:30 JST にも実行（`--only matches,standings`オプションをrun.pyに追加）。

### 2) `weekly_audit.yml`（毎週月曜）
- kana未設定リスト・null率レポート・リンク切れチェックを出力し、GitHub Issue を自動起票（既存 dispatch_issue.py 流用可）

## 差分検知 → ニュース自動生成（pipeline/news_gen.py）
`_meta/diff/` の差分から、**テンプレートのみ**でニュース記事mdを生成する。LLM不使用。

| 差分イベント | 検知方法 | 生成記事 |
|---|---|---|
| 加入 | 新idが出現 / team_id変化(移籍) | 「{選手名}が{チーム名}に加入」（海外リーグは下記の通り週次ダイジェストが既定） |
| 退団 | idがロスターから消失 | 「{選手名}が{チーム名}を退団」※移籍先検出時は移籍記事に統合（海外リーグは下記の通り週次ダイジェストが既定） |
| 初キャップ | caps 0/null → 1以上 | 「{選手名}が{国}代表初キャップ」 |
| キャップ更新 | caps増加 | 週次でまとめ記事（1件ずつは作らない） |
| 節の結果 | matches の finished 増加 | 「{リーグ}第{節}節 結果まとめ」（スコア表のみ） |

記事frontmatter: `title, pubDate, category: "NEWS", tags, source_diff: {diffファイル名}`。
本文はテンプレ文＋masterの値＋関連選手ページへのリンクのみ。**背景説明・感想・展望を書かない。**
foreign選手名でname_ja未設定の場合、`data/manual/kana_overrides.json`に確定表記があれば
「英語表記（カタカナ）」で併記する（03_VALIDATIONのカタカナ手順で確定させたもののみ）。

- 退団/消失は誤検知しやすいので、**2回連続の実行で消失が確認されたときのみ**記事化（1回目は `_meta/pending_departures.json` に保留）。

### 海外リーグの加入/退団は週次ダイジェストが既定（2026-08 改訂）
`OVERSEAS_LEAGUES = {top14, super-rugby, urc, premiership, nrl}` の加入/退団は、
スクレイプ元(all.rugby等)にキャップ・国籍データがほぼ無く「{選手名}が{チーム名}に加入」
1文だけの記事が大量に乱立していた（Adsense的にも薄いコンテンツ、カタカナ表記も無い）。
そのため既定では個別記事を作らず、caps_updatesと同じくISO週単位で
`_meta/news/join_weekly_{league}_{isoweek}.json` / `departure_weekly_...json` に累積し、
「{リーグ}週間加入まとめ（{ISO週}）」「{リーグ}週間退団まとめ（{ISO週}）」1本にまとめる
（同一週内は冪等）。

例外: `data/manual/notable_overseas_players.json` に選手idを明示登録した選手は、これまで通り
個別記事を生成する。登録基準は次のいずれかを満たし、かつ人が事実確認したもののみ:
  1. 日本に縁がある: 学校またはクラブで日本でプレーした経験がある
  2. 代表歴がある: 自国・出身国・縁のある国のいずれかでU19/U20/U23〜本代表の経歴がある
自動判定はしない（AIの知識で「該当しそう」等を推測して登録することを禁止、03_VALIDATION原則）。

## 通知
- 既存 `scripts/discord_notify.py` を `pipeline/notify.py` に移植。Webhook URLは GitHub Secrets `DISCORD_WEBHOOK`（.envやコードに書かない）。
- 通知内容: 成功/失敗、リーグ別件数、生成ニュース一覧、warning。

## セキュリティ
- リポジトリ直下の `.github_token` と `.env` が git 管理下にないか確認し、管理下なら履歴から除去して無効化・再発行を促す一文を README に記載（実装AIはトークンを再発行できないので、Issueを立ててユーザーに知らせる）。

## 完了条件
- workflow_dispatch で daily_update.yml を手動実行し、master更新→ニュース生成→デプロイ→Discord通知まで一気通貫で成功
- 検証を故意に失敗させた場合（テスト用ブランチ）にコミットされないことを確認
