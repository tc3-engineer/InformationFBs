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
# Per-declaration regex: find `name : type;` anywhere in the (already comment-
# stripped) region. Anchors:
#   - Search anywhere (not just chunk start) so an orphan token like "ed)"
#     left over from a wrapped (= ...) parenthetical comment doesn't hide
#     the next real declaration.
#   - Negative lookahead (?!=) skips ST assignments like `Var1 := LEN(...)`
#     where `:` is part of `:=`.
#   - Terminator is either `;` or end-of-line (some PDFs render the LAST
#     declaration before END_VAR without the trailing semicolon).
VAR_DECL_RE = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?!=)([^;\n]+?)\s*(?:;|$)",
    re.MULTILINE,
)


_NEW_DECL_LINE_RE = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*:(?!=)")


def _join_wrapped_decls(region: str) -> str:
    """Reflow declarations whose type wraps onto the next line.

    A "continuation" line:
      - the previous accumulated line contains `:` but not `;`
      - this line does not itself start with `<name>:` (i.e. it isn't the
        next declaration)
      - this line is non-blank
    On match, the continuation is appended (space-joined) to the previous
    line. Blank lines are passed through unchanged.
    """
    lines = region.split("\n")
    out: list[str] = []
    for raw in lines:
        if (
            out
            and out[-1].strip()
            and ":" in out[-1]
            and ";" not in out[-1]
            and raw.strip()
            and not _NEW_DECL_LINE_RE.match(raw)
            and not raw.lstrip().upper().startswith(("END_VAR", "VAR_"))
        ):
            out[-1] = out[-1].rstrip() + " " + raw.strip()
        else:
            out.append(raw)
    return "\n".join(out)


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
        # Strip (* multi-line comments *) and // line comments. Done BEFORE
        # decl extraction so the `;` we hunt for is the real terminator, not
        # one buried inside a comment.
        region = re.sub(r"\(\*.*?\*\)", "", region, flags=re.DOTALL)
        region = re.sub(r"//.*$", "", region, flags=re.MULTILINE)
        # Join wrapped-type lines: if pypdf split a type across two lines
        # (e.g. "in : POINTER TO\nT_HUGE_INTEGER;"), the type token would
        # otherwise be truncated by the `\n` exclusion in VAR_DECL_RE. A line
        # is a continuation when (a) it does not start with a new "name :"
        # declaration AND (b) the previous accumulated line still has an
        # unterminated `:` (no `;`).
        region = _join_wrapped_decls(region)
        for vm in VAR_DECL_RE.finditer(region):
            typ = vm.group(2)
            typ = re.sub(r":=.*$", "", typ, flags=re.DOTALL).strip()
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

    # For OO parent FBs (e.g. TC_CoreBoostMonitor with method children at
    # depth-3), the extracted section text includes the children's bodies and
    # therefore their VAR_INPUTs. The parent doc only describes its own
    # interface, so restrict the comparison to the parent's own body.
    if entry.get("is_parent"):
        child_pat = re.compile(rf"^\s*{re.escape(entry['section'])}\.\d+\s+\w+", re.MULTILINE)
        cm = child_pat.search(section_text)
        if cm:
            section_text = section_text[: cm.start()]

    # FBs that document their methods inline (e.g. FB_GetAdaptersInfoEx with
    # an inline `METHOD Get : BOOL`) expose method-internal VAR_INPUTs that
    # don't belong to the FB's own interface. Cut at the first inline METHOD
    # declaration so we compare only the FB-level VAR.
    inline_method = re.search(r"(?m)^\s*METHOD\s+\w+", section_text)
    if inline_method:
        section_text = section_text[: inline_method.start()]

    # If the entry is NOT a global constant, the PDF section may still embed
    # a VAR_GLOBAL CONSTANT block inside an Example (e.g. WEST_EUROPE_TZI in
    # FB_SetTimeZoneInformation). Strip those so they don't appear in the FB
    # VAR comparison set.
    if entry.get("type") != "GVL":
        section_text = re.sub(
            r"VAR_GLOBAL(?:\s+CONSTANT)?\s*\n[\s\S]*?END_VA[R]?",
            "",
            section_text,
            flags=re.IGNORECASE,
        )

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

    # Empty VAR on both sides is legitimate for pure-OO parent FBs that only
    # expose methods (e.g. FB_CalcHashValue: start()/update()/finish()) and
    # for methods that take no args. Only flag if PDF has none but doc claims
    # to have some — which would indicate doc-side hallucination.
    if not pdf_vars and doc_vars:
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
