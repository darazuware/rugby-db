# 04 サイト生成 — SSOT駆動のAstro

## 方針
- 現在の見た目（UI/UX）は維持する。**デザインの作り直しはしない。** データの流し込み元を master に差し替える。
- 選手ページは Markdown コンテンツ生成をやめ、**Astroが master JSON を直接読む動的ルート**にする（6000件のmd生成・同期という現行の破綻ポイントを排除）。

## ページ構成
| ルート | データ源 | 備考 |
|---|---|---|
| `/players/[slug]` | `data/master/players/*.json` | getStaticPaths で全リーグ結合 |
| `/teams/[id]` | `teams/*.json` + roster | 既存 `src/content/teams/` の紹介記事は監査後(03)に本文として併載可 |
| `/leagues/[league]` | teams + standings | |
| `/standings/...` | `standings/*.json` | |
| `/results/...` | `matches/*.json` | |
| `/national-teams/...` | `players/national.json` + `matches/national_*.json` | |
| `/news/...` | 既存 content/news + 05の自動生成ニュース | |

- `src/lib/master.ts` を新設: master JSON の読み込み・リーグ結合・slug索引を一元化。各ページはこれ経由でのみデータ取得。
- 旧URL（既存 `src/content/players/` のslug）→ 新slug のリダイレクトを `_meta/redirects.json` から vercel.json の redirects に生成するスクリプトを作る（SEO維持。最大1000件超なら Astro 側で410/リダイレクトページ生成に切替）。

## 選手ページの本文（テンプレ生成文）
自由記述禁止。以下のテンプレに JSON 値を埋める関数を `src/lib/playerText.ts` に実装。値が null の文は**丸ごと出さない**。

```
{name_ja}（{name_kana}）は{team_name}所属の{position_ja}。
{birthdate}生まれ{age}歳、{height_cm}cm・{weight_kg}kg。
[caps有] {caps.team}代表キャップ{caps.count}。
[league_caps有] リーグワン通算{league_caps}キャップ。
[education有] {university}出身。
[career有] これまで{career各チーム名の列挙}でプレー。
[season_stats有] {season}シーズンは{matches}試合出場、{tries}トライ。
```

ポジション略号→日本語対訳表は `src/lib/positions.ts` に定数で持つ（PR=プロップ 等、全略号分）。

## 表示要素
- 各選手・チーム・順位表ページに「最終更新: {scraped_at} / 出典: {source表示名}」を小さく表示（信頼性＝サイトの差別化点）
- 有名選手（is_featured）は拡張レイアウト: Instagram埋め込み or イラスト（06）、キャリア年表、関連ニュース一覧
- 検索・フィルタ（ポジション/チーム/国籍）は既存UIを master 駆動に接続

## 完了条件
- `npm run build` が成功し、選手ページ数 ≒ master の選手数
- ランダムに選んだ選手10件で、ページ表示値と master JSON の値が完全一致
- 旧URLサンプル20件が新URLへ301される
- Lighthouse (モバイル) Performance 80以上を維持
