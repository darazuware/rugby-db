#!/usr/bin/env python3
"""完成動画をTelegramに送る。使い方: python3 send_telegram.py <mp4> [キャプション]"""
import os, sys, subprocess

ENV = os.path.expanduser("~/x-trend-bot/.env")
cfg = {}
for line in open(ENV):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        cfg[k.strip()] = v.strip().strip('"').strip("'")
TOKEN, CHAT_ID = cfg["TELEGRAM_TOKEN"], cfg["CHAT_ID"]

def send_video(path, caption=""):
    r = subprocess.run([
        "curl", "-s", "-X", "POST",
        f"https://api.telegram.org/bot{TOKEN}/sendVideo",
        "-F", f"chat_id={CHAT_ID}",
        "-F", f"caption={caption}",
        "-F", "supports_streaming=true",
        "-F", f"video=@{path};type=video/mp4",
    ], capture_output=True, text=True, timeout=300)
    print("OK" if '"ok":true' in r.stdout else r.stdout or r.stderr)

if __name__ == "__main__":
    path = sys.argv[1]
    caption = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(path)
    send_video(path, caption)
