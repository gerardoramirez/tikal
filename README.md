# Tikal

Tikal is a reusable instruction kit for AI coding agents (Claude Code, Cursor, Copilot, Windsurf, and others).

Agents read a **thin router**, then only the stack docs that match the consuming repository. A Flutter app does not load Astro guidance. This repository is the framework itself; its `tikal.yaml` keeps `types` empty so application stacks stay out of toolkit work.

It is not an application, a CLI product, or a language runtime. Helper scripts are Python 3.11+ and have no third-party package requirements.

---

## How context is selected

```
tikal.yaml          →  project.types: [astro]
        │
        ▼
processes/getting-started.md   (always-on router)
        │
        ├── tikal.project.md                   (this app's overview)
        ├── processes/rules-of-engagement.md   (always)
        ├── processes/design-principles.md     (always)
        ├── stacks/typescript/                 (implied by astro)
        ├── stacks/astro/                      (only if listed)
        ├── docs/htdd/AGENTS.md                (only if that file exists)
        ├── docs/htdd/MILESTONES/CURRENT.md    (only the folder it names)
        └── processes/htdd-gate.md             (only if AGENTS.md exists)
```

`tikal.yaml` lives at the **consuming repo root**, not inside the toolkit. That keeps a submodule or symlink checkout clean.

```yaml
project:
  name: trail_app
  types:
    - astro
  # code_reviews: code-reviews   # optional, relative to this workspace
  # auto_commit_message: true    # optional; propose a message, do not commit
```

Known types: `flutter`, `typescript`, `astro`. `astro` always expands to `typescript` then `astro`. `typescript` alone does not load Astro.

If `tikal.yaml` is missing, Tikal infers types from markers (`pubspec.yaml` + a top-level `flutter:` key, `astro.config.*`, `tsconfig.json`). Confirm with:

```bash
python3 ai-coding-tools/scripts/resolve_stack.py
```

Optional process files load only when that work is happening: refactoring, benchmarking, [git commits](ai-coding-tools/processes/git.md), and [code review](ai-coding-tools/processes/code-review.md). Design principles load with the router on every session.

Tikal uses [Human Truth Driven Design](https://github.com/gerardoramirez/human-truth-driven-design) for HTDD. Agents follow the product's `docs/htdd/AGENTS.md` and `docs/htdd/MILESTONES/CURRENT.md` only when those files exist, and load `processes/htdd-gate.md` before implementation when `AGENTS.md` exists. Tikal does not ship the method.

## How to get a proposed commit message

`auto_commit_message: true` only asks for a proposal. It does not stage or commit. `resolve_stack.py` reading the flag does not print a message in chat.

Two things produce the message. The flag alone is neither of them.

1. At the end of a turn that changed files, the agent opens `ai-coding-tools/processes/git.md` and prints one line under `## Proposed commit message` that you can copy: `git commit -m "why this change exists"`. That file lives on the `ai-coding-tools` link (submodule or symlink). Open that path. A search of the app repo that does not follow the link will miss the file, and the turn will end with no proposal.
2. The backup is a stop hook. If the reply has no `## Proposed commit message` and the worktree is still dirty, `propose_commit_message.py` sends one follow-up. `init_project.py` does not install this hook. A new app does not register it: no `.cursor/hooks.json`, no Claude `Stop` entry, and no `.codex/hooks.json`. With the hook absent, a turn that skips the heading ends with no message.

The same script serves Cursor, Claude Code, and Codex. It stays quiet when the flag is off, when the worktree is clean, or when the reply already has the heading. If the change is already committed, adding the hook afterward does not propose a message for that commit. It runs on the next turn that leaves the tree dirty.

### Cursor

Add `.cursor/hooks.json` at the consuming repo root. Cursor runs that file from the repo root.

```json
{
  "version": 1,
  "hooks": {
    "stop": [
      {
        "command": "python3 ai-coding-tools/scripts/propose_commit_message.py",
        "loop_limit": 1
      }
    ]
  }
}
```

Cursor reads `followup_message` and submits it once.

### Claude Code

Add the command to `Stop` in `.claude/settings.json` at the repo root, or in `~/.claude/settings.json` for every repo. `init_project.py` does not write either file. If `Stop` already lists other commands, add this one beside them. The session-summary command in [Optional hooks](#optional-hooks) can stay in the same list.

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "python3 ai-coding-tools/scripts/propose_commit_message.py"
      }
    ]
  }
}
```

Claude Code reads `{"decision": "block", "reason": "..."}` and continues once.

### Codex

Hooks run unless `~/.codex/config.toml` sets `[features] hooks = false`. Add `.codex/hooks.json` at the repo root. Project hooks load only when that project is trusted. After you add the file, run `/hooks` and trust the new command. Codex skips it until that review is saved. A user-wide copy can live in `~/.codex/hooks.json` instead.

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$(git rev-parse --show-toplevel)/ai-coding-tools/scripts/propose_commit_message.py\"",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

The `git rev-parse` form keeps the script path stable when Codex starts in a subdirectory. Codex uses the same `decision` / `reason` output as Claude Code.

Copilot and Windsurf have no stop hook here. They only get the message when the agent opens `git.md`.

---

## Add Tikal to an app

Link or submodule the **inner** `ai-coding-tools/` directory (not this repo root) so paths stay `ai-coding-tools/processes/...`.

### Method A: Git submodule

```bash
git submodule add https://github.com/gerardoramirez/tikal.git vendor/tikal
ln -s vendor/tikal/ai-coding-tools ai-coding-tools
python3 ai-coding-tools/scripts/init_project.py --type astro
```

### Method B: Local symlink (good while you edit Tikal)

Replace `/path/to/cloned/tikal` with the real path where you cloned this repo; running this command verbatim creates a broken symlink.


```bash
ln -s /path/to/cloned/tikal/ai-coding-tools ai-coding-tools
python3 ai-coding-tools/scripts/init_project.py --type astro
```

`init_project.py` writes `tikal.yaml`, copies `tikal.project.md` from the template, and installs thin Claude / Cursor / Copilot / Windsurf entrypoints. `--type astro` writes `astro` only and copies both Astro and TypeScript Cursor glob rules. Fill in that app's `tikal.project.md`.

Repeat `--type` to enable more than one stack. Existing files are not overwritten.

Do **not** commit a local `ai-coding-tools` symlink. Do **not** write app plans, overviews, or secrets into `ai-coding-tools/`. Before an agent commit, check paths:

```bash
python3 ai-coding-tools/scripts/commit_paths_ok.py --root . -- tikal.yaml tikal.project.md
```

That script only refuses unsafe paths. It does not `git add` or `git commit`.

---

## This repository

| File | Role |
|---|---|
| `tikal.yaml` | Allow-list for *this* checkout (`types: []`) |
| `tikal.project.md` | Toolkit overview (commands, layout) |
| `plans/` | Implementation plans for Tikal. Never inside the toolkit. |
| `CLAUDE.md`, `.cursor/rules/tikal.mdc`, `.github/copilot-instructions.md`, `.windsurfrules` | Thin entrypoints that point at the router |

### `ai-coding-tools/`

| Path | Role |
|---|---|
| `processes/getting-started.md` | Context router (always-on, small) |
| `processes/project-overview.template.md` | Copied to a consuming repo as `tikal.project.md` |
| `processes/rules-of-engagement.md` | Communication, complexity, and test standards |
| `processes/design-principles.md` | Always-on philosophy for modules, interfaces, and change |
| `processes/refactoring.md`, `benchmarking.md`, `git.md`, `code-review.md` | Optional workflows |
| `processes/htdd-gate.md` | Before implementation, only when the product has `docs/htdd/AGENTS.md` |
| `stacks/flutter/` | Loaded only when `flutter` is listed |
| `stacks/typescript/` | Loaded when listed, or when implied by `astro` |
| `stacks/astro/` | Implies TypeScript |
| `scripts/resolve_stack.py` | Resolves active stacks from config or markers |
| `scripts/init_project.py` | Writes config and agent entrypoints into an app |
| `scripts/commit_paths_ok.py` | Guards commit paths (symlink toolkit, secrets) |
| `scripts/propose_commit_message.py` | Stop hook: asks for one commit message when the flag is on. Does not stage or commit |
| `scripts/check_file_changes.py` | Reloads changed process files; watches only active stacks |
| `scripts/save_session_summary.py`, `track_queries.py` | Local session summary and usage telemetry |
| `templates/cursor/` | Optional glob rules (e.g. Flutter review when `*.dart` is in play) |
| `context/` | Local hook output for this checkout |

---

## Tests

```bash
python3 -m unittest discover -s ai-coding-tools/tests -v
```

---

## Optional hooks

To reload instructions when process files change, and to write a local session summary:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": "python3 ai-coding-tools/scripts/check_file_changes.py"
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "python3 ai-coding-tools/scripts/save_session_summary.py"
      },
      {
        "type": "command",
        "command": "python3 ai-coding-tools/scripts/propose_commit_message.py"
      }
    ]
  }
}
```

Put that in `~/.claude/settings.json` or the project settings. Summaries stay on disk under `ai-coding-tools/context/`.

`propose_commit_message.py` on `Stop` is the Claude Code backup in [How to get a proposed commit message](#how-to-get-a-proposed-commit-message). It is safe while `auto_commit_message` is off: it prints `{}` and exits. `init_project.py` does not add this registration. Claude Code reads `decision` / `reason`. Cursor reads `followup_message` from `.cursor/hooks.json`. Codex reads the same `decision` / `reason` pair from `.codex/hooks.json`. Each host continues once, then the hook stays quiet.

---

## Customizing

* Put an app's commands, layout, and architecture in that app's `tikal.project.md`, not in the router.
* Put implementation plans in `plans/` at the **app** repo root.
* Edit `ai-coding-tools/processes/rules-of-engagement.md` for start tokens, comments, and test naming.
* Edit `ai-coding-tools/processes/design-principles.md` for how agents should shape modules and APIs.
* Add a stack as `ai-coding-tools/stacks/<type>/` (`index.md` plus focused docs), register it in `scripts/resolve_stack.py` and `scripts/init_project.py`, and list it in the app's `tikal.yaml`. See [stacks/README.md](ai-coding-tools/stacks/README.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).
