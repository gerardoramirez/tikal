# Plan: Design Principles Host

Give agents a single, stack-agnostic philosophy file for shaping code, and
load it through the existing router — not from each agent entrypoint.

## Problem

`ai-coding-tools/design-principles.md` is a stub at the toolkit root. The
router lists it as optional, so sessions that write code never see it unless
someone is already "doing design work." Agent files (`CLAUDE.md`,
`.cursor/rules/tikal.mdc`, Copilot, Windsurf) stay thin and only point at
`getting-started.md`; they should not grow a second `@` path.

## Current organization

```
agent entrypoints (CLAUDE.md, tikal.mdc, …)
        │
        └── always ──► processes/getting-started.md
                            │
                            ├── tikal.project.md
                            ├── processes/rules-of-engagement.md   ALWAYS
                            ├── stacks/<type>/                     if listed
                            └── design-principles.md               OPTIONAL, toolkit root
                                    (not in processes/; not in ALWAYS_TRACKED globs
                                     except by accident if someone opens it)
```

## Target organization

```
agent entrypoints (unchanged, still thin)
        │
        └── always ──► processes/getting-started.md
                            │
                            ├── tikal.project.md
                            ├── processes/rules-of-engagement.md   ALWAYS (how we work)
                            ├── processes/design-principles.md     ALWAYS (how we shape code)
                            └── stacks/<type>/                     if listed

optional: refactoring.md, benchmarking.md, git.md
```

## Mechanism

1. **Location:** `ai-coding-tools/processes/design-principles.md`
   - Ships with the toolkit (submodule / inner symlink).
   - Stack-agnostic, same family as rules-of-engagement.
   - Covered by existing `ALWAYS_TRACKED` glob `ai-coding-tools/processes/*.md`.
2. **Router:** Move it from the optional list into the always-load table.
3. **Agent files:** No new `@` links. Tying is: entrypoint → router → this file.
4. **Remove** the stub at `ai-coding-tools/design-principles.md`.
5. **README / tikal.project.md:** Show it as always-on process, not optional.

## Status

Implemented.
