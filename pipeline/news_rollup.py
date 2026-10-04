"""短信ニュース（加入・初キャップ・キャップ更新・退団の自動生成記事）を月次まとめ記事へ統合する。

- 対象: pipeline.news_gen が出す自動記事のうち本文1,000字未満・draft:false のもの
- エントリは data/meta/news/rollup_YYYY-MM.json に蓄積し、月次記事 transfers-roundup-YYYY-MM.md を再生成（追記方式）
- 元記事は削除し、旧URLは data/redirects.json 経由でまとめ記事へ301
- 事実は元記事本文の範囲のみ。集計（件数・チーム別）は本文中のリンクから機械的に数えるだけ
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

from . import io

ROOT = Path(__file__).resolve().parent.parent
NEWS_DIR = ROOT / "src" / "content" / "news"
REDIRECTS = ROOT / "data" / "redirects.json"
ROLLUP_DIR = io.META_DIR / "news"
MIN_CHARS = 1000

KINDS = [  # (slugパターン, kind, 見出し)
    (re.compile(r"-first-cap-"), "cap1", "初キャップ"),
    (re.compile(r"-caps-weekly-"), "caps", "代表キャップ更新"),
    (re.compile(r"-departure-"), "dep", "退団"),
    (re.compile(r"-join-"), "join", "新加入"),
]
KIND_TITLE = {k: t for _, k, t in KINDS}
KIND_ORDER = ["join", "dep", "cap1", "caps"]
KIND_NOTE = {
    "join": "新シーズンに向けた加入が確認された選手",
    "dep": "所属チームを退団した選手",
    "cap1": "代表で初キャップを記録した選手",
    "caps": "代表キャップ数が更新された選手",
}
FM = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)


def _classify(slug: str):
    for pat, kind, _ in KINDS:
        if pat.search(slug):
            return kind
    return None


def _label(fm: str) -> str:
    m = re.search(r'tags:\s*\["([^"]+)"', fm)
    return m.group(1) if m else "その他"


def _collect() -> dict[str, list[dict]]:
    """月ごとの新規エントリを集め、元記事を削除してリダイレクトを追記する。"""
    new: dict[str, list[dict]] = {}
    redirects: dict[str, str] = {}
    for f in sorted(NEWS_DIR.glob("*.md")):
        slug = f.stem
        kind = _classify(slug)
        if not kind:
            continue
        m = FM.match(f.read_text(encoding="utf-8"))
        if not m:
            continue
        fm, body = m.groups()
        if re.search(r"^draft:\s*true", fm, re.M):
            continue
        if len(re.sub(r"\s", "", body)) >= MIN_CHARS:
            continue
        pd = re.search(r"pubDate:\s*(\d{4}-\d{2}-\d{2})", fm)
        if not pd:
            continue
        month = pd.group(1)[:7]
        for line in (l.strip() for l in body.strip().splitlines() if l.strip()):
            text = line if line.startswith("- ") else "- " + line
            new.setdefault(month, []).append(
                {"kind": kind, "label": _label(fm), "date": pd.group(1), "text": text})
        redirects[f"/news/{slug}"] = f"/news/transfers-roundup-{month}/"
        f.unlink()
    if redirects:
        r = json.loads(REDIRECTS.read_text(encoding="utf-8"))
        r.update(redirects)
        REDIRECTS.write_text(json.dumps(r, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
    return new


def _team_counts(texts: list[str]) -> Counter:
    c: Counter = Counter()
    for t in texts:
        for name in re.findall(r"\[([^\]]+)\]\(/teams/[^)#]+/\)", t):
            c[name] += 1
    return c


def _render(month: str, entries: list[dict]) -> str:
    y, mo = month.split("-")
    groups: dict[tuple, list[str]] = {}
    for e in entries:
        lines = groups.setdefault((e["kind"], e["label"]), [])
        if e["text"] not in lines:
            lines.append(e["text"])
    total = sum(len(v) for v in groups.values())
    labels = sorted({l for _, l in groups})
    out = [
        f"{y}年{int(mo)}月に確認された、加入・退団・代表キャップ更新の動きを{'・'.join(labels)}別にまとめた。"
        f"掲載は合計{total}件。各選手名のリンクから所属チームの名簿に進める。",
        "",
    ]
    for kind in KIND_ORDER:
        for k in sorted((k for k in groups if k[0] == kind), key=lambda k: -len(groups[k])):
            lines = groups[k]
            out += [f"## {k[1]}：{KIND_TITLE[kind]}（{len(lines)}件）", "",
                    f"{y}年{int(mo)}月に{KIND_NOTE[kind]}は{len(lines)}名。"]
            tc = _team_counts(lines)
            if kind in ("join", "dep"):
                top = [(n, c) for n, c in tc.most_common(3) if c >= 2]
                if top:
                    out[-1] += "チーム別で最も多かったのは" + "、".join(f"{n}（{c}名）" for n, c in top) + "。"
            out += ["", *lines, ""]
    return "\n".join(out).rstrip() + "\n"


def run() -> int:
    new = _collect()
    ROLLUP_DIR.mkdir(parents=True, exist_ok=True)
    for month, entries in new.items():
        p = ROLLUP_DIR / f"rollup_{month}.json"
        state = io.read_json(p, default=[])
        seen = {(s["kind"], s["label"], s["text"]) for s in state}
        state += [e for e in entries if (e["kind"], e["label"], e["text"]) not in seen]
        io.write_json(p, state)
        y, mo = month.split("-")
        last = max(e["date"] for e in state)
        labels = "・".join(sorted({e["label"] for e in state}))
        fm = [
            "---",
            f'title: "ラグビー移籍・代表キャップ動向まとめ（{y}年{int(mo)}月）"',
            f'description: "{y}年{int(mo)}月の{labels}における加入・退団・代表キャップ更新を一覧でまとめた月次レポート。"',
            f"pubDate: {last}",
            'category: "NEWS"',
            'tags: ["移籍", "加入", "キャップ更新", "月次まとめ"]',
            "draft: false",
            "---",
            "",
        ]
        (NEWS_DIR / f"transfers-roundup-{month}.md").write_text(
            "\n".join(fm) + _render(month, state), encoding="utf-8")
        print(f"[rollup] {month}: {len(state)} entries")
    return sum(len(v) for v in new.values())


if __name__ == "__main__":
    argparse.ArgumentParser(prog="pipeline.news_rollup").parse_args()
    run()
