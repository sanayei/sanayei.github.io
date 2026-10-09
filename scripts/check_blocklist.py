#!/usr/bin/env python3
"""Fail if any site source file contains a blocklisted term.

The blocklist is private (employer names, internal terms, unpublished paper
titles) and lives outside this repo. Runs as a git pre-push hook; never in CI.
Exit codes: 0 clean, 1 matches found, 2 blocklist missing or empty.
"""
import argparse
import os
import sys
from pathlib import Path

DEFAULT_BLOCKLIST = Path.home() / "projects/content-engine/config/blocklist.yaml"
SUFFIXES = {".qmd", ".md", ".yml", ".yaml", ".bib"}
SKIP_DIRS = {"_site", "_freeze", ".git", ".quarto", "__pycache__"}


def load_terms(path: Path) -> list[str]:
    terms = []
    for line in path.read_text().splitlines():
        s = line.strip()
        if s.startswith("- "):
            term = s[2:].strip().strip("\"'")
            if term:
                terms.append(term)
    return terms


def scan(root: Path, terms: list[str]) -> list[tuple[Path, int, str]]:
    lowered = [(t, t.lower()) for t in terms]
    hits = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in SUFFIXES:
            continue
        if SKIP_DIRS.intersection(path.relative_to(root).parts):
            continue
        for n, line in enumerate(path.read_text(errors="replace").splitlines(), start=1):
            low = line.lower()
            hits.extend((path.relative_to(root), n, t) for t, tl in lowered if tl in low)
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--blocklist", type=Path,
                    default=Path(os.environ.get("BLOCKLIST_PATH", DEFAULT_BLOCKLIST)))
    args = ap.parse_args()
    if not args.blocklist.is_file():
        print(f"blocklist not found: {args.blocklist} (set BLOCKLIST_PATH)", file=sys.stderr)
        return 2
    terms = load_terms(args.blocklist)
    if not terms:
        print(f"blocklist has no terms: {args.blocklist}", file=sys.stderr)
        return 2
    hits = scan(args.root, terms)
    for path, n, term in hits:
        print(f"{path}:{n}: {term}")
    if hits:
        print(f"blocklist check failed: {len(hits)} match(es)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
