/**
 * `astro build` の Vercel 出力（.vercel/output）をローカルで配信するテスト用サーバ。
 * Vercel の挙動（filesystem 優先 → それ以外は _render 関数）を最小限で再現する。
 * 本番コードは変更しない。ビルド済みであることが前提（npm run build）。
 */
import { createServer, type Server } from "node:http";
import { existsSync, readFileSync, statSync } from "node:fs";
import { extname, join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

export const OUTPUT_DIR = resolve(__dirname, "../../.vercel/output");
export const STATIC_DIR = join(OUTPUT_DIR, "static");
const ENTRY = join(OUTPUT_DIR, "functions/_render.func/dist/server/entry.mjs");

const MIME: Record<string, string> = {
  ".html": "text/html; charset=utf-8",
  ".json": "application/json",
  ".xml": "application/xml",
  ".txt": "text/plain; charset=utf-8",
  ".css": "text/css",
  ".js": "text/javascript",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".png": "image/png",
  ".webp": "image/webp",
};

export function isBuilt(): boolean {
  return existsSync(ENTRY) && existsSync(join(STATIC_DIR, "index.html"));
}

/** URL パス → 配信する静的ファイル（無ければ null）。 */
export function staticFileFor(pathname: string): string | null {
  let p: string;
  try {
    p = decodeURIComponent(pathname);
  } catch {
    return null;
  }
  const base = join(STATIC_DIR, p);
  if (!base.startsWith(STATIC_DIR)) return null;
  for (const cand of [base, join(base, "index.html"), `${base}.html`]) {
    if (existsSync(cand) && statSync(cand).isFile()) return cand;
  }
  return null;
}

export async function startServer(): Promise<{ server: Server; baseUrl: string }> {
  const mod = await import(pathToFileURL(ENTRY).href);
  const handler = mod.default as (req: unknown, res: unknown) => Promise<void>;
  const server = createServer((req, res) => {
    const url = new URL(req.url ?? "/", "http://localhost");
    const file = staticFileFor(url.pathname);
    if (file) {
      res.statusCode = 200;
      res.setHeader("content-type", MIME[extname(file)] ?? "application/octet-stream");
      res.end(readFileSync(file));
      return;
    }
    handler(req, res).catch((err) => {
      res.statusCode = 500;
      res.end(String(err?.stack ?? err));
    });
  });
  await new Promise<void>((r) => server.listen(0, "127.0.0.1", r));
  const addr = server.address();
  const port = typeof addr === "object" && addr ? addr.port : 0;
  return { server, baseUrl: `http://127.0.0.1:${port}` };
}
