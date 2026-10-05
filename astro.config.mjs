// @ts-check
import { defineConfig } from 'astro/config';

import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';
import vercel from '@astrojs/vercel';

import sitemap from '@astrojs/sitemap';
import thinPages from './data/manual/thin_pages.json' with { type: 'json' };
import { readdirSync, readFileSync } from 'node:fs';

// frontmatter に noindex: true を持つニュース記事
const noindexNews = readdirSync('./src/content/news')
  .filter((f) => f.endsWith('.md') && /^noindex:\s*true\s*$/m.test(readFileSync(`./src/content/news/${f}`, 'utf-8').split(/^---$/m)[1] ?? ''))
  .map((f) => `/news/${f.replace(/\.md$/, '').toLowerCase()}/`); // Astro は content slug を小文字化する

const thinPaths = new Set([
  ...thinPages.players.map((s) => `/players/${s}/`),
  ...thinPages.teams,
  ...noindexNews,
  '/dream-team/', '/magazine/', '/sitemap/', '/notice/saimoni-vunilagi/',
  // /teams/[league] と重複する noindex ページ
  ...['league-one', 'super-rugby', 'top14', 'premiership', 'urc'].map((l) => `/leagues/${l}/`),
]);

// https://astro.build/config
export default defineConfig({
  site: "https://rugbypick.com",
  output: 'server',
  integrations: [
    react(),
    sitemap({
      changefreq: 'daily',
      priority: 0.7,
      lastmod: new Date(),
      filter: (page) => {
        if (page.includes('/api/')) return false;
        const p = decodeURI(new URL(page).pathname);
        return !thinPaths.has(p.endsWith('/') ? p : p + '/');
      },
    }),
  ],
  adapter: vercel({
    webAnalytics: {
      enabled: true,
    },

  }),
  vite: {
    plugins: [tailwindcss()]
  }
});