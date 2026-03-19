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
        league_one_caps: z.string().optional(),
        category: z.string().optional(),
        division: z.string().optional(),
        joined_year: z.number().nullable().optional(),
        has_scores: z.union([z.boolean(), z.string()]).optional(),
        tries: z.number().optional(),
        matches: z.number().optional(),
        starts: z.number().optional(),
        minutes: z.number().optional(),
    }),
});

export const collections = {
    'players': players,
};
