# Plan: Stack-Routed Context

Agents should load only the Tikal docs that match the consuming project's
type. Currently Tikal supports Typescript, Flutter, and Astro. More stacks can be added the same way.

## Problem

Every agent entrypoint (Claude, Cursor, Copilot, Windsurf) points at the same
generic `processes/getting-started.md`. There is no project-type switch, so
adding Flutter review guidance would land in every session — including
non-Flutter repos that vendor Tikal.

`getting-started.md` is also the per-project overview template. If Tikal is a
submodule, editing that file dirties the submodule. Project-specific facts
must live *outside* `ai-coding-tools/`.

## Current organization

```
consumer repo (or this repo)
├── CLAUDE.md / .cursor/rules / copilot / windsurf
│         │
│         └── always load ──► ai-coding-tools/processes/getting-started.md
│                             ai-coding-tools/processes/rules-of-engagement.md
│                             (no type filter; no Flutter pack)
└── (no project-type config)
```

## Target organization

```
consumer repo
├── tikal.yaml                 # allow-list: project.types
├── tikal.project.md           # this repo's overview (optional)
├── plans/                     # this repo's implementation plans
├── CLAUDE.md / .cursor/rules  # thin: "read tikal.yaml, then the router"
└── ai-coding-tools/
    ├── processes/
    │   ├── getting-started.md           # ROUTER (always-on, small)
    │   ├── project-overview.template.md
    │   └── rules-of-engagement.md       # stack-agnostic
    └── stacks/
        ├── flutter/                     # loaded only if types includes flutter
        ├── typescript/                  # listed, or implied by astro
        └── astro/                       # implies typescript
```

## Mechanism

1. **Allow-list config** at the consuming repo root: `tikal.yaml`
   (or `.tikal.yaml` / `tikal.json`).
2. **Fallback detection** when the config is missing: `pubspec.yaml` with a
   top-level `flutter:` key ⇒ `flutter`; `astro.config.*` ⇒ `astro`
   (implies `typescript`); `tsconfig.json` ⇒ `typescript`.
3. **Implied bases:** `STACK_IMPLIES` inserts base stacks before the
   declaring type (`astro` → `typescript`, `astro`). Agents load the
   expanded list, not only the raw YAML.
4. **Router** (`processes/getting-started.md`) tells agents to load
   `tikal.project.md` plus `stacks/<type>/` for each expanded type, and to
   skip every other stack.
5. **`resolve_stack.py`** is the programmatic source of truth (hooks, init,
   tests). `check_file_changes.py` reloads only active-stack files.
6. **`init_project.py --type flutter|typescript|astro`** writes the config
   and copies entrypoint templates (including implied-base Cursor rules).

Cursor cannot hide `.mdc` files from a YAML file at session start. The
portable approach (Claude, Cursor, Copilot, Windsurf) is a tiny always-on
router plus on-demand stack files. Optional Cursor glob rules
(`**/*.dart`) are templates copied into the consuming project so Flutter
review attaches when Dart files are in play.

## Tikal itself

This repository is the framework, not a Flutter app. Its `tikal.yaml` has
an empty `types` list so agents do not load the Flutter pack while
working on Tikal.

## Status

Implemented: router, `tikal.yaml`, `resolve_stack.py` (including
`STACK_IMPLIES` and any-file detection), `init_project.py`, Flutter /
TypeScript / Astro stack docs, Cursor glob templates, and unit tests.
