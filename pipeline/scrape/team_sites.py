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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja,en;q=0.8",
}
_TIMEOUT = 20
_SLEEP = 1.5
_RETRIES = 2

# 公式HP内で新着情報がまとまっている可能性が高いパス。存在するものだけ巡回する。
_NEWS_PATHS = ("", "/news", "/news/", "/topics", "/topics/", "/information/", "/info/")

# 記事リンク判定に使う日付表記（本文 or URL 側）。
_DATE_RES = (
    re.compile(r"(20\d{2})[.\-/年](\d{1,2})[.\-/月](\d{1,2})"),
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


def _is_noise(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if any(host == h or host.endswith("." + h) for h in _NOISE_HOSTS):
        return True
    return bool(_NOISE_PATH_RE.search(parsed.path))


def _get(url: str) -> Optional[requests.Response]:
    for attempt in range(_RETRIES + 1):
        try:
            res = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
            if res.status_code == 200:
                res.encoding = res.apparent_encoding or res.encoding
                return res
            if res.status_code in (404, 403, 410):
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
            for key, value in profile.items():
                if key == "practice_ground":
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


def _extract_items(html: str, page_url: str) -> list[dict]:
    """日付を伴う同一ホスト内リンクを新着記事候補として抽出する。"""
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
            continue
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
        if re.search(r"/(news|topics|information|info|blog)$", path) and href not in found:
            found.append(href.split("#")[0])
    return found[:3]


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

    seen: set[str] = set()
    for url in targets[:4]:
        if url in seen:
            continue
        seen.add(url)
        res = top if (top is not None and url == top.url) else _fetch_page(url, robots, warnings)
        if res is None:
            continue
        pages.append(
            {
                "url": res.url,
                "hash": hashlib.sha256(res.text.encode("utf-8", "ignore")).hexdigest()[:16],
            }
        )
        for item in _extract_items(res.text, res.url):
            items.setdefault(item["url"], item)

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


def monitor(divisions: Iterable[str] = DIVISIONS, limit: Optional[int] = None) -> dict:
    """全チーム公式HPを巡回し、前回スナップショットとの差分を返す。"""
    robots = _Robots()
    checked_at = datetime.now(io.JST).isoformat(timespec="seconds")
    results, warnings = [], []
    count = 0
    for division in divisions:
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
            results.append(
                {
                    "team_id": team_id,
                    "league": division,
                    "name": name,
                    "official_url": official_url,
                    "status": status,
                    "first_run": not prev,
                    "item_count": len(crawled["items"]),
                    "new_items": [] if not prev else new_items,
                    "changed_pages": changed_pages,
                }
            )
    report = {"checked_at": checked_at, "teams": results, "warnings": warnings}
    io.write_json(REPORT_DIR / f"{checked_at[:10]}.json", report)
    return report
