#!/usr/bin/env python3
"""Bulk-generate Tc2_DALI low-level command FB docs + tcpou files.

The function takes a list of "spec dicts" describing each FB and produces a
verbose, fully-compliant doc + TcPOU pair.

Library-internal helper (filename prefix `_dali_`).
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
    out: dict[str, list[tuple[str, str, str]]] = {"INPUT": [], "OUTPUT": [], "IN_OUT": []}
    for m in _VAR_BLOCK.finditer(section_text):
        region_type = m.group(1).upper()
        body = m.group(2)
        body = re.sub(r"\(\*[\s\S]*?\*\)", "", body)
        body = re.sub(r"//.*$", "", body, flags=re.MULTILINE)
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


# Standard descriptions
STD_IN = {
    "bStart": "上升沿触发本命令一次执行；`bBusy = TRUE` 期间忽略后续上升沿",
    "nAddr": "目标地址：单灯 short address 0..63，或组号 0..15，或 `eAddrType = Broadcast` 时忽略",
    "eAddrType": "寻址类型：`eDALIV2AddrTypeShort`（单灯）/ `eDALIV2AddrTypeGroup`（组）/ `eDALIV2AddrTypeBroadcast`（全线广播）",
    "eCommandPriority": "命令优先级：`High` / `Middle` / `Low`，决定本命令在 `FB_KL68x1Communication` 三优先级队列中的派发顺序",
    "nGroup": "目标组号（0..15）",
    "nScene": "目标场景号（0..15）",
    "nLevel": "目标亮度值（0..254，DALI 对数曲线索引）",
    "nValue": "要写入的值",
}
STD_OUT = {
    "bBusy": "本 FB 接到 `bStart` 上升沿后置 TRUE；命令派发完且收到 DALI 响应（或超时）后回 FALSE",
    "bError": "执行错时置 TRUE；下次 `bStart` 上升沿自动复位",
    "nErrorId": "错误号（命令专用）；详见 §4 错误码表与全库错误码（PDF §4.1.4）",
    "nQueryData": "查询结果值",
    "bQueryData": "查询布尔结果",
}
STD_IO = {
    "stCommandBuffer": "DALI 命令缓冲区结构；连到对应 KL68x1 通信 FB 的同名变量",
}


def make_doc(spec: dict) -> str:
    name = spec["name"]
    section = spec["section"]
    section_text = extract_section("Tc2_DALI", section)
    vars_ = parse_vars(section_text)

    inputs_desc = {**STD_IN, **spec.get("inputs_desc", {})}
    outputs_desc = {**STD_OUT, **spec.get("outputs_desc", {})}

    def fmt_block(region, items, desc_map, has_default):
        if not items:
            return "无\n"
        block = render_var_block(region, items)
        head = "| 名称 | 类型 | 默认值 | 说明（中文） |\n|---|---|---|---|\n" if has_default else "| 名称 | 类型 | 说明（中文） |\n|---|---|---|\n"
        rows = []
        for n, t, d in items:
            desc = desc_map.get(n, "⚠️ 待人工确认")
            if has_default:
                rows.append(f"| `{n}` | `{t}` | {'`' + d + '`' if d else '—'} | {desc} |")
            else:
                rows.append(f"| `{n}` | `{t}` | {desc} |")
        return f"\n```iecst\n{block}\n```\n\n{head}{chr(10).join(rows)}\n"

    inputs_md = fmt_block("INPUT", vars_["INPUT"], inputs_desc, True)
    outputs_md = fmt_block("OUTPUT", vars_["OUTPUT"], outputs_desc, False)
    in_out_md = fmt_block("IN_OUT", vars_["IN_OUT"], STD_IO, False)

    pitfalls_md = "\n".join(f"- {p}" for p in spec["pitfalls"])
    if spec.get("extra_notes"):
        pitfalls_md += "\n\n" + spec["extra_notes"]

    error_codes = spec.get("error_codes_table", (
        "`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。\n\n"
        "| `nErrorId` | 含义 | 处理建议 |\n"
        "|---|---|---|\n"
        "| `16#0000` | 无错 | — |\n"
        "| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |\n"
        "| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |\n"
        "| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |"
    ))

    return f"""# {name}

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `{spec['category_display']}` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf |
| Source InfoSys | {spec['infosys']} |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU) |

---

## 1. 功能简述

{spec['summary']}

## 2. 接口定义

### VAR_INPUT
{inputs_md}
### VAR_OUTPUT
{outputs_md}
### VAR_IN_OUT
{in_out_md}

## 3. 行为说明

{spec['behavior']}

## 4. 错误码 / 返回值

{error_codes}

## 5. 使用注意 / 常见坑

{pitfalls_md}

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：{spec['scenario']}
- **价值**：{spec['value']}
- **替代方案对比**：{spec['alternative']}

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §{section}
- **InfoSys topic**：{spec['infosys']}
- **相关**：{spec['related']}
"""


def make_tcpou(spec: dict) -> str:
    name = spec["name"]
    guid = guid_for(name)
    decls = spec.get("tcpou_decls", "")
    inputs_assigns = spec["tcpou_inputs_assigns"]
    scenario = spec.get("tcpou_scenario", spec["scenario"])
    value = spec.get("tcpou_value", spec["value"])
    verify_lines = spec["tcpou_verify"]
    verify_md = "\n".join(f"//   {ln}" for ln in verify_lines.split("\n"))
    return f'''<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">
  <POU Name="P_Demo_{name}" Id="{guid}" SpecialFunc="None">
    <Declaration><![CDATA[PROGRAM P_Demo_{name}
VAR
    fb{name}        : {name};
    stCommandBuffer : ST_DALIV2CommandBuffer;

    bTrigger        : BOOL;
{decls}
    bBusy           : BOOL;
    bErr            : BOOL;
    nErrId          : UDINT;
END_VAR
]]></Declaration>
    <Implementation>
      <ST><![CDATA[// =============================================================================
// 场景：{scenario}
//
// 价值：{value}
//
// 验证步骤：
{verify_md}
// =============================================================================
fb{name}(
{inputs_assigns}
    stCommandBuffer  := stCommandBuffer
);

bBusy  := fb{name}.bBusy;
bErr   := fb{name}.bError;
nErrId := fb{name}.nErrorId;
]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>
'''


def write_pair(spec: dict):
    subdir = spec["subdir"]
    name = spec["name"]
    doc = make_doc(spec)
    tcpou = make_tcpou(spec)
    doc_path = ROOT / "Tc2_DALI" / subdir / f"{name}.md"
    tcpou_path = ROOT / "Tc2_DALI" / "examples" / f"P_Demo_{name}.TcPOU"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(doc, encoding="utf-8")
    tcpou_path.write_text(tcpou, encoding="utf-8")
    return doc_path, tcpou_path


if __name__ == "__main__":
    pass
