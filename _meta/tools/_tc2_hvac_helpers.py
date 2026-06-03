#!/usr/bin/env python3
"""Helper script for Tc2_HVAC documentation generation.

Library-internal generation script. Lives at _meta/tools/ per CLAUDE.md
agent boundaries: scripts with `_<lower_lib>_` prefix may live there.

Provides:
 - parse_pdf_section(section) -> {var_input, var_output, var_in_out, body_text, descriptions}
 - extract_var_block(section_text, kind) -> raw VAR_<kind> text (PDF verbatim, comments stripped)
 - extract_descriptions(section_text) -> dict mapping var name -> English description text
 - render_doc(...) is NOT used; docs are hand-edited from extracted skeletons.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "_meta" / ".pdf-cache"
LIB = "Tc2_HVAC"


def extract_section(section: str) -> str:
    """Call extract_section.py to get PDF body text for a given section number."""
    res = subprocess.run(
        ["python3", str(ROOT / "_meta/tools/extract_section.py"), LIB, section],
        capture_output=True,
        text=True,
        check=True,
    )
    return res.stdout


# --- VAR-block extraction -------------------------------------------------

_VAR_KEYWORDS = ("VAR_INPUT", "VAR_OUTPUT", "VAR_IN_OUT")
_VAR_BLOCK_RE = re.compile(
    r"^(VAR_(?:INPUT|OUTPUT|IN_OUT))\s*$([\s\S]*?)^(?:END_VAR|" +
    r"|".join(_VAR_KEYWORDS) + r"|Requirements|VAR_GLOBAL|Application example:|" +
    r"NOTICE|^\d+\.\d+|^[a-zA-Z][^\n]*?:\s*If\s|^[a-zA-Z][^\n]*?:\s*[A-Z])",
    re.MULTILINE,
)


def extract_var_blocks(section_text: str) -> dict[str, str]:
    """Find VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT blocks.

    Returns dict {VAR_INPUT: "...declarations...", ...} with declaration lines only.
    Empty string if not present.

    HVAC PDF format quirks handled:
     - No END_VAR terminator after VAR block (description text starts next line)
     - Description text uses `name: prose` format which can be misread as a decl
     - Some FBs use `rIn1 - rIn8` ranged decl syntax — keep as-is (PDF verbatim)
    """
    result = {kw: "" for kw in _VAR_KEYWORDS}

    # Description-line detector: a `name : prose` line that's NOT a real
    # declaration. We classify by RHS: if RHS contains lowercase prose words
    # OR begins with `(` `'` etc, treat as description and STOP the block.
    def is_desc_line(stripped: str) -> bool:
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*(?:\s*[-–—]\s*[a-zA-Z_][a-zA-Z0-9_]*)?)\s*:\s+(.*)$", stripped)
        if not m:
            return False
        rhs = m.group(2)
        if not rhs:
            return False
        # Hint words that ALWAYS indicate description prose
        prose_hints = (
            "If ", "The ", "TRUE", "FALSE", "this ", "this F",
            "Enum ", "Function", "Acknowledge", "Indicates", "Shows ",
            "Goes ", "Among ", "Number of", "input ", "output ", "Number ",
            "Parameter ", "Activates", "Output ", "Actuator ", "Setpoint",
            "Setpoints", "Value", "Contains", "When ", "Reset", "control",
            "Among other", "value", "feedback", "Time", "It is ",
            "Used ", "Conversion", "Permissible",
        )
        if any(w in rhs for w in prose_hints):
            return True
        # If RHS doesn't look like an IEC type, treat as prose
        if not re.match(r"^[A-Z][A-Za-z0-9_]*(\s*\(|\s*\[|\s*;|\s*$|\s*:=)", rhs):
            return True
        return False

    def is_decl_line(stripped: str) -> bool:
        """A real IEC declaration: `name : Type;` or `name1 - nameN : Type;`.

        Accepts Array, structured, custom-typed, default-valued, range-named,
        and (PDF typo) trailing `:` instead of `;`. Range separator can be
        `-` or U+2013 (en-dash `–`) or U+2014 (em-dash `—`) — PDF typo cases.
        """
        # 1) name(s) : Type
        m = re.match(
            r"^([a-zA-Z_][a-zA-Z0-9_]*(?:\s*[-–—]\s*[a-zA-Z_][a-zA-Z0-9_]*)?)"
            r"\s*:\s*([A-Za-z_][^;\n]*)",
            stripped,
        )
        if not m:
            return False
        rhs = m.group(2)
        # If RHS contains a `:` somewhere (e.g. another `name:` description), reject.
        # But `:=` (default value) is OK; `Array[1..N]` is OK; `;` end is OK.
        # Strict: if the RHS contains `: ` (space-after-colon outside brackets), reject.
        rhs_no_brackets = re.sub(r"\[[^\]]*\]", "", rhs)
        if re.search(r":\s+(?!=)", rhs_no_brackets):
            return False
        # The RHS must start with a Type-like token (uppercase first letter
        # for IEC types, OR start with "Array" / "ARRAY" / "STRING" / "POINTER").
        first_token = re.match(r"^\s*([A-Za-z][A-Za-z0-9_]*)", rhs).group(1)
        type_like = (
            first_token[0].isupper()
            or first_token.lower() in {"array", "string", "pointer"}
        )
        return type_like

    lines = section_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line in _VAR_KEYWORDS:
            kw = line
            i += 1
            block_lines = []
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                # terminators
                if stripped == "END_VAR":
                    i += 1
                    break
                if stripped in _VAR_KEYWORDS:
                    break
                if stripped in ("Requirements", "NOTICE"):
                    break
                if stripped.startswith("VAR_GLOBAL"):
                    break
                if re.match(r"^\d+\.\d+\s+[A-Z_]", stripped):  # next section
                    break
                if stripped.startswith("Application example:"):
                    break
                # Empty line is ambiguous — skip in block
                if not stripped:
                    i += 1
                    continue
                # Description line that uses `name: prose` format — STOP the block
                if is_desc_line(stripped):
                    break
                # Real declaration — keep
                if is_decl_line(stripped):
                    block_lines.append(line)
                    i += 1
                    continue
                # Anything else (PDF page header, comment) — stop the block too
                break
            result[kw] = "\n".join(l.rstrip() for l in block_lines).rstrip()
        else:
            i += 1
    return result


def extract_description_lines(section_text: str, var_names: list[str]) -> dict[str, str]:
    """Extract `name: description` lines from prose into dict.

    var_names: list of declared variable names; only those are picked.
    """
    out = {n: "" for n in var_names}
    lines = section_text.split("\n")
    current = None
    buf = []
    name_set = set(var_names)

    def flush():
        if current and buf:
            txt = " ".join(b.strip() for b in buf if b.strip())
            # collapse multiple spaces
            txt = re.sub(r"\s+", " ", txt)
            out[current] = txt.strip()

    for raw in lines:
        stripped = raw.strip()
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)$", stripped)
        if m:
            name = m.group(1)
            rest = m.group(2)
            # type-like? skip; description-like? pick.
            # If it's a declaration line (RHS starts with TypeName + optional default + ;),
            # skip.
            if re.match(r"^[A-Z][A-Za-z0-9_]*\s*(:=|;|$)", rest):
                continue
            if name in name_set:
                flush()
                current = name
                buf = [rest]
                continue
        # continuation
        if current:
            # Stop at next section number / NOTICE / VAR_xx / Requirements
            if not stripped:
                continue
            if stripped in ("NOTICE", "Requirements") or stripped in _VAR_KEYWORDS:
                flush()
                current = None
                buf = []
                continue
            if re.match(r"^\d+\.\d+\s+[A-Z_]", stripped):
                flush()
                current = None
                buf = []
                continue
            buf.append(stripped)
    flush()
    return out


# --- VAR-decl parsing (after extract_var_blocks) -------------------------------

VAR_NAME_RE = re.compile(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*([^;]+)(?:;|$)")


def parse_decls(var_block: str) -> list[tuple[str, str, str | None]]:
    """Return [(name, type, default), ...] for declarations in var_block.

    Type captures up to ":=" or ";". Default captures literal between := and ;.
    """
    out = []
    for line in var_block.split("\n"):
        m = VAR_NAME_RE.match(line)
        if not m:
            continue
        name = m.group(1)
        rest = m.group(2).strip()
        if ":=" in rest:
            tp, _, df = rest.partition(":=")
            out.append((name, tp.strip(), df.strip()))
        else:
            out.append((name, rest, None))
    return out


if __name__ == "__main__":
    # quick smoke: print VAR_INPUT extraction for §5.1.2.1
    section = sys.argv[1] if len(sys.argv) > 1 else "5.1.2.1"
    txt = extract_section(section)
    blocks = extract_var_blocks(txt)
    for kw, bk in blocks.items():
        print(f"--- {kw} ---")
        print(bk)
    decls = parse_decls(blocks.get("VAR_INPUT", ""))
    names = [n for n, _, _ in decls]
    print(f"--- names: {names} ---")
    descs = extract_description_lines(txt, names)
    for n in names:
        print(f"  {n}: {descs.get(n, '')[:120]!r}")
