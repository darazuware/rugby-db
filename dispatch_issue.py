#!/usr/bin/env python3
"""
rugby-db GitHub Issue Dispatcher
Dispatchコマンドで携帯からIssueを作成
"""
import sys
import os
from github import Github

# GitHub認証（環境変数 GITHUB_TOKEN から読む。直書き禁止）
TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO_NAME = "darazuware/rugby-db"

def create_issue(title, body="", issue_type="task"):
    """GitHub Issueを作成"""
    try:
        g = Github(TOKEN)
        repo = g.get_repo(REPO_NAME)

        # タイプに応じたラベル
        labels = ["enhancement"] if issue_type == "feature" else ["bug"]

        # Issueを作成
        issue = repo.create_issue(
            title=title,
            body=body,
            labels=labels
        )

        print(f"✅ Issue作成完了: #{issue.number}")
        print(f"📍 {issue.html_url}")
        return True

    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python dispatch_issue.py '修正: バグの説明' [feature|bug]")
        sys.exit(1)

    title = sys.argv[1]
    issue_type = sys.argv[2] if len(sys.argv) > 2 else "task"

    create_issue(title, issue_type=issue_type)
