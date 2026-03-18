import os
import json
import requests
from dotenv import load_dotenv

# .envファイルを読み込む (スクリプトのあるディレクトリの親ディレクトリを探す)
script_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(script_dir, "..", ".env")
load_dotenv(dotenv_path=dotenv_path)

def send_discord_notification(title, message, color=0x3498db):
    """
    Discord Webhookに通知を送信する関数
    :param title: 通知のタイトル
    :param message: 通知の本文
    :param color: メッセージの横線の色 (16進数)
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("エラー: DISCORD_WEBHOOK_URL が設定されていません。")
        return False

    payload = {
        "embeds": [
            {
                "title": title,
                "description": message,
                "color": color,
                "footer": {
                    "text": "Antigravity Assistant Notification"
                }
            }
        ]
    }

    print(f"Discord Webhookに送信中: {title}...")
    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"レスポンスステータス: {response.status_code}")
        response.raise_for_status()
        print("Discord通知を送信しました。")
        return True
    except Exception as e:
        print(f"Discord通知の送信に失敗しました: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        title = sys.argv[1]
        msg = sys.argv[2]
        color_code = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x3498db
        send_discord_notification(title, msg, color_code)
    else:
        # デフォルトのテストメッセージ
        send_discord_notification("テスト通知", "Antigravityからのテストメッセージです。")
