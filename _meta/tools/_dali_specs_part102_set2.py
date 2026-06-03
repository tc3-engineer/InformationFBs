#!/usr/bin/env python3
"""Generate remaining Set-Xxx FBs + power control + queries (batch)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))

from _dali_bulk_gen import write_pair  # noqa: E402

A_BASIC = (
    "    bStart           := bTrigger,\n"
    "    nAddr            := nLampAddr,\n"
    "    eAddrType        := eDALIV2AddrTypeShort,\n"
    "    eCommandPriority := eDALIV2CommandPriorityMiddle,"
)
D_BASIC = "    nLampAddr        : BYTE := 0;\n\n"
INFOSYS_BASE = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/"

SPECS = []

# --- SetShortAddress ---
SPECS.append({
    "name": "FB_DALIV2SetShortAddress",
    "section": "4.1.2.3.3.11",
    "subdir": "part102_low_config",
    "category_display": "Part 102 / Low-Level / Configuration",
    "infosys": f"{INFOSYS_BASE}142801803.html",
    "summary": (
        "**直接设置镇流器短地址的命令**——给当前已寻址（用 random addressing 找到）的灯具写入"
        "一个新的 short address。`nShortAddress` 范围 0..63，写入后灯具立即按新短地址应答。\n\n"
        "与 `FB_DALIV2ProgramShortAddress` 区别：本 FB 用于重新分配已有地址；后者用于初始寻址过程中"
        "写入第一个地址。"
    ),
    "inputs_desc": {
        "nShortAddress": "目标短地址 0..63（不可 64..254，那是无效范围）",
    },
    "behavior": (
        "**调用方式**：`bStart` 上升沿；本 FB 写 DTR0 = `nShortAddress` 经过特殊编码（DALI 协议要求"
        "`(nShortAddress << 1) | 1`），下发 `STORE THE DTR AS SHORT ADDRESS` 命令灯具更新短地址寄存器。\n\n"
        "**寻址模式要求**：本命令在 random addressing 序列中（已 SELECT 一盏灯）才能精确指定哪盏灯改地址。"
        "在普通模式下用 `eAddrType := Short` + 旧短地址寻址也行，但风险是写后旧地址失效，下一次寻址要"
        "重新校验。\n\n"
        "**EEPROM 写**：失电保护。\n\n"
        "**典型陷阱**：① `nShortAddress > 63` 灯具忽略；② 设到已被其它灯占用的短地址 → 总线上两盏灯同地址，"
        "命令冲突，必须重新寻址；③ 改完后用 `FB_DALIV2QueryShortAddress` 验证。"
    ),
    "pitfalls": [
        "`nShortAddress` 必须 0..63，64..254 灯具忽略。",
        "改地址前确认目标地址未被其它灯占用，否则总线冲突。",
        "通常在 random addressing 序列中调用（已 SELECT 一盏灯）。",
    ],
    "scenario": "DALI 寻址过程中给具体一盏灯写入设计文档规定的短地址（如把找到的某盏灯设为 short addr 5）。",
    "value": "替代厂家工具的 GUI 操作；PLC 程序里按设计表批量改地址。",
    "alternative": (
        "1) `FB_DALIV2ProgramShortAddress`：寻址过程中分配新地址；2) `FB_DALIV2SwapShortAddress`："
        "两灯地址交换；3) **本 FB**：直接覆盖单灯短地址。"
    ),
    "related": (
        "[`FB_DALIV2QueryShortAddress`](../part102_low_special/FB_DALIV2QueryShortAddress.md)、"
        "[`FB_DALIV2ProgramShortAddress`](../part102_low_special/FB_DALIV2ProgramShortAddress.md)、"
        "[`FB_DALIV2SwapShortAddress`](../part102_addressing/FB_DALIV2SwapShortAddress.md)"
    ),
    "tcpou_decls": D_BASIC + "    nNewShortAddr    : BYTE := 5;\n",
    "tcpou_inputs_assigns": A_BASIC + "\n    nShortAddress    := nNewShortAddr,",
    "tcpou_scenario": "给当前寻址到的灯写入 short address 5。",
    "tcpou_value": "DALI 寻址过程中固定地址；按设计表精确配置。",
    "tcpou_verify": (
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 必须先做 random addressing 流程让灯被 SELECT，本例简化只展示命令。\n"
        "3. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
        "4. 用 P_Demo_FB_DALIV2QueryShortAddress 应能用 short addr 5 查到这盏灯。"
    ),
})

# --- SetSystemFailureLevel ---
SPECS.append({
    "name": "FB_DALIV2SetSystemFailureLevel",
    "section": "4.1.2.3.3.12",
    "subdir": "part102_low_config",
    "category_display": "Part 102 / Low-Level / Configuration",
    "infosys": f"{INFOSYS_BASE}142803339.html",
    "summary": (
        "**设置镇流器 `SYSTEM FAILURE LEVEL` 寄存器**——DALI 总线物理失效（如 PLC 死机或 KL6821 断电）"
        "导致灯具长时间收不到命令时，灯具会自动调到 `SYSTEM FAILURE LEVEL` 值。"
        "类似 `POWER ON LEVEL`，但触发条件是 DALI 总线断、不是 220V 断。出厂默认 254（全亮）。"
    ),
    "inputs_desc": {
        "nFailureLevel": "目标 `SYSTEM FAILURE LEVEL`（0..254 或 MASK=255）。MASK 表示总线失效时灯具保持当前状态",
    },
    "behavior": (
        "**调用方式**：`bStart` 上升沿；本 FB 写 DTR0 = `nFailureLevel`，下发 `STORE THE DTR AS SYSTEM "
        "FAILURE LEVEL` 写入 EEPROM。\n\n"
        "**触发时机**：灯具在约 200..400 ms 收不到任何 DALI 命令（KL6821 / PLC 失联）后自动调到 "
        "`SYSTEM FAILURE LEVEL`。比 `POWER ON LEVEL` 更敏感——总线一旦失联立即生效。\n\n"
        "**典型应用**：① 应急照明法规：总线断时灯具自动全亮（254），保护逃生路径；② 普通办公照明："
        "总线断时维持当前亮度（MASK），让用户不感知；③ 装饰灯：总线断时关灯（0），节能。\n\n"
        "**与 KL6821 KBus watchdog 的关系**：KL6821 端子也有自己的 KBus 看门狗（K-Bus 主断时端子触发 "
        "DALI 命令）；`SYSTEM FAILURE LEVEL` 是灯具端独立的二级保险——KL6821 也死了灯具仍可自救。"
    ),
    "pitfalls": [
        "范围 0..254 或 MASK (255)。",
        "默认 254 在总线频繁短断时会大量全亮，慎选。",
        "应急照明法规可能强制要求非 MASK 值（如 193 = 75% 亮度），按法规配置。",
        "与 `FB_KL6821Config.eCommandKBusWatchdog` 协同——前者是端子自动发 DALI 命令；本 FB 是灯具自救。",
    ],
    "scenario": "医院应急照明：要求 DALI 总线断时灯具自动全亮 (254)，保护病人疏散通道。",
    "value": "灯具硬件层面的故障保险，PLC / 端子全挂时也能保证安全。",
    "alternative": (
        "1) `FB_KL6821Config.eCommandKBusWatchdog`：KL6821 端子层故障保险；2) **本 FB**：灯具层故障保险；"
        "两者并用形成两道防线。"
    ),
    "related": (
        "[`FB_DALIV2QuerySystemFailureLevel`](../part102_low_queries/FB_DALIV2QuerySystemFailureLevel.md)、"
        "[`FB_DALIV2SetPowerOnLevel`](FB_DALIV2SetPowerOnLevel.md)、"
        "[`FB_KL6821Config`](../kl6821_base/FB_KL6821Config.md)"
    ),
    "tcpou_decls": D_BASIC + "    nNewFailureLevel : BYTE := 254;\n",
    "tcpou_inputs_assigns": A_BASIC + "\n    nFailureLevel    := nNewFailureLevel,",
    "tcpou_scenario": "应急照明：把 SYSTEM FAILURE LEVEL 设为 254，总线断时灯全亮。",
    "tcpou_value": "灯具内置的故障保险，PLC 失效时仍保证安全照明。",
    "tcpou_verify": (
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
        "3. 用 P_Demo_FB_DALIV2QuerySystemFailureLevel 查 → 应为 254。\n"
        "4. 实测：把 KL6821 拔下来或断 K-Bus，等 ~400 ms → 灯具应自动全亮到 254。"
    ),
})

# --- StoreActualLevelInDTR0 ---
SPECS.append({
    "name": "FB_DALIV2StoreActualLevelInDTR0",
    "section": "4.1.2.3.3.13",
    "subdir": "part102_low_config",
    "category_display": "Part 102 / Low-Level / Configuration",
    "infosys": f"{INFOSYS_BASE}142804875.html",
    "summary": (
        "**把灯具当前实际亮度存到 DTR0 寄存器**——灯具读取自身 `ACTUAL DIM LEVEL` 寄存器值"
        "（即此刻物理亮度索引）并存入 DTR0。常用于把当前亮度作为新的 `POWER ON LEVEL` / "
        "`MAX VALUE` / 场景值——一气呵成完成调到舒服位置后定为某属性这套操作。"
    ),
    "behavior": (
        "**调用方式**：`bStart` 上升沿；本 FB 下发 `STORE ACTUAL LEVEL IN DTR` 命令；灯具内部把 "
        "`ACTUAL DIM LEVEL` 复制到 DTR0。DTR0 是灯具的临时寄存器，本身不失电保护，但可作为后续 "
        "`STORE DTR AS ...` 命令的源。\n\n"
        "**典型连贯用法**：（1）用户调光到舒适位置 → 调 `FB_DALIV2DirectArcPowerControl` 设亮度 →"
        "（2）调本 FB 把当前亮度存入 DTR0 → （3）调 `FB_DALIV2StoreDTRAsScene` 把 DTR0 写为某场景值。"
        "这套流程让用户调到喜欢的位置后告诉系统这就是场景 5 的亮度。\n\n"
        "**与 `FB_DALIV2QueryActualLevel` 区别**：后者读出来给 PLC，本 FB 只在灯具内部移动（DTR0 → "
        "灯具寄存器链）。本 FB 不返回亮度值。"
    ),
    "pitfalls": [
        "DTR0 本身不失电保护——本 FB 后必须跟随 `STORE DTR AS ...` 命令才能持久化。",
        "组 / 广播下发时所有灯都把各自亮度存入各自 DTR0，跨灯亮度不汇总（DTR0 是每灯独立的）。",
        "本 FB 不返回亮度值——要读到 PLC 用 `FB_DALIV2QueryActualLevel`。",
    ],
    "scenario": (
        "智能家居记录当前亮度为场景功能：用户调光到舒适位置（用面板或 HMI），按保存为场景 3 按钮，"
        "PLC 先调本 FB 把当前亮度存到 DTR0，再调 `FB_DALIV2StoreDTRAsScene`（不在本仓库范围，"
        "用 `FB_DALIV2SetScene` 等效）把场景 3 设为该亮度。"
    ),
    "value": "替代『先查亮度 再下发 SetScene』两步操作，灯具内部一气呵成。",
    "alternative": (
        "1) `FB_DALIV2QueryActualLevel` + 应用层拿到值 + `FB_DALIV2SetScene` 写场景：两次命令更慢；"
        "2) **本 FB** + 后续 `StoreDTRAsScene`：灯具内一气呵成。"
    ),
    "related": (
        "[`FB_DALIV2QueryActualLevel`](../part102_low_queries/FB_DALIV2QueryActualLevel.md)、"
        "[`FB_DALIV2SetScene`](FB_DALIV2SetScene.md)、"
        "[`FB_DALIV2SetDTR0`](../part102_low_special/FB_DALIV2SetDTR0.md)"
    ),
    "tcpou_decls": D_BASIC,
    "tcpou_inputs_assigns": A_BASIC,
    "tcpou_scenario": "用户调好亮度后存为场景的第一步：把当前亮度存到 DTR0。",
    "tcpou_value": "灯具内一气呵成读 + 存，省去两次命令。",
    "tcpou_verify": (
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 先用 P_Demo_FB_DALIV2DirectArcPowerControl 把 short addr 0 调到 150。\n"
        "3. 调用本 FB 一次上升沿；等 bBusy 回 FALSE。\n"
        "4. 用 P_Demo_FB_DALIV2QueryContentDTR0 → 应读出 150。"
    ),
})


def main():
    for spec in SPECS:
        doc_path, tcpou_path = write_pair(spec)
        print(f"  {doc_path.name}")
        print(f"  {tcpou_path.name}")


if __name__ == "__main__":
    main()
