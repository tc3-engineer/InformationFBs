#!/usr/bin/env python3
"""Helper: generate stable GUID + TcPOU skeleton for Tc2_BACnet entries.

Only used during Tc2_BACnet doc generation. Not a public tool.
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

LIBRARY = "Tc2_BACnet"
NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # DNS namespace
ROOT = Path(__file__).resolve().parents[2]


def stable_guid(name: str) -> str:
    """Same algorithm as _meta/tools/plcopen_to_tcpou.py::_stable_guid."""
    path = f"tc3-libraries-kb/{LIBRARY}/{name}"
    return "{" + str(uuid.uuid5(NS, path)) + "}"


def render_tcpou(pou_name: str, decl_body: str, st_body: str) -> str:
    """Render a TwinCAT 3 .TcPOU XML with CDATA Declaration + Implementation."""
    guid = stable_guid(pou_name)
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">\n'
        f'  <POU Name="{pou_name}" Id="{guid}" SpecialFunc="None">\n'
        f'    <Declaration><![CDATA[PROGRAM {pou_name}\n'
        f'{decl_body}\n'
        ']]></Declaration>\n'
        '    <Implementation>\n'
        f'      <ST><![CDATA[{st_body}\n'
        ']]></ST>\n'
        '    </Implementation>\n'
        '  </POU>\n'
        '</TcPlcObject>\n'
    )


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "guid":
        print(stable_guid(sys.argv[2]))
