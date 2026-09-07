# Astro Commands

Prefer the scripts in `package.json`. Typical Astro 5 sites in this
pipeline use:

```bash
npm run dev
npm run build
npm run preview
npx astro check
```

`astro check` plus `tsc --noEmit` (see the TypeScript stack) after
`.astro`, `.ts`, or content-schema edits. Do not add MDX, Starlight, or
adapter packages unless the user asks.

If the site is already deployed (Netlify, Vercel, GitHub Pages), keep the
existing `astro.config` `site` / `base` values.
