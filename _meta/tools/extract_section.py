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


def _ge_pattern(n: int) -> str:
    """Regex fragment matching a positive integer >= n.

    Used by extract_section's next-heading scan to enforce monotonic section
    numbering: a "next section" candidate at depth d may only have a d-th
    number >= current_section[d-1] + 1 (siblings) or, for shallower ancestors,
    >= the corresponding part. Anything smaller is a false match (prose row
    "1 …" inside a 4.3 body etc.).
    """
    if n <= 1:
        return r"\d+"
    s = str(n)
    L = len(s)
    parts: list[str] = [rf"\d{{{L + 1},}}"]  # more digits → strictly larger
    for i, ch in enumerate(s):
        d = int(ch)
        if d == 9:
            if i == L - 1:
                parts.append(s)
            continue
        head = re.escape(s[:i])
        lo = d + 1 if i < L - 1 else d
        tail_len = L - i - 1
        tail = rf"\d{{{tail_len}}}" if tail_len else ""
        parts.append(rf"{head}[{lo}-9]{tail}")
    return "(?:" + "|".join(parts) + ")"


def extract(lib: str, section: str) -> str:
    txt = CACHE / f"{lib}.txt"
    if not txt.exists():
        raise SystemExit(f"cache miss: run fetch_pdf.py {lib} first")
    full = txt.read_text()

    # Drop TOC region — find first body chapter heading after TOC.
    # TOC entries are recognizable by trailing "...   <page>"; body headings are not.
    # Strategy: take text from second occurrence of the requested section heading.
    # Title may start with a letter, digit or underscore: most POUs start with a
    # letter, but a few Beckhoff FBs are named with a leading digit (Tc2_SerialCom
    # §5.1.4.1 "3964R"). Requiring a letter-start dropped those entirely.
    sec_re = re.compile(rf"(?m)^\s*{re.escape(section)}\s+[A-Za-z0-9_][^\.\n]{{0,80}}$")
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

    # Find next heading of same/shallower depth. Title rules differ by depth to
    # avoid matching prose lines that happen to begin with a number:
    #   depth-1 chapter ("6 Examples", "8 Support and Service"): title MUST start
    #     with an uppercase letter. Real Beckhoff chapter titles are always
    #     capitalized, so this excludes numeric-prose lines like "7 or 8" (a
    #     parameter-value description that was truncating Tc2_SerialCom
    #     KL6Configuration before its VAR_OUTPUT block).
    #   depth>=2 ("5.1.4 3964R + RK512 protocols", "5.4.1 sLiteral_TO_UTF8"):
    #     title may start with letter/digit/underscore so digit-leading POU names
    #     ("3964R") and lowercase-first FCs are still recognized as boundaries.
    # Disallow `:` `,` `.` in the title to avoid matching descriptive lines such
    # as "100 ms pulse (zero): min: 70 ms, typical: 95 ms".
    # Section numbers are monotonic so the leading number at each depth-d
    # candidate must be >= the current section's d-th number (strict > for the
    # full path means "next section"). Stops "Prio Description Conditions
    # Comments\n1 Synchronization via\nbSync" inside Tc3_BA2_Common
    # FB_BA_PIDCtrl §4.3.2.1.1 from looking like a fresh chapter-1 boundary.
    parts = [int(p) for p in section.split(".")]
    depth = len(parts)
    alts = []
    for d in range(1, depth + 1):
        # For depth-d candidate, the first d-1 number parts must match the
        # current section's prefix exactly, and the d-th part must be >= the
        # current section's d-th part + (1 if d == depth else 0) — siblings at
        # depth-d, deeper-numbered ancestors at d < depth.
        head_lit = "".join(rf"{p}\." for p in parts[: d - 1])
        min_n = parts[d - 1] + (1 if d == depth else 1)
        num = head_lit + _ge_pattern(min_n)
        # Depth-1 chapter titles are short in real Beckhoff manuals (Foreword /
        # Introduction / Programming / Support and Service / Appendix etc., all
        # <= ~25 chars). Capping at 30 rejects prose-row matches that share a
        # leading number, e.g. Tc3_BA2_Common FB_BA_PIDCtrl's "Prio Description"
        # table row "5 Anti-Reset-Windup Controller enabled - bEn" (41 chars).
        # Depth >= 2 titles can be long POU names (Tc2_MC2_Drive has 41-char
        # FB_SoEAX5000ReadActMainVoltage_ByDriveRef) so the 80-char bound stays.
        title = r"[A-Z][^.:,\n]{0,30}" if d == 1 else r"[A-Za-z0-9_][^.:,\n]{0,80}"
        alts.append(num + r"\s+" + title)
    next_heading = re.compile(r"(?m)^\s*(?:" + "|".join(alts) + r")$")
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
# Beckhoff PDFs use several page-header prefixes:
#   "TE<digits>"  — Tc2_* / Tc3_* libraries (most TwinCAT 3 standard libs)
#   "TF<digits>"  — TF product manuals (e.g. Tc2_TcpIp = TF6310; the
#                   number+page often concatenates as "TF6310 3" or "TF631032")
_VERSION_LINE = r"T[EFS]\d+\s*(?:\d+\s*)?Version:\s*[\d.]+\n"
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
