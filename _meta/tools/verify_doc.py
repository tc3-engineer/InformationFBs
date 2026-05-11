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


_NAKED_PARAM_RE = re.compile(
    r"^\s*([A-Za-z_]\w*)\s*:\s*(?!=)([^;\n]+?)\s*(?:;|$)",
    re.MULTILINE,
)


def _naked_method_params(section_text: str) -> list[tuple[str, str]]:
    """Recover parameters from a METHOD declaration that lacks VAR_INPUT.

    Beckhoff PDFs occasionally render a method signature as
        METHOD <Name> : <RetType>
            param1 : T1;
            param2 : T2 := def;
            ...
    with NO surrounding `VAR_INPUT ... END_VAR`. _vars_from_text misses
    these. Capture the block between the METHOD header and the next
    structural marker.
    """
    m = re.search(
        r"METHOD\s+\w+\s*:\s*\w+[^\n]*\n([\s\S]*?)(?=\n\s*(?:METHOD\b|VAR_|END_VAR|FUNCTION_BLOCK\b|FUNCTION\b|Inputs\b|Outputs\b|Return\s+value\b|\Z))",
        section_text,
    )
    if not m:
        return []
    body = m.group(1)
    body = re.sub(r"\(\*.*?\*\)", "", body, flags=re.DOTALL)
    body = re.sub(r"//.*$", "", body, flags=re.MULTILINE)
    body = _join_wrapped_decls(body)
    out: list[tuple[str, str]] = []
    for vm in _NAKED_PARAM_RE.finditer(body):
        name = vm.group(1)
        typ = vm.group(2)
        typ = re.sub(r":=.*$", "", typ, flags=re.DOTALL).strip()
        typ = re.sub(r"\s+", " ", typ).strip()
        if name.upper() in {
            "METHOD", "END_VAR", "VAR_INPUT", "VAR_OUTPUT",
            "FUNCTION_BLOCK", "FUNCTION", "INPUTS", "OUTPUTS",
        }:
            continue
        if not typ:
            continue
        out.append((name, typ))
    return out


_DEFAULT_PAT = re.compile(
    r"\b([A-Za-z_]\w*)\s*:\s*[^;\n]+?:=\s*([^;\n]+?)\s*(?:;|$)",
    re.MULTILINE,
)


def _extract_defaults(section_text: str) -> dict[str, str]:
    """Return {var_name: default_value} for every `name : type := def` inside
    any VAR_(INPUT|OUTPUT|IN_OUT|GLOBAL) region. Comments stripped first."""
    out: dict[str, str] = {}
    for m in VAR_REGION_RE.finditer(section_text):
        region = m.group(1)
        region = re.sub(r"\(\*.*?\*\)", "", region, flags=re.DOTALL)
        region = re.sub(r"//.*$", "", region, flags=re.MULTILINE)
        region = _join_wrapped_decls(region)
        for dm in _DEFAULT_PAT.finditer(region):
            name = dm.group(1)
            default = dm.group(2).strip()
            if not default:
                continue
            out.setdefault(name, default)
    return out


def _read_doc_meta(doc: str) -> dict:
    meta: dict[str, str] = {}
    pat = re.compile(r"\|\s*([A-Za-z _\-]+?)\s*\|\s*(.+?)\s*\|\s*$", re.MULTILINE)
    for m in pat.finditer(doc):
        k = m.group(1).strip()
        v = m.group(2).strip().strip("`")
        meta.setdefault(k, v)
    return meta


# ----------------------------------------------------------------------------
# Content quality (CLAUDE.md hard rules B / C / E added 2026-05-11)
# ----------------------------------------------------------------------------
_PLACEHOLDER_PHRASES = (
    "（详见 PDF）",
    "详见 PDF",
    "见上方功能简述。",
    "见上方'功能简述'。",
    "见上方使用注意中标 ⚠️ 的项",
    "请见对应 InfoSys 页面，⚠️ 待人工补全",
    "请对照 PDF 第",
    "（详细见 PDF）",
)

_CJK_RE = re.compile(r"[一-鿿]")
_INFOSYS_TOPIC_RE = re.compile(
    r"https?://infosys\.beckhoff\.com/content/\d+/tcplclib_[a-z0-9_]+/\d+\.html"
)
_INFOSYS_CHECKED_OK_RE = re.compile(
    r"(?:✅\s*\d{4}-\d{2}-\d{2}|⚠️\s*not-on-infosys)"
)


def _strip_doc_chrome(doc: str) -> str:
    """Strip code fences and tables so prose-only checks aren't fooled by them."""
    t = re.sub(r"```[\s\S]*?```", "", doc)
    t = re.sub(r"^\|.*\|\s*$", "", t, flags=re.MULTILINE)
    return t


def _section_text(doc: str, header_pat: str) -> str:
    m = re.search(rf"{header_pat}([\s\S]*?)(?=^## |\Z)", doc, re.MULTILINE)
    return m.group(1) if m else ""


def _check_content_quality(doc: str, meta: dict) -> list[str]:
    diags: list[str] = []

    # C. Placeholder phrases — anywhere in the doc is a fail
    for phrase in _PLACEHOLDER_PHRASES:
        if phrase in doc:
            diags.append(f"placeholder phrase present: {phrase!r}")

    # C. Variable description table cells equal to "（详见 PDF）"
    bad_cells = re.findall(
        r"^\|\s*`[^`]+`\s*\|\s*`[^`]+`\s*\|\s*（详见 PDF）\s*\|\s*$",
        doc,
        re.MULTILINE,
    )
    if bad_cells:
        diags.append(
            f"variable description: {len(bad_cells)} table cell(s) are bare '（详见 PDF）'"
        )

    # B. English-only §1 功能简述 / §3 行为说明 — require CJK characters in prose
    prose_doc = _strip_doc_chrome(doc)
    s1 = _section_text(prose_doc, r"^## 1\. 功能简述")
    s3 = _section_text(prose_doc, r"^## 3\. 行为说明")
    if s1 and not _CJK_RE.search(s1):
        diags.append("English-only §1 功能简述 (no CJK characters in prose)")
    # §3 must have substantive Chinese prose. Remove bullet placeholders first.
    s3_clean = re.sub(r"^\s*-\s.*$", "", s3, flags=re.MULTILINE)
    cjk_count = len(_CJK_RE.findall(s3_clean))
    if s3 and cjk_count < 80:
        diags.append(
            f"§3 行为说明 too short or non-Chinese ({cjk_count} CJK chars, need ≥80)"
        )

    # E. InfoSys topic URL + checked status in metadata
    src_info = meta.get("Source InfoSys", "").strip()
    if not src_info or not _INFOSYS_TOPIC_RE.search(src_info):
        diags.append(
            "Source InfoSys: missing or not a specific topic URL "
            "(must match https://infosys.beckhoff.com/content/.../tcplclib_*/<id>.html)"
        )
    checked = meta.get("InfoSys-checked", "").strip()
    if not checked or not _INFOSYS_CHECKED_OK_RE.search(checked):
        diags.append(
            "InfoSys-checked: missing or wrong format (need '✅ YYYY-MM-DD' or '⚠️ not-on-infosys')"
        )

    return diags


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

    # find section for this name. Some libs have the same method name under
    # multiple OO parents (Tc3_EventLogger: FB_TcAlarm.Create vs
    # FB_TcMessage.Create vs FB_TcSourceInfo.Clear etc.). Disambiguate by
    # using the doc's parent directory as a hint: the subdir is the lowercased
    # category name (FB_TcMessage -> fb_tcmessage).
    toc = parse_toc(lib)
    parent_dir = p.parent.name.lower()
    candidates = [e for e in toc if e["name"] == name]
    entry = None
    if len(candidates) > 1:
        entry = next(
            (e for e in candidates if e["category"].lower() == parent_dir), None
        )
    if entry is None and candidates:
        entry = candidates[0]
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
    # an inline `METHOD Get : BOOL`, or FB_CalcHashValue whose body is
    # entirely methods with no FB-level VAR) expose method-internal
    # VAR_INPUTs that don't belong to the FB's own interface. Cut at the
    # first inline METHOD declaration.
    #
    # Skip the cut when the entry IS itself a method (depth-3+ child under
    # an OO parent like TC_CoreBoostMonitor.GetAllRtCoreThrottling at
    # section 3.83.1) — its body legitimately contains a METHOD declaration
    # for the method itself, and we need its VAR_INPUT block.
    # Don't cut for inline-method entries (synthetic `<sec>#mN` ids): the
    # section_text IS the method body whose METHOD header + VAR_INPUT we
    # want to keep.
    entry_depth = entry["section"].count(".") + 1
    is_inline_method = entry.get("inline_method") or "#" in entry["section"]
    if entry_depth <= 2 and not is_inline_method:
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
    # Some Beckhoff PDFs print method signatures without VAR_INPUT/END_VAR
    # wrappers (e.g. Tc3_EventLogger FB_TcAlarm.Create §3.6.3). Recover those
    # "naked-param" declarations so the diff below actually flags doc-side
    # omissions instead of silently double-passing.
    if not pdf_vars:
        pdf_vars = _naked_method_params(section_text)

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

    # Default-value fidelity check (硬规则 #1 — 逐字搬运).
    # Every `name := default` in the PDF VAR regions must appear verbatim in
    # the doc Interface section.
    pdf_defaults = _extract_defaults(section_text)
    doc_iface_norm = re.sub(r"\s+", " ", interface_doc)
    for var_name, default in pdf_defaults.items():
        pat = rf"\b{re.escape(var_name)}\b\s*:[^;\n]*?:=\s*{re.escape(default)}"
        if not re.search(pat, doc_iface_norm):
            diags.append(f"default value missing in doc: {var_name} := {default}")

    # example link — read the actual link from the doc so parent-prefixed
    # stems for OO method collisions (e.g. P_Demo_FB_TcAlarm_Create.xml) are
    # honoured.
    examples_dir = p.parent.parent / "examples"
    m_ex = re.search(r"examples/P_Demo_([A-Za-z0-9_]+)\.xml", doc)
    example_stem = m_ex.group(1) if m_ex else name
    if not (examples_dir / f"P_Demo_{example_stem}.xml").exists():
        diags.append(f"example missing: examples/P_Demo_{example_stem}.xml")

    # Empty VAR on both sides is legitimate for pure-OO parent FBs that only
    # expose methods (e.g. FB_CalcHashValue: start()/update()/finish()) and
    # for methods that take no args. Only flag if PDF has none but doc claims
    # to have some — which would indicate doc-side hallucination.
    if not pdf_vars and doc_vars:
        diags.append(
            "PDF section had no VAR_INPUT/OUTPUT — manual review needed (FC with no params?)"
        )

    # ---- Content quality (CLAUDE.md hard rules B / C / E, 2026-05-11) ----
    diags.extend(_check_content_quality(doc, meta))

    if any(
        d.startswith("VAR not present")
        or d.startswith("cache miss")
        or d.startswith("default value missing")
        or d.startswith("placeholder phrase")
        or d.startswith("English-only")
        or d.startswith("§3 行为说明 too short")
        or d.startswith("Source InfoSys")
        or d.startswith("InfoSys-checked")
        or d.startswith("variable description")
        for d in diags
    ):
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
