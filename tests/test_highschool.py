"""P5-6: 高校名簿スクレイパーをオフラインの行データ/フィクスチャで検証
（ネットワークアクセスなし）。行データは実ページ（2026-07-19確認）のレイアウトを模す。"""
import pathlib

from pipeline.scrape import highschool as hs
from pipeline.transform import normalize

FX = pathlib.Path(__file__).parent / "fixtures"


# --- r-cms系（関西学院高等部の実レイアウト: 氏名→かな→学年→身長→出身中→体重） ---
KGH_LINES = [
    "メンバー一覧",
    "写真", "名前", "学年", "身長", "出身校", "ポジション", "体重",
    "田中 章雅", "たなかあきまさ", "関西学院大学", "部長",
    "安藤 昌宏", "あんどうまさひろ", "天理大学", "監督",
    "新川 温橙", "しんかわはると", "3年生", "170cm", "宝塚市立山手台中", "79kg",
    "辻井 稀子", "つじいきこ", "関西学院中学部", "マネージャー",
    "徳永 伊吹", "とくながいぶき", "172cm", "東大阪市立枚岡中", "76kg",
]

# --- r-cms系（名古屋: 中高一貫1〜6年生表記。かな→氏名→学年） ---
NAGOYA_LINES = [
    "メンバー一覧",
    "イシイ ダイキ", "石井 太基", "4年生",
    "アンドウ ヒョウガ", "安東 彪冴", "6年生",
    "ナカムラ チュウタ", "中村 忠太", "2年生",  # 中学部員 -> 除外
]

# --- bukatsunavi系（目黒学院: 氏名→ポジション→学年。スタッフは氏名→肩書） ---
MEGURO_LINES = [
    "竹内 圭介", "監督",
    "今関 大輔", "中学部 監督",
    "渥美 瑠海", "WTB、FB", "3年生", "【出身中学校・出身スクール】", "京華中・ワセダクラブ",
    "伊藤 琉真", "CTB", "3年生",
]

# --- 学年別ページ系（流経大柏: ポジション+氏名の複合行。学年はページ見出し） ---
RYUKEI_LINES = [
    "3年生の選手紹介(2025年4月)",
    "PR 石村 ビシャル",
    "FL ナモア・フェレティリキ",
    "NO.8 阿部 虎生",
    "FB 髙梨 太吾",
]

# --- WordPress系（慶應志木: 学年→ポジション→氏名→かな。field_direction=before） ---
KEIO_LINES = [
    "部員紹介",
    "3年生 /", "LO", "No.8", "伊東 凱", "いとう がい",
    "3年生 /", "WTB", "北 蓮輝", "きた はずき", "リーダー",
    "2年生 /", "PR", "山田 太郎", "やまだ たろう",
]

# --- Wix系（御所実業: 氏名→かな(断片割れあり)→ポジション行。学年はページ見出し） ---
GOSE_LINES = [
    "3年生 | 御所実業高校ラグビー部ホームページ",
    "岡本 脩磨", "おかもと しゅうま", "ポジション FL",
    "押野 虎太朗", "おし", "の こたろう", "ポジション LO NO8",
    "金澤 晃大", "かなざわ こうた", "ポジション LO",
]


def test_kgh_layout_extracts_players_and_excludes_staff_and_manager():
    recs = hs._extract_records(KGH_LINES, scheme="hs")
    by = {r["kanji"]: r for r in recs}
    assert "新川 温橙" in by and by["新川 温橙"]["grade"] == 3
    assert by["新川 温橙"]["kana"] == "しんかわはると"
    # 部長・監督・マネージャーは除外
    assert "田中 章雅" not in by and "安藤 昌宏" not in by and "辻井 稀子" not in by
    # 学年列が空でも身長+体重が揃う行は採用（値は保持しない）
    assert "徳永 伊吹" in by and by["徳永 伊吹"]["grade"] is None
    assert "height_cm" not in by["徳永 伊吹"] and "weight_kg" not in by["徳永 伊吹"]


def test_nagoya_unified6_maps_grades_and_drops_junior_high():
    recs = hs._extract_records(NAGOYA_LINES, scheme="unified6")
    by = {r["kanji"]: r for r in recs}
    assert by["石井 太基"]["grade"] == 1  # 4年生 -> 高1
    assert by["安東 彪冴"]["grade"] == 3  # 6年生 -> 高3
    assert by["石井 太基"]["kana"] == "イシイダイキ"
    assert "中村 忠太" not in by  # 2年生=中学部員は収集対象外


def test_meguro_layout_staff_title_line_is_not_a_player():
    recs = hs._extract_records(MEGURO_LINES, scheme="hs")
    names = {r["kanji"] for r in recs}
    assert "竹内 圭介" not in names  # 監督
    assert "中学部 監督" not in names  # 肩書入り行を氏名と誤認しない
    by = {r["kanji"]: r for r in recs}
    assert by["渥美 瑠海"]["position"] == "WTB/FB" and by["渥美 瑠海"]["grade"] == 3
    assert by["伊藤 琉真"]["position"] == "CTB"


def test_ryukei_combined_pos_name_lines_with_page_grade():
    recs = hs._extract_records(RYUKEI_LINES, scheme="hs")
    by = {r["kanji"]: r for r in recs}
    assert by["石村 ビシャル"] == {"kanji": "石村 ビシャル", "kana": None, "grade": 3, "position": "PR"}
    assert "ナモア・フェレティリキ" in by  # カタカナ+中点氏名
    assert by["阿部 虎生"]["position"] == "NO8"
    assert by["髙梨 太吾"]["grade"] == 3


def test_keio_direction_before_takes_preceding_grade_and_position():
    recs = hs._extract_records(KEIO_LINES, scheme="hs", direction="before")
    by = {r["kanji"]: r for r in recs}
    assert by["伊東 凱"]["grade"] == 3 and by["伊東 凱"]["position"] == "NO8"
    assert by["北 蓮輝"]["kana"] == "きたはずき"  # 役職語「リーダー」をかなに混ぜない
    assert by["山田 太郎"]["grade"] == 2 and by["山田 太郎"]["position"] == "PR"


def test_gose_kana_fragments_merged_and_no_neighbor_borrow():
    recs = hs._extract_records(GOSE_LINES, scheme="hs")
    by = {r["kanji"]: r for r in recs}
    assert by["押野 虎太朗"]["kana"] == "おしのこたろう"  # 断片行の結合
    assert by["押野 虎太朗"]["position"] == "LO/NO8"
    assert by["岡本 脩磨"]["position"] == "FL"  # 隣の選手のポジションを借用しない
    assert by["金澤 晃大"]["position"] == "LO"
    assert all(r["grade"] == 3 for r in recs)  # ページ見出しから学年補完


def test_grade_regex_does_not_match_year_numbers():
    # 「2025年U17オール東京」等の年号・代表歴行を学年と誤認しない
    lines = ["渥美 瑠海", "WTB、FB", "2025年U17オール東京"]
    recs = hs._extract_records(lines, scheme="hs")
    assert recs[0]["grade"] is None


def test_player_highschool_is_minor_and_minimal_fields():
    rec = {"kanji": "押野 虎太朗", "kana": "おしのこたろう", "grade": 3, "position": "LO/NO8"}
    player, warns = normalize.player_highschool(
        rec, school_name="御所実業高校",
        source_url="https://www.goseihsrugbyteam.com/複製-2年生-2")
    assert player is not None, warns
    assert player["is_minor"] is True
    assert player["league"] == "highschool"
    assert player["team_id"] is None
    # 未成年ポリシー: 生年月日・身長体重・SNS・画像は保持しない
    assert player["birthdate"] is None
    assert player["height_cm"] is None and player["weight_kg"] is None
    assert player["instagram"] is None and player["image_url"] is None
    edu = player["education"]
    assert len(edu) == 1 and edu[0]["type"] == "hs"
    assert edu[0]["name_raw"] == "御所実業高校"
    assert edu[0]["grad_year"] is not None


def test_player_highschool_grad_year_calculation():
    # 2026年7月時点の3年生 -> 2027年3月卒業
    assert normalize._hs_grad_year(3, "2026-07-19T12:00:00+09:00") == 2027
    assert normalize._hs_grad_year(1, "2026-07-19T12:00:00+09:00") == 2029
    # 年度またぎ（1-3月は前年度）: 2027年2月時点の3年生 -> 2027年3月卒業
    assert normalize._hs_grad_year(3, "2027-02-01T12:00:00+09:00") == 2027
    assert normalize._hs_grad_year(None, "2026-07-19T12:00:00+09:00") is None


def test_player_highschool_requires_name():
    player, warns = normalize.player_highschool(
        {"kanji": None, "kana": None, "grade": 2, "position": None},
        school_name="御所実業高校", source_url="https://www.goseihsrugbyteam.com/")
    assert player is None and warns


def test_collect_school_without_roster_urls_warns_and_skips():
    res = hs._collect_school({"name": "テスト高校", "roster_urls": [], "note": "名簿未公開"})
    assert res["records"] == []
    assert any("テスト高校" in w and "スキップ" in w for w in res["warnings"])


def test_collect_school_fetch_failure_warns(monkeypatch):
    monkeypatch.setattr(hs, "_get_html", lambda url: None)
    monkeypatch.setattr(hs.time, "sleep", lambda s: None)
    res = hs._collect_school({
        "name": "テスト高校", "roster_urls": ["https://example.com/member/"]})
    assert res["records"] == []
    assert any("取得失敗" in w for w in res["warnings"])
    assert any("抽出0件" in w for w in res["warnings"])


def test_collect_school_discovers_rcms_pagination(monkeypatch):
    page1 = """<html><body>
    <a href="?pageID=2">2</a>
    <p>イシイ ダイキ</p><p>石井 太基</p><p>4年生</p>
    <p>アンドウ ヒョウガ</p><p>安東 彪冴</p><p>6年生</p>
    <p>スズキ セイタ</p><p>鈴木 晴太</p><p>6年生</p>
    <p>タナカ ソウジロウ</p><p>田中 颯次郎</p><p>6年生</p>
    </body></html>"""
    page2 = """<html><body>
    <p>トミヅカ コウタ</p><p>富塚 耕太</p><p>5年生</p>
    </body></html>"""
    calls = []

    def fake_get(url):
        calls.append(url)
        return page2 if "pageID=2" in url else page1

    monkeypatch.setattr(hs, "_get_html", fake_get)
    monkeypatch.setattr(hs.time, "sleep", lambda s: None)
    res = hs._collect_school({
        "name": "テスト高校", "grade_scheme": "unified6",
        "roster_urls": ["http://example.d2.r-cms.jp/member_list/"]})
    names = {r["kanji"] for r in res["records"]}
    assert "富塚 耕太" in names  # 2ページ目も取得
    assert len(calls) == 2
