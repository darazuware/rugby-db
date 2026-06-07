#!/bin/bash

# rugby-db GitHub Issue Dispatcher
# 使用方法: ./dispatch-issue.sh "修正: バグの説明"

TOKEN="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"
REPO="darazuware/rugby-db"
API_URL="https://api.github.com/repos/$REPO/issues"

TITLE="$1"

if [ -z "$TITLE" ]; then
    echo "使用方法: ./dispatch-issue.sh '修正: バグの説明'"
    exit 1
fi

# GitHub APIでIssue作成
RESPONSE=$(curl -s -X POST "$API_URL" \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"$TITLE\"}")

# レスポンス確認
if echo "$RESPONSE" | grep -q '"number"'; then
    ISSUE_NUM=$(echo "$RESPONSE" | grep -o '"number": [0-9]*' | head -1 | cut -d' ' -f2)
    echo "✅ Issue作成完了: #$ISSUE_NUM"
    echo "📍 https://github.com/$REPO/issues/$ISSUE_NUM"
else
    echo "❌ エラー: $RESPONSE"
    exit 1
fi
