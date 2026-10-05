import { defineConfig } from "vitest/config";

// .claude/worktrees/ 配下のワークツリー複製はテスト対象外
// （同名テストが多重実行され、古いコードで fail するため）
export default defineConfig({
  test: {
    // tests/e2e/ はビルド成果物が必要なため別設定（vitest.e2e.config.ts / npm run test:e2e）
    exclude: ["**/node_modules/**", "**/dist/**", "**/.claude/**", "tests/e2e/**"],
  },
});
