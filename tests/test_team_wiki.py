"""team_wiki（Wikipedia 抽出）と team_facts（master 適用）のテスト。値はダミー。"""
import pytest
from pydantic import ValidationError

from pipeline import team_facts
from pipeline.schemas import Team
from pipeline.scrape import team_wiki as tw

EN = """{{Infobox rugby team
| founded = {{Start date and age|df=yes|1900}}
| ground = [[Test Park|Test Arena]] (Capacity: 10,000)<br>[[Second Ground]]
| location = [[Testville]], [[Testland]]
}}
==Honours==
===First XV===
*[[Test League]]
**Champions: (2) [[2001–02 Test League|2001–02]], [[2010–11 Test League|2010–11]]
**Runners-up: (1) 2003–04
* '''[[Test Cup]]'''
** '''Champions (1):''' [[2005 Test Cup|2005]]
===Sevens===
*[[Test Sevens]]
**Champions: (3) 2001, 2002, 2003
==Players==
"""

JA = """{{ラグビーチーム
|創設=1950
| ground = [[テスト競技場]]
}}
== タイトル ==
'''全国大会'''
*[[テスト選手権]]　優勝：2回（[[第1回|1960]], 1961<ref>注</ref>）
** 準優勝：1回（1962）
'''7人制大会'''
*[[テストセブンズ]]　優勝：1回（1970）
== 成績 ==
"""


def test_infobox_fields():
    ib = tw.infobox(EN)
    assert tw.parse_founded(ib) == 1900
    assert tw.parse_stadiums(ib) == ["Test Arena", "Second Ground"]
    assert tw.parse_location(ib) == "Testville, Testland"


def test_founded_ambiguous_is_none():
    assert tw.parse_founded({"founded": "1883 (A)<br>1995 (B)"}) is None


def test_stadium_with_period_is_skipped():
    assert tw.parse_stadiums({"ground": "[[A]] (2025-2026)<br>[[B]] (2026–)"}) == []


def test_titles_en_excludes_runners_up_and_sevens():
    titles = tw.parse_titles(EN, "en")
    assert titles == [
        {"competition": "Test League", "count": 2, "seasons": ["2001–02", "2010–11"]},
        {"competition": "Test Cup", "count": 1, "seasons": ["2005"]},
    ]


def test_titles_ja():
    assert tw.parse_titles(JA, "ja") == [
        {"competition": "テスト選手権", "count": 2, "seasons": ["1960", "1961"]},
    ]


def test_count_mismatch_dropped():
    assert tw._make("X", 3, "2001, 2002") is None


def test_apply_fills_only_nulls():
    url = "https://en.wikipedia.org/w/index.php?title=T&oldid=1"
    facts = {"t1": {
        "founded": {"value": 1900, "source_url": url},
        "home_area": {"value": "Testville", "source_url": url},
        "home_stadiums": [{"name": "Test Arena", "source_url": url}],
        "titles": [{"competition": "Test League", "count": 1, "seasons": ["2001"], "source_url": url}],
    }}
    team = {"id": "t1", "league": "top14", "name_en": "t1", "source_url": "https://all.rugby/club/t1/squad",
            "scraped_at": "2026-01-01T00:00:00+09:00", "home_area": "既存", "founded": None}
    teams = [team]
    assert team_facts.apply_all(teams, facts) == []
    t = teams[0]
    assert t["founded"] == 1900 and t["home_area"] == "既存"
    assert t["home_stadiums"][0]["name"] == "Test Arena"
    assert t["field_sources"] == {"founded": url, "titles": url}


def test_fact_url_domain_restricted():
    with pytest.raises(ValidationError):
        Team.model_validate({"id": "x", "league": "top14", "name_en": "x",
                             "source_url": "https://all.rugby/club/x/squad", "scraped_at": "t",
                             "field_sources": {"founded": "https://example.com/x"}})
