"""P5-5: 大学ラグビー部員名簿スクレイパー（10_YOUTH_AGEGRADE.md 大学スコープ / 02_SCRAPERS.md）。

対象6区分: 関東大学対抗戦A/B・関東大学リーグ戦1部/2部・関西大学A/Bリーグ。

所属校の一覧は各連盟公式サイトの実ページで確認した（2026-07-18）:
  - 関東対抗戦A/B・リーグ戦1部/2部: 関東ラグビーフットボール協会 www.rugby.or.jp の
    直近シーズン星取表（/univ/sheet/{id}/）。各校の公式サイトURLは関東大学ラグビー
    フットボール連盟 www.kurfa.org/team/ のチーム一覧（1部/2部は同じ16校の入れ替え
    のみで対抗戦とは独立集計のため、対抗戦A/Bの8校×2はチーム一覧に無く個別検索で
    確認した）。
  - 関西A/B: 関西ラグビーフットボール協会 rugby-kansai.or.jp/gameuniversity の
    2026年度シーズン日程（A/Bとも8校）。各校公式サイトURLは個別に実在確認した。
連盟サイト自体は日程・星取表のみで部員名簿を持たないため、名簿は各校公式サイトから
取得する（02の想定通り「各連盟公式 + 大学部公式サイト」）。

各校公式サイトはHTML構造が統一されていない（自作/WordPress/Wix/r-cms.jp等バラバラ）。
_extract_records() は「かな氏名の行」を手がかりに前後数行を探索し、漢字氏名・学年・
ポジション・出身高校・身長体重（公式サイトが記載している場合のみ）を拾う汎用スキャナで
抽出する。かな氏名+漢字氏名の組が拾えても学年・ポジションのどちらも伴わない場合は
信頼度不足として捨てる（00原則3: 迷ったら null/スキップ）。

十分な件数（_MIN_CONFIDENT件）が正規表現で拾えたチームはそのまま採用し、拾えなかった
チームのみ pipeline.llm_fallback.extract_roster_members() にページ本文プレーンテキスト
を渡す（02:「抽出失敗時のみSonnetに粗抽出ブロックだけ渡す」の踏襲）。

実データで確認済みの既知の失敗パターン（2026-07-18）。偽データは作らず warning に残す:
  - Wix/React等クライアントサイド描画のサイト（立教大学、筑波大学の一部）は
    requests での静的取得では本文が空になる。
  - 中央大学 curfcsc.jp・拓殖大学 takushoku-rugby.com・白鷗大学 hakuoh-rugby.com・
    追手門学院大学 otemongakuinrfc.com は名前解決不可（サイト消滅/移転の可能性）。
  - 日本大学等、部員一覧がJSでの絞り込みUI経由でのみ描画されるサイトは静的取得では
    フィルタ用の見出し語しか取れない。
  - 国士舘大学は公式サイトが個人ブログ(ameblo.jp)のみで安定した名簿ページが無いため
    DIVISIONS に含めない（対象外）。

学年(grade)は取得できるが生年月日は取得しない・掲載しない（10: 学生は成人でも生年月日
禁止、学年のみ）。身長体重は各校サイトが名簿ページ自体に明記している場合のみ拾う
（10:「身長体重...大学以上は公式発表分のみ」）。SNS・写真は一切収集しない。
"""
from __future__ import annotations

import re
import time
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from pipeline import llm_fallback
from pipeline.transform import normalize

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
_SLEEP = 1.5
_TIMEOUT = 15
_RETRIES = 2
_MIN_CONFIDENT = 5  # これ未満なら regex 結果を信頼せず LLM フォールバックに回す

# division key -> (label, 連盟公式ソース(所属校一覧の根拠), [(校名, 部員名簿URL), ...])
# 校名・URLは実ページで到達性を確認済み（2026-07-18、fetch_status確認）。
DIVISIONS: dict[str, dict] = {
    "kanto_taikosen_a": {
        "label": "関東大学対抗戦Aグループ",
        "source_url": "https://www.rugby.or.jp/univ/sheet/2651/",
        "teams": [
            ("早稲田大学", "https://www.wasedarugby.com/list/member/"),
            ("帝京大学", "https://www.teikyo-sports.jp/rugby/member/"),
            ("明治大学", "https://www.meijirugby.jp/players/"),
            ("慶應義塾大学", "https://keiorugby.com/team/team_cat/player/"),
            ("青山学院大学", "https://www.aogaku-rugby.com/member_list/"),
            # 旧 tsa.tsukuba.ac.jp/rugby/member/ は接続不可（2026-08-11確認）。
            # 筑波大学体育スポーツ局の共通ポータルに掲載場所が移っている。
            ("筑波大学", "https://www.tsukubaowls.com/member/rugby"),
            ("立教大学", "https://www.rikkyo-rugby.com/member"),
            ("日本体育大学", "https://nssurfc.jp/member/"),
        ],
    },
    "kanto_taikosen_b": {
        "label": "関東大学対抗戦Bグループ",
        "source_url": "https://www.rugby.or.jp/univ/sheet/2667/",
        "teams": [
            ("成蹊大学", "https://www.seikeiruggerclub.com/member_list/"),
            # 旧 /member_list/ は実質空ページ（2026-08-12確認）。/player/ に移行。
            ("明治学院大学", "https://www.mgurfc.com/player/"),
            ("武蔵大学", "https://musashi-rugby.net/member/"),
            ("東京大学", "https://www.turfc.com/member_list/"),
            ("上智大学", "https://sophia-rugby.com/player"),
            ("成城大学", "https://www.seijorugby.com/"),
            ("一橋大学", "https://hurfc.jp/member/"),
            ("学習院大学", "https://www.gakushuin-rugby.com/member/"),
        ],
    },
    "kanto_league_1": {
        "label": "関東大学リーグ戦1部",
        "source_url": "https://www.rugby.or.jp/univ/sheet/2652/",
        "teams": [
            # 旧 daito-rfc.com は実質空ページ（2026-08-12確認）。daitorugby.com に移行。
            ("大東文化大学", "https://daitorugby.com/members/"),
            ("東洋大学", "https://toyorugby.com/category/member/"),
            ("東海大学", "http://seagales.com/member/"),
            # トップページには一覧が無く、profile1.html に全部員のプロフィールが
            # まとまっている（2026-08-12確認）。
            ("流通経済大学", "https://rku-rugby.jp/profile1.html"),
            ("法政大学", "https://hosei-rugby.org/"),
            ("立正大学", "http://www.ris.ac.jp/sports/rugby/index.html"),
            ("日本大学", "http://www.nurfc.net/member/"),
            ("関東学院大学", "http://www.kgu-rugby.net/"),
        ],
    },
    "kanto_league_2": {
        "label": "関東大学リーグ戦2部",
        "source_url": "https://www.rugby.or.jp/univ/sheet/2668/",
        "teams": [
            ("中央大学", "http://www.curfcsc.jp/"),
            ("専修大学", "http://www.senshurugby.com/"),
            ("山梨学院大学", "http://www.ygu.ac.jp/sports/rugby/"),
            ("拓殖大学", "http://www.takushoku-rugby.com/"),
            ("白鷗大学", "http://hakuoh-rugby.com/"),
            ("國學院大學", "http://kokugakuinrugby.com/archives/members/4th"),
            ("朝鮮大学校", "http://krurfc.d2.r-cms.jp/member_list/"),
            # 国士舘大学: 公式サイトが個人ブログ(ameblo.jp)のみのため対象外（本文冒頭参照）
        ],
    },
    "kansai_a": {
        "label": "関西大学Aリーグ",
        "source_url": "https://rugby-kansai.or.jp/gameuniversity",
        "teams": [
            ("立命館大学", "https://www.ritsumeirugby.com/member/"),
            ("京都産業大学", "https://www.cc.kyoto-su.ac.jp/circle/rugby/pg22.html"),
            ("摂南大学", "https://setsunan-rugby.com/"),
            ("天理大学", "https://rugby.tenri-u.net/player4/"),
            ("関西大学", "https://kandairugby.com/member.php"),
            ("同志社大学", "https://www.doshisha-rugby.com/member"),
            ("近畿大学", "https://kindai-rugby.jp/members"),
            ("関西学院大学", "https://www.kgrfc.net/member_list/"),
        ],
    },
    "kansai_b": {
        "label": "関西大学Bリーグ",
        "source_url": "https://rugby-kansai.or.jp/gameuniversity",
        "teams": [
            ("大阪体育大学", "https://www.ouhs.jp/ouhs-athletics/rugby/"),
            ("京都大学", "https://www.kiurfc.com/player"),
            ("甲南大学", "https://konan-rugby.com/member.html"),
            ("大阪経済大学", "http://ouerugby.o-oku.jp/"),
            ("龍谷大学", "https://ryukoku-univ-rugby.com/memberprofile/"),
            ("大阪国際大学", "https://oiu-rugby.com/members"),
            ("追手門学院大学", "https://www.otemongakuinrfc.com/"),
            ("大阪産業大学", "https://osu-rugby.jp/"),
        ],
    },
}

# --- 抽出用パターン ---------------------------------------------------------
_POS_TOKENS = r"PR|HO|LO|FL|N[O0]\.?8|SH|SO|CTB|WTB|FB"
# 区切りに「・」も許容（例:「LO・No.8」、実データ確認: 成城大学）。
_POS_RE = re.compile(rf"^({_POS_TOKENS})([\s/／・]+({_POS_TOKENS}))*$", re.I)
# 末尾に $ を付けない: 「2年生 / 桐蔭学園高校」のように学年と出身校が1行に
# まとまっているサイト（慶應義塾大学等、実データ確認）があり、行全体一致だと
# 学年を一切拾えなくなるため先頭一致のみ要求する。「年」単独表記（帝京大学「4年」等、
# 実データ確認）にも対応。1桁の数字直後限定なので「2026年」等の西暦とは衝突しない。
_GRADE_RE = re.compile(r"^([1-4１２３４])\s*(回生|年生|年)(?:[\s　]|$)")
_KANA_RE = re.compile(r"^[ぁ-んァ-ヶー　\s]{3,20}$")
# かな表記の読みが無く、ローマ字氏名（例: "Junnosuke Aoyagi"）を読みとして掲載する
# サイト向けの代替アンカー（実データ確認: 帝京大学）。
_ROMAJI_NAME_RE = re.compile(r"^[A-Z][a-zA-Z'\-]+(?:[\s　]+[A-Z][a-zA-Z'\-]+){1,2}$")
# 「出身校　興国高校」のようなラベル+値も形の上では氏名パターンに一致してしまうため、
# 既知のラベル語で始まる場合は除外する（実データ確認: 立命館大学。誤って選手名として
# 取り込んでいた不正レコードを02発見・修正）。
_KANJI_NAME_RE = re.compile(
    r"^(?!(出身校|出身高校|出身地|出身大学|学年|学部|学科|ポジション|身長|体重)[　 ])"
    r"[一-龥々ヶ]{1,4}[　 ][一-龥々ぁ-んァ-ヶー]{1,8}$"
)
_SCHOOL_RE = re.compile(r"(高等学校|高校|高等部|高等科)$")
# 「学年｜4年」「出身校｜成城学園」のようにラベル+区切り記号(｜:：)+値の形式
# （実データ確認: 成城大学）。値部分だけを取り出して各項目の判定に再利用する。
_LABEL_PREFIX_RE = re.compile(r"^[^\d｜:：/／]{1,8}[｜:：]\s*")
_SCHOOL_LABEL_RE = re.compile(r"^(出身校|出身高校)[｜:：]\s*(.+)$")
_HEIGHT_RE = re.compile(r"(\d{3})\s*(?:cm|㎝)", re.I)
_WEIGHT_RE = re.compile(r"(\d{2,3})\s*(?:kg|㎏)", re.I)


def _strip_label(w: str) -> str:
    """先頭の「ラベル｜」「ラベル:」「ラベル：」を1回だけ取り除く（無ければそのまま）。"""
    return _LABEL_PREFIX_RE.sub("", w, count=1).strip()
# 名前らしく見えても実際は見出し・ラベルであるノイズ（実データ確認で誤検出したもの）
_NAME_STOPWORDS = {"部員 紹介", "部員 一覧", "選手 一覧", "メンバー 紹介", "学年 別", "採用 担当"}
# スタッフ肩書・ポジション名（カタカナ表記）は全てカタカナの行で氏名の読みと
# 区別がつきにくく、表組みのヘッダ行を氏名として誤検出することがある
# （実データ確認: 天理大学の選手一覧テーブルでポジション名カタカナ「プロップ」等が
# かな氏名候補に誤ってヒットし、表ヘッダ「学年」「体重」を漢字氏名として拾ってしまう
# 誤検出を確認した）。かな氏名候補から明示的に除外する。
_KANA_STOPWORDS = {
    "スタッフ", "コーチ", "ヘッドコーチ", "アシスタントコーチ", "チームディレクター",
    "ドクター", "トレーナー", "マネージャー", "アナリスト", "キャプテン",
    "アスレチックトレーナー", "パフォーマンスインテグレーター", "エスアンドシーコーチ",
    "プロップ", "フッカー", "ロック", "フランカー", "ナンバーエイト", "スクラムハーフ",
    "スタンドオフ", "センター", "ウイング", "フルバック", "フォワード", "バックス",
}

_GRADE_INT = {"1": 1, "2": 2, "3": 3, "4": 4, "１": 1, "２": 2, "３": 3, "４": 4}
# 探索幅（ブロック境界検出 _block_bound が主たる安全機構）。前方向は氏名(漢字/かな/
# ローマ字)の相互参照分のみで足りるため狭く保つ（実データ確認: 成城大学で後方に
# 広げすぎるとページ上部のナビ見出し「スタッフ」等を誤って拾ってしまう）。後方向は
# 学年/ポジション/出身校/身長体重が並ぶことが多く、離れたサイトもあるため広めに取る
# （実データ確認: 成城大学は距離6、筑波大学は _extract_records_kanji 側の
# _school_forward_scan でさらに広くカバー）。
_BACK_WINDOW = 3
_FORWARD_WINDOW = 10
_WINDOW = _FORWARD_WINDOW  # _school_forward_scan 等、既存コードとの互換用エイリアス

# --- 個別ページ経由の出身校補完 ---------------------------------------------
# 一覧ページ自体には出身校が載っておらず、選手ごとの個別ページ（例:
# meijirugby.jp/players/detail227/、wasedarugby.com/player/{氏名}/、
# keiorugby.com/team/{数字ID}/、kiurfc.com/player/detail/id/{数字}、
# nssurfc.jp/member/{氏名}/）にのみ記載しているサイトがある（実データ確認:
# 明治大学・早稲田大学・慶應義塾大学・京都大学・日本体育大学）。個別ページのURL形式は
# サイトごとにバラバラ（数字ID/氏名/ネストしたパス等）で全パターンを網羅するのは
# 非現実的なため、URLの形は仮定せず「一覧ページから既に抽出できた選手の漢字氏名が
# アンカーの表示テキストに含まれているか」だけで対応付ける（00原則5: 既知の実在選手名と
# 一致した場合のみ辿るため誤検出リスクが低い）。一致するリンクが1つも無いサイトでは
# 対応表が空になり、追加リクエストは一切発生しない。
# ラベル行のみ（次行が値: 明治大学・京都大学方式。末尾コロンのみ+次行が値: 慶應義塾大学
# 方式）と、「ラベル：値」1行方式（早稲田大学方式）の両対応。「出身」単独（出身地/都道府県
# の意味で使われる、実データ確認: 日本体育大学）は出身校ラベルとして扱わないよう
# 「校」「高校」を必須にする。
_DETAIL_SCHOOL_LABEL_RE = re.compile(r"^(出身校|出身高校)[：:]?$")
_DETAIL_SCHOOL_INLINE_RE = re.compile(r"^(出身校|出身高校)[：:]\s*(.+)$")
# ナビ等の汎用リンクを個別ページと誤認しないための足切り（アンカーの表示テキストが
# 長すぎる=一覧全体を1つのaタグで囲うような構造の誤検出を避ける）。
_DETAIL_ANCHOR_TEXT_MAX = 60


def _detail_link_map(html: str, base_url: str, known_kanji: set[str]) -> dict[str, str]:
    """一覧ページHTML -> {漢字氏名(空白除去): 個別ページ絶対URL}。
    known_kanji（そのページから既に regex/ローマ字抽出できた実在選手の漢字氏名）を
    手がかりに、表示テキストにその氏名を含むリンクだけを個別ページ候補として拾う。
    一致が無いサイトでは空dictを返し、既存の抽出結果に一切影響しない。"""
    soup = BeautifulSoup(html, "html.parser")
    known = {re.sub(r"[\s　]+", "", k) for k in known_kanji}
    mapping: dict[str, str] = {}
    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)
        if not text or len(text) > _DETAIL_ANCHOR_TEXT_MAX:
            continue
        flat = re.sub(r"[\s　]+", "", text)
        for kanji in known:
            if kanji in mapping:
                continue
            if kanji in flat:
                mapping[kanji] = urljoin(base_url, a["href"])
    return mapping


def _extract_school_from_detail(lines: list[str]) -> Optional[str]:
    """個別ページの行リストから出身校名を拾う。「出身校」ラベル行の直後の行を値と
    する方式（明治大学）と、「出身校：大阪桐蔭」のように1行にまとまった方式
    （早稲田大学）の両方に対応する。値が異常に長い場合は None（信頼度不足として拾わない）。"""
    for i, l in enumerate(lines):
        s = l.strip()
        im = _DETAIL_SCHOOL_INLINE_RE.match(s)
        if im:
            val = im.group(2).strip()
            if val and len(val) <= 30:
                return val
        if _DETAIL_SCHOOL_LABEL_RE.match(s) and i + 1 < len(lines):
            val = lines[i + 1].strip()
            if val and len(val) <= 30:
                return val
    return None


# --- ヘッドレスブラウザ フォールバック ---------------------------------------
# Wix/React等クライアントサイド描画のサイト（本文冒頭の既知の失敗パターン参照）向け。
# regex/ローマ字抽出とも信頼度不足だった場合のみ呼ばれる最終手段。プロセス内で
# ブラウザを使い回す（collect()/collect_all() の呼び出し単位で起動・終了）。
_pw_ctx = None
_pw_browser = None


def _ensure_browser():
    global _pw_ctx, _pw_browser
    if _pw_browser is None:
        from playwright.sync_api import sync_playwright
        _pw_ctx = sync_playwright().start()
        _pw_browser = _pw_ctx.chromium.launch()
    return _pw_browser


def close_browser() -> None:
    """collect()/collect_all() 呼び出し後に呼ぶ（起動していなければ no-op）。"""
    global _pw_ctx, _pw_browser
    if _pw_browser is not None:
        _pw_browser.close()
        _pw_browser = None
    if _pw_ctx is not None:
        _pw_ctx.stop()
        _pw_ctx = None


def _get_rendered_html(url: str) -> Optional[str]:
    """ヘッドレスブラウザで描画後のHTMLを取得する。失敗時はNone（呼び出し側は
    従来通りLLMフォールバックへ進む。00原則5: 迷ったら保守的に）。"""
    try:
        browser = _ensure_browser()
        page = browser.new_page(user_agent=_HEADERS["User-Agent"])
        try:
            page.goto(url, timeout=20000, wait_until="networkidle")
        except Exception:
            pass  # タイムアウトしても描画済みDOMは使う
        html = page.content()
        page.close()
        return html
    except Exception:
        return None


def _get_html(url: str) -> Optional[str]:
    """GET→HTML文字列（timeout=15、指数バックオフ最大2回、失敗はNone）。"""
    delay = 1.0
    for attempt in range(_RETRIES + 1):
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or resp.encoding
            return resp.text
        except Exception:
            if attempt >= _RETRIES:
                return None
            time.sleep(delay)
            delay *= 2
    return None


def _flatten(html: str) -> list[str]:
    """HTML -> 空行を除いたテキスト行のリスト（script/style除去）。"""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text("\n")
    return [l.strip() for l in text.split("\n") if l.strip()]


def _is_anchor_like(w: str) -> bool:
    """かな/ローマ字/漢字いずれかの氏名アンカーパターンに一致するか（他選手の
    ブロック境界検出用。氏名ストップワードは除外）。「グラウンドスタッフ」等の
    複合語もかな氏名パターンに一致してしまうため、_KANA_STOPWORDS は部分一致で
    弾く（実データ確認: 筑波大学）。"""
    if w in _NAME_STOPWORDS:
        return False
    if any(sw in w for sw in _KANA_STOPWORDS):
        return False
    return bool(_KANA_RE.match(w) or _ROMAJI_NAME_RE.match(w) or _KANJI_NAME_RE.match(w))


def _block_bound(lines: list[str], i: int, direction: int, limit: int) -> int:
    """iからdirection(+1/-1)方向に、他選手のアンカーらしき行に当たる直前まで進んだ
    インデックスを返す（limit歩まで）。ブロック密度が高いサイトで隣接選手の値を
    誤って拾わないための境界（実データ確認: 成城大学）。直後(距離1)の行がアンカー
    らしくても打ち切らない（「漢字氏名の次の行がかな」のようにこのアンカー自身の
    別表記である可能性が高いため。距離2以降で初めて「次の選手」とみなす）。"""
    bound = i
    for step in range(1, limit + 1):
        j = i + direction * step
        if j < 0 or j >= len(lines):
            break
        if step >= 2 and _is_anchor_like(lines[j]):
            break
        bound = j
    return bound


def _fields_near(lines: list[str], i: int) -> dict:
    """行番号iのアンカー（かな氏名 or ローマ字氏名）を中心に、周辺から漢字氏名/学年/
    ポジション/出身校/身長体重を拾う（アンカー種別に依存しない共通ロジック）。
    他選手のアンカー行に達したらそこで打ち切り、ブロックをまたいだ混線を防ぐ。"""
    lo = _block_bound(lines, i, -1, _BACK_WINDOW)
    hi = _block_bound(lines, i, 1, _FORWARD_WINDOW)
    # (行番号, 文字列) を中心 i からの距離が近い順に見る -> 隣接レコードの
    # 値を拾ってしまう混線を避け、このアンカーに最も近い値を優先する。
    window = sorted(range(lo, hi + 1), key=lambda j: abs(j - i))
    kanji = grade = pos = school = height = weight = None
    kanji_dist = None
    is_staff = False
    for j in window:
        w = lines[j]
        if j == i:
            continue
        dist = abs(j - i)
        # ブロック境界(_block_bound)が既に他選手の値との混線を防いでいるため、
        # 境界内であれば距離を問わず拾う（実データ確認: 出身校がアンカーから
        # 遠いサイトがある一方、境界のおかげで隣接選手の値の誤取得は防げる）。
        if kanji is None and _KANJI_NAME_RE.match(w) and w not in _NAME_STOPWORDS:
            kanji = w
            kanji_dist = dist
        if w in ("スタッフ", "STAFF", "監督・コーチ", "COACH"):
            is_staff = True
        if grade is None:
            gm = _GRADE_RE.match(w) or _GRADE_RE.match(_strip_label(w))
            if gm:
                grade = gm.group(1)
        if pos is None:
            # 生の行、ラベル除去後、さらに "/／・、" 区切りの先頭/末尾の順に試す
            # （「4年生 / PR」「副将・LO」「ポジション｜LO・No.8/主将」等、実データ確認:
            # 日本体育大学・筑波大学・成城大学）。
            candidates = [w.upper()]
            stripped = _strip_label(w).upper()
            if stripped != w.upper():
                candidates.append(stripped)
            for c in list(candidates):
                parts = re.split(r"[/／、]", c)
                if len(parts) > 1:
                    candidates.append(parts[0].strip())
                    candidates.append(parts[-1].strip())
            for c in candidates:
                if c and _POS_RE.match(c):
                    pos = c
                    break
        if school is None:
            lm = _SCHOOL_LABEL_RE.match(w) or _SCHOOL_LABEL_RE.match(_strip_label(w))
            if lm:
                # 「出身校｜成城学園」等、値に「高校」接尾辞が無くてもラベル一致を優先する。
                school = lm.group(2).strip()
            elif _SCHOOL_RE.search(w):
                # 「2年生 / 桐蔭学園高校」のように学年+出身校が1行にまとまっている
                # 場合は "/" 以降の校名部分だけを取り出す。
                school = re.split(r"[/／]", w)[-1].strip().replace("\xa0", "")
        if height is None:
            hm = _HEIGHT_RE.search(w)
            if hm:
                height = hm.group(1)
        if weight is None:
            wm = _WEIGHT_RE.search(w)
            if wm:
                weight = wm.group(1)
    return {
        "kanji": kanji, "kanji_dist": kanji_dist, "grade": grade, "position": pos,
        "school_raw": school, "height_cm": height, "weight_kg": weight, "is_staff": is_staff,
    }


def _dedupe_by_kanji(records: list[dict]) -> list[dict]:
    """同一漢字氏名の重複除去。ローマ字表記の外国人選手が隣接すると、その選手の
    かな氏名が「漢字表記が無い(ローマ字なので_KANJI_NAME_REに一致しない)」ため
    window内の別の日本人選手の漢字氏名を誤って一番近いものとして拾ってしまう
    ケースを実データで確認した（例: 慶應義塾大学 "Thomas Nicholas Pappas" の
    かな「とーます にこらす ぱぱす」が隣の日本人選手「長山 晃久」の漢字と
    誤って組まれる）。同じ漢字氏名について複数候補がある場合は、アンカーからの
    行距離が最も近い(=本来のペアである可能性が最も高い)ものだけを残す。"""
    best: dict[str, dict] = {}
    for r in records:
        cur = best.get(r["kanji"])
        if cur is None or r["_kanji_dist"] < cur["_kanji_dist"]:
            best[r["kanji"]] = r
    out = []
    for r in best.values():
        r.pop("_kanji_dist", None)
        out.append(r)
    return out


def _extract_records(lines: list[str]) -> list[dict]:
    """かな氏名行を手がかりに周辺から漢字氏名/学年/ポジション/出身校/身長体重を拾う。

    学年・ポジションのどちらも伴わない候補は信頼度不足として捨てる（誤検出対策）。
    """
    records: list[dict] = []
    for i, l in enumerate(lines):
        if not _KANA_RE.match(l):
            continue
        if len(l.replace("　", "").replace(" ", "")) < 3:
            continue
        if l.replace("　", "").replace(" ", "") in _KANA_STOPWORDS:
            continue
        f = _fields_near(lines, i)
        if f["is_staff"]:
            continue  # 監督・コーチ・スタッフは選手名簿ではないため除外
        if f["kanji"] and (f["grade"] or f["position"]):
            records.append({
                "kana": re.sub(r"\s+", "", l),
                "kanji": f["kanji"],
                "grade": _GRADE_INT.get(f["grade"]) if f["grade"] else None,
                "position": f["position"],
                "school_raw": f["school_raw"],
                "height_cm": f["height_cm"],
                "weight_kg": f["weight_kg"],
                "_kanji_dist": f["kanji_dist"],
            })
    return _dedupe_by_kanji(records)


def _extract_records_romaji(lines: list[str]) -> list[dict]:
    """かな表記の読みが無く、ローマ字氏名のみを読みとして掲載するサイト向けフォールバック
    抽出（実データ確認: 帝京大学。00原則5: かな版で信頼度不足だった場合のみ呼ばれる）。
    ロジックは _extract_records と同一だが、アンカーがローマ字のため kana ではなく
    name_en_raw として拾う（ローマ字は氏名の読みではなく英語表記のため）。
    """
    records: list[dict] = []
    for i, l in enumerate(lines):
        if not _ROMAJI_NAME_RE.match(l):
            continue
        f = _fields_near(lines, i)
        if f["is_staff"]:
            continue
        if f["kanji"] and (f["grade"] or f["position"]):
            records.append({
                "kana": None,
                "name_en_raw": l,
                "kanji": f["kanji"],
                "grade": _GRADE_INT.get(f["grade"]) if f["grade"] else None,
                "position": f["position"],
                "school_raw": f["school_raw"],
                "height_cm": f["height_cm"],
                "weight_kg": f["weight_kg"],
                "_kanji_dist": f["kanji_dist"],
            })
    return _dedupe_by_kanji(records)


_SCHOOL_SCAN_MAX = 12  # ブロック型ポータルサイトの出身校前方探索の最大距離（実データ確認: 筑波大学）


def _school_forward_scan(lines: list[str], anchor_i: int) -> Optional[str]:
    """kanjiアンカーより後方のみを、次の選手ブロック（次の漢字氏名行）に到達するまで
    探索し、最初に見つかった出身校らしき行を返す（_FIELD_WINDOWより離れた位置に
    出身校を置くブロック型ポータルサイト向け。実データ確認: 筑波大学
    tsukubaowls.com。次アンカーで打ち切るためブロック境界を越えて隣の選手の値を
    誤って拾うことはない）。"""
    hi = min(len(lines), anchor_i + _SCHOOL_SCAN_MAX + 1)
    for j in range(anchor_i + 1, hi):
        w = lines[j]
        if _KANJI_NAME_RE.match(w):
            break
        if _SCHOOL_RE.search(w):
            return re.split(r"[/／]", w)[-1].strip().replace("\xa0", "")
    return None


def _extract_records_kanji(lines: list[str]) -> list[dict]:
    """かな・ローマ字の読みが一切無く、漢字氏名のみを掲載するサイト向け最終フォールバック
    （実データ確認: 日本体育大学・筑波大学。00原則5: かな版・ローマ字版とも信頼度不足
    だった場合の最終手段。誤検出リスクが最も高い方式のため最後に試す）。漢字氏名の行
    自体をアンカーに、直後の学年/ポジション行（例:「4年生 / PR」）等から拾う。
    """
    records: list[dict] = []
    for i, l in enumerate(lines):
        if not _KANJI_NAME_RE.match(l) or l in _NAME_STOPWORDS:
            continue
        f = _fields_near(lines, i)
        if f["is_staff"]:
            continue
        if f["grade"] or f["position"]:
            # 前方探索(次選手ブロック境界で打ち切り)を優先する。f["school_raw"]は
            # 双方向探索のため、ブロック間隔が狭いサイトだと前の選手の出身校を
            # 誤って拾うことがある（実データ確認: 筑波大学）。
            school = _school_forward_scan(lines, i) or f["school_raw"]
            records.append({
                "kana": None,
                "kanji": l,
                "grade": _GRADE_INT.get(f["grade"]) if f["grade"] else None,
                "position": f["position"],
                "school_raw": school,
                "height_cm": f["height_cm"],
                "weight_kg": f["weight_kg"],
                "_kanji_dist": 0,
            })
    return _dedupe_by_kanji(records)


def _grade_from_llm_text(g: Optional[str]) -> Optional[int]:
    if not g:
        return None
    m = re.search(r"([1-4１２３４])", g)
    return _GRADE_INT.get(m.group(1)) if m else None


def _collect_team(team_name: str, url: str) -> dict:
    """1校分の名簿ページ取得 -> raw records（{kanji,kana,grade,position,school_raw,...}）。"""
    warnings: list[str] = []
    html = _get_html(url)
    time.sleep(_SLEEP)
    if html is None:
        warnings.append(f"university {team_name}: 名簿ページ取得失敗（接続不可/DNS不可/404）、スキップ")
        return {"records": [], "warnings": warnings, "used_llm": False}

    lines = _flatten(html)
    records = _extract_records(lines)

    # かな氏名が無くローマ字氏名のみのサイト向けフォールバック（実データ確認: 帝京大学）。
    if len(records) < _MIN_CONFIDENT:
        romaji_records = _extract_records_romaji(lines)
        if len(romaji_records) > len(records):
            records = romaji_records

    # かな・ローマ字とも読みが一切無く漢字氏名のみのサイト向け最終フォールバック
    # （実データ確認: 日本体育大学。誤検出リスクが高いため上記2方式の後にのみ試す）。
    if len(records) < _MIN_CONFIDENT:
        kanji_records = _extract_records_kanji(lines)
        if len(kanji_records) > len(records):
            records = kanji_records

    # 上記3方式とも信頼度不足（JS描画で一覧が空 等）の場合のみヘッドレスブラウザで
    # 再取得する（00原則5: 通常のサイトには一切追加負荷をかけない、対応外サイトは
    # レンダリング結果でも0件のままno-op）。
    if len(records) < _MIN_CONFIDENT:
        rendered_html = _get_rendered_html(url)
        if rendered_html:
            rendered_lines = _flatten(rendered_html)
            rendered_records = _extract_records(rendered_lines)
            if len(rendered_records) < _MIN_CONFIDENT:
                romaji_rendered = _extract_records_romaji(rendered_lines)
                if len(romaji_rendered) > len(rendered_records):
                    rendered_records = romaji_rendered
            if len(rendered_records) < _MIN_CONFIDENT:
                kanji_rendered = _extract_records_kanji(rendered_lines)
                if len(kanji_rendered) > len(rendered_records):
                    rendered_records = kanji_rendered
            if len(rendered_records) > len(records):
                records = rendered_records
                lines = rendered_lines
                html = rendered_html

    used_llm = False

    # 一覧ページに出身校が無いサイト向け: 個別ページへのカード型リンクがあれば
    # 出身校未取得の選手だけ追加取得して補う（対応外サイトは detail_map が空で no-op）。
    missing_school = [r for r in records if not r.get("school_raw")]
    if missing_school:
        known_kanji = {r["kanji"] for r in records}
        detail_map = _detail_link_map(html, url, known_kanji)
        for rec in missing_school:
            detail_url = detail_map.get(re.sub(r"[\s　]+", "", rec["kanji"]))
            if not detail_url:
                continue
            detail_html = _get_html(detail_url)
            time.sleep(_SLEEP)
            if not detail_html:
                warnings.append(f"university {team_name}: 個別ページ取得失敗 {detail_url}、出身校スキップ")
                continue
            school = _extract_school_from_detail(_flatten(detail_html))
            if school:
                rec["school_raw"] = school

    if len(records) < _MIN_CONFIDENT:
        text = "\n".join(lines)
        llm_hits = llm_fallback.extract_roster_members(text, team_name)
        if llm_hits:
            used_llm = True
            records = [{
                "kana": h["kana"] or "",
                "kanji": h["name"],
                "grade": _grade_from_llm_text(h.get("grade")),
                "position": h.get("position"),
                "school_raw": None,
                "height_cm": None,
                "weight_kg": None,
            } for h in llm_hits]
        if not records:
            warnings.append(
                f"university {team_name}: 名簿抽出0件（regex/Sonnetいずれも不可。"
                f"JS描画サイト・フィルタUI経由の可能性）、スキップ")
    return {"records": records, "warnings": warnings, "used_llm": used_llm}


def _dedupe_players(players: list[dict], warnings: list[str]) -> list[dict]:
    """id重複を最終防御としてここでも弾く（サイト側の一時的な二重描画等、_extract_records
    のチーム内かな氏名/漢字氏名重複除去をすり抜けるケースへの安全策。00原則5）。"""
    seen: set[str] = set()
    out = []
    for p in players:
        if p["id"] in seen:
            warnings.append(f"university: id重複 {p['id']} を検出、2件目以降を除外")
            continue
        seen.add(p["id"])
        out.append(p)
    return out


def collect(division_key: str) -> dict:
    """1区分（対抗戦A等）分の全校名簿を収集する。"""
    warnings: list[str] = []
    players: list[dict] = []
    div = DIVISIONS[division_key]
    try:
        for team_name, url in div["teams"]:
            res = _collect_team(team_name, url)
            warnings.extend(res["warnings"])
            for rec in res["records"]:
                player, pw = normalize.player_university(
                    rec, team_name=team_name, division=division_key, source_url=url)
                warnings.extend(pw)
                if player is not None:
                    players.append(player)
    finally:
        close_browser()
    players = _dedupe_players(players, warnings)
    return {"players": players, "teams": [], "matches": [], "standings": [], "warnings": warnings}


def collect_all() -> dict:
    """6区分（大学スコープ全体）をまとめて収集する（run.py の league="university" 用）。"""
    warnings: list[str] = []
    players: list[dict] = []
    for division_key in DIVISIONS:
        res = collect(division_key)
        players.extend(res["players"])
        warnings.extend(res["warnings"])
    players = _dedupe_players(players, warnings)
    return {"players": players, "teams": [], "matches": [], "standings": [], "warnings": warnings}
