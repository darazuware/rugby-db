"""リーグワン全チーム公式HPの監視スクレイパー（D1/D2/D3）。

2段構え:
  1. discover_official_urls() — league-one.jp の各チームページ「チームプロフィール」表から
     公式サイトURL / ホストエリア / 練習グラウンドを取得し teams master へ書き戻す。
  2. monitor() — 各チーム公式HPを巡回し、新着記事リンクとページハッシュのスナップショットを
     data/monitor/team_sites/*.json に保存。前回スナップショットとの差分（新規記事）を返す。

方針（02/03）:
  - robots.txt を必ず確認し、Disallow のURLは取得しない（status="robots_denied"）。
  - HTML構造が想定と違う項目は null / 空にして warnings に積む。例外で全体を止めない。
  - AIの知識でチーム事実を書かない。全ての値は取得したHTMLに由来する。
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import time
from datetime import datetime
from typing import Iterable, Optional
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from pipeline import io

BASE = "https://league-one.jp"
DIVISIONS = ("league-one-d1", "league-one-d2", "league-one-d3")
SNAPSHOT_DIR = io.REPO_ROOT / "data" / "monitor" / "team_sites"
REPORT_DIR = io.REPO_ROOT / "data" / "monitor" / "reports"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    # 企業サイト（suntory.co.jp / jreast.co.jp 等）のWAFは UA だけだと 403 を返す。
    # 実ブラウザと同じ sec-fetch-* / sec-ch-ua を添えると通常のナビゲーションとして扱われる。
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
    "sec-ch-ua": '"Chromium";v="126", "Not.A/Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
}
_TIMEOUT = 20
_SLEEP = 1.5
_RETRIES = 2

# 公式HP内で新着情報がまとまっている可能性が高いパス。存在するものだけ巡回する。
_NEWS_PATHS = ("", "/news", "/news/", "/topics", "/topics/", "/information/", "/info/")

# 記事リンク判定に使う日付表記（本文 or URL 側）。
_DATE_RES = (
    re.compile(r"(20\d{2})\s*[.\-/年]\s*(\d{1,2})\s*[.\-/月]\s*(\d{1,2})"),
    re.compile(r"/(20\d{2})/(\d{1,2})/(\d{1,2})/"),
    re.compile(r"/(20\d{2})(\d{2})(\d{2})"),
)
# 記事ではないリンクの除外。ホスト名とパスを分けて判定する
# （"voltex.com" が "x.com" に誤ヒットするような事故を防ぐ）。
_NOISE_HOSTS = (
    "twitter.com",
    "x.com",
    "facebook.com",
    "instagram.com",
    "youtube.com",
    "youtu.be",
    "tiktok.com",
    "line.me",
)
_NOISE_PATH_RE = re.compile(
    r"/(ticket|store|shop|privacy|policy|contact|sitemap|recruit|login|cart)(/|$)",
    re.IGNORECASE,
)
# 月別アーカイブ・ページャ等の一覧リンク（記事本体ではない）。
_NOISE_QUERY_RE = re.compile(r"(^|&)(ym|page|paged|cat|category|tag)=", re.IGNORECASE)


# 改称・新チーム名の告知を見つけるためのキーワード（AZ-COM丸和の新名称は2026年8月上旬発表予定）。
_RENAME_RE = re.compile(
    r"(チーム名(称)?(の)?(変更|決定|発表)|新チーム名|新名称|改称|名称変更|"
    r"新エンブレム|エンブレム.*(決定|発表|刷新)|リブランディング)"
)

# 読者の関心が最も高いのは選手の加入・退団。改称より優先して拾い、通知の先頭に出す。
_ROSTER_RE = re.compile(
    r"(新加入|加入内定|加入のお知らせ|入団|移籍|獲得|補強|契約(更新|更改|締結|継続|満了|解除)|"
    r"退団|退部|離脱|引退|現役引退|卒業|新体制|選手登録|追加登録|キャプテン|主将|"
    r"(ヘッド)?コーチ(就任|退任|契約)|監督(就任|退任)|(就任|退任)のお知らせ)"
)
# 代表招集（ブレイブブロッサムズ / PNC 系）。試合ごとの「メンバー発表」は
# 毎節出て通知が埋もれるため、代表・招集に関する語だけを対象にする。
_SQUAD_RE = re.compile(
    r"(代表(候補)?(メンバー|スコッド|選手|チーム|活動|合宿)?[^。]{0,6}(選出|招集|決定|発表)|"
    r"日本代表|ブレイブブロッサムズ|サクラフィフティーン|"
    r"squad|call-?up|named|selection)",
    re.IGNORECASE,
)
_INJURY_RE = re.compile(r"(負傷|けが|怪我|手術|復帰|コンディション)")


def _categorize(title: str) -> Optional[str]:
    """記事タイトルを通知カテゴリに分類する。該当なしは None（=通常の新着）。"""
    if _ROSTER_RE.search(title):
        return "roster"
    if _SQUAD_RE.search(title):
        return "squad"
    if _INJURY_RE.search(title):
        return "injury"
    if _RENAME_RE.search(title):
        return "rename"
    return None


# チーム公式HP以外に監視する統括団体・大会公式。チーム名だけでなく代表招集・大会情報の一次情報源。
EXTRA_SOURCES = (
    {"key": "league_one", "name": "リーグワン公式", "url": f"{BASE}/news/"},
    {"key": "jrfu", "name": "日本ラグビー協会（ブレイブブロッサムズ）", "url": "https://www.rugby-japan.jp/news/"},
    {
        "key": "pnc",
        "name": "パシフィック・ネーションズカップ（World Rugby）",
        "url": "https://www.world.rugby/news",
        # 一覧に日付が出ないため URL パターンで記事を判定する。
        "article_re": re.compile(r"/news/\d{4,}/"),
        # World Rugby 全体のニュースは量が多い。PNC・日本関連だけに絞る。
        "topic_re": re.compile(
            r"(pacific[- ]nations|\bpnc\b|japan|brave blossoms|fiji|samoa|tonga|"
            r"usa eagles|canada)",
            re.IGNORECASE,
        ),
    },
)


def _is_noise(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if any(host == h or host.endswith("." + h) for h in _NOISE_HOSTS):
        return True
    if parsed.query and _NOISE_QUERY_RE.search(parsed.query):
        return True
    return bool(_NOISE_PATH_RE.search(parsed.path))


class _CurlResponse:
    """curl フォールバック時の最小レスポンス（requests.Response 互換の使用部分のみ）。"""

    def __init__(self, url: str, text: str, content_type: str) -> None:
        self.url = url
        self.text = text
        self.headers = {"content-type": content_type}
        self.status_code = 200

    def json(self):
        import json

        return json.loads(self.text)


def _curl_get(url: str) -> Optional[_CurlResponse]:
    """requests が 403 の場合の HTTP/2 フォールバック。

    suntory.co.jp / jreast.co.jp の WAF は HTTP/1.1 の requests を弾くが、
    ブラウザと同じ HTTP/2 + sec-fetch-* なら通常のナビゲーションとして通る。
    """
    cmd = ["curl", "-sS", "--http2", "-L", "--compressed", "-m", str(_TIMEOUT), "-w", "\n%{content_type}"]
    for key, value in _HEADERS.items():
        cmd += ["-H", f"{key}: {value}"]
    cmd.append(url)
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=_TIMEOUT + 10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0 or not proc.stdout:
        return None
    body, _, content_type = proc.stdout.decode("utf-8", "replace").rpartition("\n")
    if not body.strip():
        return None
    return _CurlResponse(url, body, content_type.strip())


def _get(url: str):
    for attempt in range(_RETRIES + 1):
        try:
            res = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
            if res.status_code == 200:
                res.encoding = res.apparent_encoding or res.encoding
                return res
            if res.status_code == 403:
                return _curl_get(url)
            if res.status_code in (404, 410):
                return None
        except requests.RequestException:
            pass
        if attempt < _RETRIES:
            time.sleep(_SLEEP * (attempt + 1))
    return None


class _Robots:
    """ホスト単位で robots.txt をキャッシュする。取得失敗時は許可扱い。"""

    def __init__(self) -> None:
        self._cache: dict[str, Optional[RobotFileParser]] = {}

    def allowed(self, url: str) -> bool:
        host = urlparse(url).netloc
        if host not in self._cache:
            rp = RobotFileParser()
            robots_url = f"{urlparse(url).scheme}://{host}/robots.txt"
            try:
                res = requests.get(robots_url, headers=_HEADERS, timeout=10)
                if res.status_code == 200:
                    rp.parse(res.text.splitlines())
                else:
                    rp = None
            except requests.RequestException:
                rp = None
            self._cache[host] = rp
        rp = self._cache[host]
        return True if rp is None else rp.can_fetch(_HEADERS["User-Agent"], url)


# --------------------------------------------------------------------------
# 1. 公式サイトURLの取得（league-one.jp チームプロフィール表）
# --------------------------------------------------------------------------

_PROFILE_KEYS = {
    "公式チーム名称": "official_name",
    "公式サイト": "official_url",
    "ホストエリア自治体名": "home_area",
    "練習グラウンド所在地": "practice_ground",
}


def _parse_profile(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    out: dict = {}
    for th in soup.select("th"):
        key = _PROFILE_KEYS.get(th.get_text(strip=True))
        if not key:
            continue
        td = th.find_next_sibling("td")
        if not td:
            continue
        if key == "official_url":
            a = td.find("a", href=True)
            out[key] = a["href"].strip() if a else None
        else:
            out[key] = td.get_text(strip=True) or None
    return out


def discover_official_urls(divisions: Iterable[str] = DIVISIONS) -> dict:
    """teams master の source_url（league-one.jp/team/N）から公式HP等を取得して書き戻す。"""
    updated, warnings = [], []
    for division in divisions:
        path = io.teams_path(division)
        teams = io.read_records(path)
        changed = False
        for team in teams:
            src = team.get("source_url") or ""
            if "league-one.jp/team/" not in src:
                warnings.append(f"{team.get('id')}: source_url がリーグワン公式でない")
                continue
            res = _get(src)
            time.sleep(_SLEEP)
            if res is None:
                warnings.append(f"{team.get('id')}: {src} 取得失敗")
                continue
            profile = _parse_profile(res.text)
            if not profile.get("official_url"):
                warnings.append(f"{team.get('id')}: 公式サイト行が見つからない")
            official_name = profile.get("official_name")
            if official_name and official_name != team.get("name_ja"):
                warnings.append(
                    f"{team.get('id')}: チーム名がリーグ公式と不一致"
                    f"（master='{team.get('name_ja')}' / league-one.jp='{official_name}'）"
                )
            for key, value in profile.items():
                if key in ("practice_ground", "official_name"):
                    continue
                if value and team.get(key) != value:
                    team[key] = value
                    changed = True
            if profile.get("official_url"):
                updated.append(
                    {
                        "id": team["id"],
                        "league": division,
                        "name": team.get("name_ja"),
                        "official_url": profile["official_url"],
                    }
                )
        if changed:
            io.write_records(path, teams)
    return {"teams": updated, "warnings": warnings}


# --------------------------------------------------------------------------
# 2. 公式HPの監視
# --------------------------------------------------------------------------


def _extract_date(text: str, href: str) -> Optional[str]:
    for pattern in _DATE_RES:
        m = pattern.search(text) or pattern.search(href)
        if m:
            y, mo, d = m.groups()
            try:
                return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"
            except ValueError:
                return None
    return None


def _link_contexts(a) -> list[str]:
    """リンク周辺テキストを内側から順に返す（日付は兄弟要素側にあることが多い）。

    巨大なラッパー div の全文まで見ると無関係な日付を掴むため、300文字を超えた
    時点で打ち切る。呼び出し側は内側から順に日付を探す。
    """
    contexts = [re.sub(r"\s+", " ", a.get_text(" ", strip=True))]
    node = a
    for _ in range(4):
        node = node.parent
        if node is None:
            break
        text = re.sub(r"\s+", " ", node.get_text(" ", strip=True))
        if len(text) > 300:
            break
        contexts.append(text)
    return contexts


def _extract_items(html: str, page_url: str, article_re: Optional[re.Pattern] = None) -> list[dict]:
    """日付を伴う同一ホスト内リンクを新着記事候補として抽出する。

    article_re を渡した場合、日付が無くても記事URLパターンに一致すれば拾う
    （world.rugby のように一覧に日付を出さないサイト向け。date は "" になる）。
    """
    soup = BeautifulSoup(html, "html.parser")
    host = urlparse(page_url).netloc
    items: dict[str, dict] = {}
    for a in soup.find_all("a", href=True):
        href = urljoin(page_url, a["href"].strip())
        if urlparse(href).netloc != host or _is_noise(href):
            continue
        contexts = _link_contexts(a)
        title = contexts[0]
        date = next((d for d in (_extract_date(c, href) for c in contexts) if d), None)
        if not date:
            if article_re is None or not article_re.search(urlparse(href).path):
                continue
            date = ""
        title = title or contexts[-1]
        if not (4 <= len(title) <= 160):
            continue
        if href not in items:
            items[href] = {"url": href, "title": title, "date": date}
    return sorted(items.values(), key=lambda i: (i["date"], i["url"]), reverse=True)[:40]


def _discover_news_paths(html: str, page_url: str) -> list[str]:
    """トップページのリンクから、そのサイトの新着一覧ページURLを見つける。"""
    soup = BeautifulSoup(html, "html.parser")
    host = urlparse(page_url).netloc
    found: list[str] = []
    for a in soup.find_all("a", href=True):
        href = urljoin(page_url, a["href"].strip())
        if urlparse(href).netloc != host or _is_noise(href):
            continue
        path = urlparse(href).path.rstrip("/")
        # 新着一覧本体に加え、年別アーカイブ（/news/2026.html 等）も対象にする。
        # 一覧トップが JS 描画でも年別ページは静的HTMLのことが多い。
        if (
            re.search(r"/(news|topics|information|info|blog)$", path)
            or re.search(r"/(news|topics|information|info|blog)/20\d\d(\.html)?$", path)
        ) and href not in found:
            found.append(href.split("#")[0])
    return found[:4]


def _follow_relocation(html: str, page_url: str) -> Optional[str]:
    """「移動します」系の案内ページなら移転先URLを返す（NEC→JR東日本のようなケース）。"""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    if len(text) > 400 or not re.search(r"(移動|移転|リニューアル|新しい.*サイト)", text):
        return None
    host = urlparse(page_url).netloc
    for a in soup.find_all("a", href=True):
        href = urljoin(page_url, a["href"].strip())
        if href.startswith("http") and urlparse(href).netloc != host:
            return href
    return None


def _parse_feed(xml: str, feed_url: str) -> list[dict]:
    """RSS/Atom から記事候補を作る（JS描画サイトのフォールバック）。"""
    # lxml 非依存のため html.parser を使う（タグ名は小文字化される）。
    soup = BeautifulSoup(xml, "html.parser")
    items: list[dict] = []
    for entry in soup.find_all(["item", "entry"])[:40]:
        link_tag = entry.find("link")
        link = (link_tag.get_text(strip=True) if link_tag else "") or (
            link_tag.get("href") if link_tag else ""
        )
        title_tag = entry.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""
        date_tag = entry.find(["pubdate", "published", "updated", "dc:date"])
        raw_date = date_tag.get_text(strip=True) if date_tag else ""
        date = _extract_date(raw_date, link) or _parse_rfc822(raw_date)
        if link and title and date:
            items.append({"url": urljoin(feed_url, link), "title": title, "date": date})
    return items


_RFC822_MONTHS = {
    m: i
    for i, m in enumerate(
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1
    )
}


def _parse_rfc822(value: str) -> Optional[str]:
    m = re.search(r"(\d{1,2})\s+([A-Z][a-z]{2})\s+(20\d{2})", value)
    if not m:
        return None
    day, month, year = m.groups()
    if month not in _RFC822_MONTHS:
        return None
    return f"{year}-{_RFC822_MONTHS[month]:02d}-{int(day):02d}"


def _fetch_page(url: str, robots: _Robots, warnings: list[str]):
    if not robots.allowed(url):
        warnings.append(f"robots.txt により取得しない: {url}")
        return None
    res = _get(url)
    time.sleep(_SLEEP)
    return res


def _crawl_site(official_url: str, robots: _Robots) -> dict:
    """公式HPのトップと新着一覧を巡回し、記事候補とページハッシュを返す。

    トップ → （移転案内なら移転先へ）→ トップのリンクから新着一覧を発見 → 巡回。
    HTML から記事が取れない（JS描画）サイトは RSS/Atom フィードにフォールバックする。
    """
    pages: list[dict] = []
    items: dict[str, dict] = {}
    warnings: list[str] = []
    relocated_to: Optional[str] = None

    top = _fetch_page(official_url.rstrip("/") + "/", robots, warnings)
    if top is not None:
        moved = _follow_relocation(top.text, top.url)
        if moved:
            relocated_to = moved
            warnings.append(f"公式サイトが移転: {official_url} -> {moved}")
            top = _fetch_page(moved, robots, warnings)

    targets: list[str] = []
    if top is not None:
        targets.append(top.url)
        targets.extend(_discover_news_paths(top.text, top.url))
    if not targets:
        targets = [official_url.rstrip("/") + p for p in _NEWS_PATHS[1:]]

    # 幅優先で最大6ページ。記事が取れなかったページからは、そのページ自身のリンクを
    # たどって1段だけ深追いする（トップ→/news/→/news/2026.html のようなサイト対策）。
    seen: set[str] = set()
    queue = list(targets)
    depth = {url: 0 for url in queue}
    while queue and len(pages) < 6:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        res = top if (top is not None and url == top.url) else _fetch_page(url, robots, warnings)
        if res is None:
            continue
        found_here = _extract_items(res.text, res.url)
        if not found_here and depth[url] < 2:
            for child in _discover_news_paths(res.text, res.url):
                if child not in seen and child not in depth:
                    depth[child] = depth[url] + 1
                    queue.append(child)
        pages.append(
            {
                "url": res.url,
                "hash": hashlib.sha256(res.text.encode("utf-8", "ignore")).hexdigest()[:16],
            }
        )
        for item in found_here:
            items.setdefault(item["url"], item)

    if not items:
        # 年別アーカイブの直接指定。一覧トップが JS 描画でも
        # /news/2026.html や /news/2026/ は静的HTMLで配信されているサイトがある。
        base = (relocated_to or official_url).rstrip("/")
        year = datetime.now(io.JST).year
        candidates = [
            f"{base}/news/{year}.html",
            f"{base}/news/{year}/",
            f"{base}/topics/{year}.html",
            f"{base}/topics/{year}/",
        ]
        for url in candidates:
            if url in seen:
                continue
            res = _fetch_page(url, robots, warnings)
            if res is None:
                continue
            found_here = _extract_items(res.text, res.url)
            if not found_here:
                continue
            pages.append(
                {
                    "url": res.url,
                    "hash": hashlib.sha256(res.text.encode("utf-8", "ignore")).hexdigest()[:16],
                }
            )
            for item in found_here:
                items.setdefault(item["url"], item)
            break

    if not items:
        # WordPress REST（JS描画サイトでも記事一覧が JSON で取れることが多い）。
        base = (relocated_to or official_url).rstrip("/")
        for path in ("/wp-json/wp/v2/posts?per_page=20", "/api/wp/v2/posts?per_page=20"):
            res = _fetch_page(base + path, robots, warnings)
            if res is None or "json" not in res.headers.get("content-type", ""):
                continue
            try:
                posts = res.json()
            except ValueError:
                continue
            for post in posts if isinstance(posts, list) else []:
                link = post.get("link")
                title = (post.get("title") or {}).get("rendered") or ""
                date = (post.get("date") or "")[:10]
                if link and title and re.fullmatch(r"20\d\d-\d\d-\d\d", date):
                    items.setdefault(
                        link,
                        {"url": link, "title": re.sub(r"<[^>]+>", "", title).strip(), "date": date},
                    )
            if items:
                pages.append(
                    {
                        "url": res.url,
                        "hash": hashlib.sha256(res.text.encode("utf-8", "ignore")).hexdigest()[:16],
                    }
                )
                break

    if not items:
        base = (relocated_to or official_url).rstrip("/")
        for path in ("/feed", "/rss.xml", "/feed.xml", "/news/feed"):
            res = _fetch_page(base + path, robots, warnings)
            if res is None or "<" not in res.text[:200]:
                continue
            feed_items = _parse_feed(res.text, res.url)
            if feed_items:
                for item in feed_items:
                    items.setdefault(item["url"], item)
                pages.append(
                    {
                        "url": res.url,
                        "hash": hashlib.sha256(res.text.encode("utf-8", "ignore")).hexdigest()[:16],
                    }
                )
                break

    if not pages:
        warnings.append(f"到達できるページがない: {official_url}")
    elif not items:
        warnings.append(f"記事リンクを抽出できない（JS描画の可能性）: {official_url}")
    return {
        "pages": pages,
        "items": sorted(items.values(), key=lambda i: (i["date"], i["url"]), reverse=True)[:60],
        "warnings": warnings,
        "relocated_to": relocated_to,
    }


def _snapshot_path(team_id: str):
    return SNAPSHOT_DIR / f"{team_id}.json"


def _check_source(source: dict, robots: _Robots, warnings: list[str], checked_at: str) -> dict:
    """統括団体・大会公式のニュース一覧を巡回し、新着差分とカテゴリ該当記事を返す。

    チーム名称はリーグ公式（league-one.jp）を正とするため、各チームHPだけでなく
    リーグ側の告知も見る。改称は見落とすと表示名がずれるため、差分に出なくても
    直近記事からキーワード一致を毎回返す。
    """
    # 正規表現は JSON に載せられないため、レポートには識別情報だけを渡す。
    meta = {k: source[k] for k in ("key", "name", "url")}
    path = SNAPSHOT_DIR / f"_{source['key']}.json"
    prev = io.read_json(path, default={}) or {}
    prev_urls = {i["url"] for i in prev.get("items", [])}

    res = _fetch_page(source["url"], robots, warnings)
    if res is None:
        warnings.append(f"{source['name']}: ニュース一覧を取得できない")
        return {**meta, "status": "unreachable", "new_items": [], "rename_signals": []}

    items = _extract_items(res.text, res.url, article_re=source.get("article_re"))
    topic_re = source.get("topic_re")
    if topic_re is not None:
        items = [i for i in items if topic_re.search(i["title"]) or topic_re.search(i["url"])]
    if not items:
        warnings.append(f"{source['name']}: 記事リンクを抽出できない（JS描画の可能性）")
    new_items = [] if not prev else [i for i in items if i["url"] not in prev_urls]
    for item in new_items:
        item["category"] = _categorize(item["title"])
    io.write_json(path, {"checked_at": checked_at, "url": res.url, "items": items})
    return {
        **meta,
        "status": "ok",
        "first_run": not prev,
        "item_count": len(items),
        "new_items": new_items,
        # 改称のみ差分に関係なく毎回返す（見落とし防止）。
        "rename_signals": [i for i in items if _RENAME_RE.search(i["title"])],
    }


def monitor(
    divisions: Iterable[str] = DIVISIONS,
    limit: Optional[int] = None,
    teams: bool = True,
    sources: bool = True,
) -> dict:
    """全チーム公式HPと統括団体サイトを巡回し、前回スナップショットとの差分を返す。

    teams=False で統括団体のみ（軽量・高頻度チェック用）、
    sources=False でチーム公式HPのみを巡回する。
    """
    robots = _Robots()
    checked_at = datetime.now(io.JST).isoformat(timespec="seconds")
    results, warnings = [], []
    count = 0
    for division in divisions if teams else ():
        for team in io.read_records(io.teams_path(division)):
            official_url = team.get("official_url")
            team_id = team.get("id")
            name = team.get("name_ja") or team_id
            if not official_url:
                warnings.append(f"{name}: official_url 未設定（discover を先に実行）")
                continue
            if limit is not None and count >= limit:
                break
            count += 1

            prev = io.read_json(_snapshot_path(team_id), default={}) or {}
            prev_urls = {i["url"] for i in prev.get("items", [])}
            prev_hashes = {p["url"]: p["hash"] for p in prev.get("pages", [])}

            crawled = _crawl_site(official_url, robots)
            warnings.extend(f"{name}: {w}" for w in crawled["warnings"])
            new_items = [i for i in crawled["items"] if i["url"] not in prev_urls]
            changed_pages = [
                p["url"] for p in crawled["pages"] if prev_hashes.get(p["url"]) not in (None, p["hash"])
            ]
            status = "ok" if crawled["pages"] else "unreachable"
            snapshot = {
                "team_id": team_id,
                "league": division,
                "name": name,
                "official_url": official_url,
                "checked_at": checked_at,
                "status": status,
                "relocated_to": crawled["relocated_to"],
                "pages": crawled["pages"],
                "items": crawled["items"],
            }
            if status == "ok":
                io.write_json(_snapshot_path(team_id), snapshot)
            team_new = [] if not prev else new_items
            for item in team_new:
                item["category"] = _categorize(item["title"])
            results.append(
                {
                    "team_id": team_id,
                    "league": division,
                    "name": name,
                    "official_url": official_url,
                    "status": status,
                    "first_run": not prev,
                    "item_count": len(crawled["items"]),
                    "new_items": team_new,
                    "changed_pages": changed_pages,
                    # 改称・エンブレム変更の告知は表示名の更新が必要になるため個別に立てる。
                    "rename_signals": [i for i in team_new if _RENAME_RE.search(i["title"])],
                }
            )

    source_results = [
        _check_source(s, robots, warnings, checked_at) for s in (EXTRA_SOURCES if sources else ())
    ]

    # 読者の関心が高い順（選手動向 > 代表招集 > 負傷）に、全ソース横断でまとめる。
    highlights: list[dict] = []
    for team in results:
        for item in team["new_items"]:
            if item.get("category") in ("roster", "squad", "injury"):
                highlights.append({"source": team["name"], **item})
    for src in source_results:
        for item in src["new_items"]:
            if item.get("category") in ("roster", "squad", "injury"):
                highlights.append({"source": src["name"], **item})
    order = {"roster": 0, "squad": 1, "injury": 2}
    highlights.sort(key=lambda i: (order[i["category"]], i["date"]), reverse=False)

    report = {
        "checked_at": checked_at,
        "teams": results,
        "sources": source_results,
        "highlights": highlights,
        "league_rename_news": [i for s in source_results for i in s["rename_signals"]],
        "warnings": warnings,
    }
    # 全巡回は日次レポートとして残す。軽量巡回（統括団体のみ等）は日次を上書きしない。
    name = f"{checked_at[:10]}.json" if teams and sources else "latest_light.json"
    io.write_json(REPORT_DIR / name, report)
    return report
