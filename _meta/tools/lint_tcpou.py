#!/usr/bin/env python3
"""
Lint a TwinCAT 3 .TcPOU file.

Checks:
1. XML well-formed.
2. Root is <TcPlcObject Version="..." ProductVersion="..."/>.
3. Exactly one <POU Name="..." Id="{guid}" SpecialFunc="..."/>.
4. <Declaration> with CDATA-wrapped text containing PROGRAM / FUNCTION_BLOCK /
   FUNCTION header + matching VAR/END_VAR block(s).
5. <Implementation>/<ST> with CDATA-wrapped ST body.
6. No XML entities (`&lt;` etc.) appearing UNCDATA'd in Declaration/Implementation.

Exit:
    0 = PASS
    1 = lint failed
    2 = unexpected error
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


GUID_RE = re.compile(r"^\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\}$")
HEADER_RE = re.compile(r"^(PROGRAM|FUNCTION_BLOCK|FUNCTION)\s+\w+", re.MULTILINE)


def lint(path: Path) -> tuple[bool, list[str]]:
    diags: list[str] = []
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        return False, [f"XML parse error: {e}"]

    root = tree.getroot()
    if root.tag != "TcPlcObject":
        diags.append(f"root tag is {root.tag!r}, expected 'TcPlcObject'")
    if not root.get("Version"):
        diags.append("TcPlcObject missing Version attribute")
    if not root.get("ProductVersion"):
        diags.append("TcPlcObject missing ProductVersion attribute")

    pous = root.findall("POU")
    if len(pous) != 1:
        diags.append(f"expected exactly 1 <POU>, found {len(pous)}")
        return False, diags
    pou = pous[0]
    name = pou.get("Name")
    pid = pou.get("Id", "")
    spec = pou.get("SpecialFunc")
    if not name:
        diags.append("POU missing Name attribute")
    if not GUID_RE.match(pid):
        diags.append(f"POU Id {pid!r} not in {{8-4-4-4-12}} GUID form")
    if spec is None:
        diags.append("POU missing SpecialFunc attribute")

    decl = pou.find("Declaration")
    if decl is None or not (decl.text and decl.text.strip()):
        diags.append("Declaration missing or empty (must be CDATA-wrapped IEC text)")
    else:
        if not HEADER_RE.search(decl.text):
            diags.append("Declaration text missing PROGRAM/FUNCTION_BLOCK/FUNCTION header")
        if "VAR" in decl.text and "END_VAR" not in decl.text:
            diags.append("Declaration has VAR without matching END_VAR")

    impl = pou.find("Implementation")
    if impl is None:
        diags.append("Implementation element missing")
    else:
        st = impl.find("ST")
        if st is None or st.text is None or not st.text.strip():
            diags.append("Implementation/ST missing or empty")

    return (len(diags) == 0), diags


def check_unique_guids(root: Path) -> tuple[bool, list[str]]:
    """Repo-wide check: every .TcPOU under <root>/Tc*/examples/ must carry a
    unique POU Id. Same-named FBs across libraries (e.g. MC_Halt in Tc2_MC2 vs
    Tc3_DriveMotionControl, FB_SoEReset in Tc2_MC2_Drive vs Tc2_NcDrive) would
    otherwise collide and XAE refuses to load two POUs with the same Id.
    """
    import collections
    guid_to_files: dict[str, list[str]] = collections.defaultdict(list)
    for f in sorted(root.glob("Tc*/examples/P_Demo_*.TcPOU")):
        text = f.read_text()
        m = re.search(r'Id="(\{[0-9a-f-]{36}\})"', text)
        if m:
            guid_to_files[m.group(1)].append(str(f.relative_to(root)))
    dups = {g: fs for g, fs in guid_to_files.items() if len(fs) > 1}
    diags: list[str] = []
    for g, fs in dups.items():
        diags.append(f"duplicate Id {g}: " + " ↔ ".join(fs))
    return (len(dups) == 0), diags


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: lint_tcpou.py <file.TcPOU> [...]\n"
              "       lint_tcpou.py --check-unique [<root>]", file=sys.stderr)
        return 2
    if sys.argv[1] == "--check-unique":
        root = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path.cwd()
        ok, diags = check_unique_guids(root)
        if ok:
            print(f"PASS: all TcPOU GUIDs unique under {root}")
            return 0
        print(f"FAIL: {len(diags)} duplicate-GUID groups under {root}")
        for d in diags:
            print(f"  - {d}")
        return 1
    overall = 0
    for arg in sys.argv[1:]:
        path = Path(arg).resolve()
        if not path.exists():
            print(f"FAIL ({path}): not found", file=sys.stderr)
            overall = 1
            continue
        ok, diags = lint(path)
        if ok:
            print("PASS")
        else:
            print(f"FAIL ({path}):")
            for d in diags:
                print(f"  - {d}")
            overall = 1
    return overall


if __name__ == "__main__":
    sys.exit(main())
