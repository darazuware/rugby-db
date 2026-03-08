// @ts-check
import { defineConfig } from 'astro/config';

import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';
import vercel from '@astrojs/vercel';

// https://astro.build/config
export default defineConfig({
  site: "https://rugbypick.com",
  integrations: [react()],
  adapter: vercel(),
  vite: {
    plugins: [tailwindcss()]
  }
});