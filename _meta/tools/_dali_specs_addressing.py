#!/usr/bin/env python3
"""Generate Part 102 / Addressing high-level FBs."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))

from _dali_bulk_gen import write_pair  # noqa: E402

INFOSYS_BASE = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/"

SPECS = []

SPECS.append({
    "name": "FB_DALIV2AddressingRandomAddressing",
    "section": "4.1.1.1.1.3",
    "subdir": "part102_addressing",
    "category_display": "Part 102 / Addressing (High-Level)",
    "infosys": f"{INFOSYS_BASE}142884107.html",
    "summary": (
        "**DALI 控制设备随机寻址（high-level）**——本 FB 是 DALI 寻址流程的完整封装。"
        "把所有未寻址（即短地址为 MASK）的镇流器按内部随机算法分配短地址（顺序 / 自定义起点）。"
        "整个流程几分钟到十几分钟（取决于灯数），过程中 PLC 可观察 `nAddressedDevices` 实时累加。"
        "**比 `FB_DALIV2AddressingIntRandomAddressing` 更慢，但提供过程反馈和提前终止能力。**"
    ),
    "inputs_desc": {
        "bStart": "上升沿启动寻址流程",
        "bAbort": "上升沿提前终止寻址（已分配的地址保留）",
        "nStartWithShortAddress": "第一盏灯的短地址（其它灯依次递增）",
        "nOptions": "选项位（按 OR 组合 `DALIV2_OPTION_*` 常量）：全新寻址 / 删除原组归属 / 删除原场景 / 视觉反馈",
    },
    "outputs_desc": {
        "bBusy": "寻址流程进行中",
        "bError": "寻址出错",
        "nErrorId": "错误号",
        "nAddressedDevices": "已成功分配短地址的灯数（实时累加）",
        "bDone": "寻址完成（成功 / 失败均算）",
    },
    "behavior": (
        "**整体流程**：本 FB 内部调一系列低层 DALI 命令完成 IEC 62386 Part 102 章节 11.2 描述的标准"
        "二分搜索寻址流程：（1）`Reset`（如果 `OPTION_COMPLETE_NEW_INSTALLATION` 置位）；"
        "（2）`Randomise` 让所有灯生成 24-bit 随机地址；（3）循环用 `SearchAddrH/M/L` 二分查找"
        "下一个未寻址灯；（4）找到后 `ProgramShortAddress` 写入短地址；（5）`Withdraw` 让该灯退出"
        "寻址队列；（6）回到 (3) 直到所有灯被寻址。\n\n"
        "**`nOptions` 详解**：4 个 DWORD 常量可 OR 组合——`DALIV2_OPTION_COMPLETE_NEW_INSTALLATION` "
        "重新寻址所有灯（包括已有短地址的）；`DALIV2_OPTION_DELETE_ALL_GROUP_ASSIGNMENTS` 寻址前先清"
        "所有组归属；`DALIV2_OPTION_DELETE_ALL_SCENE_ASSIGNMENTS` 寻址前先清所有场景；"
        "`DALIV2_OPTION_OPTICAL_FEEDBACK`（默认）寻址前所有灯调到 `MIN VALUE`、新分配地址的灯立即"
        "全亮——人眼可见地确认寻址进度。\n\n"
        "**与 `FB_DALIV2AddressingIntRandomAddressing` 区别**：后者由 KL6821 端子内部执行（更快但"
        "不能提前终止 / 无进度反馈），本 FB 由 PLC 协调（更慢但全可控）。\n\n"
        "**典型陷阱**：① 寻址期间不要下发其它 DALI 命令——会被本 FB 拒绝；② 寻址过程几分钟，"
        "HMI 要显示进度条避免用户以为程序死了；③ `bAbort` 仅停止后续分配，已分配的地址保留。"
    ),
    "pitfalls": [
        "寻址期间不要下发其它 DALI 命令。",
        "整个过程几分钟到十几分钟，HMI 需显示进度（用 `nAddressedDevices`）。",
        "上线第一步通常配 `OPTION_COMPLETE_NEW_INSTALLATION | OPTION_DELETE_ALL_GROUP_ASSIGNMENTS | OPTION_DELETE_ALL_SCENE_ASSIGNMENTS`。",
        "`bAbort` 不撤销已分配的地址。",
    ],
    "scenario": (
        "DALI 工程上线第一步——把所有刚装上的镇流器（出厂状态，无短地址）按物理位置依次分配"
        "短地址。HMI 显示寻址进度（已分配 X / 总 Y 个）。"
    ),
    "value": (
        "替代厂家寻址工具（如 Tridonic masterCONFIGURATOR）；PLC 程序里一键启动，与工程版本绑定。"
    ),
    "alternative": (
        "1) `FB_DALIV2AddressingIntRandomAddressing`：端子内部寻址，更快但无反馈；"
        "2) `FB_DALIV2AddressingPhysicalSelection`：物理按键选灯寻址（每盏灯逐个按按钮）；"
        "3) **本 FB**：批量寻址 + 进度反馈，工程标准方法。"
    ),
    "related": (
        "[`FB_DALIV2AddressingIntRandomAddressing`](FB_DALIV2AddressingIntRandomAddressing.md)、"
        "[`FB_DALIV2AddressingPhysicalSelection`](FB_DALIV2AddressingPhysicalSelection.md)、"
        "[`FB_DALIV2ChangeAddressList`](FB_DALIV2ChangeAddressList.md)（地址表批量改）"
    ),
    "tcpou_decls": (
        "    bStartAddressing : BOOL;\n"
        "    bAbortAddressing : BOOL;\n"
        "    nFoundLamps      : BYTE;\n"
        "    bAddrDone        : BOOL;\n"
    ),
    "tcpou_inputs_assigns": (
        "    bStart               := bStartAddressing,\n"
        "    bAbort               := bAbortAddressing,\n"
        "    nStartWithShortAddress := 0,\n"
        "    nOptions             := DALIV2_OPTION_COMPLETE_NEW_INSTALLATION OR DALIV2_OPTION_DELETE_ALL_GROUP_ASSIGNMENTS OR DALIV2_OPTION_DELETE_ALL_SCENE_ASSIGNMENTS OR DALIV2_OPTION_OPTICAL_FEEDBACK,"
    ),
    "tcpou_scenario": "DALI 工程上线第一次寻址——所有灯从 short addr 0 开始批量分配，并清除原有组 / 场景。",
    "tcpou_value": "工程上线标准流程，省去厂家工具的离线步骤。",
    "tcpou_verify": (
        "1. 通信 FB 跑起；编译；登录；所有灯具应通电（出厂状态 short addr 都是 MASK）。\n"
        "2. 在线 bStartAddressing 一次上升沿；fb.bBusy 应保持 TRUE 几分钟。\n"
        "3. 观察 nFoundLamps 实时累加。\n"
        "4. fb.bBusy 回 FALSE 后，nFoundLamps 应等于实际灯数。\n"
        "5. 用 P_Demo_FB_DALIV2QueryControlGearPresent 测各 short addr 应能查到。"
    ),
})


def main():
    for spec in SPECS:
        doc_path, tcpou_path = write_pair(spec)
        print(f"  {doc_path.name}")


if __name__ == "__main__":
    main()
