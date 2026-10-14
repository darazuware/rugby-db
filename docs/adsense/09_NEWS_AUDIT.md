# 09 ニュース記事監査（薄い記事・類似記事）

実施: 2026-10-14
対象: src/content/news の公開中記事123本（draft・未来日付を除く）
基準: 本文1,500字未満（frontmatter・記法・URL・空白を除いた文字数）、または他の公開記事と8割以上類似（difflib 類似度）

該当: **68本**（1,500字未満 65本、8割以上類似 13本・重複あり）

| slug | 本文字数 | 類似記事（類似度） | noindex | pubDate |
|---|---:|---|---|---|
| japan-vs-australia-2026-leg2-review | 916 | — |  | 2026-08-16 |
| japan-vs-canada-2026-review | 854 | — |  | 2026-09-06 |
| mitsubishi-dynaboars-2026-new-signings | 890 | — |  | 2026-07-31 |
| national-callup-53968 | 1808 | national-callup-54087(81%) |  | 2026-08-07 |
| national-callup-54087 | 1898 | national-callup-54111(88%);national-callup-53968(81%) |  | 2026-07-24 |
| national-callup-54111 | 1706 | national-callup-54087(88%) |  | 2026-08-10 |
| national-caps-weekly-2026-W32 | 396 | — |  | 2026-08-09 |
| national-caps-weekly-2026-W33 | 262 | — |  | 2026-08-16 |
| national-caps-weekly-2026-W34 | 107 | — |  | 2026-08-23 |
| national-caps-weekly-2026-W36 | 313 | — |  | 2026-08-31 |
| national-caps-weekly-2026-W37 | 862 | — |  | 2026-09-07 |
| national-caps-weekly-2026-W38 | 569 | — |  | 2026-09-14 |
| national-caps-weekly-2026-W39 | 932 | — |  | 2026-09-21 |
| panasonic-wild-knights-2026-new-signings | 624 | — |  | 2026-07-31 |
| premiership-bath-2025-26 | 1450 | — |  | 2026-04-22 |
| premiership-bristol-bears-2025-26 | 1010 | — |  | 2026-04-22 |
| premiership-caps-weekly-2026-W40 | 273 | — |  | 2026-09-28 |
| premiership-exeter-chiefs-2025-26 | 962 | — |  | 2026-04-22 |
| premiership-gloucester-2025-26 | 914 | — |  | 2026-04-22 |
| premiership-harlequins-2025-26 | 982 | — |  | 2026-04-22 |
| premiership-join-weekly-2026-W34 | 82 | super-rugby-join-weekly-2026-W34(100%);top14-join-weekly-2026-W32(100%);top14-join-weekly-2026-W33(100%) | ○ | 2026-08-19 |
| premiership-join-weekly-2026-W40 | 139 | — |  | 2026-09-28 |
| premiership-league-guide-2025-26 | 1053 | — |  | 2026-04-22 |
| premiership-leicester-tigers-2025-26 | 1096 | — |  | 2026-04-22 |
| premiership-newcastle-falcons-2025-26 | 713 | — |  | 2026-04-22 |
| premiership-northampton-saints-2025-26 | 1078 | — |  | 2026-04-22 |
| premiership-sale-sharks-2025-26 | 906 | — |  | 2026-04-22 |
| premiership-saracens-2025-26 | 1069 | — |  | 2026-04-22 |
| suntory-sungoliath-2026-27-new-signings | 634 | — |  | 2026-07-31 |
| super-rugby-act-brumbies-2025-26 | 1468 | — |  | 2026-04-21 |
| super-rugby-join-weekly-2026-W34 | 82 | premiership-join-weekly-2026-W34(100%);top14-join-weekly-2026-W32(100%);top14-join-weekly-2026-W33(100%) | ○ | 2026-08-19 |
| super-rugby-moana-pasifika-2025-26 | 1457 | — |  | 2026-04-21 |
| top14-bayonne-2025-26 | 1461 | — |  | 2026-04-21 |
| top14-join-weekly-2026-W32 | 82 | premiership-join-weekly-2026-W34(100%);super-rugby-join-weekly-2026-W34(100%);top14-join-weekly-2026-W33(100%) | ○ | 2026-08-08 |
| top14-join-weekly-2026-W33 | 82 | premiership-join-weekly-2026-W34(100%);super-rugby-join-weekly-2026-W34(100%);top14-join-weekly-2026-W32(100%) | ○ | 2026-08-16 |
| top14-join-weekly-2026-W34 | 82 | premiership-join-weekly-2026-W34(100%);super-rugby-join-weekly-2026-W34(100%);top14-join-weekly-2026-W32(100%) | ○ | 2026-08-23 |
| top14-join-weekly-2026-W36 | 82 | premiership-join-weekly-2026-W34(100%);super-rugby-join-weekly-2026-W34(100%);top14-join-weekly-2026-W32(100%) | ○ | 2026-08-31 |
| top14-join-weekly-2026-W37 | 82 | premiership-join-weekly-2026-W34(100%);super-rugby-join-weekly-2026-W34(100%);top14-join-weekly-2026-W32(100%) | ○ | 2026-09-07 |
| top14-join-weekly-2026-W38 | 82 | premiership-join-weekly-2026-W34(100%);super-rugby-join-weekly-2026-W34(100%);top14-join-weekly-2026-W32(100%) | ○ | 2026-09-14 |
| top14-join-weekly-2026-W39 | 82 | premiership-join-weekly-2026-W34(100%);super-rugby-join-weekly-2026-W34(100%);top14-join-weekly-2026-W32(100%) | ○ | 2026-09-21 |
| top14-la-rochelle-2025-26 | 1464 | — |  | 2026-04-21 |
| top14-lyon-2025-26 | 1447 | — |  | 2026-04-21 |
| top14-montpellier-2025-26 | 1360 | — |  | 2026-04-21 |
| top14-pau-2025-26 | 1440 | — |  | 2026-04-21 |
| top14-stade-francais-2025-26 | 1490 | — |  | 2026-04-21 |
| transfers-roundup-2026-09 | 125 | — |  | 2026-09-28 |
| u17-japan-2026-japan-korea-china-junior | 1486 | — |  | 2026-08-13 |
| urc-benetton-2025-26 | 977 | — |  | 2026-04-21 |
| urc-bulls-2025-26 | 923 | — |  | 2026-04-21 |
| urc-caps-weekly-2026-W40 | 651 | — |  | 2026-09-28 |
| urc-cardiff-2025-26 | 961 | — |  | 2026-04-21 |
| urc-connacht-2025-26 | 859 | — |  | 2026-04-21 |
| urc-dragons-2025-26 | 742 | — |  | 2026-04-21 |
| urc-edinburgh-2025-26 | 973 | — |  | 2026-04-21 |
| urc-glasgow-warriors-2025-26 | 1190 | — |  | 2026-04-21 |
| urc-join-weekly-2026-W34 | 82 | premiership-join-weekly-2026-W34(100%);super-rugby-join-weekly-2026-W34(100%);top14-join-weekly-2026-W32(100%) | ○ | 2026-08-19 |
| urc-join-weekly-2026-W37 | 302 | — |  | 2026-09-07 |
| urc-join-weekly-2026-W39 | 1053 | — |  | 2026-09-21 |
| urc-join-weekly-2026-W40 | 1397 | — |  | 2026-09-28 |
| urc-leinster-2025-26 | 1387 | — |  | 2026-04-21 |
| urc-lions-2025-26 | 758 | — |  | 2026-04-21 |
| urc-munster-2025-26 | 969 | — |  | 2026-04-21 |
| urc-ospreys-2025-26 | 867 | — |  | 2026-04-21 |
| urc-scarlets-2025-26 | 858 | — |  | 2026-04-21 |
| urc-sharks-2025-26 | 950 | — |  | 2026-04-21 |
| urc-stormers-2025-26 | 959 | — |  | 2026-04-21 |
| urc-ulster-2025-26 | 1044 | — |  | 2026-04-21 |
| urc-zebre-2025-26 | 889 | — |  | 2026-04-21 |
