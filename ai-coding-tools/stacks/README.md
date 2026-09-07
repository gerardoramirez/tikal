# Stacks

Each directory here is a project type. Agents load a stack only when
`tikal.yaml` lists that type or another type implies it
(see `processes/getting-started.md`).

| Directory | Enable with | Also loads |
|---|---|---|
| `flutter/` | `project.types: [flutter]` | — |
| `typescript/` | `project.types: [typescript]` | — |
| `astro/` | `project.types: [astro]` | `typescript` |

To add a stack: create `stacks/<type>/index.md` plus focused docs, register
detection markers (and `STACK_IMPLIES` if it has a base) in
`scripts/resolve_stack.py`, and add the type to `KNOWN_STACKS` in
`scripts/init_project.py`.
