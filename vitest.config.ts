import { defineConfig } from "vitest/config";

// .claude/worktrees/ 配下のワークツリー複製はテスト対象外
// （同名テストが多重実行され、古いコードで fail するため）
export default defineConfig({
  test: {
    exclude: ["**/node_modules/**", "**/dist/**", "**/.claude/**"],
  },
});
