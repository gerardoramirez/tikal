# Tikal

> **Tikal** provides structural alignment, guardrails, and telemetry for AI coding agents.

It is a reusable framework for the instructions, workflows, and scripts you use with AI coding assistants (Claude Code, Cursor, Copilot, Windsurf, and others).

Agents load a **thin router**, then only the stack docs that match this repo. A Flutter app does not pull Python guidance; this framework repo does not pull Flutter guidance.

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

`tikal.yaml` at the **consuming repo root** is the allow-list. It stays outside the toolkit so a submodule checkout stays clean.

```yaml
project:
  name: trail_app
  types:
    - astro
```

`astro` always expands to `typescript` then `astro`. `typescript` alone does not load Astro. If the file is missing, Tikal infers types from markers (`pubspec.yaml` + `flutter:`, `astro.config.*`, `tsconfig.json`). Confirm with:

```bash
python3 ai-coding-tools/scripts/resolve_stack.py
```

---

## Repository Structure

- **`tikal.yaml`** — Stack allow-list for this checkout.
- **`tikal.project.md`** — Per-repo overview (build commands, layout, architecture).
- **`plans/`** — Implementation plans for *this* repo. Never inside the toolkit.
- **`CLAUDE.md`** / **`.cursor/rules/tikal.mdc`** / **`.github/copilot-instructions.md`** / **`.windsurfrules`** — Thin entrypoints that point at the router.
- **`ai-coding-tools/`**
  - **`processes/getting-started.md`** — Context router (always-on, small).
  - **`processes/project-overview.template.md`** — Copied to `tikal.project.md` on init.
  - **`processes/rules-of-engagement.md`** — Communication, complexity, and test standards.
  - **`processes/refactoring.md`** / **`benchmarking.md`** — Optional workflows.
  - **`stacks/flutter/`** — Flutter commands, review, and architecture. Loaded only when `flutter` is listed.
  - **`stacks/typescript/`** — Shared TypeScript base. Loaded when listed, or when implied by `astro`.
  - **`stacks/astro/`** — Astro content-site commands, review, and architecture. Implies TypeScript.
  - **`scripts/resolve_stack.py`** — Resolves active stacks from config or markers.
  - **`scripts/init_project.py`** — Writes config and agent entrypoints into a consuming repo.
  - **`scripts/check_file_changes.py`** — Reloads changed process files; watches only active stacks.
  - **`scripts/save_session_summary.py`** / **`track_queries.py`** — Session summary and usage telemetry.
  - **`templates/cursor/`** — Optional glob rules (e.g. attach Flutter review when `*.dart` is in play).
  - **`context/`** — Session summaries from hooks (local to this toolkit checkout).

---

## Getting Started

Link or submodule the **inner** `ai-coding-tools/` directory (not the whole Tikal repo root) so paths stay `ai-coding-tools/processes/...`.

### Method A: Git Submodule
```bash
git submodule add https://github.com/your-username/tikal.git vendor/tikal
ln -s vendor/tikal/ai-coding-tools ai-coding-tools
python3 ai-coding-tools/scripts/init_project.py --type astro
```

### Method B: Local Symlink
```bash
ln -s /path/to/cloned/tikal/ai-coding-tools ai-coding-tools
python3 ai-coding-tools/scripts/init_project.py --type astro
```

`init_project.py` writes `tikal.yaml`, copies `tikal.project.md`, and installs Claude / Cursor / Copilot / Windsurf entrypoints. `--type astro` writes `astro` only and copies both Astro and TypeScript Cursor glob rules. Fill in `tikal.project.md` for that app.

Known `--type` values: `flutter`, `typescript`, `astro`. This Tikal repo keeps `types` empty so application stacks stay out of framework work.

---

## Tests

```bash
python3 -m unittest discover -s ai-coding-tools/tests -v
```

---

## Configuring Hooks (Claude Code)

To enable instruction auto-reload and session summaries, add hooks in `~/.claude/settings.json` or the project settings:

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

---

## Customizing

* Edit `ai-coding-tools/processes/rules-of-engagement.md` for start tokens, comments, and test naming.
* Put this app's commands and layout in `tikal.project.md`, not in the router.
* Put implementation plans in `plans/` at the repo root, not in `ai-coding-tools/`.
* Add a new stack as `ai-coding-tools/stacks/<type>/` and list it in `tikal.yaml`.

## License
This project is licensed under the Apache License 2.0. See the `LICENSE` file for details.
