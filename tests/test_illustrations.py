"""P4-4: pipeline.illustrations のテスト（fixtureのみ、data/master・public は使わない）。

完了条件（06 / 09_TASKS.md P4-4）:
  - is_featured かつ Instagram未登録かつイラスト未配置の選手のみ todo に載る
  - is_featured=false は対象外
  - Instagram登録済み（data/manual/instagram_accounts.json にid有り）は対象外
  - イラスト配置済み（public/illustrations/{id}.webp 存在）は対象外
  - プロンプトはポジション・チームカラーを穴埋めするのみで、実在選手の顔に似せる指定を含まない
  - team_color / position 不明時も null を捏造せず、プロンプト文言のみフォールバック表記にする
"""
from pipeline import illustrations as ill


def _player(**overrides):
    base = {
        "id": "lo_1",
        "name_ja": "山田太郎",
        "name_en": "Taro Yamada",
        "position": "PR",
        "team_id": "team_a",
        "league": "league-one-d1",
        "is_featured": True,
    }
    base.update(overrides)
    return base


TEAMS = {
    "team_a": {"id": "team_a", "colors": {"primary": "#123456"}},
    "team_b": {"id": "team_b", "colors": {}},
}


def test_featured_no_instagram_no_illustration_is_included():
    players = [_player()]
    items = ill.build_todo_items(
        players, instagram_accounts={}, teams_by_id=TEAMS, illustration_check=lambda pid: False
    )
    assert len(items) == 1
    item = items[0]
    assert item["player_id"] == "lo_1"
    assert item["name"] == "山田太郎"
    assert item["position_ja"] == "プロップ"
    assert item["team_color"] == "#123456"
    assert "プロップ" in item["prompt"]
    assert "#123456" in item["prompt"]
    assert "顔は特定人物に似せない" in item["prompt"]


def test_non_featured_is_excluded():
    players = [_player(is_featured=False)]
    items = ill.build_todo_items(
        players, instagram_accounts={}, teams_by_id=TEAMS, illustration_check=lambda pid: False
    )
    assert items == []


def test_instagram_registered_is_excluded():
    players = [_player(id="lo_2")]
    items = ill.build_todo_items(
        players,
        instagram_accounts={"lo_2": {"username": "x", "post_url": "https://instagram.com/p/x/"}},
        teams_by_id=TEAMS,
        illustration_check=lambda pid: False,
    )
    assert items == []


def test_illustration_already_placed_is_excluded():
    players = [_player(id="lo_3")]
    items = ill.build_todo_items(
        players, instagram_accounts={}, teams_by_id=TEAMS, illustration_check=lambda pid: True
    )
    assert items == []


def test_unknown_position_and_team_color_use_fallback_text_not_fabricated_values():
    players = [_player(id="lo_4", position=None, team_id="team_b")]
    items = ill.build_todo_items(
        players, instagram_accounts={}, teams_by_id=TEAMS, illustration_check=lambda pid: False
    )
    item = items[0]
    assert item["position"] is None
    assert item["position_ja"] is None
    assert item["team_color"] is None
    assert "ポジション不明" in item["prompt"]
    assert "チームカラー不明" in item["prompt"]


def test_sorted_by_player_id():
    players = [_player(id="lo_9"), _player(id="lo_2"), _player(id="lo_5")]
    items = ill.build_todo_items(
        players, instagram_accounts={}, teams_by_id=TEAMS, illustration_check=lambda pid: False
    )
    assert [it["player_id"] for it in items] == ["lo_2", "lo_5", "lo_9"]


def test_position_label_passthrough_for_unknown_code():
    # 対訳表に無いコードはそのまま使う（事実の書き換え禁止、04と同じ規則）
    assert ill.position_label("FOO") == "FOO"
    assert ill.position_label(None) is None
    assert ill.position_label("") is None


def test_team_color_hex_prefers_primary_then_main_then_first_value():
    assert ill.team_color_hex({"colors": {"primary": "#111111", "away": "#222222"}}) == "#111111"
    assert ill.team_color_hex({"colors": {"main": "#333333"}}) == "#333333"
    assert ill.team_color_hex({"colors": {"away": "#444444"}}) == "#444444"
    assert ill.team_color_hex({"colors": {}}) is None
    assert ill.team_color_hex(None) is None
