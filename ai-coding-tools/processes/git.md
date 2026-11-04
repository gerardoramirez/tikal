# Git commits

Open this file when the user asked to commit (or to review what would be committed). Also open this path at the end of a task that changed files when `project.auto_commit_message` is true. This file lives on the `ai-coding-tools` link. Open the path even when a search of the app repo does not list it. The flag alone does not print a message. If the reply has no `## Proposed commit message` and the worktree is still dirty, the stop hook in `docs/commits.md` sends one follow-up, and only when that hook is installed.

Do not commit unless the user asked. This file is judgment, not a runner. Do not add a script that stages or commits for you.

## When auto_commit_message is on

If this turn changed files, end the reply with one line the user can copy and run: `git commit -m "..."`. Run `git status`, `git diff`, and `git log` (recent messages) from the repo root. The text inside the quotes is why the change exists, not a file list.

Print the heading below as a real heading, then one fenced line. Keep the message one line, with no double quotes inside it, so it pastes cleanly. Do not run the command. Do not stage, commit, push, or amend. If you did not change files this turn, say so and do not invent a message.

## Proposed commit message

```
git commit -m "Why this change exists."
```

The heading line must be exactly `## Proposed commit message`. A stop hook looks for it and stays quiet once it is there.

## Before you stage

1. Run `git status`, `git diff`, and `git log` (recent messages) from the repo root.
2. Decide explicit paths. Never `git add -A` or `git add .`.
3. Include `plans/` when this change has a plan.
4. Check paths:

```bash
python3 ai-coding-tools/scripts/commit_paths_ok.py --root . -- path1 path2
```

If that exits non-zero, fix the list. Do not commit.

## Do not stage

- `ai-coding-tools` when it is a symlink (local Tikal link, not app source)
- `.env` and `.env.*` except `.env.example`, `.env.sample`, `.env.template`
- `credentials.json`, `secrets.json`, `service-account.json`

## Commit

- HEREDOC message when you are the one committing. When `auto_commit_message` is on, the chat proposal is the single `git commit -m "..."` line above, for the user to copy. Focus on why, not a file list.
- Do not push, amend, `--no-verify`, or change git config unless the user asked.
- After the commit, run `git status` and confirm the intended files landed.
