# 01 名鑑縮小 設計書（T1, 2026-10-04）

## 0. 現状（実データ）
- 選手ページの実体は `src/pages/players/[...slug].astro`（prerender）。データ源は `data/master/players/*.json`（SSOT）を `src/lib/master.ts#getAllPlayers` 経由で読む（player_merges適用済み）。`src/content/players/**`（5,382件）は**旧レガシー**で、カタカナ補完・旧UI（PlayerList / TeamPlayerList の非master分 / API）にだけ使われている。
- master: 7,129件、高校生を除いた個別ページは**6,738件**。内訳: university 1,197 / national 1,157 / top14 894 / urc 745 / LO-D1 733 / premiership 552 / LO-D2 439 / LO-D3 337 / super-rugby 334 / mlr 211 / age-grade 113 / sevens 26。
- 名鑑の中身は大半が身長・体重・出身校のみ（6項目中1項目以下が3,498件）。
- **重複人物**: 日本代表（team_id=japan, 71件）の多くは all.rugby の `ar_*` と リーグワンの `lo_*` で別ページになっている（英名一致で44件）。同一人物2ページ＝低品質判定を助長。
- チームページ（`src/pages/teams/[league]/[slug].astro`）には既に `TeamPlayerList`（React）の名簿があり、各行が `/players/{slug}/` へリンク。LOはmaster roster、海外リーグはレガシーmdの文字列一致。
- 既存の削除URL処理: `src/middleware.ts` が `data/master/_meta/redirects.json`（301）と `retired_slugs.json`（→/players 301）を処理。ビルドされていない `/players/*` はSSRに落ちるので middleware で 301 を返せる（実績あり）。
- 年齢: 選手ページ・LOのチーム名簿は `calcAge(birthdate)` でビルド時計算済み。**固定値が残っているのは** `PlayerList.tsx` / `TeamPlayerList.tsx`（海外リーグ分）/ `NationalPlayerList.tsx` / `api/v1/all-players-download.json.ts` が読むレガシーmdの `age` フロントマター（例: 森太志 age:37 のまま）。
- GSC: `.env` の OAuth refresh token が失効（invalid_grant）で選手ページ別の流入は取得不可。→T2前に再認可できれば「過去90日クリック≥1の選手」を強制残しに追加（任意）。

## 1. 個別ページを残す基準（=indexable）
次のいずれかを満たす選手のみ個別ページを生成する。
| ID | 条件 | 根拠データ |
|---|---|---|
| K1 日本代表・代表候補 | `team_id=="japan"` / `caps.team=="Japan" && count>0` / `data/master/callups/national.json` の members に `player_id` がある（統合先に読み替え） | master / callups |
| K2 独自素材あり | `data/master/players/episodes/{id}.json` がある / `data/manual/instagram_embeds.json` に slug がある | episodes / IG |
| K3 記事で2本以上言及 | 公開済みニュース（draft除外）のうち、`/players/{slug}/` リンク または 一意な name_ja（4文字以上・link_news.pyと同じ辞書）を本文に含む記事が**2本以上** | src/content/news |
| 手動 | `force_include` / `force_exclude`（下記ファイル） | 手動 |

- 算出結果（2026-10-04、重複統合後）: **315人**（national 126 / LO-D1 66 / premiership 63 / top14 31 / urc 13 / mlr 7 / super-rugby 5 / university 3 / age-grade 1）。6,738 → 315（-95%）。
- 「解説文を書ける根拠」= 関連記事2本以上 or エピソード or 代表招集事実。テンプレ文＋関連ニュース一覧＋同窓つながりで本文に独自性が出る層に限定。リーグワン出場数だけの基準（caps≥50で+180人）は中身が増えないため採用しない。
- 記事が増えれば言及数が増え自動で昇格（ビルド時に再計算しないで済むよう、リストはスクリプト生成→commit）。
- 見込みサイトマップ: 非選手391 + 選手315 ≒ 約700URL（選手比率 95%→約45%）。

### リストの実体
- 新規 `scripts/build_player_pages.py` → 生成物 `data/manual/player_pages.json`
  ```json
  {"_note":"scripts/build_player_pages.py が生成。force_* のみ手編集可","generated_at":"…",
   "criteria":"K1|K2|K3(mention>=2)","force_include":[],"force_exclude":[],
   "players":[{"id":"lo_484374","slug":"futoshi-mori","reasons":["K1","K3"]}]}
  ```
- data/master は書き換えない（読み取りのみ）。生成は news 追加時に `link_news.py` の前に実行（pipeline の monitor_news CI にも1ステップ追加）。

### 重複統合（K1算出の前提）
- `data/manual/player_merges.json` に `ar_* → lo_*`（team_id=japan かつ英名正規化で lo_ が1件だけ一致）の44件を追加。既存運用（ar_→lo_）と同方向。追加前に44件の一覧を目視（同名別人がいないか、生年月日一致を確認できるものは確認）。
- 統合で消える `ar_*` の slug は 301 で統合先 slug へ（middleware、§2）。

## 2. 残さない選手のURL処理 → **301 リダイレクト（チーム名簿アンカーへ）**
| 案 | 判断 |
|---|---|
| noindex | ✗ 6,400ページが残り続け、審査クローラー・訪問者は普通に到達し広告も載る。「有用性の低いページが多い」状態は解消しない。ビルド時間も減らない |
| 削除(404/410) | ✗ 被リンク・既存インデックスの評価を捨てる。名前検索の受け皿がなくなる |
| **301 → チームページの名簿行** | ◎ ページ自体が消えるので低品質ページ数が実際に減る。評価はチームページに集約。遷移先に本人の行（名前・ポジション・出身校・年齢）があり関連性が高い |

- ページ生成: `canHaveIndividualPlayerPage(p)` を「高校生でない かつ player_pages.json に含まれる」に変更 → getStaticPaths から外れ、@astrojs/sitemap からも自動で消える。
- 301 先の決定（`src/lib/master.ts` に `playerFallbackPath(player)` を新設、middleware と全リンク生成で共用）:
  1. 所属チームのページが存在 → `/teams/{league}/{teamSlug}/#p-{slug}`
  2. チーム不明・ページなし → `/leagues/{league}/`（存在する場合）
  3. それ以外 → `/players/`
- `src/middleware.ts`: 既存 redirects/retired 処理の後に「master に存在し indexable でない slug」「merge で消えた slug」を 301。`Cache-Control: public, max-age=3600`（基準変更で復活し得るため immutable にしない）。
- 既存 `retired_slugs.json`（→/players）・`redirects.json` はそのまま。チェーン（旧slug→新slug→チーム）は1ホップ化: redirects.json の行き先が非indexable なら middleware で直接最終先へ。

### 内部リンクへの影響と対処
共通ヘルパー `playerHref(player)` = indexable なら `/players/{slug}/`、そうでなければ `playerFallbackPath`（名簿アンカー）を返す。リンクを生成する全箇所をこれに置換し、内部リンクが301を経由しないようにする。
- `scripts/link_news.py`: players 辞書を player_pages.json の選手に限定（非indexable選手には新規リンクを張らない。所属クラブは既存のclub辞書で既にリンクされる）。`--fix-dead` を追加し、既存記事内の非indexable `/players/{slug}/` リンクを `playerFallbackPath` 相当URLへ書換え（現状 1,150 slug へのリンク、215記事）。
- `pipeline/news_gen.py`（auto記事の選手リンク）・`pipeline/episodes.py`: player_pages.json を読み同じ判定。
- K3 は「リンク or 名前の本文出現」で数えるので、リンク書換え後も基準が揺れない。

## 3. 年齢の方針
- SSOT は `birthdate`。`age` フィールド（レガシーmd・API出力）は**一切表示に使わない**。
- `src/lib/playerText.ts#calcAge` を `YYYY-MM-DD` に加え `YYYY.MM.DD` / `YYYY/MM/DD` も受けるよう拡張（レガシーmdの birth_date 形式）。
- サーバー描画（選手ページ・チーム名簿・代表ページ）: ビルド時 `calcAge`。CIが毎日複数回デプロイするので実質当日値。
- React（PlayerList / TeamPlayerList / NationalPlayerList）: props で birthdate を渡し、ブラウザで `calcAge` を呼ぶ（常に閲覧日基準）。age によるソート・「25歳」検索も計算値で行う。
- `api/v1/all-players-download.json.ts`: age を calcAge で出力（固定値を出さない）。
- ニュース本文の「◯歳」は記事日付時点の記述なので変更しない。

## 4. 変更ファイル一覧（T2）
| ファイル | 変更 |
|---|---|
| `scripts/build_player_pages.py`（新規） | §1の基準で `data/manual/player_pages.json` を生成。件数とリーグ内訳を出力 |
| `data/manual/player_pages.json`（新規・生成物） | indexable 選手リスト |
| `data/manual/player_merges.json` | ar_→lo_ 44件追加 |
| `src/lib/master.ts` | `canHaveIndividualPlayerPage` 変更、`isIndexablePlayer` / `playerHref` / `playerFallbackPath` 追加（team_id→チームページslugの対応は masterAdapters の `findMasterTeamBySlug` の逆引き＋海外は data/*_teams*.json） |
| `src/lib/playerText.ts` | calcAge の日付形式拡張 |
| `src/middleware.ts` | 非indexable・統合slug の 301 |
| `src/pages/teams/[league]/[slug].astro` / `src/components/TeamPlayerList.tsx` | 名簿を表形式（名前・ポジション・出身校・年齢）に。各行に `id="p-{slug}"`。名前リンクは indexable のみ。年齢は birthdate から計算 |
| `src/pages/players.astro` / `src/components/PlayerList.tsx` | /players を「注目選手」一覧（indexable 315人、サーバー描画）に変更。5,400件の client fetch 一覧は廃止またはリンクを playerHref 化 |
| `src/pages/leagues/[league].astro` / `src/pages/teams/[league]/index.astro` | PlayerList のリンクを playerHref 化 |
| `src/pages/national-teams/[slug].astro` / `src/components/NationalPlayerList.tsx` | 年齢計算化、リンク playerHref 化 |
| `src/components/RightSidebar.astro` / `src/lib/connections.ts` / `src/pages/schools/[slug].astro` | 選手リンクを playerHref 化（同窓つながり・学校名簿） |
| `src/pages/api/v1/all-players-download.json.ts` | age 計算化 |
| `src/content/config.ts` | `age` を optional 化（未使用） |
| `scripts/link_news.py` | 辞書限定＋`--fix-dead` |
| `pipeline/news_gen.py` / `pipeline/episodes.py` | 選手リンク判定に player_pages.json を使用 |
| CI（monitor_news のワークフロー） | 記事生成後に `build_player_pages.py` を実行 |
| `astro.config.mjs` | 変更不要（非生成ページは自動除外）。念のため sitemap filter で `/players/` を player_pages.json に限定 |

## 5. T2 作業手順
1. `scripts/build_player_pages.py` 作成・実行 → 約315人を確認（大きくずれたら原因をレポート）。merge 44件の一覧を出して目視後 `player_merges.json` に追加し、再実行。
2. `master.ts` にヘルパー追加、`canHaveIndividualPlayerPage` 変更、`calcAge` 拡張。単体テスト（`src/lib/__tests__`、python3.11 ではなく vitest）を追加・更新。
3. `middleware.ts` に 301 追加。
4. チーム名簿を表形式＋アンカー化、/players を注目選手一覧に。全リンク生成箇所を `playerHref` に置換（`grep -rn "/players/\${" src` で漏れ確認）。
5. 年齢: React 3コンポーネントと API を calcAge 化。
6. `link_news.py --fix-dead --write` で既存記事リンク書換え → `link_news.py --write`。pipeline 側の判定変更。CIに生成ステップ追加。
7. `astro build` 成功、`dist` のサイトマップで `/players/` が約315件・総URL約700件を確認。
8. ブラウザ確認: 残す選手ページ（例: 齋藤直人）、非indexable選手URL→チーム名簿の該当行へ301、統合された ar_ slug→lo_ slug へ301、チームページ名簿表、/players、年齢が当日計算値。
9. commit/push → TASKS.md 更新・Telegram。

## 6. リスク
- 301 先のチームページに本人行が無いケース（海外リーグは文字列一致名簿）→ T2で `playerFallbackPath` の解決不能件数を出し、行が無いなら league/`/players` へ。
- 基準の境界で記事1本の追加/削除により個別ページが出たり消えたりする → 生成リストをcommit管理し、消える方向（2→1本）は force_include で保護可能。T3（短信統合）で記事が統合されると言及数が減る可能性 → T3後に build_player_pages.py を再実行し差分確認。
