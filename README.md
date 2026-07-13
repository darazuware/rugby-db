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

## データパイプライン（構築中）
- `pipeline/` — スクレイピング→検証→data/master/ 書き込み（data/master/ は pipeline/ 以外から書き換え禁止）
- `data/legacy/`, `scripts/archive/legacy/` — 旧資産。読み取り参照のみ
