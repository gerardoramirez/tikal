# Programmer Mindset

How the programmer thinks. Agents load this whenever they write or change
code. It is not a review checklist. Judge a diff against
`processes/design-principles.md`.

## How this relates to other Tikal docs

| Doc | Job |
|---|---|
| `processes/rules-of-engagement.md` | Collaboration, naming, comments, tests, errors, plans |
| `processes/programmer-mindset.md` (this file) | How the programmer thinks |
| `processes/design-principles.md` | Modules, interfaces, complexity, change |
| `stacks/<type>/` | Framework and language conventions |

## 1. Take a strategic approach

The mindset you adopt when you approach a task is part of the design.

Many organizations encourage a tactical mindset. Its focus is getting
something working: a new feature or a bug fix. At first glance that
seems reasonable. It is short-sighted. The task is finished as quickly
as possible, so planning for the future is not a priority. Little time
goes to looking for the best design. The aim is something that works
soon.

A good system design is nearly impossible to produce that way. The
system becomes complicated through the accumulation of dozens or
hundreds of small things. That is the complexity
`processes/design-principles.md` treats as the enemy.

A strategic approach invests time to produce a clean design and to fix
problems. The rules in that file are how the investment shows up in
modules and interfaces.

## 2. Balance competing ideas

A good design balances competing ideas and approaches. Do not take any
design to its extreme — past that point the design gets worse.
