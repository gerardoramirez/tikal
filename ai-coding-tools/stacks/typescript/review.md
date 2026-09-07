# TypeScript Review and Analysis

Use this when reviewing TypeScript code or analyzing a change. Report
concrete file and symbol names, not generic advice.

## Typecheck first

- `tsc --noEmit` (or the repo's typecheck script) must be clean for files
  you touched.
- Honor `tsconfig.json` (and `tsconfig.*.json` project references). Do not
  weaken `strict` or add `// @ts-ignore` / `// @ts-expect-error` to make a
  change pass.

## Correctness

- Do not introduce new `any`. Prefer existing types, `unknown` plus
  narrowing, or a type the file already uses.
- Public functions and exported components keep explicit return types when
  neighboring code does.
- Do not assert away null with `!` unless the invariant is obvious and
  already used in this module.
- Async functions must not swallow errors. Match the repo's error path
  (throw, Result, or returned error).

## Lint and style

- Follow the existing ESLint / typescript-eslint config. Do not add a
  second lint stack.
- Match import style, path aliases, and file naming already in the repo.

## Tests

- Unit tests for logic you change; component tests only if the repo
  already has that runner (Vitest, Jest, Testing Library).
- Name tests `subject_under_test__in_situation__does_thing` unless this
  repo already uses a different convention — then match the repo.

## Shipping hygiene

- Secrets stay out of source. Use the project's existing env / define path.
- Do not commit `dist/`, `.astro/`, or other build output.
