# Tikal Context Router

Load only the docs that match this repository. Do not open other stacks.

## 1. Resolve the project type

1. Read `tikal.yaml` at the repository root (also accept `.tikal.yaml` or `tikal.json`).
2. `project.types` is the allow-list. Example: `types: [flutter]` or `types: [astro]`.
3. Expand implied bases before loading. `astro` always includes `typescript`.
   Confirm with `python3 ai-coding-tools/scripts/resolve_stack.py` — use the
   expanded `types` list, not only the raw YAML.
4. If the config is missing, infer types:
   - `pubspec.yaml` with a top-level `flutter:` key → `flutter`
   - `astro.config.mjs` / `.ts` / `.js` → `astro` (implies `typescript`)
   - `tsconfig.json` → `typescript`
   - otherwise no stack — ask the user to add `tikal.yaml`

## 2. Load these files — and only these

| File | When |
|---|---|
| `tikal.project.md` | If it exists. Project-specific overview (commands, layout, architecture). |
| `ai-coding-tools/processes/rules-of-engagement.md` | Always. Communication and code-style guardrails. |
| `ai-coding-tools/stacks/<type>/index.md` then the files it lists | For **each** type in the **expanded** list that has a stack directory. |

Do **not** read `ai-coding-tools/stacks/*` entries that are not in the
expanded type list.

Project plans live in `plans/` at the repository root. Do not create
app files inside `ai-coding-tools/`.

Optional process files — open only when the user is doing that work:

- `ai-coding-tools/processes/refactoring.md` — production TDD refactor
- `ai-coding-tools/processes/benchmarking.md` — speed work
- `ai-coding-tools/processes/git.md` — commit only when the user asked
- `ai-coding-tools/design-principles.md` — shared design rules

## 3. If this is a new checkout

```bash
python3 ai-coding-tools/scripts/init_project.py --type flutter
python3 ai-coding-tools/scripts/init_project.py --type astro
python3 ai-coding-tools/scripts/init_project.py --type typescript
```

That writes `tikal.yaml`, copies `tikal.project.md` from the template, and
installs agent entrypoints. `--type astro` writes `astro` only; resolve
expands it to TypeScript + Astro. Fill in `tikal.project.md` for this repo.
