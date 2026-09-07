import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import resolve_stack  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class ResolveStackTests(unittest.TestCase):
    def test_resolve_stack__this_tikal_repo__has_empty_types(self):
        repo_root = Path(__file__).resolve().parents[2]
        result = resolve_stack.resolve(repo_root)
        self.assertEqual(result["types"], [])
        self.assertEqual(result["source"], "config")
        self.assertEqual(result["name"], "tikal")

    def test_resolve_stack__tikal_yaml_lists_flutter__returns_flutter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root / "tikal.yaml",
                "project:\n  name: trail_app\n  types:\n    - flutter\n",
            )
            result = resolve_stack.resolve(root)

        self.assertEqual(result["types"], ["flutter"])
        self.assertEqual(result["name"], "trail_app")
        self.assertEqual(result["source"], "config")

    def test_resolve_stack__inline_types_list__returns_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "tikal.yaml", "project:\n  types: [flutter, python]\n")
            result = resolve_stack.resolve(root)

        self.assertEqual(result["types"], ["flutter", "python"])

    def test_resolve_stack__json_config__returns_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root / "tikal.json",
                json.dumps({"project": {"name": "api", "types": ["python"]}}),
            )
            result = resolve_stack.resolve(root)

        self.assertEqual(result["types"], ["python"])
        self.assertEqual(result["name"], "api")
        self.assertEqual(result["source"], "config")

    def test_resolve_stack__dotfile_yaml__is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / ".tikal.yaml", "project:\n  types:\n    - flutter\n")
            result = resolve_stack.resolve(root)

        self.assertEqual(result["types"], ["flutter"])

    def test_resolve_stack__empty_types__returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "tikal.yaml", "project:\n  name: tikal\n  types: []\n")
            _write(root / "pubspec.yaml", "name: leftover\nflutter:\n  uses-material-design: true\n")
            result = resolve_stack.resolve(root)

        self.assertEqual(result["types"], [])
        self.assertEqual(result["source"], "config")

    def test_resolve_stack__missing_config_with_pubspec_flutter__detects_flutter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root / "pubspec.yaml",
                "name: trail_app\nflutter:\n  uses-material-design: true\n",
            )
            result = resolve_stack.resolve(root)

        self.assertEqual(result["types"], ["flutter"])
        self.assertEqual(result["source"], "detect")

    def test_resolve_stack__missing_config_dart_only_pubspec__returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "pubspec.yaml", "name: cli_tool\ndependencies:\n  args: ^2.0.0\n")
            result = resolve_stack.resolve(root)

        self.assertEqual(result["types"], [])
        self.assertEqual(result["source"], "none")

    def test_resolve_stack__project_overview_present__is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "tikal.yaml", "project:\n  types:\n    - flutter\n")
            _write(root / "tikal.project.md", "# Overview\n")
            result = resolve_stack.resolve(root)

        self.assertEqual(result["project_overview"], "tikal.project.md")

    def test_resolve_stack__unknown_type__is_kept_and_missing_stack_noted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "tikal.yaml", "project:\n  types:\n    - rust\n")
            (root / "ai-coding-tools" / "stacks").mkdir(parents=True)
            result = resolve_stack.resolve(root)

        self.assertEqual(result["types"], ["rust"])
        self.assertEqual(result["missing_stacks"], ["rust"])

    def test_tracked_patterns__flutter_config__includes_flutter_stack_glob(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "tikal.yaml", "project:\n  types:\n    - flutter\n")
            patterns = resolve_stack.tracked_patterns(root)

        self.assertIn("ai-coding-tools/stacks/flutter/**/*.md", patterns)
        self.assertNotIn("ai-coding-tools/stacks/python/**/*.md", patterns)

    def test_resolve_stack__astro_type__expands_to_typescript_then_astro(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "tikal.yaml", "project:\n  types:\n    - astro\n")
            result = resolve_stack.resolve(root)

        self.assertEqual(result["types"], ["typescript", "astro"])
        self.assertEqual(result["source"], "config")

    def test_resolve_stack__typescript_type__does_not_add_astro(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "tikal.yaml", "project:\n  types:\n    - typescript\n")
            result = resolve_stack.resolve(root)

        self.assertEqual(result["types"], ["typescript"])

    def test_resolve_stack__missing_config_astro_and_tsconfig__detects_both(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "astro.config.mjs", "export default {}\n")
            _write(root / "tsconfig.json", "{}\n")
            result = resolve_stack.resolve(root)

        self.assertEqual(result["types"], ["typescript", "astro"])
        self.assertEqual(result["source"], "detect")

    def test_resolve_stack__missing_config_astro_only__still_implies_typescript(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "astro.config.ts", "export default {}\n")
            result = resolve_stack.resolve(root)

        self.assertEqual(result["types"], ["typescript", "astro"])
        self.assertEqual(result["source"], "detect")

    def test_resolve_stack__missing_config_tsconfig_only__detects_typescript(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "tsconfig.json", "{}\n")
            result = resolve_stack.resolve(root)

        self.assertEqual(result["types"], ["typescript"])
        self.assertEqual(result["source"], "detect")

    def test_resolve_stack__flutter_pubspec_without_tsconfig__does_not_add_typescript(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root / "pubspec.yaml",
                "name: trail_app\nflutter:\n  uses-material-design: true\n",
            )
            result = resolve_stack.resolve(root)

        self.assertEqual(result["types"], ["flutter"])
        self.assertNotIn("typescript", result["types"])

    def test_tracked_patterns__astro_config__includes_typescript_and_astro_globs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "tikal.yaml", "project:\n  types:\n    - astro\n")
            patterns = resolve_stack.tracked_patterns(root)

        self.assertIn("ai-coding-tools/stacks/typescript/**/*.md", patterns)
        self.assertIn("ai-coding-tools/stacks/astro/**/*.md", patterns)

    def test_tracked_patterns__empty_types__omits_flutter_stack_glob(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "tikal.yaml", "project:\n  name: tikal\n  types: []\n")
            patterns = resolve_stack.tracked_patterns(root)

        self.assertTrue(all("stacks/flutter" not in item for item in patterns))


if __name__ == "__main__":
    unittest.main()
