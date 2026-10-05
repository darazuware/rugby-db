# data/master 整合性監査 全件リスト（自動生成）

生成: `python3 -m pipeline.validate.master_audit --md docs/renewal/validation_findings.md`

| severity | 件数 |
|---|---|
| error | 79 |
| warn | 1278 |
| info | 170 |

## age_grade_age（22件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| error | players/age-grade.json | jrfu_u17_319611 | squad=u17 だが birthdate=2002-10-26（2026年に 24 歳） / {"name": "吉村隆志", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319611"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319612 | squad=u17 だが birthdate=2002-11-27（2026年に 24 歳） / {"name": "松井亜星", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319612"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319613 | squad=u17 だが birthdate=2002-09-17（2026年に 24 歳） / {"name": "亀山昇太郎", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319613"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319614 | squad=u17 だが birthdate=2002-10-09（2026年に 24 歳） / {"name": "本田啓", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319614"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319615 | squad=u17 だが birthdate=2002-07-04（2026年に 24 歳） / {"name": "松永壮太朗", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319615"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319616 | squad=u17 だが birthdate=2002-10-29（2026年に 24 歳） / {"name": "福田大晟", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319616"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319617 | squad=u17 だが birthdate=2002-07-03（2026年に 24 歳） / {"name": "登根大斗", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319617"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319618 | squad=u17 だが birthdate=2002-05-09（2026年に 24 歳） / {"name": "寺下功起", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319618"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319621 | squad=u17 だが birthdate=2002-10-10（2026年に 24 歳） / {"name": "小林龍司", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319621"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319622 | squad=u17 だが birthdate=2002-07-09（2026年に 24 歳） / {"name": "村尾幹太", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319622"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319623 | squad=u17 だが birthdate=2002-06-14（2026年に 24 歳） / {"name": "青木恵斗", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319623"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319624 | squad=u17 だが birthdate=2002-07-24（2026年に 24 歳） / {"name": "二重賢治", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319624"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319625 | squad=u17 だが birthdate=2002-12-28（2026年に 24 歳） / {"name": "吉田爽真", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319625"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319626 | squad=u17 だが birthdate=2003-01-04（2026年に 23 歳） / {"name": "佐藤健次", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319626"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319627 | squad=u17 だが birthdate=2002-09-04（2026年に 24 歳） / {"name": "福井蓮", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319627"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319628 | squad=u17 だが birthdate=2002-06-01（2026年に 24 歳） / {"name": "宮尾昌典", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319628"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319629 | squad=u17 だが birthdate=2002-10-21（2026年に 24 歳） / {"name": "久木野太一", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319629"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319630 | squad=u17 だが birthdate=2002-10-21（2026年に 24 歳） / {"name": "江口翔", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319630"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319631 | squad=u17 だが birthdate=2002-05-16（2026年に 24 歳） / {"name": "秋濱悠太", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319631"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319632 | squad=u17 だが birthdate=2002-07-08（2026年に 24 歳） / {"name": "安田昂平", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319632"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319633 | squad=u17 だが birthdate=2002-07-28（2026年に 24 歳） / {"name": "坂本公平", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319633"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |
| error | players/age-grade.json | jrfu_u17_319634 | squad=u17 だが birthdate=2002-04-10（2026年に 24 歳） / {"name": "吉野遼", "source_url": "https://www.rugby-japan.jp/u17/member/detail/319634"} | 生年月日の誤パース/他人の値か、スタッフ混入。公式ページで確認 | 要 |

## callup_date（1件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| error | callups/national.json | callup_national_53968 | start_date=2027-03-01 が scraped_at=2026-09-28T12:01:27+09:00 の153日後（タイトル『（9/21更新）男子日本代表 宮崎合宿 参加メンバーのお知らせ』）。日付パース誤りの疑い | 本文の日付をスクレイパーで再取得 | 要 |

## callup_order（1件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| error | callups/national.json | callup_national_53968>callup_national_54087 | news_id 昇順（53968<54087）なのに start_date が逆転 （2027-03-01 > 2026-07-25） | 記事の掲載年をスクレイパーで取得し start_date の年補完ロジックを修正 | 要 |

## callup_player_ref（17件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| error | callups/national.json | callup_national_54087:jrfu_national_510411 | player_id が players/* にも player_merges にも無い（イノケ・ブルア） |  |  |
| error | callups/national.json | callup_national_54087:jrfu_national_510424 | player_id が players/* にも player_merges にも無い（平 翔太 ※1.） |  |  |
| error | callups/national.json | callup_national_54087:jrfu_national_510431 | player_id が players/* にも player_merges にも無い（平野 叶翔） |  |  |
| error | callups/national.json | callup_national_54087:jrfu_national_510438 | player_id が players/* にも player_merges にも無い（渡邊 晴斗） |  |  |
| error | callups/national.json | callup_national_54087:jrfu_national_510441 | player_id が players/* にも player_merges にも無い（木田 晴斗） |  |  |
| error | callups/national.json | callup_national_54111:jrfu_national_510663 | player_id が players/* にも player_merges にも無い（イノケ・ブルア） |  |  |
| error | callups/national.json | callup_national_54111:jrfu_national_510683 | player_id が players/* にも player_merges にも無い（平野 叶翔） |  |  |
| error | callups/national.json | callup_national_54139:jrfu_national_511558 | player_id が players/* にも player_merges にも無い（平野 叶翔） |  |  |
| warn | callups/national.json | callup_national_54087 | player_id=null: 池田 悠希 ※2. Yuki IKEDA |  |  |
| warn | callups/national.json | callup_national_54111 | player_id=null: 稲場 巧 ※1 Takumi INABA |  |  |
| warn | callups/national.json | callup_national_54111 | player_id=null: サム・グリーン ※1 Sam GREENE |  |  |
| warn | callups/national.json | callup_national_54139 | player_id=null: 加藤 一希 ※9. Kazuki KATO |  |  |
| warn | callups/national.json | callup_national_54139 | player_id=null: 古畑 翔 ※7. Sho FURUHATA |  |  |
| warn | callups/national.json | callup_national_54139 | player_id=null: 佐藤 健次 Kenji SATO |  |  |
| warn | callups/national.json | callup_national_54139 | player_id=null: 木村 星南 ※5. Sena KIMURA |  |  |
| warn | callups/national.json | callup_national_54139 | player_id=null: 武藤 ゆらぎ ※3. Yuragi MUTO |  |  |
| warn | callups/national.json | callup_national_54139 | player_id=null: 植田 和磨 Kazuma UEDA |  |  |

## dup_person（1件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| error | players/league-one-d1.json | lo_announced_jumpei-ogura | name_ja+birthdate+squad が lo_484838 と一致 | 同一人物なら一方を除去 |  |

## dup_slug（19件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| error | players/* | aki-tuivailala | リーグ横断で別 id が同一 slug を使用: ['ar_aki-tuivailala', 'lo_announced_aki-tuivailala'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | antonio-shalfoon | リーグ横断で別 id が同一 slug を使用: ['ar_antonio-shalfoon', 'lo_announced_antonio-shalfoon'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | aphelele-fassi | リーグ横断で別 id が同一 slug を使用: ['ar_aphelele-fassi', 'lo_announced_aphelele-fassi'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | bailey-trew | リーグ横断で別 id が同一 slug を使用: ['ar_bailey-trew', 'lo_announced_bailey-trew'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | david-havili | リーグ横断で別 id が同一 slug を使用: ['ar_david-havili', 'lo_announced_david-havili'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | ed-kasprowicz | リーグ横断で別 id が同一 slug を使用: ['ar_ed-kasprowicz', 'lo_announced_ed-kasprowicz'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | george-bridge | リーグ横断で別 id が同一 slug を使用: ['ar_george-bridge', 'lo_announced_george-bridge'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | grant-williams | リーグ横断で別 id が同一 slug を使用: ['ar_grant-williams', 'lo_announced_grant-williams'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | hunter-paisami | リーグ横断で別 id が同一 slug を使用: ['ar_hunter-paisami', 'lo_announced_hunter-paisami'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | jack-dempsey | リーグ横断で別 id が同一 slug を使用: ['ar_jack-dempsey', 'lo_announced_jack-dempsey'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | james-lowe | リーグ横断で別 id が同一 slug を使用: ['ar_james-lowe', 'lo_announced_james-lowe'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | jonah-lowe | リーグ横断で別 id が同一 slug を使用: ['ar_jonah-lowe', 'lo_announced_jonah-lowe'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | keran-van-staden | リーグ横断で別 id が同一 slug を使用: ['ar_keran-van-staden', 'lo_announced_keran-van-staden'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | kurt-eklund | リーグ横断で別 id が同一 slug を使用: ['ar_kurt-eklund', 'lo_announced_kurt-eklund'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | kurt-lee-arendse | リーグ横断で別 id が同一 slug を使用: ['ar_kurt-lee-arendse', 'lo_announced_kurt-lee-arendse'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | laghlan-mcwhannell | リーグ横断で別 id が同一 slug を使用: ['ar_laghlan-mcwhannell', 'lo_announced_laghlan-mcwhannell'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | ruan-nortje | リーグ横断で別 id が同一 slug を使用: ['ar_ruan-nortje', 'lo_announced_ruan-nortje'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | samipeni-finau | リーグ横断で別 id が同一 slug を使用: ['ar_samipeni-finau', 'lo_announced_samipeni-finau'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |
| error | players/* | stephen-perofeta | リーグ横断で別 id が同一 slug を使用: ['ar_stephen-perofeta', 'lo_announced_stephen-perofeta'] | 同一人物なら player_merges.json に登録、別人なら slug を分離 |  |

## episode_ref（1件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| error | players/episodes/jrfu_callup_ruan-botha.json | jrfu_callup_ruan-botha | player_id が players/* にも player_merges にも無い | 現存 id に付け替え（player_merges 登録 or ファイル名変更） |  |

## match_team_ref（16件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| error | matches/national_2026.json | jrfu_29964 | home_team_id='japan-xv' が teams/*.json に存在しない | teams/national.json（現在 0件）を整備 |  |
| error | matches/national_2026.json | jrfu_29964 | away_team_id='maori-all-blacks' が teams/*.json に存在しない | teams/national.json（現在 0件）を整備 |  |
| error | matches/national_2026.json | jrfu_29966 | home_team_id='japan' が teams/*.json に存在しない | teams/national.json（現在 0件）を整備 |  |
| error | matches/national_2026.json | jrfu_29966 | away_team_id='italy' が teams/*.json に存在しない | teams/national.json（現在 0件）を整備 |  |
| error | matches/national_2026.json | jrfu_29967 | home_team_id='japan' が teams/*.json に存在しない | teams/national.json（現在 0件）を整備 |  |
| error | matches/national_2026.json | jrfu_29967 | away_team_id='france' が teams/*.json に存在しない | teams/national.json（現在 0件）を整備 |  |
| error | matches/national_2026.json | jrfu_29968 | home_team_id='japan' が teams/*.json に存在しない | teams/national.json（現在 0件）を整備 |  |
| error | matches/national_2026.json | jrfu_29968 | away_team_id='australia' が teams/*.json に存在しない | teams/national.json（現在 0件）を整備 |  |
| error | matches/national_2026.json | jrfu_29969 | home_team_id='japan' が teams/*.json に存在しない | teams/national.json（現在 0件）を整備 |  |
| error | matches/national_2026.json | jrfu_29969 | away_team_id='ireland' が teams/*.json に存在しない | teams/national.json（現在 0件）を整備 |  |
| error | matches/national_2026.json | jrfu_29975 | home_team_id='japan' が teams/*.json に存在しない | teams/national.json（現在 0件）を整備 |  |
| error | matches/national_2026.json | jrfu_29975 | away_team_id='canada' が teams/*.json に存在しない | teams/national.json（現在 0件）を整備 |  |
| error | matches/national_2026.json | jrfu_29986 | home_team_id='japan' が teams/*.json に存在しない | teams/national.json（現在 0件）を整備 |  |
| error | matches/national_2026.json | jrfu_29986 | away_team_id='scotland' が teams/*.json に存在しない | teams/national.json（現在 0件）を整備 |  |
| error | matches/national_2026.json | jrfu_30035 | home_team_id='japan' が teams/*.json に存在しない | teams/national.json（現在 0件）を整備 |  |
| error | matches/national_2026.json | jrfu_30035 | away_team_id='australia' が teams/*.json に存在しない | teams/national.json（現在 0件）を整備 |  |

## name_not_person（2件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| error | players/university.json | univ_國學院大學__経済学部経済学科 | name_ja='経済学部\u3000経済学科' は人名でない語を含む（名簿パース時の見出し/所属行の誤取り込み疑い） | 名簿パーサの行判定を修正し再取得 | 要 |
| error | players/university.json | univ_慶應義塾大学__慶應志木派遣学生コーチ | name_ja='慶應志木 派遣学生コーチ' は人名でない語を含む（名簿パース時の見出し/所属行の誤取り込み疑い） | 名簿パーサの行判定を修正し再取得 | 要 |

## roster_contamination（4件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| error | teams/* | bath+dragons+pau | 27 人が同時に ('bath', 'dragons', 'pau') の full roster に重複所属。同一組み合わせへの集中はスクレイパーが別クラブのスカッドページを混入させた疑い | 該当クラブの squad ページ取得処理（URL・ページング・キャッシュ）を確認し再取得 | 要 |
| error | teams/* | glasgow+gloucester+la-rochelle | 28 人が同時に ('glasgow', 'gloucester', 'la-rochelle') の full roster に重複所属。同一組み合わせへの集中はスクレイパーが別クラブのスカッドページを混入させた疑い | 該当クラブの squad ページ取得処理（URL・ページング・キャッシュ）を確認し再取得 | 要 |
| error | teams/* | gloucester+la-rochelle | 4 人が同時に ('gloucester', 'la-rochelle') の full roster に重複所属。同一組み合わせへの集中はスクレイパーが別クラブのスカッドページを混入させた疑い | 該当クラブの squad ページ取得処理（URL・ページング・キャッシュ）を確認し再取得 | 要 |
| error | teams/* | harlequins+pau | 3 人が同時に ('harlequins', 'pau') の full roster に重複所属。同一組み合わせへの集中はスクレイパーが別クラブのスカッドページを混入させた疑い | 該当クラブの squad ページ取得処理（URL・ページング・キャッシュ）を確認し再取得 | 要 |

## standings_rows_missing（2件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| error | standings/mlr_unknown.json | mlr_unknown | rank 欠番 [1]（5行 / teams 6チーム） / {"missing_teams": ["chicago"]} | 欠落行は数値欠落で除外された可能性（last_run warnings参照）。公式順位表で再取得 | 要 |
| error | standings/top14_2026-27.json | top14_2026-27 | rank 欠番 [1, 2, 3, 12, 13, 14]（8行 / teams 14チーム） / {"missing_teams": ["la-rochelle", "lyon", "pau", "racing-92", "toulon", "vannes"]} | 欠落行は数値欠落で除外された可能性（last_run warnings参照）。公式順位表で再取得 | 要 |

## standings_season（2件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| error | standings/mlr_unknown.json | mlr_unknown | season='unknown' | ソースページからシーズン表記を取得してファイル名ごと修正 | 要 |
| error | standings/super-rugby_unknown.json | super-rugby_unknown | season='unknown' | ソースページからシーズン表記を取得してファイル名ごと修正 | 要 |

## callup_caps_vs_player（35件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | callups/national.json | ar_ben-gunter | 最新 callup caps=22（callup_national_54139）/ players/national caps=31（https://all.rugby/player/ben-gunter） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_dylan-riley | 最新 callup caps=43（callup_national_54139）/ players/national caps=54（https://all.rugby/player/dylan-riley） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_esei-ha-angana | 最新 callup caps=1（callup_national_54139）/ players/national caps=5（https://all.rugby/player/esei-ha-angana） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_harry-hockings | 最新 callup caps=7（callup_national_54139）/ players/national caps=10（https://all.rugby/player/harry-hockings） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_haruto-kida | 最新 callup caps=3（callup_national_54139）/ players/national caps=5（https://all.rugby/player/haruto-kida） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_hayate-era | 最新 callup caps=10（callup_national_54111）/ players/national caps=11（https://all.rugby/player/hayate-era） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_inoke-burua | 最新 callup caps=0（callup_national_54139）/ players/national caps=3（https://all.rugby/player/inoke-burua） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_itsuki-kamimura | 最新 callup caps=2（callup_national_54111）/ players/national caps=4（https://all.rugby/player/itsuki-kamimura） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_izi-sword | 最新 callup caps=2（callup_national_54139）/ players/national caps=3（https://all.rugby/player/izi-sword） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_jack-cornelsen | 最新 callup caps=34（callup_national_54139）/ players/national caps=45（https://all.rugby/player/jack-cornelsen） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_kazuma-ueda | 最新 callup caps=6（callup_national_54111）/ players/national caps=10（https://all.rugby/player/kazuma-ueda） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_keijiro-tamefusa | 最新 callup caps=23（callup_national_54087）/ players/national caps=32（https://all.rugby/player/keijiro-tamefusa） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_kenji-sato- | 最新 callup caps=10（callup_national_54111）/ players/national caps=15（https://all.rugby/player/kenji-sato-） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_kenta-fukuda | 最新 callup caps=8（callup_national_54139）/ players/national caps=13（https://all.rugby/player/kenta-fukuda） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_kippei-ishida | 最新 callup caps=11（callup_national_54087）/ players/national caps=9（https://all.rugby/player/kippei-ishida） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_lua-makisi | 最新 callup caps=25（callup_national_54139）/ players/national caps=34（https://all.rugby/player/lua-makisi） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_mamoru-harada | 最新 callup caps=16（callup_national_54139）/ players/national caps=22（https://all.rugby/player/mamoru-harada） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_michael-leitch | 最新 callup caps=96（callup_national_54111）/ players/national caps=81（https://all.rugby/player/michael-leitch） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_mike-stolberg | 最新 callup caps=3（callup_national_54139）/ players/national caps=8（https://all.rugby/player/mike-stolberg） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_naoto-saito | 最新 callup caps=33（callup_national_54139）/ players/national caps=46（https://all.rugby/player/naoto-saito） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_ryosuke-iwaihara | 最新 callup caps=5（callup_national_54139）/ players/national caps=7（https://all.rugby/player/ryosuke-iwaihara） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_ryunosuke-ito | 最新 callup caps=5（callup_national_54139）/ players/national caps=9（https://all.rugby/player/ryunosuke-ito） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_sam-greene | 最新 callup caps=7（callup_national_54139）/ players/national caps=18（https://all.rugby/player/sam-greene） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_samisoni-tua | 最新 callup caps=6（callup_national_54139）/ players/national caps=8（https://all.rugby/player/samisoni-tua） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_shinobu-fujiwara | 最新 callup caps=19（callup_national_54139）/ players/national caps=26（https://all.rugby/player/shinobu-fujiwara） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_shuhei-takeuchi | 最新 callup caps=28（callup_national_54139）/ players/national caps=41（https://all.rugby/player/shuhei-takeuchi） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_sojiro-otsuka | 最新 callup caps=5（callup_national_54139）/ players/national caps=7（https://all.rugby/player/sojiro-otsuka） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_takato-okabe | 最新 callup caps=13（callup_national_54139）/ players/national caps=19（https://all.rugby/player/takato-okabe） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_takumi-inaba | 最新 callup caps=0（callup_national_54139）/ players/national caps=3（https://all.rugby/player/takumi-inaba） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_takuro-matsunaga | 最新 callup caps=10（callup_national_54139）/ players/national caps=12（https://all.rugby/player/takuro-matsunaga） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_tiennan-costley | 最新 callup caps=16（callup_national_54139）/ players/national caps=22（https://all.rugby/player/tiennan-costley） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_tomoki-osada | 最新 callup caps=26（callup_national_54139）/ players/national caps=32（https://all.rugby/player/tomoki-osada） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_warner-dearns | 最新 callup caps=36（callup_national_54111）/ players/national caps=40（https://all.rugby/player/warner-dearns） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_yoshitaka-yazaki | 最新 callup caps=10（callup_national_54111）/ players/national caps=12（https://all.rugby/player/yoshitaka-yazaki） | ソース・時点の差。公式記録で確認 | 要 |
| warn | callups/national.json | ar_yuya-hirose | 最新 callup caps=7（callup_national_54139）/ players/national caps=10（https://all.rugby/player/yuya-hirose） | ソース・時点の差。公式記録で確認 | 要 |

## callup_name_annotation（28件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | callups/national.json | callup_national_53968:ar_esei-ha-angana | name_ja='エセイ・ハアンガナ ※1.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_53968:ar_haruto-kida | name_ja='木田 晴斗 ※11.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_53968:ar_izi-sword | name_ja='イジー・ソード ※1.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_53968:ar_mamoru-harada | name_ja='原田 衛 ※1.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_53968:ar_mike-stolberg | name_ja='マイケル・ストーバーグ ※1.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_53968:ar_ryunosuke-ito | name_ja='伊藤 龍之介 ※1.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_53968:ar_samisoni-tua | name_ja='サミソニ・トゥア ※1.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_53968:ar_shinya-komura | name_ja='小村 真也 ※1 ※6.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_53968:ar_sojiro-otsuka | name_ja='大塚 壮二郎 ※1.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_53968:ar_takato-okabe | name_ja='岡部 崇人 ※1.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_53968:ar_takuro-matsunaga | name_ja='松永 拓朗 ※1.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_53968:jrfu_callup_haruto-watanabe | name_ja='渡邊 晴斗 ※1.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_53968:jrfu_callup_shogo-nakano | name_ja='中野 将伍 ※11.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_53968:jrfu_callup_takuro-hojo | name_ja='北條 拓郎 ※1. ※11.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_53968:jrfu_callup_yota-kamimori | name_ja='紙森 陽太 ※7.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_54087:None | name_ja='池田 悠希 ※2. Yuki IKEDA' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_54087:jrfu_national_510424 | name_ja='平 翔太 ※1.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_54111:None | name_ja='稲場 巧 ※1 Takumi INABA' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_54111:None | name_ja='サム・グリーン ※1 Sam GREENE' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_54139:None | name_ja='加藤 一希 ※9. Kazuki KATO' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_54139:None | name_ja='古畑 翔 ※7. Sho FURUHATA' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_54139:None | name_ja='木村 星南 ※5. Sena KIMURA' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_54139:None | name_ja='武藤 ゆらぎ ※3. Yuragi MUTO' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_54139:ar_izi-sword | name_ja='イジー・ソード ※4.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_54139:ar_ryosuke-iwaihara | name_ja='祝原 涼介 ※6.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_54139:ar_shunsuke-uenobo | name_ja='上ノ坊 駿介 ※2.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_54139:ar_takato-okabe | name_ja='岡部 崇人 ※8.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |
| warn | callups/national.json | callup_national_54139:ar_takumi-inaba | name_ja='稲場 巧 ※1.' に注記記号が混入 | スクレイパーで注記（※n.）を除去し別フィールド化 |  |

## callup_name_mismatch（15件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | callups/national.json | callup_national_53968:ar_esei-ha-angana | callup name_en='Esei HAANGANA' / players/national name_en="Esei HA'ANGANA" |  | 要 |
| warn | callups/national.json | callup_national_53968:ar_mike-stolberg | callup name_en='Michael STOLBERG' / players/national name_en='Mike STOLBERG' |  | 要 |
| warn | callups/national.json | callup_national_53968:jrfu_callup_haruto-watanabe | callup name_ja='渡邊 晴斗 ※1.' / players/national name_ja='渡邊 晴斗 ※1.' |  | 要 |
| warn | callups/national.json | callup_national_53968:jrfu_callup_shogo-nakano | callup name_ja='中野 将伍 ※11.' / players/national name_ja='中野 将伍 ※11.' |  | 要 |
| warn | callups/national.json | callup_national_53968:jrfu_callup_takuro-hojo | callup name_ja='北條 拓郎 ※1. ※11.' / players/national name_ja='北條 拓郎 ※1. ※11.' |  | 要 |
| warn | callups/national.json | callup_national_53968:jrfu_callup_yota-kamimori | callup name_ja='紙森 陽太 ※7.' / players/national name_ja='紙森 陽太 ※7.' |  | 要 |
| warn | callups/national.json | callup_national_54087:ar_esei-ha-angana | callup name_en='Esei HAANGANA' / players/national name_en="Esei HA'ANGANA" |  | 要 |
| warn | callups/national.json | callup_national_54087:ar_lua-makisi | callup name_en='Faulua MAKISI' / players/national name_en='Lua MAKISI' |  | 要 |
| warn | callups/national.json | callup_national_54087:ar_mike-stolberg | callup name_en='Michael STOLBERG' / players/national name_en='Mike STOLBERG' |  | 要 |
| warn | callups/national.json | callup_national_54111:ar_esei-ha-angana | callup name_en='Esei HAANGANA' / players/national name_en="Esei HA'ANGANA" |  | 要 |
| warn | callups/national.json | callup_national_54111:ar_lua-makisi | callup name_en='Faulua MAKISI' / players/national name_en='Lua MAKISI' |  | 要 |
| warn | callups/national.json | callup_national_54111:ar_mike-stolberg | callup name_en='Michael STOLBERG' / players/national name_en='Mike STOLBERG' |  | 要 |
| warn | callups/national.json | callup_national_54139:ar_esei-ha-angana | callup name_en='Esei HAANGANA' / players/national name_en="Esei HA'ANGANA" |  | 要 |
| warn | callups/national.json | callup_national_54139:ar_lua-makisi | callup name_en='Faulua MAKISI' / players/national name_en='Lua MAKISI' |  | 要 |
| warn | callups/national.json | callup_national_54139:ar_mike-stolberg | callup name_en='Michael STOLBERG' / players/national name_en='Mike STOLBERG' |  | 要 |

## caps_conflict（10件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | players/* | ar_ben-spencer | リーグ間で caps 不一致: [('England', 26), ('England', 31)] | 最新 scraped_at 側を採用 | 要 |
| warn | players/* | ar_blair-murray | リーグ間で caps 不一致: [('Wales', 18), ('Wales', 24)] | 最新 scraped_at 側を採用 | 要 |
| warn | players/* | ar_cheslin-kolbe | リーグ間で caps 不一致: [('South Africa', 48), ('South Africa', 52)] | 最新 scraped_at 側を採用 | 要 |
| warn | players/* | ar_fin-smith | リーグ間で caps 不一致: [('England', 19), ('England', 21)] | 最新 scraped_at 側を採用 | 要 |
| warn | players/* | ar_jamie-dobie | リーグ間で caps 不一致: [('Scotland', 18), ('Scotland', 19)] | 最新 scraped_at 側を採用 | 要 |
| warn | players/* | ar_jean-kleyn | リーグ間で caps 不一致: [('Ireland', 5), ('South Africa', 15)] | 最新 scraped_at 側を採用 | 要 |
| warn | players/* | ar_michele-lamaro | リーグ間で caps 不一致: [('Italy', 59), ('Italy', 69)] | 最新 scraped_at 側を採用 | 要 |
| warn | players/* | ar_sam-moli | リーグ間で caps 不一致: [('Tonga', 30), ('Tonga', 33)] | 最新 scraped_at 側を採用 | 要 |
| warn | players/* | ar_scott-sio | リーグ間で caps 不一致: [('Australia', 60), ('Samoa', 2)] | 最新 scraped_at 側を採用 | 要 |
| warn | players/* | ar_tommy-freeman | リーグ間で caps 不一致: [('England', 31), ('England', 38)] | 最新 scraped_at 側を採用 | 要 |

## caps_team（1件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | players/national.json | ar_jean-kleyn | caps.team='South Africa' と team_id='ireland' 不一致 |  |  |

## cross_league_conflict（756件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | players/* | ar_aaron-grandidier | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:189", "top14:192"], "weight_kg": ["national:81", "top14:97"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_aaron-wainwright | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:181", "premiership:187"], "weight_kg": ["national:96", "premiership:106"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_abraham-papali-i | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "top14:194"], "weight_kg": ["national:126", "top14:136"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_adam-beard | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:213", "top14:199"], "weight_kg": ["national:124", "top14:119"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_adam-hastings | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:185", "top14:203"], "weight_kg": ["national:96", "top14:84"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_agustin-moyano | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:160", "super-rugby:180"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_aidan-ross | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "super-rugby:174"], "weight_kg": ["national:108", "super-rugby:129"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_aiden-stait | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:196", "top14:189", "urc:192"], "weight_kg": ["premiership:150", "top14:128", "urc:128"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_aj-lam | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:182", "top14:188"], "weight_kg": ["super-rugby:94", "top14:91"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_akenzua-al-kareem-abdul-khalik | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:189", "top14:193"], "weight_kg": ["premiership:116", "top14:108"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_aleksandre-kuntelia | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:210", "top14:206"], "weight_kg": ["national:125", "top14:128"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_alessandro-fusco | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:185", "urc:179"], "weight_kg": ["national:94", "urc:76"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_alessandro-garbisi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:162", "urc:171"], "weight_kg": ["national:86", "urc:74"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_alessandro-izekor | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:206", "urc:211"], "weight_kg": ["national:95", "urc:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_alessandro-ortombina | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:192", "urc:191"], "weight_kg": ["national:108", "urc:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_alex-coles | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:216", "premiership:203"], "weight_kg": ["national:126", "premiership:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_alex-craig | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "urc:194"], "weight_kg": ["national:104", "urc:113"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_alex-dombrandt | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "premiership:195"], "weight_kg": ["national:131", "premiership:126"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_alex-mann | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:197", "urc:205"], "weight_kg": ["national:84", "urc:98"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_alex-maughan | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:190", "national:174"], "weight_kg": ["mlr:125", "national:119"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_alex-mitchell | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:180", "premiership:167"], "weight_kg": ["national:79", "premiership:92"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_alex-samuel | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:212", "urc:201"], "weight_kg": ["national:121", "urc:130"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_alexandre-roumat | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "top14:188"], "weight_kg": ["national:124", "top14:104"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_alfie-barbeary | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:196", "top14:186"], "weight_kg": ["premiership:109", "top14:113"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_alfred-parisien | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:181", "top14:182"], "weight_kg": ["national:81", "top14:95"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_allan-alaalatoa | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:169", "super-rugby:184"], "weight_kg": ["national:130", "super-rugby:128"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_alvaro-garcia | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:167", "top14:179"], "weight_kg": ["national:116", "top14:105"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_andre-esterhuizen | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:207", "urc:181"], "weight_kg": ["national:114", "urc:110"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_andre-hugo-venter | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "urc:191"], "weight_kg": ["national:118", "urc:106"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_andre-riaan-warner | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:197", "urc:175"], "weight_kg": ["mlr:102", "urc:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_andrea-zambonin | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:189", "premiership:207"], "weight_kg": ["national:122", "premiership:113"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_andrew-kellaway | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:108", "super-rugby:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_andrew-porter | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:179", "urc:192"], "weight_kg": ["national:138", "urc:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_andrew-quattrin | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:171", "national:179"], "weight_kg": ["mlr:113", "national:107"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_andro-dvali | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "top14:203"], "weight_kg": ["national:96", "top14:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_andy-christie | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:175", "premiership:187"], "weight_kg": ["national:99", "premiership:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ange-capuozzo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "top14:168"], "weight_kg": ["national:73", "top14:81"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_anthony-jelonch | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:181", "top14:183"], "weight_kg": ["national:97", "top14:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_antoine-dupont | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:185", "top14:171"], "weight_kg": ["national:73", "top14:80"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_antoine-hastoy | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:181", "top14:194"], "weight_kg": ["national:77", "top14:92"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_anton-segner | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:196", "super-rugby:203"], "weight_kg": ["national:108", "super-rugby:98"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_anzelo-tuitavuki | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "urc:175"], "weight_kg": ["national:111", "urc:112"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_archie-griffin | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:178", "premiership:196", "top14:180", "urc:192"], "weight_kg": ["national:131", "premiership:117", "top14:124", "urc:113"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_archie-stanley | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:171", "top14:167", "urc:181"], "weight_kg": ["premiership:111", "top14:106", "urc:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_arthur-cordwell | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:194", "top14:192", "urc:186"], "weight_kg": ["premiership:130", "top14:116", "urc:123"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_arthur-green | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:202", "top14:176"], "weight_kg": ["premiership:114", "top14:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_asafo-aumua | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:170", "super-rugby:168"], "weight_kg": ["national:117", "super-rugby:116"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_asher-opoku | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:200", "premiership:197"], "weight_kg": ["national:110", "premiership:116"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_atunaisa-sokobale | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:178", "top14:177"], "weight_kg": ["national:112", "top14:111"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_bachuki-tchumbadze | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:175", "premiership:180"], "weight_kg": ["national:118", "premiership:113"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_badri-tsikhistavi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:190", "top14:174", "urc:195"], "weight_kg": ["premiership:116", "top14:126", "urc:113"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_baptiste-erdocio | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:170", "top14:172"], "weight_kg": ["national:116", "top14:100"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_baptiste-jauneau | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:178", "top14:179"], "weight_kg": ["national:85", "top14:80"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_baptiste-serin | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "top14:170"], "weight_kg": ["national:76", "top14:80"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_barnabe-massa | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "top14:175"], "weight_kg": ["national:90", "top14:108"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_bautista-delguy | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:197", "top14:181"], "weight_kg": ["national:91", "top14:70"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_bayley-kuenzle | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:185", "urc:181"], "weight_kg": ["super-rugby:103", "urc:100"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_beauden-barrett | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:197", "super-rugby:176"], "weight_kg": ["national:104", "super-rugby:108"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_beka-gigashvili | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "top14:180"], "weight_kg": ["national:124", "top14:108"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_beka-gorgadze | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:176", "top14:187"], "weight_kg": ["national:107", "top14:112"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_beka-saghinadze | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "top14:179"], "weight_kg": ["national:119", "top14:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_beka-shvangiradze | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:203", "top14:198"], "weight_kg": ["national:91", "top14:90"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ben-carter | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:198", "urc:188"], "weight_kg": ["national:109", "urc:122"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ben-curry | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "premiership:175"], "weight_kg": ["national:120", "premiership:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ben-donaldson | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:180", "super-rugby:182"], "weight_kg": ["national:82", "super-rugby:87"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ben-earl | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:177", "premiership:194"], "weight_kg": ["national:110", "premiership:92"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ben-jason-dixon | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:206", "urc:189"], "weight_kg": ["national:102", "urc:112"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ben-lesage | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:183", "national:195"], "weight_kg": ["mlr:84", "national:98"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ben-spencer | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:175", "premiership:173"], "weight_kg": ["national:99", "premiership:95"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ben-tameifuna | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:175", "top14:196"], "weight_kg": ["national:148", "top14:159"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ben-thomas | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:169", "urc:189"], "weight_kg": ["national:87", "urc:96"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ben-warren | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:186", "urc:183"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ben-white | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:187", "top14:180"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_benhard-janse-van-rensburg | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "premiership:187"], "weight_kg": ["national:112", "premiership:87"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_benjamin-bonasso | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:201", "national:192"], "weight_kg": ["mlr:121", "national:110"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_benjamin-grondona | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:184", "premiership:203"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_benjamin-lahet | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:190", "top14:172", "urc:186"], "weight_kg": ["premiership:114", "top14:111", "urc:129"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_beno--obano- | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:173", "premiership:180", "top14:184", "urc:193"], "weight_kg": ["national:114", "premiership:117", "top14:129", "urc:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_bevan-rodd | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:177", "premiership:192"], "weight_kg": ["national:107", "premiership:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_billy-bohan | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "urc:199"], "weight_kg": ["national:128", "urc:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_billy-pollard | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "super-rugby:193"], "weight_kg": ["national:116", "super-rugby:97"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_billy-proctor | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:188", "super-rugby:190"], "weight_kg": ["national:107", "super-rugby:105"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_billy-sela | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:205", "top14:187", "urc:198"], "weight_kg": ["premiership:116", "top14:102", "urc:121"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_billy-vunipola | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:192", "top14:178"], "weight_kg": ["national:136", "top14:148"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_blair-kinghorn | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "top14:208"], "weight_kg": ["national:95", "top14:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_blair-murray | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:171", "urc:159"], "weight_kg": ["national:97", "urc:71"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_boan-venter | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:135", "urc:119"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_bongi-mbonambi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:171", "urc:177"], "weight_kg": ["national:125", "urc:128"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_boris-wenger | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:189", "premiership:191"], "weight_kg": ["national:107", "premiership:116"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_brandon-harvey | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:204", "national:198"], "weight_kg": ["mlr:122", "national:119"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_brandon-paenga-amosa | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:169", "super-rugby:185"], "weight_kg": ["national:123", "super-rugby:130"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_braydon-ennor | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:192", "top14:182"], "weight_kg": ["super-rugby:87", "top14:107"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_brodie-coghlan | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:192", "urc:190"], "weight_kg": ["national:120", "urc:123"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_bryn-ward | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:171", "urc:175"], "weight_kg": ["national:131", "urc:125"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_bundee-aki | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:170", "urc:173"], "weight_kg": ["national:99", "urc:110"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_cadan-murley | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:175", "premiership:192"], "weight_kg": ["national:86", "premiership:105"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_caelan-doris | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:197", "urc:194"], "weight_kg": ["national:114", "urc:116"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_caleb-clarke | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:204", "super-rugby:194"], "weight_kg": ["national:118", "super-rugby:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_calixto-martinez | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:177", "national:171"], "weight_kg": ["mlr:115", "national:124"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_callum-botchar | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:200", "national:190"], "weight_kg": ["mlr:121", "national:107"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_callum-sheedy | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:164", "urc:190"], "weight_kg": ["national:82", "urc:76"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_cameron-hanekom | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:184", "urc:183"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_cameron-roigard | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "super-rugby:198"], "weight_kg": ["national:79", "super-rugby:85"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_canan-moodie | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:197", "urc:198"], "weight_kg": ["national:81", "urc:107"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_caolin-blade | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:156", "urc:173"], "weight_kg": ["national:78", "urc:95"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_carlo-tizzano | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:175", "super-rugby:192"], "weight_kg": ["national:93", "super-rugby:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_carlu-sadie | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:170", "top14:185"], "weight_kg": ["national:125", "top14:152"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_carter-gordon | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "super-rugby:199"], "weight_kg": ["national:107", "super-rugby:93"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_cassh-maluia | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:172", "national:191"], "weight_kg": ["mlr:102", "national:126"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_chandler-cunningham-south | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:180", "premiership:197"], "weight_kg": ["national:124", "premiership:127"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_charles-ollivon | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:203", "top14:190"], "weight_kg": ["national:126", "top14:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_charlie-abel | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:192", "national:175"], "weight_kg": ["mlr:119", "national:132"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_charlie-cale | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:202", "super-rugby:208"], "weight_kg": ["national:110", "super-rugby:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_charlie-ewels | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:206", "premiership:209", "top14:187", "urc:210"], "weight_kg": ["national:122", "premiership:122", "top14:110", "urc:117"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_cheslin-kolbe | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "urc:170"], "weight_kg": ["national:78", "urc:72"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_chris-cloete | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:180", "top14:178"], "weight_kg": ["premiership:109", "top14:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_chris-coleman | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:198", "urc:186"], "weight_kg": ["national:144", "urc:134"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_christian-lio-willie | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:176", "super-rugby:173"], "weight_kg": ["national:94", "super-rugby:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_christian-poidevin | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:186", "national:198"], "weight_kg": ["mlr:99", "national:100"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_christopher-hilsenbeck | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:186", "national:178"], "weight_kg": ["mlr:73", "national:75"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_cian-prendergast | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "urc:202"], "weight_kg": ["national:119", "urc:121"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ciaran-frawley | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:177", "urc:193"], "weight_kg": ["national:101", "urc:86"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_cleopas-kundiona | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "premiership:189"], "weight_kg": ["national:119", "premiership:117"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_cobus-reinach | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:161", "urc:160"], "weight_kg": ["national:73", "urc:77"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_cobus-wiese | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "urc:212"], "weight_kg": ["national:140", "urc:119"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_codie-taylor | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:169", "super-rugby:191"], "weight_kg": ["national:104", "super-rugby:108"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_conner-mooneyham | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:174", "national:186"], "weight_kg": ["mlr:86", "national:98"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_connor-treacey | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:187", "top14:199"], "weight_kg": ["premiership:116", "top14:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_corey-toole | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:171", "super-rugby:166"], "weight_kg": ["national:71", "super-rugby:73"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_cormac-izuchukwu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:216", "urc:197"], "weight_kg": ["national:114", "urc:131"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_cortez-ratima | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:176", "super-rugby:178"], "weight_kg": ["national:85", "super-rugby:86"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_cory-gilliland-daniel | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:180", "national:186"], "weight_kg": ["mlr:116", "national:117"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_courtney-lawes | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:196", "premiership:192"], "weight_kg": ["national:108", "premiership:112"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_craig-casey | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:167", "urc:152"], "weight_kg": ["national:70", "urc:77"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_cullen-grace | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:188", "urc:196"], "weight_kg": ["super-rugby:118", "urc:93"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_d-arcy-rae | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "urc:179"], "weight_kg": ["national:121", "urc:137"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_dafydd-jenkins | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:213", "premiership:211"], "weight_kg": ["national:110", "premiership:122"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_dallas-mcleod | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:205", "super-rugby:178"], "weight_kg": ["premiership:95", "super-rugby:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_dalton-papali-i | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:197", "top14:201"], "weight_kg": ["super-rugby:123", "top14:117"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_damian-mckenzie | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:169", "super-rugby:180"], "weight_kg": ["national:90", "super-rugby:72"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_damian-penaud | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "top14:193"], "weight_kg": ["national:100", "top14:84"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_damian-willemse | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:96", "urc:102"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_dan-edwards | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:173", "urc:163"], "weight_kg": ["national:80", "urc:75"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_dan-sheehan | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:178", "urc:194"], "weight_kg": ["national:109", "urc:117"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_daniel-bibi-biziwu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:194", "top14:178"], "weight_kg": ["national:119", "top14:133"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_daniel-marais | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:192", "top14:197", "urc:182"], "weight_kg": ["premiership:101", "top14:104", "urc:93"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_danilo-fischetti | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:187", "premiership:168"], "weight_kg": ["national:135", "premiership:110"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_danny-southworth | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:194", "urc:192"], "weight_kg": ["national:120", "urc:123"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_darcy-graham | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:167", "urc:174"], "weight_kg": ["national:71", "urc:92"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_darcy-swain | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:201", "top14:194"], "weight_kg": ["super-rugby:123", "top14:124"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_darragh-murray | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:206", "urc:189"], "weight_kg": ["national:113", "urc:124"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_dave-cherry | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:173", "top14:177"], "weight_kg": ["national:96", "top14:119"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_david-coetzer | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:170", "national:180"], "weight_kg": ["mlr:72", "national:96"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_david-odiase | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:179", "urc:190"], "weight_kg": ["national:99", "urc:100"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_david-ribbans | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:207", "top14:188"], "weight_kg": ["national:132", "top14:106"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_davit-lagvilava | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:208", "top14:201"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_davit-niniashvili | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:199", "top14:183"], "weight_kg": ["national:92", "top14:96"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_declan-meredith | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:177", "super-rugby:178"], "weight_kg": ["national:79", "super-rugby:98"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_demba-bamba | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:190", "top14:172"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_denis-marchois | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:202", "top14:188", "urc:188"], "weight_kg": ["premiership:129", "top14:109", "urc:100"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_deon-fourie | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:169", "urc:178"], "weight_kg": ["national:88", "urc:101"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_dewald-kotze | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:171", "national:175"], "weight_kg": ["mlr:111", "national:104"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_dewi-lake | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "premiership:186"], "weight_kg": ["national:124", "premiership:100"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_diego-escobar | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:181", "top14:187"], "weight_kg": ["national:108", "top14:113"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_dillon-lewis | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "urc:179"], "weight_kg": ["national:126", "urc:134"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_dorian-aldegheri | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:185", "top14:190"], "weight_kg": ["national:121", "top14:119"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_du-plessis-kirifi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "super-rugby:185"], "weight_kg": ["national:117", "super-rugby:107"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_duhan-van-der-merwe | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "urc:198"], "weight_kg": ["national:119", "urc:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_dylan-pietsch | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "super-rugby:202"], "weight_kg": ["national:92", "super-rugby:100"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_dylan-richardson | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:179", "urc:195"], "weight_kg": ["national:125", "urc:104"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_eben-etzebeth | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:214", "urc:198"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_eddie-erskine | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:186", "top14:198", "urc:184"], "weight_kg": ["premiership:96", "top14:116", "urc:111"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_eddie-james | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:205", "urc:188"], "weight_kg": ["national:97", "urc:95"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_edoardo-todaro | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:195", "premiership:169"], "weight_kg": ["national:88", "premiership:79"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_edward-sigauke | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:172", "premiership:163"], "weight_kg": ["national:67", "premiership:68"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_edwill-van-der-merwe | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:170", "urc:186"], "weight_kg": ["national:76", "urc:78"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_edwin-edogbo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:188", "urc:189"], "weight_kg": ["national:135", "urc:123"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_efrain-elias | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "top14:192"], "weight_kg": ["national:131", "top14:122"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_elia-canakaivata | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "premiership:181", "super-rugby:190"], "weight_kg": ["national:108", "premiership:104", "super-rugby:117"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_elliot-millar-mills | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "premiership:179"], "weight_kg": ["national:112", "premiership:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_elliot-stooke | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:194", "top14:195", "urc:202"], "weight_kg": ["premiership:118", "top14:135", "urc:127"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_elliott-daly | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "premiership:173"], "weight_kg": ["national:106", "premiership:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ellis-genge | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:199", "premiership:184"], "weight_kg": ["national:116", "premiership:108"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ellis-mee | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:185", "urc:184"], "weight_kg": ["national:101", "urc:83"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_elrigh-louw | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:196", "urc:210"], "weight_kg": ["national:127", "urc:106"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_embrose-papier | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:159", "urc:181"], "weight_kg": ["national:75", "urc:73"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_emilien-gailleton | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:176", "top14:187"], "weight_kg": ["national:76", "top14:81"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_emmanuel-iyogun | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:203", "premiership:184"], "weight_kg": ["national:123", "premiership:124"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_emmanuel-meafou | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:203", "top14:215"], "weight_kg": ["national:140", "top14:130"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_enoch-opoku-gyamfi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:197", "premiership:204"], "weight_kg": ["national:131", "premiership:147"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ereatara-enari | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "super-rugby:171", "urc:164"], "weight_kg": ["national:95", "super-rugby:90", "urc:88"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_erich-storti | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:177", "national:188"], "weight_kg": ["mlr:78", "national:90"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_eroni-mawi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:185", "premiership:199"], "weight_kg": ["national:125", "premiership:123"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_etene-nanai-seturo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:189", "top14:197"], "weight_kg": ["super-rugby:90", "top14:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ethan-blackadder | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "super-rugby:199"], "weight_kg": ["national:118", "super-rugby:116"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ethan-de-groot | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:196", "super-rugby:202"], "weight_kg": ["national:115", "super-rugby:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ethan-hooker | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "urc:186"], "weight_kg": ["national:111", "urc:95"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ethan-mcveigh | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:168", "national:169"], "weight_kg": ["mlr:82", "national:93"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ethan-staddon | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:204", "top14:209"], "weight_kg": ["premiership:115", "top14:97"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_evan-roos | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:187", "urc:183"], "weight_kg": ["national:106", "urc:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ewan-ashman | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:196", "urc:186"], "weight_kg": ["national:111", "urc:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ewan-richards | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:193", "top14:188"], "weight_kg": ["premiership:122", "top14:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_fabien-brau-boirie | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:203", "top14:184"], "weight_kg": ["national:88", "top14:111"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_facundo-bosch | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:168", "top14:168", "urc:169"], "weight_kg": ["premiership:97", "top14:113", "urc:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_faka-osi-pifeleti | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:179", "national:180"], "weight_kg": ["mlr:120", "national:128"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_faletoi-peni | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "super-rugby:173"], "weight_kg": ["national:108", "super-rugby:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_federico-ruzza | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:204", "urc:205"], "weight_kg": ["national:122", "urc:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_fehi-fineanganofo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "super-rugby:194"], "weight_kg": ["national:115", "super-rugby:117"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_fergus-burke | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "premiership:189"], "weight_kg": ["national:95", "premiership:107"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_filipo-daugunu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:172", "super-rugby:196"], "weight_kg": ["national:99", "super-rugby:89"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_fin-baxter | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:175", "premiership:195"], "weight_kg": ["national:111", "premiership:125"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_fin-smith | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "premiership:167"], "weight_kg": ["national:103", "premiership:79"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_fine-inisi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "urc:182"], "weight_kg": ["national:112", "urc:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_finlay-bealham | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:112", "urc:121"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_finlay-christie | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:188", "super-rugby:183"], "weight_kg": ["national:70", "super-rugby:80"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_finn-russell | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "premiership:174"], "weight_kg": ["national:78", "premiership:89"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_fletcher-newell | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "super-rugby:191"], "weight_kg": ["national:115", "super-rugby:133"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_florian-verhaeghe | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:121", "top14:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_francisco-moreno | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:179", "premiership:174"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_franco-molina | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:206", "premiership:192", "super-rugby:210"], "weight_kg": ["national:121", "premiership:118", "super-rugby:128"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_francois-cros | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:195", "top14:192"], "weight_kg": ["national:113", "top14:97"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_frank-lomani | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "super-rugby:177"], "weight_kg": ["national:87", "super-rugby:91"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_fraser-dingwall | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "premiership:180"], "weight_kg": ["national:110", "premiership:101"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_fraser-mcreight | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "super-rugby:190"], "weight_kg": ["national:119", "super-rugby:123"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_freddie-steward | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:198", "premiership:194"], "weight_kg": ["national:104", "premiership:93"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_freddie-thomas | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "premiership:182"], "weight_kg": ["national:115", "premiership:104"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_freddy-douglas | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:189", "urc:173"], "weight_kg": ["national:83", "urc:80"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_gabriel-hamer-webb | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "premiership:190"], "weight_kg": ["national:100", "premiership:93"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_gael-drean | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:179", "top14:187"], "weight_kg": ["national:82", "top14:70"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_gael-fickou | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "top14:194"], "weight_kg": ["national:115", "top14:92"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_gareth-thomas-1993 | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:181", "urc:173"], "weight_kg": ["national:118", "urc:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_garry-ringrose | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:82", "urc:105"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_gary-porter | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:211", "urc:205"], "weight_kg": ["national:103", "urc:124"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_george-bell | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:180", "super-rugby:189"], "weight_kg": ["national:114", "super-rugby:101"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_george-bower | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:177", "super-rugby:196"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_george-ford | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:175", "premiership:167"], "weight_kg": ["national:86", "premiership:89"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_george-furbank | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:167", "premiership:188"], "weight_kg": ["national:106", "premiership:84"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_george-horne | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:181", "urc:169"], "weight_kg": ["national:89", "urc:90"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_george-kloska | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:188", "premiership:174"], "weight_kg": ["national:124", "premiership:107"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_george-martin | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:122", "premiership:134"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_george-timmins | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:186", "top14:198"], "weight_kg": ["premiership:108", "top14:93"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_george-turner | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:168", "premiership:183"], "weight_kg": ["national:112", "premiership:105"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_georges-henri-colombe | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:192", "top14:195"], "weight_kg": ["national:143", "top14:155"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_gerhard-steenekamp | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "urc:183"], "weight_kg": ["national:116", "urc:143"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_geronimo-prisciantelli | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:197", "top14:196"], "weight_kg": ["national:81", "top14:77"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_giacomo-da-re | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:166", "urc:190"], "weight_kg": ["national:99", "urc:83"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_giacomo-nicotera | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:169", "top14:184"], "weight_kg": ["national:105", "top14:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_gianmarco-lucchesi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:179", "top14:184"], "weight_kg": ["national:102", "top14:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_giorgi-akhaladze | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:187", "top14:182"], "weight_kg": ["national:116", "top14:139"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_giorgi-melikidze | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:189", "top14:190"], "weight_kg": ["national:104", "top14:121"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_giorgi-tetrashvili | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:176", "top14:184"], "weight_kg": ["national:121", "top14:125"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_giosue-zilocchi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:187", "urc:192"], "weight_kg": ["national:129", "urc:130"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_giulio-marini | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "urc:197"], "weight_kg": ["national:123", "urc:126"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_glen-young | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:207", "urc:205"], "weight_kg": ["national:122", "urc:126"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_gonzalo-bertranou | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:178", "national:187"], "weight_kg": ["mlr:90", "national:93"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_gonzalo-garcia-1999 | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:163", "top14:175"], "weight_kg": ["national:82", "top14:90"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_grant-gilchrist | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:188", "urc:196"], "weight_kg": ["national:121", "urc:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_greg-alldritt | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:177", "top14:179"], "weight_kg": ["national:108", "top14:125"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_gregor-brown | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "urc:210"], "weight_kg": ["national:116", "urc:107"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_gregor-hiddleston | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:196", "urc:189"], "weight_kg": ["national:107", "urc:133"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_guido-petti | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:207", "premiership:194", "top14:197"], "weight_kg": ["national:112", "premiership:101", "top14:118"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_guillaume-cramont | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:105", "top14:116"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_gus-mccarthy | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:178", "urc:175"], "weight_kg": ["national:111", "urc:94"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_guy-pepper | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "premiership:202"], "weight_kg": ["national:111", "premiership:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_haereiti-hetet | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:192", "super-rugby:187"], "weight_kg": ["national:128", "super-rugby:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_hame-faiva | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:189", "top14:167", "urc:185"], "weight_kg": ["premiership:100", "top14:101", "urc:93"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_hamish-stewart | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:194", "super-rugby:185"], "weight_kg": ["national:90", "super-rugby:88"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_hamish-watson | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:105", "top14:91"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_handre-pollard | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:188", "urc:186"], "weight_kg": ["national:90", "urc:86"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_harison-mataele | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:214", "national:190"], "weight_kg": ["mlr:115", "national:113"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_harri-deaves-small | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "urc:170"], "weight_kg": ["national:95", "urc:94"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_harri-morris | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:88", "urc:89"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_harrison-keddie | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "urc:180"], "weight_kg": ["national:103", "urc:108"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_harry-byrne | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:200", "urc:193"], "weight_kg": ["national:104", "urc:83"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_harry-johnson-holmes | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:189", "super-rugby:181"], "weight_kg": ["premiership:131", "super-rugby:112"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_harry-plummer | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:183", "top14:187"], "weight_kg": ["super-rugby:90", "top14:105"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_harry-potter | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:176", "super-rugby:186"], "weight_kg": ["national:98", "super-rugby:110"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_harry-wilson | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:195", "super-rugby:198"], "weight_kg": ["national:104", "super-rugby:107"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_harvey-cuckson | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:214", "top14:211", "urc:187"], "weight_kg": ["premiership:116", "top14:135", "urc:105"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_henry-arundell | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:194", "premiership:178"], "weight_kg": ["national:82", "premiership:97"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_henry-pollock | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:182", "premiership:195"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_henry-slade | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:196", "premiership:198"], "weight_kg": ["national:104", "premiership:105"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_herschel-jantjies | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:177", "top14:155"], "weight_kg": ["national:86", "top14:81"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_hoskins-sotutu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:202", "super-rugby:196"], "weight_kg": ["premiership:122", "super-rugby:127"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_hugo-auradou | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:204", "top14:197"], "weight_kg": ["national:119", "top14:108"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_hugo-gonzalez | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "top14:194"], "weight_kg": ["national:121", "top14:134"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_hugo-keenan | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:173", "urc:182"], "weight_kg": ["national:95", "urc:83"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_hunter-paisami | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "super-rugby:163"], "weight_kg": ["national:76", "super-rugby:92"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_huw-jones | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:176", "top14:188"], "weight_kg": ["national:107", "top14:95"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_iain-henderson | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:210", "urc:208"], "weight_kg": ["national:110", "urc:132"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ignacio-brex | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:198", "top14:180"], "weight_kg": ["national:87", "top14:88"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ignacio-mendy | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:177", "urc:187"], "weight_kg": ["national:82", "urc:76"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ignacio-peculo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:198", "national:191"], "weight_kg": ["mlr:134", "national:140"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ignacio-ruiz | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "top14:187"], "weight_kg": ["national:103", "top14:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_immanuel-feyi-waboso | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "premiership:196"], "weight_kg": ["national:105", "premiership:104"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_inia-tabuavou | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["super-rugby:193", "top14:197"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ioan-emanuel | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:186", "top14:188", "urc:185"], "weight_kg": ["premiership:133", "top14:109", "urc:108"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ioane-iashagashvili | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "top14:187"], "weight_kg": ["national:103", "top14:113"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ion-neculai | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "premiership:174"], "weight_kg": ["national:142", "premiership:150"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_irakli-aptsiauri | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:172", "top14:171"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_isaac-aedo-kailea | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:205", "super-rugby:207"], "weight_kg": ["national:131", "super-rugby:134"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_isaac-henry | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:187", "super-rugby:172"], "weight_kg": ["national:113", "super-rugby:108"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_isaia-walker-leawere | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:206", "urc:212"], "weight_kg": ["super-rugby:131", "urc:130"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_isaiah-ravula | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:177", "super-rugby:183"], "weight_kg": ["national:77", "super-rugby:93"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_isoa-nasilasila | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:194", "super-rugby:209"], "weight_kg": ["national:104", "super-rugby:102"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jac-morgan | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "premiership:170"], "weight_kg": ["national:95", "premiership:101"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jack--walker- | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "premiership:177"], "weight_kg": ["national:94", "premiership:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jack-bennett | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:186", "top14:194", "urc:207"], "weight_kg": ["premiership:101", "top14:108", "urc:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jack-conan | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:189", "urc:190"], "weight_kg": ["national:111", "urc:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jack-crowley | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:180", "urc:196"], "weight_kg": ["national:78", "urc:105"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jack-iscaro | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "top14:190"], "weight_kg": ["national:122", "top14:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jack-van-poortvliet | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "premiership:174"], "weight_kg": ["national:87", "premiership:97"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jack-willis | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:175", "top14:194"], "weight_kg": ["national:97", "top14:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jaco-coetzee | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:177", "top14:176"], "weight_kg": ["premiership:123", "top14:97"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jaco-williams | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:167", "urc:190"], "weight_kg": ["national:83", "urc:62"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jacob-stockdale | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:204", "urc:182"], "weight_kg": ["national:109", "urc:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jacob-umaga | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:176", "urc:191"], "weight_kg": ["national:98", "urc:95"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jacques-du-plessis | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:198", "top14:189", "urc:192"], "weight_kg": ["premiership:120", "top14:114", "urc:111"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jake-gordon | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "super-rugby:196"], "weight_kg": ["national:87", "super-rugby:83"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_james-botham | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "urc:203"], "weight_kg": ["national:105", "urc:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_james-ratti | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:209", "urc:193"], "weight_kg": ["national:110", "urc:133"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_james-ryan | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:207", "urc:198"], "weight_kg": ["national:115", "urc:104"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_james-slipper | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:188", "super-rugby:183"], "weight_kg": ["national:108", "super-rugby:119"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jamie-bhatti | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:176", "premiership:185"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jamie-dobie | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:85", "urc:92"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jamie-george | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:196", "premiership:197"], "weight_kg": ["national:122", "premiership:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jamie-hannah | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:201", "super-rugby:202"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jamie-osborne | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:187", "urc:185"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jamie-ritchie | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:198", "urc:179"], "weight_kg": ["national:116", "urc:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jamison-gibson-park | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:170", "urc:171"], "weight_kg": ["national:77", "urc:90"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jan-hendrik-wessels | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:106", "urc:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_janick-tarrit | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "top14:192"], "weight_kg": ["national:98", "top14:110"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jarrod-evans | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:185", "urc:163"], "weight_kg": ["national:100", "urc:89"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jason-damm | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:191", "national:185"], "weight_kg": ["mlr:117", "national:110"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jasper-spandler | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:185", "top14:190", "urc:164"], "weight_kg": ["premiership:107", "top14:110", "urc:119"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jean-baptiste-gros | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:171", "top14:175"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jean-cotarmanac-h | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:172", "top14:177"], "weight_kg": ["national:99", "top14:73"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jean-kleyn | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:201", "premiership:214"], "weight_kg": ["national:121", "premiership:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jefferson-poirot | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:168", "top14:182"], "weight_kg": ["national:125", "top14:127"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jeffery-toomaga-allen | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:118", "super-rugby:140"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jeremy-loughman | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:179", "urc:198"], "weight_kg": ["national:128", "urc:124"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jeremy-williams | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "super-rugby:207"], "weight_kg": ["national:107", "super-rugby:116"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jimi-maximin | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:216", "top14:193"], "weight_kg": ["national:141", "top14:144"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jimmy-o-brien | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:168", "urc:193"], "weight_kg": ["national:90", "urc:80"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jiuta-wainiqolo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:176", "top14:186"], "weight_kg": ["national:94", "top14:102"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jj-kotze | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:197", "urc:178"], "weight_kg": ["national:121", "urc:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_joaquin-moro | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:179", "premiership:178"], "weight_kg": ["national:88", "premiership:89"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_joaquin-oviedo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:199", "top14:190"], "weight_kg": ["national:102", "top14:119"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jock-campbell | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:181", "super-rugby:190"], "weight_kg": ["national:78", "super-rugby:106"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_joe-hawkins | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:198", "urc:179"], "weight_kg": ["national:98", "urc:102"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_joe-heyes | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "premiership:197"], "weight_kg": ["national:137", "premiership:134"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_joe-mccarthy | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:202", "urc:190"], "weight_kg": ["national:113", "urc:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_joe-roberts | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "urc:181"], "weight_kg": ["national:108", "urc:89"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_joe-taufete-e | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:173", "national:191"], "weight_kg": ["mlr:129", "national:117"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_joel-merkler | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:208", "top14:192"], "weight_kg": ["national:130", "top14:122"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_johan-grobbelaar | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:172", "urc:190"], "weight_kg": ["national:102", "urc:90"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_johan-momsen | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:180", "urc:189"], "weight_kg": ["mlr:119", "urc:107"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_johannes-jonker | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:174", "top14:198", "urc:188"], "weight_kg": ["premiership:121", "top14:129", "urc:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_john-stewart | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:198", "top14:201", "urc:187"], "weight_kg": ["premiership:97", "top14:112", "urc:95"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_joji-nasova- | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:176", "super-rugby:172"], "weight_kg": ["national:91", "super-rugby:96"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jon-zabala | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:195", "top14:192"], "weight_kg": ["national:120", "top14:117"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jonny-gray | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:189", "top14:194"], "weight_kg": ["national:134", "top14:133"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jonny-hill | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "top14:206"], "weight_kg": ["national:128", "top14:136"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jordie-barrett | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:185", "super-rugby:203"], "weight_kg": ["national:88", "super-rugby:91"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jose-madeira | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:110", "top14:116"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_joseph-dweba | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "premiership:175"], "weight_kg": ["national:104", "premiership:119"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_joseph-mano | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:175", "national:192"], "weight_kg": ["mlr:100", "national:92"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_joseph-sua-ali-i | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:188", "super-rugby:198"], "weight_kg": ["national:103", "super-rugby:87"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_josh--adams- | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:199", "urc:189"], "weight_kg": ["national:91", "urc:98"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_josh-bayliss | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:179", "premiership:193"], "weight_kg": ["national:93", "premiership:116"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_josh-canham | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:204", "super-rugby:202"], "weight_kg": ["national:105", "super-rugby:121"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_josh-flook | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:187", "urc:177"], "weight_kg": ["super-rugby:93", "urc:102"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_josh-lord | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:206", "super-rugby:193"], "weight_kg": ["national:119", "super-rugby:117"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_josh-macleod | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:197", "urc:203"], "weight_kg": ["national:104", "urc:125"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_josh-mcnally | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:214", "top14:212", "urc:204"], "weight_kg": ["premiership:120", "top14:125", "urc:131"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_josh-nasser | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:175", "super-rugby:200"], "weight_kg": ["national:111", "super-rugby:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_josh-van-der-flier | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:198", "urc:178"], "weight_kg": ["national:116", "urc:104"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_joshua-brennan | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:202", "top14:201"], "weight_kg": ["national:103", "top14:108"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_joshua-moorby | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "super-rugby:200"], "weight_kg": ["national:87", "super-rugby:89"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_josua-tuisova | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:195", "top14:192"], "weight_kg": ["national:119", "top14:111"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_juan-cruz-mallia | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:195", "top14:177"], "weight_kg": ["national:98", "top14:78"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_juan-martin-gonzalez-samso | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:202", "premiership:195"], "weight_kg": ["national:94", "premiership:119"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_juan-martin-scelzo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "top14:195"], "weight_kg": ["national:118", "top14:104"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_juan-schoeman | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:199", "top14:190", "urc:198"], "weight_kg": ["premiership:114", "top14:122", "urc:112"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_jules-martin-bonnard | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:212", "top14:188"], "weight_kg": ["premiership:90", "top14:92"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_julian-montoya | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "top14:192"], "weight_kg": ["national:125", "top14:111"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_julian-roberts | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:160", "national:166"], "weight_kg": ["mlr:79", "national:96"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_julien-marchand | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:170", "top14:176"], "weight_kg": ["national:100", "top14:104"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_justo-piccardo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "top14:197"], "weight_kg": ["national:126", "top14:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_kalani-thomas | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "super-rugby:182"], "weight_kg": ["national:94", "super-rugby:82"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_kalaveti-ravouvou | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "premiership:197"], "weight_kg": ["national:100", "premiership:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_kaleb-geiger | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:176", "national:173"], "weight_kg": ["mlr:108", "national:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_kalvin-gourgues | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "top14:198"], "weight_kg": ["national:98", "top14:110"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_kane-james | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:180", "premiership:188"], "weight_kg": ["national:114", "premiership:102"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_kapeli-pifeleti-jr | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "premiership:173"], "weight_kg": ["national:124", "premiership:104"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_kavaia-tagivetaua | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:188", "super-rugby:180"], "weight_kg": ["national:118", "super-rugby:121"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_khutha-mchunu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "urc:169"], "weight_kg": ["national:110", "urc:125"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_kienan-higgins | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:182", "urc:189"], "weight_kg": ["mlr:87", "urc:112"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_kieran-hardy | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:189", "urc:174"], "weight_kg": ["national:102", "urc:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_kieran-verden | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:191", "top14:187", "urc:178"], "weight_kg": ["premiership:108", "top14:119", "urc:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_kieron-assiratti | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:184", "urc:193"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_killian-tixeront | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:204", "top14:191"], "weight_kg": ["national:104", "top14:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_kitione-salawa-jr | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "super-rugby:184"], "weight_kg": ["national:81", "super-rugby:89"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_konstantine-mikautadze | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:204", "top14:207"], "weight_kg": ["national:134", "top14:131"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_kyle-preston | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:166", "super-rugby:176"], "weight_kg": ["national:77", "super-rugby:88"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_kyle-rowe | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "urc:181"], "weight_kg": ["national:86", "urc:79"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_kyle-sinckler | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:178", "top14:197"], "weight_kg": ["national:122", "top14:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_kyle-steeves | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:170", "national:187"], "weight_kg": ["mlr:115", "national:118"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_kyle-steyn | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "urc:173"], "weight_kg": ["national:99", "urc:96"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_lachlan-shaw | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:192", "super-rugby:215"], "weight_kg": ["national:109", "super-rugby:122"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_lalakai-foketi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:173", "urc:184"], "weight_kg": ["super-rugby:113", "urc:97"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_lalomilo-lalomilo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "super-rugby:168"], "weight_kg": ["national:110", "super-rugby:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_lance-williams | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:176", "national:181"], "weight_kg": ["mlr:96", "national:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_lawson-creighton | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:193", "urc:175"], "weight_kg": ["super-rugby:93", "urc:84"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_leicester-fainga-anuku | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:185", "super-rugby:175"], "weight_kg": ["national:112", "super-rugby:95"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_lekima-tagitagivalu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:196", "top14:209"], "weight_kg": ["national:98", "top14:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_lenni-nouchi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:180", "top14:191"], "weight_kg": ["national:121", "top14:107"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_leo-barre | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "top14:183"], "weight_kg": ["national:96", "top14:86"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_leonardo-marin | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:181", "urc:180"], "weight_kg": ["national:91", "urc:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_leonel-oviedo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "super-rugby:173"], "weight_kg": ["national:111", "super-rugby:126"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_leroy-carter | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:179", "super-rugby:190"], "weight_kg": ["national:78", "super-rugby:79"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_levani-botia | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:169", "top14:186"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_lewis-ludlam | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "top14:203"], "weight_kg": ["national:123", "top14:96"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_liam-belcher | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:164", "urc:190"], "weight_kg": ["national:100", "urc:105"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_liam-mcconnell | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "urc:187"], "weight_kg": ["national:121", "urc:108"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_lorenzo-cannone | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:177", "urc:189"], "weight_kg": ["national:110", "urc:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_lorenzo-pani | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:188", "urc:179"], "weight_kg": ["national:99", "urc:86"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_louie-chapman | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["super-rugby:90", "urc:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_louie-hennessey | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:203", "premiership:199"], "weight_kg": ["national:116", "premiership:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_louis-bielle-biarrey | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "top14:199"], "weight_kg": ["national:91", "top14:89"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_louis-lynagh | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "urc:200"], "weight_kg": ["national:88", "urc:97"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_louis-ortolan | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:171", "top14:182", "urc:182"], "weight_kg": ["premiership:117", "top14:106", "urc:100"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_louis-rees-zammit | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:194", "premiership:186"], "weight_kg": ["national:95", "premiership:105"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_louis-werchon | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:190", "urc:168"], "weight_kg": ["super-rugby:82", "urc:70"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_luca-tabarot | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:178", "top14:201"], "weight_kg": ["national:116", "top14:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_lucas-official | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:193", "top14:198", "urc:184"], "weight_kg": ["premiership:101", "top14:95", "urc:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_lucas-rumball | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:206", "national:202"], "weight_kg": ["mlr:117", "national:116"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_lucas-velarte | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:197", "top14:174"], "weight_kg": ["national:114", "top14:110"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_lucio-luna | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "premiership:189"], "weight_kg": ["national:99", "premiership:111"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_luka-ivanishvili | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "premiership:173"], "weight_kg": ["national:106", "premiership:96"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_luka-japaridze | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "top14:173"], "weight_kg": ["national:138", "top14:121"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_luke-carty | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:181", "national:194"], "weight_kg": ["mlr:81", "national:91"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_luke-cowan-dickie | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:171", "premiership:196"], "weight_kg": ["national:110", "premiership:100"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_luke-jacobson | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:181", "super-rugby:192"], "weight_kg": ["national:117", "super-rugby:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_luke-tagi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:189", "top14:192", "urc:175"], "weight_kg": ["premiership:127", "top14:130", "urc:121"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_lukhan-lealaiaulolo-tui | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:188", "super-rugby:204"], "weight_kg": ["national:134", "super-rugby:132"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ma-ake-muti | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:176", "national:190"], "weight_kg": ["mlr:116", "national:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mackenzie-hansen | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:176", "urc:197"], "weight_kg": ["national:85", "urc:102"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_magnus-bradbury | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:181", "urc:188"], "weight_kg": ["national:118", "urc:111"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_makeen-alikhan | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:180", "national:191"], "weight_kg": ["mlr:91", "national:95"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mako-vunipola | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:168", "premiership:165"], "weight_kg": ["national:137", "premiership:132"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_malik-faissal | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:197", "premiership:193"], "weight_kg": ["national:103", "premiership:93"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_maliu-niuafe | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:206", "national:204"], "weight_kg": ["mlr:116", "national:126"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mamoru-harada | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:173", "super-rugby:185"], "weight_kg": ["national:92", "super-rugby:86"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_manasa-mataele | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:170", "super-rugby:196"], "weight_kg": ["national:89", "super-rugby:105"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_manuel-leindekar | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:219", "top14:191"], "weight_kg": ["national:124", "top14:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_manuel-zuliani | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:189", "urc:178"], "weight_kg": ["national:97", "urc:112"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_marco-fepulea-i | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "premiership:180"], "weight_kg": ["national:115", "premiership:133"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_marco-riccioni | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "top14:187"], "weight_kg": ["national:118", "top14:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_marco-van-staden | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:178", "urc:176"], "weight_kg": ["national:123", "urc:125"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_marcos-kremer | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:209", "top14:191"], "weight_kg": ["national:102", "top14:123"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_marcus-smith | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:189", "premiership:172"], "weight_kg": ["national:80", "premiership:77"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mark-o-keeffe | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["mlr:187", "national:196"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_marko-gazzotti | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:206", "top14:183"], "weight_kg": ["national:98", "top14:101"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_marno-redelinghuys | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:192", "national:195"], "weight_kg": ["mlr:114", "national:121"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_maro-itoje | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:197", "premiership:198"], "weight_kg": ["national:123", "premiership:122"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_marshall-sykes | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:214", "urc:210"], "weight_kg": ["national:120", "urc:121"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_martin-page-relo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:179", "top14:162"], "weight_kg": ["national:72", "top14:85"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_martin-villar | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:176", "top14:194", "urc:189"], "weight_kg": ["premiership:115", "top14:125", "urc:113"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mason-flesch | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:182", "national:184"], "weight_kg": ["mlr:113", "national:102"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mason-grady | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:132", "urc:122"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mason-pedersen | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:185", "national:187"], "weight_kg": ["mlr:118", "national:108"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_massimo-de-lutiis | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "super-rugby:176"], "weight_kg": ["national:122", "super-rugby:138"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mateo-carreras | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:187", "top14:173"], "weight_kg": ["national:95", "top14:76"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mateo-guerin | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:197", "top14:199", "urc:188"], "weight_kg": ["premiership:134", "urc:134", "top14:145"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mathieu-smaili | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:192", "top14:179"], "weight_kg": ["national:103", "top14:102"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mathieu-tanguy | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:209", "top14:182"], "weight_kg": ["national:124", "top14:104"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_matias-alemanno | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:185", "top14:187"], "weight_kg": ["national:114", "top14:128"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_matias-moroni | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:89", "premiership:80"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_matis-perchaud | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:190", "top14:190", "urc:188"], "weight_kg": ["premiership:117", "top14:129", "urc:123"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_matt-faessler | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "super-rugby:185"], "weight_kg": ["national:105", "super-rugby:124"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_matt-fagerson | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:177", "urc:189"], "weight_kg": ["national:124", "urc:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_matt-oworu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:198", "national:201"], "weight_kg": ["mlr:117", "national:121"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_matteo-le-corvec | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "top14:193"], "weight_kg": ["national:103", "top14:123"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_matthieu-jalibert | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:172", "top14:169"], "weight_kg": ["national:75", "top14:87"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_max-bru | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:173", "top14:185", "urc:184"], "weight_kg": ["premiership:101", "top14:100", "urc:106"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_max-jorgensen | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:171", "super-rugby:187"], "weight_kg": ["national:84", "super-rugby:86"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_max-llewellyn | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:198", "premiership:190"], "weight_kg": ["national:97", "premiership:101"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_max-ojomoh | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:188", "premiership:170"], "weight_kg": ["national:113", "premiership:91"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_max-pearce | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:194", "top14:181", "urc:195"], "weight_kg": ["premiership:125", "top14:111", "urc:107"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_max-spring | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:164", "top14:165"], "weight_kg": ["national:65", "top14:75"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_max-williamson | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:207", "urc:210"], "weight_kg": ["national:121", "urc:116"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_maxime-lamothe | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:177", "top14:198"], "weight_kg": ["national:117", "top14:102"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_maxime-lucu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:187", "top14:192"], "weight_kg": ["national:70", "top14:84"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_maxime-machenaud | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:178", "top14:182"], "weight_kg": ["national:89", "top14:100"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_meli-tuni | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:197", "super-rugby:198"], "weight_kg": ["national:102", "super-rugby:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mesake-doge | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "super-rugby:178"], "weight_kg": ["national:107", "super-rugby:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mesake-vocevoce | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:196", "super-rugby:195"], "weight_kg": ["national:118", "super-rugby:116"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_michael-alaalatoa | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "urc:193"], "weight_kg": ["national:131", "urc:125"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_michael-baska | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:196", "national:189"], "weight_kg": ["mlr:89", "national:92"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_michael-milne | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:170", "urc:192"], "weight_kg": ["national:114", "urc:126"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_michele-lamaro | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "urc:182"], "weight_kg": ["national:93", "urc:117"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mickael--guillard | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:209", "top14:206"], "weight_kg": ["national:117", "top14:112"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mikehil-alania | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "top14:165"], "weight_kg": ["national:96", "top14:74"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mikey-summerfield | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:167", "top14:184", "urc:191"], "weight_kg": ["premiership:114", "top14:127", "urc:121"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mikheili-shioshvili | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:181", "top14:191"], "weight_kg": ["national:110", "top14:104"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_miles-amatosero | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:189", "super-rugby:193"], "weight_kg": ["national:114", "super-rugby:121"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mills-sanerivi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "super-rugby:180", "top14:174"], "weight_kg": ["national:125", "super-rugby:117", "top14:101"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_miracle-fai-ilagi | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:103", "super-rugby:90"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mirco-spagnolo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "urc:179"], "weight_kg": ["national:112", "urc:117"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mirko-belloni | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:199", "urc:192"], "weight_kg": ["national:86", "urc:105"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_mitch-wilson | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:179", "national:165"], "weight_kg": ["mlr:93", "national:74"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_monty-ioane | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "top14:188"], "weight_kg": ["national:103", "top14:80"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_morgan-morse | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:176", "urc:195"], "weight_kg": ["national:106", "urc:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_morne-van-den-berg | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "urc:168"], "weight_kg": ["national:88", "urc:97"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_moses-alo-emile | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:189", "top14:190"], "weight_kg": ["national:145", "top14:123"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_muhamed-hasa | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "urc:180"], "weight_kg": ["national:131", "urc:112"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_murphy-walker | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:198", "urc:203"], "weight_kg": ["national:111", "urc:107"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_nathan-den-hoedt | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:197", "national:194"], "weight_kg": ["mlr:110", "national:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_nathan-doak | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:173", "urc:200"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_nathan-mcbeth | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:108", "urc:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_nial-annett | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:178", "top14:181", "urc:171"], "weight_kg": ["premiership:111", "top14:115", "urc:132"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_niccolo-cannone | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:204", "urc:196"], "weight_kg": ["national:119", "urc:113"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_nick--tompkins | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:196", "premiership:169"], "weight_kg": ["national:95", "premiership:89"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_nick-champion-de-crespigny | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:201", "super-rugby:200"], "weight_kg": ["national:104", "super-rugby:125"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_nick-frost | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "super-rugby:209"], "weight_kg": ["national:112", "super-rugby:111"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_nick-isiekwe | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:213", "premiership:209"], "weight_kg": ["national:115", "premiership:106"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_nick-timoney | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:199", "urc:181"], "weight_kg": ["national:101", "urc:105"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_nicky-smith | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:170", "premiership:178"], "weight_kg": ["national:127", "premiership:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_nicolas-depoortere | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:179", "top14:186"], "weight_kg": ["national:98", "top14:84"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_nicolas-martins | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "top14:184"], "weight_kg": ["national:101", "top14:90"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_nika-abuladze | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:195", "premiership:172"], "weight_kg": ["national:122", "premiership:119"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_nika-sutidze | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "top14:179"], "weight_kg": ["national:105", "top14:106"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_niko-jones | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:201", "super-rugby:196"], "weight_kg": ["national:105", "super-rugby:104"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_noah-brown | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:184", "national:183"], "weight_kg": ["mlr:84", "national:90"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_noah-caluori | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:198", "premiership:183"], "weight_kg": ["national:106", "premiership:88"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_noah-nene | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:198", "top14:201"], "weight_kg": ["national:121", "top14:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_nolann-le-garrec | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:188", "top14:182"], "weight_kg": ["national:84", "top14:86"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ntuthuko-mchunu | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:120", "urc:127"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ollie-chessum | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "premiership:212"], "weight_kg": ["national:133", "premiership:121"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ollie-lawrence | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:169", "premiership:168"], "weight_kg": ["national:97", "premiership:104"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ollie-smith | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:178", "urc:184"], "weight_kg": ["national:113", "urc:84"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_olly-cracknell | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:203", "premiership:189"], "weight_kg": ["national:106", "premiership:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_oriol-marsinyac | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:198", "top14:174"], "weight_kg": ["national:91", "top14:86"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_oscar-jegou | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:179", "top14:197"], "weight_kg": ["national:95", "top14:82"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_oscar-lennon | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:168", "premiership:166"], "weight_kg": ["mlr:78", "premiership:77"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ox-nche | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "urc:186"], "weight_kg": ["national:120", "urc:116"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_paddy-mccarthy | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:173", "urc:169"], "weight_kg": ["national:109", "urc:111"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_paddy-ryan-1998 | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:184", "national:175"], "weight_kg": ["mlr:101", "national:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_paolo-garbisi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:198", "top14:199"], "weight_kg": ["national:96", "top14:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_pascal-cotet | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:183", "top14:178", "urc:175"], "weight_kg": ["premiership:127", "top14:133", "urc:123"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_pasilio-tosi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:202", "super-rugby:189"], "weight_kg": ["national:132", "super-rugby:147"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_patrick-harrison | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "urc:170"], "weight_kg": ["national:123", "urc:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_patrick-pellegrini | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:162", "super-rugby:170"], "weight_kg": ["national:67", "super-rugby:89"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_patrick-tuipulotu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:210", "super-rugby:187"], "weight_kg": ["national:109", "super-rugby:130"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_paul-boudehent | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:205", "top14:196"], "weight_kg": ["national:93", "top14:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_paul-de-villiers | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "urc:187"], "weight_kg": ["national:107", "urc:100"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_paul-graou | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:173", "top14:175"], "weight_kg": ["national:88", "top14:79"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_paulo-odogwu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:175", "urc:171"], "weight_kg": ["national:93", "urc:100"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_payton-telea-ilalio | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:181", "national:177"], "weight_kg": ["mlr:118", "national:126"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_peato-mauvaka | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:97", "top14:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_peceli-yato | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "top14:191"], "weight_kg": ["national:110", "top14:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_pedro-delgado | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:197", "premiership:172"], "weight_kg": ["national:144", "premiership:140"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_pedro-rubiolo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:205", "premiership:201"], "weight_kg": ["national:123", "premiership:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_penaia-cakobau | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:194", "super-rugby:166"], "weight_kg": ["national:111", "super-rugby:97"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_peni-ravai | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:200", "super-rugby:199"], "weight_kg": ["national:106", "super-rugby:113"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_pete-samu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "super-rugby:193"], "weight_kg": ["national:105", "super-rugby:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_peter-lakai | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:181", "super-rugby:199"], "weight_kg": ["national:95", "super-rugby:100"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_pierre-bochaton | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:188", "top14:208"], "weight_kg": ["national:117", "top14:118"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_pierre-castillon | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:184", "top14:186", "urc:195"], "weight_kg": ["premiership:99", "top14:94", "urc:107"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_pierre-louis-barassi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "top14:177"], "weight_kg": ["national:95", "top14:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_pierre-popelin | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:169", "top14:196"], "weight_kg": ["national:76", "top14:101"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_pierre-schoeman | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:169", "urc:170"], "weight_kg": ["national:112", "urc:122"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_piers-von-dadelszen | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["mlr:126", "national:104"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_pieter-scholtz | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:194", "top14:174", "urc:195"], "weight_kg": ["premiership:153", "top14:134", "urc:143"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_pita-gus-sowakula | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "top14:188"], "weight_kg": ["national:113", "top14:118"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ponipate-loganimasi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:193", "super-rugby:188"], "weight_kg": ["premiership:79", "super-rugby:98"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_pouri-rakete-stones | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:188", "super-rugby:187"], "weight_kg": ["premiership:116", "super-rugby:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_quan-horn | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:69", "urc:93"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_quentin-bethune | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:178", "top14:180", "urc:190"], "weight_kg": ["premiership:128", "top14:122", "urc:104"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_quinn-roux | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:192", "top14:183", "urc:211"], "weight_kg": ["premiership:133", "top14:118", "urc:110"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_quinn-tupaea | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:107", "super-rugby:88"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_rafael-cayuela | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:175", "top14:159", "urc:182"], "weight_kg": ["premiership:103", "top14:96", "urc:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_reda-wardi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "top14:170"], "weight_kg": ["national:96", "top14:113"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_regis-montagne | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:194", "top14:181"], "weight_kg": ["national:144", "top14:118"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_reuben-morgan-williams | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:189", "urc:183"], "weight_kg": ["national:87", "urc:100"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_rg-snyman | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:216", "urc:215"], "weight_kg": ["national:136", "urc:130"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_rhys-barratt | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:188", "urc:173"], "weight_kg": ["national:113", "urc:102"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_rhys-carre | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "premiership:180", "urc:194"], "weight_kg": ["national:131", "premiership:130", "urc:123"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_rhys-davies | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:205", "urc:212"], "weight_kg": ["national:114", "urc:118"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_riccardo-favretto | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:214", "urc:193"], "weight_kg": ["national:123", "urc:100"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ricky-riccitelli | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:197", "top14:172"], "weight_kg": ["super-rugby:109", "top14:108"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_riley-higgins | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:200", "urc:188"], "weight_kg": ["super-rugby:105", "urc:93"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_riley-norton | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "urc:209"], "weight_kg": ["national:105", "urc:116"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_rio-dyer | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "urc:187"], "weight_kg": ["national:87", "urc:85"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_rob-valetini | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:195", "super-rugby:198"], "weight_kg": ["national:111", "super-rugby:102"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_robbie-henshaw | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:205", "urc:200"], "weight_kg": ["national:90", "urc:112"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_robert-baloucoune | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:206", "urc:179"], "weight_kg": ["national:96", "urc:94"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_rodrigo-isgro-alastra | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "premiership:175"], "weight_kg": ["national:106", "premiership:118"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_rodrigo-marta | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:192", "top14:179"], "weight_kg": ["national:87", "top14:97"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_rodrigo-martinez | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "urc:200"], "weight_kg": ["national:126", "urc:111"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_rodrigue-neti | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "top14:190"], "weight_kg": ["national:133", "top14:130"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_romain-ntamack | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:195", "top14:172"], "weight_kg": ["national:79", "top14:98"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_romain-taofifenua | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:213", "top14:206"], "weight_kg": ["national:136", "top14:134"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ronan-kelleher | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:185", "urc:181"], "weight_kg": ["national:114", "urc:117"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_rory-cameron | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:199", "top14:190", "urc:186"], "weight_kg": ["premiership:117", "top14:122", "urc:106"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_rory-darge | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:171", "urc:186"], "weight_kg": ["national:104", "urc:95"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_rory-hutchinson | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:172", "premiership:176"], "weight_kg": ["national:81", "premiership:84"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_rory-sutherland | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:195", "urc:176"], "weight_kg": ["national:123", "urc:110"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ross-thompson | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "urc:191"], "weight_kg": ["national:93", "urc:80"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ross-vintcent | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:178", "premiership:184"], "weight_kg": ["national:109", "premiership:90"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ruan-nortje | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:213", "urc:200"], "weight_kg": ["national:117", "urc:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ruben-de-haas | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:187", "national:173"], "weight_kg": ["mlr:76", "national:90"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ruben-love | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "super-rugby:175"], "weight_kg": ["national:101", "super-rugby:77"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ruben-van-heerden | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:189", "top14:215"], "weight_kg": ["national:125", "top14:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_rufus-mclean | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:167", "national:179", "top14:192"], "weight_kg": ["mlr:104", "national:79", "top14:92"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ryan-baird | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:209", "urc:184"], "weight_kg": ["national:122", "urc:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ryan-elias | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "urc:192"], "weight_kg": ["national:124", "urc:121"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ryan-lonergan | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:195", "super-rugby:171"], "weight_kg": ["national:69", "super-rugby:87"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_ryan-woodman | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:204", "urc:207"], "weight_kg": ["national:119", "urc:105"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sacha-mngomezulu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:201", "urc:203"], "weight_kg": ["national:92", "urc:88"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sacha-zegueur | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:193", "top14:182"], "weight_kg": ["national:115", "top14:122"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_salesi-rayasi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:197", "top14:182"], "weight_kg": ["national:104", "top14:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_salmaan-moerat | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:192", "top14:215"], "weight_kg": ["national:135", "top14:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sam-costelow | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "urc:160"], "weight_kg": ["national:75", "urc:87"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sam-crean | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:183", "urc:189"], "weight_kg": ["premiership:120", "urc:119"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sam-darry | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:200", "super-rugby:192"], "weight_kg": ["national:117", "super-rugby:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sam-golla | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["mlr:204", "national:206"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sam-illo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "urc:183"], "weight_kg": ["national:133", "urc:121"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sam-moli | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:173", "premiership:194", "super-rugby:195"], "weight_kg": ["national:110", "premiership:122", "super-rugby:113"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sam-prendergast | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "urc:204"], "weight_kg": ["national:77", "urc:87"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sam-underhill | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:187", "premiership:206"], "weight_kg": ["national:102", "premiership:122"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sama-malolo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:179", "top14:178"], "weight_kg": ["national:119", "top14:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_samisoni-taukei-aho | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:195", "super-rugby:174"], "weight_kg": ["national:111", "super-rugby:118"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_samu-tawake | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:196", "super-rugby:185"], "weight_kg": ["national:112", "super-rugby:111"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_samuel-ezeala | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "top14:200"], "weight_kg": ["national:109", "top14:102"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_santiago-carreras | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "premiership:179"], "weight_kg": ["national:95", "premiership:96"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_santiago-chocobares | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:200", "top14:175"], "weight_kg": ["national:97", "top14:87"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_santiago-grondona | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "top14:213"], "weight_kg": ["national:101", "top14:118"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_santiago-videla | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:180", "national:175"], "weight_kg": ["mlr:85", "national:93"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_scott-barrett | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:201", "super-rugby:210"], "weight_kg": ["national:127", "super-rugby:106"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_scott-cummings | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:206", "urc:186"], "weight_kg": ["national:122", "urc:130"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_scott-kirk | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:176", "top14:175", "urc:187"], "weight_kg": ["premiership:102", "top14:120", "urc:101"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_scott-sio | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:179", "urc:181"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sean-jansen | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:177", "urc:206"], "weight_kg": ["national:109", "urc:125"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sean-mcnulty | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:200", "national:185"], "weight_kg": ["mlr:107", "national:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_seb-atkinson | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "premiership:201"], "weight_kg": ["national:92", "premiership:113"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_seb-stephen | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:179", "urc:194"], "weight_kg": ["national:98", "urc:127"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_selestino-ravutaumada | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:173", "top14:188"], "weight_kg": ["national:92", "top14:84"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_semisi-paea | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:187", "super-rugby:187", "urc:201"], "weight_kg": ["national:124", "super-rugby:101", "urc:128"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_seru-uru | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:193", "top14:211"], "weight_kg": ["super-rugby:118", "top14:128"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_setareki-turagacoke | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:209", "top14:188"], "weight_kg": ["national:127", "top14:128"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_setariki-tuicuvu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "top14:189"], "weight_kg": ["national:102", "top14:90"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sevu-reece | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "super-rugby:190", "top14:193"], "weight_kg": ["national:84", "super-rugby:93", "top14:87"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_simione-kuruvoli | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:170", "super-rugby:165", "top14:186"], "weight_kg": ["national:73", "super-rugby:77", "top14:68"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_simon-benitez-cruz | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:167", "premiership:190"], "weight_kg": ["national:63", "premiership:65"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_simon-parker | 同一 id がリーグ間で値不一致: weight_kg / {"values": {"weight_kg": ["national:131", "super-rugby:126"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_simone-ferrari | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "urc:178"], "weight_kg": ["national:119", "urc:112"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_simphiwe-moyo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:169", "urc:175"], "weight_kg": ["national:106", "urc:81"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sione-ahio | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:177", "top14:187"], "weight_kg": ["super-rugby:112", "top14:117"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sione-tuipulotu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:189", "urc:187"], "weight_kg": ["national:116", "urc:115"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sipili-falatea | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:197", "top14:183"], "weight_kg": ["national:115", "top14:123"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_sireli-maqala | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:182", "top14:184"], "weight_kg": ["national:77", "top14:94"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_siua-maile | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:178", "urc:172"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_siya-kolisi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:178", "urc:193"], "weight_kg": ["national:107", "urc:119"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_solomone-kata | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:162", "premiership:191"], "weight_kg": ["national:106", "premiership:112"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_stafford-mcdowall | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:202", "urc:200"], "weight_kg": ["national:92", "urc:113"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_stephen-varney | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "premiership:166"], "weight_kg": ["national:83", "premiership:85"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_stuart-mccloskey | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:187", "urc:186"], "weight_kg": ["national:129", "urc:117"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_swan-cormenier | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:186", "top14:192", "urc:173"], "weight_kg": ["premiership:117", "top14:134", "urc:124"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tadhg-beirne | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "urc:188"], "weight_kg": ["national:108", "urc:128"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tadhg-furlong | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:172", "urc:177"], "weight_kg": ["national:108", "urc:114"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_taine-plumtree | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:196", "super-rugby:184", "urc:206"], "weight_kg": ["national:105", "super-rugby:116", "urc:108"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tamaiti-williams | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:203", "super-rugby:202"], "weight_kg": ["national:148", "super-rugby:133"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tane-edmed | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:197", "super-rugby:175"], "weight_kg": ["national:101", "super-rugby:102"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_taniela-tupou | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "top14:169"], "weight_kg": ["national:161", "top14:142"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tate-mcdermott | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:164", "super-rugby:190"], "weight_kg": ["national:87", "super-rugby:85"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tavite-lopeti | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:171", "national:186"], "weight_kg": ["mlr:88", "national:96"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_taylor-gontineac | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "top14:186"], "weight_kg": ["national:90", "top14:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_teddy-williams | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "urc:203"], "weight_kg": ["national:111", "urc:126"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_temo-matiu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "top14:200"], "weight_kg": ["national:98", "top14:101"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_temo-mayanavanua | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:198", "super-rugby:187"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_terrell-peita | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:174", "urc:176"], "weight_kg": ["super-rugby:98", "urc:105"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tevita-naqali | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:199", "national:193"], "weight_kg": ["mlr:112", "national:111"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tevita-ratuva | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:205", "top14:188"], "weight_kg": ["national:112", "top14:122"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tevita-tatafu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:175", "urc:175", "premiership:200", "top14:174"], "weight_kg": ["national:131", "premiership:130", "top14:135", "urc:125"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_theo-attissogbe | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:167", "top14:189"], "weight_kg": ["national:83", "top14:95"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_theo-mcfarland | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:210", "top14:192"], "weight_kg": ["national:127", "top14:117"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_theodore-dan | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:176", "premiership:187"], "weight_kg": ["national:98", "premiership:122"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_thibaud-flament | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:203", "top14:214"], "weight_kg": ["national:102", "top14:119"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_thomas-acquier | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:175", "top14:176", "urc:196"], "weight_kg": ["premiership:110", "top14:125", "urc:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_thomas-du-toit | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:184", "premiership:202", "top14:181", "urc:198"], "weight_kg": ["national:137", "premiership:127", "top14:125", "urc:144"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_thomas-gallo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:173", "top14:178"], "weight_kg": ["national:115", "top14:92"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_thomas-laclayat | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:191", "top14:177"], "weight_kg": ["national:138", "top14:132"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_thomas-ramos | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:169", "top14:187"], "weight_kg": ["national:100", "top14:87"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_thomas-staniforth | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:210", "top14:202"], "weight_kg": ["national:139", "top14:135"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tietie-tuimauga | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:177", "premiership:203"], "weight_kg": ["national:120", "premiership:143"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tim-hoyt | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:204", "top14:195"], "weight_kg": ["national:118", "top14:111"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tinotenda-blithe-mavesere | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:185", "urc:189"], "weight_kg": ["national:103", "urc:94"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_titi-lamositele | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:196", "premiership:192"], "weight_kg": ["national:142", "premiership:129"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tom-allen | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:193", "urc:209"], "weight_kg": ["super-rugby:101", "urc:128"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tom-clarkson | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:198", "urc:187"], "weight_kg": ["national:125", "urc:130"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tom-curry | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "premiership:198"], "weight_kg": ["national:113", "premiership:103"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tom-dunn | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:172", "top14:197", "urc:200"], "weight_kg": ["premiership:106", "top14:118", "urc:118"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tom-farrell | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:202", "urc:191"], "weight_kg": ["national:104", "urc:117"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tom-francis | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:192", "premiership:199"], "weight_kg": ["national:121", "premiership:131"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tom-hooper | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:189", "premiership:210"], "weight_kg": ["national:111", "premiership:137"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tom-jordan | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:202", "premiership:183"], "weight_kg": ["national:97", "premiership:94"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tom-o-toole | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:199", "urc:186"], "weight_kg": ["national:127", "urc:136"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tom-robertson | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:167", "super-rugby:182"], "weight_kg": ["national:121", "super-rugby:107"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tom-roebuck | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:177", "premiership:185"], "weight_kg": ["national:109", "premiership:97"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tom-rogers | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:200", "urc:187"], "weight_kg": ["national:90", "urc:76"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tom-stewart | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:179", "urc:181"], "weight_kg": ["national:103", "urc:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tom-wright | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:185", "super-rugby:191"], "weight_kg": ["national:97", "super-rugby:87"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tomas-albornoz | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:187", "top14:186"], "weight_kg": ["national:79", "top14:85"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tomas-lavanini | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:194", "super-rugby:198"], "weight_kg": ["national:112", "super-rugby:124"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tomas-rapetti | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:188", "top14:175"], "weight_kg": ["national:126", "top14:116"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tommaso-di-bartolomeo | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:180", "urc:166"], "weight_kg": ["national:104", "urc:112"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tommaso-menoncello | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:195", "top14:185"], "weight_kg": ["national:101", "top14:100"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tommy-allan | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:179", "urc:178"], "weight_kg": ["national:98", "urc:96"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tommy-freeman | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:190", "premiership:182"], "weight_kg": ["national:88", "premiership:100"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tommy-o-brien | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:192", "urc:171"], "weight_kg": ["national:100", "urc:102"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tommy-reffell | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:178", "premiership:174"], "weight_kg": ["national:85", "premiership:104"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tomos-williams | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:192", "premiership:168"], "weight_kg": ["national:98", "premiership:97"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tonga-kofe | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["mlr:184", "national:183"], "weight_kg": ["mlr:137", "national:156"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_trevor-davison | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:195", "premiership:200"], "weight_kg": ["national:117", "premiership:120"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_trevor-nyakane | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "urc:186"], "weight_kg": ["national:110", "urc:136"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tuidraki-samusamuvodre | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:185", "super-rugby:192"], "weight_kg": ["national:95", "super-rugby:81"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tumua-manu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:174", "top14:191"], "weight_kg": ["national:96", "top14:91"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tuna-tuitama- | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:198", "super-rugby:180"], "weight_kg": ["national:91", "super-rugby:93"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tupou-va-ai | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:187", "super-rugby:207"], "weight_kg": ["national:103", "super-rugby:107"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_tyrel-lomax | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:180", "super-rugby:178"], "weight_kg": ["national:126", "super-rugby:130"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_veikoso-poloniati | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:204", "super-rugby:202"], "weight_kg": ["national:140", "super-rugby:131"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_viliame-mata | 同一 id がリーグ間で値不一致: height_cm / {"values": {"height_cm": ["national:199", "premiership:203"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_vilimoni-botitu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:171", "top14:188"], "weight_kg": ["national:83", "top14:94"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_vincent-giudicelli | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:181", "top14:188", "urc:195"], "weight_kg": ["premiership:99", "top14:110", "urc:116"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_vincent-koch | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:196", "urc:193"], "weight_kg": ["national:117", "urc:110"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_vincent-tshituka | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:198", "urc:195"], "weight_kg": ["national:113", "urc:124"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_virimi-vakatawa | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:187", "super-rugby:178"], "weight_kg": ["national:98", "super-rugby:101"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_vuate-karawalevu | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "top14:181"], "weight_kg": ["national:92", "top14:109"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_wallace-sititi | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:172", "super-rugby:189"], "weight_kg": ["national:119", "super-rugby:98"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_warner-dearns | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:195", "super-rugby:218"], "weight_kg": ["national:130", "super-rugby:128"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_wilco-louw | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:194", "urc:180"], "weight_kg": ["national:137", "urc:157"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_will-hurd | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:172", "premiership:193"], "weight_kg": ["national:139", "premiership:135"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_will-jordan | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:175", "super-rugby:185"], "weight_kg": ["national:80", "super-rugby:81"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_will-stuart | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "premiership:180", "top14:173", "urc:203"], "weight_kg": ["national:145", "premiership:135", "top14:133", "urc:139"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_xavier-numia | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:181", "super-rugby:199"], "weight_kg": ["national:128", "super-rugby:111"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_xavier-roe | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:180", "super-rugby:175"], "weight_kg": ["premiership:90", "super-rugby:88"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_yon-caperaa | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:195", "top14:166", "urc:178"], "weight_kg": ["premiership:104", "top14:108", "urc:124"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_yonn-ramond | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["premiership:197", "top14:190", "urc:201"], "weight_kg": ["premiership:123", "top14:110", "urc:128"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_yoram-moefana | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:194", "top14:195"], "weight_kg": ["national:110", "top14:107"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_zach-fittler | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["super-rugby:189", "top14:198"], "weight_kg": ["super-rugby:91", "top14:92"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_zachary-porthen | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:186", "urc:174"], "weight_kg": ["national:120", "urc:131"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_zander-fagerson | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:194", "urc:189"], "weight_kg": ["national:112", "urc:137"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_zane-nonggorr | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:192", "super-rugby:178"], "weight_kg": ["national:125", "super-rugby:136"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |
| warn | players/* | ar_zuriel-togiatama | 同一 id がリーグ間で値不一致: height_cm, weight_kg / {"values": {"height_cm": ["national:183", "premiership:193", "super-rugby:188"], "weight_kg": ["national:107", "premiership:101", "super-rugby:99"]}} | fresher な scraped_at 側を正とするルールを transform に実装し再生成。身長体重はソース間で異なり得るため公式ページで確認 |  |

## cross_person（35件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | players/* | ar_sojiro-otsuka,jrfu_u23_497477 | name_en+birthdate 一致の別 id（sojiro otsuka 2004-07-05） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_callup_haruto-watanabe,jrfu_u23_497503 | name_en+birthdate 一致の別 id（haruto watanabe 2004-12-10） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_callup_shogo-nakano,lo_484322 | name_en+birthdate 一致の別 id（shogo nakano 1997-06-11） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_callup_takuro-hojo,lo_484712 | name_en+birthdate 一致の別 id（takuro hojo 2001-09-18） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_callup_waisake-raratubua,lo_483968 | name_en+birthdate 一致の別 id（waisake raratubua 1998-03-17） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_callup_yota-kamimori,lo_483754 | name_en+birthdate 一致の別 id（yota kamimori 1999-04-26） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_national_511552,lo_483494 | name_en+birthdate 一致の別 id（shin takeuchi 2000-08-07） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_national_511566,lo_483765 | name_en+birthdate 一致の別 id（ruan botha 1992-01-10） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510767,lo_483542 | name_en+birthdate 一致の別 id（naoya ogita 2002-09-20） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510768,lo_484410 | name_en+birthdate 一致の別 id（josua kerevi 1992-06-18） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510769,lo_484882 | name_en+birthdate 一致の別 id（yoshiyuki koga 1998-08-28） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510772,lo_484906 | name_en+birthdate 一致の別 id（tomu takamoto 2001-10-10） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510775,lo_485514 | name_en+birthdate 一致の別 id（takemichi nakano 1996-12-18） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510776,lo_484887 | name_en+birthdate 一致の別 id（daisuke nishikawa 1997-08-24） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510777,lo_484751 | name_en+birthdate 一致の別 id（kouki hattori 2000-01-16） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510778,lo_484713 | name_en+birthdate 一致の別 id（koki miyasaka 2002-03-01） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510779,lo_485026 | name_en+birthdate 一致の別 id（taiki yamaguchi 2001-11-17） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319616,lo_484153 | name_en+birthdate 一致の別 id（taisei fukuda 2002-10-29） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319617,lo_484401 | name_en+birthdate 一致の別 id（daito tone 2002-07-03） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319621,lo_484531 | name_en+birthdate 一致の別 id（ryuji kobayashi 2002-10-10） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319623,lo_484451 | name_en+birthdate 一致の別 id（keito aoki 2002-06-14） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319624,lo_484258 | name_en+birthdate 一致の別 id（kenji nigara 2002-07-24） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319628,lo_484304 | name_en+birthdate 一致の別 id（masanori miyao 2002-06-01） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319629,lo_484861 | name_en+birthdate 一致の別 id（taichi kugino 2002-10-21） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u18_496082,jrfu_u20_504960 | name_en+birthdate 一致の別 id（koshi tsumura 2007-06-20） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u18_496083,jrfu_u20_505357 | name_en+birthdate 一致の別 id（yuga ichikawa 2007-06-04） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u18_496092,jrfu_u20_504973 | name_en+birthdate 一致の別 id（soshi kataoka 2007-10-12） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u18_496096,jrfu_u20_504977 | name_en+birthdate 一致の別 id（kohaku suda 2007-12-14） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u18_496099,jrfu_u20_504978 | name_en+birthdate 一致の別 id（tsunehidemichi fukuda 2007-05-17） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u18_496100,jrfu_u20_505362 | name_en+birthdate 一致の別 id（gentaro sakata 2008-01-23） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u20_504964,lo_484148 | name_en+birthdate 一致の別 id（keitatsu motoyama 2006-12-26） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | lo_483550,lo_announced_pari-pari-parkinson | name_en+birthdate 一致の別 id（pari pari parkinson 1996-09-12） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | lo_483557,lo_announced_ryoi-kamei | name_en+birthdate 一致の別 id（ryoi kamei 1994-10-08） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | lo_483678,lo_announced_shinichi-tanaka | name_en+birthdate 一致の別 id（shinichi tanaka 1994-06-08） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |
| warn | players/* | lo_484536,lo_announced_rintaro-maruyama | name_en+birthdate 一致の別 id（rintaro maruyama 1999-12-17） | 公式名鑑で同一人物確認後 data/manual/player_merges.json に登録 | 要 |

## cross_person_ja（37件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | players/* | jrfu_callup_waisake-raratubua,lo_483968 | name_ja+birthdate 一致の別 id（ワイサケララトゥブア 1998-03-17）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_national_511552,lo_483494 | name_ja+birthdate 一致の別 id（武内慎 2000-08-07）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_national_511566,lo_483765 | name_ja+birthdate 一致の別 id（ルアンボタ 1992-01-10）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510767,lo_483542 | name_ja+birthdate 一致の別 id（荻田直弥 2002-09-20）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510768,lo_484410 | name_ja+birthdate 一致の別 id（ケレビジョシュア 1992-06-18）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510769,lo_484882 | name_ja+birthdate 一致の別 id（古賀由教 1998-08-28）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510772,lo_484906 | name_ja+birthdate 一致の別 id（高本とむ 2001-10-10）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510775,lo_485514 | name_ja+birthdate 一致の別 id（中野剛通 1996-12-18）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510776,lo_484887 | name_ja+birthdate 一致の別 id（西川大輔 1997-08-24）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510777,lo_484751 | name_ja+birthdate 一致の別 id（服部航大 2000-01-16）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510778,lo_484713 | name_ja+birthdate 一致の別 id（宮坂航生 2002-03-01）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_sevens_m_510779,lo_485026 | name_ja+birthdate 一致の別 id（山口泰輝 2001-11-17）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319613,lo_483544 | name_ja+birthdate 一致の別 id（亀山昇太郎 2002-09-17）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319615,lo_484530 | name_ja+birthdate 一致の別 id（松永壮太朗 2002-07-04）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319616,lo_484153 | name_ja+birthdate 一致の別 id（福田大晟 2002-10-29）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319617,lo_484401 | name_ja+birthdate 一致の別 id（登根大斗 2002-07-03）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319621,lo_484531 | name_ja+birthdate 一致の別 id（小林龍司 2002-10-10）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319623,lo_484451 | name_ja+birthdate 一致の別 id（青木恵斗 2002-06-14）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319624,lo_484258 | name_ja+birthdate 一致の別 id（二重賢治 2002-07-24）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319626,lo_484033 | name_ja+birthdate 一致の別 id（佐藤健次 2003-01-04）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319628,lo_484304 | name_ja+birthdate 一致の別 id（宮尾昌典 2002-06-01）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319629,lo_484861 | name_ja+birthdate 一致の別 id（久木野太一 2002-10-21）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319631,lo_484862 | name_ja+birthdate 一致の別 id（秋濱悠太 2002-05-16）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u17_319632,lo_484305 | name_ja+birthdate 一致の別 id（安田昂平 2002-07-08）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u18_496082,jrfu_u20_504960 | name_ja+birthdate 一致の別 id（津村晃志 2007-06-20）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u18_496083,jrfu_u20_505357 | name_ja+birthdate 一致の別 id（市川結雅 2007-06-04）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u18_496092,jrfu_u20_504973 | name_ja+birthdate 一致の別 id（片岡湊志 2007-10-12）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u18_496096,jrfu_u20_504977 | name_ja+birthdate 一致の別 id（須田琥珀 2007-12-14）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u18_496099,jrfu_u20_504978 | name_ja+birthdate 一致の別 id（福田恒秀道 2007-05-17）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u18_496100,jrfu_u20_505362 | name_ja+birthdate 一致の別 id（坂田弦太郎 2008-01-23）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u20_504964,lo_484148 | name_ja+birthdate 一致の別 id（本山佳龍 2006-12-26）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | jrfu_u23_497497,lo_announced_midori-masuo | name_ja+birthdate 一致の別 id（舛尾緑 2004-10-19）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | lo_483550,lo_announced_pari-pari-parkinson | name_ja+birthdate 一致の別 id（パリパリパーキンソン 1996-09-12）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | lo_483557,lo_announced_ryoi-kamei | name_ja+birthdate 一致の別 id（亀井亮依 1994-10-08）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | lo_483678,lo_announced_shinichi-tanaka | name_ja+birthdate 一致の別 id（田中真一 1994-06-08）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | lo_484536,lo_announced_rintaro-maruyama | name_ja+birthdate 一致の別 id（丸山凜太朗 1999-12-17）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |
| warn | players/* | lo_484838,lo_announced_jumpei-ogura | name_ja+birthdate 一致の別 id（小倉順平 1992-07-11）、player_merges 未登録 | 公式名鑑で同一人物確認後 player_merges.json に登録 | 要 |

## match_home_away（2件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | matches/national_2026.json | jrfu_29986 | home=japan だが venue_raw='Scottish Gas Murrayfield Stadium' は英語表記（日本開催の他試合は日本語表記）。JRFU のホーム/アウェイ表記規則か、ホーム/アウェイ逆転の可能性 / {"tour_callups": ["callup_national_54111"]} | 公式試合ページでホーム/アウェイ区分を確認 | 要 |
| warn | matches/national_2026.json | jrfu_30035 | home=japan だが venue_raw='Queensland Country Bank Stadium' は英語表記（日本開催の他試合は日本語表記）。JRFU のホーム/アウェイ表記規則か、ホーム/アウェイ逆転の可能性 / {"tour_callups": ["callup_national_54111"]} | 公式試合ページでホーム/アウェイ区分を確認 | 要 |

## match_venue（1件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | matches/national_2026.json | jrfu_29969 | finished なのに venue_raw='未定'（試合前の取得値が残存） | 試合ページを再スクレイプして会場を更新 | 要 |

## merge_candidates_stale（37件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | _meta/merge_candidates.json | ar_kenta-fukuda,lo_announced_kenta-fukuda | 記録済み候補が現データでは再現しない（解決済み or id消滅） | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | ar_ryosuke-iwaihara,lo_announced_ryosuke-iwaihara | 記録済み候補が現データでは再現しない（解決済み or id消滅） | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | ar_sojiro-otsuka,jrfu_u23_497477 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_callup_haruto-watanabe,jrfu_u23_497503 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_callup_shogo-nakano,lo_484322 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_callup_takuro-hojo,lo_484712 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_callup_waisake-raratubua,lo_483968 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_callup_yota-kamimori,lo_483754 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_national_511552,lo_483494 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_national_511566,lo_483765 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_sevens_m_510767,lo_483542 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_sevens_m_510768,lo_484410 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_sevens_m_510769,lo_484882 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_sevens_m_510772,lo_484906 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_sevens_m_510775,lo_485514 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_sevens_m_510776,lo_484887 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_sevens_m_510777,lo_484751 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_sevens_m_510778,lo_484713 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_sevens_m_510779,lo_485026 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_u17_319616,lo_484153 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_u17_319617,lo_484401 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_u17_319621,lo_484531 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_u17_319623,lo_484451 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_u17_319624,lo_484258 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_u17_319628,lo_484304 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_u17_319629,lo_484861 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_u18_496082,jrfu_u20_504960 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_u18_496083,jrfu_u20_505357 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_u18_496092,jrfu_u20_504973 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_u18_496096,jrfu_u20_504977 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_u18_496099,jrfu_u20_504978 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_u18_496100,jrfu_u20_505362 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | jrfu_u20_504964,lo_484148 | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | lo_483550,lo_announced_pari-pari-parkinson | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | lo_483557,lo_announced_ryoi-kamei | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | lo_483678,lo_announced_shinichi-tanaka | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |
| warn | _meta/merge_candidates.json | lo_484536,lo_announced_rintaro-maruyama | 現データの候補が merge_candidates.json に未記録 | 次回 run で再生成 |  |

## missing_key（13件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | players/league-one-d1.json | 2件 | キー 'nationality' 自体が欠落（null ではなく未定義） / {"sample_ids": ["lo_announced_midori-masuo", "lo_announced_toshi-kurita-butlin"]} | 生成元を schemas.Player.model_dump() 経由に統一して全キーを出力 |  |
| warn | players/league-one-d1.json | 30件 | キー 'caps' 自体が欠落（null ではなく未定義） / {"sample_ids": ["lo_announced_aki-tuivailala", "lo_announced_antonio-shalfoon", "lo_announced_bailey-trew", "lo_announced_bailyn-sullivan", "lo_announced_ed-kasprowicz", "lo_announced_eiji-tsuchiya", "lo_announced_gage-jackson", "lo_announced_jack-dempsey", "lo_announced_james-lowe", "lo_announced_jonah-lowe"]} | 生成元を schemas.Player.model_dump() 経由に統一して全キーを出力 |  |
| warn | players/league-one-d1.json | 40件 | キー 'instagram' 自体が欠落（null ではなく未定義） / {"sample_ids": ["lo_announced_aki-tuivailala", "lo_announced_antonio-shalfoon", "lo_announced_aphelele-fassi", "lo_announced_bailey-trew", "lo_announced_bailyn-sullivan", "lo_announced_david-havili", "lo_announced_ed-kasprowicz", "lo_announced_eiji-tsuchiya", "lo_announced_gage-jackson", "lo_announced_george-bridge"]} | 生成元を schemas.Player.model_dump() 経由に統一して全キーを出力 |  |
| warn | players/league-one-d1.json | 40件 | キー 'merged_from' 自体が欠落（null ではなく未定義） / {"sample_ids": ["lo_announced_aki-tuivailala", "lo_announced_antonio-shalfoon", "lo_announced_aphelele-fassi", "lo_announced_bailey-trew", "lo_announced_bailyn-sullivan", "lo_announced_david-havili", "lo_announced_ed-kasprowicz", "lo_announced_eiji-tsuchiya", "lo_announced_gage-jackson", "lo_announced_george-bridge"]} | 生成元を schemas.Player.model_dump() 経由に統一して全キーを出力 |  |
| warn | players/league-one-d1.json | 40件 | キー 'squad' 自体が欠落（null ではなく未定義） / {"sample_ids": ["lo_announced_aki-tuivailala", "lo_announced_antonio-shalfoon", "lo_announced_aphelele-fassi", "lo_announced_bailey-trew", "lo_announced_bailyn-sullivan", "lo_announced_david-havili", "lo_announced_ed-kasprowicz", "lo_announced_eiji-tsuchiya", "lo_announced_gage-jackson", "lo_announced_george-bridge"]} | 生成元を schemas.Player.model_dump() 経由に統一して全キーを出力 |  |
| warn | players/league-one-d1.json | 40件 | キー 'league_caps' 自体が欠落（null ではなく未定義） / {"sample_ids": ["lo_announced_aki-tuivailala", "lo_announced_antonio-shalfoon", "lo_announced_aphelele-fassi", "lo_announced_bailey-trew", "lo_announced_bailyn-sullivan", "lo_announced_david-havili", "lo_announced_ed-kasprowicz", "lo_announced_eiji-tsuchiya", "lo_announced_gage-jackson", "lo_announced_george-bridge"]} | 生成元を schemas.Player.model_dump() 経由に統一して全キーを出力 |  |
| warn | players/league-one-d1.json | 40件 | キー 'education' 自体が欠落（null ではなく未定義） / {"sample_ids": ["lo_announced_aki-tuivailala", "lo_announced_antonio-shalfoon", "lo_announced_aphelele-fassi", "lo_announced_bailey-trew", "lo_announced_bailyn-sullivan", "lo_announced_david-havili", "lo_announced_ed-kasprowicz", "lo_announced_eiji-tsuchiya", "lo_announced_gage-jackson", "lo_announced_george-bridge"]} | 生成元を schemas.Player.model_dump() 経由に統一して全キーを出力 |  |
| warn | players/league-one-d1.json | 40件 | キー 'is_featured' 自体が欠落（null ではなく未定義） / {"sample_ids": ["lo_announced_aki-tuivailala", "lo_announced_antonio-shalfoon", "lo_announced_aphelele-fassi", "lo_announced_bailey-trew", "lo_announced_bailyn-sullivan", "lo_announced_david-havili", "lo_announced_ed-kasprowicz", "lo_announced_eiji-tsuchiya", "lo_announced_gage-jackson", "lo_announced_george-bridge"]} | 生成元を schemas.Player.model_dump() 経由に統一して全キーを出力 |  |
| warn | players/league-one-d1.json | 40件 | キー 'is_minor' 自体が欠落（null ではなく未定義） / {"sample_ids": ["lo_announced_aki-tuivailala", "lo_announced_antonio-shalfoon", "lo_announced_aphelele-fassi", "lo_announced_bailey-trew", "lo_announced_bailyn-sullivan", "lo_announced_david-havili", "lo_announced_ed-kasprowicz", "lo_announced_eiji-tsuchiya", "lo_announced_gage-jackson", "lo_announced_george-bridge"]} | 生成元を schemas.Player.model_dump() 経由に統一して全キーを出力 |  |
| warn | players/league-one-d1.json | 40件 | キー 'career' 自体が欠落（null ではなく未定義） / {"sample_ids": ["lo_announced_aki-tuivailala", "lo_announced_antonio-shalfoon", "lo_announced_aphelele-fassi", "lo_announced_bailey-trew", "lo_announced_bailyn-sullivan", "lo_announced_david-havili", "lo_announced_ed-kasprowicz", "lo_announced_eiji-tsuchiya", "lo_announced_gage-jackson", "lo_announced_george-bridge"]} | 生成元を schemas.Player.model_dump() 経由に統一して全キーを出力 |  |
| warn | players/league-one-d1.json | 40件 | キー 'season_stats' 自体が欠落（null ではなく未定義） / {"sample_ids": ["lo_announced_aki-tuivailala", "lo_announced_antonio-shalfoon", "lo_announced_aphelele-fassi", "lo_announced_bailey-trew", "lo_announced_bailyn-sullivan", "lo_announced_david-havili", "lo_announced_ed-kasprowicz", "lo_announced_eiji-tsuchiya", "lo_announced_gage-jackson", "lo_announced_george-bridge"]} | 生成元を schemas.Player.model_dump() 経由に統一して全キーを出力 |  |
| warn | players/league-one-d1.json | 40件 | キー 'image_url' 自体が欠落（null ではなく未定義） / {"sample_ids": ["lo_announced_aki-tuivailala", "lo_announced_antonio-shalfoon", "lo_announced_aphelele-fassi", "lo_announced_bailey-trew", "lo_announced_bailyn-sullivan", "lo_announced_david-havili", "lo_announced_ed-kasprowicz", "lo_announced_eiji-tsuchiya", "lo_announced_gage-jackson", "lo_announced_george-bridge"]} | 生成元を schemas.Player.model_dump() 経由に統一して全キーを出力 |  |
| warn | players/league-one-d1.json | 40件 | キー 'name_kana' 自体が欠落（null ではなく未定義） / {"sample_ids": ["lo_announced_aki-tuivailala", "lo_announced_antonio-shalfoon", "lo_announced_aphelele-fassi", "lo_announced_bailey-trew", "lo_announced_bailyn-sullivan", "lo_announced_david-havili", "lo_announced_ed-kasprowicz", "lo_announced_eiji-tsuchiya", "lo_announced_gage-jackson", "lo_announced_george-bridge"]} | 生成元を schemas.Player.model_dump() 経由に統一して全キーを出力 |  |

## name_format（25件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | players/age-grade.json | 1件 | name_ja 注記/括弧混入 / {"sample_ids": ["jrfu_u18_496087"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| warn | players/highschool.json | 204件 | name_kana がひらがな（他リーグはカタカナ） / {"sample_ids": ["hs_名古屋高等学校__井上咲太郎", "hs_名古屋高等学校__大鋸一貴", "hs_名古屋高等学校__大隈大介", "hs_名古屋高等学校__安東彪冴", "hs_名古屋高等学校__安田悠", "hs_名古屋高等学校__富塚耕太", "hs_名古屋高等学校__山北剛大", "hs_名古屋高等学校__山根奏大", "hs_名古屋高等学校__平松佑一朗", "hs_名古屋高等学校__服部謙成", "hs_名古屋高等学校__松野秀悟", "hs_名古屋高等学校__森本伊吹", "hs_名古屋高等学校__森本昊希", "hs_名古屋高等学校__田中颯次郎", "hs_名古屋高等学校__荒川拓澄"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| warn | players/league-one-d1.json | 1件 | name_ja 注記/括弧混入 / {"sample_ids": ["lo_493747"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| warn | players/league-one-d1.json | 232件 | name_ja 空白+中黒（例『ギディオン ・コーヘレンバーグ』） / {"sample_ids": ["lo_483287", "lo_483288", "lo_483289", "lo_483290", "lo_483474", "lo_483475", "lo_483478", "lo_483479", "lo_483486", "lo_483487", "lo_483489", "lo_483490", "lo_483492", "lo_483497", "lo_483500"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| warn | players/league-one-d1.json | 6件 | name_ja に英字 / {"sample_ids": ["lo_484300", "lo_484338", "lo_484671", "lo_484734", "lo_484865", "lo_484866"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| warn | players/league-one-d2.json | 104件 | name_ja 空白+中黒（例『ギディオン ・コーヘレンバーグ』） / {"sample_ids": ["lo_483527", "lo_483530", "lo_483531", "lo_483533", "lo_483534", "lo_483535", "lo_483540", "lo_483541", "lo_483546", "lo_483547", "lo_483548", "lo_483550", "lo_483567", "lo_483569", "lo_483679"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| warn | players/league-one-d2.json | 6件 | name_ja 注記/括弧混入 / {"sample_ids": ["lo_483704", "lo_483708", "lo_484224", "lo_484232", "lo_484233", "lo_484978"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| warn | players/league-one-d3.json | 11件 | name_ja 注記/括弧混入 / {"sample_ids": ["lo_483803", "lo_484111", "lo_484123", "lo_484128", "lo_484636", "lo_484655", "lo_484769", "lo_484782", "lo_484796", "lo_484805", "lo_497518"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| warn | players/league-one-d3.json | 1件 | name_ja に英字 / {"sample_ids": ["lo_484083"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| warn | players/league-one-d3.json | 42件 | name_ja 空白+中黒（例『ギディオン ・コーヘレンバーグ』） / {"sample_ids": ["lo_483787", "lo_483788", "lo_483798", "lo_483802", "lo_483822", "lo_483823", "lo_484081", "lo_484082", "lo_484083", "lo_484085", "lo_484091", "lo_484092", "lo_484093", "lo_484094", "lo_484095"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| warn | players/national.json | 3件 | name_en に非ラテン文字 / {"sample_ids": ["ar_adrian-motoc", "ar_dragos-ser", "ar_stefan-iancu"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| warn | players/national.json | 4件 | name_ja 注記/括弧混入 / {"sample_ids": ["jrfu_callup_haruto-watanabe", "jrfu_callup_shogo-nakano", "jrfu_callup_takuro-hojo", "jrfu_callup_yota-kamimori"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| warn | players/university.json | 350件 | name_ja 全角空白 / {"sample_ids": ["univ_國學院大學__三浦涼哉", "univ_國學院大學__大矢青空", "univ_國學院大學__石原悠汰", "univ_國學院大學__経済学部経済学科", "univ_大東文化大学__中山棱斗", "univ_大東文化大学__中嶋祥太郎", "univ_大東文化大学__中森悠路", "univ_大東文化大学__丸山貞", "univ_大東文化大学__乙成凌暢", "univ_大東文化大学__亀川和真", "univ_大東文化大学__井上大悟", "univ_大東文化大学__井崎克", "univ_大東文化大学__井川太陽", "univ_大東文化大学__今石大輝", "univ_大東文化大学__佐藤淳平"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| warn | players/university.json | 661件 | name_kana がひらがな（他リーグはカタカナ） / {"sample_ids": ["univ_大東文化大学__中山棱斗", "univ_大東文化大学__中嶋祥太郎", "univ_大東文化大学__中森悠路", "univ_大東文化大学__丸山貞", "univ_大東文化大学__乙成凌暢", "univ_大東文化大学__亀川和真", "univ_大東文化大学__二上伊織", "univ_大東文化大学__井上大悟", "univ_大東文化大学__井崎克", "univ_大東文化大学__井川太陽", "univ_大東文化大学__今村朱里", "univ_大東文化大学__今石大輝", "univ_大東文化大学__佐々木開地", "univ_大東文化大学__佐藤淳平", "univ_大東文化大学__保坂浩幸"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| info | players/age-grade.json | 20件 | name_en 全大文字（ソース表記） / {"sample_ids": ["jrfu_u17_319611", "jrfu_u17_319612", "jrfu_u17_319613", "jrfu_u17_319614", "jrfu_u17_319616", "jrfu_u17_319617", "jrfu_u17_319618", "jrfu_u17_319622", "jrfu_u17_319623", "jrfu_u17_319624", "jrfu_u17_319625", "jrfu_u17_319626", "jrfu_u17_319627", "jrfu_u17_319628", "jrfu_u17_319629"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| info | players/league-one-d1.json | 4件 | name_en 全大文字（ソース表記） / {"sample_ids": ["lo_484149", "lo_484723", "lo_485067", "lo_485070"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| info | players/league-one-d2.json | 20件 | name_en 全大文字（ソース表記） / {"sample_ids": ["lo_484995", "lo_484996", "lo_484997", "lo_484998", "lo_484999", "lo_485000", "lo_485001", "lo_485002", "lo_485003", "lo_485004", "lo_485005", "lo_485006", "lo_485007", "lo_485008", "lo_485009"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| info | players/league-one-d3.json | 60件 | name_en 全大文字（ソース表記） / {"sample_ids": ["lo_484628", "lo_484634", "lo_484656", "lo_484914", "lo_484915", "lo_484917", "lo_484918", "lo_484919", "lo_484921", "lo_484923", "lo_484933", "lo_484934", "lo_484935", "lo_484936", "lo_484937"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| info | players/mlr.json | 2件 | name_en 全大文字（ソース表記） / {"sample_ids": ["ar_ej-freeman", "ar_juan-philip-smith"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| info | players/national.json | 6件 | name_en 全大文字（ソース表記） / {"sample_ids": ["ar_aj-alatimu", "ar_aniol-franch", "ar_jj-kotze", "ar_john-wessel-bell", "ar_rg-snyman", "ar_wp-nel"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| info | players/premiership.json | 3件 | name_en 全大文字（ソース表記） / {"sample_ids": ["ar_aj-macginty", "ar_jj-scheepers", "ar_jj-van-der-mescht"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| info | players/super-rugby.json | 3件 | name_en 全大文字（ソース表記） / {"sample_ids": ["ar_aj-lam", "ar_jd-van-der-westhuizen", "ar_tk-howden"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| info | players/top14.json | 3件 | name_en 全大文字（ソース表記） / {"sample_ids": ["ar_aj-lam", "ar_gj-van-velze", "ar_jj-fourie"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| info | players/university.json | 87件 | name_en 全大文字（ソース表記） / {"sample_ids": ["univ_同志社大学__上嶋友也", "univ_同志社大学__下平夏生", "univ_同志社大学__中島仙太郎", "univ_同志社大学__中嶋優成", "univ_同志社大学__中村壮吾", "univ_同志社大学__中谷陸人", "univ_同志社大学__丹羽雄丸", "univ_同志社大学__仁保顕隆", "univ_同志社大学__伊藤陽生", "univ_同志社大学__内田瑛佑", "univ_同志社大学__前川竜之介", "univ_同志社大学__前田卓耶", "univ_同志社大学__吉川航平", "univ_同志社大学__吉田慧悟", "univ_同志社大学__吉田樹"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |
| info | players/urc.json | 13件 | name_en 全大文字（ソース表記） / {"sample_ids": ["ar_jc-mars", "ar_jc-pretorius", "ar_jd-hattingh", "ar_jd-schickerling", "ar_jf-van-heerden", "ar_jj-hanrahan", "ar_jj-kotze", "ar_jj-theron", "ar_jp-du-preez", "ar_pj-botha", "ar_rf-schoeman", "ar_rg-snyman", "ar_sj-kotze"]} | transform で正規化（空白・中黒・注記除去）。全大文字は表示側で整形 |  |

## nationality_variant（2件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | players/* | nationality | 国籍コード体系が混在: ISO2=['JP']（{'JP': {'age-grade': 113, 'national': 7, 'sevens-national': 26}}） / {"examples": {"JP": {"age-grade": 113, "national": 7, "sevens-national": 26}, "Japan": {"league-one-d1": 9, "national": 22}}} | 日本は 'Japan' と 'JP' が併存。どちらかに統一 |  |
| info | players/* | United-States | 国名にハイフン（slug由来）: {'national': 28, 'premiership': 3} | 表示名へ変換 |  |

## position_variant（2件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | players/national.json | national | 詳細ポジションと FW/BK 区分が混在 / {"examples": {"Back row": 235, "BK": 3, "FW": 4}} | ポジション正規化表（NO.8→NO8、区切り→'/'）を transform に追加 |  |
| warn | players/university.json | university | NO8 / NO.8; 複数ポジション区切り [' ', '/', '・'] / {"examples": {"NO.8": 44, "FL/NO.8": 7, "PR/ LO": 1, "LO/NO.8": 4, "PR/LO/NO.8": 1, "LO/FL/NO.8": 5, "NO.8/HO/FL": 1, "SH WTB": 1, "FL NO.8": 1, "WTB CTB": 5, "LO FL": 1, "PR HO WTB": 1, "PR LO": 2, "SO CTB FB": 1, "SH WTB FB": 1, "PR LO NO.8": 1, "HO FL": 1, "WTB FB": 1, "PR HO": 1, "SO FB": 1, "FL・NO.8": 1, "SH・SO": 1, "CTB・WTB": 2, "LO・FL": 3, "FB・SO": 2, "HO/NO.8": 2, "PR/LO/FL/NO.8": 1, "FL/N | ポジション正規化表（NO.8→NO8、区切り→'/'）を transform に追加 |  |

## redirect_source_live（1件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | _meta/redirects.json | 79件 | リダイレクト元 slug が現 master の有効 slug と同一（現ページを潰す） / {"samples": ["/players/adrian-choat", "/players/akira-ioane", "/players/anton-lienert-brown", "/players/ardie-savea", "/players/ben-gunter", "/players/charlie-lawrence", "/players/charlie-titcombe", "/players/cheslin-kolbe", "/players/damian-de-allende", "/players/dylan-riley", "/players/epineri-uluiviti", "/players/faf-de-klerk", "/players/franco-mostert", "/players/harry-hockings", "/players/har |  |  |

## redirect_target（1件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | _meta/redirects.json | 18件 | リダイレクト先 slug が現 master に存在しない（404 になる） / {"samples": [["/players/amanaki-taiyo-lotoahea", "/players/amanaki-taiyo-lotoahea-483529"], ["/players/christian-lealiifano", "/players/christian-lealiifano-160"], ["/players/dino-lamb", "/players/dino-lamb-484810"], ["/players/faf-de-klerk", "/players/faf-de-klerk-390"], ["/players/genki-sudou", "/players/genki-sudou-483476"], ["/players/hayato-ishibashi", "/players/hayato-ishibashi-1174"], ["/pl | retired 扱いに移すか、現 slug に付け替え |  |

## retired_live（1件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | _meta/retired_slugs.json | 1435件 | retired 扱いの slug が現 master で有効（復活済み） / {"samples": ["/players/aaron-o-brien", "/players/aaron-wainwright", "/players/abraham-pole", "/players/adam-hastings", "/players/adam-lennox", "/players/adam-radwan", "/players/adre-smith", "/players/agustin-moyano", "/players/aidan-pugh", "/players/aidan-ross", "/players/aiden-ainsworth-cave", "/players/aisea-nawai", "/players/aitzol-king", "/players/aj-lam", "/players/aj-macginty"]} | retired_slugs から除外 |  |

## roster_multi_team（117件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | teams/* | ar_aiden-stait | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_aj-lam | 複数チームの roster に所属: ['blues', 'clermont'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_akenzua-al-kareem-abdul-khalik | 複数チームの roster に所属: ['gloucester', 'la-rochelle'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_alfie-barbeary | 複数チームの roster に所属: ['gloucester', 'la-rochelle'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_andre-riaan-warner | 複数チームの roster に所属: ['seattle-seawolves', 'stormers'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_archie-griffin | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_archie-stanley | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_arthur-cordwell | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_arthur-green | 複数チームの roster に所属: ['gloucester', 'la-rochelle'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_badri-tsikhistavi | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_bayley-kuenzle | 複数チームの roster に所属: ['western-force', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_benjamin-lahet | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_beno--obano- | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_billy-sela | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_braydon-ennor | 複数チームの roster に所属: ['crusaders', 'perpignan'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_charlie-ewels | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_chris-cloete | 複数チームの roster に所属: ['gloucester', 'la-rochelle'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_connor-treacey | 複数チームの roster に所属: ['bath', 'la-rochelle'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_cullen-grace | 複数チームの roster に所属: ['crusaders', 'scarlets'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_dallas-mcleod | 複数チームの roster に所属: ['exeter', 'crusaders'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_dalton-papali-i | 複数チームの roster に所属: ['hurricanes', 'castres'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_daniel-marais | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_darcy-swain | 複数チームの roster に所属: ['blues', 'clermont'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_denis-marchois | 複数チームの roster に所属: ['bath', 'pau', 'scarlets'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_dylan-indaburu | 複数チームの roster に所属: ['bath', 'pau'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_eddie-erskine | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_elia-canakaivata | 複数チームの roster に所属: ['sale', 'fijian-drua'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_elliot-stooke | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_ereatara-enari | 複数チームの roster に所属: ['hurricanes', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_etene-nanai-seturo | 複数チームの roster に所属: ['chiefs', 'clermont'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_ethan-staddon | 複数チームの roster に所属: ['bristol', 'la-rochelle'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_ewan-richards | 複数チームの roster に所属: ['bath', 'la-rochelle'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_facundo-bosch | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_franco-molina | 複数チームの roster に所属: ['newcastle', 'western-force'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_george-timmins | 複数チームの roster に所属: ['bath', 'clermont'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_guido-petti | 複数チームの roster に所属: ['harlequins', 'bayonne'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_hame-faiva | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_harry-johnson-holmes | 複数チームの roster に所属: ['harlequins', 'western-force'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_harry-plummer | 複数チームの roster に所属: ['waratahs', 'clermont'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_harvey-cuckson | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_hoskins-sotutu | 複数チームの roster に所属: ['newcastle', 'hurricanes'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_hugo-afonso | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_hugo-leclerq | 複数チームの roster に所属: ['bath', 'pau'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_ignacio-valdes-leiva | 複数チームの roster に所属: ['harlequins', 'pau'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_imanol-thicoipe | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_inia-tabuavou | 複数チームの roster に所属: ['fijian-drua', 'vannes'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_ioan-emanuel | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_isaia-walker-leawere | 複数チームの roster に所属: ['hurricanes', 'benetton'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_jack-bennett | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_jaco-coetzee | 複数チームの roster に所属: ['bath', 'clermont'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_jacques-du-plessis | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_jasper-spandler | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_johan-momsen | 複数チームの roster に所属: ['anthem-rc', 'sharks'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_johannes-jonker | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_john-stewart | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_jokin-duhalt | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_josh-flook | 複数チームの roster に所属: ['reds', 'benetton'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_josh-mcnally | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_juan-schoeman | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_jules-derre | 複数チームの roster に所属: ['harlequins', 'pau'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_jules-martin-bonnard | 複数チームの roster に所属: ['harlequins', 'pau'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_kienan-higgins | 複数チームの roster に所属: ['new-england-free-jacks', 'edinburgh'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_kieran-verden | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_lalakai-foketi | 複数チームの roster に所属: ['chiefs', 'ospreys'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_lawson-creighton | 複数チームの roster に所属: ['waratahs', 'ospreys'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_louie-chapman | 複数チームの roster に所属: ['crusaders', 'edinburgh'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_louis-ortolan | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_louis-werchon | 複数チームの roster に所属: ['reds', 'benetton'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_lucas-official | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_luke-tagi | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_martin-villar | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_mateo-guerin | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_matheo-futhazar | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_matis-perchaud | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_max-bru | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_max-pearce | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_mikey-summerfield | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_mills-sanerivi | 複数チームの roster に所属: ['moana-pasifika', 'vannes'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_nial-annett | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_oscar-lennon | 複数チームの roster に所属: ['new-england-free-jacks', 'bristol'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_pascal-cotet | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_peio-dospital | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_pierre-castillon | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_pieter-scholtz | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_ponipate-loganimasi | 複数チームの roster に所属: ['sale', 'fijian-drua'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_pouri-rakete-stones | 複数チームの roster に所属: ['newcastle', 'hurricanes'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_quentin-bethune | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_quinn-roux | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_rafael-cayuela | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_rhys-carre | 複数チームの roster に所属: ['saracens', 'bulls'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_ricky-riccitelli | 複数チームの roster に所属: ['hurricanes', 'montpellier'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_riley-higgins | 複数チームの roster に所属: ['hurricanes', 'edinburgh'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_rory-cameron | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_rufus-mclean | 複数チームの roster に所属: ['seattle-seawolves', 'paris'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_sam-crean | 複数チームの roster に所属: ['northampton', 'ulster'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_sam-moli | 複数チームの roster に所属: ['leicester', 'moana-pasifika'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_scott-kirk | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_semisi-paea | 複数チームの roster に所属: ['moana-pasifika', 'cardiff'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_seru-uru | 複数チームの roster に所属: ['reds', 'racing-92'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_sevu-reece | 複数チームの roster に所属: ['crusaders', 'perpignan'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_simione-kuruvoli | 複数チームの roster に所属: ['fijian-drua', 'vannes'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_sione-ahio | 複数チームの roster に所属: ['chiefs', 'la-rochelle'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_swan-cormenier | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_taine-plumtree | 複数チームの roster に所属: ['hurricanes', 'scarlets'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_terrell-peita | 複数チームの roster に所属: ['blues', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_tevita-tatafu | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_thomas-acquier | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_thomas-du-toit | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'sharks'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_tom-allen | 複数チームの roster に所属: ['hurricanes', 'scarlets'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_tom-dunn | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_vincent-giudicelli | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_will-stuart | 複数チームの roster に所属: ['gloucester', 'la-rochelle', 'glasgow'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_xavier-roe | 複数チームの roster に所属: ['sale', 'chiefs'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_yon-caperaa | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_yonn-ramond | 複数チームの roster に所属: ['bath', 'pau', 'dragons'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_zach-fittler | 複数チームの roster に所属: ['waratahs', 'pau'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |
| warn | teams/* | ar_zuriel-togiatama | 複数チームの roster に所属: ['newcastle', 'fijian-drua'] | 移籍途中の可能性。公式名鑑で現所属確認 | 要 |

## school_name_variant（32件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | schools/schools.json | hartpurycollege,hartpurycollege-2 | 正規化後同名（高等学校/高校・空白・全半角）: hartpurycollege | school_aliases.json で統合 |  |
| warn | schools/schools.json | kings,kings-2 | 正規化後同名（高等学校/高校・空白・全半角）: kings | school_aliases.json で統合 |  |
| warn | schools/schools.json | thesouthportschool,thesouthportschool-2 | 正規化後同名（高等学校/高校・空白・全半角）: thesouthportschool | school_aliases.json で統合 |  |
| warn | schools/schools.json | 中部大学春日丘高校,中部大学春日丘高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 中部大学春日丘高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 京都市立京都工学院高校,京都市立京都工学院高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 京都市立京都工学院高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 京都成章高校,京都成章高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 京都成章高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 仙台育英学園高校,仙台育英学園高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 仙台育英学園高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 國學院大學久我山高校,國學院大學久我山高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 國學院大學久我山高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 國學院大學栃木高校,國學院大學栃木高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 國學院大學栃木高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 報徳学園高校,報徳学園高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 報徳学園高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 大阪桐蔭高校,大阪桐蔭高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 大阪桐蔭高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 天理高校,天理高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 天理高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 崇徳高校,崇徳高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 崇徳高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 常翔学園高校,常翔学園高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 常翔学園高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 愛知高校,愛知高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 愛知高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 日本大学高校,日本大学高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 日本大学高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 日本航空石川高校,日本航空石川高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 日本航空石川高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 早稲田摂陵高校,早稲田摂陵高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 早稲田摂陵高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 昌平高校,昌平高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 昌平高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 本郷高校,本郷高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 本郷高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 東海大学付属大阪仰星高校,東海大学付属大阪仰星高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 東海大学付属大阪仰星高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 東海大学付属相模高校,東海大学付属相模高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 東海大学付属相模高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 東福岡高校,東福岡高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 東福岡高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 桐蔭学園高校,桐蔭学園高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 桐蔭学園高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 流通経済大学付属柏高校,流通経済大学付属柏高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 流通経済大学付属柏高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 流通経済大学柏高校,流通経済大学柏高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 流通経済大学柏高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 目黒学院高校,目黒学院高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 目黒学院高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 石見智翠館高校,石見智翠館高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 石見智翠館高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 茗溪学園高校,茗溪学園高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 茗溪学園高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 開志国際高校,開志国際高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 開志国際高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 関東学院六浦高校,関東学院六浦高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 関東学院六浦高校 | school_aliases.json で統合 |  |
| warn | schools/schools.json | 静岡聖光学院高校,静岡聖光学院高等学校 | 正規化後同名（高等学校/高校・空白・全半角）: 静岡聖光学院高校 | school_aliases.json で統合 |  |

## school_ref（1件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | players/* | 5409件 | education.school_id が全件 null（schools.json と未接続） | migrate_schools の name_raw→school_id 解決を transform に組み込む |  |

## school_type（5件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | schools/schools.json | college | type=univ だが名称が高校系: 'College' |  |  |
| warn | schools/schools.json | grammar | type=univ だが名称が高校系: 'Grammar' |  |  |
| warn | schools/schools.json | hartpurycollege | type=univ だが名称が高校系: 'HartpuryCollege' |  |  |
| warn | schools/schools.json | highschool | type=univ だが名称が高校系: 'Highschool' |  |  |
| warn | schools/schools.json | setantacollege | type=univ だが名称が高校系: 'Setantacollege' |  |  |

## slug_format（47件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | players/mlr.json | ar_aidan-king- | slug='aidan-king-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/national.json | ar_beno--obano- | slug='beno--obano-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/national.json | ar_jack--walker- | slug='jack--walker-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/national.json | ar_joji-nasova- | slug='joji-nasova-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/national.json | ar_josh--adams- | slug='josh--adams-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/national.json | ar_kenji-sato- | slug='kenji-sato-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/national.json | ar_mickael--guillard | slug='mickael--guillard' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/national.json | ar_nick--tompkins | slug='nick--tompkins' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/national.json | ar_tuna-tuitama- | slug='tuna-tuitama-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/premiership.json | ar_adam-scott- | slug='adam-scott-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/premiership.json | ar_beno--obano- | slug='beno--obano-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/premiership.json | ar_george-taylor- | slug='george-taylor-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/premiership.json | ar_jack--walker- | slug='jack--walker-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/premiership.json | ar_nick--tompkins | slug='nick--tompkins' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/premiership.json | ar_oliver-spencer- | slug='oliver-spencer-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/premiership.json | ar_osian-williams- | slug='osian-williams-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/premiership.json | ar_sam-harris- | slug='sam-harris-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/premiership.json | ar_sam-williams- | slug='sam-williams-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/premiership.json | ar_simon--kerrod | slug='simon--kerrod' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/premiership.json | ar_tom-james- | slug='tom-james-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/premiership.json | ar_tom-rowe- | slug='tom-rowe-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/premiership.json | ar_val-rapava-ruskin- | slug='val-rapava-ruskin-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/super-rugby.json | ar_james-moore- | slug='james-moore-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/super-rugby.json | ar_joji-nasova- | slug='joji-nasova-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/super-rugby.json | ar_tuna-tuitama- | slug='tuna-tuitama-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/top14.json | ar_-juan-segundo-martin-montilla | slug='-juan-segundo-martin-montilla' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/top14.json | ar_bartholome-sanson- | slug='bartholome-sanson-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/top14.json | ar_beno--obano- | slug='beno--obano-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/top14.json | ar_martin-durand- | slug='martin-durand-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/top14.json | ar_mateo-tissot- | slug='mateo-tissot-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/top14.json | ar_mickael--guillard | slug='mickael--guillard' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/top14.json | ar_ruan-swart- | slug='ruan-swart-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/top14.json | ar_sio-kite- | slug='sio-kite-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/urc.json | ar_armand--van-der-merwe | slug='armand--van-der-merwe' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/urc.json | ar_ben-evans- | slug='ben-evans-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/urc.json | ar_ben-white- | slug='ben-white-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/urc.json | ar_beno--obano- | slug='beno--obano-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/urc.json | ar_dan-kelly- | slug='dan-kelly-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/urc.json | ar_dylan-james- | slug='dylan-james-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/urc.json | ar_evan-lloyd- | slug='evan-lloyd-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/urc.json | ar_henry-walker- | slug='henry-walker-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/urc.json | ar_joe-roberts- | slug='joe-roberts-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/urc.json | ar_josh--adams- | slug='josh--adams-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/urc.json | ar_lewis-jones- | slug='lewis-jones-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/urc.json | ar_scott-wilson- | slug='scott-wilson-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/urc.json | ar_shane-jennings- | slug='shane-jennings-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |
| warn | players/urc.json | ar_tom-wood- | slug='tom-wood-' に先頭/末尾/連続ハイフン（元ページslug由来の可能性） | URLとして残すかは all.rugby 側slugを確認のうえ判断 | 要 |

## source_kind（40件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | players/league-one-d1.json | lo_announced_aki-tuivailala | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6047"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_antonio-shalfoon | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6047"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_aphelele-fassi | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6042"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_bailey-trew | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6092"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_bailyn-sullivan | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6092"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_david-havili | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6042"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_ed-kasprowicz | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6079"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_eiji-tsuchiya | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6047"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_gage-jackson | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6040"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_george-bridge | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6023"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_grant-williams | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6023"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_hunter-paisami | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6071"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_jack-dempsey | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6042"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_james-lowe | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6079"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_jonah-lowe | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6073"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_joseph-gavigan | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6073"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_jumpei-ogura | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6060"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_keita-ando | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6067"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_keito-tawara | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6040"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_keran-van-staden | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6092"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_kurt-eklund | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6040"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_kurt-lee-arendse | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6049"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_laghlan-mcwhannell | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6040"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_malakye-enasio | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6044"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_mamoru-harada | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6016"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_mark-nawaqanitawase | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/5322"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_matthew-dalton | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6078"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_max-douglas | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6047"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_midori-masuo | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/5570"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_naoto-saito | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6033"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_pari-pari-parkinson | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6040"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_rintaro-maruyama | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6060"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_ruan-nortje | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6036"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_ryoi-kamei | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6060"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_samipeni-finau | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6040"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_shinichi-tanaka | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6040"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_stephen-perofeta | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6040"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_tamati-tua | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6081"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_tanielu-terea | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6060"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |
| warn | players/league-one-d1.json | lo_announced_toshi-kurita-butlin | source='manual-curated'（スクレイパー以外の由来。00 原則1） / {"source_url": "https://league-one.jp/news/6044"} | 公式名鑑に掲載され次第スクレイプ値で置換し manual 由来レコードを除去 |  |

## standings_stale（2件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | standings/premiership_2025-26.json | premiership_2025-26 | scraped_at=2026-08-18T21:30:12+09:00 が teams 最新 2026-09-28T10:30:51+09:00 より40日古い | standings スクレイプが失敗し旧データ残存の可能性。再取得 |  |
| warn | standings/urc_2025-26.json | urc_2025-26 | scraped_at=2026-08-18T21:04:33+09:00 が teams 最新 2026-09-28T10:05:23+09:00 より40日古い | standings スクレイプが失敗し旧データ残存の可能性。再取得 |  |

## team_id_variant（1件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | matches/national_2026.json | japan/japan-xv | 類似 team id が混在（japan: 7件, japan-xv: 1件） | 別チーム扱い（例: XV 名義の非テストマッチ）か同一チームの表記ゆれかを公式で確認 | 要 |

## team_name_missing（17件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | teams/mlr.json | anthem-rc | 表示可能なチーム名が無い（name_ja=null かつ name_en=slug） |  |  |
| warn | teams/mlr.json | ca-legion | 表示可能なチーム名が無い（name_ja=null かつ name_en=slug） |  |  |
| warn | teams/mlr.json | chicago | 表示可能なチーム名が無い（name_ja=null かつ name_en=slug） |  |  |
| warn | teams/mlr.json | new-england-free-jacks | 表示可能なチーム名が無い（name_ja=null かつ name_en=slug） |  |  |
| warn | teams/mlr.json | old-glory | 表示可能なチーム名が無い（name_ja=null かつ name_en=slug） |  |  |
| warn | teams/mlr.json | seattle-seawolves | 表示可能なチーム名が無い（name_ja=null かつ name_en=slug） |  |  |
| warn | teams/super-rugby.json | blues | 表示可能なチーム名が無い（name_ja=null かつ name_en=slug） |  |  |
| warn | teams/super-rugby.json | brumbies | 表示可能なチーム名が無い（name_ja=null かつ name_en=slug） |  |  |
| warn | teams/super-rugby.json | chiefs | 表示可能なチーム名が無い（name_ja=null かつ name_en=slug） |  |  |
| warn | teams/super-rugby.json | crusaders | 表示可能なチーム名が無い（name_ja=null かつ name_en=slug） |  |  |
| warn | teams/super-rugby.json | fijian-drua | 表示可能なチーム名が無い（name_ja=null かつ name_en=slug） |  |  |
| warn | teams/super-rugby.json | highlanders | 表示可能なチーム名が無い（name_ja=null かつ name_en=slug） |  |  |
| warn | teams/super-rugby.json | hurricanes | 表示可能なチーム名が無い（name_ja=null かつ name_en=slug） |  |  |
| warn | teams/super-rugby.json | moana-pasifika | 表示可能なチーム名が無い（name_ja=null かつ name_en=slug） |  |  |
| warn | teams/super-rugby.json | reds | 表示可能なチーム名が無い（name_ja=null かつ name_en=slug） |  |  |
| warn | teams/super-rugby.json | waratahs | 表示可能なチーム名が無い（name_ja=null かつ name_en=slug） |  |  |
| warn | teams/super-rugby.json | western-force | 表示可能なチーム名が無い（name_ja=null かつ name_en=slug） |  |  |

## team_name_placeholder（17件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| warn | teams/mlr.json | anthem-rc | name_en='anthem-rc' が id slug と同一（正式名未取得） | 公式表記をソースから取得（推測で埋めない） | 要 |
| warn | teams/mlr.json | ca-legion | name_en='ca-legion' が id slug と同一（正式名未取得） | 公式表記をソースから取得（推測で埋めない） | 要 |
| warn | teams/mlr.json | chicago | name_en='chicago' が id slug と同一（正式名未取得） | 公式表記をソースから取得（推測で埋めない） | 要 |
| warn | teams/mlr.json | new-england-free-jacks | name_en='new-england-free-jacks' が id slug と同一（正式名未取得） | 公式表記をソースから取得（推測で埋めない） | 要 |
| warn | teams/mlr.json | old-glory | name_en='old-glory' が id slug と同一（正式名未取得） | 公式表記をソースから取得（推測で埋めない） | 要 |
| warn | teams/mlr.json | seattle-seawolves | name_en='seattle-seawolves' が id slug と同一（正式名未取得） | 公式表記をソースから取得（推測で埋めない） | 要 |
| warn | teams/super-rugby.json | blues | name_en='blues' が id slug と同一（正式名未取得） | 公式表記をソースから取得（推測で埋めない） | 要 |
| warn | teams/super-rugby.json | brumbies | name_en='brumbies' が id slug と同一（正式名未取得） | 公式表記をソースから取得（推測で埋めない） | 要 |
| warn | teams/super-rugby.json | chiefs | name_en='chiefs' が id slug と同一（正式名未取得） | 公式表記をソースから取得（推測で埋めない） | 要 |
| warn | teams/super-rugby.json | crusaders | name_en='crusaders' が id slug と同一（正式名未取得） | 公式表記をソースから取得（推測で埋めない） | 要 |
| warn | teams/super-rugby.json | fijian-drua | name_en='fijian-drua' が id slug と同一（正式名未取得） | 公式表記をソースから取得（推測で埋めない） | 要 |
| warn | teams/super-rugby.json | highlanders | name_en='highlanders' が id slug と同一（正式名未取得） | 公式表記をソースから取得（推測で埋めない） | 要 |
| warn | teams/super-rugby.json | hurricanes | name_en='hurricanes' が id slug と同一（正式名未取得） | 公式表記をソースから取得（推測で埋めない） | 要 |
| warn | teams/super-rugby.json | moana-pasifika | name_en='moana-pasifika' が id slug と同一（正式名未取得） | 公式表記をソースから取得（推測で埋めない） | 要 |
| warn | teams/super-rugby.json | reds | name_en='reds' が id slug と同一（正式名未取得） | 公式表記をソースから取得（推測で埋めない） | 要 |
| warn | teams/super-rugby.json | waratahs | name_en='waratahs' が id slug と同一（正式名未取得） | 公式表記をソースから取得（推測で埋めない） | 要 |
| warn | teams/super-rugby.json | western-force | name_en='western-force' が id slug と同一（正式名未取得） | 公式表記をソースから取得（推測で埋めない） | 要 |

## callup_missing（1件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| info | callups/national.json | callup_national_54111 | kind=tour で start_date/venue が null |  |  |

## caps_nationality（35件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| info | players/league-one-d1.json | lo_announced_hunter-paisami | caps.team='Australia' が nationality=['Samoa'] に含まれない |  |  |
| info | players/national.json | ar_aidan-ross | caps.team='Australia' が nationality=['New Zealand'] に含まれない |  |  |
| info | players/national.json | ar_atunaisa-moli | caps.team='Tonga' が nationality=['New Zealand'] に含まれない |  |  |
| info | players/national.json | ar_benjamin-bonasso | caps.team='Usa' が nationality=['Argentina', 'United-States'] に含まれない |  |  |
| info | players/national.json | ar_charlie-abel | caps.team='Usa' が nationality=['Australia', 'United-States'] に含まれない |  |  |
| info | players/national.json | ar_christopher-hilsenbeck | caps.team='Usa' が nationality=['Germany'] に含まれない |  |  |
| info | players/national.json | ar_cory-gilliland-daniel | caps.team='Usa' が nationality=['United-States'] に含まれない |  |  |
| info | players/national.json | ar_dominic-besag | caps.team='Usa' が nationality=['United-States'] に含まれない |  |  |
| info | players/national.json | ar_erich-storti | caps.team='Usa' が nationality=['United-States'] に含まれない |  |  |
| info | players/national.json | ar_ezekiel-lindenmuth | caps.team='Usa' が nationality=['Samoa', 'United-States'] に含まれない |  |  |
| info | players/national.json | ar_jack-dempsey | caps.team='Scotland' が nationality=['Australia'] に含まれない |  |  |
| info | players/national.json | ar_jack-iscaro | caps.team='Usa' が nationality=['United-States'] に含まれない |  |  |
| info | players/national.json | ar_jeffery-toomaga-allen | caps.team='Samoa' が nationality=['New Zealand'] に含まれない |  |  |
| info | players/national.json | ar_joe-taufete-e | caps.team='Usa' が nationality=['United-States'] に含まれない |  |  |
| info | players/national.json | ar_kapeli-pifeleti-jr | caps.team='Usa' が nationality=['Tonga', 'United-States'] に含まれない |  |  |
| info | players/national.json | ar_marno-redelinghuys | caps.team='Usa' が nationality=['South Africa', 'United-States'] に含まれない |  |  |
| info | players/national.json | ar_michelangelo-sosene-feagai | caps.team='Usa' が nationality=['Samoa', 'United-States'] に含まれない |  |  |
| info | players/national.json | ar_mitch-wilson | caps.team='Usa' が nationality=['Australia', 'United-States'] に含まれない |  |  |
| info | players/national.json | ar_paddy-ryan-1998 | caps.team='Usa' が nationality=['Ireland', 'United-States'] に含まれない |  |  |
| info | players/national.json | ar_payton-telea-ilalio | caps.team='Usa' が nationality=['United-States'] に含まれない |  |  |
| info | players/national.json | ar_peter-umaga-jensen | caps.team='Samoa' が nationality=['New Zealand'] に含まれない |  |  |
| info | players/national.json | ar_pita-anae-ah-sue | caps.team='Samoa' が nationality=['New Zealand', 'Australia'] に含まれない |  |  |
| info | players/national.json | ar_pono-davis | caps.team='Usa' が nationality=['United-States'] に含まれない |  |  |
| info | players/national.json | ar_ruben-de-haas | caps.team='Usa' が nationality=['South Africa', 'United-States'] に含まれない |  |  |
| info | players/national.json | ar_rufus-mclean | caps.team='Usa' が nationality=['United-States', 'Scotland'] に含まれない |  |  |
| info | players/national.json | ar_sam-golla | caps.team='Usa' が nationality=['United-States'] に含まれない |  |  |
| info | players/national.json | ar_scott-sio | caps.team='Samoa' が nationality=['Australia'] に含まれない |  |  |
| info | players/national.json | ar_shilo-klein | caps.team='Usa' が nationality=['United-States'] に含まれない |  |  |
| info | players/national.json | ar_tavite-lopeti | caps.team='Usa' が nationality=['United-States'] に含まれない |  |  |
| info | players/national.json | ar_tevita-naqali | caps.team='Usa' が nationality=['Fiji', 'United-States'] に含まれない |  |  |
| info | players/national.json | ar_titi-lamositele | caps.team='Samoa' が nationality=['United-States'] に含まれない |  |  |
| info | players/national.json | ar_toby-fricker | caps.team='Usa' が nationality=['Wales', 'United-States'] に含まれない |  |  |
| info | players/national.json | ar_tommaso-boni | caps.team='Usa' が nationality=['Italy'] に含まれない |  |  |
| info | players/national.json | ar_tonga-kofe | caps.team='Usa' が nationality=['United-States'] に含まれない |  |  |
| info | players/national.json | ar_vili-helu | caps.team='Usa' が nationality=['United-States'] に含まれない |  |  |

## episode_source_domain（44件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| info | players/episodes/ar_naoto-saito.json | ar_naoto-saito#0 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/ar_naoto-saito.json | ar_naoto-saito#1 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/ar_naoto-saito.json | ar_naoto-saito#2 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/ar_naoto-saito.json | ar_naoto-saito#3 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/ar_naoto-saito.json | ar_naoto-saito#4 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/ar_naoto-saito.json | ar_naoto-saito#5 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/ar_naoto-saito.json | ar_naoto-saito#6 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/ar_naoto-saito.json | ar_naoto-saito#7 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/ar_naoto-saito.json | ar_naoto-saito#8 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/ar_naoto-saito.json | ar_naoto-saito#9 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/jrfu_callup_ruan-botha.json | jrfu_callup_ruan-botha#0 | source_url ドメイン www.kubota-spears.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/jrfu_callup_ruan-botha.json | jrfu_callup_ruan-botha#1 | source_url ドメイン www.kubota-spears.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/jrfu_callup_ruan-botha.json | jrfu_callup_ruan-botha#2 | source_url ドメイン www.kubota-spears.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/jrfu_callup_ruan-botha.json | jrfu_callup_ruan-botha#3 | source_url ドメイン www.kubota-spears.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/jrfu_callup_ruan-botha.json | jrfu_callup_ruan-botha#4 | source_url ドメイン www.kubota-spears.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/jrfu_u23_497504.json | jrfu_u23_497504#0 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/jrfu_u23_497504.json | jrfu_u23_497504#1 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/jrfu_u23_497504.json | jrfu_u23_497504#2 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/jrfu_u23_497504.json | jrfu_u23_497504#3 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/jrfu_u23_497504.json | jrfu_u23_497504#4 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/jrfu_u23_497504.json | jrfu_u23_497504#5 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/jrfu_u23_497504.json | jrfu_u23_497504#6 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/lo_485712.json | lo_485712#0 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/lo_485712.json | lo_485712#1 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/lo_485712.json | lo_485712#2 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/lo_485712.json | lo_485712#3 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/lo_485712.json | lo_485712#4 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/lo_485712.json | lo_485712#5 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/lo_485712.json | lo_485712#6 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/lo_485712.json | lo_485712#7 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/lo_485712.json | lo_485712#8 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/lo_485712.json | lo_485712#9 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/univ_早稲田大学__矢崎由高.json | univ_早稲田大学__矢崎由高#0 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/univ_早稲田大学__矢崎由高.json | univ_早稲田大学__矢崎由高#1 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/univ_早稲田大学__矢崎由高.json | univ_早稲田大学__矢崎由高#10 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/univ_早稲田大学__矢崎由高.json | univ_早稲田大学__矢崎由高#12 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/univ_早稲田大学__矢崎由高.json | univ_早稲田大学__矢崎由高#2 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/univ_早稲田大学__矢崎由高.json | univ_早稲田大学__矢崎由高#3 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/univ_早稲田大学__矢崎由高.json | univ_早稲田大学__矢崎由高#4 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/univ_早稲田大学__矢崎由高.json | univ_早稲田大学__矢崎由高#5 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/univ_早稲田大学__矢崎由高.json | univ_早稲田大学__矢崎由高#6 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/univ_早稲田大学__矢崎由高.json | univ_早稲田大学__矢崎由高#7 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/univ_早稲田大学__矢崎由高.json | univ_早稲田大学__矢崎由高#8 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |
| info | players/episodes/univ_早稲田大学__矢崎由高.json | univ_早稲田大学__矢崎由高#9 | source_url ドメイン rugby-rp.com は ALLOWED_DOMAINS 外（03の許可リスト） | エピソードに許可リストを適用するか運用方針を人間が決定 |  |

## kana_override_ref（74件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| info | manual/kana_overrides.json | ar_akato-fakatika | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_alex-newsome | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_alovisio-kolivai | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_antoine-tichit | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_arno-botha | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_atu-manu | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_aubin-cazaubon | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_aymeric-luc | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_baptiste-chouzenoux | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_bobby-bissu | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_carwyn-tuipulotu | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_charles-laloi | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_charlesty-berguet | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_cyril-blanchard | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_enzo-herve | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_etienne-falgoux | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_feleti-kaitu-u | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_francis-saili | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_gabin-kretchmann | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_gael-galvan | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_gwenael-duplenne | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_irae-simone | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_ismael-faleyras | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_james-o-reilly | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_jermaine-ainsley | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_job-poulet | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_jordan-petaia | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_joseph-laharrague | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_jules-le-bail | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_julien-catala | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_kane-douglas | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_kitione-kamikamica | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_kleo-labarbe | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_leone-nakarawa | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_lino-julien | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_lucas-dessaigne | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_luke-whitelock | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_mahamadou-diaby | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_malo-malval | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_marco-tauleigne | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_matteo-samyn | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_noa-zinzen | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_olivier-klemenczak | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_paga-tafili | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_paul-jedrasiak | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_paul-rocher | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_pierre-fouyssac | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_reece-hodge | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_richard-judd | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_rob-simmons | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_romain-macurdy | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_sacha-benoit | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_seilala-lam | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_suliasi-vunivalu | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_tavite-veredamu | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_theo-roucayrol | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_thibault-debaes | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_thomas-carol | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_thomas-darmon | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_thomas-duchene | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_thomas-vincent | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_tom-raffy | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_tom-sarthou | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_tom-whorrod | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_ultan-dillane | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_victor-hannoun | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_vincent-rattez | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_will-rowlands | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | ar_yanis-lux | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | lo_160 | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | lo_390 | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | lo_484385 | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | lo_484810 | 対象 id が master に無い（離脱/マージ済み） |  |  |
| info | manual/kana_overrides.json | lo_790 | 対象 id が master に無い（離脱/マージ済み） |  |  |

## name_sep_mixed（3件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| info | players/league-one-d1.json | league-one-d1 | カタカナ名の区切り記号が混在: {'・': 252, '空白': 23} |  |  |
| info | players/league-one-d2.json | league-one-d2 | カタカナ名の区切り記号が混在: {'・': 101, '空白': 9} |  |  |
| info | players/league-one-d3.json | league-one-d3 | カタカナ名の区切り記号が混在: {'・': 41, '空白': 3} |  |  |

## standings_played_spread（1件）

| sev | file | target | 内容 | 修正案 | 公式確認 |
|---|---|---|---|---|---|
| info | standings/super-rugby_unknown.json | super-rugby_unknown | played の分布 {12: 9, 13: 2} | 試合消化数が揃わない（延期・未消化）可能性。最終順位なら要確認 | 要 |

