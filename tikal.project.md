# Tikal

Reusable instructions, workflows, and hooks for AI coding agents.

- **Project Name:** Tikal
- **Description:** Structural alignment, guardrails, and telemetry for AI coding assistants.
- **Target Runtime/Language:** Markdown instructions plus Python 3.11+ helper scripts.

## Build System and Development Commands

```bash
python3 -m unittest discover -s ai-coding-tools/tests -v
python3 ai-coding-tools/scripts/resolve_stack.py
python3 ai-coding-tools/scripts/init_project.py --type flutter --root /path/to/app
python3 ai-coding-tools/scripts/commit_paths_ok.py --root . -- path1 path2
python3 ai-coding-tools/scripts/propose_commit_message.py
```

## Repository Structure

- **ai-coding-tools/processes/** — stack-agnostic router, always-on design principles, and optional workflows
- **ai-coding-tools/stacks/** — per-type packs (loaded only when `tikal.yaml` lists them)
- **ai-coding-tools/scripts/** — resolve, init, hooks, telemetry. `propose_commit_message.py` is a stop hook: with `auto_commit_message` on, it asks for one commit message and does not commit. It runs only after `.cursor/hooks.json`, a Claude `Stop` entry, or `.codex/hooks.json` registers it. `init_project.py` does not add that registration. See the README how-to.
- **ai-coding-tools/templates/** — entrypoints copied into consuming repos
- **tikal.yaml** — stack allow-list for *this* checkout. `project.code_reviews` is the relative directory for review write-ups (`code-reviews` here). `auto_commit_message` stays off.
- **tikal.project.md** — this file
- **plans/** — implementation plans for this repo (not inside `ai-coding-tools/`)

## Development Guidelines

- Keep `processes/getting-started.md` a thin router. Stack knowledge goes in `stacks/<type>/`.
- Project-specific facts for a consuming app belong in that app's `tikal.yaml` and `tikal.project.md`, not in the submodule.
- If a consuming repo has `docs/htdd/AGENTS.md`, agents read it and `processes/htdd-gate.md` before implementation, then `docs/htdd/MILESTONES/CURRENT.md` when `MILESTONES/` exists. HTDD comes from https://github.com/gerardoramirez/human-truth-driven-design. Tikal does not ship the method. Skip the file when it is absent.
