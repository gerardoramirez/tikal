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
        ├── tikal.project.md                 (this app's overview)
        ├── processes/rules-of-engagement.md (always)
        ├── stacks/typescript/               (implied by astro)
        └── stacks/astro/                    (only if listed)
```

`tikal.yaml` lives at the **consuming repo root**, not inside the toolkit. That keeps a submodule or symlink checkout clean.

```yaml
project:
  name: trail_app
  types:
    - astro
```

Known types: `flutter`, `typescript`, `astro`. `astro` always expands to `typescript` then `astro`. `typescript` alone does not load Astro.

If `tikal.yaml` is missing, Tikal infers types from markers (`pubspec.yaml` + a top-level `flutter:` key, `astro.config.*`, `tsconfig.json`). Confirm with:

```bash
python3 ai-coding-tools/scripts/resolve_stack.py
```

Optional process files load only when that work is happening: refactoring, benchmarking, [git commits](ai-coding-tools/processes/git.md), and design principles.

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
| `processes/refactoring.md`, `benchmarking.md`, `git.md` | Optional workflows |
| `stacks/flutter/` | Loaded only when `flutter` is listed |
| `stacks/typescript/` | Loaded when listed, or when implied by `astro` |
| `stacks/astro/` | Implies TypeScript |
| `scripts/resolve_stack.py` | Resolves active stacks from config or markers |
| `scripts/init_project.py` | Writes config and agent entrypoints into an app |
| `scripts/commit_paths_ok.py` | Guards commit paths (symlink toolkit, secrets) |
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

## Optional Claude Code hooks

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
      }
    ]
  }
}
```

Put that in `~/.claude/settings.json` or the project settings. Summaries stay on disk under `ai-coding-tools/context/`.

---

## Customizing

* Put an app's commands, layout, and architecture in that app's `tikal.project.md`, not in the router.
* Put implementation plans in `plans/` at the **app** repo root.
* Edit `ai-coding-tools/processes/rules-of-engagement.md` for start tokens, comments, and test naming.
* Add a stack as `ai-coding-tools/stacks/<type>/` (`index.md` plus focused docs), register it in `scripts/resolve_stack.py` and `scripts/init_project.py`, and list it in the app's `tikal.yaml`. See [stacks/README.md](ai-coding-tools/stacks/README.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).
