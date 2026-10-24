"""公開済み(draft: false)のニュース記事が、存在しない/下書きの /news/ 記事へリンクしていないこと。
下書きのうちは未公開記事へ張ってよいが、公開するときにリンク先も公開されている必要がある（公開前チェック）。"""
import re
from pathlib import Path

NEWS = Path(__file__).resolve().parent.parent / "src" / "content" / "news"
LINK = re.compile(r'(?:\]\(|href=")/news/([a-z0-9][a-z0-9_-]*)/?(?:#[^)"\s]*)?[)"]')


def _draft(text: str) -> bool:
    head = text.split("---", 2)[1] if text.startswith("---") else ""
    return bool(re.search(r"^draft:\s*true\s*$", head, flags=re.M))


def test_published_articles_do_not_link_to_missing_or_draft_news():
    meta = {p.stem: _draft(p.read_text(encoding="utf-8")) for p in NEWS.glob("*.md")}
    bad = []
    for p in sorted(NEWS.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        if meta[p.stem]:
            continue
        for slug in set(LINK.findall(text)):
            if slug not in meta or meta[slug]:
                bad.append(f"{p.name} -> /news/{slug}/ ({'下書き' if slug in meta else '存在しない'})")
    assert not bad, "公開記事から未公開/存在しない記事へのリンク:\n" + "\n".join(bad)
