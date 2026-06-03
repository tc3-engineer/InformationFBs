#!/usr/bin/env python3
"""Generate Part 102 / Configuration low-level command FBs (batch)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))

from _dali_bulk_gen import write_pair  # noqa: E402

COMMON_INPUT_ASSIGNS = (
    "    bStart           := bTrigger,\n"
    "    nAddr            := nLampAddr,\n"
    "    eAddrType        := eDALIV2AddrTypeShort,\n"
    "    eCommandPriority := eDALIV2CommandPriorityMiddle,"
)
COMMON_DECL = "    nLampAddr        : BYTE := 0;\n\n"

SPECS = [
    {
        "name": "FB_DALIV2RemoveFromGroup",
        "section": "4.1.2.3.3.2",
        "subdir": "part102_low_config",
        "category_display": "Part 102 / Low-Level / Configuration",
        "infosys": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142787979.html",
        "summary": (
            "**把镇流器从 DALI 组中移除的配置命令**——`FB_DALIV2AddToGroup` 的对应反向操作。"
            "本 FB 把 `nAddr` 寻址到的镇流器从 `nGroup` 指定的组（0..15）中移除。"
            "镇流器原本属于的其它组归属保留——本命令只清这一组成员。\n\n"
            "运行时调整 DALI 分组的核心命令（工程上线后某盏灯被改作他用 / 房间合并改造等场景）。"
        ),
        "inputs_desc": {
            "nGroup": "要从该组中移除的组号（0..15）"
        },
        "behavior": (
            "**调用方式**：`bStart` 上升沿；本 FB 写 DTR0 = `nGroup`，下发 `REMOVE FROM GROUP n` 命令，"
            "灯具更新内部 16-bit 组归属位图（清除对应 bit）写回 EEPROM。\n\n"
            "**EEPROM 写次数**：与 `FB_DALIV2AddToGroup` 一样，EEPROM 额定 10 万次写入；分组调整应是低频操作，"
            "不应循环调用。\n\n"
            "**与 `FB_DALIV2AddToGroup` 的对偶**：本 FB 只清这一组的 bit；其它组归属保留。"
            "要让镇流器从所有组移除可循环调用本 FB 16 次（每次一个 nGroup），或更简单地用 `FB_DALIV2Reset` "
            "复位灯具到出厂状态（同时也清除其它配置如 `FADE TIME` / 短地址，慎用）。\n\n"
            "**广播 / 组寻址下的语义**：`eAddrType := Broadcast` + `nGroup := 5` 让全线所有灯都退出组 5，"
            "用于运行时收回某组成员资格。\n\n"
            "**典型陷阱**：① 在循环里改不同组要等 `bBusy = FALSE` 才下一次上升沿；② 写完后用 "
            "`FB_DALIV2QueryGroups` 确认实际生效。"
        ),
        "pitfalls": [
            "EEPROM 写次数有限，分组调整应低频。",
            "本 FB 只清 `nGroup` 一组；其它组归属不变。",
            "`nGroup > 15` 灯具忽略，本 FB 不报错。",
            "写完用 `FB_DALIV2QueryGroups0UpTo7` / `_8UpTo15` 验证实际生效。",
        ],
        "scenario": (
            "DALI 工程运行时调整：某盏灯原本属于走廊照明组（组 1），后来房间改造把它划入会议室组（组 5），"
            "本 FB 把它从组 1 移除，再用 `FB_DALIV2AddToGroup` 加到组 5。"
        ),
        "value": "运行时灵活调整 DALI 分组不需要重置灯具；保留 `FADE TIME` 等其它配置不变。",
        "alternative": (
            "1) `FB_DALIV2Reset`：复位灯具到出厂状态，所有配置清空，过于激进；2) 手动用厂家工具："
            "运维成本高；3) **本 FB**：运行时调整组归属的标准工具。"
        ),
        "related": (
            "[`FB_DALIV2AddToGroup`](FB_DALIV2AddToGroup.md)、"
            "[`FB_DALIV2QueryGroups`](../part102_low_queries/FB_DALIV2QueryGroups.md)、"
            "[`FB_DALIV2Reset`](FB_DALIV2Reset.md)"
        ),
        "tcpou_decls": COMMON_DECL + "    nGroupToRemove   : BYTE := 1;\n",
        "tcpou_inputs_assigns": COMMON_INPUT_ASSIGNS + "\n    nGroup           := nGroupToRemove,",
        "tcpou_scenario": (
            "把 short addr 5 从走廊照明组（组 1）中移除——准备把它划入其它组。"
        ),
        "tcpou_value": "运行时灵活调整 DALI 分组，不需要重置灯具。",
        "tcpou_verify": (
            "1. P_Demo_FB_KL6821Communication 先跑起来共享 stCommandBuffer。\n"
            "2. 编译，登录，运行；等通信 FB bLineIsInitialized = TRUE。\n"
            "3. 调用前先用 P_Demo_FB_DALIV2QueryGroups0UpTo7 看 short addr 5 当前组位图，确认 bit 1 已置。\n"
            "4. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
            "5. 再查组位图——bit 1 应已清除，其它 bit 保留。"
        ),
    },

    {
        "name": "FB_DALIV2RemoveFromScene",
        "section": "4.1.2.3.3.3",
        "subdir": "part102_low_config",
        "category_display": "Part 102 / Low-Level / Configuration",
        "infosys": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142789515.html",
        "summary": (
            "**清除镇流器某个场景预设的命令**——DALI 镇流器内部存 16 个场景寄存器（`SCENE 0..15`），"
            "每个场景对应一个亮度值。本 FB 把 `nAddr` 寻址到的镇流器的 `nScene`（0..15）场景值"
            "清成 `MASK`（表示该灯不参与该场景，调用此场景时不变化）。\n\n"
            "场景预设的反向操作；`FB_DALIV2SetScene` 是设场景值，本 FB 是清场景值。"
        ),
        "inputs_desc": {
            "nScene": "要清除的场景号（0..15）"
        },
        "behavior": (
            "**调用方式**：`bStart` 上升沿；本 FB 写 DTR0 = `MASK`（=255），下发 `STORE DTR AS SCENE n` 命令，"
            "灯具把第 n 个场景寄存器写为 `MASK`，等同于该灯不参与场景 n。\n\n"
            "**场景调用时的影响**：之后 `FB_DALIV2GoToScene` 用 `nScene = n` 触发场景 n 时，本灯（被本 FB 清的灯）"
            "亮度不变（即忽略该场景）。其它灯不受影响。\n\n"
            "**EEPROM 写次数**：与 Add/Remove Group 一样，分场景配置应是低频。\n\n"
            "**典型陷阱**：① 与 `FB_DALIV2SetScene` 配合使用——先 SetScene 给一组灯设值，"
            "后 RemoveFromScene 把不应该响应该场景的灯清掉；② 不要在生产期循环清除。"
        ),
        "pitfalls": [
            "本 FB 把场景值写为 `MASK`（255），等同于该灯不参与此场景。",
            "EEPROM 写次数有限。",
            "`nScene > 15` 灯具忽略。",
        ],
        "scenario": (
            "会议室场景调用配置：场景 0 = 会议开场全亮、场景 1 = 演示模式（只亮投影附近灯）。"
            "演示模式应让窗边灯不亮——用本 FB 把窗边灯 short addr 15 的场景 1 清成 MASK，"
            "调场景 1 时窗边灯保持原状。"
        ),
        "value": "替代手动给每盏灯都设场景值；不参与是更精准的语义。",
        "alternative": (
            "1) `FB_DALIV2SetScene` 设为 0：表示灯关——但调用场景时灯会被主动关灭（如果原本亮就被关）；"
            "2) **本 FB** 设为 MASK：表示不参与——调用场景时不动；语义更精确。"
        ),
        "related": (
            "[`FB_DALIV2SetScene`](FB_DALIV2SetScene.md)、"
            "[`FB_DALIV2GoToScene`](../part102_low_power/FB_DALIV2GoToScene.md)、"
            "[`FB_DALIV2QuerySceneLevel`](../part102_low_queries/FB_DALIV2QuerySceneLevel.md)"
        ),
        "tcpou_decls": COMMON_DECL + "    nSceneToClear    : BYTE := 1;\n",
        "tcpou_inputs_assigns": COMMON_INPUT_ASSIGNS + "\n    nScene           := nSceneToClear,",
        "tcpou_scenario": (
            "把 short addr 15 (窗边灯) 的场景 1 清成 MASK——调用场景 1 时这盏灯保持原状。"
        ),
        "tcpou_value": "精确控制哪些灯参与哪个场景；比统一设为 0 的语义更准确。",
        "tcpou_verify": (
            "1. 先跑通信 FB；编译运行；等 bLineIsInitialized。\n"
            "2. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
            "3. 用 P_Demo_FB_DALIV2QuerySceneLevel 查 short addr 15 场景 1 → 应为 255 (MASK)。\n"
            "4. 用 P_Demo_FB_DALIV2GoToScene 触发场景 1，short addr 15 应保持原状不变。"
        ),
    },

    {
        "name": "FB_DALIV2Reset",
        "section": "4.1.2.3.3.4",
        "subdir": "part102_low_config",
        "category_display": "Part 102 / Low-Level / Configuration",
        "infosys": "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142791051.html",
        "summary": (
            "**镇流器复位到出厂默认值的命令**——把目标镇流器的全部配置寄存器"
            "（亮度、`FADE TIME`、`FADE RATE`、`MIN/MAX VALUE`、`POWER ON LEVEL`、组归属、场景值、短地址等）"
            "复位到 DALI 规范的出厂默认。\n\n"
            "**危险操作**——慎用；通常仅在工程上线初次配置前 / 灯具配置完全混乱需重新规划时使用。"
        ),
        "behavior": (
            "**调用方式**：`bStart` 上升沿；本 FB 下发两次 `RESET` 命令（DALI 协议要求双指令防误触发），"
            "灯具收到后用约 300 ms 完成 EEPROM 清空与重写。命令派发完 `bBusy` 回 FALSE，但灯具复位过程仍可能"
            "持续到调用结束后 300+ ms。\n\n"
            "**复位的内容**：（按 DALI 规范 IEC 62386 Part 102）`ACTUAL DIM LEVEL` 复位为 `POWER ON LEVEL` "
            "（出厂 254）；`FADE TIME = 0`、`FADE RATE = 7`、`MIN VALUE = 1`、`MAX VALUE = 254`、"
            "`POWER ON LEVEL = 254`、`SYSTEM FAILURE LEVEL = 254`、组归属 = 0（不属任何组）、"
            "场景 0..15 全为 `MASK`、`RANDOM ADDRESS = 0xFFFFFF`。**短地址（`SHORT ADDRESS`）也被清成 `MASK`（即 255 = 无短地址）**。\n\n"
            "**短地址清空后的影响**：本 FB 用 `eAddrType := Short` + `nAddr := N` 调用后，灯具短地址被清——"
            "再用同样 `nAddr := N` 找不到这盏灯了！需要重新做寻址（用 `FB_DALIV2AddressingRandomAddressing`）。\n\n"
            "**用 Broadcast 复位整网**：`eAddrType := Broadcast` 一次复位所有灯具——工程上线第一步常用法。\n\n"
            "**典型陷阱**：① Reset 单灯后短地址也被清，找不到了；② Broadcast Reset 会清光所有灯的配置，"
            "包括组归属——工程上线前用没事，运行时绝对不要广播 Reset；③ Reset 命令期间灯具亮度可能短暂"
            "跳到 254（`POWER ON LEVEL` 默认值），用户可能感知到闪烁。"
        ),
        "pitfalls": [
            "**复位会清掉短地址**——单灯复位后这盏灯失联，需要重新寻址。",
            "**Broadcast Reset 清光所有配置**——运行时绝对不要广播 Reset。",
            "复位期间灯具亮度可能短暂跳变（`POWER ON LEVEL` 默认 254），用户感知闪烁。",
            "EEPROM 写次数高（一次复位写多个寄存器），不要频繁调用。",
            "复位后立即下发其它命令前应等 ~500 ms 让灯具完成 EEPROM 操作。",
        ],
        "scenario": (
            "DALI 工程初始装机第一步：上线前对整条 DALI 线广播一次 Reset，把所有镇流器复位到出厂状态，"
            "然后按设计文档统一寻址 / 分组 / 配置 Fade 参数。也用于灯具配置完全混乱（被多人乱改）需要重新规划的场景。"
        ),
        "value": "替代手动用厂家工具一盏盏复位；广播一次复位整网，省时省事。",
        "alternative": (
            "1) 手动用厂家工具：太慢；2) 单独发各个 SetXxx 命令把每个寄存器写回默认值：相当于重写本 FB，"
            "效率低；3) **本 FB**：标准复位接口。"
        ),
        "related": (
            "[`FB_DALIV2AddressingRandomAddressing`](../part102_addressing/FB_DALIV2AddressingRandomAddressing.md)（复位后重新寻址）、"
            "[`FB_DALIV2QueryResetState`](../part102_low_queries/FB_DALIV2QueryResetState.md)（查询是否处于复位状态）、"
            "[`FB_DALIV2SetSettings`](../part102_settings/FB_DALIV2SetSettings.md)（高层批量配置）"
        ),
        "tcpou_decls": COMMON_DECL,
        "tcpou_inputs_assigns": COMMON_INPUT_ASSIGNS,
        "tcpou_scenario": (
            "DALI 工程上线第一步——对整网广播一次 Reset 让所有灯回到出厂状态，准备重新规划寻址和分组。"
        ),
        "tcpou_value": "一次广播代替手动复位每盏灯。",
        "tcpou_verify": (
            "1. 先跑通信 FB；编译运行；等 bLineIsInitialized。\n"
            "2. 把 eAddrType 改为 eDALIV2AddrTypeBroadcast（默认 Short 仅复位 nLampAddr 灯）。\n"
            "3. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
            "4. 等 500 ms 让灯具完成 EEPROM 操作。\n"
            "5. 所有灯应跳到 POWER ON LEVEL 默认值（254 即全亮）；短地址全部被清——\n"
            "   再用 P_Demo_FB_DALIV2QueryControlGearPresent 试任何 short addr 都查不到。\n"
            "6. 然后用 P_Demo_FB_DALIV2AddressingRandomAddressing 重新寻址。"
        ),
    },
]


def main():
    for spec in SPECS:
        doc_path, tcpou_path = write_pair(spec)
        print(f"  {doc_path.name}")
        print(f"  {tcpou_path.name}")


if __name__ == "__main__":
    main()
