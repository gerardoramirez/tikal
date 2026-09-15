# Software Design Principles

Stack-agnostic rules for shaping code. Agents load this whenever they write
or change code. Language and framework layout live in
`stacks/<type>/architecture.md`. This file governs complexity and module
design in every stack.

## How this relates to other Tikal docs

| Doc | Job |
|---|---|
| `processes/rules-of-engagement.md` | Collaboration, naming, comments, tests, errors, plans |
| `processes/design-principles.md` (this file) | Modules, interfaces, complexity, change |
| `stacks/<type>/` | Framework and language conventions |

If a stack doc and this file disagree on a framework idiom, follow the stack.
Do not follow an idiom that explodes complexity or leaks internals across
module boundaries.

## 1. Complexity is the enemy

The job is to reduce the complexity that a later reader (human or agent)
must hold in their head — not to demonstrate cleverness.

- Prefer a design whose pieces can be understood one at a time.
- Do not spread a single decision across many files.
- Do not introduce a second pattern for a problem the repo already solved.

## 2. Deep modules, small interfaces

A module should hide a lot of mechanism behind a small, stable surface.

- Callers should not need to know how the work is done.
- If using a module requires knowing its internals, the interface is too
  shallow — hide more, or split the wrong boundary.
- New features go in their own directory when they can; do not drip a
  feature through unrelated packages.

## 3. Hide information at the right boundary

Each module owns a secret: a data format, a policy, a dependency, a
failure mode.

- Put knowledge next to the code that must change when that knowledge
  changes.
- Do not leak types, paths, or status codes that callers cannot act on.
- Pass the data a callee needs, not the object graph it might rummage
  through.

## 4. Design for the change you can name

Change will happen. Guessing every future change is not design.

- Make the variation you already know inexpensive (a new stack, a new
  command, a new error case).
- Do not add indirection, generics, or plugin seams for hypothetical
  futures. YAGNI applies to architecture too.
- When two designs are equal, pick the one that matches this repo.

## 5. Make illegal states hard to represent

If a combination should never happen, do not let the type, constructor, or
API express it.

- Validate at the edge; keep inner code on the happy shape.
- Prefer explicit types over booleans and string modes that can be
  combined wrongly.
- Fail at the call that is wrong, with an error that says what to change
  (see rules-of-engagement for message quality).

## 6. One reason to change

A module should have one job and one audience.

- Split when a file mixes unrelated reasons to edit (parsing and display,
  I/O and policy, two product features).
- Do not split when the pieces are only understood together — that makes
  shallow modules and a larger interface.

## 7. Consistency over novelty

A codebase is a dialect. Speak it.

- Match existing names, layering, and error style even if you prefer
  another school.
- A new abstraction must earn its keep: it removes duplication or hides a
  real secret, not just "we might need it."

## Applying these while coding

1. Before adding a type or file, name the secret it hides and the callers
   that should not see that secret.
2. After the change, a reader should understand the new surface without
   opening the implementation.
3. If the change fights the current architecture, stop and plan — do not
   paper over it with a helper in the wrong layer.
