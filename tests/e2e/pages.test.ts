/**
 * 主要画面の自動テスト（ビルド成果物 .vercel/output を対象にした E2E スモーク）。
 * 実行: npm run build && npm run test:e2e
 *
 * - 表示内容は data/master（SSOT）の値と突合する。AI知識由来の期待値は書かない（03）。
 * - data/master は読み取りのみ。
 */
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { readFileSync, readdirSync } from "node:fs";
import { join, resolve } from "node:path";
import type { Server } from "node:http";
import { STATIC_DIR, isBuilt, startServer } from "./server";

const ROOT = resolve(__dirname, "../..");
const MASTER = join(ROOT, "data/master");
const readJson = (p: string) => JSON.parse(readFileSync(p, "utf-8"));

let server: Server;
let baseUrl = "";

beforeAll(async () => {
  if (!isBuilt()) {
    throw new Error(".vercel/output が無い。先に `npm run build` を実行すること");
  }
  ({ server, baseUrl } = await startServer());
});

afterAll(async () => {
  await new Promise<void>((r) => (server ? server.close(() => r()) : r()));
});

async function get(path: string, redirect: RequestRedirect = "manual") {
  return fetch(baseUrl + path, { redirect });
}

/** script/style を除いた可視テキスト。 */
function visibleText(html: string): string {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<!--[\s\S]*?-->/g, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/\s+/g, " ");
}

function unescapeHtml(s: string): string {
  return s
    .replace(/&amp;/g, "&")
    .replace(/&#39;|&#x27;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">");
}

/** HTMLページとして最低限壊れていないことの共通チェック。 */
async function expectHealthyPage(path: string): Promise<string> {
  const res = await get(path);
  expect(res.status, `${path} status`).toBe(200);
  expect(res.headers.get("content-type") ?? "", `${path} content-type`).toMatch(/text\/html/);
  const html = await res.text();
  expect(html, `${path} <title>`).toMatch(/<title>[^<]{2,}<\/title>/);
  expect(html, `${path} <h1>`).toMatch(/<h1[\s>]/);
  const text = visibleText(html);
  for (const bad of ["undefined", "[object Object]", "NaN"]) {
    expect(text.includes(bad), `${path} に "${bad}" が表示されている`).toBe(false);
  }
  return html;
}

function firstDir(dir: string): string {
  const d = readdirSync(join(STATIC_DIR, dir), { withFileTypes: true }).find((e) => e.isDirectory());
  if (!d) throw new Error(`${dir} に静的ページが無い`);
  return d.name;
}

// ---------------------------------------------------------------------------
// 既知の不具合。ここに載っているURLはリンク切れ判定から除外する。直したらこの一覧から消すこと。
// 新たなリンク切れはテスト失敗になる。
// ---------------------------------------------------------------------------
const KNOWN_BROKEN = new Set<string>([]);
const isKnownBroken = (href: string) => KNOWN_BROKEN.has(href.replace(/\/$/, ""));

// ---------------------------------------------------------------------------
// 主要画面（静的プリレンダ＋SSR）
// ---------------------------------------------------------------------------
const MAIN_PAGES = [
  // prerender
  "/",
  "/players/",
  "/leagues/",
  "/leagues/top14/",
  "/standings/",
  "/results/",
  "/national-teams/",
  "/schools/",
  "/rwc2027/",
  // SSR
  "/about/",
  "/news/",
  "/teams/",
  "/privacy/",
  "/terms/",
  "/contact/",
  "/world-rankings/",
];

describe("主要画面が 200 で正常に描画される", () => {
  it.each(MAIN_PAGES)("%s", async (path) => {
    await expectHealthyPage(path);
  });

  it("存在しないURLは 404", async () => {
    const res = await get("/__no_such_page__/");
    expect(res.status).toBe(404);
  });

  it("トップページに主要セクションへのリンクがある", async () => {
    const html = await expectHealthyPage("/");
    for (const href of ["/standings", "/news", "/teams/league-one"]) {
      expect(new RegExp(`href="${href}/?"`).test(html), `トップに ${href} へのリンクが無い`).toBe(true);
    }
  });

  it("sitemap / robots.txt が配信される", async () => {
    expect((await get("/sitemap-index.xml")).status).toBe(200);
    const robots = await get("/robots.txt");
    expect(robots.status).toBe(200);
  });
});

// ---------------------------------------------------------------------------
// master（SSOT）由来の値がページに出ていること
// ---------------------------------------------------------------------------
describe("選手ページ（master 駆動）", () => {
  const pages = readJson(join(ROOT, "data/manual/player_pages.json")).players as { id: string; slug: string }[];
  const byId = new Map<string, Record<string, unknown>>();
  for (const f of readdirSync(join(MASTER, "players"))) {
    if (!f.endsWith(".json")) continue;
    for (const p of readJson(join(MASTER, "players", f))) if (!byId.has(p.id)) byId.set(p.id, p);
  }
  const sample = pages.filter((r) => byId.has(r.id)).slice(0, 5);

  it("サンプル選手が存在する", () => {
    expect(sample.length).toBeGreaterThan(0);
  });

  it.each(sample.map((r) => [r.slug, r.id]))("/players/%s/ に master の氏名が表示される", async (slug, id) => {
    const html = unescapeHtml(await expectHealthyPage(`/players/${encodeURIComponent(slug)}/`));
    const p = byId.get(id)!;
    const names = [p.name_ja, p.name_en].filter((v): v is string => typeof v === "string" && v.length > 0);
    expect(names.length).toBeGreaterThan(0);
    const normalized = html.replace(/\s+/g, " ").toLowerCase();
    const hit = names.some((n) => normalized.includes(n.replace(/\s+/g, " ").toLowerCase()) ||
      n.split(/\s+/).every((part) => normalized.includes(part.toLowerCase())));
    expect(hit, `${slug}: ${names.join(" / ")} がページに無い`).toBe(true);
  });
});

describe("チームページ", () => {
  const league = "league-one";
  const slug = firstDir(`teams/${league}`);
  it(`/teams/${league}/{slug}/ が描画される`, async () => {
    await expectHealthyPage(`/teams/${league}/${encodeURIComponent(slug)}/`);
  });
});

describe("ニュース記事", () => {
  const slug = firstDir("news");
  it(`/news/{slug}/ が描画される`, async () => {
    await expectHealthyPage(`/news/${encodeURIComponent(slug)}/`);
  });
});

describe("リーグページ（master teams と突合）", () => {
  it("/leagues/top14/ に master の Top14 全チームが表示される", async () => {
    const teams = readJson(join(MASTER, "teams/top14.json")) as { id: string; name_ja: string | null; name_en: string | null }[];
    expect(teams.length).toBeGreaterThan(0);
    const html = unescapeHtml(await expectHealthyPage("/leagues/top14/"));
    const missing = teams.filter((t) => ![t.name_ja, t.name_en].some((n) => !!n && html.includes(n)));
    expect(missing.map((t) => t.id)).toEqual([]);
  });
});

// ---------------------------------------------------------------------------
// 内部リンク・リダイレクト
// ---------------------------------------------------------------------------
async function resolveFinal(path: string, maxHops = 5): Promise<{ status: number; path: string }> {
  let cur = path;
  for (let i = 0; i <= maxHops; i++) {
    const res = await get(cur);
    if (res.status >= 300 && res.status < 400) {
      const loc = res.headers.get("location");
      if (!loc) return { status: res.status, path: cur };
      const next = new URL(loc, baseUrl + cur);
      if (next.origin !== baseUrl) return { status: 200, path: next.href }; // 外部
      cur = next.pathname + next.search;
      continue;
    }
    return { status: res.status, path: cur };
  }
  return { status: 508, path: cur };
}

function internalLinks(html: string): string[] {
  const out = new Set<string>();
  const body = html.replace(/<script[\s\S]*?<\/script>/gi, " ");
  for (const m of body.matchAll(/href="(\/[^"#?]*)/g)) {
    const href = unescapeHtml(m[1]);
    if (href.startsWith("//") || href.startsWith("/_astro/")) continue;
    out.add(href);
  }
  return [...out];
}

describe("主要画面の内部リンクが切れていない", () => {
  it.each(["/", "/players/", "/standings/", "/leagues/", "/national-teams/"])("%s", async (page) => {
    const html = await (await get(page)).text();
    const broken: string[] = [];
    for (const href of internalLinks(html)) {
      if (isKnownBroken(href)) continue;
      const { status, path } = await resolveFinal(href);
      if (status >= 400) broken.push(`${href} -> ${path} (${status})`);
    }
    expect(broken, broken.join("\n")).toEqual([]);
  }, 120_000);
});

describe("master の redirects.json の行き先が解決できる", () => {
  it("全リダイレクトが最終的に 200 に到達する", async () => {
    const redirects = readJson(join(MASTER, "_meta/redirects.json")) as Record<string, string>;
    const broken: string[] = [];
    for (const from of Object.keys(redirects)) {
      if (isKnownBroken(from)) continue;
      const { status, path } = await resolveFinal(from + "/");
      if (status !== 200) broken.push(`${from} -> ${path} (${status})`);
    }
    expect(broken, broken.join("\n")).toEqual([]);
  }, 300_000);
});
