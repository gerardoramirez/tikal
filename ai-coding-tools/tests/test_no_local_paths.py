import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Split so this file does not itself contain a home-directory prefix.
HOME_MARKERS = (
    b"/Use" + b"rs/",
    b"/ho" + b"me/",
    b"/private/var/fol" + b"ders/",
)


class NoLocalPathsTests(unittest.TestCase):
    def test_tracked_files__contain_no_machine_paths(self):
        tracked = subprocess.check_output(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
        )
        paths = [p for p in tracked.decode().split("\0") if p]
        offenders = []
        for rel in paths:
            if rel.endswith((".pyc", ".pyo")) or "/__pycache__/" in rel:
                offenders.append(f"{rel}: tracked bytecode can embed a local path")
                continue
            data = (ROOT / rel).read_bytes()
            for marker in HOME_MARKERS:
                if marker in data:
                    offenders.append(f"{rel}: contains {marker.decode()}")
        self.assertEqual(offenders, [])
