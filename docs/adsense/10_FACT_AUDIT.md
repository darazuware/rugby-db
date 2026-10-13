# 10 事実監査（teams / news 本文）

実施: 2026-10-13〜14
対象: src/content/teams 全記事、src/content/news の公開記事（draft除外、pipeline生成の *-join-weekly-* / *-caps-weekly-* / national-callup-* は対象外）
方法: 順位・タイトル歴以外の逸話・数値を Wikipedia／公式サイトで検証。誤りは修正、検証できない記述は削除（AI知識での補完なし）。

## Top14

# 事実監査結果：Top14（teams/top14 全件 + news/top14-*-2025-26 非draft）

## teams/top14

### src/content/teams/top14/bayonne.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | 創設年 1904年 | 1906年（1904年は母体の漕艇クラブ） | https://fr.wikipedia.org/wiki/Aviron_bayonnais_(rugby_à_XV) |

### src/content/teams/top14/bordeaux.md — 問題なし（検証5件）
### src/content/teams/top14/castres.md — 問題なし（検証5件）
### src/content/teams/top14/clermont.md — 問題なし（検証6件）
### src/content/teams/top14/la-rochelle.md — 問題なし（検証5件）

### src/content/teams/top14/lyon.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | title「フランス第2都市」 | 「フランス第2の都市圏」（市は第3、都市圏が第2） | https://en.wikipedia.org/wiki/Lyon |
| 修正 | 本文「フランス第2の都市・リヨン」 | 「フランス第2の都市圏を持つリヨン」 | https://en.wikipedia.org/wiki/Lyon |

### src/content/teams/top14/montpellier.md — 問題なし（検証5件）

### src/content/teams/top14/paris.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 削除 | 「フランス最古のラグビークラブの一つ」 | （削除） | 検証不可：en/fr Wikipedia（「最も成功した／偉大なクラブ」とのみ記載） |

### src/content/teams/top14/pau.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 削除 | title「バスク隣接の」 | （削除） | 検証不可：en Wikipedia Pau（ベアルンの中心とのみ記載） |
| 削除 | 本文「バスク地方と隣接する」 | （削除） | 同上 |

### src/content/teams/top14/perpignan.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | 創設年 1902年 | 1933年（1902年は前身ASペルピニャン） | https://fr.wikipedia.org/wiki/Union_sportive_arlequins_perpignanais |

### src/content/teams/top14/racing-92.md（draft: true）
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 削除 | 「先進的なクラブ運営が特徴」 | （削除。「積極的な投資」は残す） | 検証不可：en Wikipedia Racing 92 |

### src/content/teams/top14/toulon.md — 問題なし（検証6件）
### src/content/teams/top14/toulouse.md — 問題なし（検証7件）

### src/content/teams/top14/vannes.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | title「初のTop14で戦う」 | 「Top14に帰ってきた」（2025降格→2026-27昇格） | https://fr.wikipedia.org/wiki/Championnat_de_France_de_rugby_à_XV_2026-2027 |

## news/top14-*-2025-26（基準日2026-04-21。caps は en/fr Wikipedia の 2026-04-21 以前の最新版の値に修正）

ロースターは en Wikipedia 各クラブ記事の 2026-04-21 直前版（API rvstart）のトップ／エスポワール一覧と照合。en版に無い選手は選手個別記事・fr版で確認（全員確認済）。ポジション表記の差異は対象外として未変更。

### src/content/news/top14-bayonne-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | 創設年 1904年 | 1906年 | https://fr.wikipedia.org/wiki/Aviron_bayonnais_(rugby_à_XV) |
| 削除 | 「代表経験のある主力選手は確認されていません（ローカル中心）」＋見出し | （削除。見出し「その他在籍選手」→「在籍選手」） | 検証不可（在籍表にTuilagi・Anscombe等の代表経験者がいる） |

### src/content/news/top14-bordeaux-begles-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | title「青と白の新興勢力」 | 「クラレットと白の新興勢力」 | https://en.wikipedia.org/wiki/Union_Bordeaux_Bègles |
| 修正 | 本文「青と白のジャージ」 | 「ボルドー色（クラレット）と白のジャージ」 | 同上 |
| 修正 | caps Penaud 65 / Jalibert 45 / Lucu 25 / Woki 25 / Bielle-Biarrey 20 | 59 / 39 / 30 / 33 / 27 | https://fr.wikipedia.org/wiki/Damian_Penaud ・ https://en.wikipedia.org/wiki/Matthieu_Jalibert ・ https://fr.wikipedia.org/wiki/Maxime_Lucu ・ https://fr.wikipedia.org/wiki/Cameron_Woki ・ https://en.wikipedia.org/wiki/Louis_Bielle-Biarrey |
| 削除 | 在籍表 Madosh TAMBWE | （削除。2024年からモンペリエ所属） | https://en.wikipedia.org/wiki/Madosh_Tambwe |

### src/content/news/top14-castres-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | caps Babillot 10 | 5 | https://fr.wikipedia.org/wiki/Mathieu_Babillot |

### src/content/news/top14-clermont-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | Irae Simone フィジー代表 20caps | オーストラリア代表 2caps | https://en.wikipedia.org/wiki/Irae_Simone |

### src/content/news/top14-la-rochelle-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | 「人口わずか7万人の都市」 | 「人口約8万人の都市」（2023年 79,851人） | https://en.wikipedia.org/wiki/La_Rochelle |
| 修正 | caps Alldritt 55 / Botia 45 / Danty 25 / Dillane 25 / Skelton 20 / Hastoy 15 | 58 / 30 / 29 / 19 / 32 / 10 | https://fr.wikipedia.org/wiki/Grégory_Alldritt ・ https://en.wikipedia.org/wiki/Levani_Botia ・ https://fr.wikipedia.org/wiki/Jonathan_Danty ・ https://en.wikipedia.org/wiki/Ultan_Dillane ・ https://en.wikipedia.org/wiki/Will_Skelton ・ https://fr.wikipedia.org/wiki/Antoine_Hastoy |

### src/content/news/top14-lyon-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | title「フランス第2都市」 | 「フランス第2の都市圏」 | https://en.wikipedia.org/wiki/Lyon |
| 修正 | 本文「フランス第2の都市・リヨン」 | 「フランス第2の都市圏を持つリヨン」 | 同上 |
| 修正 | caps Couilloud 15 / Dumortier 15 | 17 / 6 | https://fr.wikipedia.org/wiki/Baptiste_Couilloud ・ https://fr.wikipedia.org/wiki/Ethan_Dumortier |

### src/content/news/top14-montpellier-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | 創設年 1902年 | 1986年（合併で設立） | https://en.wikipedia.org/wiki/Montpellier_Hérault_Rugby |
| 削除 | 「2022年の優勝後は主力選手の流出もあり再建途上にあるが、」 | （削除） | 検証不可：en/fr Wikipedia |

### src/content/news/top14-pau-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 削除 | title「バスク隣接の」・本文「バスク地方と隣接する」 | （削除） | 検証不可：en Wikipedia Pau |
| 修正 | Laporte フランス代表 15caps | フランスU20代表 7（A代表キャップなし） | https://fr.wikipedia.org/wiki/Clément_Laporte |

### src/content/news/top14-perpignan-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | 創設年 1902年 | 1933年 | https://fr.wikipedia.org/wiki/Union_sportive_arlequins_perpignanais |
| 修正 | caps Yato 45 | 20 | https://en.wikipedia.org/wiki/Peceli_Yato |

### src/content/news/top14-stade-francais-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 削除 | 「フランス最古のラグビークラブの一つ」 | （削除） | 検証不可：en/fr Wikipedia |
| 修正 | caps Macalou 35 | 20 | https://fr.wikipedia.org/wiki/Sekou_Macalou |

### src/content/news/top14-toulon-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | caps Garbisi 45 / Ollivon 45 / Serin 35 / Mercer 20 | 49 / 53 / 50 / 2 | https://en.wikipedia.org/wiki/Paolo_Garbisi ・ https://fr.wikipedia.org/wiki/Charles_Ollivon ・ https://fr.wikipedia.org/wiki/Baptiste_Serin ・ https://fr.wikipedia.org/wiki/Zach_Mercer |

### src/content/news/top14-toulouse-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | caps Dupont 75 / Baille 55 / Marchand 50 / Ntamack 50 / Flament 25 / Cros 25 | 64 / 57 / 53 / 43 / 38 / 44 | https://fr.wikipedia.org/wiki/Antoine_Dupont ・ https://fr.wikipedia.org/wiki/Cyril_Baille ・ https://fr.wikipedia.org/wiki/Julien_Marchand ・ https://fr.wikipedia.org/wiki/Romain_Ntamack ・ https://fr.wikipedia.org/wiki/Thibaud_Flament ・ https://fr.wikipedia.org/wiki/François_Cros |
| 修正 | caps Jelonch 20 / Meafou 15 / Willis 15 / Ramos 40 | 40 / 16 / 14 / 52 | https://fr.wikipedia.org/wiki/Anthony_Jelonch ・ https://fr.wikipedia.org/wiki/Emmanuel_Meafou ・ https://en.wikipedia.org/wiki/Jack_Willis_(rugby_union) ・ https://fr.wikipedia.org/wiki/Thomas_Ramos |
| 削除 | caps 斎藤直人 40 | 「—」（数値のみ削除） | 検証不可：ja版27・en版36で不一致 |

### src/content/news/top14-vannes-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 削除 | 「代表経験のある主力選手は確認されていません（ローカル中心）」＋見出し | （削除。見出し「在籍選手」に統一） | 検証不可（在籍表にMako Vunipola等がいる） |

要判断：top14-vannes-2025-26.md はタグ「Top14」「2025-26」だが、ヴァンヌは2025-26シーズンPro D2所属（本文の降格・2026-27昇格は事実として確認済）。シリーズ内の位置づけは親で判断を。

### 集計
- 記事数：27（teams 14〈racing-92はdraft〉＋news 13）
- 修正：45件（caps・代表国 32件含む）／削除：12件（文・語句8、表の行1、caps値1、見出し＋文2）
- 要判断：1件（vannes記事の2025-26 Top14表記）

