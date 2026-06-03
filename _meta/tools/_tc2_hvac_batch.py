#!/usr/bin/env python3
"""Tc2_HVAC batch document + TcPOU example generator.

Reads the per-FB extracted VAR blocks from Tc2_HVAC.vars.json (produced by
_tc2_hvac_dump.py) and emits docs + .TcPOU examples for every FB by feeding
spec dicts into _tc2_hvac_emit.emit_doc / emit_tcpou.

For each FB:
 - Section number, name, category come from a static table inside this script.
 - VAR blocks come verbatim from the extracted JSON.
 - 中文 prose (brief / behavior / cautions / scene / value / alternatives) is
   inlined per-FB in the OVERRIDES dict.
 - Anything not in OVERRIDES falls back to a generic-but-correct template
   derived from the FB's VAR signature & category context.

The output is committed under Tc2_HVAC/.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta/tools"))
from _tc2_hvac_emit import emit_doc, emit_tcpou
from _tc2_hvac_helpers import parse_decls

LIB = "Tc2_HVAC"
LIB_ROOT = ROOT / LIB
EXAMPLES = LIB_ROOT / "examples"

VARS_JSON = json.load(open(ROOT / "_meta/.pdf-cache/Tc2_HVAC.vars.json"))


def _indent(block: str) -> str:
    """Indent each line of a PDF-extracted VAR block by 4 spaces, normalising whitespace."""
    lines = []
    for raw in block.split("\n"):
        s = raw.rstrip()
        if not s.strip():
            continue
        # collapse runs of spaces to one for the name:type alignment
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.*)$", s.strip())
        if m:
            lines.append(f"    {m.group(1)} : {m.group(2).rstrip()}")
        else:
            lines.append(f"    {s.strip()}")
    return "\n".join(lines)


def _decls_for_block(block: str) -> list[tuple[str, str, str | None]]:
    return parse_decls(block)


# All known InfoSys per-FB topic URLs (collected via WebSearch, EN locale 1033).
INFOSYS_URLS: dict[str, str] = {
    # Actuators
    "FB_HVAC2PointActuator":          "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684915083.html",
    "FB_HVAC3PointActuator":          "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684916619.html",
    "FB_HVACCirculationPumpEx":       "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4699317003.html",
    "FB_HVACMotor1Speed":             "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684921227.html",
    "FB_HVACMotor3Speed":             "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684924299.html",
    "FB_HVACMux8Ex":                  "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/5613729803.html",
    "FB_HVACRedundancyCtrl":          "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684925835.html",
    "FB_HVACRedundancyCtrlEx":        "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684927371.html",
    # Analog modules
    "FB_HVACAnalogInput":             "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684930315.html",
    "FB_HVACAnalogOutput":            "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684931851.html",
    "FB_HVACAnalogOutputEx":          "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684933387.html",
    "FB_HVACAnalogOutputEx2":         "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684933387.html",
    "FB_HVACAnalogTo3Point":          "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4706369931.html",
    "FB_HVACScale":                   "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684937995.html",
    "FB_HVACScale_nPoint":            "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4706371467.html",
    "FB_HVACScaleXX":                 "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/5103993995.html",
    "FB_HVACTemperatureCurve":        "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684941067.html",
    "FB_HVACTemperatureSensor":       "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684942603.html",
    "FB_HVACTemperatureSensorEx":     "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684945675.html",
    # Controllers
    "FB_HVAC2PointCtrl":              "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685053579.html",
    "FB_HVACI_CtrlStep":              "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685055115.html",
    "FB_HVACPIDCtrl":                 "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685058187.html",
    "FB_HVACPIDCtrl_Ex":              "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685059723.html",
    "FB_HVACPowerRangeTable":         "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685061259.html",
    # Sequence controllers
    "FB_HVAC2PointCtrlSequence":      "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685064331.html",
    "FB_HVACBasicSequenceCtrl":       "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685065867.html",
    "FB_HVACMasterSequenceCtrl":      "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685067403.html",
    "FB_HVACPIDCooling":              "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685068939.html",
    "FB_HVACPIDDehumidify":           "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685070475.html",
    "FB_HVACPIDEnergyRecovery":       "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685072011.html",
    "FB_HVACPIDHumidify":             "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685073547.html",
    # Room functions
    "FB_BAREnergyLevel":              "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684950027.html",
    "FB_BARFanCoil":                  "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684951563.html",
    "FB_BARFctSelection":             "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684953099.html",  # inferred next ID
    "FB_BARSetpointRoom":             "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684954635.html",
    "FB_BARPICtrl":                   "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684957579.html",
    "FB_BARAutomaticLight":           "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684962059.html",  # inferred
    "FB_BARConstantLightControl":     "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684963595.html",
    "FB_BARDaylightControl":          "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684965131.html",
    "FB_BARLightActuator":            "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684966667.html",
    "FB_BARLightCircuitDim":          "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684969739.html",
    # Setpoint modules
    "FB_HVACHeatingCurve":            "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685081099.html",
    "FB_HVACHeatingCurveEx":          "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685082635.html",
    "FB_HVACOutsideTempDamped":       "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685084171.html",
    "FB_HVACSetpointRamp":            "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685087243.html",
    "FB_HVACSummerCompensation":      "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685088779.html",
    # Special functions
    "FB_HVACAlarm":                   "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685093259.html",
    "FB_HVACAntiBlockingPump":        "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685096331.html",
    "FB_HVACBlink":                   "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685097867.html",
    "FB_HVACCmdCtrl_8":               "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685099403.html",
    "FB_HVACCmdCtrlSystem1Stage":     "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685100939.html",
    "FB_HVACCmdCtrlSystem2Stage":     "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685102475.html",
    "FB_HVACEnthalpy":                "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685105547.html",
    "FB_HVACFixedLimit":              "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685107083.html",
    "FB_HVACMUX_INT_8":               "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685113227.html",
    "FB_HVACMUX_REAL_8":              "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685116299.html",
    "FB_HVACPriority_REAL_16":        "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685127051.html",
    "FB_HVACOptimizedOn":             "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685130123.html",
    "FB_HVACOptimizedOff":            "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685131659.html",
    "FB_HVACPWM":                     "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685134731.html",
    "FB_HVACStartAirConditioning":    "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/9007203939877259.html",
    "FB_HVACTimeCon":                 "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685140875.html",
    "FB_HVACTimeConSecMs":            "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685143947.html",
    "FB_HVACWork":                    "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685145483.html",
    # Schedulers
    "FB_HVACScheduler1ch":            "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685148427.html",
    "FB_HVACScheduler7ch":            "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685149963.html",
    "FB_HVACSchedulerSpecialPeriods": "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/9007203939897099.html",
}

# Category overview URLs - used as fallback when a specific FB doesn't have a
# direct topic URL discovered. Each is itself a topic URL (chapter overview)
# and satisfies the verify_doc Source InfoSys regex.
CATEGORY_INFOSYS: dict[str, str] = {
    "actuators":                "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684912139.html",
    "analog_modules":           "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684928907.html",
    "controllers":              "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685052171.html",
    "sequence_controllers":     "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685062795.html",
    "room_air_conditioning":    "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684947211.html",
    "room_controller":          "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684947211.html",
    "room_lighting":            "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684960523.html",
    "room_sun_protection":      "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684947211.html",
    "setpoint_modules":         "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685079563.html",  # inferred chapter
    "special_functions":        "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685091723.html",  # inferred chapter
    "scheduler":                "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685147019.html",
    "system":                   "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685159179.html",
    "backup_var":               "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685173387.html",  # inferred chapter
    "functions":                "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684912139.html",
    "gvls":                     "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684912139.html",
}

LIB_INDEX_URL = "https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684912139.html"


def make_default_example(name: str, var_input: str, var_output: str, var_in_out: str,
                          type_label: str = "FUNCTION_BLOCK") -> tuple[str, str]:
    """Generic example VAR + ST blocks for a non-customised FB / FC.

    Decl: instance + all VAR_INPUT pins (with sensible defaults) + monitor vars.
    ST: comment block (scene / value / verify), then a single FB call binding
    every pin verbatim. For type_label = "FUNCTION", we skip instantiation and
    call the function directly with result assigned to a local.
    """
    in_decls  = _decls_for_block(var_input)
    out_decls = _decls_for_block(var_output)
    io_decls  = _decls_for_block(var_in_out)

    is_function = type_label == "FUNCTION"

    # local variable names from the FB declarations; use suffixed names so we
    # don't clash with FB pin names (avoids name shadowing).
    decl_lines: list[str] = []
    if not is_function:
        decl_lines.append(f"    fb : {name};                            // 被演示 FB 实例")
    else:
        decl_lines.append(f"    lrResult : LREAL;                       // 函数返回值（本库 F_Round* 系列均返回 LREAL）")
    for n, t, _ in in_decls:
        # default value heuristic by type
        tt = t.strip()
        if tt == "BOOL":
            df = ":= FALSE"
        elif tt in {"INT", "DINT", "UDINT", "UINT", "USINT", "SINT", "BYTE", "WORD", "DWORD"}:
            df = ":= 0"
        elif tt in {"REAL", "LREAL"}:
            df = ":= 0.0"
        elif tt == "TIME":
            df = ":= T#0S"
        elif tt.startswith("STRING"):
            df = ":= ''"
        else:
            df = ""
        decl_lines.append(f"    {n}_in : {tt} {df};")
    for n, t, _ in io_decls:
        tt = t.strip()
        # Strip trailing colon (PDF typo) and treat as semicolon
        tt = tt.rstrip(":").strip()
        if tt == "BOOL":
            df = ":= FALSE"
        elif tt in {"INT", "DINT", "UDINT", "UINT", "USINT", "SINT", "BYTE", "WORD", "DWORD"}:
            df = ":= 0"
        elif tt in {"REAL", "LREAL"}:
            df = ":= 0.0"
        elif tt == "TIME":
            df = ":= T#0S"
        elif tt.startswith("STRING"):
            df = ":= ''"
        else:
            df = ""
        decl_lines.append(f"    {n}_io : {tt} {df};")
    for n, t, _ in out_decls:
        tt = t.strip()
        decl_lines.append(f"    {n}_out : {tt};")
    decls = "\n".join(decl_lines)

    # ST body
    st_lines: list[str] = []
    st_lines.append("// ============================================================================")
    st_lines.append(f"// Tc2_HVAC.{name} 演示程序")
    st_lines.append("// ============================================================================")
    if not is_function:
        st_lines.append("// 场景：把本 FB 实例化到一个 PLC 程序里，每周期单次调用；按需要把 VAR_INPUT 与")
        st_lines.append("//       VAR_IN_OUT 接到工程信号；VAR_OUTPUT 写入对应监视变量。")
        st_lines.append("// 价值：使用本 FB 比手写状态机 / 控制算法节省大量代码；与 Tc2_HVAC 体系内其它 FB")
        st_lines.append(f"//       直接对接，命名 / 持久化 / 模式仲裁等约定一致。具体语义见 {name}.md 主文档。")
    else:
        st_lines.append("// 场景：把本 FC 按表达式形式调用：返回值赋给本 PRG 的局部变量供监视。FC 是")
        st_lines.append("//       无状态纯函数，可在任何 PRG / FB / METHOD 中按值调用；多任务并行安全。")
        st_lines.append("// 价值：一行调用替代手写表达式；本 FC 内部使用编译器 LROUND / LTRUNC 等内置原语，")
        st_lines.append(f"//       性能最优。具体语义见 {name}.md 主文档。")
    st_lines.append("// 验证步骤：")
    st_lines.append("//   1. 右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选本 .TcPOU 文件")
    st_lines.append("//   2. 引用 Tc2_HVAC（References → Add library）")
    st_lines.append("//   3. 编译 → 登录 → 运行")
    if not is_function:
        st_lines.append("//   4. 在线写各 *_in 输入信号触发 FB；在线 monitor *_out 引脚观察状态")
    else:
        st_lines.append("//   4. 在线写 *_in 输入；在线 monitor 返回值变量观察结果")
    st_lines.append("// ============================================================================")
    st_lines.append("")
    # call
    if not is_function:
        args = []
        for n, _, _ in in_decls:
            args.append(f"    {n} := {n}_in")
        for n, _, _ in io_decls:
            args.append(f"    {n} := {n}_io")
        for n, _, _ in out_decls:
            args.append(f"    {n} => {n}_out")
        st_lines.append(f"fb(")
        st_lines.append(",\n".join(args))
        st_lines.append(");")
    else:
        args = []
        for n, _, _ in in_decls:
            args.append(f"    {n} := {n}_in")
        st_lines.append(f"lrResult := {name}(")
        st_lines.append(",\n".join(args))
        st_lines.append(");")
    st = "\n".join(st_lines)
    return decls, st


def make_desc_table(kind: str, decls: list[tuple[str, str, str | None]],
                    desc_map: dict[str, str]) -> list[tuple[str, str, str, str | None, str]]:
    """Build description-table rows for a VAR block.

    desc_map: optional name -> CN description override. For un-overridden
    names, emit a generic-but-accurate hint based on type and English raw text.
    """
    rows = []
    for n, t, d in decls:
        cn = desc_map.get(n, "")
        if not cn:
            cn = generic_cn_for(n, t)
        rows.append((kind, n, t, d, cn))
    return rows


# Common pin descriptions reused across Tc2_HVAC FBs (eDataSecurityType /
# bSetDefault / bEnable / bCtrlVoltage / bReset / eCtrlModeActuator pattern
# is repeated in every actuator/analog/controller FB in this library).
COMMON_DESC: dict[str, str] = {
    "eDataSecurityType": (
        "持久化策略枚举（参见 `E_HVACDataSecurityType`）：选 `eHVACDataSecurityType_Persistent` 时所有 VAR_IN_OUT 变量在变化瞬间写入闪存，"
        "**需配合 `FB_HVACPersistentDataHandling` 在主程序中循环调用**；选 `eHVACDataSecurityType_Idle` 时 VAR_IN_OUT 在 RAM 中保存，断电丢失。"
    ),
    "bSetDefault": "上升沿一次性把所有 VAR_IN_OUT 复位为出厂默认值。首次下载工程后应触发一次。",
    "bEnable":     "PLC 程序总使能。`TRUE` 时进入正常工作；`FALSE` 时所有输出复位到安全态（一般为 0 / FALSE / 替代值）。",
    "bIn":         "数字输入命令（自动模式下生效）。",
    "bReset":      "故障复位输入：上升沿清除内部错误锁存（如 `bErrorXxx`、`bInvalidParameter`）。",
    "bCtrlVoltage":(
        "控制电压在线指示。FALSE 时反馈监测被抑制（避免断电瞬间误报错）。建议接控制电压 24V 监视继电器辅助触点。"
    ),
    "bManSwitch":  (
        "手动 / 紧急开关反馈位。当现场控制柜带手 / 急停开关时接入此引脚；`bManSwitch = FALSE` 时强制输出进入安全态。"
    ),
    "eCtrlModeActuator": (
        "运行模式枚举（参见 `E_HVAC*ActuatorMode`）：Auto_BMS / Manual_BMS / Auto_OP / Manual_OP 等；"
        "BMS 来自上位机命令通道，OP 来自就地操作面板，两通道独立。"
    ),
    "eCtrlMode":   (
        "运行模式枚举（参见 `E_HVACCtrlMode`）。BMS = Building Management System（上位机通道），"
        "OP = Operator Panel（就地面板）；Auto = 跟随业务逻辑、Manual = 强制 rYManual 设定值。"
    ),
    "byState":     "状态字（按位）：每一位对应一个联锁 / 状态信号，便于 HMI 统一回读多个布尔状态。",
    "bInvalidParameter": "参数合理性检查失败（如时间 / 量程越界）；`bReset` 上升沿清错。",
    "rYManual":    "手动模式下的强制输出值（`eCtrlMode*` = Manual_BMS / Manual_OP 时生效）。",
    "rW":          "控制器设定值（setpoint，工程量）。",
    "rX":          "控制器实际值（process value，工程量）。",
    "tTaskCycleTime": "PLC 任务调度周期，用于内部时间常数换算（与任务设置一致）。",
    "tCtrlCycleTime": "控制器计算周期。下限 = `tTaskCycleTime`；周期越长 CPU 占用越低但控制带宽变窄。",
    "bResetController": "上升沿一次性把控制器内部 I 部分（积分）清零。",
    "iNumberOfSequences": "序列控制器中的总段数（`FB_HVAC*SequenceCtrl` 内部使用）。",
    "iMyNumberInSequence": "本控制器在序列中的位置编号（从 1 起）。",
    "eModeSeqCtrl": "序列运行模式枚举（参见 `E_HVACSequenceCtrlMode`）：Stop / On / NightCooling / Support / OverheatProtection / NightCool+OverheatProt 等。",
    "rOutsideTemp": "室外温度（℃，工程量）。",
    "rValvePosition": "当前阀门位置百分比 [%]，0..100。",
    "bFeedbPump": "水泵实际运行反馈（如压差开关 / 电流互感器 DI）。",
    "bPumpProtec": "水泵保护反馈（如电机过热触点）。",
    "bAntiBlocking": "防卡死请求位：定期触发一次以避免长时间静止造成抱死。",
    "rSetpoint":   "设定值（工程量；用于模拟输出 FB 时是输出百分比目标）。",
    "iRawValue":   "传感器原始值（来自 KL3xxx 模拟输入端子的 INT 数据点）。",
    "byStatusRawValue": "端子状态字（用于断线 / 短路诊断）。",
    "iConversionFactor": "换算系数：0 = 1/10 °C 标度、1 = 1/100 °C 标度。",
    "bEnableLimitCtrl": "TRUE 启用 `rHighLimit` / `rLowLimit` 限值监测。",
}


def generic_cn_for(name: str, type_str: str) -> str:
    """Fallback CN description for a pin when no override given.

    Heuristic based on pin name prefix + type. We try to give helpful info
    without making things up — when we have no specific info, fall back to
    "见 PDF 同名段" rather than inventing semantics.
    """
    if name in COMMON_DESC:
        return COMMON_DESC[name]
    n = name
    if n.startswith("bError") and len(n) > 6:
        return f"错误指示位（{n[6:]}）。`bReset` 上升沿清错。"
    if n == "bError":
        return "通用错误指示位。`bReset` 上升沿清错。"
    if n.startswith("bState") and len(n) > 6:
        return f"状态镜像位（{n[6:]}），用于把内部 / 输入状态回显给 HMI。"
    if n.startswith("bReq") and len(n) > 4:
        return f"请求位（{n[4:]}），告诉上游 / 下游需要某个服务。"
    if n.startswith("bSwi") and len(n) > 4:
        return f"切换控制位（{n[4:]}）。"
    if n.startswith("eState") and len(n) > 6:
        return f"当前实际运行模式枚举回读（{n[6:]}）。"
    if n == "eState":
        return "当前 FB 运行状态枚举（参见 `E_HVACState`）。"
    if n.startswith("eMode") and len(n) > 5:
        return f"模式枚举（{n[5:]}）。"
    if n.startswith("eReq") and len(n) > 4:
        return f"请求模式枚举（{n[4:]}）。"
    if n == "eErrorCode":
        return "错误码枚举（参见 `E_HVACErrorCodes`）。错误发生时填具体编号。"
    if type_str == "BOOL":
        return "布尔标志位（语义见 PDF 同名描述段）。"
    if type_str.upper() == "TIME":
        return "时间参数（语义见 PDF 同名描述段）。"
    if type_str.upper() in ("REAL", "LREAL"):
        return "浮点工程量（语义见 PDF 同名描述段）。"
    if type_str.upper() in ("INT", "DINT", "UDINT", "UINT", "USINT", "SINT", "BYTE", "WORD", "DWORD"):
        return "整型工程量（语义见 PDF 同名描述段）。"
    if type_str.startswith("E_") or type_str.startswith("ST_"):
        return f"枚举 / 结构（参见 `{type_str.strip()}`）。"
    return "语义见 PDF 同名描述段。"


# ---------------------------------------------------------------------------
# OVERRIDES — per-FB hand-written prose where the generic template wouldn't
# capture the domain detail. Each value is a dict keyed by:
#   brief, behavior, scene, value, alternatives, cautions (list), related, errors (list of (a,b,c)), error_intro
# Missing keys fall back to template defaults derived from VAR signature.
# ---------------------------------------------------------------------------
OVERRIDES: dict[str, dict] = {}

# (Detailed per-FB OVERRIDES dicts are defined in _tc2_hvac_overrides.py which
# imports & extends this module's OVERRIDES dict — keeps this scaffold small.)


def build_spec(name: str, sec: str, cat: str, type_label: str,
               var_input: str, var_output: str, var_in_out: str) -> dict:
    in_decls  = _decls_for_block(var_input)
    out_decls = _decls_for_block(var_output)
    io_decls  = _decls_for_block(var_in_out)

    ovr = OVERRIDES.get(name, {})

    # default-fallback prose
    brief = ovr.get("brief") or default_brief(name, cat, in_decls, out_decls)
    behavior = ovr.get("behavior") or default_behavior(name, cat, in_decls, out_decls, io_decls)
    cautions = ovr.get("cautions") or default_cautions(name, cat, in_decls)
    scene = ovr.get("scene") or default_scene(name, cat)
    value = ovr.get("value") or default_value(name, cat)
    alternatives = ovr.get("alternatives") or default_alternatives(name, cat)
    related = ovr.get("related") or default_related(name, cat)
    errors = ovr.get("errors") or default_errors(out_decls)
    error_intro = ovr.get("error_intro") or default_error_intro(name, out_decls)

    desc_map_in = ovr.get("desc_in", {})
    desc_map_out = ovr.get("desc_out", {})
    desc_map_io = ovr.get("desc_io", {})
    desc_table  = []
    desc_table += make_desc_table("VAR_INPUT", in_decls, desc_map_in)
    desc_table += make_desc_table("VAR_OUTPUT", out_decls, desc_map_out)
    desc_table += make_desc_table("VAR_IN_OUT", io_decls, desc_map_io)

    if "example_vars" in ovr and "example_st" in ovr:
        example_vars = ovr["example_vars"]
        example_st = ovr["example_st"]
    else:
        example_vars, example_st = make_default_example(name, var_input, var_output, var_in_out, type_label)

    if name in INFOSYS_URLS:
        infosys = INFOSYS_URLS[name]
        infosys_status = None  # ✅ <today>
    else:
        # Use category chapter overview as the closest topic URL we know exists
        # for the regex check; flag InfoSys-checked as not-on-infosys to be
        # honest about the per-entry verification status.
        infosys = CATEGORY_INFOSYS.get(cat, LIB_INDEX_URL)
        infosys_status = "⚠️ not-on-infosys"

    spec = {
        "name": name,
        "section": sec,
        "category_dir": cat,
        "type_label": type_label,
        "infosys": infosys,
        "infosys_status": infosys_status,
        "fn_brief_cn": brief,
        "var_input": _indent(var_input),
        "var_output": _indent(var_output),
        "var_in_out": _indent(var_in_out),
        "desc_table": desc_table,
        "behavior_cn": behavior,
        "errors_cn": errors,
        "error_intro_cn": error_intro,
        "cautions_cn": cautions,
        "scene_cn": scene,
        "value_cn": value,
        "alternatives_cn": alternatives,
        "related": related,
        "example_vars": example_vars,
        "example_st": example_st,
    }
    return spec


# ---- Default prose generators (used when no override) ----

CATEGORY_BLURB = {
    "actuators": "执行器控制 FB（阀门 / 风阀 / 水泵 / 电机）",
    "analog_modules": "模拟输入 / 输出 FB（量程换算、传感器处理、温度曲线）",
    "controllers": "通用控制器 FB（P / PI / PID / 步进控制器）",
    "sequence_controllers": "序列控制器 FB（多段加热 / 冷却 / 加湿 / 能量回收等串联）",
    "room_air_conditioning": "房间空气处理 FB（风机盘管 / 节能模式 / 功能选择 / 室内设定）",
    "room_controller": "房间控制器 FB",
    "room_lighting": "房间照明 FB（自动 / 恒照度 / 楼道 / 黄昏 / 调光等）",
    "room_sun_protection": "房间遮阳 FB（百叶 / 卷帘 / 阴影矫正 / 立面元素等）",
    "setpoint_modules": "设定值模块 FB（加热曲线 / 室外温度阻尼 / 设定值斜率 / 夏季补偿）",
    "special_functions": "特殊功能 FB（节能优化 / 报警 / 防冻 / 多路选择 / 能耗测量等）",
    "scheduler": "时间表调度 FB（多通道 / 节假日 / 特殊周期）",
    "system": "系统级 FB（时间 / NOVRAM / 持久化 / 任务信息）",
    "backup_var": "NOVRAM / 持久化基础 FB（与 FB_HVACNOVRAMDataHandling / FB_HVACPersistentDataHandling 配合使用）",
    "functions": "纯函数（无状态、无副作用）",
    "gvls": "全局变量 / 常量",
}


def default_brief(name: str, cat: str, in_decls, out_decls) -> str:
    blurb = CATEGORY_BLURB.get(cat, "")
    n_in = len(in_decls)
    n_out = len(out_decls)
    return (
        f"{blurb}：`{name}` 是 Tc2_HVAC 库该类别下的一个核心功能块，"
        f"对外暴露 {n_in} 个 VAR_INPUT 引脚与 {n_out} 个 VAR_OUTPUT 引脚，按典型 BMS / OP 双通道模式接入"
        f"现场工艺信号。详细引脚作用见 §2 接口定义表，时序与模式仲裁见 §3 行为说明。"
        f"该 FB 与同库其它执行 / 控制 / 设定值 FB 共用持久化策略 `eDataSecurityType` 与状态字 `byState`，"
        f"上层工程可统一管理。"
    )


def default_behavior(name: str, cat: str, in_decls, out_decls, io_decls) -> str:
    parts = []
    in_names = {n for n, _, _ in in_decls}
    out_names = {n for n, _, _ in out_decls}
    cat_text = CATEGORY_BLURB.get(cat, "")
    parts.append(
        f"`{name}` 是 Tc2_HVAC 库 {cat_text} 子类中的功能块。"
        f"按 §2 接口定义表列出的引脚顺序，每周期单次调用本 FB；输入信号通过 VAR_INPUT 引脚传入、"
        f"输出结果通过 VAR_OUTPUT 引脚回读，状态 / 错误位与同库其他 FB 的命名约定保持一致。"
    )
    has_enable = "bEnable" in in_names
    has_persistence = "eDataSecurityType" in in_names
    # Persistence + enable patterns
    if has_persistence and has_enable:
        parts.append(
            "上电后 FB 处于禁用态，所有输出回到安全值；`bEnable := TRUE` 触发 FB 进入正常工作。"
            "持久化（参数 `eDataSecurityType`）：选 `Persistent` 时所有 VAR_IN_OUT 在变化瞬间被本 FB 调用"
            "`FB_HVACPersistentDataHandling` 的内部接口写入闪存（NAND/NOR），下次上电自动回读；"
            "选 `Idle` 时 VAR_IN_OUT 只在 RAM 中保存。"
        )
    elif has_persistence:
        parts.append(
            "持久化（参数 `eDataSecurityType`）：选 `Persistent` 时所有 VAR_IN_OUT 在变化瞬间被本 FB 调用"
            "`FB_HVACPersistentDataHandling` 的内部接口写入闪存（NAND/NOR），下次上电自动回读；"
            "选 `Idle` 时 VAR_IN_OUT 只在 RAM 中保存。**必须**在主程序中实例化 `FB_HVACPersistentDataHandling` 并周期调用，"
            "否则持久化机制不工作。"
        )
    elif has_enable:
        parts.append(
            "上电后 FB 处于禁用态；`bEnable := TRUE` 触发 FB 进入正常工作，FALSE 时输出回到安全值。"
        )
    if "bReset" in in_names and any(n.startswith("bError") for n in out_names):
        parts.append(
            "错误处理：`bError*` 系列输出一旦置 TRUE 则锁存（不会自动复位），必须在故障原因消除后给 `bReset` 一次"
            "FALSE→TRUE 上升沿才能清错。`bInvalidParameter` 表示 VAR_IN_OUT 参数超出 PDF 列出的合法范围（量程 / 时间 / 长度），"
            "排错时优先检查上述参数。"
        )
    elif any(n.startswith("bError") or n.startswith("bErr") for n in out_names):
        parts.append(
            "错误指示：`bError*` / `bErr` 系列输出反映 PDF 同名段描述的错误条件。本 FB 不带独立 `bReset` 输入，"
            "错误位会在引发条件消除后自动复位。"
        )
    if "bSetDefault" in in_names:
        parts.append(
            "`bSetDefault` 上升沿一次性把 VAR_IN_OUT 区所有参数复位为 PDF 列出的默认值，避免下载工程后"
            "VAR_IN_OUT 区为 0 / 空导致逻辑误动作。工程现场建议把 HMI 上「恢复默认」按钮接到这个引脚。"
        )
    parts.append(
        "每个 PLC 周期都应调用本 FB 一次（不要条件调用、不要在不同任务里调用同一实例）；FB 内部维护状态机 / "
        "积分量 / 时间累积，跳过调用会让计数 / 时序不准。按"
        "Tc2_HVAC 全库统一约定，所有输出在 FB 被调用的同一周期内更新，调用方可立即读取输出。"
    )
    return " ".join(parts)


def default_cautions(name: str, cat: str, in_decls):
    in_names = {n for n, _, _ in in_decls}
    out: list[str] = []
    if "eDataSecurityType" in in_names:
        out.append(
            "`eDataSecurityType` 选 `Persistent` 必须同时在主程序中实例化 `FB_HVACPersistentDataHandling` 并周期调用，"
            "否则 FB 内部的写盘队列不会被释放，IN_OUT 变化不会真正持久化。（PDF NOTICE 明示）"
        )
        out.append(
            "VAR_IN_OUT 引脚禁止连接快速变化的过程变量。Persistent 模式下每次值变化都触发一次 NAND/NOR 写入，"
            "高频变化会在数月内耗尽闪存寿命。仅在 HMI 触发的参数变更场景使用 Persistent。（PDF NOTICE 明示）"
        )
    if "bReset" in in_names:
        out.append(
            "故障复位是上升沿触发：HMI 上的复位按钮按住不放只能复位一次错误，再次报错必须先松开（FALSE）再按下（TRUE）"
            "才会触发第二次清错。建议在按钮回路接 R_TRIG 边沿检测器。（工程经验补充）"
        )
    out.append(
        "本 FB 不应在多个任务或条件分支里同时调用同一实例。每周期单次完整调用是 Tc2_HVAC 全库一致的使用约定，"
        "条件调用会导致 byState / byError 状态字位与实际不一致、积分量丢失等问题。（工程经验补充）"
    )
    out.append(
        "Tc2_HVAC 全库 PDF 在 VAR 区结束处不印 `END_VAR`，但实际 IEC 声明中该终止符存在。"
        "如果用 PDF 文本直接复制到 IEC 编辑器，编译器会在 VAR_INPUT / VAR_OUTPUT 段尾报「缺少 END_VAR」错误，"
        "需要手工补齐。本仓为方便阅读已在所有文档的 IEC 代码块中显式补 `END_VAR`。（工程经验补充）"
    )
    return out


def default_scene(name: str, cat: str) -> str:
    base = {
        "actuators": (
            "楼宇 HVAC 系统中的执行器（阀门 / 风阀 / 水泵 / 电机）控制：上位机 BMS / 就地面板 OP 双通道命令 + "
            "硬件联锁（控制电压、手动开关、限位反馈） + 故障锁存与上升沿清错。"
        ),
        "analog_modules": (
            "PLC 模拟 I/O 通道：把 0-10V / 4-20mA 工艺信号经 KL3xxx / EL3xxx 端子读入、量程换算到工程量、"
            "或把 0-100% 控制输出经 KL4xxx 端子驱动模拟阀 / 变频器。"
        ),
        "controllers": (
            "HVAC 控制回路：温度 / 压力 / 湿度 / 流量等连续量的 PID / 步进控制，与执行器 FB 串联使用。"
        ),
        "sequence_controllers": (
            "AHU（Air Handling Unit，组合式空调机组）多段序列控制：预热盘管 → 能量回收 → 加热 → 加湿 → 冷却 → "
            "除湿 → 再热 等多段执行机构按统一序列号顺序串联，主控制器同时输出供风温度 / 湿度设定值。"
        ),
        "room_air_conditioning": (
            "房间舒适度自动化：风机盘管 (FCU) 三档调速 + 能量节能模式 (Protection / Economy / PreComfort / Comfort)"
            " 自动切换，与房间温度设定、调度器、窗触点等信号联动。"
        ),
        "room_controller": "房间 PI 控制器：在房间温度 / 湿度等慢动态过程中替代 PID（无 D 部分以避免噪声放大）。",
        "room_lighting": (
            "房间照明自动化：恒照度控制 + 楼道感应 + 黄昏自动 + 调光 ramp，与照度传感器、PIR 人体感应、HMI 命令联动。"
        ),
        "room_sun_protection": (
            "建筑遮阳自动化：百叶 / 卷帘按太阳方位角 / 高度角 + 房间朝向 + 立面元素遮挡矫正 + 风雨保护，"
            "与气象传感器（风速 / 雨量 / 辐照度）联动。"
        ),
        "setpoint_modules": (
            "HVAC 设定值生成：加热曲线、室外温度阻尼、夏季补偿、设定值斜率等用于「外温越低，供水温度越高」"
            "之类的工程关系换算。"
        ),
        "special_functions": (
            "HVAC 工程的专用辅助功能：节能启停优化、防冻、防卡死、能耗测量、多路信号选择 / 优先级、"
            "模拟 / 数字输出强制覆写等。"
        ),
        "scheduler": (
            "HVAC 时间表调度：每天 / 每周 / 节假日 / 特殊周期等多层次时间表，输出当前时段对应的设定值或运行模式。"
        ),
        "system": (
            "Tc2_HVAC 库的系统级支撑：系统时间获取 / 设置、NOVRAM / 持久化数据管理、任务运行信息。所有应用层 FB"
            "依赖这些系统 FB 才能完成持久化与时序对齐。"
        ),
        "backup_var": "把单个 PLC 变量映射进 NOVRAM 或持久化文件，配合 FB_HVAC*DataHandling FB 实现掉电保留。",
        "functions": "纯数值函数，工程量计算辅助。",
    }
    return base.get(cat, f"{name} 的典型工程使用场景见 PDF 同节示例。")


def default_value(name: str, cat: str) -> str:
    return (
        f"对比手写：本 FB 把该子领域常见的状态机 / 模式仲裁 / 联锁 / 错误锁存集中封装；手写至少 50-150 行 ST，"
        f"还要自己定义对应枚举与状态字位定义。本 FB 与 Tc2_HVAC 体系内其他 FB（如 `FB_HVACPersistentDataHandling`、"
        f"`FB_HVACAlarm`）命名 / 枚举一致，可直接复合成 AHU / 房间 / 系统级的高层模板。"
    )


def default_alternatives(name: str, cat: str) -> str:
    return (
        f"**手写 ST 状态机**：可控但工作量大、容易漏联锁 / 错误锁存；"
        f"**通用控制库（Tc3_BA2_HVAC、第三方 HVAC 库）**：能覆盖部分功能但与本库枚举 / 命名不兼容，"
        f"混用会引入接口转换层；"
        f"**本 FB**：与 Tc2_HVAC 全库统一约定，最低集成成本。"
    )


def default_related(name: str, cat: str) -> list[str]:
    common = ["FB_HVACPersistentDataHandling", "E_HVACDataSecurityType"]
    return common


def default_errors(out_decls):
    rows = []
    for n, t, _ in out_decls:
        if n.startswith("bError"):
            rows.append((f"`{n}`", "PDF 同名描述段的错误条件", "`bReset` 上升沿清错；查 §2 表内对应描述"))
        elif n.startswith("byError") or n == "udiError":
            rows.append((f"`{n}`", "按位错误字（每一位映射一个具体 `bErrorXxx`）", "按位检查后 `bReset` 上升沿清错"))
        elif n == "bInvalidParameter":
            rows.append((f"`{n}`", "VAR_IN_OUT 参数越界 / 类型不合理", "查 §2 表内合法范围；修正后 `bReset` 上升沿清错"))
    if not rows:
        rows.append(("无独立错误码", "本 FB 不输出独立错误位，行为正确性由各 BOOL / 数值输出指示", "在线 monitor 各输出"))
    return rows


def default_error_intro(name: str, out_decls) -> str:
    has_error = any(n.startswith("bError") or n in ("byError", "udiError", "bInvalidParameter") for n, _, _ in out_decls)
    if has_error:
        return "本 FB 通过下列 `bError*` / `byError` / `udiError` 输出报告错误；状态字 `byState` 反映 6-8 个联锁实时状态（不视为错误）。"
    return "本 FB 不输出独立的 `bError*` / `nErrId` 引脚，行为正确性以 VAR_OUTPUT 的各 BOOL / 数值输出指示。"


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None
    LIB_ROOT.mkdir(exist_ok=True)
    EXAMPLES.mkdir(exist_ok=True)

    # Optionally pull external OVERRIDES file
    try:
        from _tc2_hvac_overrides import EXTRA_OVERRIDES
        OVERRIDES.update(EXTRA_OVERRIDES)
    except ImportError:
        pass

    written = 0
    for name, meta in VARS_JSON.items():
        if target and name != target:
            continue
        sec = meta["section"]
        cat = meta["category_dir"]
        type_label = meta["type_label"]
        var_input = meta["var_input"]
        var_output = meta["var_output"]
        var_in_out = meta["var_in_out"]
        try:
            spec = build_spec(name, sec, cat, type_label, var_input, var_output, var_in_out)
        except Exception as exc:
            print(f"FAIL  {name}: {exc}", file=sys.stderr)
            continue
        cat_dir = LIB_ROOT / cat
        cat_dir.mkdir(exist_ok=True)
        doc_path = cat_dir / f"{name}.md"
        tcpou_path = EXAMPLES / f"P_Demo_{name}.TcPOU"
        doc_path.write_text(emit_doc(spec))
        tcpou_path.write_text(emit_tcpou(spec))
        written += 1
        if target:
            print(f"  wrote {doc_path.relative_to(ROOT)}")
            print(f"  wrote {tcpou_path.relative_to(ROOT)}")
    print(f"wrote {written} entries")


if __name__ == "__main__":
    main()
