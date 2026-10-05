import { defineConfig } from "vitest/config";

// 主要画面の E2E スモーク（ビルド成果物 .vercel/output を配信して検証）。
// 実行: npm run build && npm run test:e2e
export default defineConfig({
  test: {
    include: ["tests/e2e/**/*.test.ts"],
    exclude: ["**/node_modules/**", "**/dist/**"],
    testTimeout: 60_000,
    hookTimeout: 60_000,
    fileParallelism: false,
  },
});
