# 08 リポジトリ整理（P0 — 最初に実施）

## 目的
約100本の一回限りスクリプトと30超のJSONが混在し、AIが誤ったファイルを参照する温床になっている。
**削除はせずアーカイブ**（過去のパースロジックを02で流用するため）。

## 手順
1. `scripts/archive/legacy/` を作り、scripts/ 直下の全 .py/.mjs/.sh を移動。
   例外（残す・後で pipeline に移植するもの）:
   - `scripts/scrapers/`（丸ごと残す。02で流用）
   - `scripts/discord_notify.py`
   - `dispatch_issue.py`（ルート。weekly_audit用）
2. `data/legacy/` を作り、data/ 直下の全JSONを移動。
   例外: `team_names_jp.json` → `data/manual/` へ。`unified_player_database_final.json` は移行(P1-4)が終わるまで data/ 直下に残す。
3. ルート直下の掃除:
   - `build_all.py`, `audit.csv`, `dev.log`, `dev_reboot_v5.log`, `gemini.md`, `content/`（ルートの）, `css/`, `images/`, `index.html`（Astro外の静的物） → `backups/pre_renewal/` へ移動。※`index.html` がデプロイに使われていないこと（vercel.jsonとastro出力を確認）を先に確認
   - `__pycache__`, `scripts/__pycache__` を削除し `.gitignore` に追加
4. **セキュリティ（最優先）**: `.github_token` と `.env` について
   - `git ls-files` で追跡状況を確認。追跡されていれば `git rm --cached` + `.gitignore` 追加 + 「トークン無効化・再発行が必要」とIssue起票
   - `git log --all -- .github_token .env` で過去コミット履歴も確認し、履歴に残っていればその旨もIssueに書く（履歴書換はユーザー判断）
5. `README.md` を刷新: プロジェクト概要・docs/renewal/ への導線・`pipeline/` の使い方だけの簡潔な内容に
6. `CLAUDE.md`（プロジェクト側）に追記:
   ```
   ## 実装ルール
   - 実装前に docs/renewal/00_MASTER_PLAN.md と担当タスク（09_TASKS.md）を読む
   - data/master/ は pipeline/ 以外から書き換え禁止
   - 選手・チーム・試合の事実をAIの知識で書かない（03参照）
   - scripts/archive/legacy/ と data/legacy/ は読み取り参照のみ
   ```

## 完了条件
- scripts/ 直下に残るのは `scrapers/` `archive/` `discord_notify.py` のみ
- `npm run build` が引き続き成功（既存サイトを壊さない）
- git status がクリーン（1コミットで完結、メッセージ: `chore: P0 リポジトリ整理`）
