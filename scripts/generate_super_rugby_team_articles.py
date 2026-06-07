#!/usr/bin/env python3
"""
Super Rugby 個別チーム記事ジェネレーター
- データソース: src/content/teams/super-rugby/*.md + data/super_rugby_katakana.json
- ハルシネーション対策: ファイル記載データのみ使用、AI不使用
- 出力: src/content/news/super-rugby-[slug]-2025-26.md
"""
import json
import re
import os
from datetime import date

TEAMS_DIR = "src/content/teams/super-rugby"
KATAKANA_FILE = "data/super_rugby_katakana.json"
OUTPUT_DIR = "src/content/news"
TODAY = date.today().isoformat()

POSITION_MAP = {
    "PR": "プロップ", "HO": "フッカー", "LO": "ロック",
    "FL": "フランカー", "No8": "ナンバーエイト", "FL/No8": "フランカー/No8",
    "SH": "スクラムハーフ", "SO": "スタンドオフ", "CTB": "センター",
    "WTB": "ウィング", "FB": "フルバック",
    # 英語表記ゆれ対応
    "Prop": "プロップ", "Hooker": "フッカー", "Lock": "ロック",
    "Flanker": "フランカー", "Back row": "バックロー",
    "Scrum-half": "スクラムハーフ", "Fly-half": "スタンドオフ",
    "Centre": "センター", "Wing": "ウィング", "Full-back": "フルバック",
}

COUNTRY_MAP = {
    "New Zealand": "ニュージーランド代表", "Australia": "オーストラリア代表",
    "Fiji": "フィジー代表", "Samoa": "サモア代表", "Tonga": "トンガ代表",
    "Argentina": "アルゼンチン代表", "South Africa": "南アフリカ代表",
    "France": "フランス代表", "England": "イングランド代表",
    "Scotland": "スコットランド代表", "Ireland": "アイルランド代表",
    "Wales": "ウェールズ代表", "Japan": "日本代表",
    "Italy": "イタリア代表", "USA": "アメリカ代表", "Canada": "カナダ代表",
    "Namibia": "ナミビア代表", "Romania": "ルーマニア代表",
    "Georgia": "グルジア代表", "Uruguay": "ウルグアイ代表",
    "Tonga ": "トンガ代表",
}


def load_katakana(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {p["name_en"]: p["name_ja"] for p in data}


def parse_team_md(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # frontmatter
    fm_match = re.search(r"---\n(.*?)\n---", content, re.DOTALL)
    fm = fm_match.group(1) if fm_match else ""
    title_match = re.search(r'title:\s*"(.+?)"', fm)
    title = title_match.group(1) if title_match else ""

    # 基本データ表
    rows = {}
    for row in re.finditer(r"\|\s*(.+?)\s*\|\s*(.+?)\s*\|", content):
        k, v = row.group(1).strip(), row.group(2).strip()
        if k not in ("項目", ":---"):
            rows[k] = v

    # 歴史テキスト
    hist_match = re.search(r"## チームの歴史と特徴\n\n(.+?)(?=\n##|\Z)", content, re.DOTALL)
    history = hist_match.group(1).strip() if hist_match else ""

    # 代表経験あり選手
    capped = []
    capped_section = re.search(r"### 代表経験あり\n\n(.+?)(?=###|\Z)", content, re.DOTALL)
    if capped_section:
        pattern = r"\*\*([A-Za-z][A-Za-z'\-\s\.]+)\*\*（([^）]+)）(?:、([A-Za-z][A-Za-z\-]*(?:\s+[A-Za-z][A-Za-z\-]*)*)(?:\s+\((\d+)\))?)?"
        for m in re.finditer(pattern, capped_section.group(1)):
            capped.append({
                "name_en": m.group(1).strip(),
                "position": m.group(2).strip(),
                "country": m.group(3).strip() if m.group(3) else "",
                "caps": int(m.group(4)) if m.group(4) else 0,
            })

    # その他選手
    others = []
    other_section = re.search(r"### その他在籍選手\n\n(.+?)(?=##|\Z)", content, re.DOTALL)
    if other_section:
        pattern = r"\*\*([A-Za-z][A-Za-z'\-\s\.]+)\*\*（([^）]+)）"
        for m in re.finditer(pattern, other_section.group(1)):
            others.append({
                "name_en": m.group(1).strip(),
                "position": m.group(2).strip(),
            })

    return {
        "title": title,
        "rows": rows,
        "history": history,
        "capped": capped,
        "others": others,
        "slug": os.path.basename(path).replace(".md", ""),
    }


def render_article(team, katakana):
    slug = team["slug"]
    title = team["title"]
    rows = team["rows"]
    league = rows.get("リーグ", "スーパーラグビー・パシフィック")
    founded = rows.get("創設年", "")
    home = rows.get("本拠地", "")
    titles = rows.get("タイトル歴", "なし")

    # タグ生成
    team_name_ja = re.sub(r"【チーム紹介】(.+?)：.*", r"\1", title)
    tags = ["スーパーラグビー", "チーム紹介", "2025-26", team_name_ja]

    # description
    desc = f"{team_name_ja}の2025-26シーズン完全ガイド。チームの歴史・タイトル歴・在籍選手一覧を詳細解説。"

    lines = []
    # frontmatter
    lines.append("---")
    lines.append(f'title: "{title}"')
    lines.append(f'description: "{desc}"')
    lines.append(f"pubDate: {TODAY}")
    lines.append('category: "COLUMN"')
    tags_str = ", ".join(f'"{t}"' for t in tags)
    lines.append(f"tags: [{tags_str}]")
    lines.append("---")
    lines.append("")

    # チーム概要
    lines.append("## チーム概要")
    lines.append("")
    lines.append("| 項目 | 詳細 |")
    lines.append("| :--- | :--- |")
    lines.append(f"| リーグ | {league} |")
    if founded:
        lines.append(f"| 創設年 | {founded} |")
    if home:
        lines.append(f"| 本拠地 | {home} |")
    lines.append(f"| タイトル歴 | {titles} |")
    lines.append("")

    # 歴史
    if team["history"]:
        lines.append("## チームの歴史と特徴")
        lines.append("")
        lines.append(team["history"])
        lines.append("")

    # 代表経験あり選手
    if team["capped"]:
        lines.append("## 代表経験あり選手（2025-26シーズン）")
        lines.append("")
        lines.append("| 選手名 | カタカナ | ポジション | 代表 | caps |")
        lines.append("| :--- | :--- | :--- | :--- | ---: |")
        for p in team["capped"]:
            name_ja = katakana.get(p["name_en"], p["name_en"])
            pos = POSITION_MAP.get(p["position"], p["position"])
            country_raw = p["country"].strip().rstrip()
            country_ja = COUNTRY_MAP.get(country_raw, country_raw)
            caps = str(p["caps"]) if p["caps"] else "—"
            lines.append(f"| {p['name_en']} | {name_ja} | {pos} | {country_ja} | {caps} |")
        lines.append("")

    # その他選手
    if team["others"]:
        lines.append("## その他在籍選手（2025-26シーズン）")
        lines.append("")
        lines.append("| 選手名 | カタカナ | ポジション |")
        lines.append("| :--- | :--- | :--- |")
        for p in team["others"]:
            name_ja = katakana.get(p["name_en"], p["name_en"])
            pos = POSITION_MAP.get(p["position"], p["position"])
            lines.append(f"| {p['name_en']} | {name_ja} | {pos} |")
        lines.append("")

    # フッター
    lines.append("---")
    lines.append(f"*データ基準日: {TODAY}*")

    return "\n".join(lines)


def main():
    katakana = load_katakana(KATAKANA_FILE)
    print(f"カタカナDB: {len(katakana)}名読み込み\n")

    for fname in sorted(os.listdir(TEAMS_DIR)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(TEAMS_DIR, fname)
        team = parse_team_md(path)
        slug = team["slug"]

        article = render_article(team, katakana)
        out_path = os.path.join(OUTPUT_DIR, f"super-rugby-{slug}-2025-26.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(article)

        capped_count = len(team["capped"])
        others_count = len(team["others"])
        print(f"✓ {slug}: 代表{capped_count}名 + その他{others_count}名 → {out_path}")

    print("\n完了")


if __name__ == "__main__":
    main()
