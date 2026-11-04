# Usage

Tikal attaches to a repository as a link. The link points at the inner `ai-coding-tools/` directory, so every path stays `ai-coding-tools/processes/...`. One script writes the project config and the agent entrypoints. It leaves skills and hooks unregistered.

Helper scripts are Python 3.11+ and depend on the standard library.

## Attach the toolkit

### Git submodule

```bash
git submodule add https://github.com/gerardoramirez/tikal.git vendor/tikal
ln -s vendor/tikal/ai-coding-tools ai-coding-tools
python3 ai-coding-tools/scripts/init_project.py --type astro
```

### Local symlink

Use a symlink while you edit Tikal itself. Replace `/path/to/cloned/tikal` with the checkout. The placeholder path creates a broken link.

```bash
ln -s /path/to/cloned/tikal/ai-coding-tools ai-coding-tools
python3 ai-coding-tools/scripts/init_project.py --type astro
```

Leave the local symlink out of the app’s commits.

## Initialize

```bash
python3 ai-coding-tools/scripts/init_project.py --type flutter
python3 ai-coding-tools/scripts/init_project.py --type astro
python3 ai-coding-tools/scripts/init_project.py --type typescript
```

`init_project.py` writes `tikal.yaml` at the app root, copies `tikal.project.md` from the template, and installs thin entrypoints for Claude, Cursor, Copilot, and Windsurf. Repeat `--type` to enable more than one stack. Existing files stay as they are.

`--type astro` writes `astro` only. Resolution expands that to TypeScript, then Astro, and the init step copies both Cursor glob rules. Fill in that app’s `tikal.project.md`.

`init_project.py` does not link skills and does not register hooks.

## Config

`tikal.yaml` lives at the consuming repository root.

```yaml
project:
  name: trail_app
  types:
    - astro
  # code_reviews: code-reviews   # optional, relative to this workspace
  # auto_commit_message: true    # optional; propose a message, do not commit
```

`project.types` is the allow-list. Known types are `flutter`, `typescript`, and `astro`. `code_reviews` is the relative directory for review write-ups. `auto_commit_message` asks for a proposed message after a turn that changed files. The flag is off when it is absent. See [Commits](commits.md).

This repository is the framework. Its `tikal.yaml` keeps `types` empty, so application stacks stay out of toolkit work.

When `tikal.yaml` is missing, Tikal infers a type from markers:

- `pubspec.yaml` with a top-level `flutter:` key → `flutter`
- `astro.config.mjs`, `.ts`, or `.js` → `astro`, which implies `typescript`
- `tsconfig.json` → `typescript`

Confirm the expanded list:

```bash
python3 ai-coding-tools/scripts/resolve_stack.py
```

## Where a fact belongs

Put an app’s commands, layout, and architecture in that app’s `tikal.project.md`. Put implementation plans in `plans/` at the app root. Edit `processes/rules-of-engagement.md` for collaboration, comments, and test naming. Edit `processes/programmer-mindset.md` for how the programmer thinks. Edit `processes/design-principles.md` for modules and interfaces.

Add a stack as `ai-coding-tools/stacks/<type>/` with an `index.md` and focused docs. Register it in `scripts/resolve_stack.py` and `scripts/init_project.py`, and list it in the app’s `tikal.yaml`. The stack directory notes are in [stacks/README.md](../ai-coding-tools/stacks/README.md).

App plans, overviews, and secrets stay out of `ai-coding-tools/`.

## Human Truth Driven Design

Tikal uses [Human Truth Driven Design](https://github.com/gerardoramirez/human-truth-driven-design) when a product already has the method. Tikal does not ship it. If `docs/htdd/AGENTS.md` exists, agents read it and `processes/htdd-gate.md` before implementation, then `docs/htdd/MILESTONES/CURRENT.md` when that milestones directory exists. Absent files stay unread.

## Path check

Before an agent commit, check the paths. The script refuses unsafe paths. It does not run `git add` or `git commit`.

```bash
python3 ai-coding-tools/scripts/commit_paths_ok.py --root . -- tikal.yaml tikal.project.md
```

## Tests

```bash
python3 -m unittest discover -s ai-coding-tools/tests -v
```

## Optional session hooks

Two scripts sit beside the work and stay quiet about git. `check_file_changes.py` reloads instructions when process files change, and only for stacks the project has active. `save_session_summary.py` writes a local summary under `ai-coding-tools/context/`.

For Claude Code, add this to `~/.claude/settings.json` or the project settings:

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
      }
    ]
  }
}
```

The commit-message command in [Commits](commits.md) can sit in that same `Stop` list. `init_project.py` writes neither file.
