"""P3-1: 差分 → テンプレ記事生成（05 自動更新 / 差分検知→ニュース自動生成）。

    python3 -m pipeline.news_gen [--date YYYY-MM-DD]

`_meta/diff/{date}_{league}.json`（P1-8 pipeline.diffs.detect の出力）を読み、
LLM を使わずテンプレ穴埋めのみで `src/content/news/*.md` を生成する（原則2: 事実の創作禁止）。
本文はテンプレ文＋master の値＋関連選手ページへのリンクのみ。背景説明・感想・展望は書かない。

処理する差分イベント（05の表に対応）:
  - signings / transfers（team_id 変化） → 「{選手名}が{チーム名}に加入」
    （05の表は1行にまとめて同一テンプレを指定しているため、transfers は to_team_id で加入扱いにする）
  - departures（detect.py 側で既に「2回連続消失」確認済みのもののみ渡ってくる） →
    「{選手名}が{チーム名}を退団」
  - first_caps → 「{選手名}が{国}代表初キャップ」
  - caps_updates → 1件ずつは作らず、ISO週（YYYY-Www）単位で
    `_meta/news/caps_updates_{league}_{isoweek}.json` に累積し、週次まとめ記事を生成する
    （同じ週の間は同一 slug の記事を上書き更新＝冪等）
  - newly_finished_rounds → master の matches を引いてスコア表のみの「{リーグ}第{節}節 結果まとめ」

保守的な設計判断（00 の原則5「判断に迷ったら最も保守的」に従い明記）:
  - 選手名 / チーム名 / 代表国名など、テンプレの穴埋めに必要な値が欠けている場合は
    その記事を生成しない（空欄を残さない・捏造しない）。
  - 選手ページへのリンクは、対象 id が「現在の」master players に存在し slug が
    引けるときのみ張る。退団済みで master から消えた id は平文の氏名のみにする。
  - departures と transfers は detect.diff_players() 内で id 単位に排他的に分類される
    （同じ実行で同じ id が両方に載ることはない）ため、「移籍先検出時は移籍記事に統合」の
    ための追加の突合ロジックは実装しない。リーグをまたぐ移籍（退団後に別リーグで signings
    として出現）はソースごとに id 体系が異なり安全に突合できないため統合しない
    （誤って統合するより退団記事と加入記事が別々に出る方が保守的）。
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import date as date_cls, datetime
from pathlib import Path
from typing import Optional

from pipeline import io

LEAGUE_LABEL_JA: dict[str, str] = {
    "league-one-d1": "リーグワン",
    "league-one-d2": "リーグワン",
    "league-one-d3": "リーグワン",
    "top14": "Top14",
    "super-rugby": "スーパーラグビー",
    "urc": "URC",
    "premiership": "プレミアシップ",
    "nrl": "NRL",
    "national": "代表",
    "sevens-national": "セブンズ代表",
    "age-grade": "年代別代表",
    "university": "大学",
    "highschool": "高校",
}

NEWS_DIR = io.REPO_ROOT / "src" / "content" / "news"
NEWS_META_DIR = io.META_DIR / "news"


def league_label(league: str) -> str:
    return LEAGUE_LABEL_JA.get(league, league)


# --- チーム名 → チームページURL 解決（相互リンク用） -------------------------
# data/teams.json（サイトのURL生成元）を単一の真実として使う。日本語チーム名／
# エイリアスに一致したときだけ /teams/{league}/{slug}/ を返す。一致しなければ None
# （＝平文のまま。大学・海外下部リーグ等ページが無いチームはリンクしない）。
_TEAM_URL_CACHE: Optional[dict[str, str]] = None


def _build_team_url_map() -> dict[str, str]:
    global _TEAM_URL_CACHE
    if _TEAM_URL_CACHE is not None:
        return _TEAM_URL_CACHE
    m: dict[str, str] = {}
    teams = io.read_json(io.REPO_ROOT / "data" / "teams.json", default=[])
    for t in teams or []:
        slug, lg = t.get("slug"), t.get("league")
        if not slug or not lg or slug == "2025-26":
            continue
        url = f"/teams/{lg}/{slug}/"
        for key in (t.get("team_name"), t.get("team_en_name")):
            if key:
                m.setdefault(key.strip(), url)
    # team_names_jp.json のエイリアス／日本語名も引けるようにする
    names_jp = io.read_json(io.REPO_ROOT / "data" / "team_names_jp.json", default={})
    for lg_map in (names_jp or {}).values():
        if not isinstance(lg_map, dict):
            continue
        for data in lg_map.values():
            jp = (data or {}).get("jp")
            url = m.get(jp) if jp else None
            if not url:
                continue
            for alias in (data.get("aliases") or []):
                m.setdefault(alias.strip(), url)
    _TEAM_URL_CACHE = m
    return m


def team_url(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    return _build_team_url_map().get(name.strip())


def team_md(name: Optional[str]) -> Optional[str]:
    """チーム名（ページがあれば Markdown リンク、無ければ平文）。名称不明なら None。"""
    if not name:
        return None
    url = team_url(name)
    return f"[{name}]({url})" if url else name


# --- 検証済み Instagram 埋め込み（手動キュレーション） -----------------------
# data/manual/instagram_embeds.json に「本人公式アカウントをブラウザで確認済み」の
# 投稿だけを player_id 単位で置く。捏造・未確認アカウントは載せない（03_VALIDATION）。
_IG_EMBEDS_CACHE: Optional[dict[str, dict]] = None


def _ig_embeds() -> dict[str, dict]:
    global _IG_EMBEDS_CACHE
    if _IG_EMBEDS_CACHE is None:
        raw = io.read_json(io.MANUAL_DIR / "instagram_embeds.json", default={})
        _IG_EMBEDS_CACHE = {k: v for k, v in (raw or {}).items()
                            if isinstance(v, dict) and v.get("permalink")}
    return _IG_EMBEDS_CACHE


def instagram_block(permalink: str) -> str:
    return (
        f'<blockquote class="instagram-media" data-instgrm-permalink="{permalink}" '
        f'data-instgrm-version="14" style="max-width:540px;width:100%;margin:1.5rem auto;">'
        f"</blockquote>"
    )


def team_display_name(team: Optional[dict]) -> Optional[str]:
    """team_id → 表示名（name_ja優先、無ければname_en）。master.ts teamDisplayName と同じ規則。"""
    if not team:
        return None
    return team.get("name_ja") or team.get("name_en") or None


def player_display_name(entry: dict) -> Optional[str]:
    return entry.get("name_ja") or entry.get("name_en") or None


def player_link(entry: dict, players_by_id: dict[str, dict]) -> Optional[str]:
    """現master に存在する id のみ選手ページへのリンクにする。無ければ None。"""
    p = players_by_id.get(entry.get("id"))
    if not p or not p.get("slug"):
        return None
    return f"/players/{p['slug']}/"


def _player_md(entry: dict, players_by_id: dict[str, dict]) -> Optional[str]:
    """氏名（リンクが張れれば Markdown リンク、無ければ平文）。氏名不明なら None。"""
    name = player_display_name(entry)
    if not name:
        return None
    link = player_link(entry, players_by_id)
    return f"[{name}]({link})" if link else name


@dataclass
class Article:
    slug: str
    title: str
    body: str
    tags: list[str] = field(default_factory=list)
    pub_date: str = ""
    source_diff: str = ""
    category: str = "auto"

    def filename(self) -> str:
        return f"{self.slug}.md"

    def to_markdown(self) -> str:
        tags_yaml = "[" + ", ".join(f'"{t}"' for t in self.tags) + "]"
        lines = [
            "---",
            f'title: "{self.title}"',
            f"pubDate: {self.pub_date}",
            f'category: "{self.category}"',
            f"tags: {tags_yaml}",
            f'source_diff: "{self.source_diff}"',
            "draft: false",
            "---",
            "",
            self.body.rstrip(),
            "",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 記事ビルダー（すべて純関数。ファイルI/Oは行わない）
# ---------------------------------------------------------------------------

def build_join_articles(diff: dict, *, players_by_id: dict[str, dict], teams_by_id: dict[str, dict],
                        pub_date: str, source_diff: str) -> list[Article]:
    league = diff["league"]
    label = league_label(league)
    events: list[tuple[dict, Optional[str]]] = [(e, e.get("team_id")) for e in diff.get("signings", [])]
    events += [(e, e.get("to_team_id")) for e in diff.get("transfers", [])]

    articles: list[Article] = []
    for entry, team_id in events:
        name = player_display_name(entry)
        team_name = team_display_name(teams_by_id.get(team_id))
        if not name or not team_name:
            continue
        who = _player_md(entry, players_by_id) or name
        title = f"{name}が{team_name}に加入"
        body = f"{who}が{team_md(team_name)}（{label}）に加入した。"
        slug = f"{league}-join-{entry['id']}-{pub_date}"
        articles.append(Article(slug=slug, title=title, body=body, tags=[label, "加入"],
                                pub_date=pub_date, source_diff=source_diff))
    return articles


def build_departure_articles(diff: dict, *, players_by_id: dict[str, dict], teams_by_id: dict[str, dict],
                             pub_date: str, source_diff: str) -> list[Article]:
    league = diff["league"]
    label = league_label(league)
    articles: list[Article] = []
    for entry in diff.get("departures", []):
        name = player_display_name(entry)
        team_name = team_display_name(teams_by_id.get(entry.get("team_id")))
        if not name or not team_name:
            continue
        who = _player_md(entry, players_by_id) or name
        title = f"{name}が{team_name}を退団"
        body = f"{who}が{team_md(team_name)}（{label}）を退団した。"
        slug = f"{league}-departure-{entry['id']}-{pub_date}"
        articles.append(Article(slug=slug, title=title, body=body, tags=[label, "退団"],
                                pub_date=pub_date, source_diff=source_diff))
    return articles


def build_first_cap_articles(diff: dict, *, players_by_id: dict[str, dict],
                             pub_date: str, source_diff: str) -> list[Article]:
    league = diff["league"]
    label = league_label(league)
    articles: list[Article] = []
    for entry in diff.get("first_caps", []):
        name = player_display_name(entry)
        team = entry.get("team")
        if not name or not team:
            continue
        who = _player_md(entry, players_by_id) or name
        title = f"{name}が{team}代表初キャップ"
        body = f"{who}が{team}代表で初キャップを記録した。"
        slug = f"{league}-first-cap-{entry['id']}-{pub_date}"
        articles.append(Article(slug=slug, title=title, body=body, tags=[label, "初キャップ"],
                                pub_date=pub_date, source_diff=source_diff))
    return articles


def build_round_result_articles(diff: dict, *, matches_by_id: dict[str, dict], teams_by_id: dict[str, dict],
                                pub_date: str, source_diff: str) -> list[Article]:
    league = diff["league"]
    label = league_label(league)
    articles: list[Article] = []
    for rnd in diff.get("newly_finished_rounds", []):
        round_no = rnd.get("round")
        season = rnd.get("season")
        if round_no is None:
            continue
        rows: list[tuple[str, int, int, str]] = []
        for mid in rnd.get("match_ids", []):
            m = matches_by_id.get(mid)
            if not m:
                continue
            home = team_display_name(teams_by_id.get(m.get("home_team_id")))
            away = team_display_name(teams_by_id.get(m.get("away_team_id")))
            hs, aws = m.get("home_score"), m.get("away_score")
            if not home or not away or hs is None or aws is None:
                continue
            rows.append((home, hs, aws, away))
        if not rows:
            continue
        title = f"{label}第{round_no}節 結果まとめ"
        lines = ["| ホーム | スコア | アウェイ |", "| :--- | :---: | :--- |"]
        for home, hs, aws, away in rows:
            lines.append(f"| {team_md(home)} | {hs} - {aws} | {team_md(away)} |")
        body = "\n".join(lines)
        slug = f"{league}-round-{round_no}-{season or pub_date}"
        articles.append(Article(slug=slug, title=title, body=body, tags=[label, "結果"],
                                pub_date=pub_date, source_diff=source_diff))
    return articles


def build_call_up_articles(diff: dict, *, players_by_id: dict[str, dict],
                           pub_date: str, source_diff: str) -> list[Article]:
    """gap B: 招集・合宿メンバー発表イベント（diff["call_ups"]）→ ロースター記事。

    本文はイベントの事実（期間・会場・メンバー一覧＋選手ページリンク）と、前回招集からの
    「新たに選出された選手」（機械的差分）のみ。「復帰」等の含意や展望は書かない
    （03_VALIDATION 原則2）。slug は news_id 由来で冪等（再実行で同一記事を上書き）。
    """
    league = diff["league"]
    label = league_label(league)
    articles: list[Article] = []
    for ev in diff.get("call_ups", []):
        news_id = ev.get("news_id")
        members = ev.get("members", [])
        if not news_id or not members:
            continue
        raw_title = (ev.get("title") or "").strip()
        base = raw_title.replace("のお知らせ", "").strip() or f"{label} 招集メンバー"
        n = ev.get("member_count") or len(members)
        title = f"{base}（{n}名）"

        lines: list[str] = [f"{base}（{n}名）が発表された。", ""]
        if ev.get("start_date"):
            lines.append(f"- 期間: {ev['start_date']}〜")
        if ev.get("venue"):
            lines.append(f"- 会場: {ev['venue']}")
        lines.append("")

        stats_lines = _call_up_stats_lines(members, players_by_id)
        if stats_lines:
            lines.append("**メンバー構成**")
            lines.extend(stats_lines)
            lines.append("")

        group_label = {"FW": "FW（フォワード）", "BK": "BK（バックス）"}
        seen_groups = [g for g in ("FW", "BK") if any(m.get("position_group") == g for m in members)]
        other = [m for m in members if m.get("position_group") not in ("FW", "BK")]
        for g in seen_groups:
            lines.append(f"**{group_label[g]}**")
            for m in members:
                if m.get("position_group") != g:
                    continue
                lines.append(_call_up_member_line(m, players_by_id))
            lines.append("")
        if other:
            lines.append("**その他**")
            for m in other:
                lines.append(_call_up_member_line(m, players_by_id))
            lines.append("")

        # 検証済みInstagram写真（本人公式アカウントのみ）をメンバー順に埋め込む。
        # キーは選手ページのslug（選手ページ側と共有）。
        embeds = _ig_embeds()
        def _emb_for(m: dict) -> Optional[dict]:
            p = players_by_id.get(m.get("id"))
            return embeds.get(p.get("slug")) if p and p.get("slug") else None
        photo_members = [m for m in members if _emb_for(m)]
        if photo_members:
            lines.append("## 選手フォト")
            lines.append("")
            for m in photo_members:
                emb = _emb_for(m)
                name = _player_md(m, players_by_id) or player_display_name(m) or ""
                acct = emb.get("account")
                cap = f"{name}（Instagram [@{acct}](https://www.instagram.com/{acct}/)）" if acct else name
                lines.append(cap)
                lines.append("")
                lines.append(instagram_block(emb["permalink"]))
                lines.append("")

        new_members = ev.get("new_members", [])
        if ev.get("has_previous") and new_members:
            names = [_player_md(m, players_by_id) or player_display_name(m) for m in new_members]
            names = [x for x in names if x]
            if names:
                lines.append("**前回招集から新たに選出**")
                lines.append("、".join(names))
                lines.append("")

        body = "\n".join(lines).rstrip()
        slug = f"{league}-callup-{news_id}"
        tags = [label, "招集"]
        if ev.get("kind") == "camp":
            tags.append("合宿")
        articles.append(Article(slug=slug, title=title, body=body, tags=tags,
                                pub_date=pub_date, source_diff=source_diff))
    return articles


def _call_up_stats_lines(members: list[dict], players_by_id: dict[str, dict]) -> list[str]:
    """メンバー一覧から機械的に集計できる構成情報のみを箇条書きにする（原則2: 事実の創作禁止）。
    caps / club_raw が揃っている件数だけを対象にする（欠損は集計から除外し、捏造しない）。"""
    lines: list[str] = []

    uncapped = [m for m in members if m.get("caps") == 0]
    if uncapped:
        names = [_player_md(m, players_by_id) or player_display_name(m) for m in uncapped]
        names = [x for x in names if x]
        if names:
            lines.append(f"- 初選出（0キャップ）: {len(names)}名 — " + "、".join(names))

    clubs = {m["club_raw"] for m in members if m.get("club_raw")}
    if clubs:
        lines.append(f"- 所属クラブ・大学: {len(clubs)}")

    capped = [m for m in members if isinstance(m.get("caps"), int) and m["caps"] > 0]
    if capped:
        top = max(capped, key=lambda m: m["caps"])
        who = _player_md(top, players_by_id) or player_display_name(top)
        if who:
            lines.append(f"- 最多キャップ: {who}（{top['caps']}キャップ）")

    return lines


def _call_up_member_line(m: dict, players_by_id: dict[str, dict]) -> str:
    who = _player_md(m, players_by_id) or player_display_name(m) or "（氏名不明）"
    parts: list[str] = []
    if m.get("club_raw"):
        parts.append(team_md(m["club_raw"]) or m["club_raw"])
    caps = m.get("caps")
    if isinstance(caps, int):
        parts.append(f"{caps}キャップ")
    suffix = f"（{' / '.join(parts)}）" if parts else ""
    return f"- {who}{suffix}"


def build_articles_for_diff(diff: dict, *, players_by_id: dict[str, dict], teams_by_id: dict[str, dict],
                            matches_by_id: dict[str, dict], pub_date: str, source_diff: str) -> list[Article]:
    """caps_updates（週次まとめ）を除く、1回の diff から作れる記事すべて。"""
    articles: list[Article] = []
    articles += build_join_articles(diff, players_by_id=players_by_id, teams_by_id=teams_by_id,
                                    pub_date=pub_date, source_diff=source_diff)
    articles += build_departure_articles(diff, players_by_id=players_by_id, teams_by_id=teams_by_id,
                                         pub_date=pub_date, source_diff=source_diff)
    articles += build_first_cap_articles(diff, players_by_id=players_by_id,
                                         pub_date=pub_date, source_diff=source_diff)
    articles += build_round_result_articles(diff, matches_by_id=matches_by_id, teams_by_id=teams_by_id,
                                            pub_date=pub_date, source_diff=source_diff)
    articles += build_call_up_articles(diff, players_by_id=players_by_id,
                                       pub_date=pub_date, source_diff=source_diff)
    return articles


# ---------------------------------------------------------------------------
# caps_updates 週次まとめ（ISO週単位で累積 → 記事）
# ---------------------------------------------------------------------------

def iso_week_str(d: date_cls) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def merge_caps_updates(existing: list[dict], new_entries: list[dict]) -> list[dict]:
    """id単位でマージ。from_countは週内最初の値を保持、to_countは最新（最大）を保持する。"""
    by_id: dict[str, dict] = {e["id"]: dict(e) for e in existing}
    for e in new_entries:
        pid = e["id"]
        if pid in by_id:
            prev = by_id[pid]
            prev["to_count"] = max(prev.get("to_count") or 0, e.get("to_count") or 0)
            prev["team"] = e.get("team") or prev.get("team")
            prev["name_en"] = e.get("name_en") or prev.get("name_en")
            prev["name_ja"] = e.get("name_ja") or prev.get("name_ja")
        else:
            by_id[pid] = dict(e)
    return [by_id[k] for k in sorted(by_id)]


def build_caps_weekly_article(league: str, iso_week: str, entries: list[dict], *,
                              players_by_id: dict[str, dict], pub_date: str,
                              source_diff: str) -> Optional[Article]:
    if not entries:
        return None
    label = league_label(league)
    lines: list[str] = []
    for entry in sorted(entries, key=lambda e: e["id"]):
        name = player_display_name(entry)
        team = entry.get("team")
        frm, to = entry.get("from_count"), entry.get("to_count")
        if not name or not team or frm is None or to is None:
            continue
        who = _player_md(entry, players_by_id) or name
        lines.append(f"- {who}: {team}代表{frm}→{to}キャップ")
    if not lines:
        return None
    title = f"{label}週間代表キャップ更新まとめ（{iso_week}）"
    body = "\n".join(lines)
    slug = f"{league}-caps-weekly-{iso_week}"
    return Article(slug=slug, title=title, body=body, tags=[label, "キャップ更新"],
                   pub_date=pub_date, source_diff=source_diff)


# ---------------------------------------------------------------------------
# I/O（main からのみ呼ぶ）
# ---------------------------------------------------------------------------

def write_articles(articles: list[Article], out_dir: Path = NEWS_DIR) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for a in articles:
        p = out_dir / a.filename()
        p.write_text(a.to_markdown(), encoding="utf-8")
        paths.append(p)
    return paths


def _diff_files_for_date(target_date: str) -> list[Path]:
    diff_dir = io.META_DIR / "diff"
    if not diff_dir.exists():
        return []
    return sorted(diff_dir.glob(f"{target_date}_*.json"))


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="pipeline.news_gen")
    ap.add_argument("--date", default=None, help="対象diffの日付 YYYY-MM-DD（省略時は本日 JST）")
    args = ap.parse_args(argv)
    target_date = args.date or datetime.now(io.JST).strftime("%Y-%m-%d")

    files = _diff_files_for_date(target_date)
    if not files:
        print(f"[news] {target_date} の diff ファイルなし。生成対象なし。")
        return 0

    total = 0
    for path in files:
        diff = io.read_json(path, default=None)
        if not diff:
            continue
        league = diff["league"]
        source_diff = path.name

        players = io.read_records(io.players_path(league))
        players_by_id = {p["id"]: p for p in players}
        teams = io.read_records(io.teams_path(league))
        teams_by_id = {t["id"]: t for t in teams}

        seasons = {r.get("season") for r in diff.get("newly_finished_rounds", []) if r.get("season")}
        matches_by_id: dict[str, dict] = {}
        for season in seasons:
            for m in io.read_records(io.matches_path(league, season)):
                matches_by_id[m["id"]] = m

        articles = build_articles_for_diff(
            diff, players_by_id=players_by_id, teams_by_id=teams_by_id,
            matches_by_id=matches_by_id, pub_date=target_date, source_diff=source_diff,
        )

        iso_week = iso_week_str(date_cls.fromisoformat(target_date))
        state_path = NEWS_META_DIR / f"caps_updates_{league}_{iso_week}.json"
        existing = io.read_json(state_path, default=[])
        merged = merge_caps_updates(existing, diff.get("caps_updates", []))
        if merged:
            io.write_json(state_path, merged)
            weekly = build_caps_weekly_article(
                league, iso_week, merged, players_by_id=players_by_id,
                pub_date=target_date, source_diff=source_diff,
            )
            if weekly:
                articles.append(weekly)

        write_articles(articles, NEWS_DIR)
        total += len(articles)
        print(f"[news] {league}: {len(articles)} 記事生成 ({source_diff})")

    print(f"[news] 合計 {total} 記事")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
