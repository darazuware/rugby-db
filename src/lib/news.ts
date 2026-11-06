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

/** 公開済みかつインデックス対象（noindexでない）ニュース。一覧・トップ導線用 */
export const getIndexableNews = async () =>
  (await getLiveNews()).filter((e: CollectionEntry<"news">) => !e.data.noindex);

const FEATURE_CATEGORIES = ["COLUMN", "GUIDE"];
const FEATURE_PRIORITY = /RWC ?2027|ワールドカップ|日本代表|24カ国|ネーションズ/;

/** 独自性の高いCOLUMN/GUIDE。RWC2027・日本代表系を優先し、同順位は新しい順 */
export const getFeaturedNews = async (limit = 6) =>
  (await getIndexableNews())
    .filter((e: CollectionEntry<"news">) => FEATURE_CATEGORIES.includes(e.data.category ?? ""))
    .sort((a: CollectionEntry<"news">, b: CollectionEntry<"news">) => {
      const pa = FEATURE_PRIORITY.test(a.data.title) ? 1 : 0;
      const pb = FEATURE_PRIORITY.test(b.data.title) ? 1 : 0;
      return pb - pa || b.data.pubDate.valueOf() - a.data.pubDate.valueOf();
    })
    .slice(0, limit);
