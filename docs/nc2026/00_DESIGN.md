# 00 設計書 — ネーションズチャンピオンシップ2026 自動記事システム（NC2026）

> 設計: Fable（本書）。実装・運用は Sonnet / Haiku / 他エージェントが本書と 01_TASKS.md だけで完結できること。
> docs/renewal/00_MASTER_PLAN.md の絶対原則（SSOT・事実と文章の分離・不明はnull・出所記録・検証ゲート）を全面継承する。

## 目的
NC2026（開催中）の試合・チームニュースについて、
1. 事実収集 → 2. 他媒体の見解収集 → 3. 分析・再構築 → 4. 記事ドラフト生成 → 5. ユーザー確認 → 6. `/publish` で本番デプロイ
を回す。加えて負傷離脱・メンバー変更を複数ソースから常時監視して通知する。

## 担当モデル（コスト設計）
| 工程 | 担当 | LLM使用 |
|---|---|---|
| 事実スクレイプ・監視 | GitHub Actions（Python、cron） | なし（無料） |
| 見解記事の収集（fetch・本文抽出） | Python | なし |
| 見解の要約・帰属付け | セッション内 Haiku サブエージェント | 小 |
| 記事ドラフト生成・分析 | セッション内 Sonnet | 中 |
| /publish（検証→コミット→push） | 任意のモデル（手順はスキルに全記載） | 極小 |

Fable は運用に不要。運用の入口は3つのスラッシュコマンド（`.claude/commands/`）のみ。

## 絶対原則（renewal継承 + 追加）
1. 事実（スコア・日程・選手名・負傷情報）は `data/nc2026/facts/` と bundle 内の facts のみから書く。AIの知識で補完禁止。
2. 見解・所感は必ず**帰属付き**（媒体名・執筆者・URL・日付）。無帰属の「〜と言われている」は禁止。
3. 引用は1記事1箇所まで・原文15語（日本語50字）以内・カギ括弧＋出典リンク必須。それ以外は要約・言い換え。
4. 独自分析セクションは「RUGBY PICKS編集部の見解」であることを本文中に明記。
5. `/publish` は `pipeline/nc/validate.py` を通過しない限り実行不可。

## ディレクトリ構成
```
pipeline/nc/                 # 本システムのコード（Python）。data配下を書けるのはここだけ
  collect_facts.py           # 日程・結果・スコッド → data/nc2026/facts/
  collect_voices.py          # 見解ソースのfetch・本文抽出 → data/nc2026/voices/raw/
  monitor.py                 # 負傷・離脱監視 → events/ + Discord通知
  bundle.py                  # facts+voices+event を1トピックに束ねる → bundles/
  validate.py                # 公開前検証ゲート
data/manual/nc2026_sources.json   # ソース定義（唯一の手動編集ファイル）
data/nc2026/
  facts/    matches.json standings.json squads.json（source_url, scraped_at 必須）
  voices/raw/<id>.json       # 収集した記事（url, author, published_at, 本文テキスト）
  monitor/  seen.json events/<id>.json
  bundles/<slug>.json        # ドラフト生成の入力
src/content/news/<slug>.md   # 記事（draft: true で生成）
.claude/commands/  nc-collect.md  nc-draft.md  publish.md
.github/workflows/nc2026_monitor.yml
```

## データスキーマ
### sources.json（手動編集可・唯一の設定）
```json
{
  "facts":  [{"id":"allrugby_nc","type":"html","url":"<実装時に疎通確認>","target":"matches"}],
  "voices": [{"id":"rugbypass","type":"rss","url":"<候補: rugbypass.com/feed>","lang":"en"},
             {"id":"guardian_rugby","type":"rss","url":"<候補: theguardian.com rugby-union RSS>","lang":"en"},
             {"id":"rugby_rp","type":"html","url":"<ラグビーリパブリック>","lang":"ja"}],
  "x_accounts": [],
  "monitor_keywords": {
    "injury": ["injury","injured","ruled out","sidelined","負傷","離脱","欠場"],
    "withdrawal": ["withdrawn","replacement","called up","招集","追加招集","辞退"],
    "team_news": ["team named","starting XV","lineup","メンバー発表","先発"]
  }
}
```
URLは実装タスクで疎通確認してから確定させる（本書の候補を無検証で使わない）。

### event（monitor出力）
```json
{"id":"20260713-rugbypass-a1b2","type":"injury","detected_at":"...","source_id":"rugbypass",
 "url":"...","title":"...","excerpt":"先頭300字","matched_keywords":["ruled out"],
 "status":"new"}   // new → bundled → drafted → published / ignored
```

### bundle（ドラフト生成入力）
```json
{"slug":"nc2026-r3-japan-wales","topic":"...","created_at":"...",
 "facts":{"matches":[...],"squads":[...]},           // facts/ からの抜粋コピー
 "voices":[{"source":"RugbyPass","author":"...","url":"...","published_at":"...",
            "summary_ja":"（Haikuが書く帰属付き要約）","quote":null}],
 "events":["20260713-..."]}
```

## 監視（nc2026_monitor.yml）
- cron: 2時間おき（試合日 = 土日は1時間おき）。手動 workflow_dispatch も可。
- monitor.py: sources.json の voices+facts を巡回 → 新規URLを seen.json と突合 →
  keywords 分類にヒットしたら event 作成 + `scripts/discord_notify.py` 流用で Discord 通知。
- X監視は Phase 2（01_TASKS.md T8）。API費用が発生するため、当面は各媒体のサイト/RSSで代替。
- 誤検知対策: 同一選手・同一typeの event は48時間デデュープ。

## 記事フロー（運用手順そのものはスキルに記載）
1. `/nc-collect <トピック or event-id>` — collect_facts + collect_voices 実行 → Haiku が voices を帰属付き要約 → bundle 生成。
2. `/nc-draft <slug>` — Sonnet が bundle **のみ**を根拠に `src/content/news/<slug>.md` を `draft: true` で生成。
   構成: ①事実（bundleのfactsから機械的に）②各所の反応（帰属付き）③編集部の分析（意見と明記）。
3. ユーザーが dev プレビューで確認（本番ビルドでは draft は除外）。
4. `/publish <slug>` — validate.py 通過 → `draft: false` → commit → push（Vercelが自動デプロイ）。

## validate.py（公開ゲート）
- frontmatter: title / pubDate / category:"nc2026" / sources(1件以上のURL) / bundle パス必須
- bundle が存在し、voices の各URLが frontmatter.sources に含まれる
- 本文中の数値（スコア・キャップ数等）は bundle 内に存在する数値のみ（正規表現抽出で突合、日付・見出し番号は除外）
- 引用（カギ括弧50字超）が2箇所以上あれば fail
- 「編集部の見解」明記チェック

## サイト側変更（最小）
- news collection スキーマに `draft`(default false), `sources: string[]`, `bundle` を追加
- news の getStaticPaths / index で `import.meta.env.PROD && data.draft` を除外
