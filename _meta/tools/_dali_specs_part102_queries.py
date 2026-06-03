#!/usr/bin/env python3
"""Generate Part 102 low-level Query FBs."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))

from _dali_bulk_gen import write_pair  # noqa: E402

A_BASIC = (
    "    bStart           := bTrigger,\n"
    "    nAddr            := nLampAddr,\n"
    "    eAddrType        := eDALIV2AddrTypeShort,\n"
    "    eCommandPriority := eDALIV2CommandPriorityLow,"
)
D_BASIC = "    nLampAddr        : BYTE := 0;\n\n"
INFOSYS_BASE = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/"

CAT = "Part 102 / Low-Level / Queries"
SUBDIR = "part102_low_queries"

SPECS = []

# Query that returns just a BYTE value
SIMPLE_QUERIES = [
    ("FB_DALIV2QueryActualLevel", "4.1.2.3.5.1", "142784395",
        "查询灯具当前实际亮度（`ACTUAL DIM LEVEL` 寄存器，0..254）",
        "nQueryData",
        "当前实际亮度值（0..254），即灯此刻物理输出索引"),
    ("FB_DALIV2QueryContentDTR0", "4.1.2.3.5.2", "142785931",
        "查询灯具 DTR0 临时寄存器当前内容（0..255）",
        "nQueryData", "DTR0 当前值（0..255）"),
    ("FB_DALIV2QueryContentDTR1", "4.1.2.3.5.3", "142787467",
        "查询灯具 DTR1 临时寄存器当前内容",
        "nQueryData", "DTR1 当前值（0..255）"),
    ("FB_DALIV2QueryContentDTR2", "4.1.2.3.5.4", "142789003",
        "查询灯具 DTR2 临时寄存器当前内容",
        "nQueryData", "DTR2 当前值（0..255）"),
    ("FB_DALIV2QueryDeviceType", "4.1.2.3.5.6", "142792075",
        "查询灯具设备类型（DALI Part 207=LED / Part 202=应急 / Part 203=HID 等 IEC 62386 子规范号）",
        "nQueryData", "设备类型号（0..255，0 = 普通荧光镇流器，1 = 应急照明 Part 202，2 = HID 灯 Part 203，6 = LED 模块 Part 207，8 = 色温 / 颜色 Part 209）"),
    ("FB_DALIV2QueryFadeTimeFadeRate", "4.1.2.3.5.7", "142793611",
        "查询灯具 FADE TIME（高 4 bit）+ FADE RATE（低 4 bit）合一字节",
        "nQueryData", "高 4 bit = FADE TIME 索引（0..15），低 4 bit = FADE RATE 索引（1..15）。例如 `0x47` = FADE TIME 4 + FADE RATE 7（出厂默认）"),
    ("FB_DALIV2QueryGroups0UpTo7", "4.1.2.3.5.9", "142796683",
        "查询灯具组归属 bit 0..7（即属于哪些组 0..7）",
        "nQueryData", "8-bit 位图，bit n = 1 表示灯属于组 n"),
    ("FB_DALIV2QueryGroups8UpTo15", "4.1.2.3.5.10", "142798219",
        "查询灯具组归属 bit 8..15",
        "nQueryData", "8-bit 位图，bit n 对应组 8+n"),
    ("FB_DALIV2QueryMaxLevel", "4.1.2.3.5.14", "142804363",
        "查询灯具 `MAX VALUE` 寄存器",
        "nQueryData", "MAX VALUE（1..254）"),
    ("FB_DALIV2QueryMinLevel", "4.1.2.3.5.15", "142805899",
        "查询灯具 `MIN VALUE` 寄存器",
        "nQueryData", "MIN VALUE（1..254）"),
    ("FB_DALIV2QueryPhysicalMinLevel", "4.1.2.3.5.17", "142808971",
        "查询灯具硬件 `PHYSICAL MIN LEVEL`（厂家固化的最低可点亮亮度）",
        "nQueryData", "灯具物理最暗亮度索引——任何 MIN VALUE 设到低于此值的灯具行为不确定"),
    ("FB_DALIV2QueryPowerOnLevel", "4.1.2.3.5.19", "142812043",
        "查询灯具 `POWER ON LEVEL` 寄存器",
        "nQueryData", "POWER ON LEVEL（0..254 或 MASK 255）"),
    ("FB_DALIV2QuerySystemFailureLevel", "4.1.2.3.5.27", "142824331",
        "查询灯具 `SYSTEM FAILURE LEVEL` 寄存器",
        "nQueryData", "SYSTEM FAILURE LEVEL（0..254 或 MASK 255）"),
    ("FB_DALIV2QueryVersionNumber", "4.1.2.3.5.28", "142825867",
        "查询灯具 DALI 协议版本号（高 4 bit 主版本，低 4 bit 副版本）",
        "nQueryData", "版本号字节，例如 0x10 = v1.0（DALI 1）；0x20 = v2.0（DALI 2）"),
    ("FB_DALIV2QueryGroups", "4.1.2.3.5.8", "142795147",
        "查询灯具完整组归属（合并 0-7 + 8-15 为 WORD）",
        "wGroups", "16-bit 位图，bit n = 1 表示灯属于组 n（n = 0..15）"),
    ("FB_DALIV2QueryRandomAddress", "4.1.2.3.5.20", "142813579",
        "查询灯具 `RANDOM ADDRESS` 寄存器（24-bit 随机地址，寻址过程用）",
        "dwQueryData", "24-bit 随机地址（DWORD 低 24 位有效）"),
    ("FB_DALIV2QuerySceneLevel", "4.1.2.3.5.25", "142821259",
        "查询灯具某场景对应亮度值",
        "nQueryData", "对应场景 `nScene` 的亮度值（0..254 或 MASK=255）"),
    ("FB_DALIV2QueryStatus", "4.1.2.3.5.26", "142822795",
        "查询灯具状态字节（8 个状态位的位图）",
        "nQueryData", "8-bit 状态位图：bit0=控制器存在 / bit1=灯故障 / bit2=灯亮 / bit3=限值错 / bit4=Fade 中 / bit5=Reset 状态 / bit6=短地址未设 / bit7=电源故障"),
    ("FB_DALIV2QueryRandomAddressH", "4.1.2.3.5.21", "142815115",
        "查询灯具 `RANDOM ADDRESS` 高字节",
        "nQueryData", "RANDOM ADDRESS 高字节（bit 16..23）"),
    ("FB_DALIV2QueryRandomAddressM", "4.1.2.3.5.23", "142818187",
        "查询灯具 `RANDOM ADDRESS` 中字节",
        "nQueryData", "RANDOM ADDRESS 中字节（bit 8..15）"),
    ("FB_DALIV2QueryRandomAddressL", "4.1.2.3.5.22", "142816651",
        "查询灯具 `RANDOM ADDRESS` 低字节",
        "nQueryData", "RANDOM ADDRESS 低字节（bit 0..7）"),
]

for name, section, topicid, summary_short, query_field, query_desc in SIMPLE_QUERIES:
    SPECS.append({
        "name": name,
        "section": section,
        "subdir": SUBDIR,
        "category_display": CAT,
        "infosys": f"{INFOSYS_BASE}{topicid}.html",
        "summary": (
            f"**查询命令**——{summary_short}。本 FB 通过 DALI 总线查询灯具内部寄存器，"
            f"通过 `{query_field}` 输出当前值。属于 IEC 62386 Part 102 控制设备（control gear）查询命令族。\n\n"
            "查询命令属于低优先级流量，建议用 `eCommandPriority = Low` 避免抢占调光命令带宽。"
        ),
        "outputs_desc": {
            query_field: query_desc,
            "bQueryData": "查询布尔结果（如适用）",
        },
        "behavior": (
            f"**调用方式**：`bStart` 上升沿；本 FB 下发对应 DALI 查询命令；灯具应答数据"
            f"通过 `FB_KL68x1Communication` 接收后填入 `{query_field}` 输出，`bBusy` 回 FALSE。\n\n"
            "**优先级建议**：查询命令耗 DALI 带宽且非时序敏感，建议用 `eCommandPriority := Low`，"
            "让调光等关键命令优先派发。\n\n"
            "**广播查询限制**：与所有 DALI 查询命令一样，本 FB 在广播寻址下结果不可靠——多盏灯同时应答会冲突。"
            "查询必须用 `eAddrType := Short` 单灯寻址。\n\n"
            "**典型应用**：HMI 显示当前灯状态；上线后批量检查所有灯配置是否符合工程文档；运行时定期巡检。\n\n"
            "**典型陷阱**：① 广播查询无意义，结果冲突；② 灯具离线时本 FB 会超时（约 100..500 ms），"
            "`bError` 置 TRUE；③ 高频查询占用 DALI 带宽——巡检循环周期 1..5 秒比较合理。"
        ),
        "pitfalls": [
            "查询必须单灯寻址（`eAddrType := Short`），广播 / 组寻址结果冲突。",
            "优先级建议 `Low`，避免抢占调光命令带宽。",
            "灯具离线时 `bError = TRUE`，`nErrorId` 提示超时。",
            "高频查询占用 DALI 带宽——巡检间隔不应小于 1 秒。",
        ],
        "scenario": (
            f"HMI 显示当前灯具状态——巡检循环每秒对所有在线短地址依次调本 FB 读 {summary_short}，"
            f"刷新 HMI 上的当前值显示。"
        ),
        "value": (
            "替代 PLC 自行解析 DALI 应答字节流；本 FB 自动处理 DALI 协议层的查询请求 / 应答握手。"
        ),
        "alternative": (
            "1) `FB_DALIV2GetSettings` 一次查多个寄存器：批量查询时效率更高；"
            "2) **本 FB**：单一寄存器的轻量查询。"
        ),
        "related": "见 `FB_DALIV2GetSettings`（批量查询）、`FB_DALIV2SetXxx` 对应配置命令",
        "tcpou_decls": D_BASIC + f"    {query_field:<16} : BYTE;\n" if query_field == "nQueryData" else D_BASIC + f"    wQueryGroups     : WORD;\n",
        "tcpou_inputs_assigns": A_BASIC,
        "tcpou_scenario": f"巡检读取 short addr 0 的 {summary_short}。",
        "tcpou_value": "HMI 实时显示 / 上线批量校验用。",
        "tcpou_verify": (
            "1. 通信 FB 跑起；编译；登录。\n"
            "2. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
            f"3. 观察 fb{name}.{query_field} 应为预期值（参考本 FB 文档 §4 描述）。"
        ),
    })

# Queries with BOOL result (lamp present, lamp failure, etc.)
BOOL_QUERIES = [
    ("FB_DALIV2QueryControlGearPresent", "4.1.2.3.5.5", "142790539",
        "查询灯具是否在线（应答 = 在线）",
        "确认 DALI 总线上是否存在指定短地址的灯具"),
    ("FB_DALIV2QueryLampFailure", "4.1.2.3.5.11", "142799755",
        "查询灯具是否报告灯泡故障",
        "TRUE = 灯泡损坏或灯具自检失败"),
    ("FB_DALIV2QueryLampPowerOn", "4.1.2.3.5.12", "142801291",
        "查询灯具是否当前点亮（亮度 > 0）",
        "TRUE = 灯当前点亮"),
    ("FB_DALIV2QueryLimitError", "4.1.2.3.5.13", "142802827",
        "查询灯具是否出现限值错（命令值越界）",
        "TRUE = 最近命令违反了 MIN/MAX VALUE 约束被钳位"),
    ("FB_DALIV2QueryMissingShortAddress", "4.1.2.3.5.16", "142807435",
        "查询灯具是否丢失短地址（短地址 = MASK）",
        "TRUE = 灯具未配置短地址（出厂状态 / 被 Reset 后）"),
    ("FB_DALIV2QueryPowerFailure", "4.1.2.3.5.18", "142810507",
        "查询灯具是否经历过电源故障（自上次查询以来）",
        "TRUE = 灯具检测到电源中断（自检读位后自动清零）"),
    ("FB_DALIV2QueryResetState", "4.1.2.3.5.24", "142819723",
        "查询灯具是否处于复位状态（所有寄存器为默认）",
        "TRUE = 灯具所有寄存器为出厂默认（刚 Reset 后）"),
]

for name, section, topicid, summary_short, desc_short in BOOL_QUERIES:
    SPECS.append({
        "name": name,
        "section": section,
        "subdir": SUBDIR,
        "category_display": CAT,
        "infosys": f"{INFOSYS_BASE}{topicid}.html",
        "summary": (
            f"**查询命令（布尔结果）**——{summary_short}。{desc_short}。"
            f"属于 IEC 62386 Part 102 控制设备查询命令族。建议用低优先级避免抢占调光命令带宽。"
        ),
        "outputs_desc": {
            "bQueryData": f"查询结果：{desc_short}",
            "nQueryData": "保留位（部分查询用）",
        },
        "behavior": (
            f"**调用方式**：`bStart` 上升沿；本 FB 下发查询命令；灯具应答（YES / NO）填入"
            "`bQueryData` 输出。\n\n"
            "**用 Yes/No 应答的 DALI 查询特殊性**：DALI 协议对布尔查询用前向应答机制——灯具"
            "在收到查询命令的瞬间用一个固定字节（`0xFF` = YES，无应答 = NO）回应。所以即便"
            "灯具不在线（无应答），本 FB 也会 `bQueryData = FALSE`——区分『灯具不在线』与"
            "『灯具说 NO』需要配合 `FB_DALIV2QueryControlGearPresent`。\n\n"
            "**广播查询**：本 FB 也可广播——如果总线上至少有一盏灯应答 YES 则 `bQueryData = TRUE`。"
            "适合『有没有任何灯具故障』这种群体诊断查询。\n\n"
            "**典型应用**：HMI 显示灯故障指示灯；运行时巡检；上线时检测所有灯是否在线。\n\n"
            "**典型陷阱**：① 不能区分『不在线』与『说 NO』——必要时先用 `QueryControlGearPresent` 确认在线；"
            "② 某些状态位读后自动清零（如 `QueryPowerFailure`），读完再读得到 FALSE。"
        ),
        "pitfalls": [
            "本 FB 返回 FALSE 不能区分『不在线』与『说 NO』——配合 `FB_DALIV2QueryControlGearPresent` 区分。",
            "部分查询读后自动清零（PowerFailure 等）。",
            "广播查询返回『总线上任一灯具说 YES』，适合群体诊断。",
        ],
        "scenario": f"运行时巡检 / HMI 灯故障指示——{summary_short}。",
        "value": "替代 PLC 自行解析 DALI 应答帧；自动处理 YES/NO 应答语义。",
        "alternative": (
            "1) `FB_DALIV2QueryStatus`：一次读全部 8 个状态位；"
            "2) **本 FB**：单独读某个状态位（语义清晰）。"
        ),
        "related": (
            "[`FB_DALIV2QueryStatus`](FB_DALIV2QueryStatus.md)（一次读全部状态）"
        ),
        "tcpou_decls": D_BASIC + "    bResult          : BOOL;\n",
        "tcpou_inputs_assigns": A_BASIC,
        "tcpou_scenario": f"巡检 short addr 0：{summary_short}。",
        "tcpou_value": "HMI 显示用。",
        "tcpou_verify": (
            "1. 通信 FB 跑起；编译；登录。\n"
            "2. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
            f"3. 观察 fb{name}.bQueryData 应为预期值（参考本 FB 文档 §4 描述）。"
        ),
    })


def main():
    for spec in SPECS:
        doc_path, tcpou_path = write_pair(spec)
        print(f"  {doc_path.name}")


if __name__ == "__main__":
    main()
