#!/usr/bin/env python3
"""
Parse the Table of Contents from a cached Beckhoff PDF and emit JSON entries.

Usage:
    python3 _meta/tools/parse_toc.py <Library_Name>

Each entry: {"section": "3.1.1", "name": "RS", "page": 9, "category": "Bistable",
              "type": "FB|FC", "depth": 3}

Heuristics (deterministic):
  - Reads cached <Library>.txt produced by fetch_pdf.py
  - Restricts parse to the "Table of contents" page span (between
    "Table of contents" header and the first non-TOC page break)
  - A TOC line matches: <section> <Name> <leader/dots> <page>
  - Top-level group "Function blocks" -> children type=FB
  - Top-level group "Functions"       -> children type=FC
  - "Functions for ..." also -> FC
  - Category = title of the depth-2 section (e.g. "3.1 Bistable" -> "Bistable")
  - Leaf entries are depth-3 (e.g. 3.1.1 RS)
  - Some libs have flat depth-2 leaves; fall back to depth-2 with category=group
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "_meta" / ".pdf-cache"

GROUP_TYPE = {
    "Function blocks": "FB",
    "Functions": "FC",
}

LINE_RE = re.compile(
    r"^(?P<sec>\d+(?:\.\d+){0,3})\s+(?P<title>.+?)\s+\.{2,}\s*(?P<page>\d+)\s*$"
)
# Some PDFs render TOC without dot leader but with trailing page number
LINE_RE_FALLBACK = re.compile(
    r"^(?P<sec>\d+(?:\.\d+){0,3})\s+(?P<title>.+?)\s{2,}(?P<page>\d+)\s*$"
)


def _toc_text(full: str) -> str:
    """Return the table-of-contents region of the cached PDF text.

    TOC entries end with a dot leader and a page number. The body of the
    document does NOT have that pattern, so we walk forward from "Table of
    contents" line by line and stop at the first non-blank line that doesn't
    look like a TOC entry (or a page-break artifact).
    """
    start = full.find("Table of contents")
    if start < 0:
        return full
    rest = full[start:]

    # A TOC line either matches the dot-leader pattern, or is a page-break
    # artifact ("=== PAGE N ===", "Table of contents", "TE...Version:..."),
    # or is blank.
    toc_line = re.compile(
        r"^(?:"
        r"\s*\d+(?:\.\d+){0,3}\s+.+?\s+\.{2,}\s*\d+\s*"  # "3.1 Name ......  9"
        r"|=== PAGE \d+ ==="
        r"|Table of contents"
        r"|TE\d+\s+\d+(?:\s*Version:.*)?"
        r"|TE\d+\s*Version:.*"
        r"|\s*"  # blank
        r")$"
    )
    end_offset = len(rest)
    consec_non_toc = 0
    pos = 0
    for line in rest.splitlines(keepends=True):
        if toc_line.match(line.rstrip("\n")):
            consec_non_toc = 0
        else:
            consec_non_toc += 1
            if consec_non_toc >= 2:
                # Two consecutive non-TOC lines → we've left the TOC.
                end_offset = pos
                break
        pos += len(line)
    return rest[:end_offset]


def parse(lib: str) -> list[dict]:
    txt = CACHE / f"{lib}.txt"
    if not txt.exists():
        raise SystemExit(f"cache miss: run fetch_pdf.py {lib} first")
    body = _toc_text(txt.read_text())

    entries: list[dict] = []
    current_group: str | None = None
    current_group_kind: str | None = None  # "FB" or "FC"
    current_category: str | None = None
    pending_depth2_as_category = False

    def classify_group(title: str) -> str | None:
        t = title.lower()
        if "function block" in t:
            return "FB"
        if "function" in t:
            return "FC"
        if "global constant" in t or "constants" in t:
            return "GVL"
        return None

    # First pass: detect whether a depth-2 entry under the current chapter is
    # itself a leaf (no depth-3 children) by looking at the next non-blank TOC
    # line. We approximate via two-pass over collected matches.
    matches: list[tuple[str, str, int]] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = LINE_RE.match(line) or LINE_RE_FALLBACK.match(line)
        if not m:
            continue
        matches.append((m.group("sec"), m.group("title").strip(), int(m.group("page"))))

    # Build set of section prefixes that have children (i.e. someone has section "X.Y.Z")
    has_children: set[str] = set()
    for sec, _, _ in matches:
        parts = sec.split(".")
        for k in range(1, len(parts)):
            has_children.add(".".join(parts[:k]))

    def looks_like_leaf_name(title: str) -> bool:
        # leaf POU / global constant names: single token of [A-Za-z_][A-Za-z0-9_]*
        return bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", title))

    # Some PDFs render the global constant section title as a category label
    # ("Library version") with the actual constant name inside the section body.
    # Detect: depth-2 leaf under a GVL group whose title isn't a valid identifier
    # — fall back to scanning the section body for the first VAR_GLOBAL line.
    def gvl_constant_in_section(section: str) -> str | None:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        try:
            from extract_section import extract as _extract
        except Exception:
            return None
        body = _extract(lib, section)
        if not body:
            return None
        m = re.search(
            r"VAR_GLOBAL\s+(?:CONSTANT\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*:",
            body,
        )
        return m.group(1) if m else None

    for sec, title, page in matches:
        depth = sec.count(".") + 1

        if depth == 1:
            current_group = title
            current_group_kind = classify_group(title)
            current_category = None
            continue

        if current_group_kind is None:
            continue

        if depth == 2:
            # leaf if no depth-3 children AND name looks like a POU
            if sec not in has_children and looks_like_leaf_name(title):
                entries.append(
                    {
                        "section": sec,
                        "name": title,
                        "type": current_group_kind,
                        "category": current_group,
                        "page": page,
                        "depth": depth,
                    }
                )
            elif sec not in has_children and current_group_kind == "GVL":
                # Title is a category label (e.g. "Library version"); the actual
                # constant identifier lives in the section body.
                name = gvl_constant_in_section(sec)
                if name:
                    entries.append(
                        {
                            "section": sec,
                            "name": name,
                            "type": "GVL",
                            "category": title,
                            "page": page,
                            "depth": depth,
                        }
                    )
                else:
                    current_category = title
            else:
                current_category = title
            continue

        if depth >= 3:
            if not looks_like_leaf_name(title):
                continue
            entries.append(
                {
                    "section": sec,
                    "name": title,
                    "type": current_group_kind,
                    "category": current_category or current_group,
                    "page": page,
                    "depth": depth,
                }
            )

    return entries


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    print(json.dumps(parse(sys.argv[1]), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
