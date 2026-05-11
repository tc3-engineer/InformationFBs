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
    # Allow any identifier-like first character (uppercase or lowercase letter,
    # digit, underscore) — Beckhoff uses some lowercase-first POU names like
    # "sLiteral_TO_UTF8" and "wsLiteral_TO_UTF8".
    # Disallow `:` `,` `.` in the title to avoid matching descriptive lines
    # such as "100 ms pulse (zero): min: 70 ms, typical: 95 ms" inside body
    # text — real Beckhoff section titles are POU names or short category
    # phrases without those punctuation marks.
    next_heading = re.compile(
        r"(?m)^\s*(?:" + "|".join(depth_alts) + r")\s+[A-Za-z_][^.:,\n]{0,80}$"
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


# Beckhoff PDF footers come in two layouts that pypdf preserves verbatim:
#   "TE1000 11Version: 1.3.4"   (page number is a separate token)
#   "TE100010 Version: 1.1.1"   (page number is concatenated into TE<n><pg>)
# Either pattern is the discriminator we trust to identify a real page-break
# artifact. We only consume an optional preceding short chapter-title line
# when this Version line is actually present — otherwise we'd risk eating
# real body content (e.g. the first declaration of a VAR_INPUT block).
_VERSION_LINE = r"TE\d+\s+(?:\d+\s*)?Version:\s*[\d.]+\n"
# Form A: "=== PAGE N ===" marker + optional chapter title + Version line.
_PAGE_HEADER_WITH_MARKER_RE = re.compile(
    r"\n?=== PAGE \d+ ===\n"
    r"(?:[^\n]{1,80}\n)?"
    + _VERSION_LINE,
)
# Form B: bare "<chapter title>\nTE...Version:..." with no marker (pypdf
# sometimes drops the marker but keeps the header text in mid-section).
_PAGE_HEADER_BARE_RE = re.compile(
    r"\n([A-Za-z][^\n]{0,80})\n" + _VERSION_LINE,
)
# Fallback: a stray "=== PAGE N ===" marker on its own — drop just the
# marker so surrounding text stays intact.
_PAGE_MARKER_RE = re.compile(r"\n?=== PAGE \d+ ===\n")


_INLINE_METHOD_HEADER = re.compile(
    r"(?m)^[ \t]+Methods\s+([A-Za-z_]\w*)\s*\(\s*\)"
)


def _extract_inline_method(parent_body: str, method_name: str) -> str:
    """Slice parent_body to the chunk for a single inline method.

    Range = from the matching " Methods <name>()" header up to the next
    inline method header OR the "Requirements" / next major heading.
    """
    starts: list[tuple[str, int, int]] = []
    for mm in _INLINE_METHOD_HEADER.finditer(parent_body):
        starts.append((mm.group(1), mm.start(), mm.end()))
    if not starts:
        return ""
    idx = next((i for i, s in enumerate(starts) if s[0] == method_name), -1)
    if idx < 0:
        return ""
    start = starts[idx][1]
    if idx + 1 < len(starts):
        end = starts[idx + 1][1]
    else:
        # cut at "Requirements" or first all-uppercase section-like line
        rest = parent_body[start:]
        rm = re.search(r"(?m)^Requirements\s*$", rest)
        end = (start + rm.start()) if rm else len(parent_body)
    return parent_body[start:end].rstrip()


def extract(lib: str, section: str) -> str:  # type: ignore[no-redef]
    # Synthetic id "<parent_section>#mN" or "<parent_section>#<method_name>"
    if "#" in section:
        parent_sec, _, marker = section.partition("#")
        parent = _orig_extract(lib, parent_sec)
        parent = parent.replace("\xa0", " ")
        parent = _PAGE_HEADER_WITH_MARKER_RE.sub("\n", parent)
        parent = _PAGE_HEADER_BARE_RE.sub("\n", parent)
        parent = _PAGE_MARKER_RE.sub("\n", parent)
        # marker is "mN" (index) or a method name
        if marker.startswith("m") and marker[1:].isdigit():
            idx = int(marker[1:]) - 1
            names: list[str] = []
            for mm in _INLINE_METHOD_HEADER.finditer(parent):
                if mm.group(1) not in names:
                    names.append(mm.group(1))
            if 0 <= idx < len(names):
                return _extract_inline_method(parent, names[idx])
            return ""
        return _extract_inline_method(parent, marker)

    out = _orig_extract(lib, section)
    out = out.replace("\xa0", " ")
    out = _PAGE_HEADER_WITH_MARKER_RE.sub("\n", out)
    out = _PAGE_HEADER_BARE_RE.sub("\n", out)
    out = _PAGE_MARKER_RE.sub("\n", out)
    return out


if __name__ == "__main__":
    sys.exit(main())
