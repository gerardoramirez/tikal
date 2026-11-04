import os
import sys
import tempfile
import unittest
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import resolve_process  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _toolkit(root: Path) -> Path:
    toolkit = root / "ai-coding-tools"
    for name in (
        "getting-started.md",
        "code-review.md",
        "design-principles.md",
        "git.md",
        "refactoring.md",
        "benchmarking.md",
        "rules-of-engagement.md",
        "programmer-mindset.md",
        "htdd-gate.md",
    ):
        _write(toolkit / "processes" / name, f"# {name}\n")
    for stack in ("flutter", "typescript", "astro"):
        _write(toolkit / "stacks" / stack / "review.md", f"# {stack}\n")
    return toolkit.resolve()


def _lookup(process_id: str, project: Path, **kwargs):
    kwargs.setdefault("tikal_home", None)
    kwargs.setdefault("home_checkout", project / "no-home-checkout")
    kwargs.setdefault("stop", project)
    start = kwargs.pop("start", project)
    return resolve_process.resolve_process(
        process_id,
        project_root=project,
        start=start,
        **kwargs,
    )


def _run_main(argv):
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        exit_code = resolve_process.main(argv)
    return exit_code, stdout.getvalue(), stderr.getvalue()


@contextmanager
def _without_tikal_home():
    old = os.environ.pop("TIKAL_HOME", None)
    try:
        yield
    finally:
        if old is not None:
            os.environ["TIKAL_HOME"] = old


class ResolveProcessTests(unittest.TestCase):
    def test_resolve_process__project_link_and_home_checkout__uses_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            home = base / "home-tikal"
            project_toolkit = _toolkit(project)
            home_toolkit = _toolkit(home)
            (project_toolkit / "processes" / "git.md").write_text("project\n")
            (home_toolkit / "processes" / "git.md").write_text("home\n")
            (project / "src").mkdir(parents=True)
            result = resolve_process.resolve_process(
                "git",
                project_root=project,
                start=project / "src",
                tikal_home=None,
                home_checkout=home,
                stop=base,
            )
            self.assertEqual(result["read"][0].read_text(), "project\n")

        self.assertEqual(result["toolkit"], project_toolkit)
        self.assertEqual(result["read"], [project_toolkit / "processes" / "git.md"])

    def test_resolve_process__tikal_home_and_project_link__uses_tikal_home(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            home = base / "home-tikal"
            _toolkit(project)
            home_toolkit = _toolkit(home)
            (home_toolkit / "processes" / "git.md").write_text("home\n")
            result = resolve_process.resolve_process(
                "git",
                project_root=project,
                start=project,
                tikal_home=str(home),
                home_checkout=base / "unused",
                stop=base,
            )
            self.assertEqual(result["read"][0].read_text(), "home\n")

        self.assertEqual(result["toolkit"], home_toolkit)

    def test_resolve_process__tikal_home_is_toolkit_dir__uses_that_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            home_toolkit = _toolkit(base / "home-tikal")
            _toolkit(project)
            result = resolve_process.resolve_process(
                "git",
                project_root=project,
                start=project,
                tikal_home=str(home_toolkit),
                home_checkout=base / "unused",
                stop=base,
            )

        self.assertEqual(result["toolkit"], home_toolkit)

    def test_resolve_process__no_project_link__uses_home_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            app = base / "app"
            app.mkdir()
            home = base / "home-tikal"
            home_toolkit = _toolkit(home)
            link = base / "linked-home"
            link.symlink_to(home)
            result = resolve_process.resolve_process(
                "git",
                project_root=app,
                start=app,
                tikal_home=None,
                home_checkout=link,
                stop=base,
            )

        self.assertEqual(result["toolkit"], home_toolkit)

    def test_resolve_process__invalid_tikal_home__falls_through_to_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            project = base / "project"
            project_toolkit = _toolkit(project)
            result = resolve_process.resolve_process(
                "git",
                project_root=project,
                start=project,
                tikal_home=str(base / "missing-home"),
                home_checkout=base / "also-missing",
                stop=base,
            )

        self.assertEqual(result["toolkit"], project_toolkit)

    def test_resolve_process__nothing_installed__names_the_three_locations(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            empty = base / "empty"
            empty.mkdir()
            home = base / "nope"
            with self.assertRaises(resolve_process.ProcessLookupError) as caught:
                resolve_process.resolve_process(
                    "git",
                    project_root=empty,
                    start=empty,
                    tikal_home=None,
                    home_checkout=home,
                    stop=base,
                )

        self.assertEqual(caught.exception.exit_code, 1)
        message = str(caught.exception)
        self.assertIn("TIKAL_HOME (unset)", message)
        self.assertIn("ancestors of", message)
        self.assertIn(str(home), message)
        self.assertIn("~/.tikal", message)

    def test_resolve_process__unknown_id__lists_known_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            with self.assertRaises(resolve_process.ProcessLookupError) as caught:
                _lookup("nope", project)

        self.assertEqual(caught.exception.exit_code, 2)
        message = str(caught.exception)
        self.assertIn("Known process ids:", message)
        for process_id in resolve_process.PROCESS_IDS:
            self.assertIn(process_id, message)

    def test_resolve_process__missing_process_file__names_the_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            toolkit = _toolkit(project)
            (toolkit / "processes" / "git.md").unlink()
            with self.assertRaises(resolve_process.ProcessLookupError) as caught:
                _lookup("git", project)

        self.assertEqual(caught.exception.exit_code, 1)
        self.assertIn("git.md", str(caught.exception))

    def test_resolve_process__code_review_astro__includes_design_principles_and_expanded_reviews(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            toolkit = _toolkit(project)
            _write(project / "tikal.yaml", "project:\n  name: site\n  types:\n    - astro\n")
            result = _lookup("code-review", project)
            rendered = resolve_process.format_result(result)

        relative = [path.relative_to(toolkit).as_posix() for path in result["read"]]
        self.assertEqual(
            relative,
            [
                "processes/code-review.md",
                "processes/design-principles.md",
                "stacks/typescript/review.md",
                "stacks/astro/review.md",
            ],
        )
        self.assertNotIn("stacks/flutter", rendered)
        self.assertNotIn("stacks: none", rendered)

    def test_resolve_process__code_review_types_from_project_files_from_tikal_home(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            app = base / "app"
            _write(app / "tikal.yaml", "project:\n  name: site\n  types:\n    - astro\n")
            home_toolkit = _toolkit(base / "home-tikal")
            result = resolve_process.resolve_process(
                "code-review",
                project_root=app,
                start=app,
                tikal_home=str(base / "home-tikal"),
                home_checkout=base / "unused",
                stop=base,
            )

        self.assertEqual(result["toolkit"], home_toolkit)
        self.assertTrue(all(path.is_relative_to(home_toolkit) for path in result["read"]))
        self.assertEqual(result["read"][2].parent.name, "typescript")
        self.assertEqual(result["read"][3].parent.name, "astro")

    def test_resolve_process__code_review_without_types__says_stacks_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            _toolkit(project)
            _write(project / "tikal.yaml", "project:\n  name: bare\n  types: []\n")
            result = _lookup("code-review", project)
            rendered = resolve_process.format_result(result)

        self.assertEqual(len(result["read"]), 2)
        self.assertIn("stacks: none\n", rendered)
        self.assertNotIn("stacks/flutter", rendered)
        self.assertNotIn("stacks/typescript", rendered)
        self.assertNotIn("stacks/astro", rendered)

    def test_resolve_process__code_review_without_config__says_stacks_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            _toolkit(project)
            result = _lookup("code-review", project)
            rendered = resolve_process.format_result(result)

        self.assertEqual(len(result["read"]), 2)
        self.assertIn("stacks: none\n", rendered)

    def test_resolve_process__code_review_missing_one_review__skips_that_stack(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            toolkit = _toolkit(project)
            (toolkit / "stacks" / "astro" / "review.md").unlink()
            _write(project / "tikal.yaml", "project:\n  name: site\n  types:\n    - astro\n")
            result = _lookup("code-review", project)

        self.assertEqual([path.parent.name for path in result["stack_reviews"]], ["typescript"])

    def test_resolve_process__git_with_flutter_project__does_not_include_stack_reviews(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            _toolkit(project)
            _write(project / "tikal.yaml", "project:\n  name: app\n  types:\n    - flutter\n")
            result = _lookup("git", project)
            rendered = resolve_process.format_result(result)

        self.assertEqual(len(result["read"]), 1)
        self.assertNotIn("stacks:", rendered)
        self.assertNotIn("review.md", rendered)

    def test_main__code_review__prints_read_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            toolkit = _toolkit(project)
            _write(project / "tikal.yaml", "project:\n  name: site\n  types:\n    - astro\n")
            with _without_tikal_home():
                exit_code, stdout, stderr = _run_main(["code-review", "--root", str(project)])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, "")
        self.assertIn(f"toolkit: {toolkit}\n", stdout)
        self.assertIn("process: code-review\n", stdout)
        self.assertIn(f"- {toolkit / 'processes' / 'code-review.md'}\n", stdout)
        self.assertIn(f"- {toolkit / 'processes' / 'design-principles.md'}\n", stdout)
        self.assertIn(f"- {toolkit / 'stacks' / 'typescript' / 'review.md'}\n", stdout)
        self.assertIn(f"- {toolkit / 'stacks' / 'astro' / 'review.md'}\n", stdout)
        self.assertNotIn("stacks/flutter", stdout)

    def test_main__unknown_id__writes_known_ids_to_stderr(self):
        exit_code, stdout, stderr = _run_main(["not-a-process"])

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("Known process ids:", stderr)


if __name__ == "__main__":
    unittest.main()
