# 01 データ設計 — SSOT（単一の正データ）

## ディレクトリ
```
data/
  master/                  # ★正データ。スクレイパーのみが書く。手編集禁止
    players/
      league-one-d1.json
      league-one-d2.json
      league-one-d3.json
      top14.json
      super-rugby.json
      national.json        # 代表スコッド（日本＋直近対戦国）
    teams/
      {league}.json        # 上と同じリーグキー
    matches/
      {league}_{season}.json   # 例: top14_2025-26.json
    standings/
      {league}_{season}.json
    _meta/
      last_run.json        # 各スクレイパーの最終実行時刻・件数
      diff/                # 実行ごとの差分レポート（05で使用）
  manual/                  # 人間が管理する少数の補助データのみ
    featured_players.json  # 単独ページ対象のスター選手リスト
    kana_overrides.json    # 外国人名カタカナ表記の確定表
    instagram_accounts.json
    team_names_jp.json     # 既存 data/team_names_jp.json を移動
  legacy/                  # 既存の data/*.json を全部ここへ退避（08参照）
```

## リーグキー（全コードで統一）
`league-one-d1` `league-one-d2` `league-one-d3` `top14` `super-rugby` `national`
（Phase4: `urc` `premiership` `nrl`）

## Player スキーマ（players/*.json は Player の配列）
```json
{
  "id": "lo_483678",
  "source": "league-one.jp",
  "source_url": "https://league-one.jp/player/483678",
  "scraped_at": "2026-07-07T09:00:00+09:00",
  "name_en": "Shinichi Tanaka",
  "name_ja": "田中 真一",
  "name_kana": null,
  "slug": "shinichi-tanaka-lo483678",
  "position": "FL",
  "team_id": "kyuden-voltex",
  "league": "league-one-d1",
  "height_cm": 186,
  "weight_kg": 98,
  "birthdate": "1994-06-08",
  "nationality": ["JP"],
  "caps": { "team": "Japan", "count": 12, "source_url": "..." },
  "league_caps": 9,
  "career": [
    { "team": "NEC Green Rockets", "from": 2017, "to": 2020, "source_url": "..." }
  ],
  "season_stats": { "season": "2025-26", "matches": 5, "tries": 0, "points": 0 },
  "education": [
    { "school_id": null, "name_raw": "明治大学", "type": "univ", "grad_year": null, "source_url": "...", "scraped_at": "..." }
  ],
  "instagram": null,
  "is_featured": false,
  "is_minor": false,
  "merged_from": []
}
```

### ルール
- **id**: `{prefix}_{ソース側ID}`。prefix: `lo`（league-one.jp）/ `ar`（all.rugby）。ソースIDが取れない場合のみ `slug` ベース。
- **slug**: `name_en` のkebab-case + `-` + id接尾。既存URLからの変更は `data/master/_meta/redirects.json` に旧→新を記録（04でリダイレクト生成）。
- **不明値は null**。空文字・"不明"・推測値は禁止。
- **caps / career は取得できたソースの値のみ**。all.rugby の career_path、league-one.jp の代表歴欄以外から作らない。
- 数値は数値型（既存データは "186" のような文字列が混在。変換すること）。
- 日付は `YYYY-MM-DD`。パースできない場合は null。
- **education は配列**（10のユース設計と同一形式。P1移行時点では出身校名を `name_raw` に入れ `school_id: null`。school_id は P5-1 の schools.json 構築時に正規化して埋める）。`type` は `hs`|`univ`。テンプレ生成(04)は type で高校/大学を判定する。
- **is_minor**: 高校生など未成年レコードは true。true のときサイト生成側でフィールド制限を強制（10）。リーグワン/代表の成人選手は false。

## 人物同一性（同一選手の重複防止）★P1から必須
- 日本代表選手はほぼ全員リーグワン所属のため、`league-one-*.json`（`lo_` ID）と `national.json`（`ar_` ID）に**同一人物が別IDで入る**。放置すると /players/[slug] が同一選手ページを2枚生成する（03のdup_personはリーグ内チェックのため検出しない）。
- **canonical_id 方式**: 別ソースの同一人物を検出したら、片方（原則リーグ所属の `lo_` 側）を canonical とし、もう片方の `id` を canonical の `merged_from[]` に追加、重複レコード自体は master から除外する。
- 自動突合は候補提示まで（キー = `name_en` 正規化 + `birthdate` 一致、birthdate欠損時は `name_ja`+チーム）。**確定は `data/manual/player_merges.json`**（`{"ar_12345": "lo_483678"}` = 重複ID→canonical）に人が記録。pipeline は突合候補を `_meta/merge_candidates.json` に出力するのみ。
- national.json はスコッド事実（キャップ等）を保持するため、選手の代表情報（caps/national squad）は canonical レコードにマージして反映する。

## Team スキーマ
```json
{
  "id": "kyuden-voltex",
  "league": "league-one-d1",
  "name_ja": "九州電力キューデンヴォルテクス",
  "name_en": "Kyuden Voltex",
  "source_url": "...", "scraped_at": "...",
  "home_area": "福岡県",
  "home_stadiums": [ { "name": "...", "source_url": "..." } ],
  "founded": null,
  "colors": { "primary": "#123456" },
  "official_url": "...",
  "roster_mode": "full",
  "roster_ids": ["lo_483678", "..."]
}
```
`roster_mode`: `full`（全スコッド収集）| `partial`（00でチーム＋一部選手のみと定義した urc/premiership/nrl 等）。partial は 03 の roster_sym 検証を免除。

## Match スキーマ
```json
{
  "id": "top14_2025-26_r12_toulouse-racing",
  "league": "top14", "season": "2025-26", "round": 12,
  "kickoff_utc": "2026-01-10T20:05:00Z",
  "home_team_id": "toulouse", "away_team_id": "racing-92",
  "home_score": 27, "away_score": 20,
  "status": "finished",
  "venue": null,
  "source_url": "...", "scraped_at": "..."
}
```
`status`: `scheduled` | `finished` | `postponed`。未実施の試合にスコアを入れない。

## Standing スキーマ
```json
{ "league": "top14", "season": "2025-26", "scraped_at": "...", "source_url": "...",
  "rows": [ { "rank": 1, "team_id": "toulouse", "played": 12, "won": 10, "drawn": 0,
              "lost": 2, "points": 48, "bonus": 8 } ] }
```

## 既存データからの移行
- `data/unified_player_database_final.json`（6018件）が最良の出発点。これを新スキーマに変換して初期 master を作る（09のタスクP1-4）。内訳: all.rugby由来 4040 / league_one 1375 / top_14 603。
- 変換で値が欠ける・矛盾する場合は null にして `data/master/_meta/migration_report.md` に件数を記録。**補完しない。**
- **旧slug→新slugの記録は P1-4 の責務**: 移行時に旧レコードの slug と新 slug の対応を `data/master/_meta/redirects.json`（`{"old-slug": "new-slug"}`）へ書き出す。`_meta/` は pipeline 配下なので移行スクリプトが書いてよい。P2-4 はこれを読むだけ。
- **レガシーカテゴリの行き先**: 既存 `src/content/players/` は pro / top-east / top-kyushu / top-west-a〜c / university / high-school に分かれる。移行時のリーグ判定:
  - `source` が league_one/top_14/all.rugby のものは新リーグキーへ。
  - top-east/kyushu/west 系（旧トップリーグ地域、約514件）は現行リーグに実体が無い。**master には入れず** `data/legacy/` 据え置き、該当URLは redirects.json で `/players/`（一覧）へ集約するか 410 とする（P2-4で決定、SEO実害の小さい方）。ダミーで新リーグに割り当てない。
  - high-school / university の**個別ページ（計7件）は 10 のポリシー（高校生の個別ページ禁止）に反するため master 化しない**。学校ページ移行(P5)まで redirects で退避。
- national の試合日程は例外的に `matches/national_{year}.json`（`{league}_{season}` 命名の例外。season がリーグ戦と異なり暦年管理のため）。
