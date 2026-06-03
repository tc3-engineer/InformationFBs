#!/usr/bin/env python3
"""
Convert PLCopenXML PROGRAM examples to TwinCAT 3 native `.TcPOU` files.

Why: PLCopenXML (.xml) requires the user to run "Import PLCopenXML" wizard in
XAE. `.TcPOU` files can be added directly via "Add → Existing Item" or by
dropping the file into the PLC project tree in Solution Explorer.

Usage:
    python3 _meta/tools/plcopen_to_tcpou.py <file.xml>          # single file
    python3 _meta/tools/plcopen_to_tcpou.py --all               # whole repo
    python3 _meta/tools/plcopen_to_tcpou.py --all --delete-xml  # + remove .xml

Exit codes:
    0 = success
    1 = at least one file failed (warnings printed to stderr)
    2 = unexpected error
"""
from __future__ import annotations

import argparse
import re
import sys
import uuid
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
NS_PLCOPEN = "{http://www.plcopen.org/xml/tc6_0200}"
NS_XHTML = "{http://www.w3.org/1999/xhtml}"

TCPLCOBJECT_HEAD = (
    '<?xml version="1.0" encoding="utf-8"?>\n'
    '<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">\n'
)
TCPLCOBJECT_TAIL = "</TcPlcObject>\n"

IEC_TYPE_TAGS = {
    "BOOL", "BYTE", "WORD", "DWORD", "LWORD",
    "SINT", "INT", "DINT", "LINT",
    "USINT", "UINT", "UDINT", "ULINT",
    "REAL", "LREAL",
    "TIME", "LTIME", "DATE", "DT", "TIME_OF_DAY", "TOD", "DATE_AND_TIME",
    "STRING", "WSTRING", "CHAR", "WCHAR",
}


def _render_type(type_el: ET.Element) -> str:
    """Render a PLCopenXML <type> element back to IEC text syntax."""
    if type_el is None or len(type_el) == 0:
        return "BOOL"  # fallback; shouldn't hit on valid input
    child = type_el[0]
    tag = child.tag.replace(NS_PLCOPEN, "")
    if tag in IEC_TYPE_TAGS:
        return tag
    if tag == "derived":
        return child.get("name", "UNKNOWN")
    if tag == "string":
        length_el = child.find(f"{NS_PLCOPEN}length")
        if length_el is not None and length_el.text:
            return f"STRING({length_el.text.strip()})"
        return "STRING"
    if tag == "wstring":
        length_el = child.find(f"{NS_PLCOPEN}length")
        if length_el is not None and length_el.text:
            return f"WSTRING({length_el.text.strip()})"
        return "WSTRING"
    if tag == "pointer":
        base = child.find(f"{NS_PLCOPEN}baseType")
        return f"POINTER TO {_render_type(base)}"
    if tag == "reference":
        base = child.find(f"{NS_PLCOPEN}baseType")
        return f"REFERENCE TO {_render_type(base)}"
    if tag == "array":
        dims = child.findall(f"{NS_PLCOPEN}dimension")
        base = child.find(f"{NS_PLCOPEN}baseType")
        dim_text = ",".join(f"{d.get('lower','0')}..{d.get('upper','0')}" for d in dims)
        return f"ARRAY[{dim_text}] OF {_render_type(base)}"
    if tag == "enum":
        # Not used in our generated examples; fallback to derived if present
        return child.get("name", "ENUM")
    return tag


def _render_initial_value(iv_el: ET.Element) -> str | None:
    """Extract the initial value text from <initialValue> element."""
    if iv_el is None:
        return None
    simple = iv_el.find(f"{NS_PLCOPEN}simpleValue")
    if simple is not None:
        return simple.get("value")
    return None


def _render_documentation(doc_el: ET.Element) -> str | None:
    """Extract free-form documentation text from <documentation> element."""
    if doc_el is None:
        return None
    xhtml = doc_el.find(f"{NS_XHTML}xhtml")
    if xhtml is not None and xhtml.text:
        return xhtml.text.strip()
    return None


def _render_var_block(vars_el: ET.Element, kind: str) -> list[str]:
    """Render one <localVars> / <inputVars> / etc. as `VAR ... END_VAR` lines."""
    if vars_el is None or len(vars_el) == 0:
        return []
    out = [kind]
    name_w = max((len(v.get("name", "")) for v in vars_el.findall(f"{NS_PLCOPEN}variable")), default=0)
    for var in vars_el.findall(f"{NS_PLCOPEN}variable"):
        name = var.get("name", "")
        type_el = var.find(f"{NS_PLCOPEN}type")
        iv_el = var.find(f"{NS_PLCOPEN}initialValue")
        doc_el = var.find(f"{NS_PLCOPEN}documentation")
        type_str = _render_type(type_el)
        iv_str = _render_initial_value(iv_el)
        doc_str = _render_documentation(doc_el)
        line = f"    {name.ljust(name_w)} : {type_str}"
        if iv_str:
            line += f" := {iv_str}"
        line += ";"
        if doc_str:
            line += f" // {doc_str}"
        out.append(line)
    out.append("END_VAR")
    return out


def _strip_xhtml_namespace(text: str) -> str:
    """ST body in PLCopen is wrapped in <xhtml> — strip leftover xmlns text."""
    return text


def _extract_st_body(body_el: ET.Element) -> str:
    """Get the raw ST text from a <body><ST><xhtml>...</xhtml></ST></body>."""
    if body_el is None:
        return ""
    st = body_el.find(f"{NS_PLCOPEN}ST")
    if st is None:
        return ""
    xhtml = st.find(f"{NS_XHTML}xhtml")
    text = ""
    if xhtml is not None and xhtml.text:
        text = xhtml.text
    elif st.text:
        text = st.text
    return _rewrite_import_hints(text).rstrip() + "\n"


_IMPORT_REWRITES = [
    # PLCopenXML 导入路径 → TcPOU 直接添加路径（XAE 友好）
    ("右键 PLC 项目 → Import PLCopenXML → 选本文件",
     "右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选本 .TcPOU 文件"),
    ("右键 PLC 项目 → Import PLCopenXML",
     "右键 PLC 项目下 POUs → Add → Existing Item"),
    ("Import PLCopenXML",
     "Add Existing Item (.TcPOU)"),
    ("PLCopenXML 文件",
     ".TcPOU 文件"),
    ("PLCopenXML",
     "TcPOU"),
]


def _rewrite_import_hints(text: str) -> str:
    for old, new in _IMPORT_REWRITES:
        text = text.replace(old, new)
    return text


def _stable_guid(name: str, library: str = "") -> str:
    """Deterministic UUID5 from library + POU name so re-runs produce identical
    files. The library is part of the namespace path because same-named FBs
    appear across libraries (e.g. MC_Halt in Tc2_MC2 + Tc3_DriveMotionControl,
    FB_SoEReset in Tc2_MC2_Drive + Tc2_NcDrive) — without the library qualifier
    they collide and XAE refuses to load two POUs with the same Id.
    """
    ns = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # DNS namespace
    path = f"tc3-libraries-kb/{library}/{name}" if library else f"tc3-libraries-kb/{name}"
    return "{" + str(uuid.uuid5(ns, path)) + "}"


def convert(src: Path) -> str:
    """Read a PLCopenXML .xml file and return the .TcPOU XML text."""
    tree = ET.parse(src)
    root = tree.getroot()
    pous = root.find(f"{NS_PLCOPEN}types/{NS_PLCOPEN}pous")
    if pous is None or len(pous) == 0:
        raise ValueError(f"{src}: no <pous> found")
    pou_el = pous[0]
    name = pou_el.get("name", src.stem)
    pou_type = pou_el.get("pouType", "program")

    iface = pou_el.find(f"{NS_PLCOPEN}interface")
    body = pou_el.find(f"{NS_PLCOPEN}body")

    if pou_type == "program":
        header = f"PROGRAM {name}"
    elif pou_type == "functionBlock":
        header = f"FUNCTION_BLOCK {name}"
    elif pou_type == "function":
        # FUNCTION needs a return type — peek at <returnType>
        rt_el = iface.find(f"{NS_PLCOPEN}returnType") if iface is not None else None
        if rt_el is not None and len(rt_el) > 0:
            rt = rt_el[0].tag.replace(NS_PLCOPEN, "")
        else:
            rt = "BOOL"
        header = f"FUNCTION {name} : {rt}"
    else:
        header = f"PROGRAM {name}"

    decl_lines = [header]
    if iface is not None:
        for kind_tag, kind in (
            ("inputVars", "VAR_INPUT"),
            ("outputVars", "VAR_OUTPUT"),
            ("inOutVars", "VAR_IN_OUT"),
            ("localVars", "VAR"),
            ("tempVars", "VAR_TEMP"),
        ):
            block = iface.find(f"{NS_PLCOPEN}{kind_tag}")
            decl_lines.extend(_render_var_block(block, kind))
    decl_text = "\n".join(decl_lines) + "\n"

    impl_text = _extract_st_body(body)

    # Library qualifier from the source path: <Lib>/examples/<file>.xml
    try:
        library = src.parent.parent.name
    except Exception:
        library = ""
    pou_attrs = f'Name="{name}" Id="{_stable_guid(name, library)}" SpecialFunc="None"'
    out = TCPLCOBJECT_HEAD
    out += f"  <POU {pou_attrs}>\n"
    out += f"    <Declaration><![CDATA[{decl_text}]]></Declaration>\n"
    out += f"    <Implementation>\n"
    out += f"      <ST><![CDATA[{impl_text}]]></ST>\n"
    out += f"    </Implementation>\n"
    out += f"  </POU>\n"
    out += TCPLCOBJECT_TAIL
    return out


def _convert_one(src: Path, delete_xml: bool) -> bool:
    try:
        out_text = convert(src)
    except Exception as e:
        print(f"FAIL: {src}: {e}", file=sys.stderr)
        return False
    dst = src.with_suffix(".TcPOU")
    dst.write_text(out_text, encoding="utf-8")
    if delete_xml and dst.exists():
        src.unlink()
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", help="Single .xml file to convert")
    ap.add_argument("--all", action="store_true", help="Convert every examples/*.xml in repo")
    ap.add_argument("--delete-xml", action="store_true", help="After successful conversion, delete the source .xml")
    args = ap.parse_args()

    if args.all:
        xmls = sorted(ROOT.glob("*/examples/P_Demo_*.xml"))
        ok = fail = 0
        for f in xmls:
            if _convert_one(f, args.delete_xml):
                ok += 1
            else:
                fail += 1
        print(f"converted: {ok}, failed: {fail}, total: {len(xmls)}")
        return 0 if fail == 0 else 1

    if not args.path:
        ap.print_help()
        return 2
    src = Path(args.path).resolve()
    if not src.exists():
        print(f"not found: {src}", file=sys.stderr)
        return 2
    return 0 if _convert_one(src, args.delete_xml) else 1


if __name__ == "__main__":
    sys.exit(main())
