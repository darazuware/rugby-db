import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_bot_status():
    token = os.getenv("DISCORD_BOT_TOKEN")
    headers = {"Authorization": f"Bot {token}"}
    
    # 1. ボット自身の情報を取得
    try:
        me = requests.get("https://discord.com/api/v10/users/@me", headers=headers).json()
        print(f"Bot Name: {me.get('username')}#{me.get('discriminator')}")
        print(f"Bot ID: {me.get('id')}")
    except Exception as e:
        print(f"自身情報の取得失敗: {e}")
        return

    # 2. 所属ギルド一覧を取得
    try:
        guilds = requests.get("https://discord.com/api/v10/users/@me/guilds", headers=headers).json()
        print(f"\n所属ギルド一覧 ({len(guilds)}件):")
        for g in guilds:
            print(f"- {g.get('name')} (ID: {g.get('id')})")
    except Exception as e:
        print(f"ギルド一覧の取得失敗: {e}")

if __name__ == "__main__":
    check_bot_status()
