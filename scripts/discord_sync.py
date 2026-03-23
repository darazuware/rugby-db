import os
import json
import requests
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

STATE_FILE = "/Users/ktamatzmoto/Desktop/rugbypicks/data/discord_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_processed_message_id": "0"}

def save_state(last_id):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_processed_message_id": last_id}, f, indent=4)

def get_latest_discord_messages(channel_id, limit=5):
    """
    指定したチャンネルの最新メッセージを取得する
    """
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("エラー: DISCORD_BOT_TOKEN が設定されていません。")
        return []

    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }
    
    # last_id 以降のメッセージを取得するために after パラメータを使用する
    state = load_state()
    after_id = state.get("last_processed_message_id", "0")
    
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit={limit}"
    if after_id != "0":
        url += f"&after={after_id}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"メッセージ取得失敗: {e}")
        return []

def notify_discord(title, description, color=0x3498db):
    """
    Webhookを使用してDiscordに通知を送る
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return

    payload = {
        "embeds": [
            {
                "title": title,
                "description": description,
                "color": color
            }
        ]
    }
    try:
        requests.post(webhook_url, json=payload, timeout=10)
    except Exception as e:
        print(f"通知失敗: {e}")

def sync_main():
    # 前回のWebhook検証で判明したチャンネルIDを使用
    CHANNEL_ID = "1483578689668251779"
    # 最新のメッセージを多めに取得
    messages = get_latest_discord_messages(CHANNEL_ID, limit=20)
    
    if not messages:
        print("新規メッセージはありません。")
        return

    # 重要：取得した全メッセージの中で最も新しいIDを即座に特定
    # メッセージは after パラメータ使用時、古い順（ID昇順）で返ってくる
    newest_id = messages[-1].get("id")
    
    # ボットやWebhook以外のメッセージのみを抽出
    user_messages = [
        m for m in messages 
        if not m.get("author", {}).get("bot", False) and not m.get("webhook_id")
    ]
    
    if not user_messages:
        print(f"新規のユーザーメッセージはありません（{len(messages)}件のボット通知等を既読化: {newest_id}）。")
        save_state(newest_id)
        return

    # ユーザーメッセージの中で最新の1件のみを対象とする
    msg = user_messages[-1]
    last_user_msg_id = msg.get("id")
    author = msg.get("author", {}).get("username", "不明")
    content = msg.get("content", "")
    
    print(f"--- 最新ユーザー指示の受信 (新規{len(user_messages)}件中1件) ---")
    print(f"ID: {last_user_msg_id} | Author: {author} | Content: {content}")
    
    if content:
        # 指示内容を引用して復唱（設定が有効な場合のみ）
        notify_echo = os.getenv("DISCORD_NOTIFY_ECHO", "false").lower() in ("true", "1", "on")
        if notify_echo:
            echo_message = f"以下の指示を正しく受信しました：\n\n>>> {content}\n\nこれより解析・実行を開始します。"
            notify_discord("指示内容の確認（復唱）", echo_message, 0x00ff00)
            print("Webhook通知（復唱）を送信しました。")
        else:
            print("指示受信（復唱通知は無効です）")
    
    # 状態ファイルは「呼び出した全メッセージの最後」に更新
    # これにより、この実行中に送られた自分のWebhook等も次回スキップされる
    save_state(newest_id)

if __name__ == "__main__":
    sync_main()
