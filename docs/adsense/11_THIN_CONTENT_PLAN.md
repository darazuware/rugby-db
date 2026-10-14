# 11 薄い記事・類似記事の整理計画

対象: docs/adsense/09_NEWS_AUDIT.md の68本。事実の書き足しはしない（統合は既存本文の移設のみ）。

## 件数

| 分類 | 件数 | 処置 |
|---|---:|---|
| 残す | 3 | そのまま |
| 統合 | 11（＋同種2） | まとめ記事へ集約。旧URLは data/redirects.json で301 |
| noindex | 1 | frontmatter `noindex: true`（サイトマップ除外） |
| 非公開 | 53 | `draft: true`。URLは近いページへ301 |
| 計 | 68（＋2） | |

## 種類別

| 種類 | 本数 | 分類 | 転送先 |
|---|---:|---|---|
| チーム紹介（同名のチームページと重複） | 34 | 非公開 | 各チームページ |
| 加入週次（掲載取り下げ済み・本文なし） | 7 | 非公開 | /news/transfers-roundup-2026-08/ |
| キャップ週次（生成元データが外部ソースと矛盾、10_FACT_AUDIT 要判断2） | 5 | 非公開 | /news/transfers-roundup-2026-09/ |
| キャップ週次（生成元データが外部ソースと矛盾、10_FACT_AUDIT 要判断2） | 4 | 非公開 | /news/transfers-roundup-2026-08/ |
| 加入週次 → 月次まとめ | 4 | 統合 | /news/transfers-roundup-2026-09/ |
| リーグワン新加入発表 → まとめ | 3 | 統合 | /news/league-one-2026-27-new-signings/ |
| 代表招集（メンバー重複8割超） → 年間まとめ | 3 | 統合 | /news/national-callups-2026/ |
| 加入週次（掲載取り下げ済み・本文なし） | 3 | 非公開 | /news/transfers-roundup-2026-09/ |
| 試合レビュー（独自の試合記録） | 2 | 残す | — |
| リーグガイド（/teams/premiership/ と同趣旨の一覧） | 1 | noindex | — |
| 月次まとめ（統合先。週次5本を集約） | 1 | 統合 | — |
| U17代表大会記事（独自） | 1 | 残す | — |
| 加入週次 → 月次まとめ（同種のため追加） | 1 | 統合 | /news/transfers-roundup-2026-09/ |
| 代表招集 → 年間まとめ（同種のため追加） | 1 | 統合 | /news/national-callups-2026/ |

## 記事別

| slug | 本文字数 | 分類 | 理由 | 転送先 |
|---|---:|---|---|---|
| japan-vs-australia-2026-leg2-review | 916 | 残す | 試合レビュー（独自の試合記録） | — |
| japan-vs-canada-2026-review | 854 | 残す | 試合レビュー（独自の試合記録） | — |
| mitsubishi-dynaboars-2026-new-signings | 890 | 統合 | リーグワン新加入発表 → まとめ | /news/league-one-2026-27-new-signings/ |
| national-callup-53968 | 1808 | 統合 | 代表招集（メンバー重複8割超） → 年間まとめ | /news/national-callups-2026/ |
| national-callup-54087 | 1898 | 統合 | 代表招集（メンバー重複8割超） → 年間まとめ | /news/national-callups-2026/ |
| national-callup-54111 | 1706 | 統合 | 代表招集（メンバー重複8割超） → 年間まとめ | /news/national-callups-2026/ |
| national-callup-54139 | — | 統合 | 代表招集 → 年間まとめ（同種のため追加） | /news/national-callups-2026/ |
| national-caps-weekly-2026-W32 | 396 | 非公開 | キャップ週次（生成元データが外部ソースと矛盾、10_FACT_AUDIT 要判断2） | /news/transfers-roundup-2026-08/ |
| national-caps-weekly-2026-W33 | 262 | 非公開 | キャップ週次（生成元データが外部ソースと矛盾、10_FACT_AUDIT 要判断2） | /news/transfers-roundup-2026-08/ |
| national-caps-weekly-2026-W34 | 107 | 非公開 | キャップ週次（生成元データが外部ソースと矛盾、10_FACT_AUDIT 要判断2） | /news/transfers-roundup-2026-08/ |
| national-caps-weekly-2026-W36 | 313 | 非公開 | キャップ週次（生成元データが外部ソースと矛盾、10_FACT_AUDIT 要判断2） | /news/transfers-roundup-2026-08/ |
| national-caps-weekly-2026-W37 | 862 | 非公開 | キャップ週次（生成元データが外部ソースと矛盾、10_FACT_AUDIT 要判断2） | /news/transfers-roundup-2026-09/ |
| national-caps-weekly-2026-W38 | 569 | 非公開 | キャップ週次（生成元データが外部ソースと矛盾、10_FACT_AUDIT 要判断2） | /news/transfers-roundup-2026-09/ |
| national-caps-weekly-2026-W39 | 932 | 非公開 | キャップ週次（生成元データが外部ソースと矛盾、10_FACT_AUDIT 要判断2） | /news/transfers-roundup-2026-09/ |
| panasonic-wild-knights-2026-new-signings | 624 | 統合 | リーグワン新加入発表 → まとめ | /news/league-one-2026-27-new-signings/ |
| premiership-bath-2025-26 | 1450 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/premiership/bath-rugby/ |
| premiership-bristol-bears-2025-26 | 1010 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/premiership/bristol-bears/ |
| premiership-caps-weekly-2026-W40 | 273 | 非公開 | キャップ週次（生成元データが外部ソースと矛盾、10_FACT_AUDIT 要判断2） | /news/transfers-roundup-2026-09/ |
| premiership-exeter-chiefs-2025-26 | 962 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/premiership/exeter-chiefs/ |
| premiership-gloucester-2025-26 | 914 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/premiership/gloucester-rugby/ |
| premiership-harlequins-2025-26 | 982 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/premiership/harlequins/ |
| premiership-join-weekly-2026-W34 | 82 | 非公開 | 加入週次（掲載取り下げ済み・本文なし） | /news/transfers-roundup-2026-08/ |
| premiership-join-weekly-2026-W40 | 139 | 統合 | 加入週次 → 月次まとめ | /news/transfers-roundup-2026-09/ |
| premiership-league-guide-2025-26 | 1053 | noindex | リーグガイド（/teams/premiership/ と同趣旨の一覧） | — |
| premiership-leicester-tigers-2025-26 | 1096 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/premiership/leicester-tigers/ |
| premiership-newcastle-falcons-2025-26 | 713 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/premiership/newcastle-red-bulls/ |
| premiership-northampton-saints-2025-26 | 1078 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/premiership/northampton-saints/ |
| premiership-sale-sharks-2025-26 | 906 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/premiership/sale-sharks/ |
| premiership-saracens-2025-26 | 1069 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/premiership/saracens/ |
| suntory-sungoliath-2026-27-new-signings | 634 | 統合 | リーグワン新加入発表 → まとめ | /news/league-one-2026-27-new-signings/ |
| super-rugby-act-brumbies-2025-26 | 1468 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/super-rugby/act-brumbies/ |
| super-rugby-join-weekly-2026-W34 | 82 | 非公開 | 加入週次（掲載取り下げ済み・本文なし） | /news/transfers-roundup-2026-08/ |
| super-rugby-moana-pasifika-2025-26 | 1457 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/super-rugby/moana-pasifika/ |
| top14-bayonne-2025-26 | 1461 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/top14/bayonne/ |
| top14-join-weekly-2026-W32 | 82 | 非公開 | 加入週次（掲載取り下げ済み・本文なし） | /news/transfers-roundup-2026-08/ |
| top14-join-weekly-2026-W33 | 82 | 非公開 | 加入週次（掲載取り下げ済み・本文なし） | /news/transfers-roundup-2026-08/ |
| top14-join-weekly-2026-W34 | 82 | 非公開 | 加入週次（掲載取り下げ済み・本文なし） | /news/transfers-roundup-2026-08/ |
| top14-join-weekly-2026-W36 | 82 | 非公開 | 加入週次（掲載取り下げ済み・本文なし） | /news/transfers-roundup-2026-08/ |
| top14-join-weekly-2026-W37 | 82 | 非公開 | 加入週次（掲載取り下げ済み・本文なし） | /news/transfers-roundup-2026-09/ |
| top14-join-weekly-2026-W38 | 82 | 非公開 | 加入週次（掲載取り下げ済み・本文なし） | /news/transfers-roundup-2026-09/ |
| top14-join-weekly-2026-W39 | 82 | 非公開 | 加入週次（掲載取り下げ済み・本文なし） | /news/transfers-roundup-2026-09/ |
| top14-la-rochelle-2025-26 | 1464 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/top14/la-rochelle/ |
| top14-lyon-2025-26 | 1447 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/top14/lyon/ |
| top14-montpellier-2025-26 | 1360 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/top14/montpellier/ |
| top14-pau-2025-26 | 1440 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/top14/pau/ |
| top14-stade-francais-2025-26 | 1490 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/top14/paris/ |
| transfers-roundup-2026-09 | 125 | 統合 | 月次まとめ（統合先。週次5本を集約） | — |
| u17-japan-2026-japan-korea-china-junior | 1486 | 残す | U17代表大会記事（独自） | — |
| urc-benetton-2025-26 | 977 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/urc/benetton-rugby-trevise/ |
| urc-bulls-2025-26 | 923 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/urc/vodacom-bulls/ |
| urc-caps-weekly-2026-W40 | 651 | 非公開 | キャップ週次（生成元データが外部ソースと矛盾、10_FACT_AUDIT 要判断2） | /news/transfers-roundup-2026-09/ |
| urc-cardiff-2025-26 | 961 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/urc/cardiff-rugby/ |
| urc-connacht-2025-26 | 859 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/urc/connacht-rugby/ |
| urc-dragons-2025-26 | 742 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/urc/dragons-rugby/ |
| urc-edinburgh-2025-26 | 973 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/urc/edinburgh-rugby/ |
| urc-glasgow-warriors-2025-26 | 1190 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/urc/glasgow-warriors/ |
| urc-join-weekly-2026-W34 | 82 | 非公開 | 加入週次（掲載取り下げ済み・本文なし） | /news/transfers-roundup-2026-08/ |
| urc-join-weekly-2026-W37 | 302 | 統合 | 加入週次 → 月次まとめ | /news/transfers-roundup-2026-09/ |
| urc-join-weekly-2026-W38 | — | 統合 | 加入週次 → 月次まとめ（同種のため追加） | /news/transfers-roundup-2026-09/ |
| urc-join-weekly-2026-W39 | 1053 | 統合 | 加入週次 → 月次まとめ | /news/transfers-roundup-2026-09/ |
| urc-join-weekly-2026-W40 | 1397 | 統合 | 加入週次 → 月次まとめ | /news/transfers-roundup-2026-09/ |
| urc-leinster-2025-26 | 1387 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/urc/leinster-rugby/ |
| urc-lions-2025-26 | 758 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/urc/emirates-lions/ |
| urc-munster-2025-26 | 969 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/urc/munster-rugby/ |
| urc-ospreys-2025-26 | 867 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/urc/ospreys/ |
| urc-scarlets-2025-26 | 858 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/urc/scarlets/ |
| urc-sharks-2025-26 | 950 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/urc/hollywoodbets-sharks/ |
| urc-stormers-2025-26 | 959 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/urc/dhl-stormers/ |
| urc-ulster-2025-26 | 1044 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/urc/ulster-rugby/ |
| urc-zebre-2025-26 | 889 | 非公開 | チーム紹介（同名のチームページと重複） | /teams/urc/zebre-parma/ |

## 再発防止（pipeline）

- news_rollup: 週次まとめ（*-join-weekly-* / *-departure-weekly-*）は字数に関係なく単独公開せず月次まとめへ統合。キャップ更新は月次まとめに載せない（caps週次は下書き運用）
- news_rollup: 月次まとめが本文1,500字未満なら noindex。手修正済みの月（data/manual/rollup_frozen.json）は再生成しない
- news_gen: 掲載0件になった週次は noindex 取り下げページを作らず下書き化＋月次まとめへ301
- news_gen: 代表招集は個別記事を作らず年間まとめ（{league}-callups-{年}）に追記
- middleware: 大文字を含むニュースslugの301（-W34 → -w34）が効いていなかったため小文字で照合
