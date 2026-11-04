---
name: tikal-git
description: Apply the Tikal git process when the user asked to commit or to review what would be committed, or when proposing one commit message after a change. Does not stage or commit.
---

# Tikal git

Process id: `git`

Open this process when the user asked to commit, or to review what would be committed. Also open it at the end of a task that changed files when `project.auto_commit_message` is true. Do not commit unless the user asked.

## Find the resolver

Locate `resolve_process.py` in this order:

1. If `TIKAL_HOME` is set, use `$TIKAL_HOME/ai-coding-tools/scripts/resolve_process.py` when that clone root exists, or `$TIKAL_HOME/scripts/resolve_process.py` when `TIKAL_HOME` is the `ai-coding-tools` directory.
2. Otherwise walk up from the workspace for `ai-coding-tools/scripts/resolve_process.py`.
3. Otherwise use `~/.tikal/ai-coding-tools/scripts/resolve_process.py`. `~/.tikal` is the clone root or a symlink to it.

Run that script with `python3` and the process id. Read only the paths it prints. Do not load the router or any other process.
