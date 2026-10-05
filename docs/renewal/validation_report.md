# data/master 整合性検証レポート（修正案）

- 対象: `data/master/` 全ファイル（2026-10-05 時点 main `4b491a5`）
- 検証スクリプト: `pipeline/validate/master_audit.py`（読み取り専用。master へは書き込まない）
  - 実行: `python3 -m pipeline.validate.master_audit --md docs/renewal/validation_findings.md --json <任意パス>`
  - 全件リスト: [`validation_findings.md`](validation_findings.md)（1,527件 = error 79 / warn 1,278 / info 170）
- 方針（03_VALIDATION.md 準拠）
  - 判定根拠は **master / manual 内データ同士の突合のみ**。AI の知識で値を補完・断定していない。
  - 修正は全て「スクレイパー / transform / manual ファイル側の修正 → pipeline 再実行」で行う。master の手編集は提案しない。
  - 「公式確認」= 内部データだけでは正誤を決められず、出典ページ（league-one.jp / all.rugby / rugby-japan.jp / 各校公式）で確認が必要な項目。

凡例: 🔴 error（データ誤りがほぼ確実） / 🟡 warn（不整合・表記ゆれ） / ⚪ info（運用判断）。【公式】= 公式ソース確認が必要。

---

## 1. 最優先（🔴 error）

### 1-1. クラブ roster の混入（4パターン・62人）【公式】
- 根拠: `teams/*.json` の full roster で、同一選手が複数クラブに同時所属。
  - `glasgow`(urc) + `gloucester`(premiership) + `la-rochelle`(top14): **28人**
  - `bath` + `dragons` + `pau`: **27人** / `gloucester` + `la-rochelle`: 4人 / `harlequins` + `pau`: 3人
  - 例: `ar_archie-griffin` は urc=glasgow, premiership=gloucester, top14=la-rochelle, national=wales。身長も 192/196/180/178 と各レコードで別値。
- 判断: 特定の3クラブ組に集中しており、個人の移籍では説明できない。all.rugby の squad ページ取得で別クラブのページ（またはキャッシュ）が混入した疑い。
- 修正案: `pipeline/scrape` の all.rugby squad 取得を確認（URL 組立・リダイレクト追従・キャッシュキー）。修正後に urc / premiership / top14 を再取得。checks.py に「1選手が複数 full roster に所属 → error」を追加。

### 1-2. U17 代表データが旧年度名簿（22件・u17 全件）【公式】
- 根拠: `players/age-grade.json` の `squad=u17` 22件はすべて birthdate が 2002〜2003年（2026年時点 23〜24歳）。うち12件は name_ja+birthdate が League One 在籍選手と一致（例: `jrfu_u17_319616` 福田大晟 2002-10-29 = `lo_484153`）。ID も 3196xx と他 squad（4960xx〜5053xx）より古い。
- 判断: u17 スクレイパーが過去年度の名簿ページ（member/detail/3196xx）を取得している。
- 修正案: u17 の取得 URL を当年度名簿に修正し再取得。checks.py に「squad=uN と birthdate の年齢矛盾 → error」を追加。

### 1-3. 順位表の欠損・シーズン不明・古いデータ残存【公式】
| ファイル | 問題 | 根拠 |
|---|---|---|
| `standings/top14_2026-27.json` | rank 1-3, 12-14 欠落（8/14行） | last_run: pau / lyon / la-rochelle / toulon / vannes / racing-92 を「数値欠落のため行を除外」 |
| `standings/mlr_unknown.json` | rank 1 欠落（chicago）、season=`unknown` | last_run: chicago 行除外 |
| `standings/super-rugby_unknown.json` | season=`unknown` | ファイル名・season とも unknown |
| `standings/premiership_2025-26.json` / `urc_2025-26.json` | scraped_at=2026-08-18 のまま（teams は 09-28） | 09-28 実行で全行が「数値欠落で除外」→ ファイル未更新で旧データ表示 |
- 修正案: all.rugby table パーサの数値列抽出を修正（行除外が上位チームに集中＝表構造の変化疑い）。season はページ表記から取得（取れなければファイルを出さない）。行欠落時は standings を出力しない（部分表示を避ける）よう transform を変更。

### 1-4. 試合データの参照切れ・表記ゆれ
- `matches/national_2026.json` の全8試合で home/away team_id（`japan`, `japan-xv`, `italy`, `france`, `australia`, `ireland`, `canada`, `scotland`, `maori-all-blacks`）が teams に存在しない。`teams/national.json` が空配列。→ 代表チームの teams レコードを生成するか、matches の team_id を national 用の別名前空間として checks に明記。
- 🟡 `japan`(7件) と `japan-xv`(1件: `jrfu_29964` vs maori-all-blacks) が混在。【公式】JAPAN XV 名義の別扱いか表記ゆれかを試合ページで確認。
- 🟡 `jrfu_29969`（2026-07-11, finished, 20-36）の venue_raw=`未定`。試合前取得値が残存。→ 再スクレイプ。【公式】
- 🟡 `jrfu_30035`（venue_raw=Queensland Country Bank Stadium）と `jrfu_29986`（Scottish Gas Murrayfield Stadium）が home=japan。日本開催の他6試合は venue_raw が日本語、かつ `callup_national_54111` は「オーストラリア遠征」。ホーム/アウェイ逆転の可能性。【公式】

### 1-5. 代表招集（callups）の日付・参照
- `callup_national_53968`: title「（9/21更新）男子日本代表 宮崎合宿」なのに start_date=`2027-03-01`。news_id は4件中最小（53968 < 54087 < 54111 < 54139）だが start_date は最も遅く、順序が逆転。メンバーのキャップも他3件より小さい（例: 大塚 壮二郎 0 → 3 → 4 → 5、岡部 崇人 8 → 11 → 12 → 13; news_id 順）。→ 前年の記事で、年補完ロジックが誤って未来年を付与した疑い。【公式】記事掲載日を確認し、スクレイパーで掲載年を取得。
- player_id 参照切れ 8件: `jrfu_national_510411/510424/510431/510438/510441/510663/510683/511558`。同一人物（平野 叶翔）に 510431 / 510683 / 511558 の3 ID が振られており、JRFU の合宿ごと member ID を player_id に使っている。→ 名前+生年月日で既存選手 id に解決する処理を callups に追加。
- player_id=null 9件。name_ja に英字名が連結（例: `池田 悠希 ※2. Yuki IKEDA`）＝列分割の失敗。

### 1-6. 重複・slug 衝突
- 🔴 dup_slug 19件: `lo_announced_*`（source=manual-curated）が既存 `ar_*` と同じ slug を使用（例: `james-lowe`, `kurt-lee-arendse`）。同一 slug で2ページが競合。→ 同一人物なら player_merges.json に登録、または announced 側 slug を `-lo` 等で分離。【公式】同一人物確認
- 🔴 dup_person: `lo_announced_jumpei-ogura` と `lo_484838`（小倉順平 1992-07-11、同リーグ）。公式名鑑に掲載済みなので announced 側を announced_transfers.json から除去。
- 同様に announced と公式名鑑の二重登録（同リーグ・name+birthdate 一致）: `pari-pari-parkinson`/`lo_483550`, `rintaro-maruyama`/`lo_484536`, `ryoi-kamei`/`lo_483557`, `shinichi-tanaka`/`lo_483678`。

### 1-7. 名簿パースで人名以外を取り込み（2件）【公式】
- `univ_國學院大學__経済学部経済学科`（name_ja=`経済学部　経済学科`）
- `univ_慶應義塾大学__慶應志木派遣学生コーチ`（name_ja=`慶應志木 派遣学生コーチ`）
- 修正案: university スクレイパーの行判定に学部・役職語の除外を追加し再取得。

### 1-8. エピソード参照切れ（1件）
- `players/episodes/jrfu_callup_ruan-botha.json` の player_id が players にも player_merges にも無い。master には `jrfu_national_511566` と `lo_483765`（ともに name_ja ルアン・ボタ / 1992-01-10）が存在。→ player_merges 登録後、canonical id にリネーム。【公式】同一人物確認

---

## 2. 不整合・表記ゆれ（🟡 warn）

| # | 項目 | 件数 | 根拠・例 | 修正案 | 公式 |
|---|---|---|---|---|---|
| 2-1 | 同一 id のリーグ間で身長体重不一致 | 756 | `ar_alex-maughan` mlr 190cm / national 174cm。差8cm以上が 430件超（national×club が大半）。mlr は他リーグと一致 10 / 不一致 47 | 1-1 の roster 混入と同根の疑い。混入修正後に再判定。残差は「最新 scraped_at 優先」を transform に明文化 | 要 |
| 2-2 | 同一人物候補（name+birthdate 一致・merge 未登録） | en 35 / ja 37 | sevens `jrfu_sevens_m_510767` 荻田直弥 = `lo_483542`、`jrfu_u18_*` = `jrfu_u20_*`（6組）、`jrfu_national_511552` = `lo_483494` | 確認後 player_merges.json に登録（自動マージしない） | 要 |
| 2-3 | `_meta/merge_candidates.json` が現データと不一致 | 37 | 記録2件（iwaihara, fukuda）は既に解消、現データの35組が未記録 | 次回 run で再生成 | |
| 2-4 | 代表キャップのソース間差 | callup 35 / リーグ間 10 | `ar_takato-okabe` callup最新13 / all.rugby 19。`ar_scott-sio` Australia 60 と Samoa 2、`ar_jean-kleyn` Ireland 5 と South Africa 15 がリーグ間で別 caps.team | 時点差なら許容。caps.team が別国のものは表示ルール（最新代表）を決める | 要 |
| 2-5 | callup / player の name_ja に注記 `※n.` 混入 | callup 28 / national 4 | `北條 拓郎 ※1. ※11.`（`jrfu_callup_takuro-hojo` の players レコードにも混入） | スクレイパーで注記を除去し別フィールド化 | |
| 2-6 | callup と player の name_en 不一致 | 15 | `Michael STOLBERG` vs `Mike STOLBERG`、`Esei HAANGANA` vs `Esei HA'ANGANA` | schemas.JAPAN_NAME_ALIASES 適用範囲を callups にも | |
| 2-7 | name_ja「空白+中黒」 | d1 232 / d2 104 / d3 42 | `ギディオン ・コーヘレンバーグ` | transform で `\s*・\s*` → `・` | |
| 2-8 | カタカナ名の区切り混在（・ と 空白） | d1/d2/d3 | d1: ・252 / 空白23 | 同上で統一 | |
| 2-9 | name_kana がひらがな | univ 661 / hs 204 | `いのうえさくたろう` | 他リーグはカタカナ。transform で ひらがな→カタカナ変換 | |
| 2-10 | name_ja 全角空白・注記・英字 | univ 350 ほか | 詳細は findings `name_format` | transform で正規化 | |
| 2-11 | 国籍表記の体系混在 | JP 146 / Japan 31 | age-grade・sevens・national(jrfu) は `JP`、league-one・national(all.rugby) は `Japan`。`United-States`（slug 由来ハイフン）31 | どちらかに統一（kana_coverage の判定も `JP` 前提のため影響あり） | |
| 2-12 | ポジション表記ゆれ | univ / national | univ: `NO.8` 44 と `NO8` 10、区切り `/`・`・`・空白 混在。national: 詳細ポジションと `FW`/`BK`（jrfu 由来7件）混在 | 正規化表を transform に追加 | |
| 2-13 | 学校マスタの重複・誤分類 | 32 / 5 | `桐蔭学園高校` と `桐蔭学園高等学校` 等31組、`kings`/`kings-2` 等。`College`・`Grammar`・`Highschool` が type=univ の独立校として登録（name_raw 分割ミス） | school_aliases.json（現在空）に統合定義。断片名は migrate_schools を修正 | |
| 2-14 | education.school_id が全件 null | 5,409 | schools.json と未接続 | name_raw→school_id 解決を transform に組込 | |
| 2-15 | チーム名が slug のまま | 17 | mlr / super-rugby の `name_en='blues'` 等、name_ja も null | 公式表記をソースから取得（推測で埋めない） | 要 |
| 2-16 | slug の先頭/末尾/連続ハイフン | 47 | `ar_beno--obano-`, `ar_kenji-sato-`, `ar_-juan-segundo-martin-montilla` | all.rugby 側 slug 由来か確認のうえ slug 正規化+redirect | 要 |
| 2-17 | manual-curated レコードが league-one-d1 に混在 | 40 | `lo_announced_*`。source=manual-curated、キー13種（is_minor, image_url 等）欠落 | 00原則1と緊張関係。公式名鑑掲載後に除去する運用と、全キー出力を徹底 | |
| 2-18 | redirects / retired の不整合 | 18 / 79 / 1,435 | リダイレクト先 slug が存在しない18件（例 `/players/faf-de-klerk-390`）。リダイレクト元が現役 slug と同一79件（例 `/players/ardie-savea`）。retired_slugs の1,435件が現 master で有効 | redirects/retired を現 master から再計算 | |
| 2-19 | 順位表 played のばらつき | super-rugby | played 12 と 13 が混在（season=unknown） | シーズン確定後に再判定 | 要 |

## 3. 運用判断（⚪ info）
- エピソード（`players/episodes/`）の出典44件が ALLOWED_DOMAINS 外（rugby-rp.com, kubota-spears.com）。エピソードに許可リストを適用するかは人間が決定。
- `kana_overrides.json` に master に存在しない id 74件（離脱・マージ済み）。害は無いが整理対象。
- caps.team が nationality に含まれない 35件（例 `caps.team='Usa'`）。表記体系の違いによるものが中心。
- name_en 全大文字（ソース表記そのまま）。表示側で整形する前提なら対応不要。

## 4. checks.py（CI ゲート）への追加提案
現行 `checks.run_all` では上記の多くを検出できない。03 の改訂として人間の承認を得たうえで以下の追加を提案:
1. `roster_multi_team`: 1選手が複数 full roster に所属 → error（1-1）
2. `age_grade_age`: squad=uN と birthdate の矛盾 → error（1-2）
3. `standings_complete`: rank 欠番・season=unknown → error、行欠落時は前回値を保持しない（1-3）
4. `match_team_ref`: matches の team_id 参照（1-4）
5. `callup_ref`: callups.player_id 参照・start_date と news_id 順序（1-5）
6. `slug_unique`: リーグ横断 slug 衝突 → error（1-6）

本レポートと findings は `master_audit.py` 再実行で再生成できる。修正後の再検証もこのスクリプトで行う。
