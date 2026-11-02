import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import propose_commit_message  # noqa: E402


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def _head(root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
    ).strip()


def _write_flag(root: Path, enabled: bool) -> None:
    value = "true" if enabled else "false"
    (root / "tikal.yaml").write_text(
        f"project:\n  name: app\n  types: []\n  auto_commit_message: {value}\n"
    )


def _init_repo(root: Path, enabled: bool) -> str:
    _git(root, "init")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")
    _write_flag(root, enabled)
    (root / "README").write_text("hi\n")
    _git(root, "add", "README", "tikal.yaml")
    _git(root, "-c", "commit.gpgsign=false", "commit", "-m", "init")
    return _head(root)


def _dirty(root: Path) -> None:
    (root / "notes.txt").write_text("changed\n")


class ProposeCommitMessageTests(unittest.TestCase):
    def test_propose_commit_message__flag_off__returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            head = _init_repo(root, False)
            _dirty(root)
            result = propose_commit_message.decide(
                {
                    "hook_event_name": "stop",
                    "cursor_version": "1.0",
                    "status": "completed",
                    "loop_count": 0,
                    "workspace_roots": [str(root)],
                }
            )
            self.assertEqual(result, {})
            self.assertEqual(_head(root), head)

    def test_propose_commit_message__clean_tree__returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            head = _init_repo(root, True)
            result = propose_commit_message.decide(
                {
                    "stop_hook_active": False,
                    "cwd": str(root),
                    "status": "completed",
                }
            )
            self.assertEqual(result, {})
            self.assertEqual(_head(root), head)

    def test_propose_commit_message__loop_count_already_used__returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo(root, True)
            _dirty(root)
            result = propose_commit_message.decide(
                {
                    "hook_event_name": "stop",
                    "status": "completed",
                    "loop_count": 1,
                    "workspace_roots": [str(root)],
                }
            )

        self.assertEqual(result, {})

    def test_propose_commit_message__stop_hook_active__returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo(root, True)
            _dirty(root)
            result = propose_commit_message.decide(
                {
                    "stop_hook_active": True,
                    "cwd": str(root),
                    "loop_count": 0,
                }
            )

        self.assertEqual(result, {})

    def test_propose_commit_message__aborted__returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo(root, True)
            _dirty(root)
            result = propose_commit_message.decide(
                {
                    "hook_event_name": "stop",
                    "status": "aborted",
                    "loop_count": 0,
                    "workspace_roots": [str(root)],
                }
            )

        self.assertEqual(result, {})

    def test_propose_commit_message__error_status__returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo(root, True)
            _dirty(root)
            result = propose_commit_message.decide(
                {
                    "hook_event_name": "stop",
                    "status": "error",
                    "loop_count": 0,
                    "workspace_roots": [str(root)],
                }
            )

        self.assertEqual(result, {})

    def test_propose_commit_message__cursor_dirty_tree__returns_followup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            head = _init_repo(root, True)
            _dirty(root)
            result = propose_commit_message.decide(
                {
                    "hook_event_name": "stop",
                    "cursor_version": "1.0",
                    "status": "completed",
                    "loop_count": 0,
                    "workspace_roots": [str(root)],
                }
            )
            self.assertEqual(_head(root), head)

        self.assertEqual(set(result), {"followup_message"})
        self.assertIn("## Proposed commit message", result["followup_message"])
        self.assertIn("Do not stage", result["followup_message"])

    def test_propose_commit_message__claude_dirty_tree__returns_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            head = _init_repo(root, True)
            _dirty(root)
            result = propose_commit_message.decide(
                {
                    "session_id": "abc",
                    "hook_event_name": "Stop",
                    "stop_hook_active": False,
                    "cwd": str(root),
                }
            )
            self.assertEqual(_head(root), head)

        self.assertEqual(result["decision"], "block")
        self.assertIn("## Proposed commit message", result["reason"])
        self.assertNotIn("followup_message", result)

    def test_propose_commit_message__proposal_already_present__returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            head = _init_repo(root, True)
            _dirty(root)
            transcript = root / "transcript.jsonl"
            transcript.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "message": {
                                    "role": "assistant",
                                    "content": "working",
                                }
                            }
                        ),
                        json.dumps(
                            {
                                "message": {
                                    "role": "assistant",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "## Proposed commit message\n\nwhy",
                                        }
                                    ],
                                }
                            }
                        ),
                        json.dumps(
                            {"message": {"role": "user", "content": "thanks"}}
                        ),
                    ]
                )
                + "\n"
            )
            result = propose_commit_message.decide(
                {
                    "hook_event_name": "stop",
                    "status": "completed",
                    "loop_count": 0,
                    "cwd": str(root),
                    "transcript_path": str(transcript),
                }
            )
            self.assertEqual(result, {})
            self.assertEqual(_head(root), head)

    def test_propose_commit_message__last_assistant_message_has_heading__returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _init_repo(root, True)
            _dirty(root)
            result = propose_commit_message.decide(
                {
                    "hook_event_name": "Stop",
                    "stop_hook_active": False,
                    "cwd": str(root),
                    "last_assistant_message": "## Proposed commit message\n\nwhy",
                }
            )

        self.assertEqual(result, {})

    def test_propose_commit_message__not_a_repository__returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_flag(root, True)
            _dirty(root)
            result = propose_commit_message.decide(
                {
                    "stop_hook_active": False,
                    "cwd": str(root),
                    "status": "completed",
                }
            )

        self.assertEqual(result, {})

    def test_propose_commit_message__source__does_not_invoke_git_commit(self):
        source = (SCRIPTS / "propose_commit_message.py").read_text()
        self.assertIn("git commit -m", source)
        self.assertNotIn("HEREDOC", source)
        self.assertNotIn("git add", source)
        self.assertIn('["git", "status", "--porcelain"]', source)
        self.assertNotIn('"commit"', source)
        self.assertNotIn("'commit'", source)

    def test_propose_commit_message__main_cursor_dirty_tree__prints_followup_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            head = _init_repo(root, True)
            _dirty(root)
            payload = json.dumps(
                {
                    "hook_event_name": "stop",
                    "cursor_version": "1.0",
                    "status": "completed",
                    "loop_count": 0,
                    "workspace_roots": [str(root)],
                }
            )
            stdout = StringIO()
            original_stdin = sys.stdin
            sys.stdin = StringIO(payload)
            try:
                with redirect_stdout(stdout):
                    exit_code = propose_commit_message.main([])
            finally:
                sys.stdin = original_stdin
            self.assertEqual(exit_code, 0)
            self.assertEqual(_head(root), head)

        printed = json.loads(stdout.getvalue())
        self.assertIn("followup_message", printed)


if __name__ == "__main__":
    unittest.main()
