# 03 検証ゲート — ハルシネーション根絶の仕組み

## 3層の防御
1. **スキーマ検証（pydantic）** — 型・形式。`pipeline/schemas.py`
2. **整合性チェック** — `pipeline/validate/checks.py`
3. **CI強制** — 検証を通らないデータはコミット・デプロイされない（05）

## スキーマ検証
- 01のスキーマをpydanticモデル化。必須: `id`, `source`, `source_url`, `scraped_at`, `name_en` or `name_ja`, `league`, `team_id`
- `height_cm` 150-230、`weight_kg` 60-170、`birthdate` は1970〜2010年の範囲。範囲外は null に落として warning。
- `source_url` はソースごとの許可ドメインのみ: `league-one.jp`, `all.rugby`, `jrfu.jp`（＋Phase4で追加）。**それ以外のドメインが混じったら即エラー**（=出所不明データの混入防止）。

## 整合性チェック（checks.py に実装）
| チェック | 内容 | 違反時 |
|---|---|---|
| dup_id | id 重複 | エラー |
| dup_person | 同一リーグ内で name_en+birthdate が重複 | エラー |
| team_ref | player.team_id が teams/*.json に存在 | エラー |
| roster_sym | team.roster_ids と players の相互参照が一致 | エラー |
| shrink | 前回比で選手数が30%以上減少 | エラー（サイト構造変化の検知） |
| caps_monotonic | 同一選手のキャップ数が前回より減少 | warning + 該当項目は前回値を維持 |
| match_sanity | finished以外にスコアがある / スコアが0-150外 | エラー |
| standings_sum | 順位表の played = won+drawn+lost | エラー |
| kana_coverage | name_kana が null の外国人選手数 | warningのみ（レポート） |

エラー1件でも exit 1。masterは更新しない。warningは `_meta/last_run.json` に記録。

## AI実装者への禁止事項（最重要）
実装AI（Sonnet/Opus）は以下を **絶対にしない**:
- スクレイプで取れなかった値を知識で補完する（キャップ数、経歴、移籍情報、生年月日等）
- 選手・チーム・試合に関する文章を自由記述で書く（04のテンプレのみ使用）
- master/ 配下のJSONを手で編集する
- 検証エラーを「チェックを緩めて」通す（緩和はこのファイルの改訂として人間が承認）
- テストのためにダミーの選手・試合データを master に入れる（fixtureは `tests/fixtures/` へ）

## カタカナ表記（name_kana）の扱い
外国人名のカタカナ化だけはLLMを使ってよい。ただし:
1. 対象は `name_kana: null` の選手のみ。バッチで一覧を作り、LLMが変換案を `data/manual/kana_overrides.json` に追記（`{"ar_12345": "アントワーヌ・デュポン"}` 形式）
2. transform 時に overrides を適用。**LLMの出力先は overrides ファイルのみ**で、masterに直接書かない
3. 一度確定した表記は再生成しない（表記ゆれ防止）

## 既存記事の事実監査（P2で1回実施）
`src/content/teams/` `src/content/news/` の既存記事について:
- 記事中の固有の事実（選手名・所属・成績・スコア）を master と突合するチェックリストをAIが作成し、矛盾箇所を `docs/renewal/audit_result.md` に列挙
- 矛盾が1つでもある記事は frontmatter に `draft: true` を付けて非公開化（削除はしない）。修正は master 由来の値への置換のみ許可
