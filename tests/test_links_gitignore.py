"""links.py leaves out files that git ignores. Run: python -m unittest discover -s tests"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

LINKS = Path(__file__).resolve().parent.parent / "scripts" / "links.py"


def run(root):
    return subprocess.run([sys.executable, "-I", str(LINKS), str(root)],
                          capture_output=True, text=True, encoding="utf-8")


def workspace(tmp):
    root = Path(tmp)
    (root / "AGENTS.md").write_text("# Entry\n\n[ok](notes.md)\n", encoding="utf-8")
    (root / "notes.md").write_text("# Notes\n", encoding="utf-8")
    (root / "build").mkdir()
    (root / "build" / "draft.md").write_text("# Draft\n\n[gone](missing.md)\n", encoding="utf-8")
    (root / "scratch.md").write_text("# Scratch\n\n[gone](missing.md)\n", encoding="utf-8")
    (root / ".gitignore").write_text("build/\nscratch.md\n", encoding="utf-8")
    return root


@unittest.skipUnless(shutil.which("git"), "git not installed")
class IgnoredFiles(unittest.TestCase):
    def test_ignored_files_are_not_checked_in_a_git_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workspace(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            r = run(root)
            self.assertEqual(r.returncode, 0, r.stdout)
            self.assertIn("2 files", r.stdout)

    def test_a_tracked_file_is_checked_even_if_it_matches_gitignore(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workspace(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "add", "-f", "scratch.md"], check=True)
            r = run(root)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("scratch.md: missing.md", r.stdout)

    def test_outside_a_git_repo_every_file_is_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = workspace(tmp)
            r = run(root)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("4 files", r.stdout)


if __name__ == "__main__":
    unittest.main()
