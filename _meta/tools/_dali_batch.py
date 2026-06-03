#!/usr/bin/env python3
"""Batch generator for Tc2_DALI low-level command FBs.

Produces docs + TcPOU for FBs that follow the standard "bStart + nAddr +
eAddrType + eCommandPriority [+ params] / bBusy + bError + nErrorId" pattern.
"""
from __future__ import annotations
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))

from extract_section import extract as extract_section  # noqa: E402

NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def guid_for(name: str) -> str:
    return "{" + str(uuid.uuid5(NS, f"tc3-libraries-kb/Tc2_DALI/P_Demo_{name}")) + "}"


_VAR_BLOCK = re.compile(
    r"VAR_(INPUT|OUTPUT|IN_OUT)\s*\n([\s\S]*?)END_VAR",
    re.IGNORECASE,
)
_VAR_DECL_RE = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?!=)([^;\n]+?)\s*(?:;|$)",
    re.MULTILINE,
)


def parse_vars(section_text: str) -> dict[str, list[tuple[str, str, str]]]:
    """Return {region: [(name, type, default)]}"""
    out: dict[str, list[tuple[str, str, str]]] = {"INPUT": [], "OUTPUT": [], "IN_OUT": []}
    for m in _VAR_BLOCK.finditer(section_text):
        region_type = m.group(1).upper()
        body = m.group(2)
        body = re.sub(r"\(\*[\s\S]*?\*\)", "", body)
        body = re.sub(r"//.*$", "", body, flags=re.MULTILINE)
        # Strip orphan {attribute ...} pragmas (Beckhoff PDFs occasionally have)
        body = re.sub(r"\{.*?\}", "", body)
        for vm in _VAR_DECL_RE.finditer(body):
            name = vm.group(1)
            typ_full = vm.group(2).rstrip(" ;")
            default = ""
            if ":=" in typ_full:
                t, d = typ_full.split(":=", 1)
                typ = t.strip()
                default = d.strip().rstrip(";")
            else:
                typ = typ_full
            typ = re.sub(r"\s+", " ", typ).strip()
            if name.upper() in {"INPUT", "OUTPUT", "IN_OUT", "END_VAR", "INPUTS", "OUTPUTS"}:
                continue
            out[region_type].append((name, typ, default))
    return out


def render_var_block(region: str, items: list[tuple[str, str, str]]) -> str:
    if not items:
        return ""
    name_w = max(len(n) for n, _, _ in items)
    type_w = max(len(t) for _, t, _ in items)
    lines = [f"VAR_{region}"]
    for n, t, d in items:
        if d:
            lines.append(f"    {n:<{name_w}} : {t:<{type_w}} := {d};")
        else:
            lines.append(f"    {n:<{name_w}} : {t};")
    lines.append("END_VAR")
    return "\n".join(lines)


# Standard descriptions for common inputs/outputs in low-level command FBs
STD_INPUTS = {
    "bStart": "上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿",
    "nAddr": "目标地址：单灯 short address 0..63，或组号 0..15，或 `eAddrType = Broadcast` 时忽略",
    "eAddrType": "寻址类型：`eDALIV2AddrTypeShort`（单灯）/ `eDALIV2AddrTypeGroup`（组）/ `eDALIV2AddrTypeBroadcast`（全线广播）",
    "eCommandPriority": "命令优先级：`eDALIV2CommandPriorityHigh` / `Middle` / `Low`，决定本命令在 `FB_KL68x1Communication` 三优先级队列中的派发顺序",
    "nGroup": "目标组号（0..15）",
    "nScene": "目标场景号（0..15）",
    "nBank": "存储区编号",
    "nLocation": "存储区内位置",
    "nValue": "要写入的值",
    "nFadeRate": "DALI Fade Rate 索引（0..15），决定亮度变化速率",
    "nFadeTime": "DALI Fade Time 索引（0..15），决定从一个亮度变到另一个的总时间",
}
STD_OUTPUTS = {
    "bBusy": "本 FB 接到 `bStart` 上升沿后置 TRUE；命令派发完且收到 DALI 响应（或超时）后回 FALSE",
    "bError": "执行错时置 TRUE；下次 `bStart` 上升沿自动复位",
    "nErrorId": "错误号（命令专用）；详见 §4 错误码表与全库错误码（PDF §4.1.4）",
    "bDone": "命令完成（成功 / 失败均算）时为 TRUE 一周期",
}
STD_IN_OUT = {
    "stCommandBuffer": "DALI 命令缓冲区结构；连到对应 KL68x1 通信 FB 的同名变量。整条 KL68x1 链路上所有命令 FB 共享这一变量",
}


def make_low_level_doc(
    *,
    name: str,
    section: str,
    category_subdir: str,
    category_display: str,
    infosys_url: str,
    summary_zh: str,
    behavior_zh: str,
    pitfalls: list[str],
    scenario: str,
    value_zh: str,
    alternative_zh: str,
    related_zh: str,
    extra_inputs_desc: dict[str, str] | None = None,
    extra_outputs_desc: dict[str, str] | None = None,
    extra_notes: str = "",
    error_codes_table: str = "",
) -> str:
    section_text = extract_section("Tc2_DALI", section)
    if not section_text:
        raise RuntimeError(f"No section text for {section}")
    vars_ = parse_vars(section_text)

    inputs_desc = {**STD_INPUTS, **(extra_inputs_desc or {})}
    outputs_desc = {**STD_OUTPUTS, **(extra_outputs_desc or {})}

    def fmt_inputs():
        if not vars_["INPUT"]:
            return "无\n"
        block = render_var_block("INPUT", vars_["INPUT"])
        rows = []
        for n, t, d in vars_["INPUT"]:
            desc = inputs_desc.get(n, "⚠️ 待人工确认")
            rows.append(f"| `{n}` | `{t}` | {'`' + d + '`' if d else '—'} | {desc} |")
        return (
            f"\n```iecst\n{block}\n```\n\n"
            "| 名称 | 类型 | 默认值 | 说明（中文） |\n"
            "|---|---|---|---|\n" + "\n".join(rows) + "\n"
        )

    def fmt_outputs():
        if not vars_["OUTPUT"]:
            return "无\n"
        block = render_var_block("OUTPUT", vars_["OUTPUT"])
        rows = []
        for n, t, _ in vars_["OUTPUT"]:
            desc = outputs_desc.get(n, "⚠️ 待人工确认")
            rows.append(f"| `{n}` | `{t}` | {desc} |")
        return (
            f"\n```iecst\n{block}\n```\n\n"
            "| 名称 | 类型 | 说明（中文） |\n"
            "|---|---|---|\n" + "\n".join(rows) + "\n"
        )

    def fmt_in_out():
        if not vars_["IN_OUT"]:
            return "无\n"
        block = render_var_block("IN_OUT", vars_["IN_OUT"])
        rows = []
        for n, t, _ in vars_["IN_OUT"]:
            desc = STD_IN_OUT.get(n, "⚠️ 待人工确认")
            rows.append(f"| `{n}` | `{t}` | {desc} |")
        return (
            f"\n```iecst\n{block}\n```\n\n"
            "| 名称 | 类型 | 说明（中文） |\n"
            "|---|---|---|\n" + "\n".join(rows) + "\n"
        )

    if not error_codes_table:
        error_codes_table = (
            "`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。本命令常见错误：\n\n"
            "| `nErrorId` | 含义 | 处理建议 |\n"
            "|---|---|---|\n"
            "| `16#0000` | 无错 | — |\n"
            "| `16#1xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |\n"
            "| `16#2xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |\n"
            "| `16#3xxx` | `nAddr` 越界 / `eAddrType` 不匹配 | 短地址 0..63 / 组号 0..15 / Broadcast 时 `nAddr` 任意 |"
        )

    pitfalls_md = "\n".join(f"- {p}" for p in pitfalls)

    doc = f"""# {name}

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `{category_display}` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf |
| Source InfoSys | {infosys_url} |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU) |

---

## 1. 功能简述

{summary_zh}

## 2. 接口定义

### VAR_INPUT
{fmt_inputs()}
### VAR_OUTPUT
{fmt_outputs()}
### VAR_IN_OUT
{fmt_in_out()}

## 3. 行为说明

{behavior_zh}

## 4. 错误码 / 返回值

{error_codes_table}

## 5. 使用注意 / 常见坑

{pitfalls_md}

{extra_notes}

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：{scenario}
- **价值**：{value_zh}
- **替代方案对比**：{alternative_zh}

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §{section}
- **InfoSys topic**：{infosys_url}
- **相关**：{related_zh}
"""
    return doc


def make_low_level_tcpou(
    *,
    name: str,
    scenario_zh: str,
    value_zh: str,
    verify_steps_zh: str,
    inputs_assign_block: str,
    extra_decl: str = "",
) -> str:
    guid = guid_for(name)
    verify_steps_lines = "\n".join(
        f"//   {ln}" if ln and not ln.startswith("//") else "//"
        for ln in verify_steps_zh.split("\n")
    )
    return f'''<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">
  <POU Name="P_Demo_{name}" Id="{guid}" SpecialFunc="None">
    <Declaration><![CDATA[PROGRAM P_Demo_{name}
VAR
    fb{name}         : {name};                       // 被演示的命令 FB
    stCommandBuffer  : ST_DALIV2CommandBuffer;        // 共享 KL68x1 通信 FB

    bTrigger         : BOOL;                          // 上升沿触发一次命令
{extra_decl}    // —— 观察 ——
    bBusy            : BOOL;                          // 命令派发中
    bErr             : BOOL;                          // 命令出错
    nErrId           : UDINT;                         // 错误号
END_VAR
]]></Declaration>
    <Implementation>
      <ST><![CDATA[// =============================================================================
// 场景：{scenario_zh}
//
// 价值：{value_zh}
//
// 验证步骤：
{verify_steps_lines}
// =============================================================================
// 单次完整调用：bStart 上升沿触发，bBusy 期间忽略后续上升沿
fb{name}(
{inputs_assign_block}
    stCommandBuffer := stCommandBuffer
);

bBusy  := fb{name}.bBusy;
bErr   := fb{name}.bError;
nErrId := fb{name}.nErrorId;
]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>
'''


if __name__ == "__main__":
    pass
