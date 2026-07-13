#!/bin/bash
# Antigravity をデバッグモード（ポート 9222）で起動するための補助スクリプト

echo "Antigravity をデバッグモードで起動します..."
echo "接続ポート: 9222"

# 既に起動している Antigravity を停止する必要がある場合は、手動で終了してください。
# 以下のパスは標準的なインストールパスを想定しています。

"/Applications/Antigravity.app/Contents/MacOS/Antigravity" --remote-debugging-port=9222 &

echo "コマンドを実行しました。バックグラウンドで起動を試みています。"
echo "起動後、Discord Bot が自動的に接続されます。"
