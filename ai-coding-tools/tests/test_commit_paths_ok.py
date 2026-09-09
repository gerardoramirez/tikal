import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import commit_paths_ok  # noqa: E402


def _run(argv):
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        exit_code = commit_paths_ok.main(argv)
    return exit_code, stdout.getvalue(), stderr.getvalue()


class CommitPathsOkTests(unittest.TestCase):
    def test_commit_paths_ok__ordinary_project_file__exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exit_code, _, stderr = _run(["--root", str(root), "--", "tikal.yaml"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, "")

    def test_commit_paths_ok__env_file__exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exit_code, _, stderr = _run(["--root", str(root), "--", ".env"])

        self.assertEqual(exit_code, 2)
        self.assertIn(".env", stderr)

    def test_commit_paths_ok__env_local__exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exit_code, _, stderr = _run(["--root", str(root), "--", "app/.env.local"])

        self.assertEqual(exit_code, 2)
        self.assertIn(".env.local", stderr)

    def test_commit_paths_ok__env_example__exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exit_code, _, stderr = _run(["--root", str(root), "--", ".env.example"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, "")

    def test_commit_paths_ok__credentials_json__exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exit_code, _, stderr = _run(["--root", str(root), "--", "secrets.json"])

        self.assertEqual(exit_code, 2)
        self.assertIn("secrets.json", stderr)

    def test_commit_paths_ok__symlink_ai_coding_tools__exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ai-coding-tools").symlink_to(Path(tmp) / "elsewhere")
            exit_code, _, stderr = _run(
                ["--root", str(root), "--", "ai-coding-tools", "tikal.yaml"]
            )

        self.assertEqual(exit_code, 2)
        self.assertIn("ai-coding-tools", stderr)
        self.assertIn("symlink", stderr)

    def test_commit_paths_ok__real_ai_coding_tools_file__exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ai-coding-tools" / "processes").mkdir(parents=True)
            exit_code, _, stderr = _run(
                ["--root", str(root), "--", "ai-coding-tools/processes/git.md"]
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, "")

    def test_commit_paths_ok__no_paths_and_no_staged__exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exit_code, stdout, stderr = _run(["--root", str(root)])

        self.assertEqual(exit_code, 0)
        self.assertIn("No paths to check", stdout)
        self.assertEqual(stderr, "")


if __name__ == "__main__":
    unittest.main()
