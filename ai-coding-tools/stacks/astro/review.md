# Astro Review and Analysis

Use this when reviewing an Astro content site or analyzing a change.
Report concrete collection names, slugs, and page files.

## Content collections

- New or changed Markdown must satisfy the Zod schema in
  `src/content/config.ts` (or the collection file this repo uses).
- Honor `draft` (and other flags the schema already defines). Do not
  invent frontmatter keys that the schema does not allow.
- Dates, tags, and titles stay consistent with neighboring entries in
  that collection.

## Routes

- File-based routing lives in `src/pages`. List pages and `[slug].astro`
  detail pages stay in the same collection pair.
- A new collection needs both a schema and the matching pages. Do not
  leave an orphan collection or an orphan route.
- `getCollection` / `getEntry` filters (drafts, sort by date) should match
  how sibling pages already query that collection.

## Components and islands

- Keep `.astro` components presentational. Data loading stays in pages or
  layouts, the way neighboring files do it.
- Do not add a client island (`client:load`, `client:visible`, etc.)
  unless this repo already uses islands for that kind of widget.
- Shared chrome (nav, footer, metadata) goes in existing
  `src/components` / `src/layouts` files. Do not fork a second layout.

## Typecheck and build

- `astro check` and a production `astro build` must succeed for the
  files you touched.
- Do not disable content-collection type generation or weaken
  `astro/tsconfigs/strict`.
