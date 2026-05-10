#!/usr/bin/env python3
"""
Extract the body text of a specific section from a cached Beckhoff PDF.

Usage:
    python3 _meta/tools/extract_section.py <Library_Name> <section_number>
    python3 _meta/tools/extract_section.py Tc2_Standard 3.1.1

The body runs from the heading line "<section> <title>" until the next heading
of the same or shallower depth (or end of document).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "_meta" / ".pdf-cache"


def extract(lib: str, section: str) -> str:
    txt = CACHE / f"{lib}.txt"
    if not txt.exists():
        raise SystemExit(f"cache miss: run fetch_pdf.py {lib} first")
    full = txt.read_text()

    # Drop TOC region — find first body chapter heading after TOC.
    # TOC entries are recognizable by trailing "...   <page>"; body headings are not.
    # Strategy: take text from second occurrence of the requested section heading.
    sec_re = re.compile(rf"(?m)^\s*{re.escape(section)}\s+[A-Za-z][^\.\n]{{0,80}}$")
    matches = [m.start() for m in sec_re.finditer(full)]
    if not matches:
        # also try with TOC dot leaders stripped
        cleaned = re.sub(r"\.{2,}\s*\d+\s*$", "", full, flags=re.MULTILINE)
        matches = [m.start() for m in sec_re.finditer(cleaned)]
        if not matches:
            return ""
        full = cleaned

    # Pick the *last* match — TOC entries come first, body comes later.
    start = matches[-1]

    # Find next heading of same/shallower depth.
    depth = section.count(".") + 1
    parts = section.split(".")
    # Build regex for any same-or-shallower-depth heading following.
    depth_alts = []
    for d in range(1, depth + 1):
        depth_alts.append(r"\d+" + (r"\.\d+" * (d - 1)))
    # Also any chapter at depth 1 (e.g. moving from 3.1.1 to 4)
    next_heading = re.compile(
        r"(?m)^\s*(?:" + "|".join(depth_alts) + r")\s+[A-Z][^\.\n]{0,80}$"
    )
    after = full[start + 1 :]
    nm = next_heading.search(after)
    end = (start + 1 + nm.start()) if nm else len(full)
    return full[start:end].rstrip()


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 1
    lib, section = sys.argv[1], sys.argv[2]
    out = extract(lib, section)
    if not out:
        print(f"<no match for section {section}>", file=sys.stderr)
        return 2
    sys.stdout.write(out)
    return 0


# Re-export with NBSP normalization so callers don't need to handle pypdf's
# \xa0 quirk.
_orig_extract = extract


def extract(lib: str, section: str) -> str:  # type: ignore[no-redef]
    out = _orig_extract(lib, section)
    return out.replace("\xa0", " ")


if __name__ == "__main__":
    sys.exit(main())
