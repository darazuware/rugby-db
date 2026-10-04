# T7 アフィリエイト導入

## 実装済み
- `src/components/AffiliateSlot.astro`：`kind` = `watch`（配信）/ `gear`（用品）/ `travel`（旅行）。**ASPリンク未設定なら枠ごと非表示**。PR表記・`rel="sponsored noopener"` 付き
- リンクは `src/lib/affiliates.ts` の `ASP_LINKS`（空文字）にユーザーが貼る。AIは実リンクを書かない
- 自動挿入：ニュース記事 slug が `-review` で終わる試合レビュー記事の末尾（`pages/news/[slug].astro`）／試合結果ページ `/results` のヘッダー（配信 J SPORTS・DAZN のみ）
- 既存の WatchButton / OverseasTravelButtons / AccommodationButton（公式サイトリンク）は別系統として維持
- 賭博系（ブックメーカー・toto等）は扱わない

## 特集記事の構成案（執筆は次タスク。事実は公式ソース確認必須）

### 1. RWC2027 観戦ガイド（オーストラリア）— slug案 `rwc2027-travel-guide`
| 章 | 内容 | 確認が必要な事実（公式ソース） | 枠 |
|---|---|---|---|
| 導入 | 日本代表のプールE試合日程・会場 | data/manual/rwc2027.json（出典 rugbyworldcup.com）を再確認 | — |
| 渡航準備 | 日本→豪州のビザ（ETA）要件・パスポート残存期間 | 豪州内務省 公式 | — |
| 航空券 | 直行便の有無・所要時間・早期予約の考え方 | 各航空会社公式（断定せず「確認を」） | travel: skyticket/Expedia |
| 宿 | 開催都市別エリア選び・試合日の混雑 | 公式チケット/会場情報 | travel: Agoda/Booking.com |
| 通信 | 海外Wi-Fi・eSIM比較 | 各社公式料金 | travel: travel-wifi |
| 保険 | 海外旅行保険の補償項目の見方 | 各社約款 | travel: travel-insurance |
| チケット | 公式販売ルート・転売注意 | rugbyworldcup.com 公式 | 内部リンク |

### 2. 試合の視聴方法ガイド（既存 `how-to-watch-overseas-rugby` の補強 or 新規）— slug案 `how-to-watch-japan-tests`
- 日本代表テストマッチ／リーグワン／TOP14／スーパーラグビー別の視聴先表（既存記事の表と整合）
- 放映権は年度で変わるため各社公式で最新確認、更新日を明記
- 枠：watch（J SPORTS・DAZN・WOWOW）。VPN記事は docs/renewal/07 の注意事項どおり、扱う場合は draft→ユーザー確認

### 3. ポジション別 用品選び — slug案 `rugby-gear-by-position`
- FW（PR/HO/LO/FL/No8）：スクラム・ラインアウト向けスパイク（固定式ポイントの考え方）、プロテイン、サポーター
- BK（SH/SO/CTB/WTB/FB）：軽量スパイク、ボール（サイズ4/5）、グローブ
- 製品の性能・価格は書かず、選び方の基準中心。具体商品は公式スペック確認後
- 枠：gear（Amazon/楽天）

## ユーザー作業（ASP登録）
1. A8.net 無料登録 → 「skyticket」「Expedia」「Agoda」「Booking.com」「海外Wi-Fi」「海外旅行保険」等の提携申請
2. もしもアフィリエイト 登録 → Amazon・楽天の物販提携（用品用）
3. DAZN・J SPORTS 等の配信提携（A8.net/もしも内で検索）
4. 承認後、発行された広告リンクを `src/lib/affiliates.ts` の `ASP_LINKS` に貼る（貼り方はClaudeに依頼すれば代行）
- 注意：AdSense審査中は提携申請のみ先行でも可。リンク掲載は審査後でも問題なし
