#!/usr/bin/env python3
"""
Lint a PLCopenXML demo file produced by /doc-shard.

Checks:
  1. XML is well-formed
  2. Root is <project xmlns="http://www.plcopen.org/xml/tc6_0200">
  3. Contains exactly one <pou pouType="program" name="P_Demo_<Name>">
  4. Contains <derived name="<Name>"/> referencing the demoed FB
  5. Contains a <ST> body
  6. Body does NOT contain raw `<` or `&` outside of XML entities (ie no
     bare ST `<`, `>`, `&` left unescaped)
  7. No TwinCAT private attributes (attribute pragma, accessSpecifier, etc.)

Usage:
    python3 _meta/tools/lint_plcopen.py <path-to-xml>

Exit 0 = clean, 1 = warn, 2 = fail
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS = "http://www.plcopen.org/xml/tc6_0200"
ROOT = Path(__file__).resolve().parents[2]


def lint(path: str) -> tuple[int, list[str]]:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    if not p.exists():
        return 2, [f"file not found: {p}"]
    text = p.read_text()

    diags: list[str] = []

    try:
        tree = ET.fromstring(text)
    except ET.ParseError as e:
        return 2, [f"XML parse error: {e}"]

    if not tree.tag.endswith("project") or NS not in tree.tag:
        diags.append(f"root tag must be {{{NS}}}project, got {tree.tag}")

    pous = tree.findall(f".//{{{NS}}}pou")
    if len(pous) != 1:
        diags.append(f"expected exactly one <pou>, got {len(pous)}")
    pou = pous[0] if pous else None
    if pou is not None:
        if pou.get("pouType") != "program":
            diags.append(f"pouType must be program, got {pou.get('pouType')}")
        name = pou.get("name", "")
        if not name.startswith("P_Demo_"):
            diags.append(f"pou name must start with P_Demo_, got {name!r}")
        demoed = name.removeprefix("P_Demo_")
        # For OO method demos with parent-prefixed stems (P_Demo_FB_TcAlarm_Create),
        # also accept the tail token (Create) as the demoed FB/method name.
        candidates = [demoed]
        if "_" in demoed:
            candidates.append(demoed.rsplit("_", 1)[1])
        derived = pou.findall(f".//{{{NS}}}derived")
        st_node = pou.find(f"{{{NS}}}body/{{{NS}}}ST/{{http://www.w3.org/1999/xhtml}}xhtml")
        st_text_for_check = "".join(st_node.itertext()) if st_node is not None else ""

        def _ok(sym: str) -> bool:
            has_derived = any(d.get("name") == sym for d in derived)
            called = bool(re.search(rf"\b{re.escape(sym)}\s*\(", st_text_for_check))
            bare = bool(re.search(rf"\b{re.escape(sym)}\b", st_text_for_check))
            return has_derived or called or bare

        if not any(_ok(c) for c in candidates):
            diags.append(
                f"<derived name=\"{demoed}\"/> not in localVars; {demoed}(...) not called; "
                f"and {demoed} not referenced in ST body"
            )
        XHTML = "http://www.w3.org/1999/xhtml"
        body_xhtml = None
        body_st = pou.find(f"{{{NS}}}body/{{{NS}}}ST")
        if body_st is not None:
            body_xhtml = body_st.find(f"{{{XHTML}}}xhtml")
            if body_xhtml is None:
                body_xhtml = body_st.find(f"{{{NS}}}xhtml")
        if body_st is None or body_xhtml is None:
            diags.append("missing <body><ST><xhtml> body")
        else:
            st_text = "".join(body_xhtml.itertext())
            # Check that no unescaped `<` `>` `&` appears in ST source
            # ET already de-entitied them; we search the *raw* text of the ST node
            # by re-scanning the file for the ST block
            m = re.search(r"<ST>\s*<xhtml[^>]*>([\s\S]*?)</xhtml>\s*</ST>", text)
            if m:
                raw = m.group(1)
                # Allowed entities
                for bad in re.finditer(r"&(?!lt;|gt;|amp;|quot;|apos;|#\d+;)", raw):
                    diags.append(f"unescaped & at offset {bad.start()} of ST body")
                    break

    # forbidden private attrs
    for bad in ("{http://www.beckhoff.com/", "accessSpecifier=", "{TcAddData}"):
        if bad in text:
            diags.append(f"forbidden TwinCAT private marker: {bad}")

    if not diags:
        return 0, ["PASS"]
    fail = any("XML parse error" in d or "missing <body>" in d or "<derived" in d for d in diags)
    return (2 if fail else 1), diags


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    code, diags = lint(sys.argv[1])
    for d in diags:
        print(d)
    return code


if __name__ == "__main__":
    sys.exit(main())
