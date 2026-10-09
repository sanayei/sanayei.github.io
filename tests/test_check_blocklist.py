import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_blocklist.py"
sys.path.insert(0, str(ROOT / "scripts"))
import check_blocklist  # noqa: E402


def run(root: Path, blocklist: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--blocklist", str(blocklist)],
                          capture_output=True, text=True)


class BlocklistTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.site = self.dir / "site"
        self.site.mkdir()
        self.bl = self.dir / "blocklist.yaml"
        self.bl.write_text('# comment\nterms:\n  - Acme Corp\n  - "Secret Project"\n')

    def tearDown(self):
        self.tmp.cleanup()

    def test_load_terms_reads_plain_and_quoted_items(self):
        self.assertEqual(check_blocklist.load_terms(self.bl), ["Acme Corp", "Secret Project"])

    def test_clean_site_exits_0(self):
        (self.site / "about.qmd").write_text("Nothing to see.\n")
        self.assertEqual(run(self.site, self.bl).returncode, 0)

    def test_match_in_body_is_case_insensitive_and_reported(self):
        (self.site / "about.qmd").write_text("line one\nI worked at ACME corp.\n")
        r = run(self.site, self.bl)
        self.assertEqual(r.returncode, 1)
        self.assertIn("about.qmd:2: Acme Corp", r.stdout)

    def test_match_in_front_matter_yml_and_bib_is_caught(self):
        (self.site / "post.qmd").write_text('---\ntitle: "On the Secret Project"\n---\nbody\n')
        (self.site / "_quarto.yml").write_text("description: fine\n")
        (self.site / "refs.bib").write_text("@misc{x, title={Acme Corp report}}\n")
        r = run(self.site, self.bl)
        self.assertEqual(r.returncode, 1)
        self.assertIn("post.qmd:2: Secret Project", r.stdout)
        self.assertIn("refs.bib:1: Acme Corp", r.stdout)

    def test_build_and_vcs_dirs_are_skipped(self):
        for d in ("_site", "_freeze", ".git", ".quarto"):
            (self.site / d).mkdir()
            (self.site / d / "x.md").write_text("Acme Corp\n")
        self.assertEqual(run(self.site, self.bl).returncode, 0)

    def test_missing_blocklist_exits_2(self):
        r = run(self.site, self.dir / "nope.yaml")
        self.assertEqual(r.returncode, 2)
        self.assertIn("blocklist not found", r.stderr)

    def test_empty_blocklist_exits_2(self):
        self.bl.write_text("terms:\n")
        r = run(self.site, self.bl)
        self.assertEqual(r.returncode, 2)
        self.assertIn("no terms", r.stderr)


if __name__ == "__main__":
    unittest.main()
