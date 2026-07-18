# 09 タスクリスト — 1セッション1タスクで実行

> 各タスクをSonnet/Opusの新規セッションに1つずつ依頼する。
> セッション冒頭の指示例:
> 「docs/renewal/00_MASTER_PLAN.md を読み、docs/renewal/09_TASKS.md のタスク {ID} を実施して。
>  参照指示書は {番号} のみ。完了条件を満たしたらコミットして終了。」

## Phase 0 — 整理
- [x] **P0-1** リポジトリ整理（08の全手順）。完了条件は08参照。

## Phase 1 — データ基盤
- [x] **P1-1** `pipeline/` 骨格 + `schemas.py`（pydantic、01準拠）+ `requirements.txt` + `io.py`。ユニットテスト: サンプルPlayer 1件が検証を通る/壊れた1件が落ちる。参照: 01, 02
- [x] **P1-2** `validate/checks.py`（03の全チェック実装）+ テスト（各チェックにpass/failのfixture）。参照: 03
- [x] **P1-3** `scrape/league_one.py` + `transform/normalize.py`（リーグワンD1-D3）。既存 `scripts/scrapers/league_one_scraper.py` を移植改修。完了条件: `--league league-one-d1 --dry-run` で選手・チーム・順位が取得され検証を通る。参照: 02
- [x] **P1-4** 既存 `data/unified_player_database_final.json` → 新スキーマ移行スクリプト `pipeline/migrate_legacy.py`。完了条件: master 初期化、migration_report.md 出力、null化した件数の報告、**`_meta/redirects.json`（旧slug→新slug）出力**、**旧トップリーグ地域カテゴリ(top-east/kyushu/west)と high-school/university 個別ページは master 化せず redirects 退避リストに記録**、education を配列形式で移行（school_id=null, name_raw）。参照: 01
- [x] **P1-4b** 人物同一性突合 `pipeline/merge_persons.py`: `lo_`×`ar_national` 等の同一人物候補を `_meta/merge_candidates.json` に出力（自動確定しない）。`data/manual/player_merges.json` を読み canonical へ統合。cross_person チェック(03)と連動。完了条件: 代表選手の重複候補が列挙され、merges 適用後に重複が0になる。参照: 01, 03
- [x] **P1-5** `scrape/all_rugby.py`（Top14）。完了条件: Top14チーム14・選手500+が検証を通る。参照: 02
- [x] **P1-6** all_rugby.py を Super Rugby Pacific に拡張。tournament key を実ページで確認しコメントに記録。参照: 02
- [x] **P1-7** 代表（national.json）: all.rugby の日本代表＋直近対戦国スコッド + `scrape/jrfu.py`（日程）。参照: 02
- [x] **P1-8** `diffs/detect.py`（移籍・キャップ差分、pending_departures の2回確認ロジック含む）+ テスト。参照: 02, 05

## Phase 2 — サイト刷新
- [x] **P2-1** `src/lib/master.ts` + `positions.ts` + `playerText.ts`（テンプレ文）。テスト: null項目の文が出ないこと。参照: 04
- [x] **P2-2** `/players/[slug]` を master 駆動に差替 + PlayerAvatar（③プレースホルダーのみ先行実装）。**master.ts で player_merges を適用し重複人物を1ページに統合**。完了条件: build成功、ページ数≒master件数（重複除外後）、抜き取り10件一致、代表選手が2ページになっていない。参照: 04, 06
- [x] **P2-3** teams / leagues / standings / results / national-teams を master 駆動に差替（league-one のみ実施、詳細はコミットメッセージ参照）。参照: 04
- [x] **P2-4** 旧URL→新URLリダイレクト（**Astro側を主方式**。vercel.json redirects 上限1024超のため使わない）。P1-4 が出した `_meta/redirects.json` を読む。旧地域カテゴリ/個別高校大学ページは一覧へ集約 or 410。完了条件: サンプル20件が301、退避リストのURLが404にならない。参照: 04
- [x] **P2-5** 既存記事の事実監査（03の手順）。完了条件: audit_result.md + 矛盾記事の draft 化。参照: 03
- [x] **P2-6** kanaバッチ: 未設定外国人の一覧生成 → カタカナ変換して `kana_overrides.json` へ（このタスクのみLLMによる変換を許可、03の手順厳守）。参照: 03

## Phase 3 — 自動化
- [x] **P3-1** `pipeline/news_gen.py`（差分→テンプレ記事）+ テスト（fixture差分から期待md生成）。参照: 05
- [x] **P3-2** `daily_update.yml` + `pipeline/notify.py`（Discord）。旧workflow削除。完了条件: workflow_dispatch で一気通貫成功。参照: 05
- [x] **P3-3** `weekly_audit.yml` + レポート/Issue起票。参照: 05

## Phase 4 — 収益化・画像・拡張
- [x] **P4-1** `affiliates.ts` + PR表記コンポーネント + 視聴ボタン（DAZN/スカパー、URLはプレースホルダー）。参照: 07
- [ ] **P4-2** venue_areas.json + 宿泊導線。参照: 07
- [ ] **P4-3** 視聴ガイド記事×3（draft、ユーザーレビュー待ちで止める）。参照: 07
- [ ] **P4-4** Instagram埋め込み + イラストフォールバック（PlayerAvatar完成形）+ illustrations_todo 生成。参照: 06
- [ ] **P4-5** RWC2027特集ページ（開催都市ガイド、宿泊・航空券導線はプレースホルダー）。参照: 07
- [ ] **P4-6** （任意）URC/Premiership: チームページ+日本人・スター選手のみ。**着手前にユーザーに要否確認。** 参照: 00

## Phase 5 — ユース・学生・セブンズ／U代表（P1-P3完了後。参照: 10）
- [ ] **P5-1** schools.json + Player に education/is_minor 追加 + 既存出身校データの移行
- [ ] **P5-2** is_minor のフィールド制限をサイト生成コードで強制 + 削除依頼窓口
- [ ] **P5-3** セブンズ/U代表スコッドスクレイパー（JRFU、Sonnetフォールバック付き）
- [ ] **P5-4** 学校ページ生成 + つながりグラフ強化（同期/先輩後輩/U20同期バッジ）
- [ ] **P5-5** 大学名簿スクレイパー（関東対抗戦A/B・リーグ戦1部/2部・関西A/B）
- [ ] **P5-6** 高校名簿スクレイパー（hs_target_schools.json の激戦区強豪校）

## 依存関係
P0-1 → P1-1 → P1-2 → {P1-3..P1-7並列可} → P1-4b（P1-7後: national取得後に突合）→ P1-8 → P2-1 → P2-2 → P2-3 → P2-4
P2-5, P2-6 は P1-4 以降いつでも。P3はP1-8とP2完了後。P4はP2-2以降いつでも。
P5はP3完了後。P5-1 → P5-2 → {P5-3..P5-6並列可}。

## 進捗管理
完了したらこのファイルのチェックボックスを [x] にしてコミットに含める。
