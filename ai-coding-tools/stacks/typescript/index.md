# TypeScript Stack

Load these files when `tikal.yaml` lists `typescript`, or when another
stack implies it (`astro` always loads this pack). Skip this directory
when TypeScript is not in the expanded type list.

Framework packs (Astro now; Vite or Next later) add their own docs on
top of this base. Do not treat this stack as permission to introduce a
second UI framework.

Read in this order:

1. `tikal.project.md` at the repo root — this app's commands and layout
2. `commands.md` — typecheck, lint, test, and the repo's own scripts
3. `review.md` — TypeScript review checklist
4. `architecture.md` — follow the existing app shell
