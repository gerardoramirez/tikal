#!/usr/bin/env python3
"""Bootstrap Tikal in a consuming repository.

Writes tikal.yaml, copies the project-overview template, and installs
agent entrypoints so only the requested stack docs are loaded.
"""

from __future__ import annotations

import argparse
import pathlib
import shutil
import sys

from resolve_stack import expand_types

KNOWN_STACKS = ("flutter", "typescript", "astro")

TEMPLATE_DIR = pathlib.Path(__file__).resolve().parent.parent / "templates"
PROCESSES_DIR = pathlib.Path(__file__).resolve().parent.parent / "processes"


def write_if_missing(path: pathlib.Path, contents: str) -> str:
    if path.exists():
        return f"skip  {path} (already exists)"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents)
    return f"write {path}"


def copy_if_missing(src: pathlib.Path, dest: pathlib.Path) -> str:
    if dest.exists():
        return f"skip  {dest} (already exists)"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    return f"copy  {src.name} -> {dest}"


def tikal_yaml(name: str, types: list[str]) -> str:
    type_lines = "\n".join(f"    - {item}" for item in types) or "    []"
    return (
        "# Tikal stack allow-list. Agents load only these stacks.\n"
        "# Add another type later (e.g. python) without copying Flutter docs.\n"
        "project:\n"
        f"  name: {name}\n"
        "  types:\n"
        f"{type_lines}\n"
    )


def claude_md() -> str:
    return (
        "# CLAUDE.md\n\n"
        "Read `tikal.yaml` at the repository root, then follow "
        "@ai-coding-tools/processes/getting-started.md. "
        "Load only the stack directories listed in `project.types` "
        "and that type's implied bases (`astro` always loads `typescript`).\n"
    )


def copilot_md() -> str:
    return (
        "# GitHub Copilot Instructions\n\n"
        "Read `tikal.yaml` at the repository root, then follow "
        "@ai-coding-tools/processes/getting-started.md. "
        "Load only the stack directories listed in `project.types` "
        "and that type's implied bases (`astro` always loads `typescript`).\n"
    )


def windsurf_rules() -> str:
    return (
        "# Windsurf Rules\n\n"
        "Read `tikal.yaml` at the repository root, then follow "
        "@ai-coding-tools/processes/getting-started.md. "
        "Load only the stack directories listed in `project.types` "
        "and that type's implied bases (`astro` always loads `typescript`).\n"
    )


def cursor_router_mdc() -> str:
    return (
        "---\n"
        "description: Tikal router — load only the stacks listed in tikal.yaml\n"
        "alwaysApply: true\n"
        "---\n\n"
        "Read `tikal.yaml` (or `.tikal.yaml`) at the repository root, then "
        "follow @ai-coding-tools/processes/getting-started.md. "
        "Load only `ai-coding-tools/stacks/<type>/` for each entry in "
        "`project.types` and that type's implied bases (`astro` always "
        "loads `typescript`). Do not load other stacks.\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Initialize Tikal for a project")
    parser.add_argument(
        "--type",
        dest="types",
        action="append",
        required=True,
        help="Project type to enable (repeatable). Known: " + ", ".join(KNOWN_STACKS),
    )
    parser.add_argument("--name", default=None, help="Project name (defaults to directory name)")
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    args = parser.parse_args(argv)

    root = args.root.resolve()
    types = [item.strip() for item in args.types if item.strip()]
    unknown = [item for item in types if item not in KNOWN_STACKS]
    if unknown:
        sys.stderr.write(
            f"Unknown project type(s): {', '.join(unknown)}. "
            f"Known stacks: {', '.join(KNOWN_STACKS)}.\n"
        )
        return 2

    name = args.name or root.name
    actions = []

    actions.append(write_if_missing(root / "tikal.yaml", tikal_yaml(name, types)))

    overview_src = PROCESSES_DIR / "project-overview.template.md"
    if overview_src.is_file():
        actions.append(copy_if_missing(overview_src, root / "tikal.project.md"))

    actions.append(write_if_missing(root / "CLAUDE.md", claude_md()))
    actions.append(write_if_missing(root / ".github" / "copilot-instructions.md", copilot_md()))
    actions.append(write_if_missing(root / ".windsurfrules", windsurf_rules()))
    actions.append(write_if_missing(root / ".cursor" / "rules" / "tikal.mdc", cursor_router_mdc()))

    for stack in expand_types(types):
        glob_rule = TEMPLATE_DIR / "cursor" / f"{stack}.mdc"
        if glob_rule.is_file():
            actions.append(
                copy_if_missing(glob_rule, root / ".cursor" / "rules" / f"{stack}.mdc")
            )

    sys.stdout.write("Tikal initialized for types: " + ", ".join(types) + "\n")
    for line in actions:
        sys.stdout.write(line + "\n")
    sys.stdout.write(
        "\nAgents will load ai-coding-tools/stacks/<type>/ only for the types above.\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
