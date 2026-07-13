import time
import subprocess
import os
import sys

def run_sync():
    script_path = os.path.join(os.path.dirname(__file__), "discord_sync.py")
    try:
        # discord_sync.pyを実行
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"Loop error: {e}")

def main():
    print("Discord 1分間隔巡回を開始しました。中止するには Ctrl+C を押してください。")
    # 初回実行
    run_sync()
    
    while True:
        time.sleep(60)
        print(f"--- 巡回実行 ({time.strftime('%H:%M:%S')}) ---")
        run_sync()

if __name__ == "__main__":
    main()
