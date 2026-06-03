#!/usr/bin/env python3
"""Generate multiple more FBs in a single batch."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))

from _dali_bulk_gen import write_pair  # noqa: E402

INFOSYS_BASE = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/"

A_BASIC = (
    "    bStart           := bTrigger,\n"
    "    nAddr            := nLampAddr,\n"
    "    eAddrType        := eDALIV2AddrTypeShort,\n"
    "    eCommandPriority := eDALIV2CommandPriorityMiddle,"
)
D_BASIC = "    nLampAddr        : BYTE := 0;\n\n"

SPECS = []

# === Special commands ===
SPECS.append({
    "name": "FB_DALIV2SetDTR0",
    "section": "4.1.2.3.6.11",
    "subdir": "part102_low_special",
    "category_display": "Part 102 / Low-Level / Special",
    "infosys": f"{INFOSYS_BASE}142826635.html",
    "summary": (
        "**写灯具 DTR0 临时寄存器**——DTR0 是 DALI 灯具内一字节临时寄存器，用作各种 `STORE DTR AS ...` "
        "命令的源（如 `STORE DTR AS MAX LEVEL`、`STORE DTR AS GROUPS 0-7`）。本 FB 直接把"
        "`nValue` 写入 DTR0。\n\n"
        "通常作为更高层 `FB_DALIV2SetXxx` FB 的底层基础——那些 FB 内部先调本 FB 再发 STORE 命令。"
        "工程上很少直接用本 FB，但需要做厂家特殊命令（如某厂家用 DTR0 传特殊参数）时直接调用。"
    ),
    "inputs_desc": {"nValue": "要写入 DTR0 的值（0..255）"},
    "behavior": (
        "**调用方式**：`bStart` 上升沿；本 FB 下发 `SET DTR` 命令带数据字节 `nValue`；灯具更新 DTR0。\n\n"
        "**DTR0 是临时的**——不失电保护；下次 `SET DTR` 命令立即覆盖。后续要让值持久必须配套 `STORE "
        "DTR AS ...` 命令把 DTR0 写入对应失电保护寄存器。\n\n"
        "**典型应用**：① 配合厂家自定义命令（部分厂家 DALI 设备用 DTR0 传特殊参数）；② 调试时手动"
        "构造 STORE 序列；③ `FB_DALIV2SetXxx` 高层 FB 内部使用。\n\n"
        "**典型陷阱**：① 设 DTR0 后必须立即（同优先级队列）发 STORE 命令——否则可能被其它 FB 的 SET "
        "DTR 覆盖；② 多 FB 都用 DTR0 时优先级 / 顺序要小心。"
    ),
    "pitfalls": [
        "DTR0 不失电保护，下次 SET DTR 覆盖。",
        "设 DTR0 后必须紧跟 STORE 命令——同优先级队列保证顺序。",
        "工程上很少直接用，通常通过 `FB_DALIV2SetXxx` 间接使用。",
    ],
    "scenario": "调试或厂家特殊命令——直接写 DTR0 然后发自定义 STORE 命令。",
    "value": "暴露 DALI 协议底层 DTR0 寄存器；为厂家特殊命令提供基础。",
    "alternative": (
        "1) `FB_DALIV2SetFadeTime` / SetMaxLevel 等：高层 FB 已自动用 DTR0；2) **本 FB**：底层调试 / 自定义。"
    ),
    "related": (
        "[`FB_DALIV2SetDTR1`](FB_DALIV2SetDTR1.md)、"
        "[`FB_DALIV2SetDTR2`](FB_DALIV2SetDTR2.md)、"
        "[`FB_DALIV2QueryContentDTR0`](../part102_low_queries/FB_DALIV2QueryContentDTR0.md)"
    ),
    "tcpou_decls": D_BASIC + "    nDTR0Value       : BYTE := 100;\n",
    "tcpou_inputs_assigns": A_BASIC + "\n    nValue           := nDTR0Value,",
    "tcpou_scenario": "直接写 short addr 0 的 DTR0 为 100，可后续用 STORE 命令固化为某属性。",
    "tcpou_value": "底层 DTR0 操作。",
    "tcpou_verify": (
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
        "3. 用 P_Demo_FB_DALIV2QueryContentDTR0 → 应读出 100。"
    ),
})

SPECS.append({
    "name": "FB_DALIV2SetDTR1",
    "section": "4.1.2.3.6.12",
    "subdir": "part102_low_special",
    "category_display": "Part 102 / Low-Level / Special",
    "infosys": f"{INFOSYS_BASE}142828171.html",
    "summary": (
        "**写灯具 DTR1 临时寄存器**——与 DTR0 类似但用于不同场合（部分扩展命令需要 DTR1）。"
        "本 FB 直接写 `nValue` 到 DTR1。"
    ),
    "inputs_desc": {"nValue": "要写入 DTR1 的值（0..255）"},
    "behavior": (
        "**调用方式**：`bStart` 上升沿；下发 `SET DTR1` 命令带数据字节。\n\n"
        "**DTR1 用途**：DALI 2 (IEC 62386) 引入了 DTR1 / DTR2 作为 DTR0 的补充——某些扩展命令（如"
        "颜色控制、内存访问）需要多个字节参数，分别放在 DTR0 / DTR1 / DTR2。\n\n"
        "**典型应用**：颜色控制 FB 内部、内存访问 FB 内部、厂家特殊扩展命令。工程上很少直接用。\n\n"
        "**典型陷阱**：同 DTR0——临时寄存器、不失电保护、需要紧跟 STORE 命令。"
    ),
    "pitfalls": ["同 DTR0：临时、不失电、需配套 STORE 命令。"],
    "scenario": "扩展命令（如颜色控制）的底层操作。",
    "value": "暴露 DTR1 寄存器。",
    "alternative": "通过 `FB_DALIV2WriteMemoryLocation` / 颜色 FB 间接使用。",
    "related": (
        "[`FB_DALIV2SetDTR0`](FB_DALIV2SetDTR0.md)、"
        "[`FB_DALIV2SetDTR2`](FB_DALIV2SetDTR2.md)、"
        "[`FB_DALIV2QueryContentDTR1`](../part102_low_queries/FB_DALIV2QueryContentDTR1.md)"
    ),
    "tcpou_decls": D_BASIC + "    nDTR1Value       : BYTE := 50;\n",
    "tcpou_inputs_assigns": A_BASIC + "\n    nValue           := nDTR1Value,",
    "tcpou_scenario": "底层写 DTR1。",
    "tcpou_value": "底层操作。",
    "tcpou_verify": (
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
        "3. 用 P_Demo_FB_DALIV2QueryContentDTR1 → 应读出 50。"
    ),
})

SPECS.append({
    "name": "FB_DALIV2SetDTR2",
    "section": "4.1.2.3.6.13",
    "subdir": "part102_low_special",
    "category_display": "Part 102 / Low-Level / Special",
    "infosys": f"{INFOSYS_BASE}142829707.html",
    "summary": "**写灯具 DTR2 临时寄存器**——同 DTR1，用于需要 3 个字节参数的扩展命令。",
    "inputs_desc": {"nValue": "要写入 DTR2 的值（0..255）"},
    "behavior": (
        "**调用方式**：`bStart` 上升沿；下发 `SET DTR2` 命令。\n\n"
        "**DTR2 用途**：与 DTR0/DTR1 组合实现 3 字节参数命令（如 24-bit 地址扩展、颜色 xy 坐标等）。"
        "在 Part 209 颜色控制命令族里，DTR0 / DTR1 / DTR2 分别承载颜色 xy 坐标的 LSB / 中间字节 / MSB，"
        "组成完整 16-bit 色坐标值。\n\n"
        "**典型应用**：颜色控制 FB 内部、内存访问 FB 内部、扩展命令传 24-bit 内存地址等。\n\n"
        "**典型陷阱**：同 DTR0 / DTR1——临时寄存器、不失电保护、需要紧跟相应 STORE / 命令；"
        "DTR0/1/2 三个写入要保证顺序（同优先级队列保证 FIFO）。"
    ),
    "pitfalls": ["同 DTR0/DTR1：临时、不失电、需配套 STORE。"],
    "scenario": "需要 3 字节参数的扩展命令底层操作。",
    "value": "暴露 DTR2 寄存器。",
    "alternative": "通过高层 FB 间接使用。",
    "related": (
        "[`FB_DALIV2SetDTR0`](FB_DALIV2SetDTR0.md)、"
        "[`FB_DALIV2SetDTR1`](FB_DALIV2SetDTR1.md)、"
        "[`FB_DALIV2QueryContentDTR2`](../part102_low_queries/FB_DALIV2QueryContentDTR2.md)"
    ),
    "tcpou_decls": D_BASIC + "    nDTR2Value       : BYTE := 25;\n",
    "tcpou_inputs_assigns": A_BASIC + "\n    nValue           := nDTR2Value,",
    "tcpou_scenario": "底层写 DTR2。",
    "tcpou_value": "底层操作。",
    "tcpou_verify": (
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
        "3. 用 P_Demo_FB_DALIV2QueryContentDTR2 → 应读出 25。"
    ),
})


def main():
    for spec in SPECS:
        doc_path, tcpou_path = write_pair(spec)
        print(f"  {doc_path.name}")


if __name__ == "__main__":
    main()
