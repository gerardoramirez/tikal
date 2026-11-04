#!/usr/bin/env python3
"""Print the files for one Tikal process id.

Skills name an id. This script finds the toolkit and prints only the
files that process needs.

Search order:
  1. TIKAL_HOME (clone root or the ai-coding-tools directory)
  2. Nearest ancestor that contains ai-coding-tools/processes
  3. ~/.tikal (clone root, or a symlink to one)
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys

from resolve_stack import resolve as resolve_project

_READ_ENV = object()
_MARKER = pathlib.Path("processes") / "getting-started.md"

PROCESS_SPECS: tuple[tuple[str, dict], ...] = (
    (
        "code-review",
        {
            "file": "processes/code-review.md",
            "also": ("processes/design-principles.md",),
            "stack_review": True,
        },
    ),
    ("git", {"file": "processes/git.md"}),
    ("refactoring", {"file": "processes/refactoring.md"}),
    ("benchmarking", {"file": "processes/benchmarking.md"}),
    ("design-principles", {"file": "processes/design-principles.md"}),
    ("rules-of-engagement", {"file": "processes/rules-of-engagement.md"}),
    ("programmer-mindset", {"file": "processes/programmer-mindset.md"}),
    ("htdd-gate", {"file": "processes/htdd-gate.md"}),
)

PROCESSES = dict(PROCESS_SPECS)
PROCESS_IDS = tuple(PROCESSES)


class ProcessLookupError(Exception):
    def __init__(self, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def _is_toolkit(path: pathlib.Path) -> bool:
    return (path / _MARKER).is_file()


def as_toolkit(path: pathlib.Path) -> pathlib.Path | None:
    """Return the ai-coding-tools directory when path is a clone or that directory."""
    if not path.exists():
        return None
    resolved = path.resolve()
    if _is_toolkit(resolved):
        return resolved
    nested = resolved / "ai-coding-tools"
    if _is_toolkit(nested):
        return nested.resolve()
    return None


def ancestor_toolkit(
    start: pathlib.Path,
    stop: pathlib.Path | None = None,
) -> pathlib.Path | None:
    """Nearest ancestor whose ai-coding-tools/processes directory is a toolkit."""
    boundary = stop.resolve() if stop is not None else None
    for candidate in (start, *start.parents):
        nested = candidate / "ai-coding-tools"
        if _is_toolkit(nested):
            return nested.resolve()
        if boundary is not None and candidate == boundary:
            return None
    return None


def locate_toolkit(
    start: pathlib.Path,
    *,
    tikal_home: str | None | object = _READ_ENV,
    home_checkout: pathlib.Path | None = None,
    stop: pathlib.Path | None = None,
) -> tuple[pathlib.Path | None, list[str]]:
    """Find the toolkit. The second value is the locations to report on failure."""
    if tikal_home is _READ_ENV:
        tikal_home = os.environ.get("TIKAL_HOME") or None
    if home_checkout is None:
        home_checkout = pathlib.Path.home() / ".tikal"

    tried: list[str] = []
    if tikal_home:
        tried.append(f"TIKAL_HOME={tikal_home}")
        found = as_toolkit(pathlib.Path(str(tikal_home)))
        if found is not None:
            return found, tried
    else:
        tried.append("TIKAL_HOME (unset)")

    start = start.resolve()
    tried.append(f"ancestors of {start} for ai-coding-tools/processes")
    found = ancestor_toolkit(start, stop)
    if found is not None:
        return found, tried

    tried.append(str(home_checkout))
    return as_toolkit(home_checkout), tried


def format_missing(tried: list[str]) -> str:
    lines = ["Tikal toolkit not found. Tried:"]
    lines.extend(f"- {item}" for item in tried)
    lines.append(
        "Set TIKAL_HOME to the clone root or the ai-coding-tools directory, "
        "link ai-coding-tools into the project, or check out the repo at ~/.tikal."
    )
    return "\n".join(lines) + "\n"


def resolve_process(
    process_id: str,
    *,
    project_root: pathlib.Path,
    start: pathlib.Path | None = None,
    tikal_home: str | None | object = _READ_ENV,
    home_checkout: pathlib.Path | None = None,
    stop: pathlib.Path | None = None,
) -> dict:
    """Return the toolkit and the absolute files a skill should read."""
    if process_id not in PROCESSES:
        known = ", ".join(PROCESS_IDS)
        raise ProcessLookupError(
            f"Unknown process '{process_id}'. Known process ids: {known}.\n",
            2,
        )

    toolkit, tried = locate_toolkit(
        start or project_root,
        tikal_home=tikal_home,
        home_checkout=home_checkout,
        stop=stop,
    )
    if toolkit is None:
        raise ProcessLookupError(format_missing(tried), 1)

    spec = PROCESSES[process_id]
    read_paths = [toolkit / spec["file"]]
    for extra in spec.get("also", ()):
        read_paths.append(toolkit / extra)
    missing = [path for path in read_paths if not path.is_file()]
    if missing:
        names = ", ".join(str(path) for path in missing)
        raise ProcessLookupError(
            "Process file is missing: "
            f"{names}. The toolkit was found, but that file is not in this checkout.\n",
            1,
        )

    stack_reviews: list[pathlib.Path] = []
    if spec.get("stack_review"):
        for stack in resolve_project(project_root)["types"]:
            review = toolkit / "stacks" / stack / "review.md"
            if review.is_file():
                stack_reviews.append(review)
        read_paths.extend(stack_reviews)

    return {
        "toolkit": toolkit,
        "process": process_id,
        "read": read_paths,
        "stack_review": bool(spec.get("stack_review")),
        "stack_reviews": stack_reviews,
    }


def format_result(result: dict) -> str:
    lines = [
        f"toolkit: {result['toolkit']}",
        f"process: {result['process']}",
        "read:",
    ]
    lines.extend(f"- {path}" for path in result["read"])
    if result["stack_review"] and not result["stack_reviews"]:
        lines.append("stacks: none")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print the files for one Tikal process id")
    parser.add_argument("process_id", help="Process id, for example code-review")
    parser.add_argument(
        "--root",
        type=pathlib.Path,
        default=None,
        help="Project root for stack types and the ancestor search (default: cwd)",
    )
    args = parser.parse_args(argv)
    root = (args.root or pathlib.Path.cwd()).resolve()
    try:
        result = resolve_process(args.process_id, project_root=root, start=root)
    except ProcessLookupError as exc:
        sys.stderr.write(str(exc))
        return exc.exit_code
    sys.stdout.write(format_result(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
