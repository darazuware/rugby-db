# AdSense合格・収益化 タスクチェーン

使い方：新チャットでモデルを切り替え、該当タスクの「プロンプト」をそのまま貼る。

## 共通ルール（全タスクのプロンプトに含意）
- CLAUDE.md・docs/renewal/03_VALIDATION.md を厳守（事実をAIの知識で書かない／data/master は pipeline/ 以外から書き換え禁止）
- 監査結果（2026-10-04）：サイトマップ7,188URL中6,797件(95%)が選手ページ。中身は身長体重出身校のみ＝AdSense「有用性の低いコンテンツ」の主因。1,000字未満ニュース154本（例: mlr-join-*、*-join-lo_*）。age固定値が古い。運営者情報が匿名「運営事務局」。トップtitleが「名鑑データベース」。
- 完了条件：①作業を本番反映（commit/push）②このファイルの自タスクに「✅完了日＋結果1行」を追記 ③次タスクのプロンプトを結果に合わせて更新 ④チャット末尾に「次のプロンプト全文」と「推奨モデル」を出力 ⑤Telegramに要約送信（python3.11 -m pipeline.telegram_notify send --text "..."）

---

## T1 名鑑の線引きとサイト構成設計【Opus 高】
状態：✅完了 2026-10-04 — 個別ページ6,738→315人（代表/招集・エピソード/IG・記事2本以上言及）、残りはチーム名簿アンカーへ301、ar_/lo_重複44件統合、年齢はbirthdate計算に統一。詳細 docs/adsense/01_DESIGN.md

プロンプト：
```
docs/adsense/TASKS.md の共通ルールとT1を読んで実行して。
目的：AdSense合格のため選手名鑑を縮小する設計を決める（実装はしない）。
やること：
1. src/content/players（約5,400件）と src/pages/players, src/pages/teams の構造を把握
2. 個別ページを残す選手の基準を決める（例：日本代表・代表候補・注目選手、解説文を書ける根拠データがある者）。対象人数を実データで算出
3. 残さない選手の扱いを決める：チームページ内の名簿表へ統合＋個別URLは noindex か 301リダイレクトか削除か。SEO・既存内部リンク（scripts/link_news.py の自動リンク）への影響も含めて判断
4. age固定値→birth_dateから自動計算する方針
5. 結果を docs/adsense/01_DESIGN.md に書く（対象リスト抽出条件・URL処理方針・変更ファイル一覧・T2の作業手順）
完了したら共通ルールの完了条件どおりに終える（今回commitは設計書のみ）。
```

## T2 名鑑縮小の実装【Sonnet 中】
状態：✅完了 2026-10-04 — 個別ページ6,738→260人（K1〜K3＋force1、-96%。設計の約315人から-17%：週次キャップ一覧記事 `*-caps-weekly-*` をK3から除外したため。含めると467人）、サイトマップ7,188→654URL（/players/ 261）。ar_→lo_重複を計40件統合、非対象選手は301でチーム名簿 #p-{slug} へ、チーム名簿は表形式、/players は注目選手一覧、年齢は全てbirthdateから計算、記事リンク約1,900件を書換え。vitestは既存の4件失敗のみ（baselineと同一）

プロンプト：
```
docs/adsense/TASKS.md の共通ルールとT2、docs/adsense/01_DESIGN.md を読んで、§5「T2作業手順」の1〜9どおりに実装して。
要点：
1. scripts/build_player_pages.py で data/manual/player_pages.json を生成（基準K1〜K3、約315人。大きくずれたら原因を報告）。ar_→lo_ 重複44件は一覧を目視確認してから data/manual/player_merges.json に追加
2. master.ts に isIndexablePlayer / playerHref / playerFallbackPath を追加し canHaveIndividualPlayerPage を変更。非indexable・統合slugは middleware でチーム名簿アンカー（/teams/{league}/{team}/#p-{slug}）へ301
3. チームページ名簿を表形式（名前・ポジション・出身校・年齢）＋行アンカー化、/players を注目選手一覧に。選手リンク生成箇所はすべて playerHref に置換
4. 年齢は birthdate から calcAge で計算（React 3コンポーネント・API含む。age固定値は使わない）
5. link_news.py に辞書限定と --fix-dead を追加して既存記事リンクを書換え、pipeline/news_gen.py・episodes.py・monitor_news CI も対応
6. vitest・astro build 成功、サイトマップ /players/ 約315件・総約700URL、301動作と主要ページをブラウザで確認
完了したら共通ルールの完了条件どおりに終える。
```

## T3 短信ニュースの統合【Sonnet 中】
状態：✅完了 2026-10-04 — 公開中の短信77本を月次まとめ3本（transfers-roundup-2026-07/08/09）に統合、旧URLは data/redirects.json で301。pipeline/news_rollup.py を news_gen 末尾に接続し今後は追記方式。個別ページ選手 260→276人（まとめ記事の言及で昇格）。7月まとめのみ約700字。draft 92本・手書き短め記事は未対象

プロンプト：
```
docs/adsense/TASKS.md の共通ルールとT3を読んで実行して。
前提（T2完了後）：個別ページ選手は data/manual/player_pages.json（scripts/build_player_pages.py 生成）。記事を統合・削除すると言及数が変わるので、完了前に必ず `python3 scripts/build_player_pages.py` を再実行して差分（昇格・降格した選手）を確認し、`python3 scripts/link_news.py --fix-dead --write` で記事内の選手リンクを整合させる。削除する短信内の `/players/` や `#p-` リンクも言及数に含まれる点に注意。
やること：
1. src/content/news で本文1,000字未満の記事を一覧化（加入・退団等の1行記事が中心）
2. 週単位またはリーグ単位の「移籍まとめ」記事に統合（事実は元記事と source_diff の範囲のみ、AI知識で追記しない）。各まとめ記事に独自の見どころ考察を加え1本2,000字以上を目安
3. 元の短信は削除し、URLはまとめ記事へ301リダイレクト（vercel.json）
4. 今後 pipeline が1行記事を量産しないよう、生成側を「まとめ記事へ追記」方式に変更（pipeline/ を調査して最小変更）
5. ビルド・リダイレクト動作確認
完了したら共通ルールの完了条件どおりに終える。
```

## T4 運営者情報・サイトの見せ方【Sonnet 中】
状態：✅完了 2026-10-05 — about に運営者プロフィール（プレー歴10年+草2年・観戦歴・推しMLR、個人運営）、記事に筆者欄 AuthorBox＋JSON-LD author、トップ title/description/ヒーローをメディア寄りに、ナビはニュース先頭・名鑑を後ろへ

プロンプト：
```
docs/adsense/TASKS.md の共通ルールとT4を読んで実行して。
やること：
1. 運営者名（ハンドル）・プロフィール・ラグビーとの関わりをユーザーにTelegramボタン/質問で確認（memory: feedback_ask_via_telegram）。個人情報（本名・住所）は求めない
2. src/pages/about.astro の運営者情報を更新
3. 記事ページに筆者欄を追加
4. トップのtitle/descriptionを「日本語で読むラグビーメディア」寄りに変更（名鑑DB色を薄める）
5. ナビから名鑑導線の比重を下げ、記事・特集を前面に
6. ブラウザで表示確認
完了したら共通ルールの完了条件どおりに終える。
```

## T5 機械チェック【Haiku 低】
状態：✅完了 2026-10-05 — 本番600URL全スキャン、404/リダイレクトループ/noindex問題0件

プロンプト：
```
docs/adsense/TASKS.md の共通ルールとT5を読んで実行して。コード修正はしない、調査と報告のみ。
やること：
1. 本番 https://rugbypick.com/sitemap-index.xml の全URLにアクセスし、404・リダイレクトループ・noindexなのにサイトマップ掲載、を検出
2. 記事内リンク切れを検出
3. 結果を docs/adsense/05_CHECK.md に一覧化
問題が0件なら次はT6、問題があれば次タスクを「T5修正【Sonnet 中】」としてプロンプトを書いて終える。
完了したら共通ルールの完了条件どおりに終える。
```

## T6 再申請前の最終監査【Opus 中】
状態：✅完了 2026-10-05 — 再申請不可。サイトマップ600URL中345件(57%)が本文800字未満（選手271/277・チーム58/150）。運営者情報・ポリシー・ads.txt・モバイルは合格。詳細 docs/adsense/06_AUDIT.md → T6修正へ

プロンプト：
```
docs/adsense/TASKS.md の共通ルールとT6を読んで実行して。
やること：
1. 本番サイトをAdSense審査官視点で監査（低品質ページ比率、オリジナリティ、運営者情報、ポリシー、ナビ、広告配置、モバイル表示）
2. 残課題があれば修正タスクを作り TASKS.md に追加
3. 問題なければ「Search Console でインデックス反映を確認→2〜4週間後に再申請」をユーザーにTelegramで通知し、再申請手順（ユーザー操作）を平易に1〜3行で示す
完了したら共通ルールの完了条件どおりに終える（次はT7）。
```

## T6修正 薄いページのnoindex化・統合【Sonnet 中】
状態：✅完了 2026-10-05 — 選手263人・チーム56件・dream-team/magazine/notice/sitemapをnoindex＋サイトマップ除外（thin_pages.json、scripts/build_thin_pages.py）、短信5本＋7月まとめを8/9月まとめへ統合301。本番再計測：サイトマップ600→270URL、800字未満14件=5.2%（≦10%達成）。計測 docs/adsense/06_audit_textlen_after.tsv。次＝Search Console反映確認→2〜4週間後に再申請（T7並行可）

プロンプト：
```
docs/adsense/TASKS.md の共通ルールとT6修正、docs/adsense/06_AUDIT.md・06_audit_textlen.tsv を読んで実行して。
目的：サイトマップ内の本文800字未満ページを10%以下にする（現状345/600）。
やること：
1. 選手ページ：AI知識で解説を書くのは禁止。代わりに「独自本文（エピソード・記事言及の要約等、既存データ由来）が一定量ある選手」だけ index、それ以外は個別ページを残したまま <meta name="robots" content="noindex,follow"> ＋サイトマップ除外（astro.config の sitemap filter／master.ts に isIndexablePlayer とは別の判定を追加）。リンク・301構造は変えない
2. チームページ：名簿が空 or 本文800字未満（高校・大学・トップイースト/ウエスト/九州の約58件）を noindex＋サイトマップ除外。リーグ一覧からのリンクは残す
3. ニュース1,000字未満9本：transfers-roundup-2026-07 は8月まとめへ統合して301、残りは既存事実の範囲で加筆するか統合。*-join-weekly-* は月次まとめへ寄せる
4. dream-team・magazine・notice/*・sitemap(HTML) は noindex
5. 再計測：本番反映後に docs/adsense/06_AUDIT.md と同じ方法（<main>内テキスト長）でサイトマップ全URLを測り、800字未満比率を記録。10%以下なら次は「再申請」、超えたら原因と追加タスクを書く
完了したら共通ルールの完了条件どおりに終える（次はT7。10%以下達成時はTelegramで「Search Consoleでインデックス反映確認→2〜4週間後に再申請」を通知）。
```

## T7 アフィリエイト導入【Sonnet 中】
状態：未着手

プロンプト：
```
docs/adsense/TASKS.md の共通ルールとT7を読んで実行して。
やること：
1. アフィリエイト枠コンポーネントを作成（配信サービス枠・用品枠・旅行枠）。ASPのリンクIDはユーザー登録後に差し替える前提でプレースホルダ化し、未設定なら非表示
2. 試合結果記事・日程ページに「配信サービス」枠を自動挿入
3. 特集記事の構成案を docs/adsense/07_AFFILIATE.md に作成：RWC2027観戦ガイド（オーストラリア渡航・航空券・宿・Wi-Fi・保険）、試合の視聴方法、ポジション別用品選び。大会日程等の事実は公式ソース確認必須
4. 必要なASP登録（A8.net・もしも等）をユーザー操作として平易に列挙しTelegram送信
5. 賭博系は扱わない
完了したら共通ルールの完了条件どおりに終える（次タスクは特集記事執筆【Sonnet 中】として作成）。
```
