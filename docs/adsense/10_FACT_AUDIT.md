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

## 一般ガイド（観戦・用品・用語・渡航）

# 事実監査結果（ガイド系8本）

### src/content/news/how-to-watch-japan-tests.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | 日本代表テストマッチの視聴先「地上波・BS放送、J SPORTS など」 | 「WOWOW、J SPORTS など」（地上波の中継は確認できず） | https://news.wowow.co.jp/5630.html / https://www.jsports.co.jp/rugby/nations/ |

### src/content/news/how-to-watch-overseas-rugby.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | DAZN月額「3,000円台」（本文・表4か所） | Standard 4,200円／年間プラン月々払い3,200円（表は「3,200〜4,200円」） | https://help.dazn.com/hc/ja-jp/articles/16308524311581 |
| 修正 | J SPORTS月額「2,200円（オンライン視聴プラン）」（本文・表3か所） | J SPORTSオンデマンド ラグビーパック 2,580円（税込） | https://www.jsports.co.jp/support/page/?p_id=81 |
| 修正 | リーグワン月額目安「2,200〜3,000円台」 | 2,580〜4,200円 | 上記2件 |
| 修正 | SR＋TOP14「約5,500円」 | 約5,700〜6,700円（2,530円＋3,200〜4,200円） | 上記＋https://wod.wowow.co.jp/static/join/ |
| 修正 | テストマッチ「NHK / J SPORTS」「無料〜2,200円」 | 「WOWOW / J SPORTS」「2,530〜2,580円」 | https://news.wowow.co.jp/5630.html / https://www.jsports.co.jp/rugby/nations/ |
| 修正 | DAZNは「サッカーやF1も」／メリット「サッカー・F1など」 | F1を削除（DAZNのF1配信は2025年で終了） | https://ja.wikipedia.org/wiki/DAZN |
| 修正 | リーグワンD1「12月〜5月」（3か所） | 12月〜6月（2025-26決勝は2026年6月7日） | https://ja.wikipedia.org/wiki/ジャパンラグビーリーグワン |
| 修正 | 2026注目スケジュール TOP14「通年」 | 9月〜6月 | https://en.wikipedia.org/wiki/2025–26_Top_14_season |
| 修正 | ネーションズチャンピオンシップ視聴先「J SPORTS 等」 | WOWOW / J SPORTS | https://news.wowow.co.jp/5630.html |
| 削除 | 2026注目スケジュール「7〜10月 ラグビーチャンピオンシップ J SPORTS」 | （削除）2026年は開催されず | https://en.wikipedia.org/wiki/The_Rugby_Championship |
| 削除 | J SPORTS表「ラグビーチャンピオンシップ 7〜10月」 | （削除） | 同上（2026年不開催。2027年の放映先は検証不可） |
| 削除 | URC・プレミアシップ「日本での視聴サービスなし」（description・表2行・重要欄・節冒頭・まとめ） | （削除） | 検証不可：en.wikipedia URC/Premiership、URC TV（日本の提供有無不明）、J SPORTS公式 |
| 削除 | J SPORTS「以前はURC・プレミアシップを扱い、契約終了」／デメリット「URC・プレミアシップ非対応」 | （削除） | 検証不可：J SPORTS公式（海外ラグビー頁に記載なし） |
| 削除 | DAZN表「各種テストマッチ」 | （削除） | 検証不可：DAZN公式（2026年のテストマッチ配信の記載なし） |
| 削除 | TOP14強豪例「カスタルMB」 | （削除） | 検証不可：該当クラブ名を確認できず |

### src/content/news/rugby-beginners-guide.md — 問題なし（検証14件：得点4種・80分/前後半40分・シンビン10分・ハイタックル肩線・ラック崩し反則・スクラム8人/フッカー・ラインアウト・リーグ13人/6タックル/スクラム6人/主な地域・SR参加国）

### src/content/news/rugby-gear-by-position.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 削除 | サイズ5「一般・高校生以上の試合球の標準サイズ」の「高校生以上」 | 「一般の試合球の標準サイズ」 | 検証不可：JRFU規定見つからず、ja/en Wikipedia「ラグビーボール」に年代記述なし（サイズ4=年少向けは https://passport.world.rugby/laws-of-the-game/laws-by-number/2-ball/ で確認） |

### src/content/news/rugby-glossary.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 削除 | ペナルティゴール「フィールドゴールとも呼ばれます」 | （削除）フィールドゴールはドロップゴールの別称 | https://en.wikipedia.org/wiki/Drop_goal |
| 修正 | コンバージョン「トライを取った位置の正面からキック」 | 「トライを取った地点を通りタッチラインと平行な線上からキック」 | https://passport.world.rugby/laws-of-the-game/laws-by-number/8-scoring/ |
| 修正 | ハイタックル「首から上へのタックル」 | 「肩の線より上へのタックル」 | https://passport.world.rugby/laws-of-the-game/laws-by-number/14-tackle/ |
| 削除 | チャンネル「8番の足の外側」「フランカーの足の間」などのルート | （削除） | 検証不可：ja/en Wikipedia「スクラム」に記述なし、競技規則に定義なし |

### src/content/news/rugby-watching-goods.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | リーグワンのシーズン「12月〜5月」 | 12月〜6月 | https://ja.wikipedia.org/wiki/ジャパンラグビーリーグワン |
| 削除 | 「DAZNやJ SPORTSは4K配信に対応している試合もあり」 | （削除）DAZN日本は最高1080p、J SPORTS現行4Kは確認できず | https://help.dazn.com/hc/ja-jp/articles/17472575468573 |
| 修正 | テレビ視聴に「Fire TV StickやApple TV」 | 「Fire TV Stick（DAZNはApple TVにも対応）」※J SPORTSのApple TVアプリは2025/9/30終了 | https://www.jsports.co.jp/support/page/?p_id=295 / https://help.dazn.com/hc/en-us/articles/16178652764317 |
| 削除 | 「World Rugby公式アプリ」の小見出しと説明 | （削除） | 検証不可：App Store検索・world.rugbyで該当アプリ確認できず（RWC2027公式アプリのみ） |

### src/content/news/rwc2027-travel-guide.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 削除 | 「当サイトの大会データ（出典: ラグビーワールドカップ公式サイト）では」 | 出典表記を削除（rules.md：本文に出典を書かない） | — |
| 削除 | 直行便の飛行時間「おおむね9〜10時間台」 | （削除） | 検証不可：航空会社公式・Wikipediaで所要時間確認できず（報道サイトのみ） |
※検証済みでそのまま：大会期間・24チーム/6プール/52試合、プールE構成、日本3試合の日付・会場、3会場の収容人数、決勝T日程と決勝会場（https://en.wikipedia.org/wiki/2027_Rugby_World_Cup）、ETAの3か月/12か月/A$20/パスポート紐付け/就労不可（https://en.wikipedia.org/wiki/Visa_policy_of_Australia ・ https://malaysia.embassy.gov.au/klpr/ETA.html）、直行便就航都市（en.wikipedia Sydney/Brisbane/Perth Airport）、チケット3種（https://www.world.rugby/news/1002155）

### src/content/news/vpn-for-rugby-overseas.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 削除 | 例「プレミアシップは…J SPORTSが英国向けに配信できない」 | （削除） | 検証不可：J SPORTSのプレミアシップ配信を確認できず |
| 修正 | 「既存アカウントは継続利用可能なことが多い／新規登録は国内がスムーズ」 | J SPORTSオンデマンドは海外から契約・解約不可と案内 | https://www.jsports.co.jp/support/page/?p_id=74 |
| 修正 | 「接続先を日本にすればジオブロックを回避できます」 | DAZNはVPN接続を検知すると視聴制限、J SPORTSは海外利用不可と案内 | https://help.dazn.com/hc/en-jp/articles/16184383116189 / https://www.jsports.co.jp/support/page/?p_id=74 |
| 修正 | VPN月額 Nord約500円/Express約900円/Surfshark約300円 | 約3.49ドル/約2.99〜3.49ドル(Basic)/約2.49ドル | https://nordvpn.com/pricing/ / https://www.expressvpn.com/pricing / https://surfshark.com/pricing |
| 修正 | 同時接続 NordVPN 6台・ExpressVPN 5台 | 10台・10〜14台（プランにより異なる） | https://support.nordvpn.com/hc/en-us/articles/19476515228305 / https://www.expressvpn.com/pricing |
| 削除 | VPN法的制限の例「シンガポール」 | （削除、UAEは残す） | 検証不可：en.wikipedia Internet censorship in Singapore 等にVPN規制の記述なし |
| 修正 | 「VPNの使用はグレーゾーンを含む」 | DAZNはVPNなしの接続のみ認める／J SPORTSは海外利用不可 | 同上 |
| 削除 | 「NetflixやAmazon Primeの日本コンテンツも視聴可能」 | （削除） | 検証不可：各社公式で確認せず（規約上の可否不明） |
| 修正 | FAQ「VPNで日本サーバー経由ならDAZNの日本コンテンツが観られる」 | DAZNはVPN接続を検知すると視聴制限と案内 | https://help.dazn.com/hc/en-jp/articles/16184383116189 |
| 修正 | FAQ「VPN約300〜500円＋J SPORTS 2,200円で3,000円以下／DAZN追加で5,000円前後」 | VPN月約2.49〜3.49ドル＋J SPORTS 2,580円、DAZN 3,200〜4,200円 | 上記各公式 |
※要判断：記事の前提（海外からVPNでDAZN/J SPORTSを視聴）自体が、DAZN（VPN不可）・J SPORTS（海外利用不可）の公式案内と矛盾。タイトル・description・手順節・まとめは残したため、全面書き換えか非公開化を判断してほしい。

### 集計
- 記事数：8（問題なし1：rugby-beginners-guide）
- 修正：20件（japan-tests 1／overseas 9／glossary 2／watching-goods 2／vpn 6）
- 削除：16件（overseas 6／gear 1／glossary 2／watching-goods 2／rwc2027 2／vpn 3）
- 要判断：1件（vpn-for-rugby-overseas.md の記事前提が配信各社の公式案内と矛盾）

## Premiership

# 事実監査結果：プレミアシップ

### src/content/teams/premiership/bath-rugby.md — 問題なし（検証4件）
### src/content/teams/premiership/bristol-bears.md — 問題なし（検証7件）
### src/content/teams/premiership/exeter-chiefs.md — 問題なし（検証4件）
### src/content/teams/premiership/gloucester-rugby.md — 問題なし（検証5件）
### src/content/teams/premiership/harlequins.md — 問題なし（検証7件）

### src/content/teams/premiership/leicester-tigers.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | ウェルフォード・ロードは英国最大級の収容規模 | イングランド最大のクラブ専用ラグビー場として | https://en.wikipedia.org/wiki/Welford_Road_Stadium |

### src/content/teams/premiership/newcastle-red-bulls.md — 問題なし（検証8件）
### src/content/teams/premiership/northampton-saints.md — 問題なし（検証5件）
### src/content/teams/premiership/sale-sharks.md — 問題なし（検証6件）
### src/content/teams/premiership/saracens.md — 問題なし（検証7件）

### src/content/news/premiership-bath-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | ラッセル caps 82 | 95 | https://en.wikipedia.org/wiki/Finn_Russell |
| 修正 | ローレンス caps 31 | 37 | https://en.wikipedia.org/wiki/Ollie_Lawrence |
| 修正 | スチュアート caps 45 | 53 | https://en.wikipedia.org/wiki/Will_Stuart |
| 修正 | エウェルズ caps 30 | 35 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | アンダーヒル caps 30 | 50 | https://en.wikipedia.org/wiki/Sam_Underhill |
| 修正 | C.ハリス caps 44 | 46 | https://en.wikipedia.org/wiki/Chris_Harris_(rugby_union) |
| 修正 | レッドパス caps 9 | 15 | https://en.wikipedia.org/wiki/Cameron_Redpath |
| 修正 | ベイリス caps 10 | 18 | https://en.wikipedia.org/wiki/Scotland_national_rugby_union_team |
| 修正 | コカナシガ caps 8 | 16 | https://en.wikipedia.org/wiki/Joe_Cokanasiga |
| 修正 | アランデル caps 8 | 13 | https://en.wikipedia.org/wiki/Henry_Arundell |
| 修正 | デュ・トワ caps 10 | 32 | https://en.wikipedia.org/wiki/Thomas_du_Toit |
| 修正 | T.ヒル caps 2 | 5 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | スペンサー caps 4 | 19 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | オバノ caps 3 | 5 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | データ基準日 2026-04-22 | 2026-10-14（caps更新に合わせ） | — |

（在籍確認：https://en.wikipedia.org/wiki/Bath_Rugby / List_of_2025–26・2026–27_Premiership_Rugby_transfers。S.ウィンターズは https://en.wikipedia.org/wiki/Sam_Winters 。カラーは bathrugby.com 「Blue, Black and White」で確認）

### src/content/news/premiership-bristol-bears-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | ゲンジ caps 62 | 83 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | ランダル caps 11 | 14 | https://en.wikipedia.org/wiki/Harry_Randall_(rugby_union) |
| 修正 | リース=ザミット caps 27 | 43 | https://en.wikipedia.org/wiki/Wales_national_rugby_union_team |
| 修正 | マクギンティ caps 24 | 43 | https://en.wikipedia.org/wiki/AJ_MacGinty |
| 修正 | S.グロンドーナ caps 15 | 25 | https://en.wikipedia.org/wiki/Santiago_Grondona |
| 修正 | ラヴォウヴォウ caps 6 | 12 | https://en.wikipedia.org/wiki/Kalaveti_Ravouvou |
| 修正 | ルビオロ caps 5 | 31 | https://en.wikipedia.org/wiki/Pedro_Rubiolo |
| 修正 | イヴァニシュヴィリ caps 7 | 23 | https://en.wikipedia.org/wiki/Luka_Ivanishvili |
| 修正 | ジョーダン caps 3 | 20 | https://en.wikipedia.org/wiki/Tom_Jordan_(rugby_union) |
| 修正 | データ基準日 2026-04-22 | 2026-10-14 | — |

### src/content/news/premiership-exeter-chiefs-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | スレイド caps 55 | 77 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | シオ caps 59 | 74（豪州代表分） | https://en.wikipedia.org/wiki/Scott_Sio |
| 修正 | ヴァーニー caps 30 | 39 | https://en.wikipedia.org/wiki/Stephen_Varney |
| 修正 | D.ジェンキンス caps 19 | 31 | https://en.wikipedia.org/wiki/Dafydd_Jenkins_(rugby_union) |
| 修正 | ヴィントセント caps 10 | 22 | https://en.wikipedia.org/wiki/Ross_Vintcent |
| 修正 | フーパー caps 4 | 25 | https://en.wikipedia.org/wiki/Tom_Hooper_(rugby_union) |
| 修正 | ザンボニン caps 3 | 21 | https://en.wikipedia.org/wiki/Andrea_Zambonin |
| 修正 | データ基準日 2026-04-22 | 2026-10-14 | — |

### src/content/news/premiership-gloucester-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | T.ウィリアムズ caps 59 | 75 | https://en.wikipedia.org/wiki/Wales_national_rugby_union_team |
| 修正 | ラウラーラ caps 49 | 53 | https://en.wikipedia.org/wiki/Nepo_Laulala |
| 修正 | R.バーン caps 21 | 22 | https://en.wikipedia.org/wiki/Ross_Byrne |
| 修正 | シングルトン caps 2 | 4 | https://en.wikipedia.org/wiki/Jack_Singleton |
| 修正 | ハサウェイ caps 2 | 1 | https://en.wikipedia.org/wiki/Josh_Hathaway |
| 修正 | ルウェリン caps 5 | 13 | https://en.wikipedia.org/wiki/Max_Llewellyn_(rugby_union) |
| 修正 | F.トーマス caps 1 | 8 | https://en.wikipedia.org/wiki/Freddie_Thomas_(rugby_union) |
| 修正 | データ基準日 2026-04-22 | 2026-10-14 | — |

### src/content/news/premiership-harlequins-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | title「イングランド最古の名門」（1866年創設で最古ではない） | 「RFU創設メンバーの名門」 | https://en.wikipedia.org/wiki/Harlequin_F.C. |
| 修正 | ライトブルー・クリムゾン・ブラック・オレンジ | チョコレートブラウン、フレンチグレー、マゼンタ、ライトブルー | https://en.wikipedia.org/wiki/Harlequin_F.C. |
| 修正 | M.スミス caps 35 | 53 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | ランチベリー caps 61 | 70 | https://en.wikipedia.org/wiki/Joe_Launchbury |
| 修正 | ドンブラント caps 20 | 23 | https://en.wikipedia.org/wiki/Alex_Dombrandt |
| 修正 | ペッティ caps 75 | 97 | https://en.wikipedia.org/wiki/Guido_Petti |
| 修正 | G.ターナー caps 40 | 50 | https://en.wikipedia.org/wiki/George_Turner_(rugby_union) |
| 修正 | カニンガム=サウス caps 11 | 23 | https://en.wikipedia.org/wiki/Chandler_Cunningham-South |
| 修正 | ラモシテレ caps 28 | 32（米国代表分） | https://en.wikipedia.org/wiki/Titi_Lamositele |
| 修正 | J.エヴァンス caps 8 | 19 | https://en.wikipedia.org/wiki/Jarrod_Evans |
| 修正 | データ基準日 2026-04-22 | 2026-10-14 | — |

（主将ドンブラント2025-26は https://en.wikipedia.org/wiki/2025–26_Premiership_Rugby で確認）

### src/content/news/premiership-leicester-tigers-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | ウェルフォード・ロードは英国最大級の収容規模 | イングランド最大のクラブ専用ラグビー場として | https://en.wikipedia.org/wiki/Welford_Road_Stadium |
| 修正 | スチュワード caps 35 | 44 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | G.マーティン caps 19 | 24 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | チェッサム caps 23 | 38 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | ファン・ポールトフリート caps 16 | 27 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | オコナー caps 48 | 71 | https://en.wikipedia.org/wiki/James_O'Connor_(rugby_union) |
| 修正 | リフェル caps 23 | 30 | https://en.wikipedia.org/wiki/Wales_national_rugby_union_team |
| 修正 | N.スミス caps 49 | 66 | https://en.wikipedia.org/wiki/Wales_national_rugby_union_team |
| 修正 | ヘイズ caps 7 | 25 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | ペレセ caps 5 | 6 | https://en.wikipedia.org/wiki/Izaia_Perese |
| 修正 | ハード caps 4 | 11 | https://en.wikipedia.org/wiki/Scotland_national_rugby_union_team |
| 修正 | カタ caps 9 | 13 | https://en.wikipedia.org/wiki/Solomone_Kata |
| 修正 | データ基準日 2026-04-22 | 2026-10-14 | — |

### src/content/news/premiership-newcastle-falcons-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | L.ウィリアムズ caps 92 | 93 | https://en.wikipedia.org/wiki/Liam_Williams_(rugby_union) |
| 修正 | ベロ caps 14 | 26 | https://en.wikipedia.org/wiki/Eduardo_Bello |
| 修正 | マフィ フランカー / caps 36 | No.8 / 29 | https://en.wikipedia.org/wiki/Amanaki_Mafi |
| 修正 | データ基準日 2026-04-22 | 2026-10-14 | — |

（畠山健介の在籍は https://en.wikipedia.org/wiki/Kensuke_Hatakeyama 、レッドブル買収・改称は https://en.wikipedia.org/wiki/Newcastle_Red_Bulls で確認。L.ウィリアムズは2026年3月に現役引退だが2025-26在籍は事実）

### src/content/news/premiership-northampton-saints-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | ミッチェル caps 18 | 32 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | フリーマン caps 16 | 30 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | F.スミス caps 6 | 19 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | ファーバンク caps 6 | 14 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | コールズ caps 7 | 22 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | スレイトホルム caps 5 | 8 | https://en.wikipedia.org/wiki/Ollie_Sleightholme |
| 修正 | フィスケッティ caps 48 | 66 | https://en.wikipedia.org/wiki/Danilo_Fischetti |
| 修正 | ハッチンソン caps 8 | 13 | https://en.wikipedia.org/wiki/Scotland_national_rugby_union_team |
| 修正 | ディンウォール caps 2 | 7 | https://en.wikipedia.org/wiki/Fraser_Dingwall |
| 修正 | ポロック caps 10 | 13 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | ラングドン caps 2 | 4 | https://en.wikipedia.org/wiki/Curtis_Langdon |
| 修正 | データ基準日 2026-04-22 | 2026-10-14 | — |

（J.ルイス・A.ピューの2025-26在籍は northamptonsaints.co.uk で確認）

### src/content/news/premiership-sale-sharks-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | 本拠地 AJベル・スタジアム（表・本文の2箇所） | コーパック・スタジアム | https://en.wikipedia.org/wiki/Sale_Sharks |
| 修正 | フォード caps 102 | 108 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | T.カリー caps 56 | 71 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | コーワン=ディッキー caps 44 | 61 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | B.カリー caps 6 | 14 | https://en.wikipedia.org/wiki/Ben_Curry |
| 修正 | ローバック caps 3 | 12 | https://en.wikipedia.org/wiki/Tom_Roebuck |
| 修正 | ロッド caps 7 | 10 | https://en.wikipedia.org/wiki/Bevan_Rodd |
| 修正 | オポク=フォーダー caps 1 | 8 | https://en.wikipedia.org/wiki/England_national_rugby_union_team |
| 修正 | ウィルグリフ・ジョン caps 2 | 5 | https://en.wikipedia.org/wiki/WillGriff_John |
| 修正 | データ基準日 2026-04-22 | 2026-10-14 | — |

（D.ホジキンソンは salesharks.com、T.バローは https://en.wikipedia.org/wiki/Tom_Burrow で在籍確認）

### src/content/news/premiership-saracens-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | ファレル caps 107 | 112 | https://en.wikipedia.org/wiki/Owen_Farrell |
| 修正 | イトジェ caps 80 | 102 | https://en.wikipedia.org/wiki/Maro_Itoje |
| 修正 | トンプキンス caps 38 | 43 | https://en.wikipedia.org/wiki/Nick_Tompkins |
| 修正 | リッチョーニ caps 31 | 39 | https://en.wikipedia.org/wiki/Marco_Riccioni |
| 修正 | マウィ caps 25 | 50 | https://en.wikipedia.org/wiki/Eroni_Mawi |
| 修正 | マリンズ caps 21 | 22 | https://en.wikipedia.org/wiki/Max_Malins |
| 修正 | チンティ caps 16 | 39 | https://en.wikipedia.org/wiki/Lucio_Cinti |
| 修正 | イシェクウェ caps 11 | 15 | https://en.wikipedia.org/wiki/Nick_Isiekwe |
| 修正 | マクファーランド caps 7 | 19 | https://en.wikipedia.org/wiki/Theo_McFarland |
| 修正 | データ基準日 2026-04-22 | 2026-10-14 | — |

### src/content/news/premiership-league-guide-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | 正式名称 ガラガー・プレミアシップ・ラグビー | ガラガー・PREM・ラグビー（Gallagher PREM Rugby） | https://en.wikipedia.org/wiki/Premiership_Rugby |
| 修正 | セール本拠地 AJベル・スタジアム | コーパック・スタジアム | https://en.wikipedia.org/wiki/Sale_Sharks |

### 集計
- 記事数：21（teams 10 / news 11）
- 修正件数：104（うち caps 87、データ基準日 10、本文・表・title 7）／削除件数：0
- 要判断：①リーグは2025年7月に「Gallagher PREM」へ改称済み。全21本の「ガラガー・プレミアシップ」表記（title・リーグ欄・本文）は正式名称欄以外未変更 ②caps を2026-10時点の Wikipedia 値へ更新したため、選手表のある10本はデータ基準日を2026-10-14に変更（見出しは「2025-26シーズン」のまま） ③caps は Wikipedia 記載値で、項目ごとに「correct as of」日付が異なる（一部は2025年時点）

