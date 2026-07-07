# 02 スクレイパー仕様

## 新構成
既存の scripts/ 直下の乱立スクリプトは使わない（08でアーカイブ）。新規に `pipeline/` を作る。

```
pipeline/
  __init__.py
  run.py                 # CLI: python3 -m pipeline.run --league top14 [--dry-run]
  schemas.py             # 01のスキーマをpydanticで定義
  scrape/
    league_one.py        # league-one.jp（D1/D2/D3）
    all_rugby.py         # all.rugby 汎用（Top14 / Super Rugby / 代表 / 順位表 / 試合）
    jrfu.py              # 代表戦日程
  transform/
    normalize.py         # ソース生データ → 01スキーマへ変換
  validate/
    checks.py            # 03の検証を実装
  diffs/
    detect.py            # 前回masterとの差分（移籍・キャップ更新）→ 05で使用
  io.py                  # master読み書き・_meta更新
requirements.txt         # requests, beautifulsoup4, pydantic
```

## 共通ルール
- User-Agent 明示、`timeout=15`、リクエスト間 `time.sleep(1.5)` 以上。リトライは最大2回（指数バックオフ）。
- HTML構造が想定と違う場合は **その項目を null にしてスキップし、`_meta/last_run.json` に warning を記録**。例外で全体を止めない。ただし取得0件のときは exit code 1（CIで検知）。
- 生HTMLのパース結果を直接 master に書かない。必ず transform → validate を通す。
- 既存スクレイパーのパースロジックは流用してよい。特に:
  - `scripts/scrapers/scrape_allrugby_stats.py`（all.rugby 選手ページのbio/careerパース）
  - `scripts/scrapers/league_one_scraper.py`（league-one.jp）
  - `scripts/scrape_jrfu_matches.py`

## ソース別仕様

### league-one.jp（リーグワン全D）
- 選手: `https://league-one.jp/player/{id}`。チーム一覧→所属選手一覧→個別ページの順に辿る。
- 取得: 氏名(ja/en)、ポジション、身長体重、生年月日、出身校、リーグワンキャップ、代表歴欄、所属チーム、画像URL(参考として保持、表示には使わない)。
- D2/D3もチーム一覧に含まれる。`league` はチームのディビジョンで振り分け。
- 順位・結果: 既存 `scripts/scrape_leagueone_results.py` / `scrape_standings.py` のロジックを移植。

### all.rugby（Top14 / Super Rugby / 代表 / URC等）
- 順位表: `https://all.rugby/tournament/{key}/table`（key例: `top14`, `urc`）※Super Rugbyのkeyは実ページで確認して transform にコメントで記録すること。
- チーム/スコッド: tournament ページからチームリンク→ `https://all.rugby/club/...` のスコッド一覧。
- 選手: `https://all.rugby/player/{id}`。bioから国籍・身長体重・ポジション・career_path・テストキャップ。
- 代表: `national.json` は日本代表＋直近1年で日本と対戦する国の現行スコッドのみ対象（全世界を取らない）。
- 試合日程・結果: tournament の calendar/results ページ。

### JRFU（jrfu.jp）
- 日本代表の試合日程・会場。`matches/national_{year}.json` に出力。会場名は正規化せず原文＋`venue_raw`で保持。

## run.py の挙動
```
python3 -m pipeline.run --league top14
  1. scrape  → scratch(一時JSON)
  2. transform → Player/Team/Match/Standing リスト
  3. validate（03）→ 失敗ならexit 1、masterは書き換えない
  4. diffs.detect → data/master/_meta/diff/{date}_{league}.json
  5. master 書き込み + _meta/last_run.json 更新
--dry-run は 5 をスキップして差分だけ表示
--all で全リーグ順次実行
```

## 完了条件（このフェーズのDone）
- `python3 -m pipeline.run --all --dry-run` がエラーなく完走し、各リーグの取得件数が表示される
- リーグワン全D合計で選手1200件以上、Top14で500件以上、Super Rugbyで400件以上取得できる
- master の全レコードが pydantic 検証を通る
