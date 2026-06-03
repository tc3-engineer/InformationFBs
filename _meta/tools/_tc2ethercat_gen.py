#!/usr/bin/env python3
"""Generate Tc2_EtherCAT FB/FC docs and TcPOU stubs.

Pipeline:
  1) For each entry in CATALOG, extract its PDF section text via extract_section.
  2) Parse VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT blocks verbatim.
  3) Parse the Name/Type/Description tables that follow.
  4) Render a markdown doc using the strict 8-section template.
  5) Render a P_Demo_<Name>.TcPOU file with a Chinese 场景/价值/验证 header.

Manual overrides live in `_tc2ethercat_overrides.py`. The catalogue/generator
is generic; the override module supplies the Chinese narrative (§1/§3/§5/§7)
that requires PDF + InfoSys human reading. Anything the override module does
NOT supply, the generator fills with a safe "needs author input" mark plus a
factual section-skeleton derived from the PDF.
"""
from __future__ import annotations

import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "_meta" / "tools"
sys.path.insert(0, str(TOOLS))

from extract_section import extract as extract_section  # noqa: E402

# Stable namespace for example POU GUIDs (library-prefixed per Wave-1 lesson).
NS_UUID = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
LIB = "Tc2_EtherCAT"
LIB_VERSION = "1.9.5"
PDF_URL = "https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf"


def stable_guid(name: str) -> str:
    return "{" + str(uuid.uuid5(NS_UUID, f"tc3-libraries-kb/{LIB}/P_Demo_{name}")) + "}"


# ----------------------------------------------------------------------------
# PDF parsing helpers
# ----------------------------------------------------------------------------
VAR_REGION_RE = re.compile(
    r"VAR_(?P<kind>INPUT|OUTPUT|IN_OUT)\s*\n([\s\S]*?)END_VAR",
    re.IGNORECASE,
)
DECL_RE = re.compile(
    r"^\s*([A-Za-z_]\w*)\s*:\s*([^;\n]+?)\s*(?:;|$)",
    re.MULTILINE,
)


def _strip_comments(s: str) -> str:
    s = re.sub(r"\(\*.*?\*\)", "", s, flags=re.DOTALL)
    s = re.sub(r"//.*$", "", s, flags=re.MULTILINE)
    return s


def parse_vars(section_text: str) -> dict[str, list[tuple[str, str, str]]]:
    """Return {kind: [(name, type, default)]} for each VAR_xxx block."""
    out: dict[str, list[tuple[str, str, str]]] = {"INPUT": [], "OUTPUT": [], "IN_OUT": []}
    for m in VAR_REGION_RE.finditer(section_text):
        kind = m.group("kind").upper()
        if kind not in out:
            continue
        body = _strip_comments(m.group(2))
        for dm in DECL_RE.finditer(body):
            name = dm.group(1)
            rest = dm.group(2).strip()
            if name.upper() in {"END_VAR", "VAR_INPUT", "VAR_OUTPUT", "VAR_IN_OUT"}:
                continue
            default = ""
            if ":=" in rest:
                typ_str, default = rest.split(":=", 1)
                typ = typ_str.strip()
                default = default.strip()
            else:
                typ = rest
            typ = re.sub(r"\s+", " ", typ).strip()
            if not typ:
                continue
            out[kind].append((name, typ, default))
    return out


def parse_function_signature(section_text: str) -> str | None:
    """For FUNCTION entries: return 'FUNCTION Name : Returntype' line if present."""
    m = re.search(
        r"^(FUNCTION\s+[A-Za-z_]\w*\s*:\s*[^\n]+)$",
        section_text,
        re.MULTILINE,
    )
    return m.group(1).strip() if m else None


def parse_desc_table(section_text: str, names: list[str]) -> dict[str, str]:
    """Best-effort: scan post-VAR text for 'Name Type Description...' lines.

    PDFs print these as 3-column tables flattened to multi-line text. For each
    target name, find the next 'name<space>type<space>desc' segment.
    Returns {name: english_description}.
    """
    out: dict[str, str] = {}
    # work on the chunk AFTER the last END_VAR — descriptions live there
    chunks = re.split(r"END_VAR", section_text)
    after = chunks[-1] if len(chunks) > 1 else section_text
    after = _strip_comments(after)
    # Stop at common "Outputs" / "Inputs" / "Sample" markers that mark next block
    # but keep prose multi-line. We try a name-anchored sweep.
    for nm in names:
        # match: name <type_with_brackets_and_links> <description...> until next name marker
        pat = re.compile(
            rf"\b{re.escape(nm)}\b\s+([A-Za-z_][\w\[\] }}{{ \.\-]*?)\s+([^\n].*?)(?=\n\s*(?:[A-Za-z_]\w*\s+[A-Za-z_]|Outputs|Inputs|Sample|Example|Prerequisites|\Z))",
            re.DOTALL,
        )
        m = pat.search(after)
        if m:
            desc = m.group(2).strip()
            desc = re.sub(r"\s+", " ", desc)
            # truncate excessive verbiage
            if len(desc) > 320:
                desc = desc[:317] + "..."
            out[nm] = desc
    return out
