# Tikal 🛕

> **Tikal** provides structural alignment, guardrails, and telemetry for AI coding agents.

It is a reusable framework and template repository to manage the instructions, workflows, guidelines, and automation scripts you use with AI coding assistants (like Claude Code, Cursor, Aider, and others).

---

## 📂 Repository Structure

- **`CLAUDE.md`** - Entrypoint for **Claude Code** (Anthropic) — redirects to `ai-coding-tools/processes/getting-started.md`.
- **`.cursor/rules/tikal.mdc`** - Entrypoint for **Cursor** — points to the same instructions using Cursor's MDC rule format.
- **`.github/copilot-instructions.md`** - Entrypoint for **GitHub Copilot** — points to the shared instructions.
- **`.windsurfrules`** - Entrypoint for **Windsurf** (Codeium) — points to the shared instructions.
- **`ai-coding-tools/`**
  - **`processes/`**
    - **`getting-started.md`** - Codebase-specific details (build commands, linting, architecture, directory layouts). Customize this for each project.
    - **`rules-of-engagement.md`** - Guidelines on communication styles, Cyclomatic complexity limits, test standards, and test name formatting.
    - **`refactoring.md`** - Standard Test-Driven Development (TDD) rules of refactoring.
    - **`benchmarking.md`** - Standard workflow for performing speed optimization safely.
  - **`scripts/`**
    - **`check_file_changes.py`** - An automated hook that watches for edits in process files and reloads them for the AI model.
    - **`save_session_summary.py`** - A stop-hook script that parses conversation logs and exports markdown summaries to `context/`.
    - **`track_queries.py`** - A metric logger that processes historical queries, calculates tokens, and estimates usage costs.
  - **`plans/`** - A directory to host implementation design plans.
  - **`context/`** - A directory to host session summaries, diagrams, and logs.

---

## 🚀 Getting Started

To use Tikal in one of your projects, you can either add it as a Git submodule or symlink it locally.

### Method A: Git Submodule (Recommended)
Add Tikal directly into your active repository as a submodule:
```bash
git submodule add https://github.com/your-username/tikal.git ai-coding-tools
```
Then copy and link the `CLAUDE.md` entrypoint:
```bash
# Create the entrypoint pointing to the instructions
echo -e "# CLAUDE.md\n\nRefer to @ai-coding-tools/processes/getting-started.md for build commands, repository structure, and instructions." > CLAUDE.md
```

### Method B: Local Symlinking (Fast Local Iteration)
Clone Tikal once on your local machine, then symlink it inside any of your active project repositories:
```bash
# Inside your active project:
ln -s /path/to/cloned/tikal/ai-coding-tools ai-coding-tools
ln -s /path/to/cloned/tikal/CLAUDE.md CLAUDE.md
```

---

## 🛠️ Configuring Hooks (Claude Code)

To enable automatic telemetry logging, session summaries, and instruction auto-reloading, configure the hooks in your user settings (`~/.claude/settings.json`) or local project settings:

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

## 📝 Customizing Rules of Engagement

The core processes are written in Markdown. You can easily adjust the files under `ai-coding-tools/processes/` to match your specific coding style preferences:
* Edit `rules-of-engagement.md` to specify your preferred start tokens, testing naming conventions, and comment guidelines.
* Fill out the project overview in `processes/getting-started.md` to map out the structure of your active project.

## 📄 License
This project is licensed under the Apache License 2.0. See the `LICENSE` file for details.
