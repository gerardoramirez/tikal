# Flutter Stack

Load these files when `tikal.yaml` lists `flutter` (or Flutter was detected
from `pubspec.yaml`). Skip this directory on every other project type.

Read in this order:

1. `tikal.project.md` at the repo root — this app's commands and layout
2. `commands.md` — analyze, test, format, run
3. `review.md` — review and analysis checklist
4. `architecture.md` — structure, state, and tests

If a Dart MCP / Flutter tooling server is available in the session, use it
for `analyze_files`, widget inspection, and test runs instead of guessing
from source alone.
