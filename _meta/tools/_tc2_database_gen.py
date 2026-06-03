#!/usr/bin/env python3
"""Tc2_Database 库内文档生成 helper（库名隔离脚本）。

用法（手动驱动）：
    python3 _meta/tools/_tc2_database_gen.py guid <Name>

主要作用是给所有 P_Demo_<Name>.TcPOU 生成稳定 UUID5；文档 / 例程文本本身由
session 直接 Write 写出（每篇都有手工润色的中文叙述）。
"""
from __future__ import annotations

import sys
import uuid


def stable_guid(name: str) -> str:
    return "{" + str(
        uuid.uuid5(
            uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8"),
            f"tc3-libraries-kb/Tc2_Database/P_Demo_{name}",
        )
    ) + "}"


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] != "guid":
        print("usage: _tc2_database_gen.py guid <Name>", file=sys.stderr)
        return 2
    print(stable_guid(sys.argv[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
