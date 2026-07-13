# 01 実装タスク — NC2026（1タスク = 1セッション、担当: Sonnet）

> 各タスクは 00_DESIGN.md を読んでから着手。完了条件を満たしたらコミットして終了。
> 質問はしない。不明点は「00の絶対原則に沿う最も保守的な選択」をしてコミットメッセージに明記。
> data/ の巨大JSONは全読み禁止。

## T1: ソース定義と facts コレクター
- `data/manual/nc2026_sources.json` を作成。00のスキーマ通り。voices は英語2＋日本語1以上、
  **各URLは curl で疎通確認してから記載**（候補: RugbyPass, The Guardian rugby-union RSS, Planet Rugby, ラグビーリパブリック, rugby365）。
- `pipeline/nc/collect_facts.py`: NC2026 の日程・結果を取得（第一候補: all.rugby。既存 `scripts/scrape_sr_results.py` の手法を流用）→ `data/nc2026/facts/matches.json`。全レコードに source_url / scraped_at。
- 完了条件: `python3 -m pipeline.nc.collect_facts` が実際の試合データを含む matches.json を生成し、null補完・推測値がないこと。

## T2: voices コレクター
- `pipeline/nc/collect_voices.py`: sources.json の voices を巡回（rss は feedparser 相当を自前実装可、html は requests+bs4）。
  NC関連判定（チーム名・"Nations Championship" 等のキーワード）を通った記事のみ
  `data/nc2026/voices/raw/<id>.json` に保存（url, title, author, published_at, text 全文, fetched_at）。
- robots.txt を尊重。取得間隔1秒以上。全文はリポジトリ内の raw/ に留め、**サイトに原文を出さない**。
- 完了条件: 実行で3媒体以上から NC 関連記事が保存される。

## T3: monitor + GitHub Actions + Discord通知
- `pipeline/nc/monitor.py`: 00の監視仕様通り（seen.json 突合 → keywords 分類 → events/ 作成 → Discord通知）。
  通知は `scripts/discord_notify.py` を流用し Webhook は Secrets `DISCORD_WEBHOOK`。
- `.github/workflows/nc2026_monitor.yml`: cron 2時間おき＋土日1時間おき、workflow_dispatch 可。
  events/seen の変更のみ commit & push（記事は触らない）。
- 完了条件: workflow_dispatch 手動実行で通知が届き、2回目実行で同一記事が再通知されない。

## T4: bundle 生成
- `pipeline/nc/bundle.py`: 引数（トピック文字列 or event-id）→ 関連 facts 抜粋＋関連 voices/raw の一覧を
  `data/nc2026/bundles/<slug>.json` に出力（voices の summary_ja は空のまま。埋めるのはスキル側のHaiku）。
- 関連判定: event の場合は同一URL＋タイトル類似、トピックの場合はチーム名・ラウンドのキーワードマッチ。
- 完了条件: 実イベント1件から bundle が生成され、00のスキーマに一致。

## T5: サイト側変更
- `src/content/config.ts` の news に `draft: z.boolean().optional().default(false)`, `sources: z.array(z.string()).optional()`, `bundle: z.string().optional()` を追加。
- `src/pages/news/index.astro` と `[slug].astro` で本番時 draft を除外（`import.meta.env.PROD`）。
- 完了条件: draft:true のテスト記事が `npm run dev` で見え、`npm run build` の dist に含まれない。テスト記事は確認後削除。

## T6: validate.py
- 00の「validate.py（公開ゲート）」仕様をそのまま実装。`python3 -m pipeline.nc.validate <slug>` で exit 0/1。
- 完了条件: 正常記事で0、①sources欠落 ②bundle外の数値 ③引用2箇所 の各異常系で1を返すテストケースを `pipeline/nc/tests/` に置き通過。

## T7: スキル3本
- `.claude/commands/nc-collect.md`: collect_facts → collect_voices → bundle 実行 → voices各記事を Haiku サブエージェントで帰属付き要約（summary_ja 埋め、引用は原則null）→ bundle 更新、の手順を**どのモデルでも実行できる粒度で**記載。
- `.claude/commands/nc-draft.md`: bundle のみを根拠に記事生成。00の3部構成・帰属・引用制限・「編集部の見解」明記・`draft: true` を明文化。**bundleにない事実を書いたら失敗**と書く。
- `.claude/commands/publish.md`: validate.py 実行 → 失敗なら中止して理由提示 → 成功なら draft:false に編集 → `git add <記事> && commit && push`。push前にユーザー確認は不要（/publish 自体が承認）。
- 完了条件: 3ファイル作成。nc-draft の出力例（雛形記事）を doc 内に含める。

## T8（Phase 2・保留）: X監視アダプタ
- sources.json の x_accounts を監視対象化。前提: X API有料枠 or 既存 x-trend-bot との連携をユーザーと合意してから着手。合意前に実装しない。

## 試運転（T1–T7完了後、ユーザー同席）
1. monitor が拾った実イベントで `/nc-collect` → `/nc-draft` → dev確認 → `/publish`
2. 公開URLと Discord 通知を確認して運用開始。
