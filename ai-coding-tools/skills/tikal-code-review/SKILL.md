---
name: tikal-code-review
description: Review a pull request or a diff with the Tikal code-review process. Use when the task is a review. Leave this skill unused for ordinary edits.
---

# Tikal code review

Process id: `code-review`

Open this process only when the task is a review of a pull request or a diff. Leave it closed for ordinary edits.

## Find the resolver

Locate `resolve_process.py` in this order:

1. If `TIKAL_HOME` is set, use `$TIKAL_HOME/ai-coding-tools/scripts/resolve_process.py` when that clone root exists, or `$TIKAL_HOME/scripts/resolve_process.py` when `TIKAL_HOME` is the `ai-coding-tools` directory.
2. Otherwise walk up from the workspace for `ai-coding-tools/scripts/resolve_process.py`.
3. Otherwise use `~/.tikal/ai-coding-tools/scripts/resolve_process.py`. `~/.tikal` is the clone root or a symlink to it.

Run that script with `python3` and the process id. Read only the paths it prints. Do not load the router or any other process.
