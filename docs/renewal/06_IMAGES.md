# 06 画像 — Instagram埋め込み + AIイラスト

## 原則
- スクレイプした選手写真（league-one.jp の image_url 等）は**著作権上サイトに表示しない**。masterに参考情報として残すだけ。
- 表示は次の優先順: ① Instagram公式埋め込み → ② AIイラスト → ③ イニシャル入りプレースホルダーSVG

## ① Instagram埋め込み（is_featured 選手のみ）
- `data/manual/instagram_accounts.json`: `{"player_id": {"username": "...", "post_url": "..."}}` を人間が登録（AIがWeb検索でアカウントを推定して登録することは**禁止**。別人アカウント掲載は事故になるため、候補リスト提示までにとどめる）
- 表示は Instagram 公式の埋め込み（blockquote + embed.js）。プロフィールではなく本人の代表的な投稿URLを1件登録する形式にする（`{"player_id": {"username": "...", "post_url": "..."}}`）
- 埋め込みスクリプトは選手ページでのみ遅延読み込み（パフォーマンス対策）

## ② AIイラスト
- 対象: is_featured かつ Instagram 未登録の選手
- 生成はユーザーのAI環境（Antigravity等）で行う運用とし、パイプラインは**「生成待ちリスト」の自動管理**まで担当:
  - `pipeline/illustrations.py` が `data/manual/illustrations_todo.json` を生成（選手id・名前・ポジション・チームカラー）
  - 生成プロンプトのテンプレを同ファイルに含める: 「ラグビー選手のフラットなベクター風イラスト、{ポジション特徴}、ユニフォームは{チームカラー}、顔は特定人物に似せない、背景単色」
  - **実在選手の顔に似せる指定は禁止**（肖像権リスク）。あくまで「ポジション・体格・チームカラーの汎用イラスト」
- 完成画像は `public/illustrations/{player_id}.webp` に置くと自動で表示される（存在チェックで切替）

## ③ プレースホルダー
- 名前イニシャル＋チームカラーのSVGを `src/components/PlayerAvatar.astro` で動的生成。追加アセット不要。全選手のデフォルト。

## 完了条件
- PlayerAvatar が ①Instagram→②イラスト→③プレースホルダー の優先順で判定し、上位が無ければ下位へフォールバックする（ファイル/登録の存在で自動判定）
- featured選手1名でInstagram埋め込みが表示されるサンプルを確認
