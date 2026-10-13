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

