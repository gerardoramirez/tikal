"""Check tracked files for changes and output updated contents.

Used as a UserPromptSubmit hook so Claude automatically receives
updated instruction/process file content when files are edited.
"""

import hashlib
import json
import os
import pathlib

from resolve_stack import project_root, tracked_patterns

STATE_FILE = ".ai-data/.file_checksums"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    env_root = os.environ.get("CLAUDE_PROJECT_DIR")
    root = project_root(pathlib.Path(env_root) if env_root else None)
    TRACKED_PATTERNS = tracked_patterns(root)
    state_path = root / STATE_FILE

    # Load previous checksums
    prev = {}
    if state_path.exists():
        try:
            prev = json.loads(state_path.read_text())
        except (json.JSONDecodeError, OSError):
            prev = {}

    # Gather current files
    current_files = {}
    for pattern in TRACKED_PATTERNS:
        for path in root.glob(pattern):
            if path.is_file():
                rel = str(path.relative_to(root))
                current_files[rel] = path

    # Compute hashes and detect changes
    new_checksums = {}
    changed = []
    for rel, path in sorted(current_files.items()):
        h = sha256(path)
        new_checksums[rel] = h
        if prev.get(rel) != h:
            changed.append((rel, path))

    # Save updated checksums
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(new_checksums, indent=2) + "\n")

    # Output changed file contents
    if changed:
        print("[Auto-reload] The following files have changed since last read:\n")
        for rel, path in changed:
            print(f"--- {rel} ---")
            print(path.read_text())
            print()


if __name__ == "__main__":
    main()
