/**
 * relatedNews.ts
 * 選手ページの「関連ニュース」— 公開済みニュース本文中の /players/{slug}/ リンクを
 * 逆引きインデックス化するだけ。AIによる要約・トピック文の新規生成は行わない
 * （リンクは news_gen.py / scripts/link_news.py が既存ルールに従って張った実リンクのみを拾う）。
 */
import type { CollectionEntry } from "astro:content";
import { getLiveNews } from "./news";

export interface RelatedNewsItem {
  slug: string;
  title: string;
  pubDate: Date;
  category?: string;
}

const PLAYER_LINK_RE = /\/players\/([a-z0-9][a-z0-9-]*)\/?\)/g;

function extractPlayerSlugs(body: string): Set<string> {
  const slugs = new Set<string>();
  let m: RegExpExecArray | null;
  PLAYER_LINK_RE.lastIndex = 0;
  while ((m = PLAYER_LINK_RE.exec(body))) {
    slugs.add(m[1]);
  }
  return slugs;
}

function buildIndex(entries: CollectionEntry<"news">[]): Map<string, RelatedNewsItem[]> {
  const index = new Map<string, RelatedNewsItem[]>();
  for (const entry of entries) {
    const slugs = extractPlayerSlugs(entry.body ?? "");
    if (slugs.size === 0) continue;
    const item: RelatedNewsItem = {
      slug: entry.slug,
      title: entry.data.title,
      pubDate: entry.data.pubDate,
      category: entry.data.category,
    };
    for (const slug of slugs) {
      const list = index.get(slug);
      if (list) list.push(item);
      else index.set(slug, [item]);
    }
  }
  return index;
}

let _relatedNewsIndexCache: Promise<Map<string, RelatedNewsItem[]>> | null = null;

/** ニュース本文からリンクされた選手slug → 関連ニュース一覧（新しい順）。ビルド中一度だけ構築。 */
export function getRelatedNewsIndex(): Promise<Map<string, RelatedNewsItem[]>> {
  if (!_relatedNewsIndexCache) {
    _relatedNewsIndexCache = getLiveNews().then(buildIndex);
  }
  return _relatedNewsIndexCache;
}

/** 指定した選手slugに関連するニュース（新しい順、最大limit件）。 */
export async function getRelatedNews(slug: string, limit = 3): Promise<RelatedNewsItem[]> {
  const index = await getRelatedNewsIndex();
  return (index.get(slug) ?? []).slice(0, limit);
}

export function __resetRelatedNewsCacheForTests(): void {
  _relatedNewsIndexCache = null;
}
