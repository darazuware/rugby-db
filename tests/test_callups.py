"""gap B: 招集・合宿メンバー発表（jrfu.parse_call_up_article + pipeline.callups +
news_gen.build_call_up_articles）をオフラインfixtureで検証（ネットワーク不使用）。"""
import pathlib

from pipeline import callups, news_gen
from pipeline.scrape import jrfu

FX = pathlib.Path(__file__).parent / "fixtures"


def _read(name):
    return (FX / name).read_text(encoding="utf-8")


def _event():
    return jrfu.parse_call_up_article(
        _read("jrfu_news_callup.html"), "https://www.rugby-japan.jp/news/54087")


# --- list / parse -----------------------------------------------------------

def test_list_national_callup_news_filters_to_roster_only():
    lst = jrfu.list_national_callup_news(_read("jrfu_news_category_national.html"))
    ids = {c["news_id"] for c in lst}
    # 男子15人制の「参加メンバー」記事のみ。女子/実施予告/レポート/セブンズ/U20は除外。
    assert ids == {"54087"}


def test_parse_call_up_article_extracts_34_members_and_meta():
    ev = _event()
    assert ev["news_id"] == "54087"
    assert ev["kind"] == "camp"
    assert ev["venue"] == "網走スポーツ・トレーニングフィールド"
    assert ev["start_date"] == "2026-07-25"
    assert len(ev["members"]) == 34
    groups = [m["position_group"] for m in ev["members"]]
    assert groups.count("FW") == 19 and groups.count("BK") == 15


def test_parse_handles_nfd_dakuten_and_caps():
    # JRFUニュースHTMLはNFD（濁点分解）配信。NFC正規化されないと氏名・所属が壊れる。
    ev = _event()
    yazaki = next(m for m in ev["members"] if (m["name_en"] or "").lower() == "yoshitaka yazaki")
    assert yazaki["name_ja"] == "矢崎 由高"
    assert yazaki["club_raw"] == "早稲田大学"
    assert yazaki["caps"] == 9
    dearns = next(m for m in ev["members"] if "dearns" in (m["name_en"] or "").lower())
    assert dearns["name_ja"] == "ワーナー・ディアンズ"  # バ=NFCで結合されている


def test_parse_returns_none_when_no_member_table():
    # メンバーテーブルの無い記事（実施予告等）はNoneでロースター扱いしない。
    html = "<html><head><title>男子日本代表 網走合宿実施のお知らせ｜JRFU</title></head><body><p>本文</p></body></html>"
    assert jrfu.parse_call_up_article(html, "https://www.rugby-japan.jp/news/54079") is None


# --- facts (Player レコード化) ---------------------------------------------

def test_callup_members_to_players_builds_records_with_caps_career_education():
    players, warnings = jrfu.callup_members_to_players(_event())
    assert len(players) == 34
    yaz = next(p for p in players if (p["name_en"] or "").lower() == "yoshitaka yazaki")
    assert yaz["id"] == "jrfu_callup_yoshitaka-yazaki"
    assert yaz["caps"] == {"team": "Japan", "count": 9,
                           "source_url": "https://www.rugby-japan.jp/news/54087"}
    assert yaz["career"][0]["team"] == "早稲田大学"
    assert yaz["education"][0]["name_raw"] == "桐蔭学園高校"
    assert yaz["education"][0]["type"] == "hs"
    assert yaz["birthdate"] == "2004-05-12"
    assert yaz["squad"] == "national"


# --- event / diff -----------------------------------------------------------

def test_assign_member_ids_prefers_master_player_id():
    ev = _event()
    national = [{"id": "ar_yoshitaka-yazaki", "name_en": "Yoshitaka Yazaki"}]
    evs = callups.assign_member_ids([ev], national)
    yaz = next(m for m in evs[0]["members"] if (m["name_en"] or "").lower() == "yoshitaka yazaki")
    assert yaz["player_id"] == "ar_yoshitaka-yazaki"  # all.rugby id に突合


def test_diff_new_events_first_event_has_no_new_members():
    ev = _event()
    evs = callups.assign_member_ids([ev], [])
    diff = callups.diff_new_events(evs, [], league="national")
    assert len(diff) == 1
    assert diff[0]["has_previous"] is False
    assert diff[0]["new_members"] == []  # 前回イベントが無ければ新規選出は計算しない
    assert diff[0]["member_count"] == 34


def test_diff_new_events_surfaces_players_absent_from_previous_camp():
    ev = _event()
    evs = callups.assign_member_ids([ev], [])
    # 前回招集（news_id 54000）から矢崎を外したロースターを用意。
    prev_members = [dict(m, player_id=None) for m in evs[0]["members"]
                    if (m["name_en"] or "").lower() != "yoshitaka yazaki"]
    prev = [{"id": "callup_national_54000", "news_id": "54000", "title": "前回合宿",
             "members": prev_members}]
    diff = callups.diff_new_events(evs, prev, league="national")
    assert diff[0]["has_previous"] is True
    new_names = {m["name_ja"] for m in diff[0]["new_members"]}
    assert "矢崎 由高" in new_names


def test_diff_new_events_is_idempotent_for_known_event():
    ev = _event()
    evs = callups.assign_member_ids([ev], [])
    recs = callups.build_event_records(evs, league="national", scraped_at="2026-07-23T00:00:00+09:00")
    # 既にmasterに存在するイベントは再度記事化しない。
    assert callups.diff_new_events(evs, recs, league="national") == []


# --- news 記事 --------------------------------------------------------------

def test_build_call_up_article_renders_roster_and_new_selection():
    ev = _event()
    players, _ = jrfu.callup_members_to_players(ev)
    evs = callups.assign_member_ids([ev], players)
    prev_members = [dict(m) for m in evs[0]["members"]
                    if (m["name_en"] or "").lower() != "yoshitaka yazaki"]
    prev = [{"id": "callup_national_54000", "news_id": "54000", "title": "前回合宿",
             "members": prev_members}]
    diff = callups.diff_new_events(evs, prev, league="national")
    pbi = {p["id"]: p for p in players}
    arts = news_gen.build_call_up_articles(
        {"league": "national", "call_ups": diff},
        players_by_id=pbi, pub_date="2026-07-23", source_diff="2026-07-23_national.json")
    assert len(arts) == 1
    md = arts[0].to_markdown()
    assert arts[0].slug == "national-callup-54087"
    assert "網走スポーツ・トレーニングフィールド" in md
    assert "FW（フォワード）" in md and "BK（バックス）" in md
    assert "前回招集から新たに選出" in md
    assert "矢崎 由高" in md
