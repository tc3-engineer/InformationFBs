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
    document does NOT have that pattern, so we walk forward from a "Table of
    contents" line by line and stop at the first run of non-blank lines that
    don't look like a TOC entry (or a page-break artifact).

    A PDF often prints "Table of contents" more than once (e.g. as a running
    header on every TOC page, plus once in the body). The first occurrence is
    not necessarily the real TOC — on some TF product manuals (e.g. ModbusRTU)
    the first hit is a header with nothing parseable after it, which truncated
    the region to a few characters. So we evaluate EVERY occurrence and keep the
    region that yields the most TOC-shaped lines.
    """
    # A TOC line either matches one of the entry shapes also accepted by
    # parse() below (LINE_RE / LINE_RE_FALLBACK — both with and without a dot
    # leader), or is a page-break artifact ("=== PAGE N ===", "Table of
    # contents", "TE...Version:..."), or is blank. Any TOC entry shape we
    # accept here MUST be accepted there, otherwise parse() can't see it
    # anyway.
    toc_line = re.compile(
        r"^(?:"
        r"\s*\d+(?:\.\d+){0,3}\s+.+?\s+\.{2,}\s*\d+\s*"  # "3.1 Name ......  9"
        r"|\s*\d+(?:\.\d+){0,3}\s+.+?\s{2,}\d+\s*"        # "3.1 Name      9" (no dot leader)
        r"|=== PAGE \d+ ==="
        r"|Table of contents"
        r"|TE\d+\s+\d+(?:\s*Version:.*)?"
        r"|TE\d+\s*Version:.*"
        r"|\s*"  # blank
        r")$"
    )
    entry_line = re.compile(
        r"^\s*\d+(?:\.\d+){0,3}\s+.+?(?:\s+\.{2,}\s*|\s{2,})\d+\s*$"
    )

    def region_from(start: int) -> str:
        rest = full[start:]
        end_offset = len(rest)
        consec_non_toc = 0
        pos = 0
        for line in rest.splitlines(keepends=True):
            if toc_line.match(line.rstrip("\n")):
                consec_non_toc = 0
            else:
                consec_non_toc += 1
                if consec_non_toc >= 2:
                    end_offset = pos
                    break
            pos += len(line)
        return rest[:end_offset]

    # Collect every "Table of contents" occurrence; score each region by the
    # number of real TOC entry lines it contains and keep the richest one.
    best = ""
    best_score = -1
    idx = full.find("Table of contents")
    if idx < 0:
        return full
    while idx >= 0:
        region = region_from(idx)
        score = sum(1 for ln in region.splitlines() if entry_line.match(ln))
        if score > best_score:
            best_score = score
            best = region
        idx = full.find("Table of contents", idx + 1)
    return best



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

    # OO parent FB detection: a depth-2 entry whose own body (before the first
    # depth-3 child heading) contains a recognizable FB declaration. Two
    # signals work in practice:
    #   1. "FUNCTION_BLOCK <Name>"      (explicit declaration; with or without EXTENDS)
    #   2. " Methods\n" + a methods table (parent FB with method children)
    # Plain category sections like "3.1 Bistable" in Tc2_Standard match neither.
    # TF product manuals (e.g. TF5055 Tc2_MC2_FlyingSaw) put the API under
    # plain depth-1 chapters ("Flying saw", "Data types") that classify_group
    # can't recognize, so current_group_kind stays None and every depth-2 leaf
    # is dropped. Recover those by inspecting the section body: an FB declares
    # "FUNCTION_BLOCK <Name>", a DUT declares "TYPE <Name> :", a function
    # declares "FUNCTION <Name>". Deterministic and body-gated, so plain
    # category sections (Tc2_Standard "3.1 Bistable") never match.
    def section_pou_kind(section: str, title: str) -> str | None:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        try:
            from extract_section import extract as _extract
        except Exception:
            return None
        body = _extract(lib, section)
        if not body:
            return None
        if re.search(rf"\bFUNCTION_BLOCK\s+{re.escape(title)}\b", body):
            return "FB"
        if re.search(rf"\bTYPE\s+{re.escape(title)}\s*:", body):
            return "DUT"
        if re.search(rf"\bFUNCTION\s+{re.escape(title)}\b", body):
            return "FC"
        # TF NC manuals (e.g. TF5055) print MC_* FBs without an explicit
        # FUNCTION_BLOCK declaration — the body opens with the prose
        # "The function block <Name> ...". Use that as an FB signal.
        if re.search(rf"\bfunction block\s+{re.escape(title)}\b", body, re.IGNORECASE):
            return "FB"
        return None

    def section_is_oo_parent(section: str, title: str) -> bool:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        try:
            from extract_section import extract as _extract
        except Exception:
            return False
        body = _extract(lib, section)
        if not body:
            return False
        # Cut at first depth-3 child heading.
        child_pat = re.compile(rf"^\s*{re.escape(section)}\.\d+\s+\w+", re.MULTILINE)
        cm = child_pat.search(body)
        own_body = body[: cm.start()] if cm else body
        # Signal 1: explicit FUNCTION_BLOCK declaration with the section title.
        if re.search(rf"\bFUNCTION_BLOCK\s+{re.escape(title)}\b", own_body):
            return True
        # Signal 2: parent has a "Methods" table heading.
        if re.search(r"^\s*Methods\s*$", own_body, re.MULTILINE):
            return True
        return False

    for sec, title, page in matches:
        depth = sec.count(".") + 1

        if depth == 1:
            current_group = title
            current_group_kind = classify_group(title)
            current_category = None
            continue

        # Some PDFs (notably TF product manuals like Tc2_TcpIp's TF6310 doc) put
        # the "PLC API" chapter at depth-1 and split into "Function blocks" /
        # "Functions" / "Global constants" at depth-2. In that layout the
        # depth-2 entries themselves are group labels (with depth-3 leaves).
        # Promote them to group_kind here. Also re-detect at depth-2 transitions
        # (FB → FC etc.) within the same chapter.
        if depth == 2:
            gk = classify_group(title)
            if gk is not None and "data type" not in title.lower():
                current_group = title
                current_group_kind = gk
                current_category = title
                continue
            # "Data types" depth-2 chapter — skip its depth-3 children entirely
            if "data type" in title.lower():
                current_group_kind = None
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
            elif (
                sec in has_children
                and looks_like_leaf_name(title)
                and current_group_kind == "FB"
                and section_is_oo_parent(sec, title)
            ):
                # OO parent FB: emit it as its own entry and use its title as
                # the category for child methods.
                entries.append(
                    {
                        "section": sec,
                        "name": title,
                        "type": "FB",
                        "category": current_group,
                        "page": page,
                        "depth": depth,
                        "is_parent": True,
                    }
                )
                current_category = title
            else:
                current_category = title
            continue

        if depth >= 3:
            if not looks_like_leaf_name(title):
                # Special case: GVL group at depth-3 with a category-label title
                # (e.g. Tc2_TcpIp §5.4.1 "Library version"). The actual constant
                # identifier lives in the section body — recover it.
                if current_group_kind == "GVL":
                    nm = gvl_constant_in_section(sec)
                    if nm:
                        entries.append(
                            {
                                "section": sec,
                                "name": nm,
                                "type": "GVL",
                                "category": current_category or current_group,
                                "page": page,
                                "depth": depth,
                            }
                        )
                continue
            # If under an OO parent, mark child as method.
            entry_type = current_group_kind
            entries.append(
                {
                    "section": sec,
                    "name": title,
                    "type": entry_type,
                    "category": current_category or current_group,
                    "page": page,
                    "depth": depth,
                }
            )

    # Inline-method discovery: some Beckhoff PDFs render an FB parent's methods
    # inline in the same TOC section instead of giving each method its own
    # depth-3 entry (e.g. Tc2_Utilities FB_CalcHashValue §3.10 has start/
    # update/finish as inline " Methods <name>()" headers + "METHOD <name> :
    # <ret>" declarations). Promote such depth-2 FB entries to is_parent and
    # synthesise virtual depth-3 child entries so verify_doc can match them.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from extract_section import extract as _extract
    except Exception:
        _extract = None
    if _extract is not None:
        synthetic: list[dict] = []
        for e in entries:
            if e.get("depth") != 2 or e.get("type") != "FB":
                continue
            if e.get("is_parent"):
                continue
            body = _extract(lib, e["section"])
            if not body:
                continue
            # Look for inline " Methods <name>()" headers — the leading space
            # disambiguates from "Inputs / Outputs" tables and from a plain
            # "Methods" table heading (already handled in section_is_oo_parent).
            method_names: list[str] = []
            seen: set[str] = set()
            for mm in re.finditer(
                r"(?m)^[ \t]+Methods\s+([A-Za-z_]\w*)\s*\(\s*\)", body
            ):
                nm = mm.group(1)
                if nm in seen:
                    continue
                seen.add(nm)
                method_names.append(nm)
            if not method_names:
                continue
            # Promote parent
            e["is_parent"] = True
            e["inline_methods"] = True
            # Build virtual section ids: parent.section + ".m1", ".m2"... so
            # parse_toc consumers know these are synthetic.
            for idx, mn in enumerate(method_names, start=1):
                synthetic.append(
                    {
                        "section": f"{e['section']}#m{idx}",
                        "name": mn,
                        "type": "FB",
                        "category": e["name"],
                        "page": e["page"],
                        "depth": 3,
                        "parent_section": e["section"],
                        "inline_method": True,
                    }
                )
        entries.extend(synthetic)

    # TF-manual fallback: some TwinCAT function-product manuals (e.g. TF5055
    # Tc2_MC2_FlyingSaw) organize the API under plain depth-1 chapters
    # ("Flying saw", "Data types") that classify_group can't recognize, so the
    # normal pass yields nothing. Only when that happens, re-scan every depth-2
    # leaf and keep the ones whose section body declares a real FB / DUT / FC.
    # Gated on "entries empty" so libraries that classify groups normally are
    # never affected.
    if not entries:
        chapter_title = ""
        for sec, title, page in matches:
            depth = sec.count(".") + 1
            if depth == 1:
                chapter_title = title
                continue
            if depth != 2 or sec in has_children or not looks_like_leaf_name(title):
                continue
            kind = section_pou_kind(sec, title)
            if kind is not None:
                entries.append(
                    {
                        "section": sec,
                        "name": title,
                        "type": kind,
                        "category": chapter_title,
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
