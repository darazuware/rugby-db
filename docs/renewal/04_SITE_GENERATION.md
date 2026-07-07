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
  - **人物重複のマージを master.ts で吸収**: `player_merges.json` を読み、`merged_from` に含まれる id / merges で解決済みの重複 id は getStaticPaths から除外し、canonical レコードに代表情報を統合してから1ページだけ生成する。これをやらないと日本代表選手が lo_ と ar_ で2ページできる（01の人物同一性）。
- 旧URL → 新slug のリダイレクト。**旧slugは約4,953件で vercel.json redirects の上限(1024)を大きく超えるため、Astro 側を主方式にする**: `_meta/redirects.json` を読み、旧slugのルートで301を返す動的ルート（or `getStaticPaths` で旧slugページを生成し `Astro.redirect`）を作る。vercel.json には使わない。
  - 注意: 新slugは id接尾（`-lo483678`）が付き旧slugと必ず変わる。全URLが変わるため redirects.json の網羅性が SEO維持の生命線。移行(P1-4)で1件も取りこぼさないこと。

## 選手ページの本文（テンプレ生成文）
自由記述禁止。以下のテンプレに JSON 値を埋める関数を `src/lib/playerText.ts` に実装。値が null の文は**丸ごと出さない**。

```
{name_ja}（{name_kana}）は{team_name}所属の{position_ja}。
{birthdate}生まれ{age}歳、{height_cm}cm・{weight_kg}kg。
[caps有] {caps.team}代表キャップ{caps.count}。
[league_caps有] リーグワン通算{league_caps}キャップ。
[education有] {education で type=="univ" の name}出身。 ※education は配列(01)。type=="univ" の要素を選ぶ。is_minor=true の選手は 10 のポリシーでこの文自体を出さない。
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
