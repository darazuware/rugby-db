# 12 再申請前の再点検（2026-10-24）

計測: 本番 rugbypick.com はこの作業環境から接続不可。代わりに最新コード（HEAD 0623604）を本番設定でビルドし、下書き非表示の状態で全URLを描画して計測。方法は 06_AUDIT と同じ（`<main>` 内テキスト、script/style/nav 除く。/contact 295字で前回と一致）。数値 12_audit_textlen.tsv。

## 薄いページ比率

| | 10/5 監査 | 10/24 |
|---|---:|---:|
| サイトマップURL | 600 | 204 |
| 800字未満 | 345（57%） | 17（8.3%） |
| └ 選手 | 271/277 | 7/13 |
| └ チーム | 58/150 | 5/94 |
| └ その他 | 16 | 5（contact, terms, schools 61字, world-rankings 101字※, national-teams 485字） |

※world-rankings は外部API取得失敗時の表示。本番の状態は未確認。
11_THIN_CONTENT_PLAN の70本は全件実行済み（非公開53・統合13・残す3・noindex1）。

## 判定

| 観点 | 結果 | 判定 |
|---|---|---|
| 薄いページ比率 | 8.3%（目標10%以下） | ○ |
| 自動生成・テンプレ記事 | premiership-join-weekly-2026-w37（64名の加入一覧、自動生成）が公開中。計画の「週次は単独公開しない」に反する | × |
| データページ比率 | チーム94・代表25・選手13＝サイトマップの65% | △ |
| 転送先の404 | transfers-roundup-2026-09 が draft のため、旧URL24件の301転送先が404 | × |
| 内部リンク切れ | テスト test_news_internal_links は合格。全ページ実測では選手リンク15件が404（national-callups-2026 14件、japan-vs-canada-2026-review 1件） | × |
| E-E-A-T | 運営者プロフィール・筆者欄あり。ただし出典の明記は公開ニュース60本中3本。利用規約に「スクレイピングによる自動取得データを含みます」 | △ |
| ナビ | ニュース先頭、フッターに about/privacy/contact/terms | ○ |
| ポリシー | privacy（AdSense・Cookie記載）、contact（フォーム）、terms | ○ |
| ads.txt | `google.com, pub-7526742711058970, DIRECT, f08c47fec0942fa0` | ○ |
| モバイル | 幅375pxで全204URLの横はみ出し0 | ○ |
| 広告枠 | 選手ページの手動広告ユニットに data-ad-slot が無い（不正なユニット） | × |
| その他 | フィジー戦レビューで「ベン・ヴォラヴォラ」が3か所 /leagues/super-rugby/（noindexページ）にリンク | △ |
