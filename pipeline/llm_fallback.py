"""P5-3: JRFU セブンズ/U代表スクレイパー用の Sonnet フォールバック（10_YOUTH_AGEGRADE.md）。

正規表現での学校名分類（scrape/jrfu.py の高校/大学サフィックス判定）が失敗した項目
だけを、学校名の文字列のみでSonnetに渡してtype判定させる。氏名・生年月日等の
個人情報は一切渡さない（渡すのは学校名候補の配列のみ）。

ANTHROPIC_API_KEY 未設定、anthropic 未インストール、API呼び出し失敗、レスポンスが
JSON配列として解釈できない場合は静かに空dictを返す。呼び出し側（scrape/jrfu.py）は
分類できなかった項目を無理に埋めず、education/career から落として warning を積む
（00原則3: 不明はnull。原則5: 判断に迷ったら保守的に）。

選手の事実（氏名・所属等）はスクレイプ結果のみを使う（03_VALIDATION.md）。ここで
Sonnetに判定させるのは「この学校名文字列は高校相当か大学相当か」という表記分類のみで、
学校名そのものを補完・創作することはない。
"""
from __future__ import annotations

import json
import os
import re

_MODEL = "claude-sonnet-5"
_SYSTEM = (
    "あなたは日本の学校名の表記を分類する分類器です。学校名の文字列だけを見て、"
    "高校相当(hs)か大学相当(univ)かを判定してください。判断できない場合は type を "
    "null にしてください。学校名以外の情報（個人情報）は一切含まれていません。"
)


def classify_school_names(names: list[str]) -> dict[str, str]:
    """学校名候補 -> "hs"|"univ" の判定結果を返す。判定不能/失敗時は該当キー無し。"""
    uniq = [n for n in dict.fromkeys(n.strip() for n in names) if n]
    if not uniq:
        return {}
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return {}
    try:
        import anthropic
    except ImportError:
        return {}

    prompt = (
        "次の学校名リストそれぞれについて type を判定し、JSON配列のみを出力してください。\n"
        'type は "hs"（高校・高等学校・高等科等）か "univ"（大学・大学校）のいずれか。'
        "判断できない場合は null。\n"
        '出力形式: [{"name": "...", "type": "hs"|"univ"|null}, ...]\n\n'
        "学校名リスト:\n" + "\n".join(f"- {n}" for n in uniq)
    )
    try:
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=_MODEL,
            max_tokens=1024,
            system=_SYSTEM,
            output_config={"effort": "low"},
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception:
        return {}
    if getattr(resp, "stop_reason", None) == "refusal":
        return {}

    text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
    m = re.search(r"\[.*\]", text, re.S)
    raw = m.group(0) if m else text
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, list):
        return {}

    result: dict[str, str] = {}
    for item in data:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        typ = item.get("type")
        if isinstance(name, str) and typ in ("hs", "univ"):
            result[name.strip()] = typ
    return result
