import { getCollection, type CollectionEntry } from "astro:content";

// pubDate は日付のみ＝UTC真夜中に解釈される。読者は日本なので JST 基準で判定する。
// publishAt があればその日時。無ければ pubDate（UTC0:00）-2h = JST 当日 7:00 に公開。
const REVEAL_OFFSET_MS = -2 * 60 * 60 * 1000;

export const liveTs = (e: CollectionEntry<"news">) =>
  e.data.publishAt ? e.data.publishAt.valueOf() : e.data.pubDate.valueOf() + REVEAL_OFFSET_MS;

export const isLive = (e: CollectionEntry<"news">) => !e.data.draft && liveTs(e) <= Date.now();

/** 公開済みニュースを新しい順で返す */
export const getLiveNews = async () =>
  (await getCollection("news", isLive)).sort(
    (a: CollectionEntry<"news">, b: CollectionEntry<"news">) =>
      b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
  );
