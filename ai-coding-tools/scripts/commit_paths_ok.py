#!/usr/bin/env python3
"""Refuse forbidden paths before an agent stages a commit.

Checks listed paths (after --) or currently staged files. Does not run
git add or git commit. Exit 0 if every path is allowed; exit 2 if any
path must stay out of the commit.
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

ALLOWED_ENV_NAMES = frozenset({".env.example", ".env.sample", ".env.template"})
CREDENTIAL_NAMES = frozenset(
    {"credentials.json", "secrets.json", "service-account.json"}
)


def _is_env_secret(name: str) -> bool:
    if name in ALLOWED_ENV_NAMES:
        return False
    return name == ".env" or name.startswith(".env.")


def forbidden_reason(root: pathlib.Path, rel_path: str) -> str | None:
    """Return why this relative path must not be committed, or None."""
    normalized = rel_path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if not normalized:
        return None
    name = pathlib.PurePosixPath(normalized).name
    if _is_env_secret(name):
        return f"{normalized}: env files can hold secrets. Do not stage this path."
    if name in CREDENTIAL_NAMES:
        return f"{normalized}: credential file. Do not stage this path."

    first = pathlib.PurePosixPath(normalized).parts[0]
    if first == "ai-coding-tools":
        toolkit = root / "ai-coding-tools"
        if toolkit.is_symlink():
            return (
                f"{normalized}: ai-coding-tools is a symlink. "
                "Do not stage the toolkit link or files through it."
            )
    return None


def staged_paths(root: pathlib.Path) -> list[str]:
    git_dir = root / ".git"
    if not git_dir.exists() and not git_dir.is_file():
        return []
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "-z"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0 or not result.stdout:
        return []
    return [part for part in result.stdout.decode().split("\0") if part]


def check_paths(root: pathlib.Path, paths: list[str]) -> list[str]:
    problems = []
    for rel_path in paths:
        reason = forbidden_reason(root, rel_path)
        if reason:
            problems.append(reason)
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that listed or staged paths are safe to commit. "
        "Does not stage or commit."
    )
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path.cwd())
    parser.add_argument(
        "paths",
        nargs="*",
        help="Relative paths to check. If omitted, uses staged files.",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    paths = list(args.paths) if args.paths else staged_paths(root)
    if not paths:
        sys.stdout.write("No paths to check.\n")
        return 0

    problems = check_paths(root, paths)
    if problems:
        sys.stderr.write("Refusing to allow these paths in a commit:\n")
        for line in problems:
            sys.stderr.write(f"  {line}\n")
        return 2

    sys.stdout.write("OK: " + ", ".join(paths) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
