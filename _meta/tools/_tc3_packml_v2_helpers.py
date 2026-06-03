#!/usr/bin/env python3
"""Helpers for the Tc3_PackML_V2 doc + TcPOU generation.

Provides:
  - stable_guid(name): library-namespaced GUID per CLAUDE.md/Wave-2 brief.

Used by hand-crafted generators in this library only. Does not modify any
shared tools.
"""
from __future__ import annotations

import uuid


_NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def stable_guid(name: str) -> str:
    """Return '{GUID}' for P_Demo_<name> namespaced to the Tc3_PackML_V2 library."""
    key = f"tc3-libraries-kb/Tc3_PackML_V2/P_Demo_{name}"
    return "{" + str(uuid.uuid5(_NS, key)) + "}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("usage: _tc3_packml_v2_helpers.py <P_Demo_target_name>", file=sys.stderr)
        sys.exit(2)
    print(stable_guid(sys.argv[1]))
