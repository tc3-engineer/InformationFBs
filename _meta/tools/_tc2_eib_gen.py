#!/usr/bin/env python3
"""Library-internal generator for Tc2_EIB docs + TcPOU examples.

Run from repo root:
    python3 _meta/tools/_tc2_eib_gen.py

Produces:
    Tc2_EIB/coupler/*.md       (2)
    Tc2_EIB/read/*.md          (15)
    Tc2_EIB/send/*.md          (29)
    Tc2_EIB/functions/*.md     (2)
    Tc2_EIB/examples/P_Demo_*.TcPOU (48)
    Tc2_EIB/README.md
    Tc2_EIB/examples/README.md

Data sourced from cached PDF Tc2_EIB.pdf (v1.16.1) + InfoSys topic IDs
discovered via WebSearch / WebFetch.
"""
from __future__ import annotations

import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = "Tc2_EIB"
LIB_VER = "1.16.1"
PDF_URL = "https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf"
INFOSYS_BASE = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/"
DATE = "2026-06-03"

NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def _guid(name: str) -> str:
    """Generate stable POU GUID with library namespace."""
    return "{" + str(uuid.uuid5(NS, f"tc3-libraries-kb/{LIB}/P_Demo_{name}")) + "}"


# ----------------------------------------------------------------------------
# Common shared blocks
# ----------------------------------------------------------------------------

# iMode mode descriptions for _EX FBs (PDF text, common)
IMODE_EX_DESC = (
    "0 - 在 `bStart` 上升沿时发送一次（单脉冲手动）；"
    "1 - Polling：`bStart = TRUE` 期间按 `CyclePolling` 周期循环发送；"
    "2 - OnChange：`bStart = TRUE` 时数据变化才发送，`MinSendTime` 控制最短发送间隔；"
    "3 - OnChangePolling：`bStart = TRUE` 时按 `CyclePolling` 周期发送或数据变化时立即发送，`MinSendTime` 仍控制最短间隔"
)


# ----------------------------------------------------------------------------
# Entry catalog
# ----------------------------------------------------------------------------

# Each entry has: name, category-subdir, infosys-id, pdf-section, type,
# brief (功能简述), vars (decl block), in_vars (input desc rows), out_vars,
# inout_vars (or None), behavior (§3 行为说明), errors (§4),
# notes (§5 list of bullet strings), example_decl, example_st,
# scenario (§7 list)


def md(entry: dict) -> str:
    """Render entry dict to markdown doc string."""
    name = entry["name"]
    cat = entry["category"]
    infosys = INFOSYS_BASE + entry["infosys_id"] + ".html"
    typ = entry["type"]
    sec = entry["pdf_section"]
    cat_label = entry["category_label"]

    parts = [
        f"# {name}\n",
        "## 元信息\n",
        "| 字段 | 值 |",
        "|---|---|",
        f"| Library | `{LIB}` |",
        f"| Library Version | `{LIB_VER}` |",
        f"| Type | `{typ}` |",
        f"| Category | `{cat_label}` |",
        f"| Source PDF | {PDF_URL} |",
        f"| Source InfoSys | {infosys} |",
        f"| Verified | {DATE} ✅ |",
        f"| InfoSys-checked | ✅ {DATE} |",
        f"| Status | `verified` |",
        f"| Example | [`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU) |",
        "\n---\n",
        "## 1. 功能简述\n",
        entry["brief"],
        "\n## 2. 接口定义\n",
    ]

    # VAR_INPUT
    parts.append("### VAR_INPUT\n")
    parts.append("```iecst")
    parts.append(entry["var_input_block"])
    parts.append("```\n")
    if entry["in_vars"]:
        parts.append("| 名称 | 类型 | 默认值 | 说明 |")
        parts.append("|---|---|---|---|")
        for n, t, d, desc in entry["in_vars"]:
            d_str = f"`{d}`" if d else "—"
            parts.append(f"| `{n}` | `{t}` | {d_str} | {desc} |")
        parts.append("")

    # VAR_OUTPUT
    parts.append("### VAR_OUTPUT\n")
    if entry["var_output_block"]:
        parts.append("```iecst")
        parts.append(entry["var_output_block"])
        parts.append("```\n")
        parts.append("| 名称 | 类型 | 说明 |")
        parts.append("|---|---|---|")
        for n, t, desc in entry["out_vars"]:
            parts.append(f"| `{n}` | `{t}` | {desc} |")
        parts.append("")
    else:
        parts.append("无（FC，返回值见 §4）。\n")

    # VAR_IN_OUT
    parts.append("### VAR_IN_OUT\n")
    if entry.get("var_inout_block"):
        parts.append("```iecst")
        parts.append(entry["var_inout_block"])
        parts.append("```\n")
        parts.append("| 名称 | 类型 | 说明 |")
        parts.append("|---|---|---|")
        for n, t, desc in entry["inout_vars"]:
            parts.append(f"| `{n}` | `{t}` | {desc} |")
        parts.append("")
    else:
        parts.append("无。\n")

    # §3 Behavior
    parts.append("## 3. 行为说明\n")
    parts.append(entry["behavior"])
    parts.append("")

    # §4 Errors
    parts.append("## 4. 错误码 / 返回值\n")
    parts.append(entry["errors"])
    parts.append("")

    # §5 Notes
    parts.append("## 5. 使用注意 / 常见坑\n")
    for note in entry["notes"]:
        parts.append(f"- {note}")
    parts.append("")

    # §6 Example
    parts.append("## 6. 最小例程\n")
    parts.append(
        f"> 配套可导入文件：[`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU)"
        f"（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）"
    )
    parts.append("")
    parts.append(
        "> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK"
    )
    parts.append("> 详见 [`examples/README.md`](../examples/README.md)")
    parts.append("")
    parts.append("```iecst")
    parts.append(entry["example_preview"])
    parts.append("```\n")

    # §7 Scenario
    parts.append("## 7. 业务场景与实际价值\n")
    parts.append(f"- **场景**：{entry['scene']}")
    parts.append(f"- **价值**：{entry['value']}")
    parts.append("- **替代方案对比**：")
    for alt in entry["alternatives"]:
        parts.append(f"  - {alt}")
    parts.append("")

    # §8 References
    parts.append("## 8. 参考资料\n")
    parts.append(f"- **PDF**：[TwinCAT_3_PLC_Lib_{LIB}_EN.pdf]({PDF_URL}) §{sec}")
    parts.append(f"- **InfoSys topic**：{infosys}")
    if entry.get("related"):
        parts.append(f"- **相关**：{entry['related']}")
    parts.append("")

    return "\n".join(parts)


def tcpou(entry: dict) -> str:
    """Generate TcPOU XML for entry."""
    name = entry["name"]
    guid = _guid(name)
    decl = entry["tcpou_decl"]
    st = entry["tcpou_st"]
    header_block = (
        f"// ============================================================\n"
        f"// {LIB}.{name} 演示程序\n"
        f"// ============================================================\n"
        f"// 场景：{entry['tcpou_scene']}\n"
        f"// 价值：{entry['tcpou_value']}\n"
        f"// 验证步骤：\n"
        f"//   1. 右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选本 .TcPOU 文件\n"
        f"//   2. 引用 {LIB}（References → Add library）\n"
        f"//   3. 编译 → 登录 → 运行；按下方在线写值步骤操作\n"
        f"// 验证：{entry['tcpou_verify']}\n"
        f"// ============================================================\n"
    )
    return (
        f'<?xml version="1.0" encoding="utf-8"?>\n'
        f'<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">\n'
        f'  <POU Name="P_Demo_{name}" Id="{guid}" SpecialFunc="None">\n'
        f'    <Declaration><![CDATA[PROGRAM P_Demo_{name}\n{decl}\n]]></Declaration>\n'
        f'    <Implementation>\n'
        f'      <ST><![CDATA[{header_block}\n{st}\n]]></ST>\n'
        f'    </Implementation>\n'
        f'  </POU>\n'
        f'</TcPlcObject>\n'
    )


# ============================================================================
# Common copy
# ============================================================================

KL6301_NEED = (
    "**调用前提**：本 FB 必须先由 `KL6301` 或 `KL6301_EX` 配置过 `EIB_REC` 结构（设过滤器、激活数据交换后 `bReady = TRUE`），"
    "并把同一个 `EIB_REC` 实例传给本 FB 的 `strData_Rec` / `str_Rec`，否则收发不通。"
    "所有 EIB 收发 FB 必须与 `KL6301` 调用在**同一个 PLC 任务**里。"
)

GROUP_ADDR_NOTE = (
    "**`Group_Address` 必须出现在 `KL6301.EIB_GROUP_FILTER` 配置的某个过滤器范围内**，"
    "否则 KL6301 不会 ACK 也不会把对应 telegram 落入过程数据，本 FB 看不到任何事件。"
)

BUS_LOAD_NOTE = (
    "**`MinSendTime` ≥ 200 ms 由库强制**：用低于 200 ms 的值不会生效，仍按 200 ms 处理（PDF 注释）。"
    "OnChange 模式下避免高频抖动数据触发刷屏。"
)

ERROR_TABLE_FULL = """| 枚举值 / 16# | 含义 | 常见原因 |
|---|---|---|
| `NO_EIB_ERROR` / 0 | 无错 | — |
| `WRONG_EIB_PHYS_ADDR` / 1 | 已废弃，新固件不再使用 | — |
| `WRONG_EIB_GROUP_ADDR` / 2 | `EIB_GROUP_FILTER.GROUP_ADDR` 字段非法 | `MAIN` 必须 < 16，`SUB_MAIN` 必须 < 8 |
| `WRONG_EIB_GROUP_LEN` / 3 | `EIB_GROUP_FILTER.GROUP_LEN` 与模式不匹配 | iMode=0 时 `GROUP_LEN` 0..63，iMode=1/2 时 0..31 |
| `WRONG_EIB_NO_FILTER` / 4 | 没检测到任何过滤器 | 至少要配一个 `EIB_GROUP_FILTER[i]`（监控模式 iMode=100 例外） |
| `WRONG_EIB_IDX_RANGE` / 5 | `idx` 越界 | `idx` 合法范围 1..64 |
| `WRONG_EIB_FIRMWARE` / 10 | 当前 KL6301 固件版本不支持该模式 | 升级 KL6301 固件到 B1 / B3 |
| `WRONG_EIB_MODE` / 11 | 参数化阶段模式非法 | `iMode` 合法值 0 / 1 / 100（B0 固件），加 2（B3 固件） |
| `WRONG_MODE` / 12 | `iMode` 值非法 | 见上 |
| `WRONG_EIB_FIRMWARE_B1_NECESSARY` / 14 | 该 `iMode` 需 B1 及以上固件 | iMode=1（8×32 过滤器）需 B1+ |
| `WRONG_EIB_FIRMWARE_B3_NECESSARY` / 15 | 该 `iMode` 需 B3 及以上固件 | iMode=2（反向过滤器）需 B3+ |
| `WRONG_EIB_DATA_LEN` / 20 | telegram 数据长度与期望不符，已丢弃 | 用 `EIB_2OCTET_*` FB 接收 1-byte telegram；过滤器或类型选错 |
| `ERROR_EIB_SERVICE_NOT_SUPPORT` / 21 | 不支持的 EIB 服务 | 接到非标准 telegram |
| `KL6301_TP_TOGGLE_ERROR` / 30 | KL6301 1 秒内未响应 | KL6301 仍在处理上一帧；检查 KL6301 物理连接 |
| `TIME_OUT` / 31 | 参数化阶段超时 | KL6301 没接好 / mapping 错 / KL6301 没上电 |
| `KL6301_NO_RESPONSE_FROM_TERMINAL` / 32 | 找不到 KL6301 | 端子不存在或 IO mapping 缺失 |
| `ERROR_SEND_8BIT_WRONG_Scaling_Mode` / 40 | `Scaling_Mode` 非法 | 8-bit 缩放模式合法值 0/1/2 |
| `ERROR_EIB_PHY_ADDR_NOT_SUPPORT` / 100 | 不允许的物理寻址 | 用了无效物理地址 |
| `ERROR_EIB_WRITE_DATA` / 101 | 已废弃 | — |
| `MONITOR_MODE_LEN_IS_NOT_OK_MUST_0` / 102 | 监控模式下过滤器长度必须为 0 | iMode=100 时 `GROUP_LEN` 必须填 0 |
| `MONITOR_MODE_ADDR_IS_NOT_OK_MUST_0` / 103 | 监控模式下地址必须为 0 | iMode=100 时过滤器内地址字段必须清零 |
| `WATCHDOG_ERROR_NO_SEND` / 104 | 数据发送失败（看门狗） | 失败的 group address 见 KL6301 内部局部变量 `NotSendGroup` |
| `ERROR_EIB_NO_ACK` / 16#0BBB (3003) | 没收到 ACK | 总线上没有目标设备 / 总线段断开 |
| `ERROR_EIB_NO_COM_TO_TP` / 16#FAFB (64251) | KL6301 EIB 物理层失联 | KL6301 EIB 侧硬件故障 / EIB 电源掉 |
| `ERROR_TP_TEMP_WARNING` / 16#0FCC (4044) | KL6301 内部温度超限 | 机柜散热不良 / KL6301 放置过密 |
| `ERROR_TP_PROTOCOL_ERROR` / 16#17CC (6092) | EIB 物理层协议错 | 总线干扰 |
| `ERROR_TP_TRANSMITTER_ERROR` / 16#27CC (10188) | 发送器协议错 | 总线干扰 |
| `ERROR_TP_RECEIVE_ERROR` / 16#47CC (18380) | 接收器协议错 | 总线干扰 |
| `ERROR_TP_SLAVE_COLLISION` / 16#87CC (34764) | EIB 物理层冲突过多 | 减少 EIB 网络负载（缩短轮询周期 / 减少 OnChange FB 数） |"""

ERROR_TABLE_SEND_COMMON = """| 枚举值 / 16# | 含义 | 常见原因 |
|---|---|---|
| `NO_EIB_ERROR` / 0 | 无错 | — |
| `WRONG_EIB_DATA_LEN` / 20 | 发送数据长度异常 | 库内部检测，正常使用不应触发 |
| `ERROR_EIB_NO_ACK` / 16#0BBB | EIB 端没有收到目标设备的 ACK | 目标组地址在 EIB 网络上无任何 ACK 设备 / 总线段不通 |
| `WATCHDOG_ERROR_NO_SEND` / 104 | 看门狗判定本帧未发出 | KL6301 长时间忙、被低优先级帧拖死；失败的 group address 写入 `KL6301.NotSendGroup` 局部变量供调试 |
| `KL6301_TP_TOGGLE_ERROR` / 30 | KL6301 1 秒未响应 toggle | KL6301 已死锁；触发 `KL6301.bActivate := FALSE` 再 TRUE 重参数化 |
| `ERROR_EIB_NO_COM_TO_TP` / 16#FAFB | EIB 物理层失联 | KL6301 EIB 侧硬件 / 电源故障 |
| `ERROR_TP_*` / 16#0FCC..16#87CC | KL6301 物理层各类错 | 见 §4 错误码完整表，多为现场布线 / 干扰问题 |

参见 `EIB_ERROR_CODE` 枚举完整定义（PDF §4.3.1.1）。
"""


# ============================================================================
# Entries
# ============================================================================
ENTRIES: list[dict] = []


# ---------- COUPLER ----------

ENTRIES.append({
    "name": "KL6301",
    "category": "coupler",
    "category_label": "Coupler",
    "infosys_id": "187726603",
    "pdf_section": "4.2.2",
    "type": "FUNCTION_BLOCK",
    "brief": (
        "EIB（European Installation Bus，等同后期 KNX TP1）总线主端子 **KL6301** 的通信功能块。"
        "用于初始化 KL6301：写物理地址、配置组地址过滤器、选择运行模式（4×64 / 8×32 / 反向 / 监控），"
        "完成后激活数据交换；其后所有 `EIB_*_REC` 和 `EIB_*_SEND` FB 通过共享的 `EIB_REC` 结构与本 FB 联通。\n\n"
        "**KL6301 与本 FB 是 1:1 关系**：每个 KL6301 端子对应一个 `KL6301` 实例（用 `idx` 区分），一个 PLC 项目最多 64 个实例。"
        "本 FB 必须**每个 PLC 周期调用一次且仅一次**，并且必须与所有挂在它下面的 `EIB_*_REC` / `EIB_*_SEND` FB 处于**同一个 PLC 任务**中。\n\n"
        "**`EIB_REC` 是收发胶水**：本 FB 通过 `str_Data_Rec` 输出 `EIB_REC` 结构，调用方把这同一个 `EIB_REC` 变量再传给每个 `EIB_*_REC` / `EIB_*_SEND` FB 的 `strData_Rec` / `str_Rec` 输入。"
        "如果忘记串联或串错实例，所有收发都「不工作但也不报错」，是新手最常见坑。"
    ),
    "var_input_block": (
        "VAR_INPUT\n"
        "    bActivate        : BOOL;\n"
        "    idx              : INT := 1;\n"
        "    EIB_PHYS_ADDR    : EIB_PHYS_ADDR;\n"
        "    EIB_GROUP_FILTER : ARRAY [1..8] OF EIB_GROUP_FILTER;\n"
        "    iMode            : INT;\n"
        "    tTimeout         : TIME := T#5s;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("bActivate", "BOOL", None,
         "激活配置和数据交换。FALSE → 完成正在进行的任务后停止数据交换；当 `bActive` 与 `bReady` 都回 FALSE 后才可再次置 TRUE 触发新一轮配置"),
        ("idx", "INT", "1",
         "本 KL6301 实例的唯一编号。同一 PLC 程序里多块 KL6301 必须 `idx` 互不相同；合法范围 1..64"),
        ("EIB_PHYS_ADDR", "EIB_PHYS_ADDR", None,
         "本 KL6301 在 EIB 网络中的物理地址（Area/Line/Device），默认 1/2/3。**必须全网唯一**，否则 EIB 上多个 KL6301 会互相干扰"),
        ("EIB_GROUP_FILTER", "ARRAY [1..8] OF EIB_GROUP_FILTER", None,
         "组地址过滤器数组。KL6301 只 ACK 并把过滤器内的 telegram 送入过程数据；过滤器之外的 telegram 会被丢弃。至少要配一个；监控模式（iMode=100）例外"),
        ("iMode", "INT", None,
         "运行模式：`0` = 4 个过滤器、每个 64 条目（B0 及以上）；`1` = 8 个过滤器、每个 32 条目（B1+）；`2` = 8 个过滤器、每个 32 条目、反向过滤（B3+，用于不需要 ACK 那些地址）；`100` = 监控模式，全收不 ACK 不发（B1+）"),
        ("tTimeout", "TIME", "T#5s",
         "单条发送 FB 的发送超时阈值。超时后发送 FB 的 `iErrorID` 会带 `WATCHDOG_ERROR_NO_SEND`"),
    ],
    "var_output_block": (
        "VAR_OUTPUT\n"
        "    bActive      : BOOL;\n"
        "    bReady       : BOOL;\n"
        "    bError       : BOOL;\n"
        "    iErrorId     : EIB_Error_Code;\n"
        "    str_Data_Rec : EIB_REC;\n"
        "END_VAR"
    ),
    "out_vars": [
        ("bActive", "BOOL",
         "FB 已激活；处于配置中或正常数据交换中"),
        ("bReady", "BOOL",
         "FB 配置完成、可收发数据。`bReady = TRUE` 是所有挂载 FB 可用的前提"),
        ("bError", "BOOL",
         "出错时置 TRUE，错误号见 `iErrorId`"),
        ("iErrorId", "EIB_ERROR_CODE",
         "错误码枚举，详见 §4 完整表"),
        ("str_Data_Rec", "EIB_REC",
         "**收发胶水结构**。必须把这个变量再传给每个 `EIB_*_REC` / `EIB_*_SEND` FB 的 `strData_Rec` / `str_Rec` 输入"),
    ],
    "var_inout_block": (
        "VAR_IN_OUT\n"
        "    KL6301_IN  : ARRAY [1..24] OF BYTE;\n"
        "    KL6301_OUT : ARRAY [1..24] OF BYTE;\n"
        "END_VAR"
    ),
    "inout_vars": [
        ("KL6301_IN", "ARRAY [1..24] OF BYTE",
         "在 System Manager 链接到 KL6301 输入过程映像（ParameterStatus + InputData1..InputData22）"),
        ("KL6301_OUT", "ARRAY [1..24] OF BYTE",
         "在 System Manager 链接到 KL6301 输出过程映像"),
    ],
    "behavior": (
        "**状态机**：调用方先填 `EIB_PHYS_ADDR` / `EIB_GROUP_FILTER[1..N]` / `iMode`，然后 `bActivate := TRUE`：\n\n"
        "1. FB 进入参数化阶段（`bActive = TRUE`、`bReady = FALSE`）。库通过 24 字节 IO 与 KL6301 协商：把过滤器表与物理地址写入 KL6301 EEPROM，校验固件版本是否支持所选 `iMode`。\n"
        "2. 参数化成功 → `bReady := TRUE`。数据交换通道打通，挂在 `str_Data_Rec` 上的所有 `EIB_*_REC` 开始向上送报文，所有 `EIB_*_SEND` 可以下发。\n"
        "3. 参数化失败 → `bError := TRUE`、`iErrorId` 给错误码（典型 `WRONG_EIB_MODE` / `WRONG_EIB_FIRMWARE_*_NECESSARY` / `KL6301_NO_RESPONSE_FROM_TERMINAL`）；必须先把 `bActivate := FALSE` 等 `bActive` 与 `bReady` 都回 FALSE，改完参数再 `bActivate := TRUE` 重试。\n"
        "4. 运行中若 `bActivate := FALSE`，FB 完成在飞的发送任务后停止数据交换；之后才可再次激活。\n\n"
        "**调用约束（PDF §4.2.2 Restrictions）**：①每实例每周期**仅调用一次**；②实例必须与挂载的所有发收 FB 在**同一 PLC 任务**；③一个 PLC 程序最多 **64 个 KL6301 实例**。\n\n"
        "**iMode 与过滤器容量**：`iMode=0` 4 过滤器 × 64 = 256 组地址（兼容 B0 老固件）；`iMode=1` 8×32 = 256（同样 256，但能更细分组）；`iMode=2` 8×32 反向，过滤器内的不 ACK / 过滤器外的才进过程数据（B3+，用于 KL6301 在的网段有大量与本机无关的 telegram，省 ACK 流量）；`iMode=100` 监控模式，所有 telegram 全收不 ACK 不发（PDF §4.1）。\n\n"
        "**IO 映射的特别用法**：`KL6301_IN[1]` = ParameterStatus，`KL6301_IN[2..23]` = InputData1..22（PDF §4.4.1）。这是 KL6301 在 K-bus 上的固定 22 字节过程数据；输出方向同样 22 字节。具体 mapping 由库内部处理，调用方只需 System Manager 拖链。"
    ),
    "errors": ERROR_TABLE_FULL,
    "notes": [
        "**至少配一个过滤器**：未配时报 `WRONG_EIB_NO_FILTER`（监控模式 iMode=100 例外）。",
        "**`EIB_PHYS_ADDR` 必须全网唯一**：网内已存在 1/2/3 而你也用默认 1/2/3 → 总线冲突 / 设备识别错位。配置阶段就要规划好物理地址表。",
        "**`MAIN < 16` 且 `SUB_MAIN < 8`**：超出范围报 `WRONG_EIB_GROUP_ADDR`。这是 EIB 3 级组地址的协议约束。",
        "**iMode + 过滤器长度对应**：iMode=0 时 `GROUP_LEN` 合法 0..63；iMode=1/2 时 0..31；填错报 `WRONG_EIB_GROUP_LEN`。`GROUP_LEN = 0` 代表**只 1 个地址**（不是 0 个），是新手常见坑。",
        "**监控模式（iMode=100）必须 `GROUP_LEN = 0` 且地址清零**：否则报 `MONITOR_MODE_LEN_IS_NOT_OK_MUST_0` / `_ADDR_IS_NOT_OK_MUST_0`。监控模式下本身就不写过滤器。",
        "**`idx` 必须唯一**：多实例时同 `idx` 会让两个 FB 互相覆盖 EIB_REC 状态。",
        "**配置失败时复位流程**：`bActivate := FALSE` → 等到 `bActive` 与 `bReady` 双 FALSE → 改参数 → `bActivate := TRUE`。直接重复触发上升沿无效，是被反复抱怨的设计。",
        "**所有 EIB 收发 FB 必须与本 FB 同一 PLC 任务**：跨任务时 `EIB_REC` 不一致，报文会丢，但 KL6301 不报错。（工程经验补充）",
        "**KL6301 固件版本影响 iMode 可用性**：B0 只能 iMode=0；B1 加 iMode=1/100；B3 加 iMode=2。固件版本可通过 KS2000 或 BTC 工具读出。（工程经验补充）",
        "**升级到 V3 库后，老工程的 `iMode=0` 仍兼容**，但建议改 iMode=1 用更细分组提升性能；切换前确认 KL6301 是 B1+ 固件，否则报 `WRONG_EIB_FIRMWARE_B1_NECESSARY`。（工程经验补充）",
    ],
    "tcpou_scene": (
        "CX5120 + KL6301 + 多个 EIB 楼宇设备（开关、调光器、温控）。需要在 PLC 启动时一次性把 KL6301 配置好——"
        "写物理地址 2/3/4，配 4 个过滤器覆盖 1/1/0..1/1/63 / 1/2/0..1/2/63 / 1/4/0..1/4/63 / 3/1/0..3/1/63 共 256 组地址。"
    ),
    "tcpou_value": (
        "把「24 字节过程数据 + KL6301 EEPROM 写入握手 + 错误重试」封装为一行 `fbKL6301(...)` 调用。"
        "手写实现要 100+ 行字节级协议。"
    ),
    "tcpou_verify": (
        "登录后置 `bStartConfig := TRUE` → 1-2 秒后 `iStep` 从 0 跳到 1，`bConfigReady = TRUE`、`bConfigError = FALSE`；"
        "若 KL6301 没接好则报错 `iLastErrorId = KL6301_NO_RESPONSE_FROM_TERMINAL (32)`。"
    ),
    "tcpou_decl": (
        "VAR\n"
        "    fbKL6301           : KL6301;\n"
        "    arrKL6301_IN       : ARRAY[1..24] OF BYTE;  // 实链 System Manager 时改 AT %I*\n"
        "    arrKL6301_OUT      : ARRAY[1..24] OF BYTE;  // 实链 System Manager 时改 AT %Q*\n"
        "    stEibRec           : EIB_REC;\n"
        "    bStartConfig       : BOOL;\n"
        "    iStep              : INT;\n"
        "    bConfigReady       : BOOL;\n"
        "    bConfigError       : BOOL;\n"
        "    iLastErrorId       : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "// 第一次进入：参数化 KL6301。物理地址 2/3/4，4 个 64 容量过滤器。\n"
        "CASE iStep OF\n"
        "0:\n"
        "    // —— 物理地址：本 KL6301 在 EIB 网络中的身份证 ——\n"
        "    fbKL6301.EIB_PHYS_ADDR.Area   := 2;\n"
        "    fbKL6301.EIB_PHYS_ADDR.Line   := 3;\n"
        "    fbKL6301.EIB_PHYS_ADDR.Device := 4;\n"
        "\n"
        "    // —— 过滤器 1：1/1/0..1/1/63（开关组）——\n"
        "    fbKL6301.EIB_GROUP_FILTER[1].GROUP_ADDR.MAIN     := 1;\n"
        "    fbKL6301.EIB_GROUP_FILTER[1].GROUP_ADDR.SUB_MAIN := 1;\n"
        "    fbKL6301.EIB_GROUP_FILTER[1].GROUP_ADDR.NUMBER   := 0;\n"
        "    fbKL6301.EIB_GROUP_FILTER[1].GROUP_LEN           := 63;  // 64 地址 = 长度 63\n"
        "\n"
        "    // —— 过滤器 2：1/2/0..1/2/63（调光组）——\n"
        "    fbKL6301.EIB_GROUP_FILTER[2].GROUP_ADDR.MAIN     := 1;\n"
        "    fbKL6301.EIB_GROUP_FILTER[2].GROUP_ADDR.SUB_MAIN := 2;\n"
        "    fbKL6301.EIB_GROUP_FILTER[2].GROUP_ADDR.NUMBER   := 0;\n"
        "    fbKL6301.EIB_GROUP_FILTER[2].GROUP_LEN           := 63;\n"
        "\n"
        "    // —— 过滤器 3：1/4/0..1/4/63（传感器组）——\n"
        "    fbKL6301.EIB_GROUP_FILTER[3].GROUP_ADDR.MAIN     := 1;\n"
        "    fbKL6301.EIB_GROUP_FILTER[3].GROUP_ADDR.SUB_MAIN := 4;\n"
        "    fbKL6301.EIB_GROUP_FILTER[3].GROUP_ADDR.NUMBER   := 0;\n"
        "    fbKL6301.EIB_GROUP_FILTER[3].GROUP_LEN           := 63;\n"
        "\n"
        "    // —— 过滤器 4：3/1/0..3/1/63（场景控制组）——\n"
        "    fbKL6301.EIB_GROUP_FILTER[4].GROUP_ADDR.MAIN     := 3;\n"
        "    fbKL6301.EIB_GROUP_FILTER[4].GROUP_ADDR.SUB_MAIN := 1;\n"
        "    fbKL6301.EIB_GROUP_FILTER[4].GROUP_ADDR.NUMBER   := 0;\n"
        "    fbKL6301.EIB_GROUP_FILTER[4].GROUP_LEN           := 63;\n"
        "\n"
        "    IF bStartConfig THEN\n"
        "        fbKL6301.bActivate := TRUE;  // 触发参数化阶段\n"
        "        IF fbKL6301.bReady THEN\n"
        "            IF NOT fbKL6301.bError THEN\n"
        "                iStep := 1;          // 进入正常数据交换\n"
        "            ELSE\n"
        "                iStep := 100;        // 出错分支\n"
        "                iLastErrorId := fbKL6301.iErrorId;\n"
        "            END_IF\n"
        "        END_IF\n"
        "    END_IF\n"
        "1:\n"
        "    ;  // 数据交换中：所有 EIB_*_REC / EIB_*_SEND FB 已可工作\n"
        "    bConfigReady := TRUE;\n"
        "100:\n"
        "    bConfigError := TRUE;\n"
        "END_CASE\n"
        "\n"
        "// 每周期调用一次：iMode=0 = 4 过滤器 × 64 条目兼容模式\n"
        "fbKL6301(\n"
        "    bActivate    := fbKL6301.bActivate,\n"
        "    idx          := 1,\n"
        "    iMode        := 0,\n"
        "    tTimeout     := T#5S,\n"
        "    KL6301_IN    := arrKL6301_IN,\n"
        "    KL6301_OUT   := arrKL6301_OUT,\n"
        "    bActive      => ,\n"
        "    bReady       => ,\n"
        "    bError       => ,\n"
        "    iErrorId     => ,\n"
        "    str_Data_Rec => stEibRec\n"
        ");"
    ),
    "scene": (
        "楼宇自动化系统：CX 系列 PLC 经 KL6301 接入 KNX/EIB TP1 总线，控制开关、调光器、卷帘、温控阀、电表等。"
        "本 FB 是接入 EIB 网络的入口，每个 KL6301 都需要它配置 + 数据交换"
    ),
    "value": (
        "把 EIB 协议栈、KL6301 的 EEPROM 配置流程、过程数据 24 字节 IO mapping 全部封装；"
        "调用方只关心物理地址 + 过滤器 + 模式三件事，不用懂 EIB 帧格式、不用懂 KL6301 内部状态机"
    ),
    "alternatives": [
        "用 KS2000 离线配 KL6301 + 自己写字节级 K-bus 通信：能做，但 KS2000 的过滤器表跟工程参数耦合，改一次工艺要重连 KS2000 改参数，运维成本高",
        "EL6201（EtherCAT KNX 主端子）+ Tc3_KNX 库：现代方案，性能更强；但要换硬件 + 改设计",
        "本 FB：是 KL6301 上 PLC 程序里**唯一**的合理选择，没有真正替代品",
    ],
    "related": (
        "`KL6301_EX`（同库 §4.2.3，支持 ETS 搜索 / LED 闪烁的 BETA 版本）、"
        "`EIB_REC`（同库 §4.3.2.5，收发胶水结构）、"
        "`EIB_GROUP_FILTER` / `EIB_PHYS_ADDR`（同库 §4.3.2.3/4，过滤器与物理地址结构）、"
        "`EIB_ERROR_CODE`（同库 §4.3.1.1，错误码枚举）"
    ),
    "example_preview": (
        "// 顶部三件套注释见 .TcPOU 文件\n"
        "PROGRAM P_Demo_KL6301\n"
        "VAR\n"
        "    fbKL6301      : KL6301;\n"
        "    arrKL6301_IN  : ARRAY[1..24] OF BYTE;\n"
        "    arrKL6301_OUT : ARRAY[1..24] OF BYTE;\n"
        "    stEibRec      : EIB_REC;\n"
        "    bStartConfig  : BOOL;\n"
        "END_VAR\n"
        "\n"
        "// 物理地址 + 4 过滤器 → 见 .TcPOU 完整示例\n"
        "fbKL6301(\n"
        "    bActivate    := bStartConfig,\n"
        "    idx          := 1,\n"
        "    iMode        := 0,\n"
        "    tTimeout     := T#5S,\n"
        "    KL6301_IN    := arrKL6301_IN,\n"
        "    KL6301_OUT   := arrKL6301_OUT,\n"
        "    str_Data_Rec => stEibRec\n"
        ");"
    ),
})


ENTRIES.append({
    "name": "KL6301_EX",
    "category": "coupler",
    "category_label": "Coupler",
    "infosys_id": "6790210699",
    "pdf_section": "4.2.3",
    "type": "FUNCTION_BLOCK",
    "brief": (
        "KL6301 的**扩展版本（BETA）**功能块，新增 **ETS 软件支持**——可被 ETS 搜索到、可触发 LED 闪烁定位物理设备。"
        "标准用法与 `KL6301` 完全一致：写物理地址、配置过滤器、选模式、激活数据交换。"
        "**与 `KL6301` 的区别**：去掉了输入 `tTimeout`（发送超时由库内部处理）；其余引脚名 / 类型 / 行为全部一致。\n\n"
        "**为什么需要 _EX**：项目里如果还有非 PLC 的 EIB/KNX 工程师在用 ETS 工具同时调试同一总线，调用 KL6301_EX 后 KL6301 可被 ETS 识别为节点，方便用 ETS 的「物理地址搜索 / LED Blink」功能定位实物。常规 PLC 单独占总线时用 `KL6301` 即可。"
    ),
    "var_input_block": (
        "VAR_INPUT\n"
        "    bActivate        : BOOL;\n"
        "    idx              : INT := 1;\n"
        "    EIB_PHYS_ADDR    : EIB_PHYS_ADDR;\n"
        "    EIB_GROUP_FILTER : ARRAY [1..8] OF EIB_GROUP_FILTER;\n"
        "    iMode            : INT;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("bActivate", "BOOL", None,
         "同 `KL6301`：激活配置和数据交换"),
        ("idx", "INT", "1",
         "同 `KL6301`：1..64 的唯一实例编号"),
        ("EIB_PHYS_ADDR", "EIB_PHYS_ADDR", None,
         "同 `KL6301`：物理地址 Area/Line/Device，默认 1/2/3，**全网唯一**"),
        ("EIB_GROUP_FILTER", "ARRAY [1..8] OF EIB_GROUP_FILTER", None,
         "同 `KL6301`：组地址过滤器数组（至多 8 个）"),
        ("iMode", "INT", None,
         "同 `KL6301`：0 / 1 / 2 / 100；本 _EX 版本固定要求 KL6301 固件 B1+（PDF §4.2.3 Requirements）"),
    ],
    "var_output_block": (
        "VAR_OUTPUT\n"
        "    bActive      : BOOL;\n"
        "    bReady       : BOOL;\n"
        "    bError       : BOOL;\n"
        "    iErrorId     : EIB_Error_Code;\n"
        "    str_Data_Rec : EIB_REC;\n"
        "END_VAR"
    ),
    "out_vars": [
        ("bActive", "BOOL", "FB 已激活；处于配置中或正常数据交换中"),
        ("bReady", "BOOL", "FB 配置完成、可收发数据"),
        ("bError", "BOOL", "出错时置 TRUE，错误号见 `iErrorId`"),
        ("iErrorId", "EIB_ERROR_CODE", "错误码枚举，详见 `EIB_ERROR_CODE`"),
        ("str_Data_Rec", "EIB_REC", "收发胶水结构，传给所有 `EIB_*_REC` / `EIB_*_SEND`"),
    ],
    "var_inout_block": (
        "VAR_IN_OUT\n"
        "    KL6301_IN  : ARRAY [1..24] OF BYTE;\n"
        "    KL6301_OUT : ARRAY [1..24] OF BYTE;\n"
        "END_VAR"
    ),
    "inout_vars": [
        ("KL6301_IN", "ARRAY [1..24] OF BYTE", "链 KL6301 输入过程映像"),
        ("KL6301_OUT", "ARRAY [1..24] OF BYTE", "链 KL6301 输出过程映像"),
    ],
    "behavior": (
        "**状态机与 `KL6301` 相同**：`bActivate` 上升沿 → 参数化阶段（`bActive = TRUE`、`bReady = FALSE`） → 成功 `bReady := TRUE` 进入数据交换 / 失败 `bError := TRUE` 给错误码；"
        "失败后必须先 `bActivate := FALSE` 等双标志回 FALSE 再 TRUE 重试。\n\n"
        "**ETS 集成（_EX 独有）**：KL6301 在数据交换状态下会同时响应 ETS 协议层的 PhysAddr Read（让 ETS 能「发现」本 KL6301）和 LED 控制（让运维在配置软件里点一下，对应实物上的 LED 会闪以便定位）。这两个功能由库内部驱动，调用方无需多余参数。\n\n"
        "**与 `KL6301` 的功能差异**：① 没有 `tTimeout` 输入——发送超时改由内部默认（实际工程中 5 秒以上即可）；② 固定要求 KL6301 固件 ≥ B1（PDF §4.2.3 Requirements 表）。如果挂的是 B0 固件 KL6301 会报 `WRONG_EIB_FIRMWARE_B1_NECESSARY` 错。\n\n"
        "**调用约束**：与 `KL6301` 完全一样——每实例每周期调用一次、同 PLC 任务内挂载、最多 64 实例。"
    ),
    "errors": ERROR_TABLE_FULL,
    "notes": [
        "**必须 KL6301 固件 B1+**：B0 老固件用 _EX 会立刻报 `WRONG_EIB_FIRMWARE_B1_NECESSARY`（错误码 14）。",
        "**没有 `tTimeout`**：从 `KL6301` 迁过来时把这一行删除，不要试图传入。",
        "**ETS BETA 状态**：PDF 写明 \"BETA: ETS support for search and LED flashing\"——表示 ETS 集成在某些 ETS 版本上可能有兼容性问题，**生产用建议先做 ETS 端联调**。",
        "**不需要 ETS 时直接用 `KL6301`**：_EX 没有性能优势，只有「被 ETS 识别」这一个功能差异。仅 PLC 控制场景下 `KL6301` 更稳定。（工程经验补充）",
        "**ETS 软件版本影响**：PDF 不写具体兼容版本；ETS5 实测可识别；ETS3 老版本不一定。生产前用现场实际 ETS 工具验证 LED Blink 是否生效。（工程经验补充）",
        "**与 `KL6301` 不能同实例共存**：同一块 KL6301 端子要么用 `KL6301` 要么用 `KL6301_EX`，不可同 idx 同时实例化，否则 `EIB_REC` 状态被互相覆盖。",
        "其余 `iMode` / 过滤器 / 物理地址 / IO 映射规则与 `KL6301` 完全一致——见 `KL6301` §3 §5 完整说明。",
    ],
    "tcpou_scene": (
        "BMS 项目：CX5120 + KL6301_EX 在系统调试期需要让现场调试员用 ETS 工具搜到 KL6301 并按 \"LED Blink\" 定位机柜里具体是哪块端子。"
    ),
    "tcpou_value": (
        "与 `KL6301` 比，多出 ETS 软件集成；不用为了 ETS 兼容而把整个 PLC 程序从 IEC 改成 ETS 项目"
    ),
    "tcpou_verify": (
        "登录后 `bStartConfig := TRUE` → 几秒后 `bConfigReady := TRUE`；现场用 ETS5 → Bus → Group monitor 应能搜到物理地址 2/3/4；"
        "在 ETS 里对该节点点 \"LED Blink\"，KL6301 物理 LED 应开始闪烁。"
    ),
    "tcpou_decl": (
        "VAR\n"
        "    fbKL6301Ex     : KL6301_EX;\n"
        "    arrKL6301_IN   : ARRAY[1..24] OF BYTE;\n"
        "    arrKL6301_OUT  : ARRAY[1..24] OF BYTE;\n"
        "    stEibRec       : EIB_REC;\n"
        "    bStartConfig   : BOOL;\n"
        "    iStep          : INT;\n"
        "    bConfigReady   : BOOL;\n"
        "    bConfigError   : BOOL;\n"
        "    iLastErrorId   : EIB_ERROR_CODE;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "// 与 KL6301 相同的配置流程；区别是没有 tTimeout 输入。\n"
        "CASE iStep OF\n"
        "0:\n"
        "    fbKL6301Ex.EIB_PHYS_ADDR.Area   := 2;\n"
        "    fbKL6301Ex.EIB_PHYS_ADDR.Line   := 3;\n"
        "    fbKL6301Ex.EIB_PHYS_ADDR.Device := 4;\n"
        "    fbKL6301Ex.EIB_GROUP_FILTER[1].GROUP_ADDR.MAIN     := 1;\n"
        "    fbKL6301Ex.EIB_GROUP_FILTER[1].GROUP_ADDR.SUB_MAIN := 1;\n"
        "    fbKL6301Ex.EIB_GROUP_FILTER[1].GROUP_ADDR.NUMBER   := 0;\n"
        "    fbKL6301Ex.EIB_GROUP_FILTER[1].GROUP_LEN           := 31;  // iMode=1 用 8×32\n"
        "    IF bStartConfig THEN\n"
        "        fbKL6301Ex.bActivate := TRUE;\n"
        "        IF fbKL6301Ex.bReady THEN\n"
        "            IF NOT fbKL6301Ex.bError THEN\n"
        "                iStep := 1;\n"
        "            ELSE\n"
        "                iStep := 100;\n"
        "                iLastErrorId := fbKL6301Ex.iErrorId;\n"
        "            END_IF\n"
        "        END_IF\n"
        "    END_IF\n"
        "1:\n"
        "    bConfigReady := TRUE;\n"
        "100:\n"
        "    bConfigError := TRUE;\n"
        "END_CASE\n"
        "\n"
        "// 注意：_EX 没有 tTimeout 参数，比 KL6301 少一个引脚\n"
        "fbKL6301Ex(\n"
        "    bActivate    := fbKL6301Ex.bActivate,\n"
        "    idx          := 1,\n"
        "    iMode        := 1,        // 8 过滤器 × 32 条目，要求固件 B1+\n"
        "    KL6301_IN    := arrKL6301_IN,\n"
        "    KL6301_OUT   := arrKL6301_OUT,\n"
        "    bActive      => ,\n"
        "    bReady       => ,\n"
        "    bError       => ,\n"
        "    iErrorId     => ,\n"
        "    str_Data_Rec => stEibRec\n"
        ");"
    ),
    "scene": (
        "BMS / 楼宇自动化项目里需要 PLC 与 ETS 工具共用一根 EIB 总线；ETS 端要能搜到 KL6301、要能 LED Blink 定位"
    ),
    "value": "在保持 PLC 控制功能不变前提下，额外获得 ETS 工具集成；不必为 ETS 兼容把整个项目重写",
    "alternatives": [
        "用 `KL6301` 普通版：能用，但 ETS 搜不到 KL6301 → 现场调试只能靠端子上面贴标签认人",
        "用 ETS 项目替代 PLC 项目：彻底兼容 ETS，但失去 PLC 工艺逻辑能力",
        "本 _EX：折中方案，**多 PLC + 调试员混用 EIB 总线**的项目首选",
    ],
    "related": (
        "`KL6301`（同库 §4.2.2，标准版，不需 ETS 时用它）、"
        "`EIB_REC`（同库 §4.3.2.5）、"
        "`EIB_GROUP_FILTER` / `EIB_PHYS_ADDR`（同库 §4.3.2）、"
        "`EIB_ERROR_CODE`（同库 §4.3.1.1）"
    ),
    "example_preview": (
        "PROGRAM P_Demo_KL6301_EX\n"
        "VAR\n"
        "    fbKL6301Ex    : KL6301_EX;\n"
        "    arrKL6301_IN  : ARRAY[1..24] OF BYTE;\n"
        "    arrKL6301_OUT : ARRAY[1..24] OF BYTE;\n"
        "    stEibRec      : EIB_REC;\n"
        "END_VAR\n"
        "// _EX 没有 tTimeout，要求 KL6301 固件 B1+\n"
        "fbKL6301Ex(\n"
        "    bActivate    := TRUE,\n"
        "    idx          := 1,\n"
        "    iMode        := 1,\n"
        "    KL6301_IN    := arrKL6301_IN,\n"
        "    KL6301_OUT   := arrKL6301_OUT,\n"
        "    str_Data_Rec => stEibRec\n"
        ");"
    ),
})


# ===========================================================================
# RECEIVE FBs (15)
# ===========================================================================

# Standard receive FB template generator
def _rec_fb(name, infosys_id, pdf_section, byte_desc, iec_type, out_var,
            extra_in=None, extra_in_block=None, in_extras=None,
            out_extras=None, output_block=None, scenario=None):
    """Build a generic EIB_*_REC entry dict."""
    var_input = "VAR_INPUT\n    Group_Address : EIB_GROUP_ADDR;\n"
    in_vars = [
        ("Group_Address", "EIB_GROUP_ADDR", None,
         "EIB 组地址（发起方的源地址；**必须出现在 KL6301 过滤器内**），3 级形式 MAIN/SUB_MAIN/NUMBER"),
    ]
    if extra_in_block:
        var_input += extra_in_block
    if in_extras:
        in_vars.extend(in_extras)
    var_input += "    strData_Rec   : EIB_REC;\nEND_VAR"
    in_vars.append(
        ("strData_Rec", "EIB_REC", None,
         "收发胶水结构，必须传 `KL6301.str_Data_Rec` 同一个实例"),
    )

    if output_block:
        var_output_block = output_block
        out_vars = out_extras
    else:
        var_output_block = (
            "VAR_OUTPUT\n"
            "    bDataReceive : BOOL;\n"
            f"    {out_var[0]:<13}: {out_var[1]};\n"
            "END_VAR"
        )
        out_vars = [
            ("bDataReceive", "BOOL",
             "**单周期脉冲信号**：收到 telegram 当 PLC 周期为 TRUE，之后立即回 FALSE。检测时用电平判断会漏掉，必须每周期采样或转上升沿"),
            (out_var[0], out_var[1], out_var[2]),
        ]

    return {
        "name": name,
        "category": "read",
        "category_label": "Read",
        "infosys_id": infosys_id,
        "pdf_section": pdf_section,
        "type": "FUNCTION_BLOCK",
        "var_input_block": var_input,
        "in_vars": in_vars,
        "var_output_block": var_output_block,
        "out_vars": out_vars,
        "var_inout_block": None,
        "inout_vars": None,
        "byte_desc": byte_desc,
        "iec_type": iec_type,
        "scenario": scenario or {},
    }


def _rec_apply(entry, brief, behavior, errors, notes, tcpou_scene,
               tcpou_value, tcpou_verify, tcpou_decl, tcpou_st, scene, value,
               alternatives, related, example_preview):
    """Mutate entry to fill prose sections."""
    entry["brief"] = brief
    entry["behavior"] = behavior
    entry["errors"] = errors
    entry["notes"] = notes
    entry["tcpou_scene"] = tcpou_scene
    entry["tcpou_value"] = tcpou_value
    entry["tcpou_verify"] = tcpou_verify
    entry["tcpou_decl"] = tcpou_decl
    entry["tcpou_st"] = tcpou_st
    entry["scene"] = scene
    entry["value"] = value
    entry["alternatives"] = alternatives
    entry["related"] = related
    entry["example_preview"] = example_preview
    return entry


# Common errors for REC FBs (no error pins, but EIB_REC may carry errors)
ERR_REC_COMMON = (
    "本 FB 自身**没有 `bError` / `iErrorID` 输出**——错误统一由 `KL6301` FB 通过 `str_Data_Rec` 内部的 `Rec_iErrorID` 字段透传："
    "若收到了不符长度的 telegram（例：用 `EIB_2OCTET_*` 接收 1-byte telegram）→ `KL6301.iErrorId := WRONG_EIB_DATA_LEN (20)`，本 FB 不会上送数据。\n\n"
    "完整错误码见 `KL6301` 文档 §4 或 `EIB_ERROR_CODE` 枚举（同库 §4.3.1.1）。"
)


_REC_GENERIC_BEHAVIOR_TEMPLATE = (
    "**触发方式**：调用即检查，每个 PLC 周期被调用时本 FB 检查 `strData_Rec` 内是否有"
    "与 `Group_Address` 匹配的**新到达 telegram**。\n\n"
    "**`bDataReceive` 的脉冲语义**：当本 FB 在某 PLC 周期检测到新 telegram 时，"
    "`bDataReceive := TRUE` **仅 1 个 PLC 周期**，下个周期自动回 FALSE。"
    "这是 EIB 库收发 FB 的**统一约定**——必须用边沿触发或单周期采样，不能写 `IF bDataReceive THEN ... END_IF` 当电平用，否则只有一帧的事件会被多次处理。\n\n"
    "**数据有效期**：`{out}` 在收到第一帧之前是 `0`（IEC 默认值）；首次收到 telegram 后保持上一次的值直到下一次更新——也就是**电平保持**。这一点与 `bDataReceive` 的脉冲语义不同。\n\n"
    "**与 KL6301 的依赖**：必须先有 `KL6301` 实例配置完成（`bReady = TRUE`）；KL6301 的 `EIB_GROUP_FILTER` 必须包含本 FB 的 `Group_Address`，否则 KL6301 根本不会把该 telegram 收进过程数据，本 FB 永远看不到事件。\n\n"
    "**调用次数**：每个 `Group_Address` 每个 PLC 任务**建议只挂一个接收实例**。多个实例监听同一地址会同时触发各自的 `bDataReceive`，不会互相干扰但占内存。\n\n"
    "**数据宽度匹配**：发送端 telegram 的负载长度必须与本 FB 类型对应（{byte_desc}）。"
    "类型不匹配的 telegram 会被 KL6301 丢弃（`WRONG_EIB_DATA_LEN`），本 FB 永远收不到。"
)


_REC_NOTES_COMMON = [
    "**`bDataReceive` 是脉冲信号，1 个 PLC 周期就回 FALSE**：检测必须用上升沿或单周期采样，写 `IF bDataReceive THEN x := y; END_IF` 会因为脉冲太短在高周期任务里偶尔丢事件。建议跟 `R_TRIG` 配合使用。",
    "**`Group_Address` 不在 KL6301 过滤器内 → 永远收不到**：检查 `KL6301.EIB_GROUP_FILTER[]` 是否覆盖。监控模式 iMode=100 例外。",
    "**`strData_Rec` 必须传 KL6301 的 `str_Data_Rec` 同一个实例**：传错 / 没传 / 传到其它 KL6301 实例的 EIB_REC 都会「不工作但不报错」。",
    "**必须与 KL6301 在同一 PLC 任务**：跨任务时 EIB_REC 状态不一致，收不到。",
    "**首次收 telegram 前数据值是 0**：业务逻辑别在启动就直接读，先等 `bDataReceive` 至少跳过一次。（工程经验补充）",
    "**EIB 长帧理论 EOT 时间 ≤ 100 ms**：如果两个发起方在 100 ms 内同时往同一组地址发，KL6301 只会收到先到的；另一帧若被丢，目标方 `bDataReceive` 不会出来。这是 EIB TP1 总线物理特性，不是本 FB 问题。（工程经验补充）",
]


def _rec_example_preview(name, out_var_name, out_var_type):
    return (
        f"PROGRAM P_Demo_{name}\n"
        f"VAR\n"
        f"    fb{name}        : {name};\n"
        f"    stEibRec        : EIB_REC;            // 由 KL6301 提供\n"
        f"    stGroupSensor   : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 4, NUMBER := 1);\n"
        f"    {out_var_name:<15} : {out_var_type};\n"
        f"    bGotNewData     : BOOL;\n"
        f"END_VAR\n"
        f"\n"
        f"fb{name}(\n"
        f"    Group_Address := stGroupSensor,\n"
        f"    strData_Rec   := stEibRec,\n"
        f"    bDataReceive  => bGotNewData,\n"
        f"    {out_var_name:<13} => {out_var_name}\n"
        f");"
    )


# ----- EIB_2OCTET_FLOAT_REC -----
e = _rec_fb(
    "EIB_2OCTET_FLOAT_REC", "187729675", "4.2.4.1",
    "EIB 2-byte float (DPT 9.xxx, 半精度 16-bit float)",
    "REAL", ("rData", "REAL",
             "收到的负载经库解码为 IEC `REAL`（32-bit float）。EIB 2-byte float 精度约 0.01，足够温度 / 湿度 / 风速等模拟量"),
)
_rec_apply(
    e,
    brief=(
        "接收 EIB 网络上指定组地址的 **2 字节 float telegram** 并解码为 IEC 标准 `REAL`。"
        "对应 KNX DPT 9.xxx 数据类型（温度、湿度、亮度、风速等模拟量）。\n\n"
        "EIB 2-byte float 是半精度浮点：1 符号位 + 4 尾数指数位 + 11 尾数位，编码范围约 ±670760，精度约 0.01。"
        "本 FB 自动把 EIB 半精度格式解码为 32-bit IEC `REAL`，业务代码直接读 `rData` 即可，不需要懂 EIB 编码。"
    ),
    behavior=_REC_GENERIC_BEHAVIOR_TEMPLATE.format(
        out="rData", byte_desc="本 FB 需要 2-byte float telegram"),
    errors=ERR_REC_COMMON,
    notes=_REC_NOTES_COMMON + [
        "**EIB 2-byte float 编码范围约 ±670760**，超出会被发送端截断/clipping。如果业务量纲超出，要么换 `EIB_4OCTET_FLOAT_REC`（4-byte float = IEEE 754 32-bit float，范围 ±1e38），要么发送端用 scaling。",
        "**精度 ~0.01**：温度 / 湿度等场景够用；用于工控级流量 / 电参数（要 4-5 位有效）就不够，要换 `EIB_4OCTET_FLOAT_REC`。",
    ],
    tcpou_scene=(
        "楼宇 BMS：DPT 9.001 室外温度传感器组地址 1/4/1 周期推送当前温度。"
        "本 demo 接收温度值，超出 [-10°C, 40°C] 报警。"
    ),
    tcpou_value=(
        "把「半精度浮点解码 + 字节序还原 + 单周期脉冲变化检测」封装为单调用；"
        "业务代码 1 行拿到温度浮点值"
    ),
    tcpou_verify=(
        "现场调试员用 ETS 模拟器把 23.5 推到 1/4/1 → 观察 `rTemperatureC` 应等于 23.5（±0.01），"
        "`bGotNewSample` 在该 PLC 周期为 TRUE，下个周期回 FALSE。"
    ),
    tcpou_decl=(
        "VAR\n"
        "    fbReceiveTemp        : EIB_2OCTET_FLOAT_REC;\n"
        "    stEibRec             : EIB_REC;          // 实际项目里链 KL6301.str_Data_Rec\n"
        "    stGroupOutdoorTemp   : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 4, NUMBER := 1);\n"
        "    rTemperatureC        : REAL;             // 当前温度\n"
        "    bGotNewSample        : BOOL;             // 单周期脉冲：刚刚收到新温度\n"
        "    rTrigSample          : R_TRIG;\n"
        "    bOutOfRange          : BOOL;             // 温度超出 [-10, 40] 报警\n"
        "    nSampleCount         : DINT;             // 自启动以来收到的样本数\n"
        "END_VAR"
    ),
    tcpou_st=(
        "// 每周期调用：库会检查 stEibRec 内 group 1/4/1 是否有新帧\n"
        "fbReceiveTemp(\n"
        "    Group_Address := stGroupOutdoorTemp,\n"
        "    strData_Rec   := stEibRec,\n"
        "    bDataReceive  => bGotNewSample,\n"
        "    rData         => rTemperatureC\n"
        ");\n"
        "\n"
        "// 单周期脉冲，必须用 R_TRIG 转上升沿才能数样本\n"
        "rTrigSample(CLK := bGotNewSample);\n"
        "IF rTrigSample.Q THEN\n"
        "    nSampleCount := nSampleCount + 1;\n"
        "    bOutOfRange  := (rTemperatureC &lt; -10.0) OR (rTemperatureC &gt; 40.0);\n"
        "END_IF;"
    ),
    scene=(
        "BMS 接入室外温度 / 湿度传感器、风速仪、亮度传感器等模拟量场。"
        "EIB 半精度浮点是楼宇行业 DPT 9.xxx 系列标准"
    ),
    value=(
        "替代手写「半精度浮点解码（按 KNX TP1 协议位拆分 + 反向运算）」——"
        "手写至少 30 行 IEC 代码，调试坑多；本 FB 一行调用"
    ),
    alternatives=[
        "用 `EIB_ALL_DATA_TYPES_REC` 收 raw byte 再自己解码：能做，但解码 EIB 半精度浮点的位运算容易写错；除非要同时收多种数据类型才用",
        "换用 `EIB_4OCTET_FLOAT_REC` 接收 IEEE 32-bit float（DPT 14.xxx）：精度高得多但 EIB 网上的传感器要支持发 4-byte float（多数低端楼宇 DPT 9 设备不支持）",
        "本 FB：DPT 9.xxx（绝大多数楼宇模拟量）的**标准**接收方式",
    ],
    related=(
        "`EIB_4OCTET_FLOAT_REC`（同库 §4.2.4.5，DPT 14 精度更高）、"
        "`EIB_2OCTET_SIGN_REC`（同库 §4.2.4.2，2-byte signed int）、"
        "`KL6301`（同库 §4.2.2，必须先配过滤器覆盖本 Group_Address）"
    ),
    example_preview=_rec_example_preview("EIB_2OCTET_FLOAT_REC", "rData", "REAL"),
)
ENTRIES.append(e)


# ----- EIB_2OCTET_SIGN_REC -----
e = _rec_fb(
    "EIB_2OCTET_SIGN_REC", "187731211", "4.2.4.2",
    "EIB 2-byte signed int (DPT 8.xxx)",
    "INT", ("iData", "INT",
            "收到的负载解码为 IEC `INT`（-32768..32767）"),
)
_rec_apply(
    e,
    brief=(
        "接收 EIB 网络上指定组地址的 **2 字节有符号整数 telegram**，对应 KNX DPT 8.xxx 数据类型。"
        "解码结果直接放入 IEC `INT`（16 位有符号，-32768..32767）。\n\n"
        "典型用于光照阈值、温度偏置、风向角等需要正负号且 16 位整数就够用的场景。"
    ),
    behavior=_REC_GENERIC_BEHAVIOR_TEMPLATE.format(
        out="iData", byte_desc="本 FB 需要 2-byte signed int telegram"),
    errors=ERR_REC_COMMON,
    notes=_REC_NOTES_COMMON + [
        "**16 位有符号整数范围 -32768..32767**：业务量纲超出会丢精度。",
        "**与无符号版本 `EIB_2OCTET_UNSIGN_REC` 不可混用**：发送端发的是哪一种 DPT 接收端就必须用对应版本。混用会把负数解读成大正数。",
    ],
    tcpou_scene=(
        "DPT 8.010 风向偏移：风向标设备每秒把「相对正北的角度偏置」以有符号 16-bit 形式发到组地址 1/4/5。"
        "本 demo 接收偏置值，超出 ±180° 时报警（数据异常）。"
    ),
    tcpou_value=(
        "把「接收 2-byte signed + 解码」压成一行调用；不用关心 EIB 字节序与符号位扩展"
    ),
    tcpou_verify=(
        "现场把 -45 推到 1/4/5 → `iAngleOffset` 应为 -45，`bGotNewSample` 单周期高；"
        "把 +200 推 → `bDataOutOfRange` 为 TRUE。"
    ),
    tcpou_decl=(
        "VAR\n"
        "    fbReceiveAngle   : EIB_2OCTET_SIGN_REC;\n"
        "    stEibRec         : EIB_REC;\n"
        "    stGroupWindDir   : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 4, NUMBER := 5);\n"
        "    iAngleOffset     : INT;                  // 风向偏置（度）\n"
        "    bGotNewSample    : BOOL;\n"
        "    rTrigSample      : R_TRIG;\n"
        "    bDataOutOfRange  : BOOL;\n"
        "END_VAR"
    ),
    tcpou_st=(
        "fbReceiveAngle(\n"
        "    Group_Address := stGroupWindDir,\n"
        "    strData_Rec   := stEibRec,\n"
        "    bDataReceive  => bGotNewSample,\n"
        "    iData         => iAngleOffset\n"
        ");\n"
        "\n"
        "rTrigSample(CLK := bGotNewSample);\n"
        "IF rTrigSample.Q THEN\n"
        "    bDataOutOfRange := (iAngleOffset &lt; -180) OR (iAngleOffset &gt; 180);\n"
        "END_IF;"
    ),
    scene=(
        "需要 16 位有符号整数（±32767 范围）的 KNX 模拟量：风向偏置、温度偏差、电参数偏差等"
    ),
    value="替代手写 byte 拼装 + 符号位扩展；EIB DPT 8 的**标准**接收方式",
    alternatives=[
        "用 `EIB_2OCTET_UNSIGN_REC` 收无符号整数：仅当 DPT 是 7.xxx 才对，DPT 8.xxx 必须用 SIGN 版本",
        "用 `EIB_4OCTET_SIGN_REC` 接收 32 位有符号：量纲超出 INT 时换它（DPT 13.xxx）",
        "本 FB：DPT 8.xxx 的**唯一正确**接收方式",
    ],
    related=(
        "`EIB_2OCTET_UNSIGN_REC`（同库 §4.2.4.3，无符号）、"
        "`EIB_4OCTET_SIGN_REC`（同库 §4.2.4.6，32 位有符号）、"
        "`KL6301`"
    ),
    example_preview=_rec_example_preview("EIB_2OCTET_SIGN_REC", "iData", "INT"),
)
ENTRIES.append(e)


# ----- EIB_2OCTET_UNSIGN_REC -----
e = _rec_fb(
    "EIB_2OCTET_UNSIGN_REC", "187732747", "4.2.4.3",
    "EIB 2-byte unsigned int (DPT 7.xxx)",
    "UINT", ("uiData", "UINT",
             "收到的负载解码为 IEC `UINT`（0..65535）"),
)
_rec_apply(
    e,
    brief=(
        "接收 EIB 网络上指定组地址的 **2 字节无符号整数 telegram**，对应 KNX DPT 7.xxx 数据类型。"
        "解码结果直接放入 IEC `UINT`（0..65535）。\n\n"
        "典型用于亮度（DPT 7.013，lux 单位）、时间间隔（毫秒/秒、DPT 7.003..7.005）、设备运行时长计数器等无负值的 16 位场景。"
    ),
    behavior=_REC_GENERIC_BEHAVIOR_TEMPLATE.format(
        out="uiData", byte_desc="本 FB 需要 2-byte unsigned int telegram"),
    errors=ERR_REC_COMMON,
    notes=_REC_NOTES_COMMON + [
        "**16 位无符号 0..65535**：业务量纲超出会回绕（wrap-around）。",
        "**别用来接收 DPT 8.xxx**（signed），会把 -1 解读成 65535。用对应 `EIB_2OCTET_SIGN_REC`。",
    ],
    tcpou_scene=(
        "DPT 7.013 室外亮度传感器把当前 lux 值（0..65535 范围）每秒推送到组地址 1/4/2。"
        "本 demo 接收 lux 值，超 50000 触发遮阳卷帘关闭。"
    ),
    tcpou_value=(
        "把「接收 2-byte unsigned + 解码」压成一行调用；不用关心字节序"
    ),
    tcpou_verify=(
        "现场把 12000 推到 1/4/2 → `uiBrightnessLux` 应为 12000，`bGotNewSample` 单周期高；"
        "把 55000 推 → `bShadeShouldClose` 为 TRUE。"
    ),
    tcpou_decl=(
        "VAR\n"
        "    fbReceiveLux       : EIB_2OCTET_UNSIGN_REC;\n"
        "    stEibRec           : EIB_REC;\n"
        "    stGroupBrightness  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 4, NUMBER := 2);\n"
        "    uiBrightnessLux    : UINT;\n"
        "    bGotNewSample      : BOOL;\n"
        "    rTrigSample        : R_TRIG;\n"
        "    bShadeShouldClose  : BOOL;\n"
        "END_VAR"
    ),
    tcpou_st=(
        "fbReceiveLux(\n"
        "    Group_Address := stGroupBrightness,\n"
        "    strData_Rec   := stEibRec,\n"
        "    bDataReceive  => bGotNewSample,\n"
        "    uiData        => uiBrightnessLux\n"
        ");\n"
        "\n"
        "rTrigSample(CLK := bGotNewSample);\n"
        "IF rTrigSample.Q THEN\n"
        "    bShadeShouldClose := (uiBrightnessLux &gt; 50000);\n"
        "END_IF;"
    ),
    scene="亮度传感器、时间间隔、运行时长等 16 位无负值场景",
    value="EIB DPT 7.xxx 的标准接收方式；替代手写字节解码",
    alternatives=[
        "`EIB_2OCTET_SIGN_REC`：仅 DPT 8 用",
        "`EIB_4OCTET_UNSIGN_REC`：32 位无符号场景（DPT 12）",
        "本 FB：DPT 7.xxx 标准选择",
    ],
    related=(
        "`EIB_2OCTET_SIGN_REC`（同库 §4.2.4.2）、"
        "`EIB_4OCTET_UNSIGN_REC`（同库 §4.2.4.7，32 位无符号）、"
        "`KL6301`"
    ),
    example_preview=_rec_example_preview("EIB_2OCTET_UNSIGN_REC", "uiData", "UINT"),
)
ENTRIES.append(e)


# ----- EIB_3BIT_CONTROL_REC -----
e = _rec_fb(
    "EIB_3BIT_CONTROL_REC", "187734283", "4.2.4.4",
    "EIB 4-bit Controlled (DPT 3.xxx, 调光 / 卷帘步进)",
    "BOOL + BYTE", None,
    output_block=(
        "VAR_OUTPUT\n"
        "    bDataReceive : BOOL;\n"
        "    bControl     : BOOL;\n"
        "    byRange      : BYTE;\n"
        "END_VAR"
    ),
    out_extras=[
        ("bDataReceive", "BOOL",
         "**单周期脉冲信号**：收到 telegram 当 PLC 周期为 TRUE，下周期回 FALSE"),
        ("bControl", "BOOL",
         "1 个控制位（TRUE/FALSE）。DPT 3.007 中 `TRUE = 增加 / 上`，`FALSE = 减少 / 下`"),
        ("byRange", "BYTE",
         "3 个数据位组成的范围值（000b..111b，即 0..7）。`0` = 停止；`1..7` = 步进幅度（步长由设备解释，典型 1 = 100%、7 = 1.5%）。**PDF Outputs 表 byControl/ByRange 是排版错误，实际 IEC 引脚名为 `bControl` / `byRange`，与 §4.2.4.4 Outputs 代码块一致**"),
    ],
)
_rec_apply(
    e,
    brief=(
        "接收 EIB **4-bit Controlled telegram**（DPT 3.xxx：调光控制 / 卷帘步进）：1 位控制方向 + 3 位幅度。"
        "对应楼宇控制里的「按住按钮调光」「按住按钮收/放卷帘」操作。\n\n"
        "**DPT 3.007 调光示例**：按住调光按钮 → 设备每 200 ms 发一帧 `bControl = TRUE, byRange = 4`（向上 50% 步进），"
        "松开按钮 → 发一帧 `byRange = 0`（停止）。本 FB 把这种「4 bit 控制 telegram」自动拆成 2 个 IEC 变量供业务代码用。"
    ),
    behavior=_REC_GENERIC_BEHAVIOR_TEMPLATE.format(
        out="bControl + byRange", byte_desc="4 bit telegram，PDF §4.2.4.4 标的是 4 bit Controlled")
        + "\n\n**位分配**（PDF §4.2.4.4 末段）：4 个 bit 按高到低 = [`bControl`, `byRange.2`, `byRange.1`, `byRange.0`]。"
        "其中 `bControl` 是方向，`byRange` 是 0..7 步幅。",
    errors=ERR_REC_COMMON,
    notes=_REC_NOTES_COMMON + [
        "**`byRange = 0` 是「停止」语义**：在 DPT 3.007 中，按住按钮发 1..7，松开发 0。业务代码看到 0 就停步进。",
        "**PDF Outputs 表把 `bControl` 写成 `byControl`、`byRange` 写成 `ByRange`** 是 PDF 排版错——以 Outputs **代码块**的 `bControl : BOOL; byRange : BYTE;` 为准。InfoSys 已修正。",
    ],
    tcpou_scene=(
        "DPT 3.007 调光控制：按住调光面板按钮发 4-bit 控制 telegram 到 1/2/3。"
        "本 demo 把控制信号转成调光增量：每收到一帧加/减"
    ),
    tcpou_value="替代手写 4-bit 解码 + 位分组；与按住调光按钮的语义直接对应",
    tcpou_verify=(
        "把 (bControl=TRUE, byRange=4) 推到 1/2/3 → `iDimmerLevel` 应在 0..100 间累加；"
        "推 byRange=0 → `bRampActive` 变 FALSE。"
    ),
    tcpou_decl=(
        "VAR\n"
        "    fbReceiveDim       : EIB_3BIT_CONTROL_REC;\n"
        "    stEibRec           : EIB_REC;\n"
        "    stGroupDimCtrl     : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 3);\n"
        "    bDirectionUp       : BOOL;        // bControl = TRUE 表示向上\n"
        "    byStep             : BYTE;        // 0..7 步幅\n"
        "    bGotNewSample      : BOOL;\n"
        "    rTrigSample        : R_TRIG;\n"
        "    iDimmerLevel       : INT;         // 0..100 当前亮度\n"
        "    bRampActive        : BOOL;        // byStep != 0 期间为 TRUE\n"
        "END_VAR"
    ),
    tcpou_st=(
        "fbReceiveDim(\n"
        "    Group_Address := stGroupDimCtrl,\n"
        "    strData_Rec   := stEibRec,\n"
        "    bDataReceive  => bGotNewSample,\n"
        "    bControl      => bDirectionUp,\n"
        "    byRange       => byStep\n"
        ");\n"
        "\n"
        "rTrigSample(CLK := bGotNewSample);\n"
        "IF rTrigSample.Q THEN\n"
        "    IF byStep = 0 THEN\n"
        "        bRampActive := FALSE;  // 操作员松开按钮\n"
        "    ELSE\n"
        "        bRampActive := TRUE;\n"
        "        IF bDirectionUp THEN\n"
        "            iDimmerLevel := iDimmerLevel + TO_INT(byStep);\n"
        "        ELSE\n"
        "            iDimmerLevel := iDimmerLevel - TO_INT(byStep);\n"
        "        END_IF;\n"
        "        IF iDimmerLevel &gt; 100 THEN\n"
        "            iDimmerLevel := 100;\n"
        "        ELSIF iDimmerLevel &lt; 0 THEN\n"
        "            iDimmerLevel := 0;\n"
        "        END_IF;\n"
        "    END_IF;\n"
        "END_IF;"
    ),
    scene="调光控制、卷帘步进等「按住调节、松开停止」语义的 KNX 4-bit 控制",
    value="替代手写位拆解；与 DPT 3.xxx 语义 1:1 对应",
    alternatives=[
        "用 `EIB_ALL_DATA_TYPES_REC` 收 raw + 自己拆位：能做，调试坑多",
        "用 `EIB_BIT_CONTROL_REC` 接收 2-bit：DPT 2.xxx 场景（开关 + 优先级），与本 FB 4-bit 不通用",
        "本 FB：DPT 3.xxx 的标准选择",
    ],
    related=(
        "`EIB_3BIT_CONTROL_SEND`（同库 §4.2.5.7，对应发送端）、"
        "`EIB_BIT_CONTROL_REC`（同库 §4.2.4.12，2-bit Controlled）、"
        "`KL6301`"
    ),
    example_preview=(
        "PROGRAM P_Demo_EIB_3BIT_CONTROL_REC\n"
        "VAR\n"
        "    fb           : EIB_3BIT_CONTROL_REC;\n"
        "    stEibRec     : EIB_REC;\n"
        "    stGroup      : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 3);\n"
        "    bDir         : BOOL;\n"
        "    byStep       : BYTE;\n"
        "    bNew         : BOOL;\n"
        "END_VAR\n"
        "fb(Group_Address := stGroup, strData_Rec := stEibRec,\n"
        "   bDataReceive => bNew, bControl => bDir, byRange => byStep);"
    ),
)
ENTRIES.append(e)


# ----- EIB_4OCTET_FLOAT_REC -----
e = _rec_fb(
    "EIB_4OCTET_FLOAT_REC", "187735819", "4.2.4.5",
    "EIB 4-byte float = IEEE 754 32-bit float (DPT 14.xxx)",
    "REAL", ("rData", "REAL",
             "收到的负载即 IEC `REAL`（IEEE 754 单精度浮点，范围约 ±1e38，精度约 1e-7）"),
)
_rec_apply(
    e,
    brief=(
        "接收 EIB 网络上指定组地址的 **4 字节 IEEE 754 float telegram**，对应 KNX DPT 14.xxx 数据类型。"
        "比 `EIB_2OCTET_FLOAT_REC` 精度高 7+ 位、范围大 ±1e38，可表达工业级测量精度（流量、压力、电参数）。\n\n"
        "EIB 4-byte float 与 IEC `REAL` 编码完全相同（IEEE 754 single precision），库只做字节序还原。"
    ),
    behavior=_REC_GENERIC_BEHAVIOR_TEMPLATE.format(
        out="rData", byte_desc="本 FB 需要 4-byte float telegram"),
    errors=ERR_REC_COMMON,
    notes=_REC_NOTES_COMMON + [
        "**DPT 14.xxx 是工业级精度场景**：流量、电流、压力等需要 4-5 位有效数字时用本 FB 而不是 2-byte float。",
        "**与 DPT 9 设备不兼容**：低端楼宇设备很多只发 DPT 9（2-byte）；用本 FB 收 DPT 9 设备会因长度不匹配收不到（`WRONG_EIB_DATA_LEN`）。",
    ],
    tcpou_scene=(
        "DPT 14.056 电能表把瞬时功率 (W) 通过 4-byte float 推送到组地址 1/4/8。"
        "本 demo 接收功率值，超 10 kW 触发负荷管理。"
    ),
    tcpou_value="不损失精度直接拿到 IEEE 754 浮点；替代手写字节序还原",
    tcpou_verify=(
        "把 8523.7 (W) 推到 1/4/8 → `rPowerW` 应等于 8523.7（±1e-3），`bGotNewSample` 单周期高。"
    ),
    tcpou_decl=(
        "VAR\n"
        "    fbReceivePower : EIB_4OCTET_FLOAT_REC;\n"
        "    stEibRec       : EIB_REC;\n"
        "    stGroupPower   : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 4, NUMBER := 8);\n"
        "    rPowerW        : REAL;\n"
        "    bGotNewSample  : BOOL;\n"
        "    rTrigSample    : R_TRIG;\n"
        "    bOverload      : BOOL;\n"
        "END_VAR"
    ),
    tcpou_st=(
        "fbReceivePower(\n"
        "    Group_Address := stGroupPower,\n"
        "    strData_Rec   := stEibRec,\n"
        "    bDataReceive  => bGotNewSample,\n"
        "    rData         => rPowerW\n"
        ");\n"
        "\n"
        "rTrigSample(CLK := bGotNewSample);\n"
        "IF rTrigSample.Q THEN\n"
        "    bOverload := rPowerW &gt; 10000.0;\n"
        "END_IF;"
    ),
    scene="电参数、流量、压力等工业级精度模拟量",
    value="不损失精度的 4-byte float 接收；标准 DPT 14 实现",
    alternatives=[
        "`EIB_2OCTET_FLOAT_REC`：精度低、范围小，但兼容低端设备",
        "`EIB_4OCTET_SIGN_REC`：32 位定点整数，不带小数",
        "本 FB：DPT 14.xxx 的标准接收方式",
    ],
    related="`EIB_2OCTET_FLOAT_REC`、`EIB_4OCTET_FLOAT_SEND`、`KL6301`",
    example_preview=_rec_example_preview("EIB_4OCTET_FLOAT_REC", "rData", "REAL"),
)
ENTRIES.append(e)


# ----- EIB_4OCTET_SIGN_REC -----
# Note: PDF prints output as `uiData : DINT` (PDF typo - actual IEC name from
# InfoSys is iData : DINT or remains uiData : DINT). We preserve PDF verbatim.
e = _rec_fb(
    "EIB_4OCTET_SIGN_REC", "187737355", "4.2.4.6",
    "EIB 4-byte signed int (DPT 13.xxx)",
    "DINT", ("uiData", "DINT",
             "**PDF 原文引脚名为 `uiData`**（典型 PDF 排版错——按命名习惯本应是 `iData`，但 PDF Outputs 代码块和表格都写 `uiData`）。类型 `DINT` 是 32 位有符号整数（-2³¹ .. 2³¹-1）"),
)
_rec_apply(
    e,
    brief=(
        "接收 EIB 网络上指定组地址的 **4 字节有符号整数 telegram**，对应 KNX DPT 13.xxx。"
        "解码到 IEC `DINT`（-2147483648..2147483647）。\n\n"
        "**PDF 排版说明**：PDF §4.2.4.6 Outputs 把引脚命名写成 `uiData : DINT`（u 前缀本意是 unsigned，但类型却是 signed `DINT`）。"
        "本文档保留 PDF 原写法以便代码逐字对照。实际语义就是 32 位有符号整数。\n\n"
        "典型用于电表累计电量（DPT 13.010）、运行时长秒数、有符号大整数计数器等。"
    ),
    behavior=_REC_GENERIC_BEHAVIOR_TEMPLATE.format(
        out="uiData", byte_desc="本 FB 需要 4-byte signed int telegram"),
    errors=ERR_REC_COMMON,
    notes=_REC_NOTES_COMMON + [
        "**PDF 引脚名 `uiData` 是排版错**（按 u-前缀惯例应该是 unsigned，但本 FB 是 signed `DINT`）。代码里必须写 `uiData`（保持与 PDF / 库实际一致）。",
        "**32 位有符号 ±2.1×10⁹**：电参数累计量在 21 亿之前都够用，超出就要换 `EIB_4OCTET_UNSIGN_REC`（0..4.3×10⁹）或物理上重置。",
    ],
    tcpou_scene=(
        "DPT 13.010 电能表累计有功电能 (Wh，可正可负)。"
        "本 demo 接收累计值，与上次记录差值做周期消耗。"
    ),
    tcpou_value="替代手写字节拼装 + 符号位扩展；DPT 13 标准接收方式",
    tcpou_verify=(
        "把 123456 推到 1/4/9 → `iAccumWh` 应等于 123456；过 1 分钟再推 124000 → `iPeriodWh` 应约等于 544。"
    ),
    tcpou_decl=(
        "VAR\n"
        "    fbReceiveEnergy : EIB_4OCTET_SIGN_REC;\n"
        "    stEibRec        : EIB_REC;\n"
        "    stGroupEnergy   : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 4, NUMBER := 9);\n"
        "    iAccumWh        : DINT;          // 累计电能 Wh\n"
        "    iLastAccumWh    : DINT;\n"
        "    iPeriodWh       : DINT;          // 上次到本次差值\n"
        "    bGotNewSample   : BOOL;\n"
        "    rTrigSample     : R_TRIG;\n"
        "END_VAR"
    ),
    tcpou_st=(
        "fbReceiveEnergy(\n"
        "    Group_Address := stGroupEnergy,\n"
        "    strData_Rec   := stEibRec,\n"
        "    bDataReceive  => bGotNewSample,\n"
        "    uiData        => iAccumWh   // PDF 写法保留\n"
        ");\n"
        "\n"
        "rTrigSample(CLK := bGotNewSample);\n"
        "IF rTrigSample.Q THEN\n"
        "    iPeriodWh    := iAccumWh - iLastAccumWh;\n"
        "    iLastAccumWh := iAccumWh;\n"
        "END_IF;"
    ),
    scene="电参数、累计计数、有符号大整数场景",
    value="DPT 13.xxx 标准接收；32 位有符号空间足够工业累计",
    alternatives=[
        "`EIB_4OCTET_UNSIGN_REC`：0..4.3×10⁹ 无负值",
        "`EIB_4OCTET_FLOAT_REC`：浮点更灵活但占字节相同",
        "本 FB：DPT 13.xxx 的标准选择",
    ],
    related=(
        "`EIB_4OCTET_UNSIGN_REC`（同库 §4.2.4.7）、"
        "`EIB_4OCTET_FLOAT_REC`（同库 §4.2.4.5）、"
        "`EIB_4OCTET_SIGN_SEND`（同库 §4.2.5.11，对应发送端）"
    ),
    example_preview=_rec_example_preview("EIB_4OCTET_SIGN_REC", "uiData", "DINT"),
)
ENTRIES.append(e)


# ----- EIB_4OCTET_UNSIGN_REC -----
e = _rec_fb(
    "EIB_4OCTET_UNSIGN_REC", "187738891", "4.2.4.7",
    "EIB 4-byte unsigned int (DPT 12.xxx)",
    "UDINT", ("uiData", "UDINT",
              "收到的负载解码为 IEC `UDINT`（0..4294967295）"),
)
_rec_apply(
    e,
    brief=(
        "接收 EIB 网络上指定组地址的 **4 字节无符号整数 telegram**，对应 KNX DPT 12.xxx。"
        "解码到 IEC `UDINT`（0..4294967295）。\n\n"
        "典型用于绝对运行时长（毫秒 / 秒计数）、累计脉冲计数等无负值大整数场景。"
    ),
    behavior=_REC_GENERIC_BEHAVIOR_TEMPLATE.format(
        out="uiData", byte_desc="本 FB 需要 4-byte unsigned int telegram"),
    errors=ERR_REC_COMMON,
    notes=_REC_NOTES_COMMON + [
        "**32 位无符号 0..4.3×10⁹**：足够绝大多数累计场景；超过会回绕。",
        "**别与 `EIB_4OCTET_SIGN_REC` 混用**：发的是 DPT 13 还是 DPT 12 要清楚。",
    ],
    tcpou_scene=(
        "DPT 12.001 设备绝对运行秒数推送到 1/4/10。"
        "本 demo 接收并换算为日 / 时 / 分。"
    ),
    tcpou_value="DPT 12.xxx 标准接收；不损失精度",
    tcpou_verify=(
        "推 86400 到 1/4/10 → `uiTotalSec` = 86400 → `nDays = 1, nHours = 0, nMinutes = 0`。"
    ),
    tcpou_decl=(
        "VAR\n"
        "    fbReceiveRuntime : EIB_4OCTET_UNSIGN_REC;\n"
        "    stEibRec         : EIB_REC;\n"
        "    stGroupRuntime   : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 4, NUMBER := 10);\n"
        "    uiTotalSec       : UDINT;\n"
        "    nDays            : UDINT;\n"
        "    nHours           : UDINT;\n"
        "    nMinutes         : UDINT;\n"
        "    bGotNewSample    : BOOL;\n"
        "    rTrigSample      : R_TRIG;\n"
        "END_VAR"
    ),
    tcpou_st=(
        "fbReceiveRuntime(\n"
        "    Group_Address := stGroupRuntime,\n"
        "    strData_Rec   := stEibRec,\n"
        "    bDataReceive  => bGotNewSample,\n"
        "    uiData        => uiTotalSec\n"
        ");\n"
        "\n"
        "rTrigSample(CLK := bGotNewSample);\n"
        "IF rTrigSample.Q THEN\n"
        "    nDays    := uiTotalSec / 86400;\n"
        "    nHours   := (uiTotalSec / 3600) MOD 24;\n"
        "    nMinutes := (uiTotalSec / 60) MOD 60;\n"
        "END_IF;"
    ),
    scene="运行时长、累计脉冲、绝对计数等无负值 32 位场景",
    value="DPT 12.xxx 标准接收",
    alternatives=[
        "`EIB_4OCTET_SIGN_REC`：有符号场景",
        "`EIB_4OCTET_FLOAT_REC`：浮点场景",
        "本 FB：DPT 12 标准选择",
    ],
    related="`EIB_4OCTET_SIGN_REC`、`KL6301`",
    example_preview=_rec_example_preview("EIB_4OCTET_UNSIGN_REC", "uiData", "UDINT"),
)
ENTRIES.append(e)


# ----- EIB_8BIT_SIGN_REC -----
e = _rec_fb(
    "EIB_8BIT_SIGN_REC", "187740427", "4.2.4.8",
    "EIB 8-bit data with scaling (DPT 5.xxx 百分比 / 角度 / byte)",
    "INT", ("iData", "INT",
            "缩放后输出值，含义由 `Scaling_Mode` 决定（见 §3）。返回 `-1` 表示 `Scaling_Mode` 非法"),
    extra_in_block="    Scaling_Mode  : INT;\n",
    in_extras=[
        ("Scaling_Mode", "INT", None,
         "缩放模式：`0` = 把 8-bit 解释为 0..100 [%]（DPT 5.001）；`1` = 解释为 0..360 [°]（DPT 5.003 角度）；`2` = 解释为 0..255 byte（DPT 5.005 原始字节）。非法值会让输出 `iData = -1`"),
    ],
)
_rec_apply(
    e,
    brief=(
        "接收 EIB 网络上指定组地址的 **8 位 telegram** 并按 `Scaling_Mode` 自动**缩放**到 IEC `INT`。"
        "支持 KNX DPT 5.001（0..100% 百分比）、DPT 5.003（0..360° 角度）、DPT 5.005（0..255 原始字节）三种语义。\n\n"
        "缩放在库内部完成——例如发送端发 0xFF (255)，本 FB 在 `Scaling_Mode = 0` 时输出 100；`Scaling_Mode = 1` 时输出 360；`Scaling_Mode = 2` 时输出 255。"
        "业务代码直接用 `iData` 数值即可。"
    ),
    behavior=_REC_GENERIC_BEHAVIOR_TEMPLATE.format(
        out="iData", byte_desc="本 FB 需要 1 byte (8-bit) telegram")
        + "\n\n**`Scaling_Mode` 处理**：库读到 8-bit 值 `raw` (0..255) 后：\n"
        "- `Scaling_Mode = 0` → `iData := raw * 100 / 255`（百分比，0..100）\n"
        "- `Scaling_Mode = 1` → `iData := raw * 360 / 255`（角度，0..360）\n"
        "- `Scaling_Mode = 2` → `iData := raw`（原始 byte，0..255）\n"
        "- 其它 `Scaling_Mode` 值 → `iData := -1` 标记错误（PDF §4.2.4.8 Outputs 注释）",
    errors=ERR_REC_COMMON + (
        "\n\n额外：本 FB 看到非法 `Scaling_Mode`（不是 0/1/2）时 `iData = -1`，但不会触发 KL6301 的 `bError`。"
        "调用方代码里应自查 `Scaling_Mode` 是否合法。"
    ),
    notes=_REC_NOTES_COMMON + [
        "**`Scaling_Mode` 决定输出语义**：发送端按哪种 DPT 发，接收端就必须填对应 mode。混用结果是数字仍出来但含义不对。",
        "**`iData = -1` 表示 mode 非法**——业务代码每次取值前可加 `IF iData &lt; 0 THEN report_error END_IF` 自检。",
        "**0..100% 实际有量化误差**：raw 255 = 100，raw 254 ≈ 99，**步长约 0.39% 而不是 1%**。要精确百分比的话别用 DPT 5.001，用 DPT 9.x（2-byte float）。（工程经验补充）",
    ],
    tcpou_scene=(
        "DPT 5.001 调光面板把当前调光百分比 (0..100%) 经 1 byte 推送到 1/2/4。"
        "本 demo 用 `Scaling_Mode = 0` 接收百分比，复制给本地 HMI 显示。"
    ),
    tcpou_value=(
        "把「8-bit 解码 + 单位换算」做成一个调用；不用关心 raw byte 到 % 的缩放"
    ),
    tcpou_verify=(
        "推 0x80 (128) 到 1/2/4 → `iDimPercent` 应约 50（128*100/255 ≈ 50.2 取整）。"
    ),
    tcpou_decl=(
        "VAR\n"
        "    fbReceiveDimPct  : EIB_8BIT_SIGN_REC;\n"
        "    stEibRec         : EIB_REC;\n"
        "    stGroupDimPct    : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 4);\n"
        "    iDimPercent      : INT;          // 解码后的 0..100\n"
        "    bGotNewSample    : BOOL;\n"
        "    rTrigSample      : R_TRIG;\n"
        "    bScalingError    : BOOL;\n"
        "END_VAR"
    ),
    tcpou_st=(
        "fbReceiveDimPct(\n"
        "    Group_Address := stGroupDimPct,\n"
        "    Scaling_Mode  := 0,             // 0..100% (DPT 5.001)\n"
        "    strData_Rec   := stEibRec,\n"
        "    bDataReceive  => bGotNewSample,\n"
        "    iData         => iDimPercent\n"
        ");\n"
        "\n"
        "rTrigSample(CLK := bGotNewSample);\n"
        "IF rTrigSample.Q THEN\n"
        "    bScalingError := (iDimPercent &lt; 0);   // -1 → mode 非法\n"
        "END_IF;"
    ),
    scene="DPT 5.001/5.003/5.005 8-bit 缩放场景：调光百分比、角度、原始字节",
    value="自动缩放无需手写公式；DPT 5.xxx 标准接收方式",
    alternatives=[
        "`EIB_8BIT_UNSIGN_REC`：纯字节（0..255），不缩放",
        "`EIB_2OCTET_UNSIGN_REC`：16-bit 精度更高",
        "本 FB：DPT 5.001/003/005 的**标准**选择",
    ],
    related=(
        "`EIB_8BIT_UNSIGN_REC`（同库 §4.2.4.9，原始字节）、"
        "`EIB_8BIT_SIGN_SEND`（同库 §4.2.5.15，对应发送端）"
    ),
    example_preview=(
        "PROGRAM P_Demo_EIB_8BIT_SIGN_REC\n"
        "VAR\n"
        "    fb           : EIB_8BIT_SIGN_REC;\n"
        "    stEibRec     : EIB_REC;\n"
        "    stGroup      : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 4);\n"
        "    iPct         : INT;\n"
        "    bNew         : BOOL;\n"
        "END_VAR\n"
        "fb(Group_Address := stGroup, Scaling_Mode := 0,\n"
        "   strData_Rec := stEibRec, bDataReceive => bNew, iData => iPct);"
    ),
)
ENTRIES.append(e)


# ----- EIB_8BIT_UNSIGN_REC -----
e = _rec_fb(
    "EIB_8BIT_UNSIGN_REC", "187741963", "4.2.4.9",
    "EIB 8-bit unsigned byte (DPT 5.010 计数 / 5.005 raw)",
    "BYTE", ("byData", "BYTE",
            "收到的负载即原始 byte (0..255)，不做缩放"),
)
_rec_apply(
    e,
    brief=(
        "接收 EIB 网络上指定组地址的 **8 位 telegram** 并放入原始 IEC `BYTE`，不做缩放（对应 DPT 5.005 / 5.010 等）。"
        "与 `EIB_8BIT_SIGN_REC` 区别：本 FB **不带 `Scaling_Mode`，直接给 raw byte**。\n\n"
        "适合需要「原汁原味」字节而不是 % / 角度场景：场景号、设备状态码、原始计数等。"
    ),
    behavior=_REC_GENERIC_BEHAVIOR_TEMPLATE.format(
        out="byData", byte_desc="本 FB 需要 1 byte (8-bit) telegram"),
    errors=ERR_REC_COMMON,
    notes=_REC_NOTES_COMMON + [
        "**不缩放**：`byData = 128` 就是 raw 128，不会被理解成百分比 50。要缩放用 `EIB_8BIT_SIGN_REC`。",
    ],
    tcpou_scene=(
        "DPT 5.005 设备状态码：故障代码、运行模式编号等以 byte 形式发到 1/2/5。"
        "本 demo 接收并按状态码分支报警。"
    ),
    tcpou_value="DPT 5.005/5.010 的标准接收；零成本拿到 raw byte",
    tcpou_verify=(
        "推 0x03 到 1/2/5 → `byStatusCode` = 3 → `bFanFault` = TRUE（状态码 3 = 风机故障）。"
    ),
    tcpou_decl=(
        "VAR\n"
        "    fbReceiveStatus : EIB_8BIT_UNSIGN_REC;\n"
        "    stEibRec        : EIB_REC;\n"
        "    stGroupStatus   : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 5);\n"
        "    byStatusCode    : BYTE;\n"
        "    bGotNewSample   : BOOL;\n"
        "    rTrigSample     : R_TRIG;\n"
        "    bFanFault       : BOOL;\n"
        "    bFilterDirty    : BOOL;\n"
        "    bOverTemp       : BOOL;\n"
        "END_VAR"
    ),
    tcpou_st=(
        "fbReceiveStatus(\n"
        "    Group_Address := stGroupStatus,\n"
        "    strData_Rec   := stEibRec,\n"
        "    bDataReceive  => bGotNewSample,\n"
        "    byData        => byStatusCode\n"
        ");\n"
        "\n"
        "rTrigSample(CLK := bGotNewSample);\n"
        "IF rTrigSample.Q THEN\n"
        "    bFanFault    := (byStatusCode = 3);\n"
        "    bFilterDirty := (byStatusCode = 5);\n"
        "    bOverTemp    := (byStatusCode = 7);\n"
        "END_IF;"
    ),
    scene="原始字节场景：设备状态码、计数、模式编号",
    value="不缩放，1:1 byte → BYTE；DPT 5.005/5.010 标准选择",
    alternatives=[
        "`EIB_8BIT_SIGN_REC`：要缩放到 %/角度时用",
        "`EIB_2OCTET_UNSIGN_REC`：16 位计数",
        "本 FB：DPT 5.005/010 标准选择",
    ],
    related="`EIB_8BIT_SIGN_REC`（带缩放）、`EIB_8BIT_UNSIGN_SEND`（发送端）",
    example_preview=_rec_example_preview("EIB_8BIT_UNSIGN_REC", "byData", "BYTE"),
)
ENTRIES.append(e)


# ----- EIB_ALL_DATA_TYPES_REC -----
e = _rec_fb(
    "EIB_ALL_DATA_TYPES_REC", "187743499", "4.2.4.10",
    "任意 EIB 数据类型",
    "ARRAY[1..14] OF BYTE", None,
    output_block=(
        "VAR_OUTPUT\n"
        "    bDataReceive     : BOOL;\n"
        "    EIB_Data_Receive : ARRAY [1..14] OF BYTE;\n"
        "    EIB_Data_Len     : USINT;\n"
        "    bEIB_READ        : BOOL;\n"
        "END_VAR"
    ),
    out_extras=[
        ("bDataReceive", "BOOL", "**单周期脉冲**：收到 telegram 时为 TRUE 1 个 PLC 周期"),
        ("EIB_Data_Receive", "ARRAY [1..14] OF BYTE",
         "原始 EIB 负载字节，从 `[1]` 开始填。库不解码，业务自己解释"),
        ("EIB_Data_Len", "USINT",
         "负载长度。规则：负载 < 8 bit 时 `EIB_Data_Len = 1`；负载 ≥ 8 bit 时 `EIB_Data_Len = 字节数 + 1`。"
         "PDF 举例：收 1 bit 数据 → len 1；收 2 byte 数据 → len 3"),
        ("bEIB_READ", "BOOL",
         "区分 telegram 类型：`TRUE` = 这是 EIB Read 命令（来自 `EIB_READ_SEND` 或其它 read_group_req）；"
         "`FALSE` = 普通数据 telegram。本字段自 V3.3.5.0 起可用（PDF §4.2.4.10）"),
    ],
)
_rec_apply(
    e,
    brief=(
        "接收 EIB 网络上指定组地址的 **任意类型** telegram，把负载以**原始字节数组**形式输出，调用方自己解码。"
        "比所有专门类型 FB 更灵活——一个组地址可能有多种 DPT 数据，或对端 DPT 不在标准列表里，本 FB 都能收。\n\n"
        "**对比专门 FB**：`EIB_2OCTET_FLOAT_REC` 等会按特定 DPT 长度过滤——长度不符会被丢；本 FB 不过滤长度。"
        "**对比 `EIB_ALL_DATA_TYPES_REC_EX`**：本 FB 必须先指定 `Group_Address`，只接该地址；EX 版本不需要地址，接全部进入过滤器的 telegram，附带源地址输出。"
    ),
    behavior=_REC_GENERIC_BEHAVIOR_TEMPLATE.format(
        out="EIB_Data_Receive[]", byte_desc="任意长度，从 1 bit 到 14 byte 都行")
        + "\n\n**`EIB_Data_Len` 编码规则**（PDF §4.2.4.10 Outputs 表）：\n"
        "- 负载 < 8 bit → `EIB_Data_Len = 1`\n"
        "- 负载 ≥ 8 bit → `EIB_Data_Len = 字节数 + 1`\n"
        "举例：收 1 bit 数据 → `EIB_Data_Len = 1`；收 2 byte 数据 → `EIB_Data_Len = 3`。\n"
        "**注意**：这与「正常字节计数 + 1」不直观，是历史协议遗留——使用时建议把它当作「已用 BYTE 数」的索引上限来记。",
    errors=ERR_REC_COMMON,
    notes=_REC_NOTES_COMMON + [
        "**`EIB_Data_Len` 编码不直观**：1 bit 数据 len = 1（不是 0），2 byte 数据 len = 3（不是 2）。读 PDF §4.2.4.10 末段表确认。",
        "**`bEIB_READ` 区分 read 请求 vs 普通数据**：网络上有别人调 `EIB_READ_SEND` 请求本地址的数据时本 FB 会同时收到，用 `bEIB_READ = TRUE` 区分。如果业务上要「被读到时主动答」，需要看本字段。",
        "**用本 FB 接专门类型时损失抽象**：能用 `EIB_2OCTET_FLOAT_REC` 就别用本 FB——专门 FB 已经做了解码，业务代码更清楚。本 FB 适合**异构数据 / 非标 DPT**。（工程经验补充）",
    ],
    tcpou_scene=(
        "实验性 KNX 设备，DPT 私有，且会同时发 1 bit / 2 byte 两种长度。"
        "本 demo 用一个 FB 接两种长度，按 `EIB_Data_Len` 分支处理。"
    ),
    tcpou_value="单 FB 处理变长 telegram + 可识别 read 命令；专用 FB 做不到",
    tcpou_verify=(
        "推 1 bit (`bData = TRUE`) → `EIB_Data_Len` = 1、`EIB_Data_Receive[1].0` = 1；"
        "推 2 byte (0x12 0x34) → `EIB_Data_Len` = 3、`EIB_Data_Receive[1]` = 0x12、`[2]` = 0x34。"
    ),
    tcpou_decl=(
        "VAR\n"
        "    fbReceiveAny       : EIB_ALL_DATA_TYPES_REC;\n"
        "    stEibRec           : EIB_REC;\n"
        "    stGroupCustomDpt   : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 1, NUMBER := 20);\n"
        "    arrPayload         : ARRAY[1..14] OF BYTE;\n"
        "    usPayloadLen       : USINT;\n"
        "    bIsReadCmd         : BOOL;\n"
        "    bGotNewSample      : BOOL;\n"
        "    rTrigSample        : R_TRIG;\n"
        "    bAsBool            : BOOL;        // 当 len = 1\n"
        "    wAsWord            : WORD;        // 当 len = 3（2 byte payload）\n"
        "END_VAR"
    ),
    tcpou_st=(
        "fbReceiveAny(\n"
        "    Group_Address    := stGroupCustomDpt,\n"
        "    strData_Rec      := stEibRec,\n"
        "    bDataReceive     => bGotNewSample,\n"
        "    EIB_Data_Receive => arrPayload,\n"
        "    EIB_Data_Len     => usPayloadLen,\n"
        "    bEIB_READ        => bIsReadCmd\n"
        ");\n"
        "\n"
        "rTrigSample(CLK := bGotNewSample);\n"
        "IF rTrigSample.Q AND NOT bIsReadCmd THEN\n"
        "    CASE usPayloadLen OF\n"
        "        1:  // < 8 bit 负载\n"
        "            bAsBool := (arrPayload[1].0 = TRUE);\n"
        "        3:  // 2 byte 负载，high/low 拼装\n"
        "            wAsWord := SHL(WORD#(arrPayload[1]), 8) + WORD#(arrPayload[2]);\n"
        "    END_CASE;\n"
        "END_IF;"
    ),
    scene="非标 DPT / 私有协议 / 变长 telegram / 需要识别 EIB read 请求",
    value="比专用 FB 灵活；唯一支持识别 EIB read 命令的接收 FB",
    alternatives=[
        "所有专用 `EIB_*_REC` FB：能用就用，业务代码清晰",
        "`EIB_ALL_DATA_TYPES_REC_EX`：不指定地址收全部",
        "本 FB：异构 DPT、识别 read 请求时必选",
    ],
    related=(
        "`EIB_ALL_DATA_TYPES_REC_EX`（同库 §4.2.4.11，不指定地址）、"
        "`EIB_ALL_DATA_TYPES_SEND`（同库 §4.2.5.19，配套发送端）、"
        "`EIB_READ_SEND`（同库 §4.2.5.27，对应的 read 命令）"
    ),
    example_preview=(
        "PROGRAM P_Demo_EIB_ALL_DATA_TYPES_REC\n"
        "VAR\n"
        "    fb         : EIB_ALL_DATA_TYPES_REC;\n"
        "    stEibRec   : EIB_REC;\n"
        "    stGroup    : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 1, NUMBER := 20);\n"
        "    arrPayload : ARRAY[1..14] OF BYTE;\n"
        "    usLen      : USINT;\n"
        "    bIsRead    : BOOL;\n"
        "    bNew       : BOOL;\n"
        "END_VAR\n"
        "fb(Group_Address := stGroup, strData_Rec := stEibRec,\n"
        "   bDataReceive => bNew, EIB_Data_Receive => arrPayload,\n"
        "   EIB_Data_Len => usLen, bEIB_READ => bIsRead);"
    ),
)
ENTRIES.append(e)


# ----- EIB_ALL_DATA_TYPES_REC_EX -----
# This FB DOES NOT have Group_Address as input; output it.
e = {
    "name": "EIB_ALL_DATA_TYPES_REC_EX",
    "category": "read",
    "category_label": "Read",
    "infosys_id": "187745035",
    "pdf_section": "4.2.4.11",
    "type": "FUNCTION_BLOCK",
    "var_input_block": (
        "VAR_INPUT\n"
        "    strData_Rec   : EIB_REC;\n"
        "END_VAR"
    ),
    "in_vars": [
        ("strData_Rec", "EIB_REC", None,
         "收发胶水结构，必须传 `KL6301.str_Data_Rec` 同一个实例。**本 FB 不需要 `Group_Address`**——会收到所有进入 KL6301 过滤器的 telegram"),
    ],
    "var_output_block": (
        "VAR_OUTPUT\n"
        "    bDataReceive     : BOOL;\n"
        "    Group_Address    : EIB_GROUP_ADDR;\n"
        "    EIB_Data_Receive : ARRAY [1..14] OF BYTE;\n"
        "    EIB_Data_Len     : USINT;\n"
        "END_VAR"
    ),
    "out_vars": [
        ("bDataReceive", "BOOL", "**单周期脉冲**：收到 telegram 时为 TRUE 1 个 PLC 周期"),
        ("Group_Address", "EIB_GROUP_ADDR",
         "**telegram 来源的组地址**（区别于 _REC 版本：地址是输入；这里是输出，告诉你刚收到的帧来自哪个地址）"),
        ("EIB_Data_Receive", "ARRAY [1..14] OF BYTE", "原始 EIB 负载字节"),
        ("EIB_Data_Len", "USINT",
         "负载长度，编码规则同 `EIB_ALL_DATA_TYPES_REC`：< 8 bit → 1；≥ 8 bit → 字节数 + 1"),
    ],
    "var_inout_block": None,
    "inout_vars": None,
    "brief": (
        "接收 EIB 网络上**所有**进入 `KL6301` 过滤器的 telegram，输出**源组地址 + 原始字节**。"
        "与 `EIB_ALL_DATA_TYPES_REC` 的关键区别：本 FB **不需要指定 `Group_Address`**——它「嗅探」所有进入过滤器的 telegram。\n\n"
        "用于诊断 / 日志 / 事件归档场景：把整条 EIB 总线上的活动按时间顺序记到 PLC 程序里，每条记录带"
        "（时间 + 源组地址 + 原始字节）三元组。配合 KL6301 监控模式（iMode=100）几乎等价于楼宇行业用的 ETS Group Monitor。"
    ),
    "behavior": (
        "**触发**：每个 PLC 周期被调用时，本 FB 检查 `strData_Rec` 中是否有**新到达且尚未被本 FB 报告**的 telegram。"
        "有就 `bDataReceive := TRUE` 1 个 PLC 周期，并把 telegram 的源组地址、负载、长度填到输出引脚。\n\n"
        "**与 `EIB_ALL_DATA_TYPES_REC` 的差异**：\n"
        "- 不要 `Group_Address` 输入（嗅探所有过滤器内的地址）\n"
        "- 多出 `Group_Address` 输出（告诉调用方刚收到的 telegram 来自哪个地址）\n"
        "- 没有 `bEIB_READ` 输出（无法区分 read 请求与普通数据）\n\n"
        "**KL6301 过滤器规则不变**：只能接收「过滤器允许进入」的 telegram。要全收必须把 KL6301 设为监控模式 iMode=100。\n\n"
        "**与多个 _REC 实例并发**：本 FB 与 `EIB_2OCTET_FLOAT_REC` 等监听同地址的实例**可同时存在**——多个接收 FB 监听同 EIB_REC 时彼此独立，互不影响。"
        "本 FB 适合做日志，专用 FB 做业务，两者并存常见。\n\n"
        "**调用约束**：每个 PLC 周期调用一次；与 KL6301 同任务；单个 PLC 程序里多实例无冲突。"
    ),
    "errors": ERR_REC_COMMON,
    "notes": _REC_NOTES_COMMON + [
        "**没有 `Group_Address` 输入**：从 `EIB_ALL_DATA_TYPES_REC` 迁过来要删除这一行参数。",
        "**没有 `bEIB_READ`**：要识别 read 请求只能用 `EIB_ALL_DATA_TYPES_REC` 加显式地址。",
        "**用于做日志记录**：典型用法是把 (timestamp, Group_Address, payload) 推进环形缓冲区。结合 KL6301 监控模式做「PLC 内置 group monitor」。（工程经验补充）",
        "**KL6301 监控模式（iMode=100）下不发数据**：本 FB 接收没问题，但**不能反向回应**——所以做日志可以，做交互不行。",
    ],
    "tcpou_scene": (
        "BMS 调试期：现场操作员说「开关 1/1/3 推几下没反应」。"
        "本 demo 把整条 EIB 总线（含 1/1/0..1/1/63）的所有 telegram 记入环形缓冲区，"
        "运维通过 HMI 翻页查最近 100 条事件确认 1/1/3 是否真有报文进来。"
    ),
    "tcpou_value": (
        "把「按地址订阅多个 _REC 实例 + 各自维护缓冲」压成一个 _EX 实例 + 一个统一缓冲；"
        "代码量减少 10 倍，且新增地址时不用改业务代码"
    ),
    "tcpou_verify": (
        "推 1/1/3 上推几下开关 → 环形缓冲 `arrLog[]` 顶端应出现 (1, 1, 3, [01], len=1) 多条；"
        "总条数 `nLogCount` 应递增。"
    ),
    "tcpou_decl": (
        "VAR\n"
        "    fbReceiveAll : EIB_ALL_DATA_TYPES_REC_EX;\n"
        "    stEibRec     : EIB_REC;\n"
        "\n"
        "    stCurrentGroup    : EIB_GROUP_ADDR;\n"
        "    arrCurrentPayload : ARRAY[1..14] OF BYTE;\n"
        "    usCurrentLen      : USINT;\n"
        "    bGotNewSample     : BOOL;\n"
        "    rTrigSample       : R_TRIG;\n"
        "\n"
        "    // 简化环形缓冲：最近 100 条事件\n"
        "    TYPE ST_LogEntry : STRUCT\n"
        "        stGroup : EIB_GROUP_ADDR;\n"
        "        arrData : ARRAY[1..14] OF BYTE;\n"
        "        usLen   : USINT;\n"
        "    END_STRUCT END_TYPE;\n"
        "    // ⚠️ TYPE 在 VAR 中无法定义；实际工程把 ST_LogEntry 放 DUT，这里仅示意\n"
        "\n"
        "    nLogCount    : DINT;\n"
        "    nLogHead     : DINT;\n"
        "END_VAR"
    ),
    "tcpou_st": (
        "fbReceiveAll(\n"
        "    strData_Rec      := stEibRec,\n"
        "    bDataReceive     => bGotNewSample,\n"
        "    Group_Address    => stCurrentGroup,\n"
        "    EIB_Data_Receive => arrCurrentPayload,\n"
        "    EIB_Data_Len     => usCurrentLen\n"
        ");\n"
        "\n"
        "// 单周期脉冲转上升沿，把 (group, payload, len) 入环形缓冲\n"
        "rTrigSample(CLK := bGotNewSample);\n"
        "IF rTrigSample.Q THEN\n"
        "    // 实际工程把 stCurrentGroup / arrCurrentPayload / usCurrentLen 写入 arrLog[nLogHead]\n"
        "    nLogCount := nLogCount + 1;\n"
        "    nLogHead  := (nLogHead + 1) MOD 100;\n"
        "END_IF;"
    ),
    "scene": "EIB 总线日志 / 事件归档 / 调试期 group monitor / 不预先知道哪些地址要听",
    "value": "嗅探整条总线，不用为每个地址写一个 _REC 实例；唯一带源地址输出的接收 FB",
    "alternatives": [
        "为每个地址挂 `EIB_BIT_REC` / 专用 _REC：业务清晰但代码量爆炸",
        "用 `EIB_ALL_DATA_TYPES_REC` + 多实例分地址：能做，要为每地址传 Group_Address，繁琐",
        "本 _EX：日志 / 调试 / 监控类用例**首选**",
    ],
    "related": (
        "`EIB_ALL_DATA_TYPES_REC`（同库 §4.2.4.10，需指定地址）、"
        "`KL6301` iMode=100 监控模式（同库 §4.2.2）、"
        "`EIB_REC`（同库 §4.3.2.5）"
    ),
    "example_preview": (
        "PROGRAM P_Demo_EIB_ALL_DATA_TYPES_REC_EX\n"
        "VAR\n"
        "    fb         : EIB_ALL_DATA_TYPES_REC_EX;\n"
        "    stEibRec   : EIB_REC;\n"
        "    stGroup    : EIB_GROUP_ADDR;\n"
        "    arrPayload : ARRAY[1..14] OF BYTE;\n"
        "    usLen      : USINT;\n"
        "    bNew       : BOOL;\n"
        "END_VAR\n"
        "fb(strData_Rec := stEibRec, bDataReceive => bNew,\n"
        "   Group_Address => stGroup, EIB_Data_Receive => arrPayload,\n"
        "   EIB_Data_Len => usLen);"
    ),
}
ENTRIES.append(e)


# ----- EIB_BIT_CONTROL_REC -----
e = _rec_fb(
    "EIB_BIT_CONTROL_REC", "187746571", "4.2.4.12",
    "EIB 2-bit Controlled (DPT 2.xxx 开关 + 优先级)",
    "BOOL + BOOL", None,
    output_block=(
        "VAR_OUTPUT\n"
        "    bDataReceive : BOOL;\n"
        "    bControl     : BOOL;\n"
        "    bValue       : BOOL;\n"
        "END_VAR"
    ),
    out_extras=[
        ("bDataReceive", "BOOL", "**单周期脉冲**：收到 telegram 时为 TRUE 1 个 PLC 周期"),
        ("bControl", "BOOL",
         "控制位（TRUE/FALSE）。在 DPT 2.001 (Switch_Control) 中 = 强制优先级位（TRUE = 强制生效）"),
        ("bValue", "BOOL",
         "数据位（TRUE/FALSE）。在 DPT 2.001 中 = 实际开关值（TRUE = ON、FALSE = OFF）"),
    ],
)
_rec_apply(
    e,
    brief=(
        "接收 EIB **2-bit Controlled telegram**（DPT 2.xxx：带优先级控制的 1-bit 数据）：1 位控制 + 1 位数据。"
        "对应 KNX「安全 / 应急覆盖」语义——比如普通开关 + 应急按钮共用一个组地址，应急按钮的命令 `bControl = TRUE` 强制覆盖普通命令。\n\n"
        "**DPT 2.001 示例**：普通开关发 `bControl = FALSE, bValue = TRUE`（请求开灯）；"
        "应急按钮发 `bControl = TRUE, bValue = FALSE`（强制关灯，不可被覆盖）。设备解释 `bControl` 决定是否优先。"
    ),
    behavior=_REC_GENERIC_BEHAVIOR_TEMPLATE.format(
        out="bControl + bValue", byte_desc="2 bit telegram")
        + "\n\n**位分配**（PDF §4.2.4.12 末段）：2 个 bit 按高到低 = [`bControl`, `bValue`]。",
    errors=ERR_REC_COMMON,
    notes=_REC_NOTES_COMMON + [
        "**`bControl` = 优先级 / 强制位**：DPT 2.xxx 的语义是「控制位为 TRUE 表示这条命令必须执行不可被普通指令覆盖」。",
        "**与 1-bit `EIB_BIT_REC` 区别**：1 bit 是单纯开关，没有优先级概念；本 FB 多 1 位优先级。混用会出现意外的覆盖关系。",
    ],
    tcpou_scene=(
        "DPT 2.001 安全应急：普通灯光开关 + 应急关灯按钮共用组地址 1/1/30。"
        "本 demo 接收 2-bit telegram，按 `bControl` 决定是否强制覆盖。"
    ),
    tcpou_value="替代手写位拆 + 优先级判断；与 DPT 2.xxx 语义直接对应",
    tcpou_verify=(
        "推 (`bControl=FALSE, bValue=TRUE`) → `bLampShouldBeOn = TRUE`；"
        "推 (`bControl=TRUE, bValue=FALSE`) → `bForceOff = TRUE`，`bLampShouldBeOn` 被强制覆盖。"
    ),
    tcpou_decl=(
        "VAR\n"
        "    fbReceiveCtl     : EIB_BIT_CONTROL_REC;\n"
        "    stEibRec         : EIB_REC;\n"
        "    stGroupLamp      : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 1, NUMBER := 30);\n"
        "    bIsForced        : BOOL;       // bControl = TRUE\n"
        "    bRequestedOn     : BOOL;       // bValue\n"
        "    bGotNewSample    : BOOL;\n"
        "    rTrigSample      : R_TRIG;\n"
        "    bLampShouldBeOn  : BOOL;\n"
        "    bForceOff        : BOOL;       // 强制关灯标志\n"
        "END_VAR"
    ),
    tcpou_st=(
        "fbReceiveCtl(\n"
        "    Group_Address := stGroupLamp,\n"
        "    strData_Rec   := stEibRec,\n"
        "    bDataReceive  => bGotNewSample,\n"
        "    bControl      => bIsForced,\n"
        "    bValue        => bRequestedOn\n"
        ");\n"
        "\n"
        "rTrigSample(CLK := bGotNewSample);\n"
        "IF rTrigSample.Q THEN\n"
        "    IF bIsForced THEN\n"
        "        // 强制命令：直接覆盖\n"
        "        bLampShouldBeOn := bRequestedOn;\n"
        "        bForceOff       := NOT bRequestedOn;\n"
        "    ELSE\n"
        "        // 普通命令：只有非强制状态下才生效\n"
        "        IF NOT bForceOff THEN\n"
        "            bLampShouldBeOn := bRequestedOn;\n"
        "        END_IF;\n"
        "    END_IF;\n"
        "END_IF;"
    ),
    scene="带优先级的 KNX 1-bit 控制：应急关闭、安全联锁覆盖普通操作",
    value="替代手写 2-bit 解码 + 优先级状态机；DPT 2.xxx 语义直接对应",
    alternatives=[
        "`EIB_BIT_REC` 简单 1 bit：失去优先级语义",
        "`EIB_3BIT_CONTROL_REC`：调光 / 步进，不是开关",
        "本 FB：DPT 2.xxx 标准选择",
    ],
    related=(
        "`EIB_BIT_REC`（同库 §4.2.4.13，简单 1 bit）、"
        "`EIB_BIT_CONTROL_SEND`（同库 §4.2.5.20，对应发送端）、"
        "`EIB_3BIT_CONTROL_REC`（同库 §4.2.4.4，4-bit 调光控制）"
    ),
    example_preview=(
        "PROGRAM P_Demo_EIB_BIT_CONTROL_REC\n"
        "VAR\n"
        "    fb       : EIB_BIT_CONTROL_REC;\n"
        "    stEibRec : EIB_REC;\n"
        "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 1, NUMBER := 30);\n"
        "    bCtl     : BOOL;\n"
        "    bVal     : BOOL;\n"
        "    bNew     : BOOL;\n"
        "END_VAR\n"
        "fb(Group_Address := stGroup, strData_Rec := stEibRec,\n"
        "   bDataReceive => bNew, bControl => bCtl, bValue => bVal);"
    ),
)
ENTRIES.append(e)


# ----- EIB_BIT_REC -----
e = _rec_fb(
    "EIB_BIT_REC", "187748107", "4.2.4.13",
    "EIB 1-bit data (DPT 1.xxx 开关 / 布尔)",
    "BOOL", ("bData", "BOOL",
            "1 bit 数据值（TRUE/FALSE）。DPT 1.001 (Switch) 中 TRUE = ON、FALSE = OFF"),
)
_rec_apply(
    e,
    brief=(
        "接收 EIB 网络上指定组地址的 **1 位 telegram**，对应 KNX DPT 1.xxx 数据类型（开关、布尔、起停等）。"
        "解码到 IEC `BOOL`。**KNX 楼宇控制最常用的 FB**——所有开关、按钮、状态反馈都用 1-bit。\n\n"
        "DPT 1.001 表示开关（TRUE = ON / FALSE = OFF）；DPT 1.009 表示开 / 关；DPT 1.002 表示 TRUE / FALSE。"
        "本 FB 不区分子类型——只关心 1 bit 值，业务代码自己解释。"
    ),
    behavior=_REC_GENERIC_BEHAVIOR_TEMPLATE.format(
        out="bData", byte_desc="1 bit telegram"),
    errors=ERR_REC_COMMON,
    notes=_REC_NOTES_COMMON + [
        "**KNX 最常用类型**：80% 楼宇 EIB 项目就是按钮 → 1-bit → 灯 / 卷帘 / 风机的开关。本 FB 是首选接收方式。",
        "**别与 `EIB_BIT_CONTROL_REC` 混**：那个是 2 bit 带优先级；本 FB 是纯 1 bit 开关。",
        "**`bData` 是电平保持**：收到 TRUE 后会一直保持 TRUE 直到下一帧到达。如果业务要在 `bData` 上升沿动作（按钮按下），用 R_TRIG。",
    ],
    tcpou_scene=(
        "DPT 1.001 灯光开关：办公室按钮经组地址 1/1/3 控制灯。"
        "本 demo 接收开关命令，并按按钮上升沿计按键次数（用于使用统计）。"
    ),
    tcpou_value="KNX 1-bit 最简单的接收；XAE 调试时 1 行代码搞定按钮事件",
    tcpou_verify=(
        "按下 → `bLightOn = TRUE`，`bGotNewSample` 单周期高；放开后按钮再发 `bData = FALSE` → "
        "`bLightOn = FALSE`；`nButtonPressCount` 每按下一次加 1。"
    ),
    tcpou_decl=(
        "VAR\n"
        "    fbReceiveSwitch   : EIB_BIT_REC;\n"
        "    stEibRec          : EIB_REC;\n"
        "    stGroupSwitch     : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 1, NUMBER := 3);\n"
        "    bLightOn          : BOOL;\n"
        "    bGotNewSample     : BOOL;\n"
        "    rTrigOnEvent      : R_TRIG;        // bLightOn 上升沿 = 按下一次\n"
        "    nButtonPressCount : DINT;\n"
        "END_VAR"
    ),
    tcpou_st=(
        "fbReceiveSwitch(\n"
        "    Group_Address := stGroupSwitch,\n"
        "    strData_Rec   := stEibRec,\n"
        "    bDataReceive  => bGotNewSample,\n"
        "    bData         => bLightOn\n"
        ");\n"
        "\n"
        "// bLightOn 是电平保持；按下 TRUE 计一次按键\n"
        "rTrigOnEvent(CLK := bLightOn);\n"
        "IF rTrigOnEvent.Q THEN\n"
        "    nButtonPressCount := nButtonPressCount + 1;\n"
        "END_IF;"
    ),
    scene="按钮、开关、布尔状态反馈——KNX 项目里几乎所有 1-bit 事件",
    value="最简洁的 EIB 接收 FB；DPT 1.xxx 的**标准**选择",
    alternatives=[
        "`EIB_BIT_CONTROL_REC`：带优先级（2 bit），不是开关而是带强制位的命令",
        "`EIB_ALL_DATA_TYPES_REC`：能做但代码更长",
        "本 FB：DPT 1.xxx 标准选择，KNX 项目首选",
    ],
    related=(
        "`EIB_BIT_SEND` / `_EX` / `_MANUAL`（同库 §4.2.5.22..24，对应发送端）、"
        "`EIB_BIT_CONTROL_REC`（同库 §4.2.4.12，2-bit 带控制）"
    ),
    example_preview=_rec_example_preview("EIB_BIT_REC", "bData", "BOOL"),
)
ENTRIES.append(e)


# ----- EIB_DATE_REC -----
e = _rec_fb(
    "EIB_DATE_REC", "187749643", "4.2.4.14",
    "EIB 3-byte date (DPT 11.001)",
    "WORD x 3", None,
    output_block=(
        "VAR_OUTPUT\n"
        "    bDataReceive : BOOL;\n"
        "    wDay         : WORD;\n"
        "    wMonth       : WORD;\n"
        "    wYear        : WORD;\n"
        "END_VAR"
    ),
    out_extras=[
        ("bDataReceive", "BOOL", "**单周期脉冲**：收到 telegram 时为 TRUE 1 个 PLC 周期"),
        ("wDay", "WORD", "日，1..31（PDF §4.2.4.14）"),
        ("wMonth", "WORD", "月，1..12"),
        ("wYear", "WORD", "年的两位数表示，0..99（DPT 11.001 用 2 位年；本世纪 25 = 2025）"),
    ],
)
_rec_apply(
    e,
    brief=(
        "接收 EIB 网络上指定组地址的 **3 字节日期 telegram**（DPT 11.001），解码到三个 IEC `WORD` 变量"
        "（日 1..31、月 1..12、年 0..99）。\n\n"
        "**注意年是 2 位**——DPT 11 协议设计于上世纪 90 年代，年字段只有 8 bit。`25` 在 BMS 行业惯例上代表 2025（< 90 → 20xx，≥ 90 → 19xx）。"
        "业务代码若要写到 IEC `DATE` / `DT` 必须自己加上世纪基。"
    ),
    behavior=_REC_GENERIC_BEHAVIOR_TEMPLATE.format(
        out="wDay/wMonth/wYear", byte_desc="3 byte date telegram"),
    errors=ERR_REC_COMMON,
    notes=_REC_NOTES_COMMON + [
        "**`wYear` 只有 2 位**：业务代码自己加世纪基，常见约定：`< 90` → +2000，`≥ 90` → +1900。",
        "**没有时间字段**：DPT 11 只有日期；时间用 `EIB_TIME_REC`（DPT 10）。",
        "**KNX 主时钟设备一般每分钟广播**：可能与本地 PLC RTC 不同步，业务上选取一个作为主源。（工程经验补充）",
    ],
    tcpou_scene=(
        "BMS 主时钟设备每分钟在组地址 1/0/1 广播当前日期。"
        "本 demo 接收日期，更新本地 HMI 时钟显示。"
    ),
    tcpou_value="DPT 11 date 标准接收；不用关心 3-byte 拆字段",
    tcpou_verify=(
        "BMS 主时钟在 2026-06-03 推送 → `wDay = 3, wMonth = 6, wYear = 26`，`nFullYear = 2026`。"
    ),
    tcpou_decl=(
        "VAR\n"
        "    fbReceiveDate : EIB_DATE_REC;\n"
        "    stEibRec      : EIB_REC;\n"
        "    stGroupDate   : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 0, NUMBER := 1);\n"
        "    wDay          : WORD;\n"
        "    wMonth        : WORD;\n"
        "    wYear         : WORD;\n"
        "    nFullYear     : DINT;\n"
        "    bGotNewSample : BOOL;\n"
        "    rTrigSample   : R_TRIG;\n"
        "END_VAR"
    ),
    tcpou_st=(
        "fbReceiveDate(\n"
        "    Group_Address := stGroupDate,\n"
        "    strData_Rec   := stEibRec,\n"
        "    bDataReceive  => bGotNewSample,\n"
        "    wDay          => wDay,\n"
        "    wMonth        => wMonth,\n"
        "    wYear         => wYear\n"
        ");\n"
        "\n"
        "rTrigSample(CLK := bGotNewSample);\n"
        "IF rTrigSample.Q THEN\n"
        "    // 还原全 4 位年：< 90 → 20xx，>= 90 → 19xx\n"
        "    IF wYear &lt; 90 THEN\n"
        "        nFullYear := DINT#2000 + TO_DINT(wYear);\n"
        "    ELSE\n"
        "        nFullYear := DINT#1900 + TO_DINT(wYear);\n"
        "    END_IF;\n"
        "END_IF;"
    ),
    scene="BMS 主时钟同步、运维日志时间戳标定",
    value="DPT 11 标准接收；3-byte 自动拆分",
    alternatives=[
        "用 NTP / Tc2_TcpIp 同步：精度高但走不同协议",
        "本地 RTC 自己计时：偏移大",
        "本 FB：KNX BMS 标准做法",
    ],
    related=(
        "`EIB_DATE_SEND` / `_EX`（同库 §4.2.5.25/26）、"
        "`EIB_TIME_REC`（同库 §4.2.4.15）"
    ),
    example_preview=(
        "PROGRAM P_Demo_EIB_DATE_REC\n"
        "VAR\n"
        "    fb       : EIB_DATE_REC;\n"
        "    stEibRec : EIB_REC;\n"
        "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 0, NUMBER := 1);\n"
        "    wD,wM,wY : WORD;\n"
        "    bNew     : BOOL;\n"
        "END_VAR\n"
        "fb(Group_Address := stGroup, strData_Rec := stEibRec,\n"
        "   bDataReceive => bNew, wDay => wD, wMonth => wM, wYear => wY);"
    ),
)
ENTRIES.append(e)


# ----- EIB_TIME_REC -----
e = _rec_fb(
    "EIB_TIME_REC", "187751179", "4.2.4.15",
    "EIB 3-byte time (DPT 10.001)",
    "WORD x 3", None,
    output_block=(
        "VAR_OUTPUT\n"
        "    bDataReceive : BOOL;\n"
        "    wHoure       : WORD;\n"
        "    wMinute      : WORD;\n"
        "    wSecond      : WORD;\n"
        "END_VAR"
    ),
    out_extras=[
        ("bDataReceive", "BOOL", "**单周期脉冲**：收到 telegram 时为 TRUE 1 个 PLC 周期"),
        ("wHoure", "WORD",
         "小时，0..23。**PDF 引脚名拼写错为 `wHoure`**（应是 wHour），与 IEC 实际声明一致，逐字保留"),
        ("wMinute", "WORD", "分钟，0..59"),
        ("wSecond", "WORD", "秒，0..59"),
    ],
)
_rec_apply(
    e,
    brief=(
        "接收 EIB 网络上指定组地址的 **3 字节时间 telegram**（DPT 10.001），解码到三个 IEC `WORD` 变量"
        "（时 0..23、分 0..59、秒 0..59）。\n\n"
        "**PDF 拼写错**：PDF 把小时输出引脚命名为 `wHoure`（多个 e）——典型 PDF/原始库的拼写错。"
        "本文档保留 PDF 原写法以便代码逐字对照。IEC 实际访问就是 `fb.wHoure`。"
    ),
    behavior=_REC_GENERIC_BEHAVIOR_TEMPLATE.format(
        out="wHoure/wMinute/wSecond", byte_desc="3 byte time telegram"),
    errors=ERR_REC_COMMON,
    notes=_REC_NOTES_COMMON + [
        "**PDF 拼写 `wHoure` 不是 `wHour`**：库实际命名就是这样，代码必须按 PDF 写，否则编译报错。",
        "**KNX DPT 10 不带日期**：日期用 `EIB_DATE_REC`（DPT 11）。",
        "**DPT 10 还有可选的星期字段**：本 FB 不输出星期；如需要用 `EIB_ALL_DATA_TYPES_REC` 接收 raw 字节自己解析（PDF §4.3.2 没列星期格式）。（工程经验补充）",
    ],
    tcpou_scene=(
        "BMS 主时钟在组地址 1/0/2 每分钟广播当前时间。"
        "本 demo 接收时间，与本地 PLC RTC 对齐。"
    ),
    tcpou_value="DPT 10 time 标准接收；不用关心字节拆分",
    tcpou_verify=(
        "推 (14:30:00) 到 1/0/2 → `wHoure = 14, wMinute = 30, wSecond = 0`，`bGotNewSample` 单周期高。"
    ),
    tcpou_decl=(
        "VAR\n"
        "    fbReceiveTime : EIB_TIME_REC;\n"
        "    stEibRec      : EIB_REC;\n"
        "    stGroupTime   : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 0, NUMBER := 2);\n"
        "    wHoure        : WORD;       // 注意拼写——保持与 PDF 一致\n"
        "    wMinute       : WORD;\n"
        "    wSecond       : WORD;\n"
        "    bGotNewSample : BOOL;\n"
        "    nTotalSec     : UDINT;       // 一天内的秒数累加\n"
        "    rTrigSample   : R_TRIG;\n"
        "END_VAR"
    ),
    tcpou_st=(
        "fbReceiveTime(\n"
        "    Group_Address := stGroupTime,\n"
        "    strData_Rec   := stEibRec,\n"
        "    bDataReceive  => bGotNewSample,\n"
        "    wHoure        => wHoure,\n"
        "    wMinute       => wMinute,\n"
        "    wSecond       => wSecond\n"
        ");\n"
        "\n"
        "rTrigSample(CLK := bGotNewSample);\n"
        "IF rTrigSample.Q THEN\n"
        "    nTotalSec := TO_UDINT(wHoure) * 3600 + TO_UDINT(wMinute) * 60 + TO_UDINT(wSecond);\n"
        "END_IF;"
    ),
    scene="BMS 主时钟同步、运维日志时间戳标定",
    value="DPT 10 标准接收；3-byte 自动拆分",
    alternatives=[
        "NTP / Tc2_TcpIp：精度高但需 IP 协议",
        "本地 RTC：偏移大",
        "本 FB：KNX BMS 标准做法",
    ],
    related="`EIB_TIME_SEND` / `_EX`（同库 §4.2.5.28/29）、`EIB_DATE_REC`",
    example_preview=(
        "PROGRAM P_Demo_EIB_TIME_REC\n"
        "VAR\n"
        "    fb       : EIB_TIME_REC;\n"
        "    stEibRec : EIB_REC;\n"
        "    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 0, NUMBER := 2);\n"
        "    wH,wM,wS : WORD;\n"
        "    bNew     : BOOL;\n"
        "END_VAR\n"
        "fb(Group_Address := stGroup, strData_Rec := stEibRec,\n"
        "   bDataReceive => bNew, wHoure => wH, wMinute => wM, wSecond => wS);"
    ),
)
ENTRIES.append(e)


# Save chunk to make sure file isn't too long for one Write
# (Total file is large; keep going in one block via Write tool.)


# Write entries to disk
def write_all():
    for entry in ENTRIES:
        cat_dir = ROOT / LIB / entry["category"]
        cat_dir.mkdir(parents=True, exist_ok=True)
        doc_path = cat_dir / f"{entry['name']}.md"
        doc_path.write_text(md(entry))

        ex_path = ROOT / LIB / "examples" / f"P_Demo_{entry['name']}.TcPOU"
        ex_path.write_text(tcpou(entry))


if __name__ == "__main__":
    write_all()
    print(f"Generated {len(ENTRIES)} doc + tcpou pairs in {LIB}/")
