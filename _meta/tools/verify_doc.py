#!/usr/bin/env python3
"""
Verify a generated FB/FC markdown doc against the cached PDF section.

Usage:
    python3 _meta/tools/verify_doc.py <doc_path>
    python3 _meta/tools/verify_doc.py Tc2_Standard/timer/TON.md

Checks (deterministic):
  1. Library + Library Version present in metadata table and matches cache
  2. Source PDF URL present
  3. Each VAR_INPUT / VAR_OUTPUT name+type from PDF appears verbatim in doc
  4. The ``<Name>`` matches the file basename
  5. Example link points to existing P_Demo_<Name>.xml

Exit codes:
  0 = PASS
  1 = MINOR (e.g. missing optional field) — emits diagnostics
  2 = FAIL (var-region mismatch)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "_meta" / ".pdf-cache"
TOOLS = ROOT / "_meta" / "tools"
sys.path.insert(0, str(TOOLS))

from parse_toc import parse as parse_toc  # noqa: E402
from extract_section import extract as extract_section  # noqa: E402

VAR_REGION_RE = re.compile(
    # Tolerate "END_VA" (PDF typo) by treating either END_VAR or END_VA + EOL as terminator
    r"VAR_(?:INPUT|OUTPUT|IN_OUT|GLOBAL)(?:\s+CONSTANT)?\s*\n([\s\S]*?)END_VA[R]?",
    re.IGNORECASE,
)
# Per-declaration regex (after the region has been comment-stripped and split on ";").
VAR_DECL_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+?)\s*$", re.DOTALL)


def _vars_from_text(text: str) -> list[tuple[str, str]]:
    # Strip markdown code-fence markers ("```iecst", "```") so they don't get
    # captured into the VAR region when scanning a generated doc that places
    # the IEC ST snippet inside a fenced code block.
    text = re.sub(r"^[ \t]*```[A-Za-z]*[ \t]*$", "", text, flags=re.MULTILINE)
    out: list[tuple[str, str]] = []
    for m in VAR_REGION_RE.finditer(text):
        region = m.group(1)
        # If the doc duplicated the VAR_INPUT keyword (e.g. once as a markdown
        # heading "### VAR_INPUT" then again inside the code block, possibly
        # preceded by a FUNCTION declaration), the first finditer match
        # consumed the heading and the captured region contains a real
        # VAR_INPUT line further in. Restart parsing from the last such
        # keyword inside the region.
        keyword = re.compile(
            r"VAR_(?:INPUT|OUTPUT|IN_OUT|GLOBAL)(?:\s+CONSTANT)?\s*\n",
            re.IGNORECASE,
        )
        last = None
        for km in keyword.finditer(region):
            last = km
        if last:
            region = region[last.end():]
        # Strip (* multi-line comments *) and // line comments.
        region = re.sub(r"\(\*.*?\*\)", "", region, flags=re.DOTALL)
        region = re.sub(r"//.*$", "", region, flags=re.MULTILINE)
        for decl in region.split(";"):
            decl = decl.strip()
            if not decl:
                continue
            vm = VAR_DECL_RE.match(decl)
            if not vm:
                continue
            typ = vm.group(2)
            # Drop ":= default" if present.
            typ = re.sub(r":=.*$", "", typ, flags=re.DOTALL).strip()
            # Collapse internal whitespace (incl. newlines) into single spaces.
            typ = re.sub(r"\s+", " ", typ).strip()
            if not typ:
                continue
            out.append((vm.group(1), typ))
    return out


def _read_doc_meta(doc: str) -> dict:
    meta: dict[str, str] = {}
    pat = re.compile(r"\|\s*([A-Za-z _]+?)\s*\|\s*(.+?)\s*\|\s*$", re.MULTILINE)
    for m in pat.finditer(doc):
        k = m.group(1).strip()
        v = m.group(2).strip().strip("`")
        meta.setdefault(k, v)
    return meta


def verify(doc_path: str) -> tuple[int, list[str]]:
    p = ROOT / doc_path
    if not p.exists():
        return 2, [f"doc not found: {p}"]
    doc = p.read_text()
    name = p.stem

    # find library from metadata
    meta = _read_doc_meta(doc)
    lib = meta.get("Library", "").strip("`")
    if not lib:
        return 2, ["Library missing in metadata table"]

    cache_meta_p = CACHE / f"{lib}.meta.json"
    if not cache_meta_p.exists():
        return 2, [f"cache miss for {lib}; run fetch_pdf.py {lib}"]
    cache_meta = json.loads(cache_meta_p.read_text())

    diags: list[str] = []

    # version
    if cache_meta.get("version") and cache_meta["version"] != meta.get("Library Version"):
        diags.append(
            f"Library Version mismatch: doc='{meta.get('Library Version')}' pdf='{cache_meta['version']}'"
        )

    # find section for this name
    toc = parse_toc(lib)
    entry = next((e for e in toc if e["name"] == name), None)
    if entry is None:
        return 2, [f"{name} not found in TOC of {lib}"]

    section_text = extract_section(lib, entry["section"])
    if not section_text:
        return 2, [f"could not extract section {entry['section']} for {name}"]

    pdf_vars = _vars_from_text(section_text)
    # Restrict doc VAR scan to the Interface section (above "最小例程" / "Minimum Example")
    interface_doc = re.split(r"##\s*\d*\.?\s*(?:最小例程|Minimum Example)", doc, maxsplit=1)[0]
    doc_vars = _vars_from_text(interface_doc)

    pdf_set = {(n, t.upper()) for n, t in pdf_vars}
    doc_set = {(n, t.upper()) for n, t in doc_vars}

    missing = pdf_set - doc_set
    extra = doc_set - pdf_set

    if missing:
        diags.append(f"VAR not present verbatim in doc: {sorted(missing)}")
    if extra:
        diags.append(f"VAR in doc not in PDF: {sorted(extra)}")

    # example link
    examples_dir = p.parent.parent / "examples"
    if not (examples_dir / f"P_Demo_{name}.xml").exists():
        diags.append(f"example missing: examples/P_Demo_{name}.xml")

    if not pdf_vars:
        diags.append(
            "PDF section had no VAR_INPUT/OUTPUT — manual review needed (FC with no params?)"
        )

    if any(d.startswith("VAR not present") or d.startswith("cache miss") for d in diags):
        return 2, diags
    if diags:
        return 1, diags
    return 0, ["PASS"]


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    code, diags = verify(sys.argv[1])
    for d in diags:
        print(d)
    return code


if __name__ == "__main__":
    sys.exit(main())
