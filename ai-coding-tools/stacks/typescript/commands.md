# TypeScript Commands

Use the package manager and scripts already in `package.json`. Do not
switch between npm, pnpm, and yarn.

```bash
npx tsc --noEmit
```

If the repo defines them, prefer the project scripts:

```bash
npm test
npm run lint
npm run build
npm run dev
```

After TypeScript edits, run `tsc --noEmit` (or the repo's typecheck
script) and the tests that cover the change before calling the work done.
Do not add ESLint, Prettier, Vitest, or other toolchain packages unless
the user asks.
