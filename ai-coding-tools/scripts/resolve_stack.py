#!/usr/bin/env python3
"""Resolve which Tikal stacks are active for this repository.

Reads tikal.yaml / .tikal.yaml / tikal.json at the project root. If no
config exists, infers types from well-known project markers.

Used by agents (via processes/getting-started.md), init_project.py, and
check_file_changes.py so only the allowed stack docs enter context.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys

CONFIG_NAMES = ("tikal.yaml", ".tikal.yaml", "tikal.json")
PROJECT_OVERVIEW_NAME = "tikal.project.md"

# Detection only runs when no config file is present.
# `files` = all must exist. `any_files` = at least one must exist.
STACK_MARKERS = {
    "flutter": {
        "files": ("pubspec.yaml",),
        "file_contains": {"pubspec.yaml": r"(?m)^flutter\s*:"},
    },
    "typescript": {
        "any_files": ("tsconfig.json",),
    },
    "astro": {
        "any_files": ("astro.config.mjs", "astro.config.ts", "astro.config.js"),
    },
}

# Implied bases are inserted before the declaring type.
STACK_IMPLIES = {
    "astro": ("typescript",),
}

ALWAYS_TRACKED = (
    "CLAUDE.md",
    "tikal.yaml",
    ".tikal.yaml",
    "tikal.json",
    "tikal.project.md",
    "ai-coding-tools/processes/*.md",
)


def _looks_like_root(path: pathlib.Path) -> bool:
    return find_config(path) is not None or (path / "ai-coding-tools" / "processes").is_dir()


def project_root(explicit: pathlib.Path | None = None) -> pathlib.Path:
    if explicit is not None:
        return explicit.resolve()
    env = os.environ.get("CLAUDE_PROJECT_DIR") or os.environ.get("TIKAL_PROJECT_DIR")
    if env:
        return pathlib.Path(env).resolve()
    start = pathlib.Path.cwd().resolve()
    for candidate in (start, *start.parents):
        if _looks_like_root(candidate):
            return candidate
    return start


def find_config(root: pathlib.Path) -> pathlib.Path | None:
    for name in CONFIG_NAMES:
        path = root / name
        if path.is_file():
            return path
    return None


def _strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    for i, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:i].rstrip()
    return line.rstrip()


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _parse_inline_list(value: str) -> list[str]:
    inner = value.strip()
    if inner == "[]":
        return []
    if inner.startswith("[") and inner.endswith("]"):
        inner = inner[1:-1].strip()
        if not inner:
            return []
        return [_unquote(part) for part in inner.split(",") if _unquote(part)]
    return []


def parse_simple_project_yaml(text: str) -> dict:
    """Parse the small tikal.yaml schema without a YAML dependency."""
    name = ""
    types: list[str] | None = None
    in_project = False
    in_types = False
    project_indent = None
    types_indent = None

    for raw_line in text.splitlines():
        line = _strip_comment(raw_line)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if not in_project:
            if stripped == "project:" or stripped.startswith("project:"):
                in_project = True
                project_indent = indent
                rest = stripped[len("project:") :].strip()
                if rest and rest != ">":
                    pass
            continue

        if indent <= project_indent and stripped != "project:":
            in_project = False
            in_types = False
            continue

        if in_types:
            if stripped.startswith("- "):
                item = _unquote(stripped[2:])
                if item:
                    types.append(item)
                continue
            if indent <= (types_indent or indent):
                in_types = False
            else:
                continue

        if stripped.startswith("name:"):
            name = _unquote(stripped[len("name:") :])
            continue

        if stripped.startswith("types:"):
            rest = stripped[len("types:") :].strip()
            if rest:
                types = _parse_inline_list(rest)
            else:
                types = []
                in_types = True
                types_indent = indent
            continue

    return {"name": name, "types": types if types is not None else []}


def load_config(path: pathlib.Path) -> dict:
    text = path.read_text()
    if path.suffix == ".json":
        data = json.loads(text)
        project = data.get("project", data)
        types = project.get("types") or []
        if isinstance(types, str):
            types = [types]
        return {"name": project.get("name", "") or "", "types": list(types)}
    return parse_simple_project_yaml(text)


def expand_types(types: list[str]) -> list[str]:
    """Insert implied base stacks before each declaring type, without duplicates."""
    expanded: list[str] = []
    for stack in types:
        for implied in STACK_IMPLIES.get(stack, ()):
            if implied not in expanded:
                expanded.append(implied)
        if stack not in expanded:
            expanded.append(stack)
    return expanded


def _marker_matches(root: pathlib.Path, rules: dict) -> bool:
    required = rules.get("files")
    if required and not all((root / filename).is_file() for filename in required):
        return False
    any_files = rules.get("any_files")
    if any_files and not any((root / filename).is_file() for filename in any_files):
        return False
    if not required and not any_files:
        return False
    for filename, pattern in rules.get("file_contains", {}).items():
        path = root / filename
        if not path.is_file() or not re.search(pattern, path.read_text()):
            return False
    return True


def detect_types(root: pathlib.Path) -> list[str]:
    found = []
    for stack, rules in STACK_MARKERS.items():
        if _marker_matches(root, rules):
            found.append(stack)
    return expand_types(found)


def existing_stack_dirs(root: pathlib.Path, types: list[str]) -> tuple[list[str], list[str]]:
    present = []
    missing = []
    for stack in types:
        stack_dir = root / "ai-coding-tools" / "stacks" / stack
        if stack_dir.is_dir():
            present.append(str(pathlib.Path("ai-coding-tools") / "stacks" / stack))
        else:
            missing.append(stack)
    return present, missing


def resolve(root: pathlib.Path | None = None) -> dict:
    root = project_root(root)
    config_path = find_config(root)
    if config_path is not None:
        parsed = load_config(config_path)
        types = expand_types(
            [item.strip() for item in parsed["types"] if str(item).strip()]
        )
        source = "config"
        name = parsed.get("name", "")
    else:
        types = detect_types(root)
        source = "detect" if types else "none"
        name = ""
        config_path = None

    overview = root / PROJECT_OVERVIEW_NAME
    stack_dirs, missing = existing_stack_dirs(root, types)

    return {
        "root": str(root),
        "name": name,
        "types": types,
        "source": source,
        "config_path": str(config_path.relative_to(root)) if config_path else None,
        "project_overview": PROJECT_OVERVIEW_NAME if overview.is_file() else None,
        "stack_dirs": stack_dirs,
        "missing_stacks": missing,
    }


def tracked_patterns(root: pathlib.Path | None = None) -> list[str]:
    """Glob patterns check_file_changes.py should watch."""
    result = resolve(root)
    patterns = list(ALWAYS_TRACKED)
    for stack in result["types"]:
        patterns.append(f"ai-coding-tools/stacks/{stack}/**/*.md")
    return patterns


def format_human(result: dict) -> str:
    lines = [
        f"project: {result['name'] or '(unnamed)'}",
        f"types: {', '.join(result['types']) or '(none)'}",
        f"source: {result['source']}",
    ]
    if result["config_path"]:
        lines.append(f"config: {result['config_path']}")
    if result["project_overview"]:
        lines.append(f"overview: {result['project_overview']}")
    if result["stack_dirs"]:
        lines.append("load:")
        for path in result["stack_dirs"]:
            lines.append(f"  - {path}/")
    if result["missing_stacks"]:
        lines.append("missing stacks (no directory): " + ", ".join(result["missing_stacks"]))
    if result["source"] == "none":
        lines.append(
            "No tikal.yaml and no known project markers. Create tikal.yaml "
            "with project.types (e.g. flutter) so agents load the right stack."
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve active Tikal stacks")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--root", type=pathlib.Path, default=None, help="Project root")
    args = parser.parse_args(argv)

    result = resolve(args.root)
    if args.json:
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(format_human(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
