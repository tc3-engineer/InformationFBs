#!/usr/bin/env python3
"""Helper to generate Tc2_DALI doc + TcPOU pairs from PDF section text.

Library-private (filename prefix `_dali_`). DO NOT use for other libraries.
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
        for vm in _VAR_DECL_RE.finditer(body):
            full = vm.group(0)
            name = vm.group(1)
            typ = vm.group(2).rstrip(" ;")
            default = ""
            if ":=" in typ:
                t, d = typ.split(":=", 1)
                typ = t.strip()
                default = d.strip().rstrip(";")
            typ = re.sub(r"\s+", " ", typ).strip()
            if name.upper() not in {"INPUT", "OUTPUT", "IN_OUT", "END_VAR"}:
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


def make_doc_skeleton(
    name: str,
    section: str,
    category: str,
    infosys_url: str,
    summary_zh: str,
    behavior_zh: str,
    inputs_desc: dict[str, str],
    outputs_desc: dict[str, str],
    in_out_desc: dict[str, str],
    pitfalls: list[str],
    scenario: str,
    value: str,
    alternative: str,
    related: str,
    error_codes_table: str = "",
    extra_notes: str = "",
) -> str:
    section_text = extract_section("Tc2_DALI", section)
    vars_ = parse_vars(section_text)

    def desc(items, desc_map, region):
        block = render_var_block(region, items)
        return block

    def desc_table_inputs(items):
        rows = []
        for n, t, d in items:
            desc = inputs_desc.get(n, "⚠️ 待人工确认")
            rows.append(f"| `{n}` | `{t}` | {'`' + d + '`' if d else '—'} | {desc} |")
        if not rows:
            return "无"
        return "\n".join(rows)

    def desc_table_outputs(items):
        rows = []
        for n, t, _ in items:
            desc = outputs_desc.get(n, "⚠️ 待人工确认")
            rows.append(f"| `{n}` | `{t}` | {desc} |")
        if not rows:
            return "无"
        return "\n".join(rows)

    def desc_table_in_out(items):
        rows = []
        for n, t, _ in items:
            desc = in_out_desc.get(n, "⚠️ 待人工确认")
            rows.append(f"| `{n}` | `{t}` | {desc} |")
        if not rows:
            return "无"
        return "\n".join(rows)

    input_block = render_var_block("INPUT", vars_["INPUT"])
    output_block = render_var_block("OUTPUT", vars_["OUTPUT"])
    in_out_block = render_var_block("IN_OUT", vars_["IN_OUT"])

    input_block_md = f"\n```iecst\n{input_block}\n```\n\n| 名称 | 类型 | 默认值 | 说明（中文） |\n|---|---|---|---|\n{desc_table_inputs(vars_['INPUT'])}\n" if vars_["INPUT"] else "无\n"
    output_block_md = f"\n```iecst\n{output_block}\n```\n\n| 名称 | 类型 | 说明（中文） |\n|---|---|---|\n{desc_table_outputs(vars_['OUTPUT'])}\n" if vars_["OUTPUT"] else "无\n"
    in_out_block_md = f"\n```iecst\n{in_out_block}\n```\n\n| 名称 | 类型 | 说明（中文） |\n|---|---|---|\n{desc_table_in_out(vars_['IN_OUT'])}\n" if vars_["IN_OUT"] else "无\n"

    pitfalls_md = "\n".join(f"- {p}" for p in pitfalls)

    if not error_codes_table:
        error_codes_table = (
            "`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。"
            "本命令常见错误：\n\n"
            "| `nErrorId` | 含义 | 处理建议 |\n"
            "|---|---|---|\n"
            "| `16#0000` | 无错 | — |\n"
            "| `16#0xxx` | 缓冲区溢出 | 缩短 `FB_KL6821Communication` 任务节拍 |\n"
            "| `16#1xxx` | DALI 总线无响应 / 设备未应答 | 检查 `nAddr` 与 `eAddrType` 设置；确认设备在线 |"
        )

    doc = f"""# {name}

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `{category}` |
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
{input_block_md}
### VAR_OUTPUT
{output_block_md}
### VAR_IN_OUT
{in_out_block_md}

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

```iecst
PROGRAM P_Demo_{name}
VAR
    fb{name} : {name};
    stCommandBuffer : ST_DALIV2CommandBuffer;
    bTrigger : BOOL;
END_VAR

fb{name}(bStart := bTrigger, stCommandBuffer := stCommandBuffer);
```

完整可运行版本见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：{scenario}
- **价值**：{value}
- **替代方案对比**：{alternative}

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §{section}
- **InfoSys topic**：{infosys_url}
- **相关**：{related}
"""
    return doc


def make_tcpou_simple(
    name: str,
    inputs_assigns: str,
    scenario: str,
    value: str,
    verify_steps: str,
    declarations_extra: str = "",
    extra_calls: str = "",
) -> str:
    """Generic TcPOU for a typical FB_DALIV2* command FB with bStart + bBusy/bError."""
    guid = guid_for(name)
    return f'''<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">
  <POU Name="P_Demo_{name}" Id="{guid}" SpecialFunc="None">
    <Declaration><![CDATA[PROGRAM P_Demo_{name}
VAR
    fb{name}        : {name};                       // 被演示的 DALI 命令 FB
    stCommandBuffer : ST_DALIV2CommandBuffer;        // 与 FB_KL6821Communication 共享的命令缓冲

    bTrigger        : BOOL;                          // 上升沿触发一次命令
{declarations_extra}
    // —— 观察 ——
    bBusy           : BOOL;                          // 命令正在执行
    bErr            : BOOL;                          // 命令出错
    nErrId          : UDINT;                         // 错误号
END_VAR
]]></Declaration>
    <Implementation>
      <ST><![CDATA[// =============================================================================
// 场景：{scenario}
//
// 价值：{value}
//
// 验证步骤：
{verify_steps}
// =============================================================================
// 单次完整调用：bStart 上升沿触发，bBusy 期间忽略后续上升沿
fb{name}(
{inputs_assigns}
    stCommandBuffer := stCommandBuffer
);
{extra_calls}
bBusy  := fb{name}.bBusy;
bErr   := fb{name}.bError;
nErrId := fb{name}.nErrorId;
]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>
'''


if __name__ == "__main__":
    # smoke test
    text = extract_section("Tc2_DALI", "4.1.2.3.3.1")
    vars_ = parse_vars(text)
    for k, v in vars_.items():
        print(k, v)
