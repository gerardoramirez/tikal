import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import init_project  # noqa: E402
import resolve_stack  # noqa: E402


def _run_init(argv):
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        exit_code = init_project.main(argv)
    return exit_code, stdout.getvalue(), stderr.getvalue()


class InitProjectTests(unittest.TestCase):
    def test_init_project__flutter_type__writes_config_and_resolves_flutter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exit_code, _, _ = _run_init(["--type", "flutter", "--name", "trail_app", "--root", str(root)])
            result = resolve_stack.resolve(root)

            self.assertEqual(exit_code, 0)
            self.assertEqual(result["types"], ["flutter"])
            self.assertEqual(result["name"], "trail_app")
            self.assertTrue((root / "tikal.yaml").is_file())
            self.assertTrue((root / "tikal.project.md").is_file())
            self.assertTrue((root / ".cursor" / "rules" / "tikal.mdc").is_file())
            self.assertTrue((root / ".cursor" / "rules" / "flutter.mdc").is_file())

    def test_init_project__astro_type__writes_astro_and_copies_typescript_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exit_code, _, _ = _run_init(["--type", "astro", "--name", "site", "--root", str(root)])
            result = resolve_stack.resolve(root)
            yaml_text = (root / "tikal.yaml").read_text()

            self.assertEqual(exit_code, 0)
            self.assertIn("- astro", yaml_text)
            self.assertNotIn("- typescript", yaml_text)
            self.assertEqual(result["types"], ["typescript", "astro"])
            self.assertTrue((root / ".cursor" / "rules" / "astro.mdc").is_file())
            self.assertTrue((root / ".cursor" / "rules" / "typescript.mdc").is_file())

    def test_init_project__unknown_type__exits_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exit_code, _, stderr = _run_init(["--type", "cobol", "--root", str(root)])
            self.assertIn("cobol", stderr)
            self.assertEqual(exit_code, 2)
            self.assertFalse((root / "tikal.yaml").exists())

    def test_init_project__second_run__does_not_overwrite_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _run_init(["--type", "flutter", "--name", "first", "--root", str(root)])
            (root / "tikal.yaml").write_text("project:\n  name: edited\n  types:\n    - flutter\n")
            _run_init(["--type", "flutter", "--name", "second", "--root", str(root)])
            result = resolve_stack.resolve(root)

        self.assertEqual(result["name"], "edited")


if __name__ == "__main__":
    unittest.main()
