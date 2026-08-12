"""ソース生 dict → 01 スキーマ dict への変換（transform 層）。

各関数は (schema_dict | None, warnings) を返す。検証を通らないレコードは None を返し
warning を積む（02: 例外で全体を止めない）。返す dict は master にそのまま書ける形。
"""
from __future__ import annotations

import re
from datetime import datetime, timezone, timedelta
from typing import Optional

from pydantic import ValidationError

from pipeline.schemas import Match, Player, Team, Standing

JST = timezone(timedelta(hours=9))


def _now() -> str:
    return datetime.now(JST).isoformat(timespec="seconds")


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s


def _slugify_ja(text: str) -> str:
    """日本語を含む文字列のkebab化（_slugifyはASCII専用でkanji/kanaを全て捨てるため別関数）。

    pipeline.migrate_schools.slugify_school と同じ方針（ローマ字化しない。
    01/10: 日本語名をAIが翻訳・補完しない）。id生成専用でschools.jsonには書かない。
    """
    s = re.sub(r"\s+", "", text or "")
    s = re.sub(r"[^\w]+", "-", s, flags=re.UNICODE).strip("-")
    return s or "x"


def player(raw: dict, *, league: str, team_id: Optional[str]) -> tuple[Optional[dict], list[str]]:
    """league-one.jp の生選手 dict → Player dict。"""
    warnings: list[str] = []
    pid = raw.get("player_id")
    if not pid:
        return None, ["player: player_id 欠落のためスキップ"]

    name_en = raw.get("name_en")
    name_ja = raw.get("name_ja")
    if name_en:
        slug = f"{_slugify(name_en)}-{pid}"
    elif name_ja:
        slug = f"lo-{pid}"
    else:
        return None, [f"lo_{pid}: name_en/name_ja が両方欠落のためスキップ"]

    data = {
        "id": f"lo_{pid}",
        "source": "league-one.jp",
        "source_url": f"https://league-one.jp/player/{pid}",
        "scraped_at": _now(),
        "name_en": name_en,
        "name_ja": name_ja,
        "slug": slug,
        "position": raw.get("position"),
        "team_id": team_id,
        "league": league,
        "height_cm": raw.get("height_cm"),
        "weight_kg": raw.get("weight_kg"),
        "birthdate": raw.get("birthdate"),
        "league_caps": raw.get("league_caps"),
        "image_url": raw.get("image_url"),
        "education": raw.get("_education") or [],
    }
    try:
        model, w = Player.parse(data)
    except ValidationError as exc:
        return None, [f"lo_{pid}: Player 検証失敗 {exc.error_count()} 件のためスキップ"]
    warnings.extend(w)
    return model.model_dump(by_alias=True), warnings


def team(raw: dict, *, league: str) -> tuple[Optional[dict], list[str]]:
    tid = raw.get("team_id")
    if not tid:
        return None, ["team: team_id 欠落のためスキップ"]
    data = {
        "id": f"lo_team_{tid}",
        "league": league,
        "name_ja": raw.get("name_ja"),
        "source_url": f"https://league-one.jp/team/{tid}",
        "scraped_at": _now(),
        "roster_mode": "full",
        "roster_ids": raw.get("roster_ids", []),
    }
    try:
        model = Team.model_validate(data)
    except ValidationError as exc:
        return None, [f"lo_team_{tid}: Team 検証失敗 {exc.error_count()} 件のためスキップ"]
    return model.model_dump(by_alias=True), []


def _height_cm(raw: Optional[str]) -> Optional[str]:
    """all.rugby の '1.82 m' → '182'（cm 文字列）。'-'/欠落は None。"""
    if not raw:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)\s*m", raw)
    if not m:
        return None
    return str(round(float(m.group(1)) * 100))


def _weight_kg(raw: Optional[str]) -> Optional[str]:
    """all.rugby の '122 kg' → '122'。'-'/欠落は None。"""
    if not raw:
        return None
    m = re.search(r"(\d+)\s*kg", raw)
    return m.group(1) if m else None


def player_allrugby(raw: dict, *, league: str, team_id: str) -> tuple[Optional[dict], list[str]]:
    """all.rugby の squad 行（＋任意で個別ページ enrich）→ Player dict。"""
    slug = raw.get("slug")
    if not slug:
        return None, ["all.rugby player: slug 欠落のためスキップ"]
    name_en = raw.get("name_en")
    if not name_en:
        return None, [f"ar_{slug}: name_en 欠落のためスキップ"]

    career = [
        {"team": c["team"], "from": c.get("from"), "to": c.get("to")}
        for c in raw.get("career", []) if c.get("team")
    ]
    data = {
        "id": f"ar_{slug}",
        "source": "all.rugby",
        "source_url": f"https://all.rugby/player/{slug}",
        "scraped_at": _now(),
        "name_en": name_en,
        "slug": slug,
        "position": raw.get("position") or None,
        "team_id": team_id,
        "league": league,
        "height_cm": _height_cm(raw.get("height_raw")),
        "weight_kg": _weight_kg(raw.get("weight_raw")),
        "birthdate": raw.get("birthdate"),
        "nationality": raw.get("nationality", []),
        "career": career,
        "caps": raw.get("caps"),
    }
    try:
        model, w = Player.parse(data)
    except ValidationError as exc:
        return None, [f"ar_{slug}: Player 検証失敗 {exc.error_count()} 件のためスキップ"]
    return model.model_dump(by_alias=True), w


def team_allrugby(raw: dict, *, league: str, roster_mode: str = "full") -> tuple[Optional[dict], list[str]]:
    """all.rugby のクラブ → Team dict。id はクラブ slug（migrate_legacy と一致）。

    roster_mode="partial"（P4-6: urc/premiership等、日本人・スター選手のみ収集するリーグ）
    を渡すと 03 の roster_sym 検証が免除される（01 L108 準拠）。
    """
    slug = raw.get("slug")
    if not slug:
        return None, ["all.rugby team: slug 欠落のためスキップ"]
    data = {
        "id": slug,
        "league": league,
        "name_ja": raw.get("name_ja"),
        "name_en": raw.get("name_en") or (None if raw.get("name_ja") else slug),
        "source_url": f"https://all.rugby/club/{slug}/squad",
        "scraped_at": _now(),
        "roster_mode": roster_mode,
        "roster_ids": raw.get("roster_ids", []),
    }
    try:
        model = Team.model_validate(data)
    except ValidationError as exc:
        return None, [f"{slug}: Team 検証失敗 {exc.error_count()} 件のためスキップ"]
    return model.model_dump(by_alias=True), []


def standing_allrugby(rows_raw: list[dict], *, league: str, season: str,
                      source_url: str) -> tuple[Optional[dict], list[str]]:
    """all.rugby 順位表の行リスト → Standing dict。team_id はクラブ slug。

    列順（all.rugby）: PTS, PL, W, D, L。played≠W+D+L や数値欠落の行は落とす。

    引分0の空欄補正（P4-6, 2026-07-19 実ページ確認）: all.rugby は引分 0 を空欄で
    表示する（例: URC表 glasgow PL17 W12 D空欄 L5）。他の数値が揃っていて
    W+L=PL が成立する場合のみ機械的検証つきで drawn=0 とみなす（推測ではなく
    算術で確認できるケースに限定。それ以外の空欄は従来どおり行ごと除外）。
    """
    warnings: list[str] = []
    rows = []
    for r in rows_raw:
        tid = r.get("team_id")
        vals = {k: _to_int(r.get(k)) for k in ("rank", "played", "won", "drawn", "lost", "points")}
        if (vals["drawn"] is None and str(r.get("drawn") or "").strip() == ""
                and None not in (vals["played"], vals["won"], vals["lost"])
                and vals["played"] == vals["won"] + vals["lost"]):
            vals["drawn"] = 0
        if tid is None or any(vals[k] is None for k in ("rank", "played", "won", "drawn", "lost", "points")):
            warnings.append(f"{league} standings: team={tid} の数値欠落のため行を除外")
            continue
        if vals["played"] != vals["won"] + vals["drawn"] + vals["lost"]:
            warnings.append(f"{league} standings: team={tid} の played≠W+D+L のため行を除外")
            continue
        rows.append({
            "rank": vals["rank"], "team_id": tid, "played": vals["played"],
            "won": vals["won"], "drawn": vals["drawn"], "lost": vals["lost"],
            "points": vals["points"],
        })
    if not rows:
        return None, warnings
    data = {
        "league": league, "season": season or "unknown", "scraped_at": _now(),
        "source_url": source_url, "rows": rows,
    }
    try:
        model = Standing.model_validate(data)
    except ValidationError as exc:
        return None, warnings + [f"{league} standings: 検証失敗 {exc.error_count()} 件"]
    return model.model_dump(by_alias=True), warnings


def _to_int(v) -> Optional[int]:
    if v is None:
        return None
    s = str(v).strip()
    return int(s) if re.fullmatch(r"-?\d+", s) else None


def standing(rows_raw: list[dict], *, league: str, season: str) -> tuple[Optional[dict], list[str]]:
    """順位表の行リスト → Standing dict。played≠W+D+L の行は落として warning。"""
    warnings: list[str] = []
    rows = []
    for r in rows_raw:
        tid = r.get("team_id")
        vals = {k: _to_int(r.get(k)) for k in ("rank", "played", "won", "drawn", "lost", "points")}
        if tid is None or any(vals[k] is None for k in ("rank", "played", "won", "drawn", "lost", "points")):
            warnings.append(f"{league} standings: team={tid} の数値欠落のため行を除外")
            continue
        if vals["played"] != vals["won"] + vals["drawn"] + vals["lost"]:
            warnings.append(f"{league} standings: team={tid} の played≠W+D+L のため行を除外")
            continue
        rows.append({
            "rank": vals["rank"],
            "team_id": f"lo_team_{tid}",
            "played": vals["played"],
            "won": vals["won"],
            "drawn": vals["drawn"],
            "lost": vals["lost"],
            "points": vals["points"],
        })
    if not rows:
        return None, warnings
    data = {
        "league": league,
        "season": season or "unknown",
        "scraped_at": _now(),
        "source_url": "https://league-one.jp/standings/",
        "rows": rows,
    }
    try:
        model = Standing.model_validate(data)
    except ValidationError as exc:
        return None, warnings + [f"{league} standings: 検証失敗 {exc.error_count()} 件"]
    return model.model_dump(by_alias=True), warnings


def _jrfu_is_minor(birthdate_raw: Optional[str], league: str) -> bool:
    """生年月日から18歳未満(is_minor)を判定する（P5-3: 10のポリシー準拠）。

    生年月日が取得できたレコードは実年齢で判定する（squadラベル(u17等)は選考時点の
    区分に過ぎず、選手が既に成人している場合がある実データを確認済み。年齢で
    判定するのが事実に忠実）。生年月日が欠落している場合は、00原則5（判断に迷ったら
    保守的に）に従い league で仮判定する: age-grade（高校生年代を含みうる）は
    True、sevens-national（実質的に成人主体の代表チーム）は False とする。
    """
    if isinstance(birthdate_raw, str):
        m = re.fullmatch(r"(\d{4})/(\d{2})/(\d{2})", birthdate_raw.strip())
        if m:
            y, mo, d = (int(x) for x in m.groups())
            try:
                bd = datetime(y, mo, d)
            except ValueError:
                bd = None
            if bd is not None:
                now = datetime.now(JST).replace(tzinfo=None)
                age = now.year - bd.year - ((now.month, now.day) < (bd.month, bd.day))
                return age < 18
    return league == "age-grade"


def player_jrfu_squad(raw: dict, *, league: str) -> tuple[Optional[dict], list[str]]:
    """JRFU（rugby-japan.jp）セブンズ/U代表 選手詳細ページ raw dict → Player dict（P5-3）。

    raw は pipeline.scrape.jrfu._parse_detail() の出力に detail_id/squad/
    _education（学校名 name_raw+type 判定済みリスト）/_career（所属名リスト）を
    加えたもの。school_id は付与しない（P5-1同様、migrate_schools.py が別途解決）。
    """
    did = raw.get("detail_id")
    squad = raw.get("squad")
    if not did or not squad:
        return None, ["jrfu squad: detail_id/squad 欠落のためスキップ"]

    name_ja = raw.get("name_ja")
    name_en = raw.get("name_en")
    if not (name_en or name_ja):
        return None, [f"jrfu_{squad}_{did}: name_en/name_ja が両方欠落のためスキップ"]
    slug = f"{_slugify(name_en)}-{did}" if name_en else f"jrfu-{squad}-{did}"

    now = _now()
    education = [
        {"name_raw": e["name_raw"], "type": e["type"],
         "source_url": raw["detail_url"], "scraped_at": now}
        for e in raw.get("_education", []) if e.get("name_raw") and e.get("type")
    ]
    career = [
        {"team": c["team"], "source_url": raw["detail_url"]}
        for c in raw.get("_career", []) if c.get("team")
    ]

    data = {
        "id": f"jrfu_{squad}_{did}",
        "source": "rugby-japan.jp",
        "source_url": raw["detail_url"],
        "scraped_at": now,
        "name_en": name_en,
        "name_ja": name_ja,
        "slug": slug,
        "position": raw.get("position"),
        "team_id": None,
        "league": league,
        "height_cm": raw.get("height_cm"),
        "weight_kg": raw.get("weight_kg"),
        "birthdate": raw.get("birthdate"),
        "nationality": ["JP"],  # 02: 全て日本代表(男女セブンズ/U代表)スコッドのため
        "career": career,
        "education": education,
        "instagram": raw.get("instagram"),
        "squad": squad,
        "is_minor": _jrfu_is_minor(raw.get("birthdate"), league),
    }
    try:
        model, w = Player.parse(data)
    except ValidationError as exc:
        return None, [f"jrfu_{squad}_{did}: Player 検証失敗 {exc.error_count()} 件のためスキップ"]
    return model.model_dump(by_alias=True), w


def player_jrfu_callup(raw: dict, *, league: str, source_url: str) -> tuple[Optional[dict], list[str]]:
    """JRFU招集・合宿メンバー発表記事の1行（gap B）→ Player dict。

    raw は pipeline.scrape.jrfu.parse_call_up_article() のメンバー要素に、呼び出し側で
    分類済みの `_education`（[{name_raw,type}]）/`_career`（[{team}]）を加えたもの。
    /japan/member/ の詳細ページ（player_jrfu_squad）と違い detail_id が無いため
    id は氏名slug由来（`jrfu_callup_{slug}`）。記事表はキャップ数を含むため caps も持つ
    （squad版には無い）。当代表の正データ源は all.rugby のため、collect_national() 側で
    all.rugby由来の日本代表と氏名突合できた選手はこのレコードを採用せずskipする。
    """
    name_ja = raw.get("name_ja")
    name_en = raw.get("name_en")
    if not (name_en or name_ja):
        return None, ["jrfu callup: name_en/name_ja が両方欠落のためスキップ"]
    slug_base = _slugify(name_en) if name_en else _slugify_ja(name_ja)
    if not slug_base:
        return None, [f"jrfu callup {name_ja or name_en!r}: slug生成不能のためスキップ"]
    pid = f"jrfu_callup_{slug_base}"

    now = _now()
    education = [
        {"name_raw": e["name_raw"], "type": e["type"], "source_url": source_url, "scraped_at": now}
        for e in raw.get("_education", []) if e.get("name_raw") and e.get("type")
    ]
    career = [{"team": c["team"], "source_url": source_url} for c in raw.get("_career", []) if c.get("team")]

    caps = None
    caps_count = raw.get("caps")
    if isinstance(caps_count, int) and caps_count >= 0:
        caps = {"team": "Japan", "count": caps_count, "source_url": source_url}

    data = {
        "id": pid,
        "source": "rugby-japan.jp",
        "source_url": source_url,
        "scraped_at": now,
        "name_en": name_en,
        "name_ja": name_ja,
        "slug": pid,
        "position": raw.get("position_group"),
        "team_id": None,
        "league": league,
        "height_cm": raw.get("height_cm"),
        "weight_kg": raw.get("weight_kg"),
        "birthdate": raw.get("birthdate"),
        "nationality": ["JP"],
        "caps": caps,
        "career": career,
        "education": education,
        "squad": "national",
        "is_minor": _jrfu_is_minor(raw.get("birthdate"), league),
    }
    try:
        model, w = Player.parse(data)
    except ValidationError as exc:
        return None, [f"jrfu callup {pid}: Player 検証失敗 {exc.error_count()} 件のためスキップ"]
    return model.model_dump(by_alias=True), w


def _univ_grad_year(grade: Optional[int], scraped_at: str) -> Optional[int]:
    """現在の学年(grade, 1-4)から卒業年(西暦)を機械的に算出する（P5-5）。

    日本の4年制大学は4月入学・3月卒業なので、年度(4月始まり)を ay とすると
    grade=g の学生は ay年度にg回生 → 卒業年度末=ay + (5-g) 年の3月。
    ay は scraped_at の月が4月以降ならその年、1-3月なら前年。
    生年月日と違い「学年」自体がソース記載の事実であり、ここでの変換は
    その事実からの機械的な暦計算（_jrfu_is_minorの年齢計算と同種）であって
    AIによる補完ではない。
    """
    if grade is None:
        return None
    try:
        dt = datetime.fromisoformat(scraped_at)
    except ValueError:
        return None
    ay = dt.year if dt.month >= 4 else dt.year - 1
    return ay + 5 - grade


def _univ_hs_grad_year(grade: Optional[int], scraped_at: str) -> Optional[int]:
    """現在の大学の学年から、出身高校の卒業年(=大学入学年)を機械的に算出する。"""
    if grade is None:
        return None
    try:
        dt = datetime.fromisoformat(scraped_at)
    except ValueError:
        return None
    ay = dt.year if dt.month >= 4 else dt.year - 1
    return ay - grade + 1


def player_university(raw: dict, *, team_name: str, division: str,
                      source_url: str) -> tuple[Optional[dict], list[str]]:
    """大学ラグビー部公式サイトの部員名簿1件 raw dict -> Player dict（P5-5）。

    raw は pipeline.scrape.university._extract_records()（または LLM フォールバック）
    の1レコード: {kanji, kana, grade(1-4|None), position, school_raw, height_cm, weight_kg}。
    team_id は付与しない（university は NO_TEAM_LEAGUES。所属大学は education の
    type="univ" エントリで表現し、school_id は migrate_schools.py が別途解決する）。
    生年月日・SNS・写真は一切収集しない（10: 学生ポリシー）。身長体重は名簿ページに
    公式記載があった場合のみ、スキーマの妥当性範囲外なら通常通りnull化される。
    """
    kanji = raw.get("kanji")
    if not kanji:
        return None, ["university: 氏名(漢字)欠落のためスキップ"]
    kana = raw.get("kana") or ""
    team_slug = _slugify_ja(team_name)
    name_slug = _slugify_ja(kanji)
    pid = f"univ_{team_slug}__{name_slug}"
    slug = f"univ-{team_slug}-{name_slug}"

    now = _now()
    grade = raw.get("grade")
    education = [{
        "name_raw": team_name, "type": "univ",
        "grad_year": _univ_grad_year(grade, now),
        "source_url": source_url, "scraped_at": now,
    }]
    school_raw = raw.get("school_raw")
    if school_raw:
        education.append({
            "name_raw": school_raw, "type": "hs",
            "grad_year": _univ_hs_grad_year(grade, now),
            "source_url": source_url, "scraped_at": now,
        })

    data = {
        "id": pid,
        "source": "university-club-site",
        "source_url": source_url,
        "scraped_at": now,
        "name_ja": kanji,
        "name_kana": kana or None,
        "name_en": raw.get("name_en_raw"),
        "slug": slug,
        "position": raw.get("position"),
        "team_id": None,
        "league": "university",
        "height_cm": raw.get("height_cm"),
        "weight_kg": raw.get("weight_kg"),
        "nationality": [],
        "education": education,
        "squad": division,
        "is_minor": False,  # 大学生は成人（10）
    }
    try:
        model, w = Player.parse(data)
    except ValidationError as exc:
        return None, [f"{pid}: Player 検証失敗 {exc.error_count()} 件のためスキップ"]
    return model.model_dump(by_alias=True), w


def _hs_grad_year(grade: Optional[int], scraped_at: str) -> Optional[int]:
    """現在の高校の学年(grade, 1-3)から卒業年(西暦)を機械的に算出する（P5-6）。

    _univ_grad_year と同じ暦計算（高校は3年制: 卒業年 = 年度 + 4 - g）。
    「学年」自体がソース記載の事実であり、AIによる補完ではない。
    """
    if grade is None:
        return None
    try:
        dt = datetime.fromisoformat(scraped_at)
    except ValueError:
        return None
    ay = dt.year if dt.month >= 4 else dt.year - 1
    return ay + 4 - grade


def player_highschool(raw: dict, *, school_name: str,
                      source_url: str) -> tuple[Optional[dict], list[str]]:
    """高校ラグビー部公式サイトの部員名簿1件 raw dict -> Player dict（P5-6）。

    raw は pipeline.scrape.highschool._extract_records()（または LLM フォールバック）
    の1レコード: {kanji, kana, grade(1-3|None), position}。

    未成年ポリシー（10、絶対）: is_minor=True を必ず設定。収集・保持するのは
    氏名・かな・学年（education.grad_year に変換）・ポジションのみ。生年月日・
    身長体重・出身中学・SNS・写真はソースに記載があっても一切保持しない
    （P5-2 のサイト側強制に加え、収集段階でも最小化する）。
    team_id は付与しない（highschool は NO_TEAM_LEAGUES。所属校は education の
    type="hs" エントリで表現し、school_id は migrate_schools.py が別途解決する）。
    """
    kanji = raw.get("kanji")
    if not kanji:
        return None, ["highschool: 氏名(漢字)欠落のためスキップ"]
    school_slug = _slugify_ja(school_name)
    name_slug = _slugify_ja(kanji)
    pid = f"hs_{school_slug}__{name_slug}"
    slug = f"hs-{school_slug}-{name_slug}"

    now = _now()
    education = [{
        "name_raw": school_name, "type": "hs",
        "grad_year": _hs_grad_year(raw.get("grade"), now),
        "source_url": source_url, "scraped_at": now,
    }]
    data = {
        "id": pid,
        "source": "highschool-club-site",
        "source_url": source_url,
        "scraped_at": now,
        "name_ja": kanji,
        "name_kana": raw.get("kana") or None,
        "slug": slug,
        "position": raw.get("position"),
        "team_id": None,
        "league": "highschool",
        "nationality": [],
        "education": education,
        "is_minor": True,  # 高校生は原則全員未成年扱い（10）
    }
    try:
        model, w = Player.parse(data)
    except ValidationError as exc:
        return None, [f"{pid}: Player 検証失敗 {exc.error_count()} 件のためスキップ"]
    return model.model_dump(by_alias=True), w


def match_jrfu(g: dict, *, home_slug: str, away_slug: str, game_id) -> tuple[Optional[dict], list[str]]:
    """JRFU（rugby-japan.jp）game.php の1試合分 dict → Match dict（02: 日本代表日程）。

    g は https://www.rugby-japan.jp/v1.0/game.php?game_id={id} の game_list[0]。
    venue は正規化せず venue_raw のみに原文を保持する（02）。
    """
    warnings: list[str] = []
    start_epoch = g.get("start_time_plan") or g.get("start_time") or g.get("game_date")
    if not start_epoch:
        return None, [f"jrfu_{game_id}: 開催日時が取得できないためスキップ"]
    try:
        kickoff_dt = datetime.fromtimestamp(int(start_epoch), tz=timezone.utc)
    except (ValueError, OSError, TypeError):
        return None, [f"jrfu_{game_id}: 開催日時のパース失敗のためスキップ"]

    status_code = g.get("game_status")
    if status_code == 2:
        status = "finished"
        home_score = _to_int(g.get("home_team_points"))
        away_score = _to_int(g.get("away_team_points"))
    else:
        if status_code not in (0, 2):
            warnings.append(f"jrfu_{game_id}: 未知の game_status={status_code!r} のため scheduled 扱い")
        status = "scheduled"
        home_score = None
        away_score = None

    venue_raw = (g.get("stadium") or {}).get("name") or None

    data = {
        "id": f"jrfu_{game_id}",
        "league": "national",
        "season": str(kickoff_dt.year),
        "round": None,
        "kickoff_utc": kickoff_dt.isoformat(timespec="seconds"),
        "home_team_id": home_slug,
        "away_team_id": away_slug,
        "home_score": home_score,
        "away_score": away_score,
        "status": status,
        "venue": None,
        "venue_raw": venue_raw,
        "source_url": f"https://www.rugby-japan.jp/match/{game_id}",
        "scraped_at": _now(),
    }
    try:
        model = Match.model_validate(data)
    except ValidationError as exc:
        return None, warnings + [f"jrfu_{game_id}: Match 検証失敗 {exc.error_count()} 件のためスキップ"]
    return model.model_dump(by_alias=True), warnings
