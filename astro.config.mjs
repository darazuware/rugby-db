// @ts-check
import { defineConfig } from 'astro/config';

import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';
import vercel from '@astrojs/vercel';

import sitemap from '@astrojs/sitemap';
import thinPages from './data/manual/thin_pages.json' with { type: 'json' };

const thinPaths = new Set([
  ...thinPages.players.map((s) => `/players/${s}/`),
  ...thinPages.teams,
  '/dream-team/', '/magazine/', '/sitemap/', '/notice/saimoni-vunilagi/',
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