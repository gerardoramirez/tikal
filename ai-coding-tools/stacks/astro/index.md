# Astro Stack

Load these files when `tikal.yaml` lists `astro` (or Astro was detected
from `astro.config.mjs` / `.ts` / `.js`). `astro` always implies the
TypeScript stack — read `../typescript/index.md` first.

These sites are content collections plus file-based `src/pages` routes,
not Starlight, MDX, or a CMS unless the repo already has them.

Read in this order:

1. `tikal.project.md` at the repo root — this site's commands and layout
2. `../typescript/` — shared TypeScript commands, review, and architecture
3. `commands.md` — astro dev, build, preview, check
4. `review.md` — collections, frontmatter, routes
5. `architecture.md` — pages, content, layouts, components
