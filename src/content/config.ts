import { defineCollection, z } from 'astro:content';

const players = defineCollection({
    type: 'content',
    schema: z.object({
        title: z.string(),
        name_en: z.string().optional(),
        name_ja: z.string().optional(),
        slug: z.string().optional(),
        position: z.string().optional(),
        team: z.string().optional(),
        height: z.string().optional(),
        weight: z.string().optional(),
        birth_date: z.string().optional(),
        age: z.number().nullable(),
        country: z.string().optional(),
        birth_place_scraped: z.string().optional(),
        league: z.string().optional(),
        caps: z.string().optional(),
        scraped_url: z.string().optional(),
        high_school: z.string().optional(),
        university: z.string().optional(),
        junior_high_school: z.string().optional(),
        rugby_school: z.string().optional(),
        league_one_caps: z.string().optional(),
        category: z.string().optional(),
        division: z.string().optional(),
        joined_year: z.number().nullable().optional(),
        has_scores: z.union([z.boolean(), z.string()]).optional(),
        tries: z.number().optional(),
        matches: z.number().optional(),
        starts: z.number().optional(),
        minutes: z.number().optional(),
        career_history_json: z.string().optional(),
        aliases: z.array(z.string()).optional(),
    }),
});

const news = defineCollection({
    type: 'content',
    schema: z.object({
        title: z.string(),
        description: z.string().optional(),
        pubDate: z.date(),
        // 予約公開の正確な日時（任意）。指定時はこの時刻で公開判定する。
        // 未指定なら pubDate の JST 当日 0:00 で公開扱い（従来動作）。
        publishAt: z.date().optional(),
        updatedDate: z.date().optional(),
        heroImage: z.string().optional(),
        category: z.string().optional(),
        tags: z.array(z.string()).optional(),
        draft: z.boolean().optional().default(false),
    }),
});

const teams = defineCollection({
    type: 'content',
    schema: z.object({
        title: z.string(),
        league: z.string(),
        updatedDate: z.date().optional(),
        draft: z.boolean().optional().default(false),
    }),
});

export const collections = {
    'players': players,
    'news': news,
    'teams': teams,
};
