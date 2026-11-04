import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
SKILLS = Path(__file__).resolve().parent.parent / "skills"
sys.path.insert(0, str(SCRIPTS))

import init_project  # noqa: E402
import link_skills  # noqa: E402
import resolve_process  # noqa: E402

FIND_BLOCK = """Locate `resolve_process.py` in this order:

1. If `TIKAL_HOME` is set, use `$TIKAL_HOME/ai-coding-tools/scripts/resolve_process.py` when that clone root exists, or `$TIKAL_HOME/scripts/resolve_process.py` when `TIKAL_HOME` is the `ai-coding-tools` directory.
2. Otherwise walk up from the workspace for `ai-coding-tools/scripts/resolve_process.py`.
3. Otherwise use `~/.tikal/ai-coding-tools/scripts/resolve_process.py`. `~/.tikal` is the clone root or a symlink to it.

Run that script with `python3` and the process id. Read only the paths it prints. Do not load the router or any other process.
"""

FEATURE_SKILLS = {
    "tikal-code-review": "code-review",
    "tikal-git": "git",
    "tikal-refactor": "refactoring",
    "tikal-benchmark": "benchmarking",
}


def _run(argv):
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        exit_code = link_skills.main(argv)
    return exit_code, stdout.getvalue(), stderr.getvalue()


class LinkSkillsTests(unittest.TestCase):
    def test_link_skills__home_dir__symlinks_index_and_workflows(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            exit_code, stdout, stderr = _run(["--home", "--home-dir", str(home)])

            self.assertEqual(exit_code, 0, stderr)
            self.assertEqual(stderr, "")
            for host in (".claude", ".cursor"):
                for name in link_skills.KNOWN_SKILLS:
                    dest = home / host / "skills" / name
                    self.assertTrue(dest.is_symlink(), dest)
                    self.assertEqual(dest.resolve(), (link_skills.SKILLS_DIR / name).resolve())
            self.assertIn("link  ", stdout)

    def test_link_skills__one_workflow_skill__also_links_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            exit_code, _, stderr = _run(
                ["--home", "--home-dir", str(home), "--skill", "tikal-git"]
            )
            linked = {path.name for path in (home / ".claude" / "skills").iterdir()}
            cursor = {path.name for path in (home / ".cursor" / "skills").iterdir()}

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(linked, {"tikal", "tikal-git"})
        self.assertEqual(cursor, {"tikal", "tikal-git"})

    def test_link_skills__index_only__does_not_add_workflows(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            exit_code, _, stderr = _run(["--home", "--home-dir", str(home), "--skill", "tikal"])
            linked = {path.name for path in (home / ".claude" / "skills").iterdir()}

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(linked, {"tikal"})

    def test_link_skills__existing_directory__leaves_it_in_place(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            dest = home / ".claude" / "skills" / "tikal"
            dest.mkdir(parents=True)
            (dest / "SKILL.md").write_text("keep\n")
            exit_code, stdout, stderr = _run(["--home", "--home-dir", str(home)])

            self.assertEqual(exit_code, 0, stderr)
            self.assertEqual((dest / "SKILL.md").read_text(), "keep\n")
            self.assertFalse(dest.is_symlink())
            self.assertIn(f"skip  {dest.resolve()} (exists)", stdout)
            self.assertTrue((home / ".cursor" / "skills" / "tikal").is_symlink())

    def test_link_skills__existing_other_symlink__leaves_it_in_place(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            other = home / "other-skill"
            other.mkdir()
            dest = home / ".claude" / "skills" / "tikal-git"
            dest.parent.mkdir(parents=True)
            dest.symlink_to(other)
            exit_code, stdout, stderr = _run(
                ["--home", "--home-dir", str(home), "--skill", "tikal-git"]
            )

            self.assertEqual(exit_code, 0, stderr)
            self.assertEqual(dest.resolve(), other.resolve())
            reported = dest.parent.resolve() / dest.name
            self.assertIn(f"skip  {reported} (exists)", stdout)

    def test_link_skills__second_run__skips_existing_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            first, _, _ = _run(["--home", "--home-dir", str(home), "--skill", "tikal"])
            exit_code, stdout, stderr = _run(
                ["--home", "--home-dir", str(home), "--skill", "tikal"]
            )

        self.assertEqual(first, 0)
        self.assertEqual(exit_code, 0, stderr)
        self.assertIn("already linked", stdout)
        self.assertNotIn("link  ", stdout)

    def test_link_skills__project_root__symlinks_under_the_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "app"
            exit_code, _, stderr = _run(["--root", str(root)])

            self.assertEqual(exit_code, 0, stderr)
            self.assertTrue((root / ".claude" / "skills" / "tikal").is_symlink())
            self.assertTrue((root / ".cursor" / "skills" / "tikal-benchmark").is_symlink())

    def test_link_skills__unknown_skill__exits_without_linking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "app"
            exit_code, stdout, stderr = _run(["--root", str(root), "--skill", "git"])

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("git", stderr)
        self.assertIn("tikal-git", stderr)
        self.assertFalse(root.exists())

    def test_link_skills__no_target__exits_without_using_a_home(self):
        exit_code, stdout, stderr = _run([])

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("--home", stderr)

    def test_link_skills__home_dir_without_home__does_not_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            exit_code, stdout, stderr = _run(["--home-dir", str(home)])

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("--home", stderr)
        self.assertFalse((home / ".claude").exists())

    def test_init_project__flutter_type__does_not_link_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = init_project.main(["--type", "flutter", "--root", str(root)])

            self.assertEqual(exit_code, 0, stderr.getvalue())
            self.assertFalse((root / ".claude" / "skills").exists())
            self.assertFalse((root / ".cursor" / "skills").exists())
            self.assertTrue((root / ".cursor" / "rules" / "tikal.mdc").is_file())

    def test_skills__feature_skills__repeat_the_find_block_and_name_a_known_process(self):
        index = (SKILLS / "tikal" / "SKILL.md").read_text()
        self.assertIn("disable-model-invocation: true", index)
        self.assertIn(FIND_BLOCK, index)
        for process_id in resolve_process.PROCESS_IDS:
            self.assertIn(f"`{process_id}`", index)

        for skill_name, process_id in FEATURE_SKILLS.items():
            text = (SKILLS / skill_name / "SKILL.md").read_text()
            self.assertIn(f"name: {skill_name}\n", text)
            self.assertIn(f"Process id: `{process_id}`", text)
            self.assertIn(FIND_BLOCK, text)
            self.assertIn(process_id, resolve_process.PROCESSES)
            self.assertNotIn("disable-model-invocation", text)


if __name__ == "__main__":
    unittest.main()
