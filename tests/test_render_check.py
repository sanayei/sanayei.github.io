import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render_check.sh"


def make_project(d: Path, link: str) -> None:
    (d / "_quarto.yml").write_text("project:\n  type: website\nwebsite:\n  title: t\n")
    (d / "index.qmd").write_text(f"---\ntitle: home\n---\n\nSee [the page]({link}).\n")
    (d / "other.qmd").write_text("---\ntitle: other\n---\n\nHello.\n")


@unittest.skipUnless(shutil.which("quarto"), "quarto not installed")
class RenderCheckTests(unittest.TestCase):
    def run_on(self, link: str) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as tmp:
            make_project(Path(tmp), link)
            return subprocess.run(["bash", str(SCRIPT), tmp], capture_output=True, text=True)

    def test_valid_internal_link_passes(self):
        self.assertEqual(self.run_on("other.qmd").returncode, 0)

    def test_broken_internal_link_fails(self):
        r = self.run_on("missing.qmd")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("broken internal link", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
