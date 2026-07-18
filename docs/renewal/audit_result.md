# P2-5 既存記事の事実監査結果

実施日: 2026-07-18
対象: `src/content/teams/` `src/content/news/` の既存記事
参照: `docs/renewal/03_VALIDATION.md`（既存記事の事実監査）
突合先SSOT: `data/master/players/{league-one-d1,league-one-d2,league-one-d3,top14}.json`、`data/master/teams/{同}.json`

## 0. 監査可能範囲（重要な前提）

`data/master/` の現状（2026-07-18時点でコミット済みのもの）は以下のみ:

| データ種別 | league-one D1/D2/D3 | top14 | super-rugby / premiership / urc | matches（試合結果） | standings（順位表） |
|---|---|---|---|---|---|
| players | ○ | ○ | ×（未収載） | - | - |
| teams（roster_ids含む） | ○ | ○ | ×（未収載） | - | - |
| 試合スコア・順位表 | - | - | - | ×（ディレクトリ空） | ×（ディレクトリ空） |

そのため今回の監査で**選手所属の突合が可能だったのは league-one と top14 の記事のみ**。
super-rugby / premiership / urc の記事（チーム紹介37本＋ニュース45本前後）は master にデータが無く、
**突合そのものが不可能**（矛盾の有無を判定できない＝draft化の対象外。原則3「不明はnull」に倣い、
無いものを「矛盾あり」と決めつけない保守的判断）。同様に、全リーグの試合結果・順位表・得失点差などの
数値記事も master に比較対象データが無いため機械的な突合は不可能。

## 1. 突合方法

1. `data/master/players/{league-one-d1,d2,d3,top14}.json` からチームID別の選手名（name_ja）索引を作成
2. league-one 26チーム・top14 14チームの各紹介記事（`src/content/teams/`）と関連ニュース（`src/content/news/`）に
   登場する選手名を正規化（空白除去）して抽出
3. 「その記事が主張する所属チーム」と「masterのteam_id」を突合し、不一致を矛盾候補として個別確認
4. 高校別輩出数など集計値を主張する記事は、masterのeducation配列を同条件で再集計して数値を検算

## 2. 矛盾を確認し draft: true にした記事（4件）

### 2-1. ノラン・ル・ガレック（Nolann LE GARREC）の所属誤り
masterでは `career` に `Racing 92 (2017–2025) → Stade Rochelais (2025–2026)` と記録されており、
2025-26シーズンの所属は **la-rochelle（ラ・ロシェル）**。以下3記事はラシン92（Racing 92）所属として
記述しており矛盾。

- `src/content/teams/top14/racing-92.md` — 本文で「次世代のエース」としてラシン92所属と明記
- `src/content/news/top14-racing-92-2025-26.md` — 本文＋代表選手テーブルにラシン92在籍として掲載
- `src/content/news/top14-league-guide-2025-26.md` — ラシン92の紹介文＋全チーム比較表の「注目選手」欄に記載

### 2-2. TJ・ペレナラ（TJ Perenara）の所属誤り
masterでは `source: league-one.jp`（公式サイト、2025-26シーズンの出場記録付き）で
`team_id: lo_team_108 = リコーブラックラムズ東京`。以下の記事は「レッドハリケーンズ大阪」所属として
記述しており矛盾。

- `src/content/news/league-one-team-guide-2025-26.md` — 「レッドハリケーンズ大阪」の節で
  「TJ・ペレナラ（NZ代表SH）が在籍」と明記

上記4件は frontmatter に `draft: true` を追加し非公開化した（本文は削除していない）。

## 3. 監査インフラの補修（本タスクに付随して必要だった変更）

`src/content/news/` の記事には `draft` フィールドの定義が `src/content/config.ts` の news
スキーマに存在せず、かつ `src/pages/news/index.astro` と `src/pages/news/[slug].astro` にも
draft除外ロジックが無かった（teams コレクションのみ既存で対応済み）。draft化しても実際には
非公開にならない状態だったため、以下を追加した:

- `src/content/config.ts`: news スキーマに `draft: z.boolean().optional().default(false)` を追加
- `src/pages/news/index.astro`: 一覧取得を `getCollection("news", entry => !entry.data.draft)` に変更
- `src/pages/news/[slug].astro`: `getStaticPaths` を同様にフィルタ＋詳細ページでも `entry.data.draft` なら404

`npm run build` で正常終了、上記4記事が生成物から除外されることを確認済み（team側は既存の
`!a.data.draft` ロジックにより本文ブロックのみ非表示、ページ自体は既存仕様どおり残存）。

## 4. 突合して矛盾なしと確認できた主な項目（サンプル）

- top14: トゥールーズ（斎藤直人・アントワーヌ・デュポン）、クレルモン（マルコス・クレメル）、
  ラ・ロシェル（グレゴリー・アルドリット）、リヨン（ダヴィト・ニニアシヴィリ、バティスト・クイユー）、
  モンペリエ（ビリー・ヴニポラ）、スタッド・フランセ（セク・マカルー）、トゥーロン（シャルル・オリヴォン）
  — いずれも記事の所属主張がmasterと一致（表記ゆれのみ、実害なし）
- league-one: コベルコ神戸スティーラーズ優勝記事の登場選手（ブロディ・レタリック、李承信、
  ティエナン・コストリー、具智元、山下裕史）、埼玉ワイルドナイツのダミアン・デアレンデ、
  三重ホンダヒートのパブロ・マテーラ／レメキ ロマノ ラヴァ — 全員masterの所属と一致
- `league-one-2025-26-data-analysis.md` の高校別輩出数（東福岡60名、桐蔭学園38名など）は、
  masterのeducation配列を学校名表記ゆれ込みで再集計した結果とほぼ一致（東海大仰星「名寄せ後49名」も
  表記ゆれ6パターンを合算すると49と一致し、記事側の主張が正しいことを確認）

## 5. 個別に判定不能だった項目（矛盾とは断定せず、要フォローとして記録のみ）

- `src/content/news/top14-league-guide-2025-26.md` の「トゥーロン: エベン・エツェベス」——
  masterのtop14.jsonに該当選手のレコードが無い（トゥーロンのロースター自体は51名収載）。
  在籍している可能性は高いが、masterに無い＝「矛盾の証明」はできないため draft化はしていない。
  次回スクレイプでロースターの再取得漏れが無いか確認推奨。
- `src/content/news/nations-championship-2026.md` の「SOアントワーヌ・デュポン」——
  masterのpositionは「スクラムハーフ」。SO表記が誤り（スタンドオフの意）である可能性があるが、
  記事の主旨（フランス代表の中心選手であること）自体に矛盾は無く、低優先度の表記ゆれとして記録のみ。
- `src/content/news/league-one-2025-26-kobe-champions.md` `league-one-2025-26-season-analysis.md` 等の
  最終順位表・得失点差・勝点などの数値 — 登場選手の所属はmasterと全一致したが、スコア自体はmasterに
  matches/standingsデータが無く数値の真偽を検証する手段が無い（監査対象外、上記0節参照）。

## 6. 対象外（監査不能）のまま残っている記事群

- `src/content/teams/{premiership,super-rugby,urc}/` 全37本
- `src/content/news/{premiership,super-rugby,urc}-*-2025-26.md` 等 約45本

これらはP1-6/P1-7で作成されたスクレイパー（`scrape/all_rugby.py`拡張、`scrape/jrfu.py`）の
実行結果がまだ `data/master/` にコミットされていないため対象外。該当リーグのmasterデータが
整備され次第、同じ手順で再監査が必要。

## 7. 完了条件チェック

- [x] `docs/renewal/audit_result.md` 出力（本ファイル）
- [x] 矛盾が確認できた記事 4件を `draft: true` 化（削除はしていない）
