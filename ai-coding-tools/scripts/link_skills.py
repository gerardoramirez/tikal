#!/usr/bin/env python3
"""Symlink Tikal skills into Claude and Cursor skill directories.

Opt-in. init_project.py does not run this. Existing destinations that are
not already the right symlink are left alone.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

INDEX_SKILL = "tikal"
FEATURE_SKILLS = (
    "tikal-code-review",
    "tikal-git",
    "tikal-refactor",
    "tikal-benchmark",
)
KNOWN_SKILLS = (INDEX_SKILL, *FEATURE_SKILLS)
HOSTS = (
    pathlib.Path(".claude") / "skills",
    pathlib.Path(".cursor") / "skills",
)
SKILLS_DIR = pathlib.Path(__file__).resolve().parent.parent / "skills"


class SkillLinkError(Exception):
    def __init__(self, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def skills_to_link(requested: list[str] | None) -> list[str]:
    """Default to every shipped skill. A named feature skill also links the index."""
    if not requested:
        return list(KNOWN_SKILLS)
    unknown = [name for name in requested if name not in KNOWN_SKILLS]
    if unknown:
        listed = ", ".join(unknown)
        known = ", ".join(KNOWN_SKILLS)
        raise SkillLinkError(
            f"Unknown skill: {listed}. Known skills: {known}.\n",
            2,
        )
    selected: list[str] = []
    if any(name != INDEX_SKILL for name in requested):
        selected.append(INDEX_SKILL)
    for name in requested:
        if name not in selected:
            selected.append(name)
    return selected


def _same_target(dest: pathlib.Path, source: pathlib.Path) -> bool:
    try:
        return dest.resolve() == source.resolve()
    except OSError:
        return False


def link_skill(dest_dir: pathlib.Path, skill_name: str, source: pathlib.Path) -> str:
    dest = dest_dir / skill_name
    if not source.is_dir():
        return f"missing {source}"
    if dest.is_symlink() and _same_target(dest, source):
        return f"skip  {dest} (already linked)"
    if dest.exists() or dest.is_symlink():
        return f"skip  {dest} (exists)"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.symlink_to(source)
    return f"link  {dest} -> {source}"


def link_into(base: pathlib.Path, skill_names: list[str]) -> list[str]:
    actions = []
    for host in HOSTS:
        dest_dir = base / host
        for name in skill_names:
            source = (SKILLS_DIR / name).resolve()
            actions.append(link_skill(dest_dir, name, source))
    return actions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Symlink Tikal skills into Claude and Cursor skill directories"
    )
    parser.add_argument(
        "--home",
        action="store_true",
        help="Link into the home skill directories",
    )
    parser.add_argument(
        "--home-dir",
        type=pathlib.Path,
        default=None,
        help="Home directory to use with --home (default: the real home)",
    )
    parser.add_argument(
        "--root",
        type=pathlib.Path,
        default=None,
        help="Project root to link into",
    )
    parser.add_argument(
        "--skill",
        action="append",
        default=None,
        help="Skill to link (repeatable). Default: the index and the workflow skills",
    )
    args = parser.parse_args(argv)
    if args.home_dir is not None and not args.home:
        sys.stderr.write("pass --home with --home-dir\n")
        return 2
    if not args.home and args.root is None:
        sys.stderr.write("pass --home, --root, or both\n")
        return 2

    try:
        names = skills_to_link(args.skill)
    except SkillLinkError as exc:
        sys.stderr.write(str(exc))
        return exc.exit_code

    actions: list[str] = []
    if args.home:
        home = (args.home_dir or pathlib.Path.home()).resolve()
        actions.extend(link_into(home, names))
    if args.root is not None:
        actions.extend(link_into(args.root.resolve(), names))

    sys.stdout.write("\n".join(actions) + "\n")
    if any(line.startswith("missing ") for line in actions):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
