# TypeScript Architecture

Follow the app shell this repo already uses. Do not introduce a second
UI or build stack.

Typical shells in this pipeline:

- **Astro** — `src/pages`, `src/content`, `src/layouts` (also load the
  Astro stack)
- **Vite + React** — `src/` with the existing router and `vite.config.*`
- **Next.js** — `app/` or `pages/` as already present
- **Expo** — `app/` / `components/` as already present

## Boundaries

- Keep types next to the module that owns them, or in the repo's existing
  `types/` folder. Do not create a parallel type tree for a small change.
- Shared utilities stay in the existing shared/lib directory. A new
  feature goes in its own folder under the existing features/modules root.
- Config (`tsconfig.json`, `vite.config.ts`, `astro.config.mjs`,
  `next.config.ts`) stays consistent with neighbors. Do not add a new
  bundler.

## When analyzing an unfamiliar TypeScript repo

1. Read `package.json`, `tsconfig.json`, and `tikal.project.md`.
2. Skim the existing entrypoint and one complete feature.
3. Copy that feature's shape. Then change code.
