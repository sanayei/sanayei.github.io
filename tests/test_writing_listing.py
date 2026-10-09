import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ENTRY = """---
title: "{title}"
date: {date}
description: "{title} description"
categories: [{cat}]
{extra}
---

Body of {title}.
"""


@unittest.skipUnless(shutil.which("quarto"), "quarto not installed")
class WritingListingTests(unittest.TestCase):
    """Render a copy of the site with sample entries and inspect the output."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.site = Path(self.tmp.name) / "site"
        shutil.copytree(ROOT, self.site, ignore=shutil.ignore_patterns("_site", ".quarto", ".git", "_freeze"))
        w = self.site / "writing"
        for slug, title, cat, extra in [
            ("e1", "Sample Essay", "essay", ""),
            ("n1", "Sample Note", "note", ""),
            ("d1", "Hidden Draft", "note", "draft: true"),
        ]:
            (w / slug).mkdir()
            (w / slug / "index.qmd").write_text(ENTRY.format(title=title, date="2026-10-01", cat=cat, extra=extra))
        r = subprocess.run(["quarto", "render", str(self.site)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        self.out = self.site / "_site" / "writing"

    def tearDown(self):
        self.tmp.cleanup()

    def test_listing_shows_both_kinds_with_filters(self):
        html = (self.out / "index.html").read_text()
        self.assertIn("Sample Essay", html)
        self.assertIn("Sample Note", html)
        self.assertIn("essay", html)
        self.assertIn("note", html)
        self.assertIn("quarto-listing-category", html)

    def test_feed_contains_published_entries_only(self):
        feed = (self.out / "index.xml").read_text()
        self.assertIn("Sample Essay", feed)
        self.assertIn("Sample Note", feed)
        self.assertNotIn("Hidden Draft", feed)

    def test_drafts_and_template_never_listed(self):
        html = (self.out / "index.html").read_text()
        self.assertNotIn("Hidden Draft", html)
        self.assertNotIn("Entry title", html)  # the template's title
        self.assertFalse((self.out / "_template").exists())


if __name__ == "__main__":
    unittest.main()
