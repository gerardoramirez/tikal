---
name: tikal
description: Load one Tikal process by id when another skill or the user names it. Process ids are code-review, git, refactoring, benchmarking, design-principles, rules-of-engagement, programmer-mindset, and htdd-gate.
disable-model-invocation: true
---

# Tikal processes

Use this when a skill or the user names a Tikal process. Do not load every process. The process file is the workflow. This skill only finds it.

## Find the resolver

Locate `resolve_process.py` in this order:

1. If `TIKAL_HOME` is set, use `$TIKAL_HOME/ai-coding-tools/scripts/resolve_process.py` when that clone root exists, or `$TIKAL_HOME/scripts/resolve_process.py` when `TIKAL_HOME` is the `ai-coding-tools` directory.
2. Otherwise walk up from the workspace for `ai-coding-tools/scripts/resolve_process.py`.
3. Otherwise use `~/.tikal/ai-coding-tools/scripts/resolve_process.py`. `~/.tikal` is the clone root or a symlink to it.

Run that script with `python3` and the process id. Read only the paths it prints. Do not load the router or any other process.

## Process ids

On-demand workflows: `code-review`, `git`, `refactoring`, `benchmarking`.

Also callable by id: `design-principles`, `rules-of-engagement`, `programmer-mindset`, `htdd-gate`.

`code-review` also prints design principles and the active stack review files. When the project has no types, the output says `stacks: none`. Do not open other stacks.

Follow the files the resolver prints.
