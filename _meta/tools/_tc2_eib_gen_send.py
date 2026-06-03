#!/usr/bin/env python3
"""Library-internal generator for Tc2_EIB SEND + FUNCTIONS docs + TcPOU examples.

Run from repo root AFTER running _tc2_eib_gen.py:
    python3 _meta/tools/_tc2_eib_gen_send.py

Produces send/*.md (29) + functions/*.md (2) + corresponding TcPOU files.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))
from _tc2_eib_gen import md, tcpou, ENTRIES, ERROR_TABLE_SEND_COMMON, INFOSYS_BASE


# ============================================================================
# Common send blocks
# ============================================================================

# iMode mode descriptions for _EX FBs (PDF text, common)
IMODE_EX_DESC_DETAIL = (
    "**`iMode` 模式（_EX 系列）**：\n"
    "- `0` = Manual：`bStart` 上升沿触发 1 次发送，`bBusy` 期间忽略后续触发\n"
    "- `1` = Polling：`bStart = TRUE` 期间按 `CyclePolling` 周期定时发送（不论数据变没变）\n"
    "- `2` = OnChange：`bStart = TRUE` 期间数据变化才发送，`MinSendTime` 控制最短发送间隔（≥ 200 ms）\n"
    "- `3` = OnChangePolling：`bStart = TRUE` 期间按 `CyclePolling` 周期定时发送 + 数据变化时立即发送，`MinSendTime` 仍控制最短间隔\n\n"
)

SEND_PLAIN_BEHAVIOR = (
    "**触发方式**：每周期调用本 FB；**只要数据值（{data_var}）发生变化**，库就把新值编码成 EIB telegram 并下发到 EIB 总线。"
    "**初次调用**也会发一次（首次值通过）。\n\n"
    "**最小发送间隔**：本 FB 不带 `MinSendTime` 引脚，但库内部固化了 {min_send}（PDF §4.2.5.x 描述）。"
    "在间隔内连续变化会被合并——最后一次值在间隔到期后被发出（PDF "
    "\"No new EIB telegram is sent if the value changes within the min. send time but falls back to the old, already sent value within the min. send time\" 描述：变化又回到旧值则不发新帧）。\n\n"
    "**与 KL6301 依赖**：必须先有 `KL6301.bReady = TRUE`；本 FB 与 KL6301 必须**同一 PLC 任务**；"
    "`str_Rec` 必须传 KL6301 的 `str_Data_Rec` 同一个实例。\n\n"
    "**`Group_Address` 必须出现在 KL6301 过滤器内**——否则 KL6301 不 ACK 也不下发，发送看似「成功」但 EIB 物理层根本没出帧。"
)


SEND_EX_BEHAVIOR = (
    IMODE_EX_DESC_DETAIL +
    "**触发流程**：\n\n"
    "1. `bStart` 上升沿 → 根据 `iMode` 选定的发送策略开始执行；`bBusy := TRUE` 直到发送完成或失败\n"
    "2. 发送成功 → `bBusy := FALSE`，`bError := FALSE`\n"
    "3. 发送失败 → `bBusy := FALSE`，`bError := TRUE`，`iErrorID` 给错误码\n\n"
    "**`bEnableReadReq`**：使能响应 EIB Read 请求。设 TRUE 时，若 EIB 网内有别人对本 `Group_Address` 发 Read_Group_Req，"
    "本 FB 会自动回应当前数据值；设 FALSE 不响应。\n\n"
    "**`CyclePolling` 最小值 200 ms**：低于 200 ms 库强制按 200 ms 处理。\n\n"
    "**`MinSendTime` 最小值 200 ms**：同上。OnChange 模式下避免高频抖动 telegram 刷屏。\n\n"
    "**与 KL6301 依赖**：必须 `KL6301.bReady = TRUE`；同 PLC 任务；`str_Rec` 传 `KL6301.str_Data_Rec` 同一实例；"
    "`Group_Address` 必须在过滤器内。"
)


SEND_PLAIN_NOTES_COMMON = [
    "**只在数据变化时发送**：写 `iData := iData` 不会触发 telegram。要强制重发用对应 `_EX` 版本的 Polling 模式。",
    "**最小发送间隔由库固化**：在间隔内的连续变化会被合并；中间值会丢。需要精细控制就用 `_EX` 版本。",
    "**`Group_Address` 不在 KL6301 过滤器内 → 静默丢弃**：写值看似成功但 EIB 网上没出帧。",
    "**必须 `KL6301.bReady = TRUE`** 才能开始发送；启动前调用本 FB 不会出错但也不会发。",
    "**与所有 EIB FB 在同一 PLC 任务**：跨任务 EIB_REC 状态不一致，发送丢失。",
    "**EIB 网络高负载时会触发 `WATCHDOG_ERROR_NO_SEND` (104)**：本帧未发出，失败的 group address 记录在 `KL6301.NotSendGroup` 局部变量供调试。（工程经验补充）",
]


SEND_EX_NOTES_COMMON = [
    "**`iMode = 1` 时 `CyclePolling` 起作用**：周期发送即使数据不变。注意带宽占用——多 _EX 实例同时 Polling 会冲爆 EIB 网。",
    "**`iMode = 2` OnChange + `MinSendTime` 抑频**：避免抖动数据轰炸 EIB 网。MinSendTime 内变化会被合并。",
    "**`CyclePolling` 与 `MinSendTime` 下限均为 200 ms**：库强制；填更小值无效。",
    "**`bBusy` 期间忽略新触发**：上一次发送未完成时，`bStart` 重新拉高不会「排队」，只能等 `bBusy` 回 FALSE。",
    "**`bEnableReadReq` 使能 read 响应**：BMS 监控软件经常用 Read_Group_Req 主动查值；不使能就查不到。",
    "**与 KL6301 在同一 PLC 任务**：跨任务静默丢失。",
    "**iMode 改变需先把 `bStart` 拉低**：上升沿才采样 iMode；运行中改 iMode 不会立即生效。（工程经验补充）",
    "**与对应非 _EX 版本不可对同一 Group_Address 共用**：会冲突；选一种用。（工程经验补充）",
]


# ============================================================================
# Send FB template — plain (no _EX)
# ============================================================================

def _send_plain_fb(name, infosys_id, pdf_section, data_pin, dpt_desc,
                   min_send, scenario_data):
    """Generate a non-_EX send FB entry.

    data_pin: (var_name, var_type, var_desc)
    dpt_desc: e.g. "DPT 9.xxx (2-byte float)"
    min_send: e.g. "1 sec" or "200 ms"
    scenario_data: dict with scene/value/verify/decl/st/etc.
    """
    name_low = name.lower()
    var_input = "VAR_INPUT\n"
    var_input += "    Group_Address : EIB_GROUP_ADDR;\n"
    var_input += f"    {data_pin[0]:<13} : {data_pin[1]};\n"
    var_input += "    str_Rec       : EIB_REC;\n"
    var_input += "END_VAR"
    in_vars = [
        ("Group_Address", "EIB_GROUP_ADDR", None,
         "**目标 EIB 组地址**（数据发送到的地址；必须在 KL6301 过滤器内）"),
        (data_pin[0], data_pin[1], None, data_pin[2]),
        ("str_Rec", "EIB_REC", None,
         "收发胶水结构，必须传 `KL6301.str_Data_Rec` 同一个实例"),
    ]
    var_output = (
        "VAR_OUTPUT\n"
        "    bError   : BOOL;\n"
        "    iErrorID : EIB_ERROR_CODE;\n"
        "END_VAR"
    )
    out_vars = [
        ("bError", "BOOL", "发送出错时置 TRUE；错误码在 `iErrorID`"),
        ("iErrorID", "EIB_ERROR_CODE", "错误码，详见 `EIB_ERROR_CODE` 枚举"),
    ]
    return {
        "name": name,
        "category": "send",
        "category_label": "Send",
        "infosys_id": infosys_id,
        "pdf_section": pdf_section,
        "type": "FUNCTION_BLOCK",
        "var_input_block": var_input,
        "in_vars": in_vars,
        "var_output_block": var_output,
        "out_vars": out_vars,
        "var_inout_block": None,
        "inout_vars": None,
        "brief": (
            f"**发送 {dpt_desc} telegram**：把 IEC `{data_pin[1]}` 值经库编码成 EIB 标准格式，"
            f"发送到指定 `Group_Address`。"
            f"**只在 `{data_pin[0]}` 值变化时下发**——周期重发要用 `{name}_EX`。\n\n"
            f"**最小发送间隔由库内部固化为 {min_send}**：在该间隔内的连续变化会被合并到最后一次值。"
            f"如果值在间隔内变化又回到旧值，**不会**发新帧（PDF §4.2.5.x 明确）。"
        ),
        "behavior": SEND_PLAIN_BEHAVIOR.format(data_var=data_pin[0], min_send=min_send),
        "errors": ERROR_TABLE_SEND_COMMON,
        "notes": SEND_PLAIN_NOTES_COMMON,
        **scenario_data,
    }


def _send_ex_fb(name, infosys_id, pdf_section, data_pin, dpt_desc,
                cycle_default, min_default, scenario_data,
                extra_in_block_after=None, extra_in_vars=None):
    """Generate an _EX send FB entry."""
    var_input = "VAR_INPUT\n"
    var_input += "    bStart         : BOOL;\n"
    var_input += "    iMode          : INT;\n"
    var_input += f"    CyclePolling   : TIME := {cycle_default};\n"
    var_input += f"    MinSendTime    : TIME := {min_default};\n"
    var_input += "    Group_Address  : EIB_GROUP_ADDR;\n"
    var_input += f"    {data_pin[0]:<14} : {data_pin[1]};\n"
    if extra_in_block_after:
        var_input += extra_in_block_after
    var_input += "    str_Rec        : EIB_REC;\n"
    var_input += "    bEnableReadReq : BOOL;\n"
    var_input += "END_VAR"

    in_vars = [
        ("bStart", "BOOL", None,
         "FB 触发输入。`iMode = 0` 时上升沿触发；`iMode = 1/2/3` 时电平 = 使能"),
        ("iMode", "INT", None,
         "0 = Manual / 1 = Polling / 2 = OnChange / 3 = OnChangePolling，见 §3"),
        ("CyclePolling", "TIME", cycle_default,
         "Polling 模式下的发送周期。**下限 200 ms**（库强制）"),
        ("MinSendTime", "TIME", min_default,
         "OnChange 模式下的最短发送间隔。**下限 200 ms**（库强制）"),
        ("Group_Address", "EIB_GROUP_ADDR", None,
         "**目标 EIB 组地址**（必须在 KL6301 过滤器内）"),
        (data_pin[0], data_pin[1], None, data_pin[2]),
    ]
    if extra_in_vars:
        in_vars.extend(extra_in_vars)
    in_vars.extend([
        ("str_Rec", "EIB_REC", None,
         "收发胶水结构，必须传 `KL6301.str_Data_Rec` 同一个实例"),
        ("bEnableReadReq", "BOOL", None,
         "使能响应 EIB Read_Group_Req（其它设备主动查值时本 FB 自动答）"),
    ])
    var_output = (
        "VAR_OUTPUT\n"
        "    bBusy    : BOOL;\n"
        "    bError   : BOOL;\n"
        "    iErrorID : EIB_ERROR_CODE;\n"
        "END_VAR"
    )
    out_vars = [
        ("bBusy", "BOOL", "FB 正在发送 / 等待重试，新触发被忽略直到回 FALSE"),
        ("bError", "BOOL", "发送出错时置 TRUE；错误码在 `iErrorID`"),
        ("iErrorID", "EIB_ERROR_CODE", "错误码，详见 `EIB_ERROR_CODE`"),
    ]
    return {
        "name": name,
        "category": "send",
        "category_label": "Send",
        "infosys_id": infosys_id,
        "pdf_section": pdf_section,
        "type": "FUNCTION_BLOCK",
        "var_input_block": var_input,
        "in_vars": in_vars,
        "var_output_block": var_output,
        "out_vars": out_vars,
        "var_inout_block": None,
        "inout_vars": None,
        "brief": (
            f"**`{name[:-3]}` 的扩展版本**：发送 {dpt_desc} telegram，支持 Manual / Polling / OnChange / OnChangePolling 4 种模式。\n\n"
            f"与非 _EX 版本相比，本 FB **支持周期定时重发**（Polling）和 **响应 EIB Read 请求**（`bEnableReadReq`）。"
            f"实际工程里大多用 _EX 版本，因为业务上经常需要周期心跳或主动答查。"
        ),
        "behavior": SEND_EX_BEHAVIOR,
        "errors": ERROR_TABLE_SEND_COMMON,
        "notes": SEND_EX_NOTES_COMMON,
        **scenario_data,
    }


# ============================================================================
# Common scenario helpers
# ============================================================================

def _scenario_plain(name, data_type, data_role, group_addr_str, addr_tup,
                    sample_value, sample_check):
    return {
        "tcpou_scene": (
            f"PLC 把当前 {data_role} 经 EIB 组地址 {group_addr_str} 推送到楼宇控制系统。"
            f"楼宇里的显示屏、记录器、其它 PLC 等通过该地址订阅本值。"
        ),
        "tcpou_value": (
            f"替代手写 EIB telegram 编码 + 变化检测；只关心 {data_type} 值的业务变化"
        ),
        "tcpou_verify": (
            f"登录后改 `{data_type.lower()}NewValue` → 1-2 秒后 EIB 总线上应能用 group monitor 看到组 {group_addr_str} 出新帧；"
            f"如果 KL6301 过滤器没配此地址，{sample_check}。"
        ),
        "tcpou_decl": (
            f"VAR\n"
            f"    fb{name}      : {name};\n"
            f"    stEibRec      : EIB_REC;\n"
            f"    stGroupTarget : EIB_GROUP_ADDR := (MAIN := {addr_tup[0]}, SUB_MAIN := {addr_tup[1]}, NUMBER := {addr_tup[2]});\n"
            f"    {data_type.lower()}NewValue : {data_type} := {sample_value};\n"
            f"    bErrFlag      : BOOL;\n"
            f"    iLastErrID    : EIB_ERROR_CODE;\n"
            f"END_VAR"
        ),
        "tcpou_st": (
            f"// 每周期调用：只在 {data_type.lower()}NewValue 变化时才下发 telegram\n"
            f"fb{name}(\n"
            f"    Group_Address := stGroupTarget,\n"
            f"    {data_pin_field(name)} := {data_type.lower()}NewValue,\n"
            f"    str_Rec       := stEibRec,\n"
            f"    bError        => bErrFlag,\n"
            f"    iErrorID      => iLastErrID\n"
            f");"
        ),
        "scene": f"{data_role}发送到 KNX/EIB BMS",
        "value": "替代手写编码 + 自动变化检测；KNX 行业标准发送方式",
        "alternatives": [
            "`EIB_ALL_DATA_TYPES_SEND`：能做但要自己拼字节",
            f"`{name}_EX`：能周期发 + 响应 Read 请求",
            "本 FB：简单变化发送的标准选择",
        ],
        "related": f"`{name}_EX`（同库下一节，扩展版）、`KL6301`、`EIB_REC`",
        "example_preview": (
            f"PROGRAM P_Demo_{name}\n"
            f"VAR\n"
            f"    fb       : {name};\n"
            f"    stEibRec : EIB_REC;\n"
            f"    stGroup  : EIB_GROUP_ADDR := (MAIN := {addr_tup[0]}, SUB_MAIN := {addr_tup[1]}, NUMBER := {addr_tup[2]});\n"
            f"    v        : {data_type} := {sample_value};\n"
            f"END_VAR\n"
            f"fb(Group_Address := stGroup, {data_pin_field(name)} := v, str_Rec := stEibRec);"
        ),
    }


def data_pin_field(name):
    """Map FB name to its data pin name (matches PDF declarations)."""
    if "_FLOAT_" in name:
        return "rData"
    if "_8BIT_SIGN" in name:
        return "iData"  # PDF: iData
    if "_8BIT_UNSIGN" in name:
        return "byData"
    if "_2OCTET_SIGN" in name:
        return "iData"
    if "_2OCTET_UNSIGN" in name:
        return "uiData"
    if "_4OCTET_SIGN" in name:
        return "uiData"  # PDF typo — uiData with DINT
    if "_4OCTET_UNSIGN" in name:
        return "uiData"
    if "EIB_3BIT_CONTROL" in name:
        return "bControl"  # plus byRange
    if "EIB_BIT_CONTROL" in name:
        return "bControl"  # plus bValue
    if "_DATE_" in name:
        return "wDay"  # plus wMonth/wYear
    if "_TIME_" in name:
        return "wHoure"
    if "_BIT_" in name:
        return "bData"
    if "_READ_" in name:
        return "bRead"
    return "?"


# ============================================================================
# ENTRIES - SEND PLAIN VERSIONS
# ============================================================================

# Each pair (plain + _EX) needs slightly different scenarios.

# EIB_2OCTET_FLOAT_SEND
ENTRIES.append(_send_plain_fb(
    "EIB_2OCTET_FLOAT_SEND", "187754251", "4.2.5.1",
    ("rData", "REAL",
     "数据值（IEC `REAL`），库自动转成 EIB 2 byte float 编码（DPT 9.xxx 半精度浮点）"),
    "DPT 9.xxx (2-byte float, 半精度)",
    "1 秒",
    {
        "tcpou_scene": (
            "PLC 测得的当前室内温度（REAL）经组地址 1/2/10 推送到 BMS。"
            "BMS 监控页面订阅 1/2/10 显示房间温度。"
        ),
        "tcpou_value": (
            "替代手写 EIB 半精度浮点编码；变化时自动发，节省 EIB 带宽"
        ),
        "tcpou_verify": (
            "登录后改 `rRoomTempC := 23.5` → 1 秒内 BMS 应看到 1/2/10 新帧；"
            "再快速改成 24.0、24.5（< 1 秒内）→ 仅最后一次发出。"
        ),
        "tcpou_decl": (
            "VAR\n"
            "    fbSendTemp    : EIB_2OCTET_FLOAT_SEND;\n"
            "    stEibRec      : EIB_REC;\n"
            "    stGroupTemp   : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 10);\n"
            "    rRoomTempC    : REAL := 22.5;\n"
            "    bSendError    : BOOL;\n"
            "    iLastErrID    : EIB_ERROR_CODE;\n"
            "END_VAR"
        ),
        "tcpou_st": (
            "// 只在 rRoomTempC 变化时下发；用最小 1 秒间隔合并连续变化\n"
            "fbSendTemp(\n"
            "    Group_Address := stGroupTemp,\n"
            "    rData         := rRoomTempC,\n"
            "    str_Rec       := stEibRec,\n"
            "    bError        => bSendError,\n"
            "    iErrorID      => iLastErrID\n"
            ");"
        ),
        "scene": "PLC 测量值（温度 / 湿度 / 风速）发送到 BMS",
        "value": "自动编码半精度浮点 + 变化触发；DPT 9.xxx 标准发送",
        "alternatives": [
            "`EIB_2OCTET_FLOAT_SEND_EX`：周期重发 + read 请求响应",
            "`EIB_4OCTET_FLOAT_SEND`：高精度场景",
            "本 FB：DPT 9.xxx 标准选择",
        ],
        "related": "`EIB_2OCTET_FLOAT_SEND_EX`（同库 §4.2.5.2）、`EIB_2OCTET_FLOAT_REC`（接收端）",
        "example_preview": (
            "PROGRAM P_Demo_EIB_2OCTET_FLOAT_SEND\n"
            "VAR\n"
            "    fb       : EIB_2OCTET_FLOAT_SEND;\n"
            "    stEibRec : EIB_REC;\n"
            "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 10);\n"
            "    r        : REAL := 22.5;\n"
            "END_VAR\n"
            "fb(Group_Address := stGroup, rData := r, str_Rec := stEibRec);"
        ),
    },
))

# EIB_2OCTET_FLOAT_SEND_EX
ENTRIES.append(_send_ex_fb(
    "EIB_2OCTET_FLOAT_SEND_EX", "187755787", "4.2.5.2",
    ("rData", "REAL",
     "数据值（IEC `REAL`），库自动转成 EIB 2 byte float（DPT 9.xxx 半精度）"),
    "DPT 9.xxx (2-byte float, 半精度)",
    "t#500ms", "t#1s",
    {
        "tcpou_scene": (
            "PLC 实测温度发送到组地址 1/2/10，周期 5 秒重发（心跳）；同时数据变化时立即推送；"
            "并响应 BMS 监控页面发起的 Read_Group_Req。"
        ),
        "tcpou_value": "周期心跳 + 即时变化 + 主动答查；BMS 数据可靠性大幅提升",
        "tcpou_verify": (
            "登录后 `bSendStart := TRUE` + `iWorkMode := 3` (OnChangePolling) → "
            "BMS 应每 5 秒看到一次 1/2/10 新帧；任意改 `rRoomTempC` 也立即出帧；"
            "BMS Read_Group_Req 1/2/10 应得到当前值。"
        ),
        "tcpou_decl": (
            "VAR\n"
            "    fbSendTempEx       : EIB_2OCTET_FLOAT_SEND_EX;\n"
            "    stEibRec           : EIB_REC;\n"
            "    stGroupTemp        : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 10);\n"
            "    bSendStart         : BOOL;\n"
            "    iWorkMode          : INT := 3;             // OnChangePolling\n"
            "    tCyclePeriod       : TIME := T#5S;\n"
            "    tMinIntervalChange : TIME := T#500MS;\n"
            "    rRoomTempC         : REAL := 22.5;\n"
            "    bResponseToRead    : BOOL := TRUE;\n"
            "    bSendBusy          : BOOL;\n"
            "    bSendError         : BOOL;\n"
            "    iLastErrID         : EIB_ERROR_CODE;\n"
            "END_VAR"
        ),
        "tcpou_st": (
            "// iMode = 3：周期 5 秒 + 变化时立即发，间隔最小 500 ms 防抖\n"
            "fbSendTempEx(\n"
            "    bStart         := bSendStart,\n"
            "    iMode          := iWorkMode,\n"
            "    CyclePolling   := tCyclePeriod,\n"
            "    MinSendTime    := tMinIntervalChange,\n"
            "    Group_Address  := stGroupTemp,\n"
            "    rData          := rRoomTempC,\n"
            "    str_Rec        := stEibRec,\n"
            "    bEnableReadReq := bResponseToRead,\n"
            "    bBusy          => bSendBusy,\n"
            "    bError         => bSendError,\n"
            "    iErrorID       => iLastErrID\n"
            ");"
        ),
        "scene": "PLC 测量值定时心跳 + 即时变化 + 响应主动查询",
        "value": "比普通 FB 强大得多；BMS 实际项目首选",
        "alternatives": [
            "非 _EX 版本：只能变化时发，不能周期",
            "本 _EX：BMS 工程**首选**",
        ],
        "related": "`EIB_2OCTET_FLOAT_SEND`（同库 §4.2.5.1，简化版）、`EIB_2OCTET_FLOAT_REC`",
        "example_preview": (
            "PROGRAM P_Demo_EIB_2OCTET_FLOAT_SEND_EX\n"
            "VAR\n"
            "    fb       : EIB_2OCTET_FLOAT_SEND_EX;\n"
            "    stEibRec : EIB_REC;\n"
            "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 10);\n"
            "    r        : REAL := 22.5;\n"
            "END_VAR\n"
            "fb(bStart := TRUE, iMode := 3, CyclePolling := T#5S, MinSendTime := T#500MS,\n"
            "   Group_Address := stGroup, rData := r, str_Rec := stEibRec,\n"
            "   bEnableReadReq := TRUE);"
        ),
    },
))


# Now build a helper to generate similar pairs concisely
def _quick_send_pair(plain_name, plain_id, plain_sec,
                     ex_name, ex_id, ex_sec,
                     data_pin, dpt_desc, min_send,
                     cycle_default, min_default, role, addr_tup,
                     sample_init, send_dpt_short):
    """Generate plain + EX pair with minimal-but-complete scenario stubs."""
    type_short = data_pin[1]
    pin_name = data_pin[0]
    addr_str = f"{addr_tup[0]}/{addr_tup[1]}/{addr_tup[2]}"

    # Plain
    plain_scenario = {
        "tcpou_scene": (
            f"PLC 测得的 {role} 经 EIB 组地址 {addr_str} 推送到 BMS。"
        ),
        "tcpou_value": f"替代手写 {send_dpt_short} 编码；变化触发自动",
        "tcpou_verify": (
            f"改 `data` → 1 秒内 EIB 总线上 {addr_str} 出新帧。"
        ),
        "tcpou_decl": (
            f"VAR\n"
            f"    fb{plain_name}     : {plain_name};\n"
            f"    stEibRec           : EIB_REC;\n"
            f"    stGroup            : EIB_GROUP_ADDR := (MAIN := {addr_tup[0]}, SUB_MAIN := {addr_tup[1]}, NUMBER := {addr_tup[2]});\n"
            f"    data               : {type_short} := {sample_init};\n"
            f"    bSendError         : BOOL;\n"
            f"    iLastErrID         : EIB_ERROR_CODE;\n"
            f"END_VAR"
        ),
        "tcpou_st": (
            f"// 每周期调用：只在 data 变化时下发 telegram\n"
            f"fb{plain_name}(\n"
            f"    Group_Address := stGroup,\n"
            f"    {pin_name:<13} := data,\n"
            f"    str_Rec       := stEibRec,\n"
            f"    bError        => bSendError,\n"
            f"    iErrorID      => iLastErrID\n"
            f");"
        ),
        "scene": f"PLC {role}发送到 BMS",
        "value": f"DPT {send_dpt_short} 标准发送方式",
        "alternatives": [
            f"`{ex_name}`：周期发 + read 响应",
            "`EIB_ALL_DATA_TYPES_SEND`：raw byte 模式",
            "本 FB：简单变化发送的标准选择",
        ],
        "related": f"`{ex_name}`（同库 §{ex_sec}）、对应接收 FB",
        "example_preview": (
            f"PROGRAM P_Demo_{plain_name}\n"
            f"VAR\n"
            f"    fb       : {plain_name};\n"
            f"    stEibRec : EIB_REC;\n"
            f"    stGroup  : EIB_GROUP_ADDR := (MAIN := {addr_tup[0]}, SUB_MAIN := {addr_tup[1]}, NUMBER := {addr_tup[2]});\n"
            f"    data     : {type_short} := {sample_init};\n"
            f"END_VAR\n"
            f"fb(Group_Address := stGroup, {pin_name} := data, str_Rec := stEibRec);"
        ),
    }
    ENTRIES.append(_send_plain_fb(
        plain_name, plain_id, plain_sec, data_pin, dpt_desc, min_send,
        plain_scenario,
    ))

    # EX
    ex_scenario = {
        "tcpou_scene": (
            f"PLC {role}发送到 EIB 组 {addr_str}，模式 OnChangePolling：心跳 + 即时变化 + 响应 read。"
        ),
        "tcpou_value": "周期心跳 + 即时变化 + 主动答查；BMS 工程首选",
        "tcpou_verify": (
            f"登录 `bSendStart := TRUE` → 周期 5 秒看到 {addr_str} 出帧；改 data 立即出帧。"
        ),
        "tcpou_decl": (
            f"VAR\n"
            f"    fb{ex_name}         : {ex_name};\n"
            f"    stEibRec            : EIB_REC;\n"
            f"    stGroup             : EIB_GROUP_ADDR := (MAIN := {addr_tup[0]}, SUB_MAIN := {addr_tup[1]}, NUMBER := {addr_tup[2]});\n"
            f"    bSendStart          : BOOL;\n"
            f"    iWorkMode           : INT := 3;\n"
            f"    tCyclePeriod        : TIME := T#5S;\n"
            f"    tMinIntervalChange  : TIME := T#500MS;\n"
            f"    data                : {type_short} := {sample_init};\n"
            f"    bResponseToRead     : BOOL := TRUE;\n"
            f"    bSendBusy           : BOOL;\n"
            f"    bSendError          : BOOL;\n"
            f"    iLastErrID          : EIB_ERROR_CODE;\n"
            f"END_VAR"
        ),
        "tcpou_st": (
            f"fb{ex_name}(\n"
            f"    bStart         := bSendStart,\n"
            f"    iMode          := iWorkMode,\n"
            f"    CyclePolling   := tCyclePeriod,\n"
            f"    MinSendTime    := tMinIntervalChange,\n"
            f"    Group_Address  := stGroup,\n"
            f"    {pin_name:<14} := data,\n"
            f"    str_Rec        := stEibRec,\n"
            f"    bEnableReadReq := bResponseToRead,\n"
            f"    bBusy          => bSendBusy,\n"
            f"    bError         => bSendError,\n"
            f"    iErrorID       => iLastErrID\n"
            f");"
        ),
        "scene": f"PLC {role}定时心跳 + 即时变化 + 响应主动查询",
        "value": "BMS 工程的实际首选方式",
        "alternatives": [
            f"`{plain_name}`：只变化发，无周期",
            "本 _EX：BMS 工程**首选**",
        ],
        "related": f"`{plain_name}`（同库 §{plain_sec}，简化版）、对应接收 FB",
        "example_preview": (
            f"PROGRAM P_Demo_{ex_name}\n"
            f"VAR\n"
            f"    fb       : {ex_name};\n"
            f"    stEibRec : EIB_REC;\n"
            f"    stGroup  : EIB_GROUP_ADDR := (MAIN := {addr_tup[0]}, SUB_MAIN := {addr_tup[1]}, NUMBER := {addr_tup[2]});\n"
            f"    data     : {type_short} := {sample_init};\n"
            f"END_VAR\n"
            f"fb(bStart := TRUE, iMode := 3, CyclePolling := T#5S, MinSendTime := T#500MS,\n"
            f"   Group_Address := stGroup, {pin_name} := data, str_Rec := stEibRec,\n"
            f"   bEnableReadReq := TRUE);"
        ),
    }
    ENTRIES.append(_send_ex_fb(
        ex_name, ex_id, ex_sec, data_pin, dpt_desc, cycle_default, min_default,
        ex_scenario,
    ))


# 2OCTET_SIGN pair
_quick_send_pair(
    "EIB_2OCTET_SIGN_SEND", "187757323", "4.2.5.3",
    "EIB_2OCTET_SIGN_SEND_EX", "6790408587", "4.2.5.4",
    ("iData", "INT", "数据值（IEC `INT`），库自动转成 EIB 2 byte signed 编码（DPT 8.xxx）"),
    "DPT 8.xxx (2-byte signed int)", "1 秒",
    "t#500ms", "t#1s",
    "温度偏置（±32768 范围）", (1, 4, 11),
    "INT#0", "DPT 8.xxx",
)

# 2OCTET_UNSIGN pair
_quick_send_pair(
    "EIB_2OCTET_UNSIGN_SEND", "187758859", "4.2.5.5",
    "EIB_2OCTET_UNSIGN_SEND_EX", "14472014219", "4.2.5.6",
    ("uiData", "UINT", "数据值（IEC `UINT`），库自动转成 EIB 2 byte unsigned 编码（DPT 7.xxx）"),
    "DPT 7.xxx (2-byte unsigned int)", "1 秒",
    "t#500ms", "t#1s",
    "亮度值（0..65535）", (1, 4, 12),
    "UINT#0", "DPT 7.xxx",
)

# 3BIT_CONTROL pair (special: BOOL + BYTE)
# Plain
ENTRIES.append({
    "name": "EIB_3BIT_CONTROL_SEND",
    "category": "send",
    "category_label": "Send",
    "infosys_id": "187760395",
    "pdf_section": "4.2.5.7",
    "type": "FUNCTION_BLOCK",
    "var_input_block": (
        "VAR_INPUT\n"
        "    Group_Address : EIB_GROUP_ADDR;\n"
        "    bControl      : BOOL;\n"
        "    byRange       : BYTE;\n"
        "    str_Rec       : EIB_REC;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("Group_Address", "EIB_GROUP_ADDR", None, "目标组地址（必须在 KL6301 过滤器内）"),
        ("bControl", "BOOL", None, "DPT 3.xxx 控制位（TRUE = 向上 / 增 / 开方向；FALSE = 向下 / 减 / 关方向）"),
        ("byRange", "BYTE", None, "DPT 3.xxx 范围 / 步幅（0..7；0 = 停止，1..7 = 步长）"),
        ("str_Rec", "EIB_REC", None, "胶水结构，传 `KL6301.str_Data_Rec`"),
    ],
    "var_output_block": (
        "VAR_OUTPUT\n"
        "    bError   : BOOL;\n"
        "    iErrorID : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "out_vars": [
        ("bError", "BOOL", "发送出错时置 TRUE"),
        ("iErrorID", "EIB_ERROR_CODE", "错误码"),
    ],
    "var_inout_block": None, "inout_vars": None,
    "brief": (
        "**发送 4-bit Controlled telegram**（DPT 3.xxx：调光控制 / 卷帘步进）：1 bit 控制 + 3 bit 范围。"
        "`bControl` 或 `byRange` **任一变化**就发；最小间隔 200 ms。\n\n"
        "典型用于「按住按钮调光」「按住按钮收/放卷帘」——按下时持续发 (TRUE, n)，松开发 (X, 0)。"
    ),
    "behavior": (
        "**触发方式**：只要 `bControl` 或 `byRange` 任一值发生变化，就立即编码并发送一帧 EIB telegram。"
        "PDF §4.2.5.7 明确指出，只在两个数据位中至少一个发生变化时才会下发——"
        "**值未变就不发**，不论 FB 被调用多少次。\n\n"
        "**最小发送间隔 200 ms**（PDF 明确）：200 ms 内的连续变化会被合并到最后一次值；"
        "如果值在间隔内变化又回到旧值，则**不会**发送新帧（与 PDF "
        "\"No new EIB telegram is sent if the value changes within the min. send time but falls back to the old, already sent value\" 描述一致）。\n\n"
        "**业务用法**：调光按钮按下时业务代码持续刷 (`bControl = TRUE`, `byRange = n`)，松开时刷 (`bControl = TRUE`, `byRange = 0`)。"
        "因为最小 200 ms 间隔，「按住按钮快速变化方向」会被库自动合并，符合调光器物理响应能力。\n\n"
        "**与 KL6301 依赖**：必须 `KL6301.bReady = TRUE`；同 PLC 任务；`str_Rec` 传 `KL6301.str_Data_Rec` 同一实例；"
        "`Group_Address` 必须在过滤器内。"
    ),
    "errors": ERROR_TABLE_SEND_COMMON,
    "notes": SEND_PLAIN_NOTES_COMMON + [
        "**`byRange = 0` 是停止语义**：DPT 3.007 规范。",
        "**两个 IEC 入口任一变化就发**：业务上要「按住保持」语义就要持续刷 (TRUE, n) 而不是只触发一次。",
    ],
    "tcpou_scene": (
        "调光面板按钮：用户按住按钮调光向上 → PLC 持续推 (TRUE, 4) 到组地址 1/2/15；松开后推 (TRUE, 0) 停止。"
    ),
    "tcpou_value": "替代手写 4-bit 拼装 + 变化检测；DPT 3.xxx 标准发送方式",
    "tcpou_verify": (
        "按下「调光向上」按钮 → 组 1/2/15 在 BMS 监控里出现 (1, 100b) 即 0x0C；松开 → 出现 (1, 000b) 即 0x08。"
    ),
    "tcpou_decl": (
        "VAR\n"
        "    fbSendDim    : EIB_3BIT_CONTROL_SEND;\n"
        "    stEibRec     : EIB_REC;\n"
        "    stGroup      : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 15);\n"
        "    bDirUp       : BOOL := TRUE;\n"
        "    byCurrentStep: BYTE;            // 0..7\n"
        "    bSendError   : BOOL;\n"
        "    iLastErrID   : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "// 业务层只要把 byCurrentStep 改成 0..7，FB 自动发\n"
        "fbSendDim(\n"
        "    Group_Address := stGroup,\n"
        "    bControl      := bDirUp,\n"
        "    byRange       := byCurrentStep,\n"
        "    str_Rec       := stEibRec,\n"
        "    bError        => bSendError,\n"
        "    iErrorID      => iLastErrID\n"
        ");"
    ),
    "scene": "调光控制、卷帘步进等 4-bit 控制场景",
    "value": "DPT 3.xxx 标准发送",
    "alternatives": [
        "`EIB_3BIT_CONTROL_SEND_EX`：周期 / OnChange / 主动答查",
        "`EIB_ALL_DATA_TYPES_SEND`：手动拼字节",
        "本 FB：简单变化发送的标准选择",
    ],
    "related": "`EIB_3BIT_CONTROL_SEND_EX`（§4.2.5.8）、`EIB_3BIT_CONTROL_REC`（接收端）",
    "example_preview": (
        "PROGRAM P_Demo_EIB_3BIT_CONTROL_SEND\n"
        "VAR\n"
        "    fb       : EIB_3BIT_CONTROL_SEND;\n"
        "    stEibRec : EIB_REC;\n"
        "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 15);\n"
        "    bDir     : BOOL := TRUE;\n"
        "    byR      : BYTE := 4;\n"
        "END_VAR\n"
        "fb(Group_Address := stGroup, bControl := bDir, byRange := byR, str_Rec := stEibRec);"
    ),
})


# 3BIT_CONTROL EX
ENTRIES.append({
    "name": "EIB_3BIT_CONTROL_SEND_EX",
    "category": "send",
    "category_label": "Send",
    "infosys_id": "15012536971",
    "pdf_section": "4.2.5.8",
    "type": "FUNCTION_BLOCK",
    "var_input_block": (
        "VAR_INPUT\n"
        "    bStart         : BOOL;\n"
        "    iMode          : INT;\n"
        "    CyclePolling   : TIME := t#500ms;\n"
        "    MinSendTime    : TIME := t#1s;\n"
        "    Group_Address  : EIB_GROUP_ADDR;\n"
        "    bControl       : BOOL;\n"
        "    byRange        : BYTE;\n"
        "    str_Rec        : EIB_REC;\n"
        "    bEnableReadReq : BOOL;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("bStart", "BOOL", None, "FB 触发输入；模式 0 用上升沿，模式 1/2/3 用电平"),
        ("iMode", "INT", None, "0/1/2/3 = Manual/Polling/OnChange/OnChangePolling，见 §3"),
        ("CyclePolling", "TIME", "t#500ms", "Polling 周期，下限 200 ms"),
        ("MinSendTime", "TIME", "t#1s", "OnChange 最短间隔，下限 200 ms"),
        ("Group_Address", "EIB_GROUP_ADDR", None, "目标组地址"),
        ("bControl", "BOOL", None, "1 bit 控制位"),
        ("byRange", "BYTE", None, "3 bit 范围（0..7）"),
        ("str_Rec", "EIB_REC", None, "胶水结构，传 `KL6301.str_Data_Rec`"),
        ("bEnableReadReq", "BOOL", None, "使能响应 read_group_req"),
    ],
    "var_output_block": (
        "VAR_OUTPUT\n"
        "    bBusy    : BOOL;\n"
        "    bError   : BOOL;\n"
        "    iErrorID : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "out_vars": [
        ("bBusy", "BOOL", "发送 / 等待中"),
        ("bError", "BOOL", "出错"),
        ("iErrorID", "EIB_ERROR_CODE", "错误码"),
    ],
    "var_inout_block": None, "inout_vars": None,
    "brief": (
        "`EIB_3BIT_CONTROL_SEND` 的扩展版本：发送 DPT 3.xxx 4-bit Controlled telegram，"
        "支持 Manual / Polling / OnChange / OnChangePolling 4 种模式。"
        "适合场景灯的状态心跳（避免 BMS 失同步）+ 响应 BMS 主动查值。"
    ),
    "behavior": SEND_EX_BEHAVIOR,
    "errors": ERROR_TABLE_SEND_COMMON,
    "notes": SEND_EX_NOTES_COMMON,
    "tcpou_scene": (
        "场景灯控制：调光命令按 OnChangePolling 模式发，确保 BMS 总能拿到最新状态；周期 10 秒心跳。"
    ),
    "tcpou_value": "周期心跳 + 即时变化 + 主动答查；调光复杂场景首选",
    "tcpou_verify": (
        "登录 `bSendStart := TRUE`、`iWorkMode := 3` → 每 10 秒看到组 1/2/15 出帧；改 byStep 立即出帧。"
    ),
    "tcpou_decl": (
        "VAR\n"
        "    fbSendDimEx        : EIB_3BIT_CONTROL_SEND_EX;\n"
        "    stEibRec           : EIB_REC;\n"
        "    stGroup            : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 15);\n"
        "    bSendStart         : BOOL;\n"
        "    iWorkMode          : INT := 3;\n"
        "    tCyclePeriod       : TIME := T#10S;\n"
        "    tMinChangeInterval : TIME := T#500MS;\n"
        "    bDirUp             : BOOL := TRUE;\n"
        "    byStep             : BYTE := 4;\n"
        "    bResponseRead      : BOOL := TRUE;\n"
        "    bSendBusy          : BOOL;\n"
        "    bSendError         : BOOL;\n"
        "    iLastErrID         : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "fbSendDimEx(\n"
        "    bStart         := bSendStart,\n"
        "    iMode          := iWorkMode,\n"
        "    CyclePolling   := tCyclePeriod,\n"
        "    MinSendTime    := tMinChangeInterval,\n"
        "    Group_Address  := stGroup,\n"
        "    bControl       := bDirUp,\n"
        "    byRange        := byStep,\n"
        "    str_Rec        := stEibRec,\n"
        "    bEnableReadReq := bResponseRead,\n"
        "    bBusy          => bSendBusy,\n"
        "    bError         => bSendError,\n"
        "    iErrorID       => iLastErrID\n"
        ");"
    ),
    "scene": "BMS 调光场景灯，心跳 + 即时变化 + 答查",
    "value": "BMS 调光工程首选",
    "alternatives": [
        "非 _EX：只变化发",
        "本 _EX：复杂场景首选",
    ],
    "related": "`EIB_3BIT_CONTROL_SEND`（§4.2.5.7）、`EIB_3BIT_CONTROL_REC`",
    "example_preview": (
        "PROGRAM P_Demo_EIB_3BIT_CONTROL_SEND_EX\n"
        "VAR\n"
        "    fb       : EIB_3BIT_CONTROL_SEND_EX;\n"
        "    stEibRec : EIB_REC;\n"
        "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 15);\n"
        "END_VAR\n"
        "fb(bStart := TRUE, iMode := 3, CyclePolling := T#10S, MinSendTime := T#500MS,\n"
        "   Group_Address := stGroup, bControl := TRUE, byRange := 4,\n"
        "   str_Rec := stEibRec, bEnableReadReq := TRUE);"
    ),
})


# 4OCTET_FLOAT pair
_quick_send_pair(
    "EIB_4OCTET_FLOAT_SEND", "187761931", "4.2.5.9",
    "EIB_4OCTET_FLOAT_SEND_EX", "187763467", "4.2.5.10",
    ("rData", "REAL", "IEC `REAL`（IEEE 754 single），库直接编码为 EIB 4-byte float（DPT 14.xxx）"),
    "DPT 14.xxx (4-byte IEEE 754 float)", "1 秒",
    "t#10m", "t#1s",   # _EX 默认 CyclePolling = 10 min
    "瞬时功率 (W)", (1, 4, 13),
    "REAL#0.0", "DPT 14.xxx",
)

# 4OCTET_SIGN pair
# PDF mistake: plain version VAR_INPUT uses `iData : DINT`; the table label
# "uiData" is wrong. _EX version VAR_INPUT uses `uiData : DINT` (PDF typo carried).
# Build each separately to match each PDF VAR_INPUT verbatim.
ENTRIES.append(_send_plain_fb(
    "EIB_4OCTET_SIGN_SEND", "187765003", "4.2.5.11",
    ("iData", "DINT",
     "数据值（IEC `DINT`），库编码为 EIB 4 byte signed（DPT 13.xxx）。"
     "**PDF VAR_INPUT 引脚为 `iData`**（PDF 描述表把它列成 `uiData` 是表头排版错；以代码块为准）"),
    "DPT 13.xxx (4-byte signed int)", "1 秒",
    {
        "tcpou_scene": "PLC 累计电能（DINT）发送到组 1/4/14。",
        "tcpou_value": "替代手写 DPT 13 编码；变化触发自动",
        "tcpou_verify": "改 `data` → 1 秒内 1/4/14 出新帧。",
        "tcpou_decl": (
            "VAR\n"
            "    fbSendEnergy : EIB_4OCTET_SIGN_SEND;\n"
            "    stEibRec     : EIB_REC;\n"
            "    stGroup      : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 4, NUMBER := 14);\n"
            "    data         : DINT := 0;\n"
            "    bSendError   : BOOL;\n"
            "    iLastErrID   : EIB_ERROR_CODE;\n"
            "END_VAR"
        ),
        "tcpou_st": (
            "fbSendEnergy(\n"
            "    Group_Address := stGroup,\n"
            "    iData         := data,\n"
            "    str_Rec       := stEibRec,\n"
            "    bError        => bSendError,\n"
            "    iErrorID      => iLastErrID\n"
            ");"
        ),
        "scene": "累计电能 / 32 位有符号大整数发送",
        "value": "DPT 13 标准发送方式",
        "alternatives": [
            "`EIB_4OCTET_SIGN_SEND_EX`：周期 + read 响应",
            "`EIB_ALL_DATA_TYPES_SEND`：raw byte",
            "本 FB：DPT 13 简单变化发送",
        ],
        "related": "`EIB_4OCTET_SIGN_SEND_EX`（同库 §4.2.5.12）、`EIB_4OCTET_SIGN_REC`",
        "example_preview": (
            "PROGRAM P_Demo_EIB_4OCTET_SIGN_SEND\n"
            "VAR\n"
            "    fb       : EIB_4OCTET_SIGN_SEND;\n"
            "    stEibRec : EIB_REC;\n"
            "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 4, NUMBER := 14);\n"
            "    data     : DINT := 0;\n"
            "END_VAR\n"
            "fb(Group_Address := stGroup, iData := data, str_Rec := stEibRec);"
        ),
    },
))
# _EX with uiData per PDF VAR_INPUT
ENTRIES.append(_send_ex_fb(
    "EIB_4OCTET_SIGN_SEND_EX", "187766539", "4.2.5.12",
    ("uiData", "DINT",
     "数据值（IEC `DINT`），库编码为 EIB 4 byte signed（DPT 13.xxx）。"
     "**PDF VAR_INPUT 引脚名为 `uiData`**（u 前缀本意是 unsigned，但类型是 signed `DINT`——PDF 排版错；按 PDF 逐字保留）"),
    "DPT 13.xxx (4-byte signed int)", "t#500ms", "t#1s",
    {
        "tcpou_scene": "PLC 累计电能 OnChangePolling 模式发到组 1/4/14。",
        "tcpou_value": "周期心跳 + 即时变化 + 答查",
        "tcpou_verify": "登录 `bSendStart := TRUE` → 周期 5 秒 1/4/14 出帧。",
        "tcpou_decl": (
            "VAR\n"
            "    fbSendEnergyEx     : EIB_4OCTET_SIGN_SEND_EX;\n"
            "    stEibRec           : EIB_REC;\n"
            "    stGroup            : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 4, NUMBER := 14);\n"
            "    bSendStart         : BOOL;\n"
            "    iWorkMode          : INT := 3;\n"
            "    tCyclePeriod       : TIME := T#5S;\n"
            "    tMinIntervalChange : TIME := T#500MS;\n"
            "    data               : DINT := 0;\n"
            "    bResponseToRead    : BOOL := TRUE;\n"
            "    bSendBusy          : BOOL;\n"
            "    bSendError         : BOOL;\n"
            "    iLastErrID         : EIB_ERROR_CODE;\n"
            "END_VAR"
        ),
        "tcpou_st": (
            "fbSendEnergyEx(\n"
            "    bStart         := bSendStart,\n"
            "    iMode          := iWorkMode,\n"
            "    CyclePolling   := tCyclePeriod,\n"
            "    MinSendTime    := tMinIntervalChange,\n"
            "    Group_Address  := stGroup,\n"
            "    uiData         := data,\n"
            "    str_Rec        := stEibRec,\n"
            "    bEnableReadReq := bResponseToRead,\n"
            "    bBusy          => bSendBusy,\n"
            "    bError         => bSendError,\n"
            "    iErrorID       => iLastErrID\n"
            ");"
        ),
        "scene": "累计电能定时心跳 + 即时变化",
        "value": "BMS 工程首选",
        "alternatives": [
            "`EIB_4OCTET_SIGN_SEND`：仅变化发",
            "本 _EX：BMS 工程首选",
        ],
        "related": "`EIB_4OCTET_SIGN_SEND`（§4.2.5.11）、`EIB_4OCTET_SIGN_REC`",
        "example_preview": (
            "PROGRAM P_Demo_EIB_4OCTET_SIGN_SEND_EX\n"
            "VAR\n"
            "    fb       : EIB_4OCTET_SIGN_SEND_EX;\n"
            "    stEibRec : EIB_REC;\n"
            "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 4, NUMBER := 14);\n"
            "    data     : DINT := 0;\n"
            "END_VAR\n"
            "fb(bStart := TRUE, iMode := 3, CyclePolling := T#5S, MinSendTime := T#500MS,\n"
            "   Group_Address := stGroup, uiData := data, str_Rec := stEibRec,\n"
            "   bEnableReadReq := TRUE);"
        ),
    },
))

# 4OCTET_UNSIGN pair
_quick_send_pair(
    "EIB_4OCTET_UNSIGN_SEND", "187768075", "4.2.5.13",
    "EIB_4OCTET_UNSIGN_SEND_EX", "16287831307", "4.2.5.14",
    ("uiData", "UDINT", "数据值（IEC `UDINT`），库编码为 EIB 4 byte unsigned（DPT 12.xxx）"),
    "DPT 12.xxx (4-byte unsigned int)", "1 秒",
    "t#500ms", "t#1s",
    "绝对运行秒数", (1, 4, 15),
    "UDINT#0", "DPT 12.xxx",
)

# 8BIT_SIGN pair (special: extra Scaling_Mode input)
# Plain
ENTRIES.append({
    "name": "EIB_8BIT_SIGN_SEND",
    "category": "send",
    "category_label": "Send",
    "infosys_id": "187769611",
    "pdf_section": "4.2.5.15",
    "type": "FUNCTION_BLOCK",
    "var_input_block": (
        "VAR_INPUT\n"
        "    Group_Address  : EIB_GROUP_ADDR;\n"
        "    iData          : INT;\n"
        "    Scaling_Mode   : INT;\n"
        "    str_Rec        : EIB_REC;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("Group_Address", "EIB_GROUP_ADDR", None, "目标组地址"),
        ("iData", "INT", None, "数据值。**取值范围依 `Scaling_Mode`**"),
        ("Scaling_Mode", "INT", None,
         "0 = `iData` 是 0..100 [%]，库按 raw = iData * 255 / 100 编码；1 = 0..360 [°]，raw = iData * 255 / 360；2 = 0..255，原始 byte 直接传"),
        ("str_Rec", "EIB_REC", None, "胶水结构"),
    ],
    "var_output_block": (
        "VAR_OUTPUT\n"
        "    bError   : BOOL;\n"
        "    iErrorID : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "out_vars": [
        ("bError", "BOOL", "发送出错"),
        ("iErrorID", "EIB_ERROR_CODE", "错误码（错误的 `Scaling_Mode` 报 `ERROR_SEND_8BIT_WRONG_Scaling_Mode` = 40）"),
    ],
    "var_inout_block": None, "inout_vars": None,
    "brief": (
        "**发送 8-bit 缩放 telegram**（DPT 5.001 % / 5.003 ° / 5.005 byte）：把 IEC `INT` 按 `Scaling_Mode` 缩放后发出。"
        "`iData` 值变化时下发；最小间隔 1 秒（PDF "
        "\"data are only transferred if there is a change in the data value\" + 1 sec min send time）。"
    ),
    "behavior": SEND_PLAIN_BEHAVIOR.format(data_var="iData", min_send="1 秒"),
    "errors": ERROR_TABLE_SEND_COMMON,
    "notes": SEND_PLAIN_NOTES_COMMON + [
        "**`Scaling_Mode` 与接收端必须一致**：接收用 `EIB_8BIT_SIGN_REC` 也要填对应 mode，否则解码错误。",
        "**`Scaling_Mode` 非法 → `iErrorID = 40 (ERROR_SEND_8BIT_WRONG_Scaling_Mode)`**：合法值 0/1/2。",
    ],
    "tcpou_scene": (
        "调光器把当前亮度（百分比）经组地址 1/2/20 推送到 BMS。"
    ),
    "tcpou_value": "替代手写 byte 缩放 + 变化检测；DPT 5 标准发送",
    "tcpou_verify": (
        "改 `iBrightnessPct := 50` → 总线出 raw 128 (0x80)；改 `iBrightnessPct := 100` → 出 raw 255 (0xFF)。"
    ),
    "tcpou_decl": (
        "VAR\n"
        "    fbSendBri   : EIB_8BIT_SIGN_SEND;\n"
        "    stEibRec    : EIB_REC;\n"
        "    stGroup     : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 20);\n"
        "    iBrightnessPct : INT := 50;\n"
        "    iScaleMode  : INT := 0;       // 0 = 0..100%\n"
        "    bSendError  : BOOL;\n"
        "    iLastErrID  : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "fbSendBri(\n"
        "    Group_Address := stGroup,\n"
        "    iData         := iBrightnessPct,\n"
        "    Scaling_Mode  := iScaleMode,\n"
        "    str_Rec       := stEibRec,\n"
        "    bError        => bSendError,\n"
        "    iErrorID      => iLastErrID\n"
        ");"
    ),
    "scene": "调光百分比、角度等 DPT 5.001/003/005 场景",
    "value": "替代手写缩放 + 编码；DPT 5 标准选择",
    "alternatives": [
        "`EIB_8BIT_SIGN_SEND_EX`：周期 + read 响应",
        "`EIB_8BIT_UNSIGN_SEND`：不缩放直接 byte",
        "本 FB：DPT 5.001/003/005 标准选择",
    ],
    "related": "`EIB_8BIT_SIGN_SEND_EX`（§4.2.5.16）、`EIB_8BIT_SIGN_REC`",
    "example_preview": (
        "PROGRAM P_Demo_EIB_8BIT_SIGN_SEND\n"
        "VAR\n"
        "    fb       : EIB_8BIT_SIGN_SEND;\n"
        "    stEibRec : EIB_REC;\n"
        "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 20);\n"
        "    pct      : INT := 50;\n"
        "END_VAR\n"
        "fb(Group_Address := stGroup, iData := pct, Scaling_Mode := 0, str_Rec := stEibRec);"
    ),
})

# 8BIT_SIGN _EX
ENTRIES.append({
    "name": "EIB_8BIT_SIGN_SEND_EX",
    "category": "send",
    "category_label": "Send",
    "infosys_id": "187771147",
    "pdf_section": "4.2.5.16",
    "type": "FUNCTION_BLOCK",
    "var_input_block": (
        "VAR_INPUT\n"
        "    bStart         : BOOL;\n"
        "    iMode          : INT;\n"
        "    CyclePolling   : TIME := t#500ms;\n"
        "    iData          : INT;\n"
        "    Scaling_Mode   : INT;\n"
        "    MinSendTime    : TIME := t#1s;\n"
        "    Group_Address  : EIB_GROUP_ADDR;\n"
        "    str_Rec        : EIB_REC;\n"
        "    bEnableReadReq : BOOL;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("bStart", "BOOL", None, "FB 触发，上升沿"),
        ("iMode", "INT", None, "0/1/2/3 = Manual/Polling/OnChange/OnChangePolling"),
        ("CyclePolling", "TIME", "t#500ms", "Polling 周期，下限 200 ms"),
        ("iData", "INT", None, "数据值，范围依 `Scaling_Mode`"),
        ("Scaling_Mode", "INT", None, "0 = 0..100% / 1 = 0..360° / 2 = 0..255"),
        ("MinSendTime", "TIME", "t#1s", "OnChange 最短间隔，下限 200 ms"),
        ("Group_Address", "EIB_GROUP_ADDR", None, "目标组地址"),
        ("str_Rec", "EIB_REC", None, "胶水结构"),
        ("bEnableReadReq", "BOOL", None, "使能 read 响应"),
    ],
    "var_output_block": (
        "VAR_OUTPUT\n"
        "    bBusy    : BOOL;\n"
        "    bError   : BOOL;\n"
        "    iErrorID : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "out_vars": [
        ("bBusy", "BOOL", "发送 / 等待中"),
        ("bError", "BOOL", "出错"),
        ("iErrorID", "EIB_ERROR_CODE", "错误码"),
    ],
    "var_inout_block": None, "inout_vars": None,
    "brief": (
        "`EIB_8BIT_SIGN_SEND` 的扩展版本：支持 Manual / Polling / OnChange / OnChangePolling 4 种模式 + 响应 Read。"
        "DPT 5.001/5.003/5.005 缩放可选。"
    ),
    "behavior": SEND_EX_BEHAVIOR,
    "errors": ERROR_TABLE_SEND_COMMON,
    "notes": SEND_EX_NOTES_COMMON + [
        "**`Scaling_Mode` 与接收端必须一致**：见 `EIB_8BIT_SIGN_SEND`。",
    ],
    "tcpou_scene": (
        "调光百分比按 OnChangePolling 模式发，周期 5 秒心跳 + 即时变化。"
    ),
    "tcpou_value": "DPT 5 + 周期心跳 + 即时变化；BMS 工程首选",
    "tcpou_verify": (
        "登录 `bStart := TRUE`、`iMode := 3` → 每 5 秒看到组 1/2/20 出帧。"
    ),
    "tcpou_decl": (
        "VAR\n"
        "    fbSendBriEx   : EIB_8BIT_SIGN_SEND_EX;\n"
        "    stEibRec      : EIB_REC;\n"
        "    stGroup       : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 20);\n"
        "    bSendStart    : BOOL;\n"
        "    iWorkMode     : INT := 3;\n"
        "    tCycle        : TIME := T#5S;\n"
        "    tMinSend      : TIME := T#500MS;\n"
        "    iBriPct       : INT := 50;\n"
        "    iScaleMode    : INT := 0;\n"
        "    bResponseRead : BOOL := TRUE;\n"
        "    bSendBusy     : BOOL;\n"
        "    bSendError    : BOOL;\n"
        "    iLastErrID    : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "fbSendBriEx(\n"
        "    bStart         := bSendStart,\n"
        "    iMode          := iWorkMode,\n"
        "    CyclePolling   := tCycle,\n"
        "    iData          := iBriPct,\n"
        "    Scaling_Mode   := iScaleMode,\n"
        "    MinSendTime    := tMinSend,\n"
        "    Group_Address  := stGroup,\n"
        "    str_Rec        := stEibRec,\n"
        "    bEnableReadReq := bResponseRead,\n"
        "    bBusy          => bSendBusy,\n"
        "    bError         => bSendError,\n"
        "    iErrorID       => iLastErrID\n"
        ");"
    ),
    "scene": "调光百分比定时心跳 + 即时变化",
    "value": "BMS 工程首选",
    "alternatives": [
        "非 _EX：仅变化发",
        "本 _EX：复杂 BMS 首选",
    ],
    "related": "`EIB_8BIT_SIGN_SEND`（§4.2.5.15）、`EIB_8BIT_SIGN_REC`",
    "example_preview": (
        "PROGRAM P_Demo_EIB_8BIT_SIGN_SEND_EX\n"
        "VAR\n"
        "    fb       : EIB_8BIT_SIGN_SEND_EX;\n"
        "    stEibRec : EIB_REC;\n"
        "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 20);\n"
        "END_VAR\n"
        "fb(bStart := TRUE, iMode := 3, CyclePolling := T#5S, iData := 50,\n"
        "   Scaling_Mode := 0, MinSendTime := T#500MS,\n"
        "   Group_Address := stGroup, str_Rec := stEibRec, bEnableReadReq := TRUE);"
    ),
})


# 8BIT_UNSIGN pair (no scaling mode)
# Plain
_quick_send_pair(
    "EIB_8BIT_UNSIGN_SEND", "187772683", "4.2.5.17",
    "EIB_8BIT_UNSIGN_SEND_EX", "187774219", "4.2.5.18",
    ("byData", "BYTE", "原始 byte 数据，0x00..0xFF"),
    "DPT 5.005 / 5.010 (1-byte raw)", "1 秒",
    "t#500ms", "t#1s",
    "设备状态码（原始 byte）", (1, 2, 21),
    "BYTE#0", "DPT 5.005",
)


# EIB_ALL_DATA_TYPES_SEND (special: array + len + priority + read_command)
ENTRIES.append({
    "name": "EIB_ALL_DATA_TYPES_SEND",
    "category": "send",
    "category_label": "Send",
    "infosys_id": "187775755",
    "pdf_section": "4.2.5.19",
    "type": "FUNCTION_BLOCK",
    "var_input_block": (
        "VAR_INPUT\n"
        "    bStart        : BOOL;\n"
        "    iMode         : INT;\n"
        "    CyclePolling  : TIME := t#100ms;\n"
        "    DATA          : ARRAY [1..14] OF BYTE;\n"
        "    EIB_Data_Len  : USINT := 1;\n"
        "    PRIORITY      : EIB_PRIORITY := EIB_PRIORITY_LOW;\n"
        "    MinSendTime   : TIME := t#1s;\n"
        "    Group_Address : EIB_GROUP_ADDR;\n"
        "    str_Rec       : EIB_REC;\n"
        "    bReadCommand  : BOOL;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("bStart", "BOOL", None, "Manual 模式上升沿触发；Polling/OnChange 电平 = 使能"),
        ("iMode", "INT", None,
         "**本 FB 只支持 3 种模式**（PDF §4.2.5.19）：0 = Manual / 1 = Polling / 2 = OnChange。**没有 OnChangePolling 模式**——与其它 _EX 不同"),
        ("CyclePolling", "TIME", "t#100ms", "Polling 周期"),
        ("DATA", "ARRAY [1..14] OF BYTE", None, "EIB 原始负载，按 [1]..[N] 顺序填字节"),
        ("EIB_Data_Len", "USINT", "1",
         "负载长度。规则同 _REC 版本：≥ 1 byte 的负载填字节数 + 1；< 1 byte 的负载填 1"),
        ("PRIORITY", "EIB_PRIORITY", None,
         "telegram 优先级：`EIB_PRIORITY_LOW` (1) / `_HIGH` (2) / `_ALARM` (3)。详见 `EIB_PRIORITY` 枚举"),
        ("MinSendTime", "TIME", "t#1s", "OnChange 模式最短间隔"),
        ("Group_Address", "EIB_GROUP_ADDR", None, "目标组地址"),
        ("str_Rec", "EIB_REC", None, "胶水结构"),
        ("bReadCommand", "BOOL", None,
         "TRUE = 本 telegram 是对 EIB READ COMMAND 的回应（不是普通数据帧）"),
    ],
    "var_output_block": (
        "VAR_OUTPUT\n"
        "    bBusy    : BOOL;\n"
        "    bError   : BOOL;\n"
        "    iErrorID : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "out_vars": [
        ("bBusy", "BOOL", "发送 / 等待中"),
        ("bError", "BOOL", "出错"),
        ("iErrorID", "EIB_ERROR_CODE", "错误码"),
    ],
    "var_inout_block": None, "inout_vars": None,
    "brief": (
        "**发送任意类型 EIB telegram**：调用方提供 byte 数组 + 长度 + 优先级，库直接打包成 EIB telegram 下发。"
        "比所有专门类型 SEND FB 都灵活——支持非标 DPT、自定义协议、对 read 请求的回应。\n\n"
        "**与 `EIB_*_SEND_EX` 的差异**：① 只支持 3 种模式（Manual / Polling / OnChange，**没有 OnChangePolling**）；"
        "② 可设 telegram 优先级（其它 _EX FB 固定 low）；③ 可主动发「对 read 请求的回应」（`bReadCommand = TRUE`）。"
    ),
    "behavior": (
        "**模式**（PDF §4.2.5.19）：\n"
        "- `iMode = 0` Manual：`bStart` 上升沿触发 1 次发送（Fig. 1）\n"
        "- `iMode = 1` Polling：`bStart = TRUE` 期间按 `CyclePolling` 定时发，不论数据变化（Fig. 2）\n"
        "- `iMode = 2` OnChange：`bStart = TRUE` 期间数据变化才发，`MinSendTime` 控制最短间隔（Fig. 3）\n\n"
        "**`bReadCommand`**：设 TRUE 时本次发的 telegram 是「对其它设备 read 请求的回应」——必须在收到 EIB_READ_REQ 后短时间内发出。"
        "典型用法：用 `EIB_ALL_DATA_TYPES_REC` 监听 read 请求，看到 `bEIB_READ = TRUE` 就用本 FB 回应当前值。\n\n"
        "**`PRIORITY`**：EIB 协议层优先级。`ALARM` 用于安全告警类 telegram（火警、安防）；`HIGH` 用于关键控制；"
        "`LOW` 默认。提高优先级在 EIB 总线繁忙时减少延迟。\n\n"
        "**与 KL6301 依赖**：必须 `bReady = TRUE`；同 PLC 任务；`str_Rec` 传同一实例；`Group_Address` 必须在过滤器内。"
    ),
    "errors": ERROR_TABLE_SEND_COMMON,
    "notes": SEND_EX_NOTES_COMMON + [
        "**没有 `bEnableReadReq` 输入**：与其它 _EX 不同——本 FB 不被动响应 read，而是主动用 `bReadCommand = TRUE` 发回应。",
        "**`EIB_Data_Len` 编码规则**：1 bit 数据填 1；2 byte 数据填 3。与 _REC 版本一致。",
        "**只有 3 种模式**：没有 OnChangePolling；要心跳 + 即时变化得自己用其它逻辑触发 `bStart`。",
        "**优先级 ALARM 应慎用**：高优先级 telegram 会抢占总线，可能导致低优先级帧被推迟。仅安全告警类用。",
    ],
    "tcpou_scene": (
        "非标 KNX 设备发 6 byte 自定义负载到组 1/3/1。本 demo 用 EIB_ALL_DATA_TYPES_SEND 按 Polling 模式定时下发。"
    ),
    "tcpou_value": "唯一支持任意长度负载 + 优先级 + read 响应的发送 FB",
    "tcpou_verify": (
        "登录 `bStart := TRUE`、`iMode := 1`、`CyclePolling := T#1S` → 每秒看到组 1/3/1 出 6 byte 帧。"
    ),
    "tcpou_decl": (
        "VAR\n"
        "    fbSendRaw      : EIB_ALL_DATA_TYPES_SEND;\n"
        "    stEibRec       : EIB_REC;\n"
        "    stGroup        : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 3, NUMBER := 1);\n"
        "    bSendStart     : BOOL;\n"
        "    iWorkMode      : INT := 1;        // Polling\n"
        "    tCycle         : TIME := T#1S;\n"
        "    tMinSend       : TIME := T#500MS;\n"
        "    arrPayload     : ARRAY[1..14] OF BYTE := [16#01, 16#02, 16#03, 16#04, 16#05, 16#06, 0,0,0,0,0,0,0,0];\n"
        "    usLen          : USINT := 7;     // 6 byte payload → len = 7\n"
        "    ePrio          : EIB_PRIORITY := EIB_PRIORITY_LOW;\n"
        "    bIsReadAnswer  : BOOL := FALSE;\n"
        "    bSendBusy      : BOOL;\n"
        "    bSendError     : BOOL;\n"
        "    iLastErrID     : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "fbSendRaw(\n"
        "    bStart        := bSendStart,\n"
        "    iMode         := iWorkMode,\n"
        "    CyclePolling  := tCycle,\n"
        "    DATA          := arrPayload,\n"
        "    EIB_Data_Len  := usLen,\n"
        "    PRIORITY      := ePrio,\n"
        "    MinSendTime   := tMinSend,\n"
        "    Group_Address := stGroup,\n"
        "    str_Rec       := stEibRec,\n"
        "    bReadCommand  := bIsReadAnswer,\n"
        "    bBusy         => bSendBusy,\n"
        "    bError        => bSendError,\n"
        "    iErrorID      => iLastErrID\n"
        ");"
    ),
    "scene": "非标 DPT / 私有协议 / 答 read 请求 / 安全告警高优先级",
    "value": "唯一全能发送 FB",
    "alternatives": [
        "专用 _EX：DPT 标准类型时用，更清晰",
        "本 FB：非标类型 / 优先级控制 / answer read 时**必选**",
    ],
    "related": (
        "`EIB_ALL_DATA_TYPES_REC` / `_EX`（接收）、"
        "`EIB_PRIORITY`（同库 §4.3.1.2 枚举）、"
        "`EIB_READ_SEND`（发起 read 请求）"
    ),
    "example_preview": (
        "PROGRAM P_Demo_EIB_ALL_DATA_TYPES_SEND\n"
        "VAR\n"
        "    fb         : EIB_ALL_DATA_TYPES_SEND;\n"
        "    stEibRec   : EIB_REC;\n"
        "    stGroup    : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 3, NUMBER := 1);\n"
        "    arrPayload : ARRAY[1..14] OF BYTE;\n"
        "END_VAR\n"
        "fb(bStart := TRUE, iMode := 1, CyclePolling := T#1S, DATA := arrPayload,\n"
        "   EIB_Data_Len := 7, PRIORITY := EIB_PRIORITY_LOW, MinSendTime := T#1S,\n"
        "   Group_Address := stGroup, str_Rec := stEibRec, bReadCommand := FALSE);"
    ),
})


# BIT_CONTROL pair (2-bit) - special
# Plain
ENTRIES.append({
    "name": "EIB_BIT_CONTROL_SEND",
    "category": "send",
    "category_label": "Send",
    "infosys_id": "187777291",
    "pdf_section": "4.2.5.20",
    "type": "FUNCTION_BLOCK",
    "var_input_block": (
        "VAR_INPUT\n"
        "    Group_Address : EIB_GROUP_ADDR;\n"
        "    bControl      : BOOL;\n"
        "    bValue        : BOOL;\n"
        "    str_Rec       : EIB_REC;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("Group_Address", "EIB_GROUP_ADDR", None, "目标组地址"),
        ("bControl", "BOOL", None, "DPT 2.xxx 控制位（强制 / 优先级位）"),
        ("bValue", "BOOL", None, "DPT 2.xxx 数据位（实际开关值）"),
        ("str_Rec", "EIB_REC", None, "胶水结构"),
    ],
    "var_output_block": (
        "VAR_OUTPUT\n"
        "    bError   : BOOL;\n"
        "    iErrorID : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "out_vars": [
        ("bError", "BOOL", "出错"),
        ("iErrorID", "EIB_ERROR_CODE", "错误码"),
    ],
    "var_inout_block": None, "inout_vars": None,
    "brief": (
        "**发送 2-bit Controlled telegram**（DPT 2.xxx：带优先级控制的 1-bit 开关）。"
        "`bControl` 或 `bValue` 任一变化即触发；最小间隔 200 ms。"
        "对应「应急覆盖普通开关」语义。"
    ),
    "behavior": (
        "**触发方式**：只要 `bControl` 或 `bValue` 任一值发生变化就立即编码并发送一帧 EIB telegram。"
        "PDF §4.2.5.20 明确：只在两个布尔位中至少一个变化时才下发，**两个都没变就不发**。\n\n"
        "**最小发送间隔 200 ms**：200 ms 内的连续变化合并到最后一次值；"
        "若值在间隔内变化又回到旧值，则不发送新帧。这是 EIB 库统一约定。\n\n"
        "**典型场景说明**：应急按钮按下时 PLC 推 `(bControl = TRUE, bValue = FALSE)` 强制关灯；"
        "应急解除时再推 `(bControl = TRUE, bValue = TRUE)` 或 `(bControl = FALSE, bValue = TRUE)`。"
        "DPT 2.xxx 接收设备会先看 `bControl` 决定是否覆盖普通指令——"
        "本 FB 只负责把组合编码下发，覆盖决策在接收端做。\n\n"
        "**与 KL6301 依赖**：必须 `KL6301.bReady = TRUE`；同 PLC 任务；`str_Rec` 传同一实例；"
        "`Group_Address` 必须在过滤器内，否则发不出去。"
    ),
    "errors": ERROR_TABLE_SEND_COMMON,
    "notes": SEND_PLAIN_NOTES_COMMON + [
        "**`bControl = TRUE` 是强制位**：DPT 2.xxx 接收端必须解码 `bControl` 决定是否覆盖。",
    ],
    "tcpou_scene": (
        "应急按钮：「警报」按下时 PLC 发 (`bControl = TRUE, bValue = FALSE`) 到组 1/1/40 强制关灯。"
    ),
    "tcpou_value": "替代手写 2-bit 拼装；DPT 2.xxx 标准发送",
    "tcpou_verify": (
        "推 (TRUE, FALSE) → 组 1/1/40 出 0b10。"
    ),
    "tcpou_decl": (
        "VAR\n"
        "    fbSendEmergency : EIB_BIT_CONTROL_SEND;\n"
        "    stEibRec        : EIB_REC;\n"
        "    stGroup         : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 1, NUMBER := 40);\n"
        "    bForced         : BOOL;\n"
        "    bValueOn        : BOOL;\n"
        "    bSendError      : BOOL;\n"
        "    iLastErrID      : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "fbSendEmergency(\n"
        "    Group_Address := stGroup,\n"
        "    bControl      := bForced,\n"
        "    bValue        := bValueOn,\n"
        "    str_Rec       := stEibRec,\n"
        "    bError        => bSendError,\n"
        "    iErrorID      => iLastErrID\n"
        ");"
    ),
    "scene": "应急 / 安全联锁 / DPT 2.xxx 优先级场景",
    "value": "DPT 2.xxx 标准发送",
    "alternatives": [
        "`EIB_BIT_CONTROL_SEND_EX`：周期 + read 响应",
        "`EIB_BIT_SEND`：纯 1-bit 无优先级",
        "本 FB：DPT 2.xxx 标准选择",
    ],
    "related": "`EIB_BIT_CONTROL_SEND_EX`（§4.2.5.21）、`EIB_BIT_CONTROL_REC`",
    "example_preview": (
        "PROGRAM P_Demo_EIB_BIT_CONTROL_SEND\n"
        "VAR\n"
        "    fb       : EIB_BIT_CONTROL_SEND;\n"
        "    stEibRec : EIB_REC;\n"
        "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 1, NUMBER := 40);\n"
        "END_VAR\n"
        "fb(Group_Address := stGroup, bControl := TRUE, bValue := FALSE, str_Rec := stEibRec);"
    ),
})


# BIT_CONTROL EX
ENTRIES.append({
    "name": "EIB_BIT_CONTROL_SEND_EX",
    "category": "send",
    "category_label": "Send",
    "infosys_id": "16287830155",
    "pdf_section": "4.2.5.21",
    "type": "FUNCTION_BLOCK",
    "var_input_block": (
        "VAR_INPUT\n"
        "    bStart         : BOOL;\n"
        "    iMode          : INT;\n"
        "    CyclePolling   : TIME := t#500ms;\n"
        "    MinSendTime    : TIME := t#1s;\n"
        "    Group_Address  : EIB_GROUP_ADDR;\n"
        "    bControl       : BOOL;\n"
        "    bValue         : BOOL;\n"
        "    str_Rec        : EIB_REC;\n"
        "    bEnableReadReq : BOOL;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("bStart", "BOOL", None, "触发输入"),
        ("iMode", "INT", None, "0/1/2/3 = Manual/Polling/OnChange/OnChangePolling"),
        ("CyclePolling", "TIME", "t#500ms", "Polling 周期，下限 200 ms"),
        ("MinSendTime", "TIME", "t#1s", "OnChange 最短间隔，下限 200 ms"),
        ("Group_Address", "EIB_GROUP_ADDR", None, "目标组地址"),
        ("bControl", "BOOL", None, "控制位"),
        ("bValue", "BOOL", None, "数据位"),
        ("str_Rec", "EIB_REC", None, "胶水结构"),
        ("bEnableReadReq", "BOOL", None, "使能 read 响应"),
    ],
    "var_output_block": (
        "VAR_OUTPUT\n"
        "    bBusy    : BOOL;\n"
        "    bError   : BOOL;\n"
        "    iErrorID : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "out_vars": [
        ("bBusy", "BOOL", "忙"),
        ("bError", "BOOL", "出错"),
        ("iErrorID", "EIB_ERROR_CODE", "错误码"),
    ],
    "var_inout_block": None, "inout_vars": None,
    "brief": (
        "`EIB_BIT_CONTROL_SEND` 的扩展版本：支持 4 种模式 + 响应 read。"
        "DPT 2.xxx 复杂场景（应急覆盖 + BMS 主动查询）首选。"
    ),
    "behavior": SEND_EX_BEHAVIOR,
    "errors": ERROR_TABLE_SEND_COMMON,
    "notes": SEND_EX_NOTES_COMMON,
    "tcpou_scene": (
        "应急状态按 OnChangePolling 心跳 10 秒，确保 BMS 即使错过即时变化也能同步当前应急状态。"
    ),
    "tcpou_value": "DPT 2.xxx + 周期心跳 + 即时变化 + 答查；安全工程首选",
    "tcpou_verify": (
        "登录 `bStart := TRUE`、`iMode := 3` → 每 10 秒看到组 1/1/40 出帧。"
    ),
    "tcpou_decl": (
        "VAR\n"
        "    fbSendEmergencyEx  : EIB_BIT_CONTROL_SEND_EX;\n"
        "    stEibRec           : EIB_REC;\n"
        "    stGroup            : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 1, NUMBER := 40);\n"
        "    bSendStart         : BOOL;\n"
        "    iWorkMode          : INT := 3;\n"
        "    tCycle             : TIME := T#10S;\n"
        "    tMinSend           : TIME := T#500MS;\n"
        "    bForced            : BOOL;\n"
        "    bValueOn           : BOOL;\n"
        "    bResponseRead      : BOOL := TRUE;\n"
        "    bSendBusy          : BOOL;\n"
        "    bSendError         : BOOL;\n"
        "    iLastErrID         : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "fbSendEmergencyEx(\n"
        "    bStart         := bSendStart,\n"
        "    iMode          := iWorkMode,\n"
        "    CyclePolling   := tCycle,\n"
        "    MinSendTime    := tMinSend,\n"
        "    Group_Address  := stGroup,\n"
        "    bControl       := bForced,\n"
        "    bValue         := bValueOn,\n"
        "    str_Rec        := stEibRec,\n"
        "    bEnableReadReq := bResponseRead,\n"
        "    bBusy          => bSendBusy,\n"
        "    bError         => bSendError,\n"
        "    iErrorID       => iLastErrID\n"
        ");"
    ),
    "scene": "DPT 2.xxx 应急 + 心跳 + 答查",
    "value": "BMS 安全工程首选",
    "alternatives": [
        "非 _EX：仅变化发",
        "本 _EX：BMS 安全工程首选",
    ],
    "related": "`EIB_BIT_CONTROL_SEND`（§4.2.5.20）、`EIB_BIT_CONTROL_REC`",
    "example_preview": (
        "PROGRAM P_Demo_EIB_BIT_CONTROL_SEND_EX\n"
        "VAR\n"
        "    fb       : EIB_BIT_CONTROL_SEND_EX;\n"
        "    stEibRec : EIB_REC;\n"
        "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 1, NUMBER := 40);\n"
        "END_VAR\n"
        "fb(bStart := TRUE, iMode := 3, CyclePolling := T#10S, MinSendTime := T#500MS,\n"
        "   Group_Address := stGroup, bControl := TRUE, bValue := FALSE,\n"
        "   str_Rec := stEibRec, bEnableReadReq := TRUE);"
    ),
})


# BIT pair - plain + EX + MANUAL
# BIT plain
_quick_send_pair(
    "EIB_BIT_SEND", "187778827", "4.2.5.22",
    "EIB_BIT_SEND_EX", "187780363", "4.2.5.23",
    ("bData", "BOOL", "1 bit 数据值（TRUE/FALSE）。DPT 1.001 中 TRUE = ON、FALSE = OFF"),
    "DPT 1.xxx (1-bit)", "200 ms",
    "t#10s", "t#1s",   # _EX default cycle 10 s for BIT
    "开关命令", (1, 1, 50),
    "FALSE", "DPT 1.xxx",
)


# EIB_BIT_SEND_MANUAL
ENTRIES.append({
    "name": "EIB_BIT_SEND_MANUAL",
    "category": "send",
    "category_label": "Send",
    "infosys_id": "187781899",
    "pdf_section": "4.2.5.24",
    "type": "FUNCTION_BLOCK",
    "var_input_block": (
        "VAR_INPUT\n"
        "    Group_Address : EIB_GROUP_ADDR;\n"
        "    bSend         : BOOL;\n"
        "    bData         : BOOL;\n"
        "    str_Rec       : EIB_REC;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("Group_Address", "EIB_GROUP_ADDR", None, "目标组地址"),
        ("bSend", "BOOL", None, "上升沿触发一次发送（即使 `bData` 没变化也强制下发）"),
        ("bData", "BOOL", None, "1 bit 数据值"),
        ("str_Rec", "EIB_REC", None, "胶水结构"),
    ],
    "var_output_block": (
        "VAR_OUTPUT\n"
        "    bBusy    : BOOL;\n"
        "    bError   : BOOL;\n"
        "    iErrorID : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "out_vars": [
        ("bBusy", "BOOL", "FB 活动期间为 TRUE，发送完成 / 失败后回 FALSE"),
        ("bError", "BOOL", "出错"),
        ("iErrorID", "EIB_ERROR_CODE", "错误码"),
    ],
    "var_inout_block": None, "inout_vars": None,
    "brief": (
        "**手动触发 1-bit 发送**：与 `EIB_BIT_SEND` 区别——本 FB 必须 `bSend` 上升沿才触发，"
        "**不论 `bData` 是否变化**都强制下发当前值。\n\n"
        "用于「心跳」或「刷新」场景：业务上想周期重发开关状态以防 BMS 失同步、或想在 BMS 失联后强制重新推送当前状态。"
    ),
    "behavior": (
        "**触发**：仅 `bSend` 上升沿触发一次发送，**不看 `bData` 是否变化**——与 `EIB_BIT_SEND`（变化触发）相反。\n\n"
        "**状态机**：`bSend ↑` → `bBusy := TRUE` 发送 → 完成或失败 `bBusy := FALSE`。"
        "完成时 `bError := FALSE`；失败时 `bError := TRUE`、`iErrorID` 给错误码。\n\n"
        "**与 KL6301 依赖**：必须 `bReady = TRUE`；同 PLC 任务；`str_Rec` 传同一实例；`Group_Address` 必须在过滤器内。\n\n"
        "**vs `EIB_BIT_SEND`**：BIT_SEND 自动检测 `bData` 变化触发；MANUAL 必须显式 `bSend` 上升沿。MANUAL 可重发同一值。"
    ),
    "errors": ERROR_TABLE_SEND_COMMON,
    "notes": SEND_PLAIN_NOTES_COMMON + [
        "**`bSend` 是手动触发**：业务逻辑里要自己定时拉高 `bSend` 一个 PLC 周期触发重发。",
        "**可重发同一值**：与 `EIB_BIT_SEND` 不同——MANUAL 能强制重发，用于心跳。",
    ],
    "tcpou_scene": (
        "心跳重发：业务上每 30 秒主动重发开关状态到组 1/1/55，避免 BMS 因网络问题失同步。"
    ),
    "tcpou_value": "强制重发同一值；BMS 失同步保险",
    "tcpou_verify": (
        "改 `bData := TRUE`、置 `bSend := TRUE` 一个周期 → BMS 应看到 1/1/55 出 TRUE 帧；"
        "再置 `bSend := TRUE`（不改 bData）→ 又出一帧（即使值没变）。"
    ),
    "tcpou_decl": (
        "VAR\n"
        "    fbSendManual    : EIB_BIT_SEND_MANUAL;\n"
        "    stEibRec        : EIB_REC;\n"
        "    stGroup         : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 1, NUMBER := 55);\n"
        "    bTriggerResend  : BOOL;       // 业务上拉高一个周期触发\n"
        "    bCurrentLamp    : BOOL := TRUE;\n"
        "    bSendBusy       : BOOL;\n"
        "    bSendError      : BOOL;\n"
        "    iLastErrID      : EIB_ERROR_CODE;\n"
        "    fbHeartbeat     : TON;\n"
        "    rTrigHeartbeat  : R_TRIG;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "// 每 30 秒触发一次重发\n"
        "fbHeartbeat(IN := NOT fbHeartbeat.Q, PT := T#30S);\n"
        "rTrigHeartbeat(CLK := fbHeartbeat.Q);\n"
        "bTriggerResend := rTrigHeartbeat.Q;\n"
        "\n"
        "fbSendManual(\n"
        "    Group_Address := stGroup,\n"
        "    bSend         := bTriggerResend,\n"
        "    bData         := bCurrentLamp,\n"
        "    str_Rec       := stEibRec,\n"
        "    bBusy         => bSendBusy,\n"
        "    bError        => bSendError,\n"
        "    iErrorID      => iLastErrID\n"
        ");"
    ),
    "scene": "BMS 心跳重发 / 失同步保险 / 强制刷新当前状态",
    "value": "唯一支持强制重发同一值的 1-bit FB",
    "alternatives": [
        "`EIB_BIT_SEND`：仅变化发，做不到强制重发",
        "`EIB_BIT_SEND_EX` (Polling 模式)：能周期发，但触发不那么显式",
        "本 FB：心跳重发的清晰选择",
    ],
    "related": "`EIB_BIT_SEND`、`EIB_BIT_SEND_EX`、`EIB_BIT_REC`",
    "example_preview": (
        "PROGRAM P_Demo_EIB_BIT_SEND_MANUAL\n"
        "VAR\n"
        "    fb       : EIB_BIT_SEND_MANUAL;\n"
        "    stEibRec : EIB_REC;\n"
        "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 1, NUMBER := 55);\n"
        "    bSend    : BOOL;\n"
        "    bData    : BOOL := TRUE;\n"
        "END_VAR\n"
        "fb(Group_Address := stGroup, bSend := bSend, bData := bData, str_Rec := stEibRec);"
    ),
})


# DATE pair
# Plain
ENTRIES.append({
    "name": "EIB_DATE_SEND",
    "category": "send",
    "category_label": "Send",
    "infosys_id": "187783435",
    "pdf_section": "4.2.5.25",
    "type": "FUNCTION_BLOCK",
    "var_input_block": (
        "VAR_INPUT\n"
        "    Group_Address : EIB_GROUP_ADDR;\n"
        "    wDay          : WORD;\n"
        "    wMonth        : WORD;\n"
        "    wYear         : WORD;\n"
        "    str_Rec       : EIB_REC;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("Group_Address", "EIB_GROUP_ADDR", None, "目标组地址"),
        ("wDay", "WORD", None, "日，1..31"),
        ("wMonth", "WORD", None, "月，1..12"),
        ("wYear", "WORD", None,
         "年，0..99。**若传入值 > 2000，库会自动减 2000**——例 2025 → 实际发 25（PDF §4.2.5.25 表）"),
        ("str_Rec", "EIB_REC", None, "胶水结构"),
    ],
    "var_output_block": (
        "VAR_OUTPUT\n"
        "    bError   : BOOL;\n"
        "    iErrorID : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "out_vars": [
        ("bError", "BOOL", "出错"),
        ("iErrorID", "EIB_ERROR_CODE", "错误码"),
    ],
    "var_inout_block": None, "inout_vars": None,
    "brief": (
        "**发送 3 字节日期 telegram**（DPT 11.001）。"
        "**首次调用 + 之后每 5 分钟**自动重发（PDF §4.2.5.25 描述："
        "\"data are sent when the block is called for the first time and then every 5 minutes\"）。\n\n"
        "**`wYear` 自动减 2000**：传入 2025 → 库发 25。这是为了兼容业务代码直接传 4 位年。"
    ),
    "behavior": (
        "**触发**：首次调用立即发一次；之后每 5 分钟自动重发当前 (wDay/wMonth/wYear)。\n\n"
        "**与变化无关**：本 FB 不检测数据变化——按固定 5 分钟节拍刷新。"
        "业务上要更频繁就用 `EIB_DATE_SEND_EX` 配 Polling 模式。\n\n"
        "**年自动减 2000**：传入 > 2000 时库内部减 2000；< 2000 直接当作 0..99。"
        "因此 2025 → 实际发 25；24 → 实际发 24（不变）。\n\n"
        "**与 KL6301 依赖**：必须 `bReady = TRUE`；同 PLC 任务；`str_Rec` 传同一实例；`Group_Address` 必须在过滤器内。"
    ),
    "errors": ERROR_TABLE_SEND_COMMON,
    "notes": SEND_PLAIN_NOTES_COMMON + [
        "**5 分钟固定节拍**：本 FB 不可调整。要更短间隔用 `_EX` 版本。",
        "**年字段自动减 2000**：传 2025 不会发 2025；库自动减成 25。业务可直接传 4 位年。",
        "**接收端 `EIB_DATE_REC` 也是 2 位年**：业务上做「未来 / 过去」判断要自己加世纪基。",
    ],
    "tcpou_scene": (
        "BMS 主时钟 PLC：把当前日期每 5 分钟广播到组 1/0/1。"
    ),
    "tcpou_value": "DPT 11 标准发送；零代码实现日期广播",
    "tcpou_verify": (
        "登录 → BMS 接收端应每 5 分钟看到 1/0/1 出 3 byte 日期帧。"
    ),
    "tcpou_decl": (
        "VAR\n"
        "    fbSendDate  : EIB_DATE_SEND;\n"
        "    stEibRec    : EIB_REC;\n"
        "    stGroup     : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 0, NUMBER := 1);\n"
        "    wDay        : WORD := 3;\n"
        "    wMonth      : WORD := 6;\n"
        "    wYear       : WORD := 2026;   // 库自动减 2000 = 26\n"
        "    bSendError  : BOOL;\n"
        "    iLastErrID  : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "fbSendDate(\n"
        "    Group_Address := stGroup,\n"
        "    wDay          := wDay,\n"
        "    wMonth        := wMonth,\n"
        "    wYear         := wYear,\n"
        "    str_Rec       := stEibRec,\n"
        "    bError        => bSendError,\n"
        "    iErrorID      => iLastErrID\n"
        ");"
    ),
    "scene": "BMS 主时钟日期广播 / 设备日历同步",
    "value": "DPT 11 标准发送，无代码量",
    "alternatives": [
        "`EIB_DATE_SEND_EX`：间隔可调 + read 响应",
        "本 FB：固定 5 分钟节拍",
    ],
    "related": "`EIB_DATE_SEND_EX`（§4.2.5.26）、`EIB_DATE_REC`、`EIB_TIME_SEND`",
    "example_preview": (
        "PROGRAM P_Demo_EIB_DATE_SEND\n"
        "VAR\n"
        "    fb       : EIB_DATE_SEND;\n"
        "    stEibRec : EIB_REC;\n"
        "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 0, NUMBER := 1);\n"
        "END_VAR\n"
        "fb(Group_Address := stGroup, wDay := 3, wMonth := 6, wYear := 2026,\n"
        "   str_Rec := stEibRec);"
    ),
})


# DATE EX
ENTRIES.append({
    "name": "EIB_DATE_SEND_EX",
    "category": "send",
    "category_label": "Send",
    "infosys_id": "16287832459",
    "pdf_section": "4.2.5.26",
    "type": "FUNCTION_BLOCK",
    "var_input_block": (
        "VAR_INPUT\n"
        "    bStart         : BOOL;\n"
        "    iMode          : INT;\n"
        "    CyclePolling   : TIME := t#500ms;\n"
        "    MinSendTime    : TIME := t#1s;\n"
        "    Group_Address  : EIB_GROUP_ADDR;\n"
        "    wDay           : WORD;\n"
        "    wMonth         : WORD;\n"
        "    wYear          : WORD;\n"
        "    str_Rec        : EIB_REC;\n"
        "    bEnableReadReq : BOOL;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("bStart", "BOOL", None, "触发"),
        ("iMode", "INT", None, "0/1/2/3"),
        ("CyclePolling", "TIME", "t#500ms", "Polling 周期，下限 200 ms"),
        ("MinSendTime", "TIME", "t#1s", "OnChange 最短间隔，下限 200 ms"),
        ("Group_Address", "EIB_GROUP_ADDR", None, "目标组地址"),
        ("wDay", "WORD", None, "日，1..31"),
        ("wMonth", "WORD", None, "月，1..12"),
        ("wYear", "WORD", None, "年，0..99；> 2000 时库自动减 2000"),
        ("str_Rec", "EIB_REC", None, "胶水结构"),
        ("bEnableReadReq", "BOOL", None, "使能 read 响应"),
    ],
    "var_output_block": (
        "VAR_OUTPUT\n"
        "    bBusy    : BOOL;\n"
        "    bError   : BOOL;\n"
        "    iErrorID : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "out_vars": [
        ("bBusy", "BOOL", "忙"),
        ("bError", "BOOL", "出错"),
        ("iErrorID", "EIB_ERROR_CODE", "错误码"),
    ],
    "var_inout_block": None, "inout_vars": None,
    "brief": (
        "`EIB_DATE_SEND` 的扩展版本：周期 / 变化 / 答查可调。"
        "替代固定 5 分钟节拍——适合需要更频繁或不定期发的场景。"
    ),
    "behavior": SEND_EX_BEHAVIOR,
    "errors": ERROR_TABLE_SEND_COMMON,
    "notes": SEND_EX_NOTES_COMMON + [
        "**`wYear` > 2000 自动减 2000**：与非 _EX 版本相同行为。",
    ],
    "tcpou_scene": "日期每分钟广播 + 响应 BMS read 请求",
    "tcpou_value": "比 5 分钟节拍更灵活",
    "tcpou_verify": "登录 `bStart := TRUE`、`iMode := 1`、`CyclePolling := T#1M` → 每分钟出帧。",
    "tcpou_decl": (
        "VAR\n"
        "    fbSendDateEx    : EIB_DATE_SEND_EX;\n"
        "    stEibRec        : EIB_REC;\n"
        "    stGroup         : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 0, NUMBER := 1);\n"
        "    bSendStart      : BOOL;\n"
        "    iWorkMode       : INT := 1;\n"
        "    tCycle          : TIME := T#1M;\n"
        "    tMinSend        : TIME := T#500MS;\n"
        "    wDay            : WORD := 3;\n"
        "    wMonth          : WORD := 6;\n"
        "    wYear           : WORD := 2026;\n"
        "    bResponseRead   : BOOL := TRUE;\n"
        "    bSendBusy       : BOOL;\n"
        "    bSendError      : BOOL;\n"
        "    iLastErrID      : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "fbSendDateEx(\n"
        "    bStart         := bSendStart,\n"
        "    iMode          := iWorkMode,\n"
        "    CyclePolling   := tCycle,\n"
        "    MinSendTime    := tMinSend,\n"
        "    Group_Address  := stGroup,\n"
        "    wDay           := wDay,\n"
        "    wMonth         := wMonth,\n"
        "    wYear          := wYear,\n"
        "    str_Rec        := stEibRec,\n"
        "    bEnableReadReq := bResponseRead,\n"
        "    bBusy          => bSendBusy,\n"
        "    bError         => bSendError,\n"
        "    iErrorID       => iLastErrID\n"
        ");"
    ),
    "scene": "灵活间隔的日期广播",
    "value": "BMS 时钟同步首选",
    "alternatives": ["非 _EX：固定 5 分钟", "本 _EX：灵活"],
    "related": "`EIB_DATE_SEND`、`EIB_DATE_REC`",
    "example_preview": (
        "PROGRAM P_Demo_EIB_DATE_SEND_EX\n"
        "VAR\n"
        "    fb       : EIB_DATE_SEND_EX;\n"
        "    stEibRec : EIB_REC;\n"
        "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 0, NUMBER := 1);\n"
        "END_VAR\n"
        "fb(bStart := TRUE, iMode := 1, CyclePolling := T#1M, MinSendTime := T#500MS,\n"
        "   Group_Address := stGroup, wDay := 3, wMonth := 6, wYear := 2026,\n"
        "   str_Rec := stEibRec, bEnableReadReq := TRUE);"
    ),
})


# EIB_READ_SEND
ENTRIES.append({
    "name": "EIB_READ_SEND",
    "category": "send",
    "category_label": "Send",
    "infosys_id": "187784971",
    "pdf_section": "4.2.5.27",
    "type": "FUNCTION_BLOCK",
    "var_input_block": (
        "VAR_INPUT\n"
        "    Group_Address : EIB_GROUP_ADDR;\n"
        "    bRead         : BOOL;\n"
        "    str_Rec       : EIB_REC;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("Group_Address", "EIB_GROUP_ADDR", None,
         "**要查询数据的组地址**（不是要发送数据的目标）。**必须在 KL6301 过滤器内**，否则收不到响应"),
        ("bRead", "BOOL", None,
         "上升沿触发：FB 发一帧 Read_Group_Req 到 EIB 网络，请求所有挂在该 group 的设备回传当前值"),
        ("str_Rec", "EIB_REC", None, "胶水结构，传 `KL6301.str_Data_Rec`"),
    ],
    "var_output_block": (
        "VAR_OUTPUT\n"
        "    bError        : BOOL;\n"
        "    iErrorID      : EIB_ERROR_CODE;\n"
        "    bBusy         : BOOL;\n"
        "END_VAR"
    ),
    "out_vars": [
        ("bError", "BOOL", "出错"),
        ("iErrorID", "EIB_ERROR_CODE", "错误码"),
        ("bBusy", "BOOL", "FB 活动期间为 TRUE，发送完成 / 失败后回 FALSE"),
    ],
    "var_inout_block": None, "inout_vars": None,
    "brief": (
        "**发送 EIB Read_Group_Req（主动查询）** 到指定组地址，请求所有挂在该地址的设备回传当前值。"
        "本 FB 只发请求；**回应数据由对应的 `EIB_*_REC` FB 接收**（接收 FB 也必须订阅这同一个 `Group_Address`）。\n\n"
        "**典型用法**：PLC 启动后想知道楼宇里现有的灯 / 调光器当前状态，调本 FB 发 read_req 到那些组地址，"
        "对应设备会主动回应——比等设备自己周期推送快得多。"
    ),
    "behavior": (
        "**触发**：`bRead` 上升沿触发一次 Read_Group_Req。`bBusy` 期间忽略新触发。\n\n"
        "**响应不由本 FB 接收**：被查的设备会发回普通 telegram，需要对应类型的 `EIB_*_REC` FB（订阅同 `Group_Address`）接收。"
        "PDF 明确 `To receive a response, the group address must be entered in the filter!` ——KL6301 过滤器必须包含该地址，否则响应会被丢。\n\n"
        "**与 KL6301 依赖**：必须 `bReady = TRUE`；同 PLC 任务；`str_Rec` 传同一实例；`Group_Address` 必须在过滤器内。"
    ),
    "errors": ERROR_TABLE_SEND_COMMON,
    "notes": SEND_PLAIN_NOTES_COMMON + [
        "**`Group_Address` 是「要查的」地址，不是「要发的」地址**：与其它 SEND FB 语义相反，新手易混淆。",
        "**响应要靠对应的 `_REC` FB**：本 FB 不收响应，业务上要并行挂一个相同 `Group_Address` 的 _REC。",
        "**`Group_Address` 必须在 KL6301 过滤器内**：否则即便对端发回响应也被 KL6301 丢；PDF 明确警告。",
    ],
    "tcpou_scene": (
        "PLC 启动时主动查询调光器 1/2/3 当前亮度——发 read_req → 调光器回应 → "
        "EIB_8BIT_SIGN_REC 接收响应值。"
    ),
    "tcpou_value": "主动查询比等设备自报快得多；常用于 BMS 启动同步",
    "tcpou_verify": (
        "置 `bTriggerRead := TRUE` 一个周期 → BMS 应能在 group monitor 看到 1/2/3 出 read_req；"
        "调光器回应后 `EIB_8BIT_SIGN_REC.bDataReceive` 单周期高，`iDimLevel` = 当前调光器亮度。"
    ),
    "tcpou_decl": (
        "VAR\n"
        "    fbReadReq        : EIB_READ_SEND;\n"
        "    fbReceiveBri     : EIB_8BIT_SIGN_REC;   // 接收对应响应\n"
        "    stEibRec         : EIB_REC;\n"
        "    stGroupDimmer    : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 3);\n"
        "    bTriggerRead     : BOOL;\n"
        "    bReadBusy        : BOOL;\n"
        "    bReadError       : BOOL;\n"
        "    iLastErrID       : EIB_ERROR_CODE;\n"
        "    bGotResponse     : BOOL;\n"
        "    iDimLevel        : INT;\n"
        "    rTrigResponse    : R_TRIG;\n"
        "    nResponseCount   : DINT;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "// 1) 发 read_req 到调光器组地址\n"
        "fbReadReq(\n"
        "    Group_Address := stGroupDimmer,\n"
        "    bRead         := bTriggerRead,\n"
        "    str_Rec       := stEibRec,\n"
        "    bError        => bReadError,\n"
        "    iErrorID      => iLastErrID,\n"
        "    bBusy         => bReadBusy\n"
        ");\n"
        "\n"
        "// 2) 并行接收同地址的响应（调光器会回 8-bit 当前亮度）\n"
        "fbReceiveBri(\n"
        "    Group_Address := stGroupDimmer,\n"
        "    Scaling_Mode  := 0,             // 0..100%\n"
        "    strData_Rec   := stEibRec,\n"
        "    bDataReceive  => bGotResponse,\n"
        "    iData         => iDimLevel\n"
        ");\n"
        "\n"
        "// 3) 数响应次数\n"
        "rTrigResponse(CLK := bGotResponse);\n"
        "IF rTrigResponse.Q THEN\n"
        "    nResponseCount := nResponseCount + 1;\n"
        "END_IF;"
    ),
    "scene": "主动同步设备当前状态（启动、失同步恢复、HMI 刷新）",
    "value": "唯一发起 EIB read 请求的 FB；比等设备自报快",
    "alternatives": [
        "等设备自己周期推送：慢且不可控",
        "本 FB：主动同步的唯一方式",
    ],
    "related": (
        "对应 `EIB_*_REC`（接收响应）、"
        "`EIB_ALL_DATA_TYPES_REC`（识别 `bEIB_READ`）、"
        "`EIB_ALL_DATA_TYPES_SEND` (`bReadCommand = TRUE` 对方答 read 用)"
    ),
    "example_preview": (
        "PROGRAM P_Demo_EIB_READ_SEND\n"
        "VAR\n"
        "    fb       : EIB_READ_SEND;\n"
        "    stEibRec : EIB_REC;\n"
        "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 3);\n"
        "    bRead    : BOOL;\n"
        "END_VAR\n"
        "fb(Group_Address := stGroup, bRead := bRead, str_Rec := stEibRec);"
    ),
})


# TIME pair
# Plain
ENTRIES.append({
    "name": "EIB_TIME_SEND",
    "category": "send",
    "category_label": "Send",
    "infosys_id": "187786507",
    "pdf_section": "4.2.5.28",
    "type": "FUNCTION_BLOCK",
    "var_input_block": (
        "VAR_INPUT\n"
        "    Group_Address : EIB_GROUP_ADDR;\n"
        "    wHoure        : WORD;\n"
        "    wMinute       : WORD;\n"
        "    wSecond       : WORD;\n"
        "    str_Rec       : EIB_REC;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("Group_Address", "EIB_GROUP_ADDR", None, "目标组地址"),
        ("wHoure", "WORD", None, "小时，0..23。**PDF 引脚名为 `wHoure`**（拼写错），逐字保留"),
        ("wMinute", "WORD", None, "分钟，0..59"),
        ("wSecond", "WORD", None, "秒，0..59"),
        ("str_Rec", "EIB_REC", None, "胶水结构"),
    ],
    "var_output_block": (
        "VAR_OUTPUT\n"
        "    bError   : BOOL;\n"
        "    iErrorID : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "out_vars": [
        ("bError", "BOOL", "出错"),
        ("iErrorID", "EIB_ERROR_CODE", "错误码"),
    ],
    "var_inout_block": None, "inout_vars": None,
    "brief": (
        "**发送 3 字节时间 telegram**（DPT 10.001）。"
        "**首次调用 + 之后每 5 分钟**自动重发，与 `EIB_DATE_SEND` 节拍一致。\n\n"
        "**PDF 拼写错**：引脚是 `wHoure`（多 e），与库实际一致，代码必须按 PDF 写。"
    ),
    "behavior": (
        "**触发节拍**：首次调用立即发一次时间 telegram；之后每 5 分钟自动重发当前 (`wHoure`/`wMinute`/`wSecond`)。"
        "节拍固定为 5 分钟，**不可配置**——业务上若要更频繁（例如每分钟）必须用 `EIB_TIME_SEND_EX` 的 Polling 模式。\n\n"
        "**首帧时机**：首次调用即发——这与「变化触发」类 SEND FB 不同。意味着：① PLC 启动后立即广播一次让 BMS 同步；"
        "② 即使 (`wHoure`/`wMinute`/`wSecond`) 值没变化也会按节拍重发，保证 BMS 不会因偶尔丢帧失同步。\n\n"
        "**时间字段语义**：`wHoure` 是 hour（PDF 拼写错），值域 0..23；`wMinute` 值域 0..59；`wSecond` 值域 0..59。"
        "本 FB 不做时区转换，业务上传入的时间就是 EIB 总线上看到的时间。如果业务用 UTC 而 BMS 期望本地时间，"
        "调用前要先做本地化转换。\n\n"
        "**与 KL6301 依赖**：必须 `KL6301.bReady = TRUE`；同 PLC 任务；`str_Rec` 传同一实例；"
        "`Group_Address` 必须在过滤器内。"
    ),
    "errors": ERROR_TABLE_SEND_COMMON,
    "notes": SEND_PLAIN_NOTES_COMMON + [
        "**`wHoure` 拼写错**：库实际就是 `wHoure`；代码必须按 PDF 写。",
        "**5 分钟节拍固定**：要更短用 `_EX`。",
        "**与 `EIB_DATE_SEND` 配合**：通常 date 和 time 双广播。",
    ],
    "tcpou_scene": "BMS 主时钟广播时间到组 1/0/2，每 5 分钟一次",
    "tcpou_value": "DPT 10 标准发送，零代码",
    "tcpou_verify": "登录后 → 每 5 分钟看到 1/0/2 出 3 byte 时间帧",
    "tcpou_decl": (
        "VAR\n"
        "    fbSendTime  : EIB_TIME_SEND;\n"
        "    stEibRec    : EIB_REC;\n"
        "    stGroup     : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 0, NUMBER := 2);\n"
        "    wHoure      : WORD := 14;\n"
        "    wMinute     : WORD := 30;\n"
        "    wSecond     : WORD := 0;\n"
        "    bSendError  : BOOL;\n"
        "    iLastErrID  : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "fbSendTime(\n"
        "    Group_Address := stGroup,\n"
        "    wHoure        := wHoure,\n"
        "    wMinute       := wMinute,\n"
        "    wSecond       := wSecond,\n"
        "    str_Rec       := stEibRec,\n"
        "    bError        => bSendError,\n"
        "    iErrorID      => iLastErrID\n"
        ");"
    ),
    "scene": "BMS 主时钟时间广播",
    "value": "DPT 10 标准发送",
    "alternatives": ["`EIB_TIME_SEND_EX`：灵活间隔", "本 FB：5 分钟固定"],
    "related": "`EIB_TIME_SEND_EX`、`EIB_TIME_REC`、`EIB_DATE_SEND`",
    "example_preview": (
        "PROGRAM P_Demo_EIB_TIME_SEND\n"
        "VAR\n"
        "    fb       : EIB_TIME_SEND;\n"
        "    stEibRec : EIB_REC;\n"
        "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 0, NUMBER := 2);\n"
        "END_VAR\n"
        "fb(Group_Address := stGroup, wHoure := 14, wMinute := 30, wSecond := 0,\n"
        "   str_Rec := stEibRec);"
    ),
})


# TIME EX (NOTE: PDF prints wDay/wMonth/wYear in inputs but text says it sends time —
# this is a PDF copy-paste error. The actual semantics is time; the EIB topic shows the FB
# is for time. Let's preserve PDF verbatim VAR_INPUT but explain.)
ENTRIES.append({
    "name": "EIB_TIME_SEND_EX",
    "category": "send",
    "category_label": "Send",
    "infosys_id": "16287833611",
    "pdf_section": "4.2.5.29",
    "type": "FUNCTION_BLOCK",
    "var_input_block": (
        # PDF page 67 shows wDay/wMonth/wYear in VAR_INPUT (PDF copy-paste error from DATE_SEND_EX)
        # then PDF page 68 description table shows wHour/wMinute/wSecond.
        # The actual library FB is for TIME. Preserve PDF VAR_INPUT verbatim per CLAUDE.md
        # rule A.1 (逐字搬运), then document the discrepancy in §3.
        "VAR_INPUT\n"
        "    bStart         : BOOL;\n"
        "    iMode          : INT;\n"
        "    CyclePolling   : TIME := t#500ms;\n"
        "    MinSendTime    : TIME := t#1s;\n"
        "    Group_Address  : EIB_GROUP_ADDR;\n"
        "    wDay           : WORD;\n"
        "    wMonth         : WORD;\n"
        "    wYear          : WORD;\n"
        "    str_Rec        : EIB_REC;\n"
        "    bEnableReadReq : BOOL;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("bStart", "BOOL", None, "触发"),
        ("iMode", "INT", None, "0/1/2/3 模式"),
        ("CyclePolling", "TIME", "t#500ms", "Polling 周期"),
        ("MinSendTime", "TIME", "t#1s", "OnChange 最短间隔"),
        ("Group_Address", "EIB_GROUP_ADDR", None, "目标组地址"),
        ("wDay", "WORD", None, "**PDF 排版错——本 FB 名为 TIME_SEND_EX 但 VAR_INPUT 误抄了 DATE_SEND_EX 的 wDay/wMonth/wYear**。详见 §3 行为说明。按 PDF 逐字保留"),
        ("wMonth", "WORD", None, "（同上 PDF 排版错）"),
        ("wYear", "WORD", None, "（同上 PDF 排版错）"),
        ("str_Rec", "EIB_REC", None, "胶水结构"),
        ("bEnableReadReq", "BOOL", None, "使能 read 响应"),
    ],
    "var_output_block": (
        "VAR_OUTPUT\n"
        "    bBusy    : BOOL;\n"
        "    bError   : BOOL;\n"
        "    iErrorID : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "out_vars": [
        ("bBusy", "BOOL", "忙"),
        ("bError", "BOOL", "出错"),
        ("iErrorID", "EIB_ERROR_CODE", "错误码"),
    ],
    "var_inout_block": None, "inout_vars": None,
    "brief": (
        "**`EIB_TIME_SEND` 的扩展版本**：发送 3 字节时间 telegram（DPT 10.001），支持 4 种模式 + 答查。\n\n"
        "**PDF 排版错警告（§4.2.5.29）**：PDF VAR_INPUT 代码块误抄了 `EIB_DATE_SEND_EX` 的 `wDay`/`wMonth`/`wYear`，"
        "但 §4.2.5.29 描述表（下页）写的是 `wHour`/`wMinute`/`wSecond`（时间字段）。"
        "**实际库**究竟用什么引脚名 PDF 自相矛盾；InfoSys 也不能明确这点。\n\n"
        "⚠️ **本文档逐字保留 PDF VAR_INPUT 代码块**（按 CLAUDE.md 硬规则 #1 不许补全/篡改）。"
        "实际工程中可能需要：① 查 .library 实际定义；② 用 `EIB_ALL_DATA_TYPES_SEND` 配置 3 byte 时间负载替代。"
    ),
    "behavior": SEND_EX_BEHAVIOR + (
        "\n\n**⚠️ PDF 排版错澄清（§4.2.5.29）**："
        "PDF 第 67 页 VAR_INPUT 代码块列出 `wDay : WORD; wMonth : WORD; wYear : WORD;`（看起来像日期参数）；"
        "第 68 页表格紧接着列出 `wHour / wMinute / wSecond`（时间参数）。"
        "本 FB 名字 `TIME_SEND_EX` 暗示是时间——但 VAR_INPUT 代码块逐字是日期字段。"
        "**正确语义无法仅凭 PDF 判定**——InfoSys 该 topic 页内容与 PDF 完全一致（同样的 PDF 排版错被搬运），"
        "未给出额外澄清。\n\n"
        "**工程建议**：① 若要可靠地用本 FB，先用 XAE 打开实际 .library 查 VAR_INPUT 实际命名；"
        "② 或退回用 `EIB_TIME_SEND`（节拍固定但定义清晰）；"
        "③ 或用 `EIB_ALL_DATA_TYPES_SEND` 手动构造 3 byte DPT 10.001 负载。"
    ),
    "errors": ERROR_TABLE_SEND_COMMON,
    "notes": SEND_EX_NOTES_COMMON + [
        "⚠️ **PDF + InfoSys VAR_INPUT 引脚名为 `wDay/wMonth/wYear` 但 FB 名是 TIME_SEND_EX**：PDF 排版错，实际库定义未确认。建议先用 `EIB_TIME_SEND`（固定 5 分钟节拍但定义清晰）。",
        "**实际语义需以 XAE 打开 .library 实查 VAR_INPUT 为准**——本文档逐字保留 PDF 写法。（工程经验补充）",
    ],
    "tcpou_scene": (
        "BMS 主时钟时间灵活间隔广播。⚠️ 由于 PDF 排版错，本 demo 按 PDF 逐字使用 wDay/wMonth/wYear 引脚名；"
        "实际语义需用 XAE 实查确认。"
    ),
    "tcpou_value": "灵活间隔的时间广播；但因 PDF 排版错优先建议 EIB_TIME_SEND",
    "tcpou_verify": (
        "登录 `bStart := TRUE`、`iMode := 1`、`CyclePolling := T#1M` → 每分钟看到 1/0/2 出 3 byte 帧。"
        "⚠️ 验证后请用 group monitor 解析帧负载，确认是日期还是时间。"
    ),
    "tcpou_decl": (
        "VAR\n"
        "    fbSendTimeEx       : EIB_TIME_SEND_EX;\n"
        "    stEibRec           : EIB_REC;\n"
        "    stGroup            : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 0, NUMBER := 2);\n"
        "    bSendStart         : BOOL;\n"
        "    iWorkMode          : INT := 1;\n"
        "    tCycle             : TIME := T#1M;\n"
        "    tMinSend           : TIME := T#500MS;\n"
        "    // ⚠️ PDF 排版错——VAR_INPUT 引脚是 wDay/wMonth/wYear，FB 名是 TIME_SEND_EX\n"
        "    wDay               : WORD := 14;       // 也许实际是 wHoure\n"
        "    wMonth             : WORD := 30;       // 也许实际是 wMinute\n"
        "    wYear              : WORD := 0;        // 也许实际是 wSecond\n"
        "    bResponseRead      : BOOL := TRUE;\n"
        "    bSendBusy          : BOOL;\n"
        "    bSendError         : BOOL;\n"
        "    iLastErrID         : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "// ⚠️ 按 PDF 引脚名调用；实际验证后需校对 group monitor 解出的字段含义\n"
        "fbSendTimeEx(\n"
        "    bStart         := bSendStart,\n"
        "    iMode          := iWorkMode,\n"
        "    CyclePolling   := tCycle,\n"
        "    MinSendTime    := tMinSend,\n"
        "    Group_Address  := stGroup,\n"
        "    wDay           := wDay,\n"
        "    wMonth         := wMonth,\n"
        "    wYear          := wYear,\n"
        "    str_Rec        := stEibRec,\n"
        "    bEnableReadReq := bResponseRead,\n"
        "    bBusy          => bSendBusy,\n"
        "    bError         => bSendError,\n"
        "    iErrorID       => iLastErrID\n"
        ");"
    ),
    "scene": "时间灵活间隔广播；但 PDF 排版错需 XAE 实查",
    "value": "灵活间隔；建议优先 EIB_TIME_SEND",
    "alternatives": [
        "`EIB_TIME_SEND`：5 分钟节拍但定义清晰，建议优先",
        "`EIB_ALL_DATA_TYPES_SEND`：手构 3 byte DPT 10 负载，完全可控",
        "本 _EX：仅在确认 .library 实际语义后才用",
    ],
    "related": "`EIB_TIME_SEND`、`EIB_TIME_REC`、`EIB_DATE_SEND_EX`",
    "example_preview": (
        "PROGRAM P_Demo_EIB_TIME_SEND_EX\n"
        "VAR\n"
        "    fb       : EIB_TIME_SEND_EX;\n"
        "    stEibRec : EIB_REC;\n"
        "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 0, NUMBER := 2);\n"
        "END_VAR\n"
        "// ⚠️ PDF 排版错：VAR_INPUT 是 wDay/wMonth/wYear 但 FB 名是 TIME_SEND_EX\n"
        "fb(bStart := TRUE, iMode := 1, CyclePolling := T#1M, MinSendTime := T#500MS,\n"
        "   Group_Address := stGroup, wDay := 14, wMonth := 30, wYear := 0,\n"
        "   str_Rec := stEibRec, bEnableReadReq := TRUE);"
    ),
})


# ============================================================================
# FUNCTIONS (2)
# ============================================================================

# F_CONV_2GROUP_TO_3GROUP
# Note: PDF section 4.2.6.1 shows VAR_INPUT with just `IN : EIB_GROUP_ADDR_2GROUP;`
# and the table label "Group_Address" (PDF mis-label - actual param name from VAR_INPUT block is IN).
ENTRIES.append({
    "name": "F_CONV_2GROUP_TO_3GROUP",
    "category": "functions",
    "category_label": "Functions",
    "infosys_id": "187789579",
    "pdf_section": "4.2.6.1",
    "type": "FUNCTION",
    "var_input_block": (
        "VAR_INPUT\n"
        "    IN : EIB_GROUP_ADDR_2GROUP;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("IN", "EIB_GROUP_ADDR_2GROUP", None,
         "2 级 EIB 组地址结构（`MAIN : BYTE` 0..15、`SUB_MAIN : WORD` 0..2048）。"
         "**PDF 描述表把名字标成 `Group_Address`**——以 VAR_INPUT 代码块的 `IN` 为准（实际 IEC 代码用 `IN`）"),
    ],
    "var_output_block": None,
    "out_vars": [],
    "var_inout_block": None, "inout_vars": None,
    "brief": (
        "**把 2 级 EIB 组地址转换为 3 级 EIB 组地址**。"
        "EIB 组地址有两种编址：① 3 级（MAIN/SUB_MAIN/NUMBER，对应新 KNX）；② 2 级（MAIN/SUB_MAIN，对应老 EIB）。"
        "本 FC 把 2 级形式转成等价的 3 级形式。\n\n"
        "**返回类型**：从 PDF/InfoSys 看本 FC 没有显式列出返回类型——按惯例返回 `EIB_GROUP_ADDR`。"
        "在 IEC 代码里用 `stOut := F_CONV_2GROUP_TO_3GROUP(IN := st2)` 形式调用。"
    ),
    "behavior": (
        "**调用即转换**：纯函数无副作用，每次调用立即返回转换后的 3 级地址。\n\n"
        "**2 级到 3 级映射规则**：2 级地址范围比 3 级大（SUB_MAIN 是 WORD 0..2048 vs NUMBER 是 BYTE 0..255），"
        "库内部按 EIB 标准把 `SUB_MAIN` 拆成 3 级的 (SUB_MAIN, NUMBER)：典型 `SUB_MAIN >> 8` → 新的 SUB_MAIN，`SUB_MAIN & 0xFF` → NUMBER。"
        "PDF 未明确算法，按 EIB/KNX 标准规范。\n\n"
        "**何时用 2 级地址**：与早期不支持 3 级的 KNX/EIB 楼宇设备对接时；"
        "现代项目几乎都用 3 级。本 FC 主要用于「老项目迁移」或「多代设备共存」场景。\n\n"
        "**与 KL6301 无关**：本 FC 是纯算法，不需要 EIB_REC、不依赖 KL6301 状态。可独立调用。"
    ),
    "errors": (
        "本 FC 是纯函数，**无错误码 / 无错误输出**。"
        "传入合法 `EIB_GROUP_ADDR_2GROUP` 总是返回有效的 `EIB_GROUP_ADDR`；"
        "极端情况（例 `SUB_MAIN > 2048`）按 EIB 规范截断或回绕。"
        "PDF + InfoSys 均未列出错码（⚠️ 待人工确认极端值行为）。"
    ),
    "notes": [
        "**纯函数无副作用**：每次调用都独立，可在任何上下文调用（不需要 KL6301、不需要 EIB_REC）。",
        "**PDF 描述表名 `Group_Address` 但 VAR_INPUT 名 `IN`**：以代码块的 `IN` 为准。",
        "**与 `F_CONV_3GROUP_TO_2GROUP` 配对**：反向转换是另一个 FC（§4.2.6.2）。",
        "**典型用法是兼容老 EIB 设备**：现代项目多用 3 级；本 FC 是迁移工具。",
    ],
    "tcpou_scene": (
        "工厂 BMS 系统升级——原老式 EIB 设备发 2 级组地址 `1/100`，新系统统一用 3 级。"
        "本 demo 把每条收到的 2 级地址转成 3 级以便统一处理。"
    ),
    "tcpou_value": "迁移工具：1 行调用替代手写位运算的地址转换",
    "tcpou_verify": (
        "改 `st2GroupAddr.MAIN := 1, .SUB_MAIN := 256` → `st3GroupAddr` 输出应是 (MAIN=1, SUB_MAIN=1, NUMBER=0)。"
    ),
    "tcpou_decl": (
        "VAR\n"
        "    st2GroupAddr : EIB_GROUP_ADDR_2GROUP := (MAIN := 1, SUB_MAIN := 256);\n"
        "    st3GroupAddr : EIB_GROUP_ADDR;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "// 纯函数调用——无需 KL6301 / EIB_REC，直接转换\n"
        "st3GroupAddr := F_CONV_2GROUP_TO_3GROUP(IN := st2GroupAddr);"
    ),
    "scene": "老 EIB 设备升级 / 多代设备共存 / 地址格式统一",
    "value": "替代手写位拆分；纯函数调用清晰",
    "alternatives": [
        "手写位运算：能做，但要懂 EIB 协议规范",
        "本 FC：迁移工具的**标准**选择",
    ],
    "related": (
        "`F_CONV_3GROUP_TO_2GROUP`（同库 §4.2.6.2，反向转换）、"
        "`EIB_GROUP_ADDR`（同库 §4.3.2.1，3 级地址结构）、"
        "`EIB_GROUP_ADDR_2GROUP`（同库 §4.3.2.2，2 级地址结构）"
    ),
    "example_preview": (
        "PROGRAM P_Demo_F_CONV_2GROUP_TO_3GROUP\n"
        "VAR\n"
        "    st2 : EIB_GROUP_ADDR_2GROUP := (MAIN := 1, SUB_MAIN := 256);\n"
        "    st3 : EIB_GROUP_ADDR;\n"
        "END_VAR\n"
        "st3 := F_CONV_2GROUP_TO_3GROUP(IN := st2);"
    ),
})


# F_CONV_3GROUP_TO_2GROUP
ENTRIES.append({
    "name": "F_CONV_3GROUP_TO_2GROUP",
    "category": "functions",
    "category_label": "Functions",
    "infosys_id": "187791115",
    "pdf_section": "4.2.6.2",
    "type": "FUNCTION",
    "var_input_block": (
        "VAR_INPUT\n"
        "    IN : EIB_GROUP_ADDR;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("IN", "EIB_GROUP_ADDR", None,
         "3 级 EIB 组地址结构（`MAIN : BYTE` 0..31、`SUB_MAIN : BYTE` 0..7、`NUMBER : BYTE` 0..255）"),
    ],
    "var_output_block": None,
    "out_vars": [],
    "var_inout_block": None, "inout_vars": None,
    "brief": (
        "**把 3 级 EIB 组地址转换为 2 级 EIB 组地址**——`F_CONV_2GROUP_TO_3GROUP` 的反向操作。\n\n"
        "**典型场景**：与老 EIB 设备对接时，业务代码内部用 3 级地址处理，"
        "下发到老设备前用本 FC 转成 2 级形式。"
    ),
    "behavior": (
        "**调用即转换**：纯函数无副作用，每次调用立即返回转换后的 2 级地址。\n\n"
        "**3 级到 2 级映射规则**：库内部按 EIB 标准把 3 级的 (SUB_MAIN, NUMBER) 两个 BYTE 合并成 2 级地址的 `SUB_MAIN : WORD`，"
        "典型实现 `new_SUB_MAIN := (SUB_MAIN << 8) | NUMBER`。`MAIN` 字段直接复制（注意 3 级 MAIN 范围 0..31 但 2 级 MAIN 范围只有 0..15）。\n\n"
        "**MAIN 值丢失风险**：3 级 `MAIN` 是 BYTE 范围 0..31，2 级 `MAIN` 是 BYTE 范围 0..15。"
        "如果 3 级 MAIN 值大于 15，截断到 2 级时会**丢失高位**——这是 EIB 协议本身的限制，不是本 FC 的 bug。"
        "业务上调用前要先确认 3 级 MAIN ≤ 15。\n\n"
        "**何时用 2 级地址**：与早期不支持 3 级地址的老 KNX/EIB 楼宇设备对接时。现代项目几乎都用 3 级；"
        "本 FC 主要用于「老设备兼容」或「多代设备共存」场景。\n\n"
        "**与 KL6301 无关**：纯算法函数，不需要 EIB_REC、不依赖 KL6301 状态。"
        "可在任何 PLC 任务、任何上下文调用。"
    ),
    "errors": (
        "本 FC 是纯函数，**无错误码 / 无错误输出**。"
        "PDF + InfoSys 均未列出错码。极端值（例 `MAIN > 15`）按 EIB 规范截断或回绕（⚠️ 待人工确认）。"
    ),
    "notes": [
        "**纯函数无副作用**：可在任何上下文调用。",
        "**MAIN 值丢精度**：3 级 MAIN 范围 0..31，2 级 MAIN 范围 0..15——值 > 15 会丢失高位。这是 EIB 协议本身的限制。",
        "**与 `F_CONV_2GROUP_TO_3GROUP` 配对**：反向。",
    ],
    "tcpou_scene": (
        "工厂 BMS 系统部分用 3 级地址，部分用老设备 2 级地址。"
        "本 demo 把内部 3 级地址转成 2 级后发到老设备。"
    ),
    "tcpou_value": "1 行调用替代位运算；老设备兼容",
    "tcpou_verify": (
        "改 `st3GroupAddr := (1, 1, 0)` → `st2GroupAddr` 应为 (MAIN=1, SUB_MAIN=256)。"
    ),
    "tcpou_decl": (
        "VAR\n"
        "    st3GroupAddr : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 1, NUMBER := 0);\n"
        "    st2GroupAddr : EIB_GROUP_ADDR_2GROUP;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "// 纯函数调用\n"
        "st2GroupAddr := F_CONV_3GROUP_TO_2GROUP(IN := st3GroupAddr);"
    ),
    "scene": "老 EIB 设备兼容 / 多代设备共存",
    "value": "替代手写位运算",
    "alternatives": [
        "手写位运算：要懂 EIB 协议",
        "本 FC：标准选择",
    ],
    "related": (
        "`F_CONV_2GROUP_TO_3GROUP`（同库 §4.2.6.1，反向）、"
        "`EIB_GROUP_ADDR` / `EIB_GROUP_ADDR_2GROUP`（同库 §4.3.2）"
    ),
    "example_preview": (
        "PROGRAM P_Demo_F_CONV_3GROUP_TO_2GROUP\n"
        "VAR\n"
        "    st3 : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 1, NUMBER := 0);\n"
        "    st2 : EIB_GROUP_ADDR_2GROUP;\n"
        "END_VAR\n"
        "st2 := F_CONV_3GROUP_TO_2GROUP(IN := st3);"
    ),
})


# ============================================================================
# Write all
# ============================================================================
def write_all():
    from _tc2_eib_gen import LIB
    count = 0
    for entry in ENTRIES:
        cat_dir = ROOT / LIB / entry["category"]
        cat_dir.mkdir(parents=True, exist_ok=True)
        doc_path = cat_dir / f"{entry['name']}.md"
        doc_path.write_text(md(entry))

        ex_path = ROOT / LIB / "examples" / f"P_Demo_{entry['name']}.TcPOU"
        ex_path.write_text(tcpou(entry))
        count += 1
    return count


if __name__ == "__main__":
    n = write_all()
    print(f"Generated {n} doc + tcpou pairs total (with first 17 + this batch)")
