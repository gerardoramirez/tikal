---
name: tikal-refactor
description: Refactor production code with the Tikal TDD refactoring process. Use when the user is refactoring production code. Do not change tests.
---

# Tikal refactor

Process id: `refactoring`

This process is for refactoring production code. Do not change test code.

## Find the resolver

Locate `resolve_process.py` in this order:

1. If `TIKAL_HOME` is set, use `$TIKAL_HOME/ai-coding-tools/scripts/resolve_process.py` when that clone root exists, or `$TIKAL_HOME/scripts/resolve_process.py` when `TIKAL_HOME` is the `ai-coding-tools` directory.
2. Otherwise walk up from the workspace for `ai-coding-tools/scripts/resolve_process.py`.
3. Otherwise use `~/.tikal/ai-coding-tools/scripts/resolve_process.py`. `~/.tikal` is the clone root or a symlink to it.

Run that script with `python3` and the process id. Read only the paths it prints. Do not load the router or any other process.
