# Astro Architecture

Prefer the layout these content sites already use:

```
src/
  pages/                 # file-based routes, including [slug].astro
  content/
    config.ts            # defineCollection + Zod schemas
    <collection>/*.md    # Markdown entries
  layouts/               # Layout.astro and collection layouts
  components/            # Navigation, Footer, Metadata, cards
astro.config.mjs
tsconfig.json            # extends astro/tsconfigs/strict
```

## Boundaries

- New writing goes in an **existing** collection when the topic fits.
  Add a collection only when the user asks for a new section.
- Pages render collections. Components do not fetch collections unless
  neighboring components already do.
- `astro.config.mjs` stays minimal (`site`, `base`). Do not add MDX,
  Starlight, a CMS, or a UI framework unless it is already a dependency.

## When analyzing an unfamiliar Astro repo

1. Read `package.json`, `astro.config.*`, `src/content/config.ts`, and
   `tikal.project.md`.
2. Open one complete collection: schema, Markdown entry, index page,
   `[slug].astro`, layout.
3. Copy that shape. Then change code.
