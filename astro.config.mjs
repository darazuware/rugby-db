// @ts-check
import { defineConfig } from 'astro/config';

import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';
import vercel from '@astrojs/vercel';

import sitemap from '@astrojs/sitemap';

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
      filter: (page) => !page.includes('/api/'),
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