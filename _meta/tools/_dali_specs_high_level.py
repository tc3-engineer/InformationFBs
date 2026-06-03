#!/usr/bin/env python3
"""Generate Part 102 High-Level FBs."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))

from _dali_bulk_gen import write_pair  # noqa: E402

INFOSYS_BASE = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/"

SPECS = []

# FB_DALIV2Dimmer2Switch
SPECS.append({
    "name": "FB_DALIV2Dimmer2Switch",
    "section": "4.1.1.1.2.5",
    "subdir": "part102_power_control",
    "category_display": "Part 102 / Power Control",
    "infosys": f"{INFOSYS_BASE}142913675.html",
    "summary": (
        "**双按钮调光开关 FB（high-level）**——两个机械按钮：`bSwitchDimmUp` 长按渐亮、`bSwitchDimmDown` "
        "长按渐暗；短按则开 / 关切换。比 `FB_DALIV2Dimmer1Switch` 多了一根按钮线，但 UX 更直观——"
        "明确的上 / 下方向。专业舞台、影院、高级会议室偏好。\n\n"
        "可控制单灯、组或广播。共享 `nMasterDevAddr` 主设备亮度跟踪机制。"
    ),
    "inputs_desc": {
        "bSwitchDimmUp": "上方向按钮：短按开关，长按渐亮到 `nMaxLevelMasterDev`",
        "bSwitchDimmDown": "下方向按钮：短按开关，长按渐暗到 `nMinLevelMasterDev`",
        "bOn": "强制开灯（上升沿）",
        "bOff": "强制关灯（上升沿）",
        "bSetDimmValue": "HMI 数值直驱（与 `nDimmValue` 配合）",
        "nDimmValue": "目标亮度（0..254）",
        "tSwitchOverTime": "短按 / 长按阈值，典型 200..400 ms",
        "tCycleDelay": "到达上 / 下限停顿时间",
        "bMemoryModeOn": "记忆模式（下次开灯回上次亮度）",
        "nOnValueWithoutMemoryMode": "非记忆模式开灯亮度",
        "nAddr": "目标地址（短地址 / 组号 / 广播）",
        "eAddrType": "寻址类型",
        "nMasterDevAddr": "主设备短地址（组 / 广播下追踪用）",
        "nMinLevelMasterDev": "调光下限",
        "nMaxLevelMasterDev": "调光上限",
        "tCycleActualLevelMasterDev": "后台读主设备亮度周期，0 禁用",
    },
    "outputs_desc": {
        "nActualLevelMasterDev": "主设备当前亮度（HMI 显示用）",
        "bBusy": "命令派发中",
        "bError": "出错",
        "nErrorId": "错误号",
    },
    "behavior": (
        "**双按钮状态机**：每个按钮独立判定短按 / 长按。短按（< `tSwitchOverTime`）任一按钮翻转开关；"
        "长按 `bSwitchDimmUp` 渐亮、长按 `bSwitchDimmDown` 渐暗，触到上 / 下限停 `tCycleDelay` 后回弹反向。"
        "与 `Dimmer1Switch` 区别：方向明确不需要『反向短松』。\n\n"
        "**`bOn` / `bOff` 强制**：上升沿强制开关，与按钮调光并行。\n\n"
        "**HMI 数值直驱**：`bSetDimmValue = FALSE` 时 `nDimmValue` 变化即透传；TRUE 时锁定等待上升沿。\n\n"
        "**记忆模式**：同 `Dimmer1Switch`。\n\n"
        "**`nMasterDevAddr` 跟踪**：组 / 广播控制时跟踪一盏主设备亮度作参考。\n\n"
        "**典型陷阱**：① 两按钮同时长按 → 行为未定义（FB 内部按谁先按下处理）；② 按钮接线时上 / 下"
        "搞反——用户体验完全反向，但 PLC 可以一键软改换 `bSwitchDimmUp` / `Down` 接线即可。"
    ),
    "pitfalls": [
        "上下按钮接反时整套 UX 反向——上线时务必测试方向。",
        "两按钮同时按行为未定义，PLC 端应互斥。",
        "其它行为同 `FB_DALIV2Dimmer1Switch`，包括 EEPROM 写次数 / 主设备跟踪等。",
    ],
    "scenario": (
        "影院 / 剧院 / 舞台技术控制台——专业操作员偏好明确的方向按钮，长按上 = 渐亮、长按下 = 渐暗。"
        "短按任一按钮开关，匹配业内传统调光台 UX。"
    ),
    "value": (
        "比 `Dimmer1Switch` UX 更直观，专业场景偏好；同样封装短按 / 长按识别、调光状态机、DALI 命令排队。"
    ),
    "alternative": (
        "1) `FB_DALIV2Dimmer1Switch`：单按钮版本，普通楼宇照明首选；"
        "2) **本 FB**：专业 / 双按钮场景首选；"
        "3) `FB_DALIV2Dimmer2SwitchEco`：节能版本带定时关灯。"
    ),
    "related": (
        "[`FB_DALIV2Dimmer1Switch`](FB_DALIV2Dimmer1Switch.md)、"
        "[`FB_DALIV2Light`](FB_DALIV2Light.md)、"
        "[`FB_DALIV2LightControl`](FB_DALIV2LightControl.md)"
    ),
    "tcpou_decls": (
        "    nGroupAddr       : BYTE := 5;\n"
        "    nMasterShortAddr : BYTE := 12;\n"
        "    nMinDim          : BYTE := 100;\n"
        "    nMaxDim          : BYTE := 254;\n"
        "    bUpButton        : BOOL;\n"
        "    bDownButton      : BOOL;\n"
        "    bForceOn         : BOOL;\n"
        "    bForceOff        : BOOL;\n"
        "    bHmiSet          : BOOL;\n"
        "    nHmiTarget       : BYTE := 150;\n"
        "    nActualLevel     : BYTE;\n"
    ),
    "tcpou_inputs_assigns": (
        "    bSwitchDimmUp              := bUpButton,\n"
        "    bSwitchDimmDown            := bDownButton,\n"
        "    bOn                        := bForceOn,\n"
        "    bOff                       := bForceOff,\n"
        "    bSetDimmValue              := bHmiSet,\n"
        "    nDimmValue                 := nHmiTarget,\n"
        "    tSwitchOverTime            := T#400MS,\n"
        "    tCycleDelay                := T#500MS,\n"
        "    bMemoryModeOn              := TRUE,\n"
        "    nOnValueWithoutMemoryMode  := 200,\n"
        "    nAddr                      := nGroupAddr,\n"
        "    eAddrType                  := eDALIV2AddrTypeGroup,\n"
        "    nMasterDevAddr             := nMasterShortAddr,\n"
        "    nMinLevelMasterDev         := nMinDim,\n"
        "    nMaxLevelMasterDev         := nMaxDim,\n"
        "    tCycleActualLevelMasterDev := T#1S,"
    ),
    "tcpou_scenario": "影院控制台双按钮调光：上 = 渐亮，下 = 渐暗，短按 = 开 / 关。",
    "tcpou_value": "方向明确的专业 UX。",
    "tcpou_verify": (
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 在线写 bUpButton := TRUE 保持 < 300 ms 再 FALSE → 灯开（关时）或关（亮时）。\n"
        "3. 在线写 bUpButton := TRUE 保持 > 400 ms → 灯渐亮到 nMaxDim。\n"
        "4. 在线写 bDownButton := TRUE 保持 > 400 ms → 灯渐暗到 nMinDim。\n"
        "5. nHmiTarget := 100，bHmiSet 一次上升沿 → 灯立即跳到 100。"
    ),
})

# FB_DALIV2Light
SPECS.append({
    "name": "FB_DALIV2Light",
    "section": "4.1.1.1.2.7",
    "subdir": "part102_power_control",
    "category_display": "Part 102 / Power Control",
    "infosys": f"{INFOSYS_BASE}142916747.html",
    "summary": (
        "**最简单的 DALI 开关 FB（high-level）**——`bSwitch` 电平 = 开关状态，TRUE 时灯调到 "
        "`nOnValue`，FALSE 时关灯。无调光功能。专门用于纯开关功能场景：洗手间灯、走廊感应灯、"
        "工业开关灯具等不需要 PLC 调光的应用。"
    ),
    "inputs_desc": {
        "bSwitch": "电平开关：TRUE 灯亮到 `nOnValue`，FALSE 灯关",
        "nOnValue": "灯亮时的目标亮度（0..254）",
        "nAddr": "目标地址",
        "eAddrType": "寻址类型",
    },
    "outputs_desc": {
        "bBusy": "命令派发中",
        "bError": "出错",
        "nErrorId": "错误号",
    },
    "behavior": (
        "**电平触发**：`bSwitch` 变化时本 FB 发一次 DAPC（TRUE → `nOnValue`，FALSE → 0）；"
        "电平稳定后不重发。\n\n"
        "**调用频率**：因为只在 `bSwitch` 变化时发命令，本 FB 不占用 DALI 总线带宽。\n\n"
        "**典型应用**：（1）感应器联动——红外感应器触发，本 FB 切换灯具；（2）定时灯——PLC 时钟到点"
        "把 `bSwitch` 写 FALSE；（3）紧急联动——消防触发把 `bSwitch` 强制 FALSE。\n\n"
        "**与 `Dimmer1Switch` 区别**：本 FB 仅开关，无调光，更简单；调光场景应用 `Dimmer1Switch`。\n\n"
        "**典型陷阱**：① `nOnValue = 0` 时『开』变成『关』，无意义；② 多个本 FB 实例控同一灯具时"
        "互相覆盖。"
    ),
    "pitfalls": [
        "无调光功能，纯开关。",
        "`nOnValue` 不要设为 0。",
        "电平触发，无去抖（输入信号要稳定）。",
    ],
    "scenario": "走廊红外感应器联动：感应到人触发开灯（`bSwitch := TRUE`），离开 30 秒后关灯。",
    "value": "替代手写一行 DAPC——封装了 DALI 命令排队 / 错误处理；专用于不需要调光的场景。",
    "alternative": (
        "1) `FB_DALIV2Dimmer1Switch`：单按钮调光，过于复杂；"
        "2) `FB_DALIV2DirectArcPowerControl(nArcPowerLevel=0 or value)`：底层命令；"
        "3) **本 FB**：纯开关场景最简方案。"
    ),
    "related": (
        "[`FB_DALIV2Dimmer1Switch`](FB_DALIV2Dimmer1Switch.md)（带调光）、"
        "[`FB_DALIV2LightControl`](FB_DALIV2LightControl.md)（带自动 / 手动模式切换）、"
        "[`FB_DALIV2StairwellDimmer`](FB_DALIV2StairwellDimmer.md)（楼梯间自动延时关灯）"
    ),
    "tcpou_decls": (
        "    bSensorTriggered : BOOL;\n"
        "    nLampLevel       : BYTE := 254;\n"
        "    nGroupAddr       : BYTE := 1;\n"
    ),
    "tcpou_inputs_assigns": (
        "    bSwitch          := bSensorTriggered,\n"
        "    nOnValue         := nLampLevel,\n"
        "    nAddr            := nGroupAddr,\n"
        "    eAddrType        := eDALIV2AddrTypeGroup,"
    ),
    "tcpou_scenario": "走廊红外感应灯：感应器 BOOL 输出接 bSensorTriggered，触发即开灯 100%，停发即关。",
    "tcpou_value": "纯开关场景最简单接法。",
    "tcpou_verify": (
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 在线写 bSensorTriggered := TRUE → 灯组应开到 254。\n"
        "3. 在线写 bSensorTriggered := FALSE → 灯组关。\n"
        "4. 多次切换 bSensorTriggered，灯应跟随。"
    ),
})

# FB_DALIV2StairwellDimmer
SPECS.append({
    "name": "FB_DALIV2StairwellDimmer",
    "section": "4.1.1.1.2.11",
    "subdir": "part102_power_control",
    "category_display": "Part 102 / Power Control",
    "infosys": f"{INFOSYS_BASE}142923915.html",
    "summary": (
        "**楼梯间灯自动定时关闭 FB**——用户按按钮（`bStart` 上升沿）灯全亮（亮度 `nOnValue`），保持 "
        "`tOnTime` 时长后自动渐暗到 `nWarnValue` 警告 `tWarnTime` 时间，最后关灭（亮度 0）。"
        "中途再按 `bStart` 重新计时。\n\n"
        "经典楼梯间 / 公共区域照明方案——既保证有人用灯时长亮，又自动节能。"
    ),
    "inputs_desc": {
        "bStart": "按钮上升沿触发开灯并启动定时",
        "tOnTime": "亮灯时长（典型 3..10 分钟）",
        "nOnValue": "亮灯期间的亮度（0..254）",
        "tWarnTime": "警告闪烁时长（典型 10..30 秒）",
        "nWarnValue": "警告期间的亮度（典型 `nOnValue / 2`）",
        "nAddr": "目标地址",
        "eAddrType": "寻址类型",
    },
    "outputs_desc": {
        "bLightOn": "灯当前是否点亮",
        "bWarning": "进入警告期（用户感知灯变暗，知道快关了，可以再按按钮续时）",
        "bBusy": "命令派发中",
        "bError": "出错",
        "nErrorId": "错误号",
    },
    "behavior": (
        "**状态机**：4 状态——OFF / ON / WARNING / OFF。\n\n"
        "1. OFF：灯关，等待 `bStart` 上升沿。\n"
        "2. `bStart` 上升沿 → ON：本 FB 发 DAPC(`nOnValue`)；启动 `tOnTime` 计时；`bLightOn = TRUE`。\n"
        "3. `tOnTime` 到 → WARNING：本 FB 发 DAPC(`nWarnValue`)；启动 `tWarnTime` 计时；`bWarning = TRUE`。\n"
        "   - 警告期内 `bStart` 上升沿 → 回到 ON，重新计 `tOnTime`。\n"
        "4. `tWarnTime` 到 → OFF：本 FB 发 OFF；`bLightOn = bWarning = FALSE`。\n\n"
        "**用户感知**：开灯亮 5 分钟，灯亮起；4 分 30 秒时灯变暗（警告）；快关了时只剩 30 秒——"
        "用户感觉到立即可以再按按钮续 5 分钟。\n\n"
        "**典型陷阱**：① 警告期 `nWarnValue = 0` 等同直接关灯，用户没有快关了的提示；"
        "② `tOnTime` 设过短（< 30 秒）用户来不及上下楼；③ 大范围使用时多按钮控同一灯组要"
        "注意 `bStart` 信号合并（任一按钮按下都续时）。"
    ),
    "pitfalls": [
        "`tOnTime` 至少几分钟，给用户合理使用时间。",
        "`nWarnValue` 应明显低于 `nOnValue`（典型 1/2），让用户感知到快关了的预警。",
        "警告期内 `bStart` 上升沿续时，给用户挽回机会。",
        "多按钮控同一灯组时，PLC 端 OR 所有按钮信号给 `bStart`。",
    ],
    "scenario": (
        "公寓楼梯间——居民进入楼梯按按钮，灯亮 5 分钟自动暗 30 秒后关。中途用户走得慢可以再按按钮"
        "续 5 分钟。也可用于地下停车场、办公楼洗手间等不需要常亮但又要够时间使用的场景。"
    ),
    "value": (
        "替代约 50 行 PLC 状态机代码 + 多个 TON 定时器；本 FB 一次调用全搞定，警告 / 续时 / 自动关三套逻辑封装。"
    ),
    "alternative": (
        "1) 自己用 TON + RS + 状态机：可行但代码量大且漏边界条件常见；"
        "2) `FB_DALIV2Light` + 外部 TON：能做但要多个 FB；"
        "3) **本 FB**：楼梯间定时灯标准解决方案。"
    ),
    "related": (
        "[`FB_DALIV2Light`](FB_DALIV2Light.md)（基础开关）、"
        "[`FB_DALIV2Sequencer`](FB_DALIV2Sequencer.md)（更复杂的多步序列）、"
        "[`FB_DALIV2LightControl`](FB_DALIV2LightControl.md)（手动 / 自动混合）"
    ),
    "tcpou_decls": (
        "    bStairButton     : BOOL;\n"
        "    nGroupAddr       : BYTE := 3;\n"
        "    bLightIsOn       : BOOL;\n"
        "    bWarningPhase    : BOOL;\n"
    ),
    "tcpou_inputs_assigns": (
        "    bStart           := bStairButton,\n"
        "    tOnTime          := T#3M,\n"
        "    nOnValue         := 254,\n"
        "    tWarnTime        := T#20S,\n"
        "    nWarnValue       := 100,\n"
        "    nAddr            := nGroupAddr,\n"
        "    eAddrType        := eDALIV2AddrTypeGroup,"
    ),
    "tcpou_scenario": "公寓楼梯灯：按按钮亮 3 分钟，警告 20 秒后关。",
    "tcpou_value": "替代复杂状态机代码；用户体验完整。",
    "tcpou_verify": (
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 在线 bStairButton 一次上升沿。\n"
        "3. bLightIsOn 应立即 TRUE；灯组应全亮。\n"
        "4. 等 3 分钟，bWarningPhase 应 TRUE，灯应暗到 100。\n"
        "5. 再等 20 秒，bLightIsOn = bWarningPhase = FALSE，灯关。\n"
        "6. 警告期内再按一次 bStairButton → 应回到 ON 重新计 3 分钟。"
    ),
})


def main():
    for spec in SPECS:
        doc_path, tcpou_path = write_pair(spec)
        print(f"  {doc_path.name}")


if __name__ == "__main__":
    main()
