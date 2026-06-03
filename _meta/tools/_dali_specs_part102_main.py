#!/usr/bin/env python3
"""Generate Part 102 low-level command FBs in bulk."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))

from _dali_bulk_gen import write_pair  # noqa: E402

# Standard input assigns + decl for "command with bStart + nAddr + eAddrType + eCommandPriority"
A_BASIC = (
    "    bStart           := bTrigger,\n"
    "    nAddr            := nLampAddr,\n"
    "    eAddrType        := eDALIV2AddrTypeShort,\n"
    "    eCommandPriority := eDALIV2CommandPriorityMiddle,"
)
D_BASIC = "    nLampAddr        : BYTE := 0;\n\n"

INFOSYS_BASE = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/"


def gen_set_value_fb(name, section, topicid, subdir, value_field, value_field_desc,
                     summary, behavior, pitfalls, scenario, value, alt, related,
                     tcpou_extra_decl, tcpou_extra_assign, tcpou_scenario, tcpou_verify,
                     inputs_desc=None):
    """Generic Set-Xxx FB (bStart + nAddr + eAddrType + eCommandPriority + nValue)."""
    full_inputs_desc = {value_field: value_field_desc}
    if inputs_desc:
        full_inputs_desc.update(inputs_desc)
    return {
        "name": name,
        "section": section,
        "subdir": subdir,
        "category_display": "Part 102 / Low-Level / Configuration",
        "infosys": f"{INFOSYS_BASE}{topicid}.html",
        "summary": summary,
        "inputs_desc": full_inputs_desc,
        "behavior": behavior,
        "pitfalls": pitfalls,
        "scenario": scenario,
        "value": value,
        "alternative": alt,
        "related": related,
        "tcpou_decls": D_BASIC + tcpou_extra_decl,
        "tcpou_inputs_assigns": A_BASIC + "\n    " + tcpou_extra_assign,
        "tcpou_scenario": tcpou_scenario,
        "tcpou_value": "运行时直接修改灯具寄存器；改完失电保护。",
        "tcpou_verify": tcpou_verify,
    }


def gen_query_fb(name, section, topicid, subdir, what, query_field, query_field_desc,
                 summary, behavior, pitfalls, scenario, value, alt, related, tcpou_verify):
    """Generic Query-Xxx FB (bStart + nAddr + eAddrType + eCommandPriority / + query result + status)."""
    return {
        "name": name,
        "section": section,
        "subdir": subdir,
        "category_display": "Part 102 / Low-Level / Queries",
        "infosys": f"{INFOSYS_BASE}{topicid}.html",
        "summary": summary,
        "outputs_desc": {query_field: query_field_desc},
        "behavior": behavior,
        "pitfalls": pitfalls,
        "scenario": scenario,
        "value": value,
        "alternative": alt,
        "related": related,
        "tcpou_decls": D_BASIC + f"    {what.lower()}Query  : BYTE;\n",
        "tcpou_inputs_assigns": A_BASIC,
        "tcpou_scenario": f"查询单灯 short addr 0 的 {what}（DALI 寄存器值）。",
        "tcpou_value": f"获取灯具内部 {what} 寄存器当前值，用于诊断 / HMI 显示。",
        "tcpou_verify": tcpou_verify,
    }


def gen_power_fb(name, section, topicid, summary, behavior, pitfalls, scenario, value, alt, related,
                 tcpou_verify):
    """Generic step / power-control FB (no extra parameter beyond addressing)."""
    return {
        "name": name,
        "section": section,
        "subdir": "part102_low_power",
        "category_display": "Part 102 / Low-Level / Power Control",
        "infosys": f"{INFOSYS_BASE}{topicid}.html",
        "summary": summary,
        "behavior": behavior,
        "pitfalls": pitfalls,
        "scenario": scenario,
        "value": value,
        "alternative": alt,
        "related": related,
        "tcpou_decls": D_BASIC,
        "tcpou_inputs_assigns": A_BASIC,
        "tcpou_scenario": scenario[:80] + "...",
        "tcpou_value": "DALI 协议的 Step Up / Down / Off / RecallMax 等命令的轻量封装。",
        "tcpou_verify": tcpou_verify,
    }


SPECS = []

# ========== Configuration FBs ==========
SPECS.append(gen_set_value_fb(
    name="FB_DALIV2SetFadeRate",
    section="4.1.2.3.3.5",
    topicid="142792587",
    subdir="part102_low_config",
    value_field="nFadeRate",
    value_field_desc=(
        "目标 `FADE RATE` 索引值 1..15（0 是非法值）。对应每秒的亮度变化步数："
        "1 = 357.6 步/秒（最快）/ 7 = 11.18（默认）/ 15 = 0.044（最慢）。控制 `FB_DALIV2Up` / `Down` "
        "等连续调光命令的速率"
    ),
    summary=(
        "**设置镇流器 `FADE RATE` 寄存器**——DALI 镇流器内部存一个 `FADE RATE`（1..15）寄存器，"
        "决定 `Up` / `Down` 这类连续步进调光命令每秒的亮度变化步数。值越小变化越快。"
        "本 FB 把目标值（输入参数）通过 DTR0 写入灯具。"
    ),
    behavior=(
        "**调用方式**：`bStart` 上升沿；本 FB 先发 `SET DTR` 命令把 `nFadeRate` 写入 DTR0 寄存器，"
        "再发 `STORE THE DTR AS FADE RATE` 命令把 DTR0 内容写入灯具的 `FADE RATE` 寄存器（EEPROM 失电保护）。\n\n"
        "**`FADE RATE` 影响范围**：仅影响 `FB_DALIV2Up` / `Down` / `StepUp` / `StepDown` 这类逐步调光命令；"
        "不影响 `DAPC`（DAPC 用 `FADE TIME` 控制速率）。\n\n"
        "**典型值**：办公照明用默认 7（约 28 步/秒，触感平滑）；舞台快速效果用 1..3（极快）；"
        "情绪照明用 13..15（极慢，给观众强烈渐进感）。\n\n"
        "**典型陷阱**：① `nFadeRate = 0` 是非法值，灯具忽略不报错；② 与 `FADE TIME` 易混："
        "`FADE RATE` 控制 Up/Down 的速率，`FADE TIME` 控制 DAPC 的渐变时长，是两套独立机制；"
        "③ 改完立即用 `FB_DALIV2QueryFadeTimeFadeRate` 验证生效。"
    ),
    pitfalls=[
        "`nFadeRate` 合法范围 1..15；0 灯具忽略不报错。",
        "本 FB 不影响 DAPC 的渐变（DAPC 用 `FADE TIME`）。",
        "EEPROM 写次数有限。",
    ],
    scenario=(
        "舞台演出现场——同一组灯需要不同的调光速率：开场缓慢渐亮（`FADE RATE = 13`），"
        "高潮段快速变化（`FADE RATE = 2`）。本 FB 在演出脚本切换段落时切换灯具内部速率。"
    ),
    value="替代每次调光都改 PLC 循环时序——直接配置灯具内部，省心。",
    alt=(
        "1) 用 PLC 循环连续 DAPC 自己控变化速率：复杂；2) 用 `FB_DALIV2SetFadeTime` 配 DAPC 做长渐变："
        "DAPC 是绝对目标，FADE TIME 决定到达时间；3) **本 FB**：步进调光速率配置标准方法。"
    ),
    related=(
        "[`FB_DALIV2SetFadeTime`](FB_DALIV2SetFadeTime.md)（控制 DAPC 渐变时长）、"
        "[`FB_DALIV2QueryFadeTimeFadeRate`](../part102_low_queries/FB_DALIV2QueryFadeTimeFadeRate.md)、"
        "[`FB_DALIV2Up`](../part102_low_power/FB_DALIV2Up.md) / [`FB_DALIV2Down`](../part102_low_power/FB_DALIV2Down.md)"
    ),
    tcpou_extra_decl="    nNewFadeRate     : BYTE := 7;\n",
    tcpou_extra_assign="nFadeRate        := nNewFadeRate,",
    tcpou_scenario="演出脚本切到慢渐变段，把灯组 short addr 0 的 FADE RATE 设为 13（约 0.7 步/秒，极慢）。",
    tcpou_verify=(
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
        "3. 用 P_Demo_FB_DALIV2QueryFadeTimeFadeRate 查 short addr 0 → FADE RATE 应等于 13。\n"
        "4. 用 P_Demo_FB_DALIV2Up 触发逐步加亮——亮度变化速率应明显比默认 (7) 慢。"
    ),
))

SPECS.append(gen_set_value_fb(
    name="FB_DALIV2SetFadeTime",
    section="4.1.2.3.3.6",
    topicid="142794123",
    subdir="part102_low_config",
    value_field="nFadeTime",
    value_field_desc=(
        "目标 `FADE TIME` 索引值 0..15。0 = 瞬时跳变；1..15 对应非线性时间表（1 ≈ 707 ms / "
        "8 ≈ 8 s / 15 ≈ 90.5 s）。控制 `DAPC` 命令从当前亮度变化到目标亮度的总时间"
    ),
    summary=(
        "**设置镇流器 `FADE TIME` 寄存器**——决定 DAPC 命令、`GoToScene`、`RecallMaxLevel` 等"
        "绝对目标命令的渐变总时间。值 0 = 瞬时跳变；越大渐变越慢。"
    ),
    behavior=(
        "**调用方式**：`bStart` 上升沿；本 FB 写 DTR0 = `nFadeTime`，下发 `STORE THE DTR AS FADE TIME` "
        "把 DTR0 写入灯具 EEPROM。\n\n"
        "**FADE TIME 数值与实际时间关系**（DALI 规范 Table）：0 = 瞬时；1 = 0.707 s；2 = 1.0 s；"
        "3 = 1.414 s；4 = 2.0 s（出厂默认）；5 = 2.828 s；6 = 4.0 s；7 = 5.657 s；8 = 8.0 s；"
        "9 = 11.314 s；10 = 16.0 s；11 = 22.627 s；12 = 32.0 s；13 = 45.255 s；14 = 64.0 s；15 = 90.510 s。\n\n"
        "**与 `FADE RATE` 区别**：本字段控制 DAPC 类绝对命令的总时间；`FADE RATE` 控制 Up/Down 类步进命令的速率。\n\n"
        "**典型场景**：办公照明 `FADE TIME = 2` (1 s)；剧院 `FADE TIME = 8` (8 s)；HMI 滑块实时调光 "
        "`FADE TIME = 0`（瞬时跟手）。\n\n"
        "**典型陷阱**：① 上线时 FADE TIME 默认 0，从 DAPC 看上去像瞬时跳变，看似无渐变功能 → 设到非零；"
        "② 改 FADE TIME 后立即 DAPC，下一次 DAPC 才用新值。"
    ),
    pitfalls=[
        "FADE TIME = 0 时 DAPC 瞬时跳变。",
        "FADE TIME 是非线性的，不是秒数——查上表换算。",
        "改完用 `FB_DALIV2QueryFadeTimeFadeRate` 验证。",
    ],
    scenario=(
        "电影院散场灯——观众散场时灯渐渐亮起，从 0 用 8 秒渐变到 200。本 FB 把 FADE TIME 设为 8 (8 s)，"
        "然后 DAPC(200) 触发渐变。"
    ),
    value="灯具内部硬件完成渐变，PLC 端不用写循环；渐变曲线由 DALI 协议保证平滑。",
    alt=(
        "1) PLC 循环连续 DAPC 实现渐变：可行但占用通信带宽；2) `FB_DALIV2SetFadeRate` 配 Up/Down 步进调光："
        "粒度有限；3) **本 FB**：绝对命令渐变标准配置。"
    ),
    related=(
        "[`FB_DALIV2SetFadeRate`](FB_DALIV2SetFadeRate.md)、"
        "[`FB_DALIV2QueryFadeTimeFadeRate`](../part102_low_queries/FB_DALIV2QueryFadeTimeFadeRate.md)、"
        "[`FB_DALIV2DirectArcPowerControl`](../part102_low_power/FB_DALIV2DirectArcPowerControl.md)、"
        "[`FB_DALIV2GoToScene`](../part102_low_power/FB_DALIV2GoToScene.md)"
    ),
    tcpou_extra_decl="    nNewFadeTime     : BYTE := 4;\n",
    tcpou_extra_assign="nFadeTime        := nNewFadeTime,",
    tcpou_scenario="电影院散场场景：把 FADE TIME 设为 8（对应 8 秒）；然后 DAPC 让灯渐亮。",
    tcpou_verify=(
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
        "3. 用 P_Demo_FB_DALIV2QueryFadeTimeFadeRate 查 short addr 0 → FADE TIME 应等于 8。\n"
        "4. 然后用 P_Demo_FB_DALIV2DirectArcPowerControl 给 short addr 0 设 DAPC=200 → 灯应用 8 秒渐变到目标。"
    ),
))

SPECS.append(gen_set_value_fb(
    name="FB_DALIV2SetMaxLevel",
    section="4.1.2.3.3.7",
    topicid="142795659",
    subdir="part102_low_config",
    value_field="nMaxLevel",
    value_field_desc="目标 `MAX VALUE` 寄存器值（1..254）。灯具内部任何亮度命令都会被这个上限钳位",
    summary=(
        "**设置镇流器 `MAX VALUE` 寄存器**——灯具内部所有亮度命令的上限值，任何 DAPC / "
        "Recall / Up 超过此值都被钳位。出厂默认 254（即 100%）。"
        "工程上常调低用于保护灯具寿命 / 满足能耗法规。"
    ),
    behavior=(
        "**调用方式**：`bStart` 上升沿；本 FB 写 DTR0 = `nMaxLevel`，下发 `STORE THE DTR AS MAX LEVEL` "
        "把 DTR0 写入灯具 EEPROM。\n\n"
        "**MAX VALUE 的作用**：（1）`DAPC > nMaxLevel` 被钳到 nMaxLevel；（2）`RecallMaxLevel` 命令亮度等于 `nMaxLevel`；"
        "（3）`Up` 命令到达 `nMaxLevel` 后停。\n\n"
        "**典型应用**：① 路灯调光保护：把 MAX 设为 200（约 80%）延长 LED 寿命；② 能耗法规："
        "办公室白天 MAX = 200 节能；③ 用户调光体验：把 MAX 设到 200 而非 254，让全亮按钮不至于刺眼。\n\n"
        "**与 `MIN VALUE` 配套**：MAX 必须 > MIN；否则灯具行为未定义。\n\n"
        "**典型陷阱**：① MAX 设到 < `nLampPhysicalMinLevel`（灯具物理最小亮度）→ 命令无效；"
        "② MAX 设过低用户感觉不够亮投诉。"
    ),
    pitfalls=[
        "MAX 必须 > MIN，否则灯具行为未定义。",
        "MAX 设过低用户感觉不够亮——调光范围与体验权衡。",
        "改完用 `FB_DALIV2QueryMaxLevel` 验证。",
    ],
    scenario="路灯节能改造：把 MAX VALUE 从 254 调到 200（约 80%）保护 LED 延长寿命。",
    value="灯具硬件层面强制亮度上限，避免应用层错误命令把灯调过亮。",
    alt=(
        "1) 应用层校验亮度命令：可行但需所有命令点都检查；2) **本 FB**：灯具内部硬钳位，更可靠。"
    ),
    related=(
        "[`FB_DALIV2SetMinLevel`](FB_DALIV2SetMinLevel.md)、"
        "[`FB_DALIV2QueryMaxLevel`](../part102_low_queries/FB_DALIV2QueryMaxLevel.md)、"
        "[`FB_DALIV2RecallMaxLevel`](../part102_low_power/FB_DALIV2RecallMaxLevel.md)"
    ),
    tcpou_extra_decl="    nNewMaxLevel     : BYTE := 200;\n",
    tcpou_extra_assign="nMaxLevel        := nNewMaxLevel,",
    tcpou_scenario="路灯节能：把灯具 MAX VALUE 设为 200，限制最大亮度约 80%。",
    tcpou_verify=(
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
        "3. 用 P_Demo_FB_DALIV2QueryMaxLevel 查 short addr 0 → MAX 应等于 200。\n"
        "4. 用 P_Demo_FB_DALIV2RecallMaxLevel 触发全亮 → 灯应只到 200 而不是 254。"
    ),
))

SPECS.append(gen_set_value_fb(
    name="FB_DALIV2SetMinLevel",
    section="4.1.2.3.3.8",
    topicid="142797195",
    subdir="part102_low_config",
    value_field="nMinLevel",
    value_field_desc="目标 `MIN VALUE` 寄存器值（1..254）。任何亮度命令低于 `nMinLevel`（但 > 0）都被钳到 `nMinLevel`",
    summary=(
        "**设置镇流器 `MIN VALUE` 寄存器**——灯具最低非零亮度。任何 DAPC / Down 命令低于此值（但不为 0）"
        "都被钳到 `MIN VALUE`。"
        "0（关灯）不受此限。出厂默认 1（DALI 对数曲线最暗的非零档，约物理 0.1%）。"
    ),
    behavior=(
        "**调用方式**：`bStart` 上升沿；写 DTR0 = `nMinLevel`，下发 `STORE THE DTR AS MIN LEVEL`。\n\n"
        "**MIN VALUE 的作用**：（1）`DAPC` 0 < val < `nMinLevel` 被钳到 `nMinLevel`；（2）`RecallMinLevel` "
        "命令亮度 = `nMinLevel`；（3）`Down` 命令到达 `nMinLevel` 后停（不会关到 0）。\n\n"
        "**关灯特例**：`DAPC = 0` 一定关灯，不受 MIN 钳位。\n\n"
        "**典型应用**：① 调光下限保护——LED 灯极低亮度时可能闪烁，把 MIN 设到 50 避免；② 不希望"
        "调光时关灯——把 MIN 设到 1 让 Down 停在最暗但不关；③ 应急照明法规要求最低亮度，把 MIN 设为"
        "法规规定值（如 50% 即 193）。\n\n"
        "**典型陷阱**：① MIN > MAX 灯具行为未定义；② 设到 0 灯具拒绝；③ 实际 MIN 不能低于灯具"
        "`PHYSICAL MIN LEVEL`（灯具硬件极限），强制低于该值灯具自动钳到物理极限。"
    ),
    pitfalls=[
        "MIN 必须 1..254，且 < MAX；0 灯具拒绝。",
        "DAPC = 0 仍是关灯，不被 MIN 钳位。",
        "灯具硬件 `PHYSICAL MIN LEVEL` 优先——本 FB 设的值可能被灯具硬件钳到更高。",
    ],
    scenario="应急照明法规：要求最低亮度 50% (193)，把 MIN VALUE 设为 193——用户怎么调光都不低于 193。",
    value="灯具硬件层面强制亮度下限，运行时调光时不会跌穿。",
    alt="**本 FB**：调光下限标准方法。",
    related=(
        "[`FB_DALIV2SetMaxLevel`](FB_DALIV2SetMaxLevel.md)、"
        "[`FB_DALIV2QueryMinLevel`](../part102_low_queries/FB_DALIV2QueryMinLevel.md)、"
        "[`FB_DALIV2QueryPhysicalMinLevel`](../part102_low_queries/FB_DALIV2QueryPhysicalMinLevel.md)"
    ),
    tcpou_extra_decl="    nNewMinLevel     : BYTE := 100;\n",
    tcpou_extra_assign="nMinLevel        := nNewMinLevel,",
    tcpou_scenario="把灯具 MIN VALUE 设为 100，调光最暗不会低于约 5% 物理亮度。",
    tcpou_verify=(
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
        "3. 用 P_Demo_FB_DALIV2QueryMinLevel 查 → MIN 应为 100。\n"
        "4. 用 P_Demo_FB_DALIV2DirectArcPowerControl 设 DAPC=50 → 灯应跳到 100（被钳）；\n"
        "   DAPC=0 → 灯关（不受钳位）。"
    ),
))

SPECS.append(gen_set_value_fb(
    name="FB_DALIV2SetPowerOnLevel",
    section="4.1.2.3.3.9",
    topicid="142798731",
    subdir="part102_low_config",
    value_field="nPowerOnLevel",
    value_field_desc="目标 `POWER ON LEVEL`（0..254 或 MASK=255）。灯具供电恢复时自动调到此亮度。MASK 表示供电恢复后保持关灯",
    summary=(
        "**设置镇流器 `POWER ON LEVEL` 寄存器**——灯具供电恢复（如停电后来电）时自动调到的亮度。"
        "出厂默认 254（全亮）；可设为 MASK (255) 表示保持关灯（不自动开）。"
        "工程上常配置为 100..150 让来电后中等亮度（避免突然全亮刺眼）。"
    ),
    behavior=(
        "**调用方式**：`bStart` 上升沿；写 DTR0 = `nPowerOnLevel`，下发 `STORE THE DTR AS POWER ON LEVEL`。\n\n"
        "**`POWER ON LEVEL` 触发时机**：灯具上电（接到 220V AC）瞬间，灯具内部读 EEPROM 取 `POWER ON LEVEL`，"
        "如果 != MASK 则直接调到这个亮度；MASK 时保持关灯，等待 PLC 主动 DAPC。\n\n"
        "**典型应用**：① 走廊灯 POWER ON = 200（停电恢复后中等亮度）；② 应急灯 POWER ON = 254（自动全亮）；"
        "③ 装饰灯 POWER ON = MASK（来电后保持关，由场景控制器决定）。\n\n"
        "**典型陷阱**：① 默认 254 + 停电次数频繁时大量灯瞬间全亮，可能冲击电网；② MASK 后用户以为"
        "灯坏了，找不到原因（应在工程文档说明）。"
    ),
    pitfalls=[
        "POWER ON LEVEL 0..254 或 MASK (255)；其它值灯具忽略。",
        "默认 254 会在每次断电恢复时全亮，工程上常调到 100..150。",
        "MASK 设置后必须有 PLC 主动 DAPC 才能开灯。",
    ],
    scenario=(
        "办公楼夜间断电恢复——希望所有办公照明来电后调到 50% 亮度（POWER ON = 150）让保安巡夜，"
        "而不是突然全亮刺眼。"
    ),
    value="替代每次断电恢复都靠 PLC 程序识别 + DAPC 下发——硬件层面就解决。",
    alt=(
        "1) PLC 上电时主动 DAPC：要等 PLC 启动好（可能几秒）；2) **本 FB**："
        "灯具供电瞬间就生效，零延迟。"
    ),
    related=(
        "[`FB_DALIV2QueryPowerOnLevel`](../part102_low_queries/FB_DALIV2QueryPowerOnLevel.md)、"
        "[`FB_DALIV2QueryPowerFailure`](../part102_low_queries/FB_DALIV2QueryPowerFailure.md)、"
        "[`FB_DALIV2SetSystemFailureLevel`](FB_DALIV2SetSystemFailureLevel.md)"
    ),
    tcpou_extra_decl="    nNewPowerOnLevel : BYTE := 150;\n",
    tcpou_extra_assign="nPowerOnLevel    := nNewPowerOnLevel,",
    tcpou_scenario="办公楼夜间来电恢复希望中等亮度，把 POWER ON LEVEL 设为 150。",
    tcpou_verify=(
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
        "3. 用 P_Demo_FB_DALIV2QueryPowerOnLevel 查 → 应为 150。\n"
        "4. 真实验证需断开灯具 220V 再上电——重新通电后灯应直接到 150 而非 254。"
    ),
))

SPECS.append(gen_set_value_fb(
    name="FB_DALIV2SetScene",
    section="4.1.2.3.3.10",
    topicid="142800267",
    subdir="part102_low_config",
    value_field="nLevel",
    value_field_desc="场景对应的目标亮度值（0..254 或 MASK=255）。0 = 调用该场景时灯关；MASK = 灯不参与该场景",
    summary=(
        "**设置镇流器某个场景预设亮度值**——DALI 镇流器内部存 16 个场景寄存器（`SCENE 0..15`），"
        "每个场景对应一个亮度。本 FB 把 `nAddr` 寻址到的灯具的 `nScene` 场景值设为 `nLevel`。"
        "之后 `FB_DALIV2GoToScene` 触发该场景时该灯就会调到此亮度。"
    ),
    inputs_desc={
        "nLevel": "场景对应的目标亮度值（0..254 或 MASK=255）。0 = 调用该场景时灯关；MASK = 灯不参与该场景",
        "nScene": "目标场景号（0..15）",
    },
    behavior=(
        "**调用方式**：`bStart` 上升沿；本 FB 写 DTR0 = `nLevel`，下发 `STORE THE DTR AS SCENE n` 命令把"
        "对应场景寄存器写入 EEPROM。\n\n"
        "**与 `FB_DALIV2RemoveFromScene` 的区别**：本 FB 设具体亮度；后者直接清成 MASK（"
        "实际等同于本 FB 的 `nLevel = 255`）。设值含义：0 = 调场景时灯关；255 = 不参与场景；其它 = 调到该亮度。\n\n"
        "**批量配置流程**：工程初始化时按场景表逐个调本 FB——例如配置场景 0 = 会议开始（全亮）：对每盏灯调"
        "`SetScene(nScene=0, nLevel=254)`；配置场景 1 = 演示模式（只亮投影附近）：对投影附近灯调"
        "`SetScene(nScene=1, nLevel=200)`，对其它灯调 `SetScene(nScene=1, nLevel=0)`。\n\n"
        "**典型陷阱**：① 场景配置忘了所有灯都设——未设的灯 SCENE 值是 MASK（不参与），调场景时不变化；"
        "② 改场景值后应立即用 `FB_DALIV2QuerySceneLevel` 验证；③ 不要混用场景值 0 与 MASK——前者"
        "调场景时强制关灯，后者保持原状，行为完全不同。"
    ),
    pitfalls=[
        "`nLevel = 0` 强制关灯；`nLevel = 255 (MASK)` 不参与场景；其它值调到该亮度。",
        "`nScene > 15` 灯具忽略。",
        "工程上线批量配置后用 `FB_DALIV2QuerySceneLevel` 逐一验证。",
        "EEPROM 写次数有限。",
    ],
    scenario=(
        "会议室预设场景：场景 0 = 全亮（会议开场）、场景 1 = 演示模式（仅投影附近灯亮 200）、"
        "场景 2 = 休息（所有灯调到 100）、场景 3 = 离场（所有灯关）。本 FB 给每盏灯配置每个场景对应亮度。"
    ),
    value="替代手动给灯具贴标签 + 用厂家工具点选；批量 PLC 代码一次配置失电保护。",
    alt="**本 FB**：场景预设配置标准方法。",
    related=(
        "[`FB_DALIV2RemoveFromScene`](FB_DALIV2RemoveFromScene.md)、"
        "[`FB_DALIV2GoToScene`](../part102_low_power/FB_DALIV2GoToScene.md)、"
        "[`FB_DALIV2QuerySceneLevel`](../part102_low_queries/FB_DALIV2QuerySceneLevel.md)"
    ),
    tcpou_extra_decl="    nSceneToSet      : BYTE := 1;\n    nSceneLevel      : BYTE := 200;\n",
    tcpou_extra_assign="nScene           := nSceneToSet,\n    nLevel           := nSceneLevel,",
    tcpou_scenario="给 short addr 0 配置场景 1 对应亮度 200（演示模式投影附近灯）。",
    tcpou_verify=(
        "1. 通信 FB 跑起；编译；登录。\n"
        "2. 在线 bTrigger 一次上升沿；等 bBusy 回 FALSE。\n"
        "3. 用 P_Demo_FB_DALIV2QuerySceneLevel 查 short addr 0 场景 1 → 应等于 200。\n"
        "4. 用 P_Demo_FB_DALIV2GoToScene 触发场景 1 → 这盏灯应调到 200。"
    ),
))


def main():
    for spec in SPECS:
        # custom inputs_desc handling: some specs have it inline
        if "inputs_desc" not in spec and spec.get("inputs_desc"):
            pass
        doc_path, tcpou_path = write_pair(spec)
        print(f"  {doc_path.name}")
        print(f"  {tcpou_path.name}")


if __name__ == "__main__":
    main()
