# Principles

A philosophy that loads only when someone is already “doing design work” never meets the edit that needed it. Copying that file into every agent entrypoint would spread one decision across Claude, Cursor, Copilot, and Windsurf.

The router is the only door. Entrypoints stay a pointer at `processes/getting-started.md`. The router always opens three stack-agnostic files, then the stacks this repository lists.

```
agent entrypoints (thin)
        │
        └── always ──► processes/getting-started.md
                            │
                            ├── tikal.project.md
                            ├── processes/rules-of-engagement.md   how we work
                            ├── processes/programmer-mindset.md    how the programmer thinks
                            ├── processes/design-principles.md     how we shape modules
                            └── stacks/<type>/                     if listed

optional: refactoring.md, benchmarking.md, git.md, code-review.md
```

`rules-of-engagement.md` covers collaboration, naming, comments, tests, errors, and plans. `programmer-mindset.md` covers the stance the programmer takes toward a task. `design-principles.md` covers complexity, modules, interfaces, and change. Each one states its job. None of them restates the others.

`design-principles.md` is stack-agnostic. Language and framework layout live in `stacks/<type>/architecture.md`. When a stack doc and the principles disagree on a framework idiom, follow the stack. An idiom that explodes complexity, or that leaks internals across a module boundary, loses to the principles.

The recorded host plan drew this path before programmer mindset joined the always-on set. The diagram above is the current one. The decision record is [plans/design-principles-host.md](../plans/design-principles-host.md).

The rules themselves stay in [design-principles.md](../ai-coding-tools/processes/design-principles.md). This page is the load path.
