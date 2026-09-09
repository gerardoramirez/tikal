# Git commits

Open this file only when the user asked to commit (or to review what would be committed). Do not commit on your own.

This file is judgment, not a runner. Do not add a script that stages or commits for you.

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

- HEREDOC message. Focus on why, not a file list.
- Do not push, amend, `--no-verify`, or change git config unless the user asked.
- After the commit, run `git status` and confirm the intended files landed.
