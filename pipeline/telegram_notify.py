"""Telegram 通知 & 承認モジュール（rugbypicks）。

x-trend-bot の `TELEGRAM_TOKEN` / `CHAT_ID` を流用する。値は環境変数を優先し、
無ければ `~/x-trend-bot/.env` から読む（トークンはコード・リポジトリに書かない）。

用途:
  send    : 任意メッセージ送信（HTML、URL添付可）。公開完了・予定・エラー報告に使う。
  approve : 承認/却下ボタン付きメッセージを送り、Telegram 上の回答を待って結果を返す。
            Claude が判断を仰ぐケースを Telegram だけで完結させる。

CLI:
  python3 -m pipeline.telegram_notify send --text "..."
  python3 -m pipeline.telegram_notify approve --text "この記事を公開して良い？" --timeout 300
    → 承認: exit 0 / 却下: exit 10 / タイムアウト: exit 20 / 設定なし: exit 30

送信失敗・未設定でもパイプラインを落とさないよう、send は例外を握って False を返す。
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Optional

import requests

API = "https://api.telegram.org/bot{token}/{method}"
XBOT_ENV = Path.home() / "x-trend-bot" / ".env"
PREFIX = "[rugbypicks] "


def _parse_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def load_credentials() -> tuple[Optional[str], Optional[str]]:
    """(token, chat_id) を返す。環境変数優先、無ければ x-trend-bot/.env。"""
    token = os.getenv("TELEGRAM_TOKEN")
    chat = os.getenv("CHAT_ID")
    if token and chat:
        return token, chat
    env = _parse_env_file(XBOT_ENV)
    return token or env.get("TELEGRAM_TOKEN"), chat or env.get("CHAT_ID")


def _call(token: str, method: str, *, timeout: int = 15, **params) -> Optional[dict]:
    try:
        resp = requests.post(API.format(token=token, method=method), data=params, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:  # noqa: BLE001 - 通知失敗はジョブを落とさない
        print(f"[telegram] {method} 失敗: {e}", file=sys.stderr)
        return None


def send(text: str, *, buttons: Optional[list] = None, prefix: bool = True,
         disable_preview: bool = False) -> Optional[dict]:
    """メッセージを送信。成功時は Telegram の message オブジェクトを返す。"""
    token, chat = load_credentials()
    if not token or not chat:
        print("[telegram] TELEGRAM_TOKEN / CHAT_ID 未設定のため送信スキップ", file=sys.stderr)
        return None
    body = (PREFIX + text) if prefix else text
    params: dict = {
        "chat_id": chat,
        "text": body[:4000],
        "parse_mode": "HTML",
        "disable_web_page_preview": "true" if disable_preview else "false",
    }
    if buttons:
        import json as _json
        params["reply_markup"] = _json.dumps({"inline_keyboard": buttons})
    res = _call(token, "sendMessage", **params)
    return res.get("result") if res and res.get("ok") else None


def _latest_update_id(token: str) -> int:
    res = _call(token, "getUpdates", timeout=10, offset=-1)
    if res and res.get("ok") and res["result"]:
        return res["result"][-1]["update_id"]
    return 0


def request_approval(text: str, *, timeout: int = 300, poll: int = 3) -> Optional[bool]:
    """承認/却下ボタン付きで送信し、Telegram 上の回答を待つ。

    戻り値: True=承認 / False=却下 / None=タイムアウト・未設定。
    ボタンのほか、返信テキスト（承認/ok/yes、却下/ng/no）も受け付ける。
    """
    token, chat = load_credentials()
    if not token or not chat:
        print("[telegram] 未設定のため承認要求スキップ", file=sys.stderr)
        return None

    offset = _latest_update_id(token) + 1  # 送信前までの古い更新を無視
    buttons = [[
        {"text": "✅ 承認", "callback_data": "approve"},
        {"text": "🚫 却下", "callback_data": "reject"},
    ]]
    msg = send(text + "\n\n👇 Telegram で承認/却下を押してください。", buttons=buttons)
    msg_id = msg.get("message_id") if msg else None

    deadline = time.time() + timeout
    decision: Optional[bool] = None
    while time.time() < deadline and decision is None:
        res = _call_long(token, offset, poll)
        if not res or not res.get("ok"):
            time.sleep(poll)
            continue
        for upd in res["result"]:
            offset = upd["update_id"] + 1
            cq = upd.get("callback_query")
            if cq and str(cq.get("message", {}).get("message_id")) == str(msg_id):
                data = cq.get("data")
                decision = data == "approve"
                _call(token, "answerCallbackQuery", callback_query_id=cq["id"],
                      text="承認しました" if decision else "却下しました")
                break
            m = upd.get("message")
            if m and str(m.get("chat", {}).get("id")) == str(chat):
                t = (m.get("text") or "").strip().lower()
                if t in ("承認", "ok", "yes", "y", "はい"):
                    decision = True
                    break
                if t in ("却下", "ng", "no", "n", "いいえ"):
                    decision = False
                    break
    if msg_id and decision is not None:
        mark = "✅ 承認済み" if decision else "🚫 却下"
        _call(token, "editMessageText", chat_id=chat, message_id=msg_id,
              text=PREFIX + text + f"\n\n<b>{mark}</b>", parse_mode="HTML")
    elif msg_id:
        _call(token, "editMessageText", chat_id=chat, message_id=msg_id,
              text=PREFIX + text + "\n\n<b>⌛ タイムアウト（未回答）</b>", parse_mode="HTML")
    return decision


def _call_long(token: str, offset: int, poll: int) -> Optional[dict]:
    # getUpdates の long-poll。requests 側は poll+余裕でタイムアウト。
    try:
        resp = requests.post(
            API.format(token=token, method="getUpdates"),
            data={"offset": offset, "timeout": poll},
            timeout=poll + 20,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:  # noqa: BLE001
        print(f"[telegram] getUpdates 失敗: {e}", file=sys.stderr)
        return None


def ask(question: str, options: list[str], *, timeout: int = 600, poll: int = 3) -> Optional[str]:
    """複数選択肢ボタンを送り、Telegram 上で選ばれた選択肢ラベルを返す。

    Claude が判断を仰ぐ質問（2択に限らない）を Telegram で完結させるための入口。
    戻り値: 選ばれたラベル / None（タイムアウト・未設定）。
    番号返信（"1"〜）でも回答可。
    """
    token, chat = load_credentials()
    if not token or not chat:
        print("[telegram] 未設定のため質問スキップ", file=sys.stderr)
        return None

    offset = _latest_update_id(token) + 1
    # 1行1ボタン（ラベルが長い日本語向け）。callback_data はインデックス。
    buttons = [[{"text": f"{i + 1}. {opt}", "callback_data": str(i)}] for i, opt in enumerate(options)]
    body = question + "\n\n👇 Telegram で選んでください（番号返信も可）。"
    msg = send(body, buttons=buttons)
    msg_id = msg.get("message_id") if msg else None

    deadline = time.time() + timeout
    chosen: Optional[int] = None
    while time.time() < deadline and chosen is None:
        res = _call_long(token, offset, poll)
        if not res or not res.get("ok"):
            time.sleep(poll)
            continue
        for upd in res["result"]:
            offset = upd["update_id"] + 1
            cq = upd.get("callback_query")
            if cq and str(cq.get("message", {}).get("message_id")) == str(msg_id):
                try:
                    idx = int(cq.get("data"))
                except (TypeError, ValueError):
                    idx = None
                if idx is not None and 0 <= idx < len(options):
                    chosen = idx
                    _call(token, "answerCallbackQuery", callback_query_id=cq["id"],
                          text=f"選択: {options[idx]}")
                    break
            m = upd.get("message")
            if m and str(m.get("chat", {}).get("id")) == str(chat):
                t = (m.get("text") or "").strip()
                if t.isdigit() and 1 <= int(t) <= len(options):
                    chosen = int(t) - 1
                    break
    if msg_id and chosen is not None:
        _call(token, "editMessageText", chat_id=chat, message_id=msg_id,
              text=PREFIX + question + f"\n\n<b>✅ {options[chosen]}</b>", parse_mode="HTML")
    elif msg_id:
        _call(token, "editMessageText", chat_id=chat, message_id=msg_id,
              text=PREFIX + question + "\n\n<b>⌛ タイムアウト（未回答）</b>", parse_mode="HTML")
    return options[chosen] if chosen is not None else None


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="pipeline.telegram_notify")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("send", help="メッセージ送信")
    s.add_argument("--text", required=True)
    s.add_argument("--no-prefix", action="store_true")

    a = sub.add_parser("approve", help="承認/却下を Telegram で仰ぐ")
    a.add_argument("--text", required=True)
    a.add_argument("--timeout", type=int, default=300)

    q = sub.add_parser("ask", help="複数選択肢を Telegram ボタンで仰ぐ")
    q.add_argument("--text", required=True)
    q.add_argument("--option", action="append", default=[], required=True,
                   help="選択肢（複数指定）")
    q.add_argument("--timeout", type=int, default=600)

    args = ap.parse_args(argv)

    if args.cmd == "send":
        ok = send(args.text, prefix=not args.no_prefix)
        return 0 if ok else 0  # 送信失敗でも 0（ジョブを落とさない）
    if args.cmd == "approve":
        d = request_approval(args.text, timeout=args.timeout)
        if d is True:
            print("approved")
            return 0
        if d is False:
            print("rejected")
            return 10
        return 20 if load_credentials()[0] else 30
    if args.cmd == "ask":
        choice = ask(args.text, args.option, timeout=args.timeout)
        if choice is not None:
            print(choice)
            return 0
        return 20 if load_credentials()[0] else 30
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
