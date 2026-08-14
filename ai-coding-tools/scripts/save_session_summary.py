"""Save a summary of the current Claude Code session to the context directory.

Intended to run as a Stop hook. Reads the transcript JSONL from stdin metadata,
extracts user prompts and assistant text responses, and writes a readable
markdown file to ai-coding-tools/context/.

Each invocation overwrites the same session file, so it stays current
throughout the conversation and is complete when the session ends.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def parse_input():
    """Read the Stop hook JSON from stdin."""
    try:
        return json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        return {}


def extract_turns(transcript_path):
    """Parse the JSONL transcript and return a list of (role, text) tuples."""
    turns = []
    with open(transcript_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Messages are nested under a "message" key in the transcript
            inner = msg.get("message", msg)
            role = inner.get("role", "")
            content = inner.get("content", "")

            # content can be a string or a list of blocks
            if isinstance(content, str):
                text = content.strip()
            elif isinstance(content, list):
                parts = []
                for block in content:
                    if isinstance(block, str):
                        parts.append(block)
                    elif isinstance(block, dict) and block.get("type") == "text":
                        parts.append(block.get("text", ""))
                text = "\n".join(parts).strip()
            else:
                continue

            if text and role in ("user", "assistant"):
                turns.append((role, text))

    return turns


def build_summary(turns, session_id):
    """Build a markdown summary from conversation turns."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# Session Summary — {timestamp}",
        f"Session ID: `{session_id}`\n",
    ]

    for role, text in turns:
        if role == "user":
            # Truncate very long user messages (e.g. pasted files)
            display = text if len(text) <= 500 else text[:500] + "\n[...truncated]"
            lines.append(f"## User\n{display}\n")
        else:
            lines.append(f"## Assistant\n{text}\n")

    return "\n".join(lines)


def slugify(text, max_words=6):
    """Turn text into a short lowercase-hyphenated slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    words = text.split()[:max_words]
    slug = "-".join(words) if words else "session"
    return slug[:60]


def main():
    hook_input = parse_input()

    # Prevent infinite loops: if this hook already triggered a continuation, skip
    if hook_input.get("stop_hook_active"):
        return

    transcript_path = hook_input.get("transcript_path", "")
    session_id = hook_input.get("session_id", "unknown")

    if not transcript_path or not Path(transcript_path).exists():
        return

    turns = extract_turns(transcript_path)
    if not turns:
        return

    summary = build_summary(turns, session_id)

    # Determine output directory
    project_dir = hook_input.get("cwd", os.getcwd())
    context_dir = Path(project_dir) / "ai-coding-tools" / "context"
    context_dir.mkdir(parents=True, exist_ok=True)

    # Build filename: YYYY-MM-DD-short-summary.md
    # Derive the summary slug from the first user message
    first_user_text = ""
    for role, text in turns:
        if role == "user":
            first_user_text = text
            break
    slug = slugify(first_user_text)
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = context_dir / f"{date_str}-{slug}.md"
    output_path.write_text(summary)


if __name__ == "__main__":
    main()
