"""pipeline/school_types.py（学校名のhs/univローカル分類）のテスト。"""
import pytest

from pipeline import school_types
from pipeline.scrape import league_one


@pytest.mark.parametrize("name", [
    "AucklandGrammar",
    "オークランドグラマースクール",
    "DeLaSalleCollege",
    "TongaCollege",
    "GreyCollege",
    "PaarlGymnasium",
    "HoerskoolNoordheuwel",
    "OtagoBoysH.S.",
    "LeleanMemorialSchool",
    "TheSouthportSchool（サウスポート高校）",
    "常翔学園",
    "石見智翠館",
    "日本航空高校石川",
    "関西学院高等部",
    "大阪朝鮮高級学校",
])
def test_hs(name):
    assert school_types.classify(name) == "hs"


@pytest.mark.parametrize("name", [
    "UniversityofSydney（シドニー大",
    "Universityofjohannesburg（ヨハ",
    "関東学院大",
    "早稲田大学",
])
def test_univ(name):
    assert school_types.classify(name) == "univ"


@pytest.mark.parametrize("name", [
    "",
    "WesternSydney",
    "プルーム・アカデミー",
    "クボタスピアーズ船橋・東京ベイ",
    "東芝ブレイブルーパス東京",
])
def test_unknown_stays_none(name):
    """判定できない表記・クラブ名は None のまま（00原則3: 不明はnull）。"""
    assert school_types.classify(name) is None


def test_league_one_regex_falls_back_to_dict():
    """scrape/league_one の判定がローカル辞書まで到達する。"""
    assert league_one._classify_school_regex("AucklandGrammar") == "hs"
    assert league_one._classify_school_regex("フゲノート高校") == "hs"
    assert league_one._classify_school_regex("東芝ブレイブルーパス東京") is None
