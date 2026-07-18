# rugbypicks

ラグビー選手名鑑サイト（Astro製）。リーグワン・海外リーグ・日本代表の選手/チーム情報と記事を掲載。

## ドキュメント
- 大幅刷新の設計・タスク: [docs/renewal/](docs/renewal/)（着手前に 00_MASTER_PLAN.md と 09_TASKS.md を読む）
- NC2026自動記事システム: [docs/nc2026/](docs/nc2026/)

## 開発
```sh
npm install
npm run dev      # 開発サーバー
npm run build    # 本番ビルド（dist/）
```

## データパイプライン
- `pipeline/` — スクレイピング→検証→data/master/ 書き込み（data/master/ は pipeline/ 以外から書き換え禁止）
- `data/legacy/`, `scripts/archive/legacy/` — 旧資産。読み取り参照のみ
- 自動更新: `.github/workflows/daily_update.yml`（毎日06:00 JST + 試合日23:30 JSTの軽量更新、workflow_dispatchで手動実行可）
  - `python3 -m pipeline.run --all` → `python3 -m pipeline.news_gen` → 成功時のみ commit & push、Discord通知（`DISCORD_WEBHOOK` Secret）

## セキュリティ注意事項
- `.github_token` が過去コミット `f368e4747` で誤ってリポジトリに追加されていました（現在は `.gitignore` 済みで追跡外）。
  **当該トークンは漏洩済みとみなし、GitHub側で失効・再発行してください。** 詳細・対応手順は [Issue #1](https://github.com/darazuware/rugby-db/issues/1) 参照。
- `.env` / `.github_token` は `.gitignore` 済み。Secrets は GitHub Actions の Secrets 機能を使い、コードや `.env` に書かない。
