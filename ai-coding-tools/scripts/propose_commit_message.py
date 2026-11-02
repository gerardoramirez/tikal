#!/usr/bin/env python3
"""Decide whether a stop hook should ask the agent for one commit message.

Prints JSON on stdout. Does not stage or commit. Stays quiet unless
project.auto_commit_message is on, the turn completed normally, the
worktree is dirty, and the reply does not already propose a message.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import resolve_stack

PROPOSAL_HEADING = "## Proposed commit message"

FOLLOWUP_MESSAGE = (
    "auto_commit_message is on. Read ai-coding-tools/processes/git.md. "
    "If you changed files this turn, propose one commit message under the heading "
    "`## Proposed commit message`, in a HEREDOC, focused on why. "
    "Do not stage, commit, push, or amend. "
    "If you did not change files this turn, say so and stop."
)


def workspace_root(hook_input: dict) -> Path:
    cwd = hook_input.get("cwd")
    if isinstance(cwd, str) and cwd.strip():
        return Path(cwd)
    roots = hook_input.get("workspace_roots") or []
    if isinstance(roots, list):
        for item in roots:
            if isinstance(item, str) and item.strip():
                return Path(item)
    return resolve_stack.project_root(None)


def _stopped_cleanly(hook_input: dict) -> bool:
    status = hook_input.get("status")
    if status is None:
        return True
    return status == "completed"


def _already_continued(hook_input: dict) -> bool:
    if hook_input.get("stop_hook_active"):
        return True
    raw = hook_input.get("loop_count", 0)
    try:
        count = int(raw)
    except (TypeError, ValueError):
        return True
    return count != 0


def _is_cursor(hook_input: dict) -> bool:
    if hook_input.get("cursor_version"):
        return True
    if "stop_hook_active" in hook_input:
        return False
    return bool(hook_input.get("hook_event_name"))


def worktree_dirty(root: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False
    if result.returncode != 0:
        return False
    return bool(result.stdout.strip())


def _content_text(content: object) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "\n".join(parts).strip()
    return ""


def last_assistant_text(transcript_path: object) -> str:
    if not isinstance(transcript_path, str) or not transcript_path.strip():
        return ""
    path = Path(transcript_path)
    if not path.is_file():
        return ""
    last = ""
    try:
        lines = path.read_text(errors="replace").splitlines()
    except OSError:
        return ""
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            msg = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if not isinstance(msg, dict):
            continue
        inner = msg.get("message", msg)
        if not isinstance(inner, dict):
            continue
        if inner.get("role") != "assistant":
            continue
        text = _content_text(inner.get("content", ""))
        if text:
            last = text
    return last


def proposal_already_present(hook_input: dict) -> bool:
    direct = hook_input.get("last_assistant_message")
    if isinstance(direct, str) and PROPOSAL_HEADING in direct:
        return True
    return PROPOSAL_HEADING in last_assistant_text(hook_input.get("transcript_path"))


def followup_output(hook_input: dict) -> dict:
    if _is_cursor(hook_input):
        return {"followup_message": FOLLOWUP_MESSAGE}
    return {"decision": "block", "reason": FOLLOWUP_MESSAGE}


def decide(hook_input: dict) -> dict:
    """Return the JSON object a stop hook should print."""
    if not isinstance(hook_input, dict):
        return {}
    if not _stopped_cleanly(hook_input) or _already_continued(hook_input):
        return {}
    root = workspace_root(hook_input)
    if not resolve_stack.resolve(root).get("auto_commit_message"):
        return {}
    if not worktree_dirty(root):
        return {}
    if proposal_already_present(hook_input):
        return {}
    return followup_output(hook_input)


def main(argv: list[str] | None = None) -> int:
    del argv
    try:
        raw = sys.stdin.read()
        hook_input = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        hook_input = {}
    if not isinstance(hook_input, dict):
        hook_input = {}
    json.dump(decide(hook_input), sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
