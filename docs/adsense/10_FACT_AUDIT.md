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

## Super Rugby Pacific

# 事実監査結果：super-rugby

共通メモ：
- 選手ロースターは公式2026スコッド発表（https://www.allblacks.com/news/dhl-super-rugby-pacific-squads-named-for-2026-season）＋各チームen.wikipedia「2026 squad」節（途中昇格選手）で照合。
- caps列は各選手en.wikipediaのinfobox（API取得）で照合。infoboxの更新日が2026年のものはその値に更新、更新日が2025年以前（現時点の値と確認できない）は数値を「—」に置換。国籍（代表）の誤りは修正。
- 各記事末尾の「データ基準日: 2026-04-21」は据え置き（caps値は2026-10時点のWikipedia値に更新したため、基準日表記とずれる点は要判断）。
- en.wikipedia「Hurricanes (rugby union)」本文にAIへの指示文が埋め込まれていたが無視した。

### src/content/teams/super-rugby/act-brumbies.md — 問題なし（検証8件）
### src/content/teams/super-rugby/blues.md — 問題なし（検証5件）

### src/content/teams/super-rugby/chiefs.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | リーチマイケル（2015年） | リーチマイケル（2015〜2017年） | https://en.wikipedia.org/wiki/Michael_Leitch |

### src/content/teams/super-rugby/crusaders.md — 問題なし（検証5件）
### src/content/teams/super-rugby/fijian-drua.md — 問題なし（検証8件）
### src/content/teams/super-rugby/highlanders.md — 問題なし（検証7件）
### src/content/teams/super-rugby/hurricanes.md — 問題なし（検証8件）

### src/content/teams/super-rugby/moana-pasifika.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 削除 | ルーツの例示「マオリ」 | （削除） | 検証不可：en.wikipedia Moana Pasifika（Pacific Island nations/Pasifika heritageのみ記載） |
| 削除 | 州協会を代表しない独自のアイデンティティを持つ | （削除） | 検証不可：en.wikipedia Moana Pasifika |

### src/content/teams/super-rugby/nsw-waratahs.md — 問題なし（検証6件）
### src/content/teams/super-rugby/queensland-reds.md — 問題なし（検証6件）
### src/content/teams/super-rugby/western-force.md — 問題なし（検証9件）

### src/content/news/super-rugby-act-brumbies-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | スリッパー caps 131 | 154 | https://en.wikipedia.org/wiki/James_Slipper |
| 修正 | スコップ caps 1 | —（infobox 2023更新で現値未確認） | https://en.wikipedia.org/wiki/Blake_Schoupp |
| 修正 | アラアラトア caps 33 | 94 | https://en.wikipedia.org/wiki/Allan_Alaalatoa |
| 修正 | フロスト caps 12 | —（infobox 2025更新） | https://en.wikipedia.org/wiki/Nick_Frost_(rugby_union) |
| 修正 | バレティーニ caps 35 | 69 | https://en.wikipedia.org/wiki/Rob_Valetini |
（本文：創設・本拠地・カラー・E.ジョーンズ1998・2000-02決勝・2023年10月来日は en/ja.wikipedia で確認。ロースター全員公式2026スコッドで確認）

### src/content/news/super-rugby-blues-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | 後にノースランドとノースハーバーを加える形で構成変更 | チーフスと担当地域を交換し、オークランド・ノースハーバー・ノースランドを代表 | https://en.wikipedia.org/wiki/Blues_(Super_Rugby) |
| 修正 | レイ caps 26 | —（infobox 2023更新） | https://en.wikipedia.org/wiki/Jordan_Lay |
| 修正 | トゥウンガファシ caps 53 | 68 | https://en.wikipedia.org/wiki/Ofa_Tuʻungafasi |
| 修正 | P.トゥイプロトゥ caps 25 | —（infobox 2024更新） | https://en.wikipedia.org/wiki/Patrick_Tuipulotu |
| 修正 | パパリイ caps 26 | —（infobox 2025更新） | https://en.wikipedia.org/wiki/Dalton_Papali%27i |
| 修正 | F.クリスティ caps 17 | 28 | https://en.wikipedia.org/wiki/Finlay_Christie |
| 修正 | B.バレット caps 116 | 146 | https://en.wikipedia.org/wiki/Beauden_Barrett |
| 修正 | アーキ caps 4 | —（infobox 2024更新） | https://en.wikipedia.org/wiki/Pita_Ahki |
| 修正 | クラーク caps 18 | 33 | https://en.wikipedia.org/wiki/Caleb_Clarke_(rugby_union) |
（マテンガ、M.トゥパエア、バーンズは公式初期発表外だがWikipedia 2026 squadで昇格選手として確認）

### src/content/news/super-rugby-chiefs-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | 本拠地 ワイカト・スタジアム（ワイカト） | FMGスタジアム・ワイカト（ハミルトン） | https://en.wikipedia.org/wiki/Chiefs_(rugby_union) |
| 修正 | 国内6州協会（…タラナキ） | 7州協会（＋ンガティ・ポロウ・イーストコースト） | https://en.wikipedia.org/wiki/Chiefs_(rugby_union) |
| 修正 | リーチ（2015・2016年在籍） | 2015〜2017年在籍 | https://en.wikipedia.org/wiki/Michael_Leitch |
| 修正 | ノリス オーストラリア代表 | ニュージーランド代表 | https://en.wikipedia.org/wiki/Ollie_Norris |
| 修正 | フィナウ トンガ代表 | ニュージーランド代表 | https://en.wikipedia.org/wiki/Samipeni_Finau |
| 修正 | タウケイアホ caps 25 | —（infobox 2025更新） | https://en.wikipedia.org/wiki/Samisoni_Taukei%27aho |
| 修正 | ヴァアイ caps 22 | —（infobox 2025更新） | https://en.wikipedia.org/wiki/Tupou_Vaa%27i |
| 修正 | ジェイコブソン caps 15 | 29 | https://en.wikipedia.org/wiki/Luke_Jacobson |
| 修正 | マッケンジー caps 42 | 82 | https://en.wikipedia.org/wiki/Damian_McKenzie |
| 修正 | フォケティ caps 6 | 9 | https://en.wikipedia.org/wiki/Lalakai_Foketi |
| 修正 | ナラワ caps 4 | —（infobox 2025更新） | https://en.wikipedia.org/wiki/Emoni_Narawa |
| 修正 | タウモエフォラウ caps 5 | 6 | https://en.wikipedia.org/wiki/Kyren_Taumoefolau |

### src/content/news/super-rugby-crusaders-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 削除 | 地元選手が豊富でドラフト依存度が低く | （削除）「在籍選手からは多くのオールブラックスが生まれている」に縮約 | 検証不可：en.wikipedia Crusaders（ドラフト記述なし、AB輩出のみ記載） |
| 修正 | ニュエル caps 8 | —（infobox 2024更新） | https://en.wikipedia.org/wiki/Fletcher_Newell |
| 修正 | T.ウィリアムズ caps 3 | —（infobox 2024更新） | https://en.wikipedia.org/wiki/Tamaiti_Williams |
| 修正 | テイラー caps 79 | 112 | https://en.wikipedia.org/wiki/Codie_Taylor |
| 修正 | S.バレット caps 62 | 90 | https://en.wikipedia.org/wiki/Scott_Barrett_(rugby_union) |
| 修正 | ブラックアダー caps 9 | 15 | https://en.wikipedia.org/wiki/Ethan_Blackadder |
| 修正 | ハビリ caps 25 | 30 | https://en.wikipedia.org/wiki/David_Havili |
| 修正 | マクニコル ニュージーランド代表 | ウェールズ代表 | https://en.wikipedia.org/wiki/Johnny_McNicholl |
| 修正 | リース caps 3 | 37 | https://en.wikipedia.org/wiki/Sevu_Reece |
| 修正 | ファインガアヌク caps 3 | 12 | https://en.wikipedia.org/wiki/Leicester_Fainga%27anuku |
| 修正 | ジョーダン caps 25 | 62 | https://en.wikipedia.org/wiki/Will_Jordan_(rugby_union) |
（コーチ在任年 Deans 2000–08/Blackadder 2009–16/Robertson 2017–23 確認。MacDonald・Grant・LeeはWikipedia 2026 squadで昇格選手として確認）

### src/content/news/super-rugby-fijian-drua-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | ラバイ caps 39 | —（infobox 2023更新・値不一致） | https://en.wikipedia.org/wiki/Peni_Ravai |
| 修正 | ドゲ caps 10 | —（infobox 2025更新） | https://en.wikipedia.org/wiki/Mesake_Doge |
| 修正 | タワケ caps 2 | —（infobox 2022更新） | https://en.wikipedia.org/wiki/Samu_Tawake |
| 修正 | トギアタマ caps 3 | —（infoboxに数値なし） | https://en.wikipedia.org/wiki/Zuriel_Togiatama |
| 修正 | ナシラシラ caps 7 | —（infobox 2022更新） | https://en.wikipedia.org/wiki/Isoa_Nasilasila |
| 修正 | マヤナヴァヌア caps 11 | —（infobox 2021更新） | https://en.wikipedia.org/wiki/Temo_Mayanavanua |
| 修正 | ミラミラ caps 5 | —（フィジー代表歴はRWC2023スコッドで確認） | https://en.wikipedia.org/wiki/2023_Rugby_World_Cup_squads |
| 修正 | ロマニ caps 26 | 40 | https://en.wikipedia.org/wiki/Frank_Lomani |
| 修正 | バカタワ caps 32 | 31（2022年で代表引退済み） | https://en.wikipedia.org/wiki/Virimi_Vakatawa |
| 修正 | ドロアセセ caps 4 | —（代表歴はRWC2023スコッドで確認） | https://en.wikipedia.org/wiki/2023_Rugby_World_Cup_squads |
| 修正 | クルヴォリ ポジション スタンドオフ | スクラムハーフ | https://en.wikipedia.org/wiki/Fijian_Drua |
（本文：2017年FRU設立・2018年NRC制覇・NRC終了・2021年4月ライセンス・スバ/ラウトカ/シガトカ開催を確認。バカタワ・カコバウはWikipedia 2026 squadで確認）

### src/content/news/super-rugby-highlanders-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | デ・フロート caps 17 | —（infobox 2024更新） | https://en.wikipedia.org/wiki/Ethan_de_Groot |
| 修正 | タアバオ caps 8 | 22 | https://en.wikipedia.org/wiki/Angus_Ta%27avao |
| 修正 | タバタバナワイ フィジー代表 | ニュージーランド代表 | https://en.wikipedia.org/wiki/Timoci_Tavatavanawai |
（本文：オタゴ等3協会・フォーサイスバー・名称由来・2015決勝・田中2013–16・姫野2021を確認。Wingham・CaseyはWikipedia 2026 squadで昇格選手として確認）

### src/content/news/super-rugby-hurricanes-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | 本拠地 ウェストパック・スタジアム | Hnryスタジアム | https://en.wikipedia.org/wiki/Hurricanes_(rugby_union) |
| 修正 | ロマックス caps 27 | 55 | https://en.wikipedia.org/wiki/Tyrel_Lomax |
| 修正 | ディアンズ caps 21 | 37 | https://en.wikipedia.org/wiki/Warner_Dearns |
| 修正 | シールズ ニュージーランド代表 | イングランド代表 | https://en.wikipedia.org/wiki/Brad_Shields |
| 修正 | エナリ caps 7 | 11 | https://en.wikipedia.org/wiki/Ere_Enari |
| 修正 | ロワガード caps 2 | 25 | https://en.wikipedia.org/wiki/Cam_Roigard |
| 修正 | J.バレット caps 52 | 85 | https://en.wikipedia.org/wiki/Jordie_Barrett |
（本文：7協会・黄と黒・2016優勝/2015決勝・ポウア2022アウピキ参加を en/ja.wikipedia で確認。PetaiaはWikipedia 2026 squadで昇格選手として確認）

### src/content/news/super-rugby-moana-pasifika-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 削除 | ルーツの例示「マオリ」 | （削除） | 検証不可：en.wikipedia Moana Pasifika |
| 削除 | 州協会を代表しない独自のアイデンティティ | （削除） | 検証不可：en.wikipedia Moana Pasifika |
| 修正 | P.ラトゥ caps 1 | —（infobox 2025更新） | https://en.wikipedia.org/wiki/Paula_Latu |
| 修正 | モリ caps 13 | 25 | https://en.wikipedia.org/wiki/Sam_Moli |
| 削除 | ポロニアティ（NZ代表・ロック）行 | （削除） | 検証不可：公式2026スコッド発表・PMN掲載スコッド・en.wikipedia Moana Pasifikaに記載なし |
| 修正 | ファイラギ caps 3 | 9 | https://en.wikipedia.org/wiki/Miracle_Fai%CA%BBilagi |
| 修正 | パエア caps 3 | 13 | https://en.wikipedia.org/wiki/Semisi_Paea |
| 削除 | N.ジョーンズ「ニュージーランド代表」 | 代表表から削除し「その他在籍選手」へ移動（在籍は公式スコッドで確認、代表歴はinfoboxに無し） | https://en.wikipedia.org/wiki/Niko_Jones |
| 修正 | プル トンガ代表 caps 3 | 10 | https://en.wikipedia.org/wiki/Augustine_Pulu |
| 修正 | マタバオ caps 13 | —（infobox 2023更新） | https://en.wikipedia.org/wiki/Melani_Matavao |
| 修正 | タウマテイン caps 11 | —（infobox 2023更新） | https://en.wikipedia.org/wiki/Jonathan_Taumateine |
| 修正 | サベア caps 35 | —（infobox 2025更新） | https://en.wikipedia.org/wiki/Julian_Savea |
| 削除 | S-P.トレアフォア（サモア代表）行 | （削除） | 検証不可：公式2026スコッド発表・PMN掲載スコッド |
| 削除 | ロラニ・ファレイバ（PR） | （削除） | 検証不可：同上 |
| 削除 | サム・トゥイトゥポウ（FL） | （削除） | 検証不可：同上 |
| 削除 | コンラッド・トレアフォア（FL） | （削除） | 検証不可：同上 |
| 削除 | デンゼル・サモア（WTB） | （削除） | 検証不可：同上 |
（本文：2020創設・2022参入・ノースハーバー・サモア/トンガ開催・2024 PMA・2026/4/15解散発表（財政難）を確認）

### src/content/news/super-rugby-nsw-waratahs-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | F.ファインガア caps 11 | —（infobox 2022更新・値不一致） | https://en.wikipedia.org/wiki/Folau_Fainga%27a |
| 修正 | フィリップ caps 29 | —（infobox 2023更新・値不一致） | https://en.wikipedia.org/wiki/Matt_Philip |
| 修正 | ケラウェイ caps 24 | —（infobox 2025更新・値不一致） | https://en.wikipedia.org/wiki/Andrew_Kellaway_(rugby_union) |
| 修正 | ヨーゲンセン caps 20 | 28 | https://en.wikipedia.org/wiki/Max_Jorgensen |
（本文：NSWRU1874・1927–28遠征31戦24勝2分・1937年SCGでスプリングボクス撃破・1930年代・1996年スーパー12参戦を確認。Scott-YoungはWikipedia 2026 squad、GroverはSuper Rugby AUS squadで確認）

### src/content/news/super-rugby-queensland-reds-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | ノングガー caps 3 | 20 | https://en.wikipedia.org/wiki/Zane_Nonggorr |
| 修正 | フェスラー caps 2 | —（infobox 2023更新） | https://en.wikipedia.org/wiki/Matt_Faessler |
| 修正 | サラカイア・ロト caps 16 | 48 | https://en.wikipedia.org/wiki/Lukhan_Salakaia-Loto |
| 修正 | マクライト caps 13 | 47 | https://en.wikipedia.org/wiki/Fraser_McReight |
| 修正 | マクダーモット caps 26 | 56 | https://en.wikipedia.org/wiki/Tate_McDermott |
| 修正 | C.ゴードン caps 5 | 12 | https://en.wikipedia.org/wiki/Carter_Gordon |
| 修正 | ヴォラヴォラ caps 38 | —（infoboxに代表更新日なし） | https://en.wikipedia.org/wiki/Ben_Volavola |
| 修正 | パイサミ サモア代表 | オーストラリア代表 | https://en.wikipedia.org/wiki/Hunter_Paisami |
| 修正 | ダウグヌ フィジー代表 | オーストラリア代表 | https://en.wikipedia.org/wiki/Filipo_Daugunu |
| 削除 | ニック・リナー（WTB） | （削除） | 検証不可：公式2026スコッド発表・en.wikipedia Queensland Reds 2026 squad |
（本文：1876年初試合・1883年北部RU・1996年3チーム参加・1996/99マイナープレミア確認。V.Latu・Mackay・RubensはWikipedia 2026 squad（DEV）で確認）

### src/content/news/super-rugby-western-force-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | 創設年 2006年 | 2005年 | https://en.wikipedia.org/wiki/Western_Force |
| 修正 | 本拠地 スビアコ・オーバル | HBFパーク（スビアコは2006–09年のみ使用） | https://en.wikipedia.org/wiki/Western_Force |
| 修正 | マット・ジトー（表記） | マット・ギタウ | https://en.wikipedia.org/wiki/Western_Force |
| 修正 | フォトゥアイカ caps 5 | —（infobox 2025更新・値不一致） | https://en.wikipedia.org/wiki/Feao_Fotuaika |
| 修正 | ドリー オーストラリア代表 | イングランド代表 | https://en.wikipedia.org/wiki/Nic_Dolly |
| 修正 | ペンガ・アモサ ニュージーランド代表 | オーストラリア代表 | https://en.wikipedia.org/wiki/Brandon_Paenga-Amosa |
| 修正 | ドナルドソン caps 3 | 26 | https://en.wikipedia.org/wiki/Ben_Donaldson_(rugby_union) |
| 修正 | ブリッジ caps 5 | —（infobox 2021更新・値不一致） | https://en.wikipedia.org/wiki/George_Bridge |
| 修正 | ビール caps 95 | —（infobox 2025更新） | https://en.wikipedia.org/wiki/Kurtley_Beale |
（本文：2006年スーパー14参戦・ギタウ獲得（豪フットボール史上最高年俸）・2017除外・NRC/GRR・2020復帰・2022恒久復帰を確認。Epenisa・Oviedo・Daly・PalmerはWikipedia 2026 squadで確認）

### src/content/news/super-rugby-pacific-team-guide-2025-26.md
| 区分 | 元の記述（要約可、60字以内） | 処置後 | 根拠URL |
|---|---|---|---|
| 修正 | チーフス本拠地 ワイカト・スタジアム | FMGスタジアム・ワイカト | https://en.wikipedia.org/wiki/Chiefs_(rugby_union) |
| 修正 | リーチ 2015・2016年にチーフス在籍 | 2015〜2017年 | https://en.wikipedia.org/wiki/Michael_Leitch |
| 修正 | ハリケーンズ本拠地 ウェストパック・スタジアム | Hnryスタジアム | https://en.wikipedia.org/wiki/Hurricanes_(rugby_union) |
| 削除 | 風の強い港町にちなんだ「嵐」の名 | （削除） | 検証不可：en/ja.wikipedia Hurricanes（名称由来の記載なし） |
| 削除 | オーストラリアのラグビー発祥の地・シドニー | 「シドニーを代表するチーム」 | 検証不可：en/ja.wikipedia Waratahs |
| 修正 | ウィル・グレニア（表記） | ウィル・ゲニア（2011年在籍はPilecki Medal 2011で確認） | https://en.wikipedia.org/wiki/Queensland_Reds |
| 修正 | フォース創設年 2006年（本文・まとめ表） | 2005年 | https://en.wikipedia.org/wiki/Western_Force |
| 削除 | 「ラグビーオーストラリアによって」除外 | （削除） | 検証不可：en.wikipedia Western Force（SANZAARの削減として記載） |
| 修正 | コロナ禍でNRCが廃止…存続を訴え続け | NRCは放映契約の変更に伴い廃止されたが | https://en.wikipedia.org/wiki/Fijian_Drua |
| 削除 | バカタワはヨーロッパから凱旋した速射砲アタッカー | （削除） | 検証不可：NZ生まれ・仏代表（https://en.wikipedia.org/wiki/Virimi_Vakatawa）、凱旋の根拠なし |
| 削除 | ルーツ例示「マオリ」／州協会を代表しないコンセプトで2022年に誕生 | 「2022年にスーパーラグビーへ参入した」 | 検証不可：en.wikipedia Moana Pasifika |
（確認済：シティティ2024年WR年間ブレイクスルー賞 https://www.world.rugby/news/974759/world-rugby-awards-2024-winners?lang=en 、J.バレットはボーデンの弟（生年1997/1991）、ボイドHC2015–18で2016優勝、J.ジョセフ元日本代表HC、E.ジョーンズ元イングランドHC、ブランビーズ2000年から5季連続PO（ja.wikipedia）、スアアリイ2024年代表デビュー、モヤノ＝アルゼンチン出身、2022年「パシフィック」改称）
（要判断：クルセイダーズ「ロバートソン時代の7シーズンで5回優勝」はタイトル歴のため未処置だが、Wikipediaでは2017–2023の7連覇。ブランビーズ創設年はen.wikipedia=1995年・ja.wikipedia=1996年で割れるため据え置き）

### 集計（担当全体）
- 記事数：23（チームページ11・ニュース12）
- 修正：94件
- 削除：18件
- 要判断：3件（①caps列を2026-10時点値へ更新したが各記事末尾「データ基準日: 2026-04-21」は据え置き ②クルセイダーズ「7シーズンで5回優勝」（タイトル歴で対象外） ③ブランビーズ創設年1995/1996の資料不一致）

（親による追補）チーム別記事11本の「データ基準日」を caps 更新に合わせ 2026-10-14 に変更。

