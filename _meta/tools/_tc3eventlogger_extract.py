#!/usr/bin/env python3
"""Helper: extract VAR_INPUT/VAR_OUTPUT and return-type for a Tc3_EventLogger entry."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))
from extract_section import extract as extract_section  # noqa: E402
from parse_toc import parse as parse_toc  # noqa: E402

VAR_REGION_RE = re.compile(
    r"VAR_(?:INPUT|OUTPUT|IN_OUT)(?:\s+CONSTANT)?\s*\n([\s\S]*?)END_VA[R]?",
    re.IGNORECASE,
)
VAR_DECL_RE = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?!=)([^;\n]+?)\s*(?:;|$)",
    re.MULTILINE,
)
NAKED_PARAM_RE = re.compile(
    r"^\s*([A-Za-z_]\w*)\s*:\s*(?!=)([^;\n]+?)\s*(?:;|$)",
    re.MULTILINE,
)


def parse_vars(section_text: str, name: str) -> dict:
    """Return dict with inputs[(name,type,default)], outputs, in_outs, return_type, return_name, signature."""
    # Find METHOD/FUNCTION signature & return type
    sig_re = re.search(r"(METHOD|FUNCTION)\s+(\w+)\s*:\s*(\w+)", section_text)
    ret_type = sig_re.group(3) if sig_re else None
    decl_kind = sig_re.group(1) if sig_re else None

    # Categorize each var region
    inputs = []
    outputs = []
    in_outs = []

    text = section_text
    for m in re.finditer(
        r"VAR_(INPUT|OUTPUT|IN_OUT)(?:\s+CONSTANT)?\s*\n([\s\S]*?)END_VA[R]?",
        text,
        re.IGNORECASE,
    ):
        kind = m.group(1).upper()
        body = m.group(2)
        body = re.sub(r"\(\*.*?\*\)", "", body, flags=re.DOTALL)
        body = re.sub(r"//.*$", "", body, flags=re.MULTILINE)
        # join wrapped types
        lines = body.split("\n")
        out_lines = []
        for raw in lines:
            if (
                out_lines
                and out_lines[-1].strip()
                and ":" in out_lines[-1]
                and ";" not in out_lines[-1]
                and raw.strip()
                and not re.match(r"^\s*[A-Za-z_]\w*\s*:(?!=)", raw)
            ):
                out_lines[-1] = out_lines[-1].rstrip() + " " + raw.strip()
            else:
                out_lines.append(raw)
        body = "\n".join(out_lines)
        for vm in VAR_DECL_RE.finditer(body):
            decl_name = vm.group(1)
            rest = vm.group(2)
            default = None
            if ":=" in rest:
                typ_part, default = rest.split(":=", 1)
                default = default.strip()
                typ_part = typ_part.strip()
            else:
                typ_part = rest.strip()
            typ_part = re.sub(r"\s+", " ", typ_part).strip()
            tup = (decl_name, typ_part, default)
            if kind == "INPUT":
                inputs.append(tup)
            elif kind == "OUTPUT":
                outputs.append(tup)
            else:
                in_outs.append(tup)

    # If still nothing on inputs and there is a METHOD signature, try naked-param recovery
    if not inputs and sig_re:
        m = re.search(
            r"METHOD\s+\w+\s*:\s*\w+[^\n]*\n([\s\S]*?)(?=\n\s*(?:METHOD\b|VAR_|END_VAR|FUNCTION_BLOCK\b|FUNCTION\b|Inputs\b|Outputs\b|Return\s+value\b|\Z))",
            section_text,
        )
        if m:
            body = m.group(1)
            body = re.sub(r"\(\*.*?\*\)", "", body, flags=re.DOTALL)
            body = re.sub(r"//.*$", "", body, flags=re.MULTILINE)
            for vm in NAKED_PARAM_RE.finditer(body):
                nm = vm.group(1)
                if nm.upper() in {"METHOD", "END_VAR", "VAR_INPUT", "VAR_OUTPUT"}:
                    continue
                rest = vm.group(2)
                default = None
                if ":=" in rest:
                    typ_part, default = rest.split(":=", 1)
                    default = default.strip()
                    typ_part = typ_part.strip()
                else:
                    typ_part = rest.strip()
                typ_part = re.sub(r"\s+", " ", typ_part).strip()
                inputs.append((nm, typ_part, default))

    return {
        "inputs": inputs,
        "outputs": outputs,
        "in_outs": in_outs,
        "return_type": ret_type,
        "decl_kind": decl_kind,
    }


def get_section_text(lib: str, name: str, parent_dir: str = "") -> tuple[str, dict]:
    toc = parse_toc(lib)
    candidates = [e for e in toc if e["name"] == name]
    entry = None
    if len(candidates) > 1 and parent_dir:
        entry = next(
            (e for e in candidates if e["category"].lower() == parent_dir.lower()),
            None,
        )
    if entry is None and candidates:
        entry = candidates[0]
    if entry is None:
        raise ValueError(f"not found: {name}")
    section_text = extract_section(lib, entry["section"])

    # Cut at child sub-section for parent FBs
    if entry.get("is_parent"):
        child_pat = re.compile(
            rf"^\s*{re.escape(entry['section'])}\.\d+\s+\w+", re.MULTILINE
        )
        cm = child_pat.search(section_text)
        if cm:
            section_text = section_text[: cm.start()]

    # Cut inline METHOD for parent-level FBs
    entry_depth = entry["section"].count(".") + 1
    if entry_depth <= 2:
        inline_method = re.search(r"(?m)^\s*METHOD\s+\w+", section_text)
        if inline_method:
            section_text = section_text[: inline_method.start()]

    return section_text, entry


if __name__ == "__main__":
    lib = sys.argv[1]
    name = sys.argv[2]
    parent = sys.argv[3] if len(sys.argv) > 3 else ""
    text, entry = get_section_text(lib, name, parent)
    print(f"# entry: {entry}")
    print(f"# section length: {len(text)}")
    print("---SECTION---")
    print(text[:2000])
    print("---VARS---")
    parsed = parse_vars(text, name)
    import json

    print(json.dumps(parsed, indent=2))
