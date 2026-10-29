"""Tests for scripts/: each builds a small workspace in a temp folder and runs a script on it.

    python -I -m unittest discover -s tests

Standard library only. Runs on Python 3.9 and later.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def run(script, *args):
    p = subprocess.run([sys.executable, "-I", str(SCRIPTS / script), *map(str, args)],
                       capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout + p.stderr


class Workspace(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        return path


class Quotes(Workspace):
    def bundle(self, raw, note, keep_out=""):
        self.write("sources/raw/talk.txt", raw)
        self.write("concepts/idea.md", note)
        if keep_out:
            self.write("_meta/keep-out.txt", keep_out)
        return run("quotes.py", self.root)

    def test_real_english_quote_passes(self):
        code, out = self.bundle("[00:10] We keep the folder small.\n", '"We keep the folder small" (talk 00:10)\n')
        self.assertEqual(code, 0, out)

    def test_invented_english_quote_fails(self):
        code, out = self.bundle("[00:10] We keep the folder small.\n", '"We make the folder huge" (talk 00:10)\n')
        self.assertEqual(code, 1, out)

    def test_real_hebrew_quote_passes(self):
        code, out = self.bundle("[00:10] אנחנו שומרים על התיקייה קטנה.\n",
                                '"אנחנו שומרים על התיקייה קטנה" (talk 00:10)\n')
        self.assertEqual(code, 0, out)

    def test_invented_hebrew_quote_fails(self):
        code, out = self.bundle("[00:10] אנחנו שומרים על התיקייה קטנה.\n",
                                '"משפט שאף אחד לא אמר" (talk 00:10)\n')
        self.assertEqual(code, 1, out)
        self.assertIn("not found", out)

    def test_invented_chinese_quote_fails(self):
        code, out = self.bundle("[00:10] 我们保持文件夹很小。\n", '"这句话从来没有人说过" (talk 00:10)\n')
        self.assertEqual(code, 1, out)

    def test_quote_matches_despite_niqqud_in_source(self):
        code, out = self.bundle("[00:10] שָׁלוֹם עוֹלָם וְכָל הַחֲבֵרִים\n", '"שלום עולם וכל החברים" (talk 00:10)\n')
        self.assertEqual(code, 0, out)

    def test_quote_with_no_words_fails(self):
        code, out = self.bundle("[00:10] We keep the folder small.\n", '"?!" (talk 00:10)\n')
        self.assertEqual(code, 1, out)

    def test_timestamp_on_its_own_line(self):
        raw = "[00:10]\nWe keep the folder small.\nIt stays readable.\n\n[00:40]\nThen we move on.\n"
        code, out = self.bundle(raw, '"We keep the folder small. It stays readable" (talk 00:10)\n')
        self.assertEqual(code, 0, out)

    def test_timestamp_on_its_own_line_still_checks_position(self):
        raw = "[00:10]\nFirst part.\n[01:00]\nSecond.\n[02:00]\nThird.\n[03:00]\nWe keep the folder small.\n"
        code, out = self.bundle(raw, '"We keep the folder small" (talk 00:10)\n')
        self.assertEqual(code, 1, out)

    def test_keep_out_whole_word_in_english(self):
        code, out = self.bundle("[00:10] hi\n", "Alice wrote this.\n", keep_out="Al\n")
        self.assertEqual(code, 0, out)
        code, out = self.bundle("[00:10] hi\n", "Al wrote this.\n", keep_out="Al\n")
        self.assertEqual(code, 1, out)

    def test_keep_out_catches_hebrew_prefixes(self):
        for text in ("דני", "לדני", "ודני", "שלדני", "כשדני"):
            with self.subTest(text=text):
                code, out = self.bundle("[00:10] hi\n", f"נתתי את זה {text} אתמול.\n", keep_out="דני\n")
                self.assertEqual(code, 1, out)

    def test_keep_out_catches_arabic_prefixes(self):
        for text in ("سمير", "لسمير", "وسمير", "بالسمير"):
            with self.subTest(text=text):
                code, out = self.bundle("[00:10] hi\n", f"قال {text} ذلك.\n", keep_out="سمير\n")
                self.assertEqual(code, 1, out)

    def test_keep_out_ignores_niqqud(self):
        code, out = self.bundle("[00:10] hi\n", "נתתי את זה לְדָנִי אתמול.\n", keep_out="דני\n")
        self.assertEqual(code, 1, out)


class Links(Workspace):
    def check(self):
        return run("links.py", self.root)

    def test_link_with_title_is_checked(self):
        self.write("a.md", '# A\n\nSee [b](missing.md "the b note").\n')
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("missing.md", out)

    def test_link_with_title_that_resolves(self):
        self.write("b.md", "# B\n")
        self.write("a.md", "# A\n\nSee [b](b.md \"the b note\") and [b](b.md 'b').\n")
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_reference_style_link_is_checked(self):
        self.write("a.md", "# A\n\nSee [b][ref].\n\n[ref]: missing.md \"title\"\n")
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("missing.md", out)

    def test_footnote_is_not_a_link(self):
        self.write("a.md", "# A\n\nA claim.[^1]\n\n[^1]: a note, not a path\n")
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_link_inside_inline_code_is_ignored(self):
        self.write("a.md", "# A\n\nWrite links as `[text](path.md)` in notes.\n")
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_every_item_of_a_consumes_block_list(self):
        self.write("data/one.md", "# One\n")
        self.write("p.md", "---\ntype: process\nconsumes:\n  - data/one.md\n  - data/two.md\n---\n# P\n")
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("data/two.md", out)

    def test_graph_carries_access_tier(self):
        self.write("a.md", "---\naccess_tier: private\n---\n# A\n")
        code, out = run("links.py", self.root, "--graph", self.root / "g.jsonl")
        self.assertEqual(code, 0, out)
        rows = [json.loads(x) for x in (self.root / "g.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([r.get("access_tier") for r in rows if "node" in r], ["private"])


class Index(Workspace):
    def index(self):
        code, out = run("index.py", self.root / "notes")
        self.assertEqual(code, 0, out)
        return (self.root / "notes" / "_index.md").read_text(encoding="utf-8")

    def test_empty_status_does_not_take_the_next_line(self):
        self.write("notes/a.md", "---\ntitle: A\nstatus:\ntype: concept\n---\n# A\n")
        self.assertIn("- [A](a.md)\n", self.index())

    def test_folded_description(self):
        self.write("notes/a.md", "---\ntitle: A\ndescription: >\n  first line\n  second line\nstatus: draft\n---\n")
        self.assertIn("- [A](a.md) - first line second line (draft)", self.index())

    def test_hostile_values(self):
        self.write("notes/q.md", "---\ntitle: \"Q&A | 'Test' \\u00d8\"\ndescription: it's # not a comment\n---\n")
        self.assertIn("- [Q&A | 'Test' Ø](q.md) - it's", self.index())


class Viz(Workspace):
    def draw(self):
        code, out = run("links.py", self.root, "--graph", self.root / "g.jsonl")
        self.assertIn(code, (0, 1), out)
        code, out = run("viz.py", self.root / "g.jsonl")
        self.assertEqual(code, 0, out)
        return (self.root / "viz.html").read_text(encoding="utf-8")

    def test_heading_cannot_close_the_script_block(self):
        self.write("AGENTS.md", "# Evil</script><script>alert(1)</script>\n")
        self.write("a.md", "# A\n")
        html = self.draw()
        self.assertNotIn("<script>alert(1)", html)

    def test_body_html_is_sanitized_before_rendering(self):
        self.write("a.md", "# A\n\n<img src=x onerror=alert(1)>\n")
        html = self.draw()
        self.assertIn("DOMPurify.sanitize(marked.parse(", html)
        self.assertNotIn("bodyEl.innerHTML = html;", html)

    def test_cdn_scripts_are_pinned_with_integrity(self):
        html = self.draw()
        scripts = [line for line in html.splitlines() if "<script src=" in line]
        self.assertEqual(len(scripts), 3)
        for line in scripts:
            self.assertIn('integrity="sha384-', line)
            self.assertIn('crossorigin="anonymous"', line)

    def test_private_bodies_are_withheld(self):
        self.write("a.md", "---\naccess_tier: private\n---\n# A\n\nsecret words\n")
        self.write("b.md", "---\naccess_tier: public\n---\n# B\n\nopen words\n")
        html = self.draw()
        self.assertNotIn("secret words", html)
        self.assertIn("open words", html)

    def test_title_names_the_tool(self):
        self.assertNotIn("OKF", self.draw())


if __name__ == "__main__":
    unittest.main()
