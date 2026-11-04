# Tikal

An agent that loads every instruction it might someday need spends its attention on the wrong project. Tikal keeps that set small. A thin entrypoint points at one router, `processes/getting-started.md`. The router names the files for this repository and leaves the rest closed.

A **stack** is the instruction pack for one project type. Flutter, TypeScript, and Astro each have one. The router opens a stack only when this repository lists that type.

These pages are for people. Agents do not load `docs/`. The working copy of a workflow stays in `ai-coding-tools/processes/` and `ai-coding-tools/stacks/`.

The [README](../README.md) is the executive summary. Read the pages below for the mechanism and the commands.

1. [Usage](usage.md) — attach Tikal, write the config, run the checks.
2. [Context](context.md) — which stack files a session opens.
3. [Principles](principles.md) — the philosophy loaded on every session, and why the entrypoints stay thin.
4. [Commits](commits.md) — when a commit happens, and when the agent only proposes a message.
5. [Skills](skills.md) — how a skill opens one process by id.

When a feature arrives, add a short page here and put its graph on that page. Leave the README as the summary.
