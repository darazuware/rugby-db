# レガシーDB移行レポート（P1-4）

生成: 2026-07-14T03:11:51+09:00  ソース: `data/unified_player_database_final.json`

## 入力→出力（選手）

| source | 入力 | master化 | 備考 |
|---|---:|---:|---|
| league_one | 1375 | 1375 | skip(チーム未収載) 0 |
| top_14 | 603 | 603 | skip(チーム未収載) 0 |
| all_rugby | 4040 | 0 | league/team不明のstubのため退避（P1-5/P1-7で取得） 4040 |

## master ファイル件数

- players/league-one-d1.json: 653
- players/league-one-d2.json: 415
- players/league-one-d3.json: 307
- players/top14.json: 603
- teams/league-one-d1.json: 12
- teams/league-one-d2.json: 8
- teams/league-one-d3.json: 6
- teams/top14.json: 14

## null 化件数（値はあるが採用不可 → null）

- birthdate: 75

補完しない方針（01）のため、上記は捏造せず null で確定。

## 旧URL処理（src/content/players 走査）

- redirects.json（旧slug→新slug 301）: 1369
- retired_slugs.json（master無し・退避、P2-4で一覧集約 or 410）: 2982

内訳:
- preserved:top14: 602
- redirect:league-one: 1369
- retired:high-school: 4
- retired:league-one-unmatched: 1
- retired:pro-premiership: 693
- retired:pro-super-rugby: 444
- retired:pro-top14: 63
- retired:pro-unknown: 305
- retired:pro-urc: 955
- retired:top-east: 78
- retired:top-kyushu: 253
- retired:top-west-a: 123
- retired:top-west-b: 53
- retired:top-west-c: 7
- retired:university: 3

> 退避対象: 旧トップリーグ地域(top-east/kyushu/west)・個別high-school/university、および現状master未整備の pro(urc/premiership/super-rugby/未分類)。super-rugby/urc/premiership は該当スクレイパー(P1-6/P4-6)整備後に再移行で301化可能。

## warnings（8件、先頭50）

- ar_ethan-tia: height_cm='' を範囲外/変換不能のため null 化
- ar_ethan-tia: weight_kg='' を範囲外/変換不能のため null 化
- ar_mayron-fahy: height_cm='' を範囲外/変換不能のため null 化
- ar_mayron-fahy: weight_kg='' を範囲外/変換不能のため null 化
- ar_-juan-segundo-martin-montilla: height_cm='' を範囲外/変換不能のため null 化
- ar_-juan-segundo-martin-montilla: weight_kg='' を範囲外/変換不能のため null 化
- ar_tom-sarthou: height_cm='' を範囲外/変換不能のため null 化
- ar_tom-sarthou: weight_kg='' を範囲外/変換不能のため null 化

