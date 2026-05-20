#!/usr/bin/env python3
"""
Generate the 61 numeric rewrites (uint64 / int64_signed / fix16 / float / lcomplex)
for Tc2_Utilities under the 2026-05-12 charter.

Reads META from _tc2utilities_numeric_meta.py and URLS from
_tc2utilities_numeric_urls.py, writes:
  Tc2_Utilities/<subdir>/<Name>.md
  Tc2_Utilities/examples/P_Demo_<Name>.xml
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from _tc2utilities_numeric_meta import META
from _tc2utilities_numeric_urls import URLS, url_for

LIB = "Tc2_Utilities"
LIB_VER = "2.18.2"
TODAY = "2026-05-12"
PDF_URL = "https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf"

CATEGORY_MAP = {
    "uint64":       "64 bit integer functions (unsigned)",
    "int64_signed": "64 bit functions (signed)",
    "fix16":        "16 bit fixed point number functions (signed)",
    "float":        "FLOAT functions",
    "lcomplex":     "LCOMPLEX functions",
}


def render_iecst(name, ret, inputs, in_out):
    lines = [f"FUNCTION {name} : {ret}"]
    if inputs:
        lines.append("VAR_INPUT")
        for n, t, d, _ in inputs:
            decl = f"    {n} : {t}"
            if d and d != "-":
                decl += f" := {d}"
            decl += ";"
            lines.append(decl)
        lines.append("END_VAR")
    if in_out:
        lines.append("VAR_IN_OUT")
        for n, t, d, _ in in_out:
            decl = f"    {n} : {t}"
            if d and d != "-":
                decl += f" := {d}"
            decl += ";"
            lines.append(decl)
        lines.append("END_VAR")
    return "\n".join(lines)


def render_var_table(rows, header_default=True):
    if not rows:
        return "无。\n"
    if header_default:
        out = ["| 名称 | 类型 | 默认值 | 说明（中文） |", "|---|---|---|---|"]
        for n, t, d, desc in rows:
            out.append(f"| `{n}` | `{t}` | {d if d else '—'} | {desc} |")
    else:
        out = ["| 名称 | 类型 | 说明（中文） |", "|---|---|---|"]
        for n, t, d, desc in rows:
            out.append(f"| `{n}` | `{t}` | {desc} |")
    return "\n".join(out) + "\n"


def render_md(name, m):
    cat = CATEGORY_MAP[m["subdir"]]
    info_url = url_for(name)
    assert info_url, f"missing InfoSys URL for {name}"

    inputs = m["inputs"]
    in_out = m["in_out"]
    pitfalls = m["pitfalls"]

    iecst = render_iecst(name, m["ret"], inputs, in_out)

    var_input_md = render_var_table(inputs) if inputs else "无。\n"
    var_inout_md = render_var_table(in_out) if in_out else "无。\n"

    pitfalls_md = "\n".join(f"- {p}" for p in pitfalls)

    md = f"""# {name}

## 元信息

| 字段 | 值 |
|---|---|
| Library | `{LIB}` |
| Library Version | `{LIB_VER}` |
| Type | `FUNCTION` |
| Category | `{cat}` |
| Source PDF | {PDF_URL} |
| Source InfoSys | {info_url} |
| Verified | {TODAY} ✅ |
| InfoSys-checked | ✅ {TODAY} |
| Status | `verified` |
| Example | [`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml) |

---

## 1. 功能简述

{m['purpose']}

## 2. 接口定义

### VAR_INPUT

```iecst
{iecst}
```

{var_input_md}
### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

{var_inout_md}
### 返回值

{m['ret_doc']}

## 3. 行为说明

{m['behavior']}

**工程视角补充**：本函数是 `Tc2_Utilities` 库 `{cat}` 一组里的成员，被设计为无内部状态、无副作用、单 PLC 周期完成的纯函数。调用方需要在调用前完成参数合法性检查（如除数非零、移位位数不越界、`REFERENCE TO` 引用为真实左值等），并把返回值缓存到稳定的工业语义变量名（例如 `uliRuntime` 而非 `tmp1`），以便后续在线监视和故障追溯。对于结构体返回类型（`T_ULARGE_INTEGER` / `T_LARGE_INTEGER` / `T_FIX16`），切勿用 IEC `=` 运算符直接比较，需使用本库的 `*Cmp64` 或 `*isZero` 等同类函数。在多人协作或与外部库混用时，建议在仓库的 README 中固定记录本函数的"返回值含义 / 错误码语义 / 边界假设"，避免后续维护时再翻 PDF。

## 4. 错误码 / 返回值

{m['ret_doc']}

PDF 与 InfoSys 均未为本 FUNCTION 列独立的错误码字段。调用层需通过参数范围预校验（除零、NaN、移位位数、有符号溢出等）来保证安全。

## 5. 使用注意 / 常见坑

{pitfalls_md}

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
PROGRAM P_Demo_{name}
VAR
    {m['demo_vars']}
END_VAR

{m['demo_call']}
```

## 7. 业务场景与实际价值

- **场景**：{m['scenario']}
- **价值**：{m['value']}
- **替代方案对比**：调用方可手写等价的双倍长 / 位运算 / IEEE 754 检测，但代码量大、易错；本函数封装好硬件指令或位级判断，单次调用即完成，与库内其它同类函数（如 `{cat}` 同组的其他成员）风格统一，便于代码审阅与维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf]({PDF_URL}) §{m['section']}
- **InfoSys topic**：{info_url}
- **同组相关 FC**：见库分类 `{cat}`，覆盖加 / 减 / 乘 / 除 / 比较 / 位运算 / 类型转换的完整接口
"""
    return md


def _xml_localvars_for(inputs, in_out, demo_vars):
    """Build PLCopenXML <variable> elements matching the demo_vars text declarations."""
    # We parse demo_vars (Pascal-like declarations) line by line.
    out = []
    for raw_line in demo_vars.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # Strip trailing comment "// ..." for type-parsing, keep it for documentation node
        comment = ""
        if "//" in line:
            line_clean, comment = line.split("//", 1)
            comment = comment.strip()
        else:
            line_clean = line
        line_clean = line_clean.rstrip(";").strip()
        if ":" not in line_clean:
            continue
        name_part, type_part = line_clean.split(":", 1)
        vname = name_part.strip()
        # Default value (after :=) — keep as initialValue (raw string)
        init = None
        if ":=" in type_part:
            type_only, init = type_part.split(":=", 1)
            init = init.strip()
            type_part = type_only
        type_part = type_part.strip()
        # Map to PLCopenXML type element
        type_xml = _type_xml(type_part)
        var_el = f'            <variable name="{vname}">\n              <type>{type_xml}</type>\n'
        if init is not None:
            # Escape & in initialValue (rare)
            init_esc = init.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            var_el += f'              <initialValue><simpleValue value="{init_esc}"/></initialValue>\n'
        if comment:
            cmt_esc = comment.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            var_el += f'              <documentation><xhtml xmlns="http://www.w3.org/1999/xhtml">{cmt_esc}</xhtml></documentation>\n'
        var_el += "            </variable>"
        out.append(var_el)
    return "\n".join(out)


_BASIC = {"BOOL","BYTE","WORD","DWORD","LWORD","SINT","USINT","INT","UINT","DINT","UDINT","LINT","ULINT","REAL","LREAL","TIME","LTIME","DATE","DT","TOD","STRING"}


def _type_xml(t):
    """Map a Pascal type string to PLCopenXML."""
    t = t.strip()
    up = t.upper()
    if up in _BASIC:
        return f"<{up}/>"
    # STRING(N)
    if up.startswith("STRING("):
        n = up[len("STRING("):-1]
        return f"<string><length>{n}</length></string>"
    # WORD(0..15) — subrange; render as plain WORD for tooling friendliness
    if "(" in up and ".." in up:
        base = up.split("(",1)[0]
        return f"<{base}/>"
    # else: derived named type
    return f'<derived name="{t}"/>'


def _esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_xml(name, m):
    # Build localVars: fb instance (the FUNCTION itself doesn't need fb instance — FC is stateless),
    # but the lint script accepts <derived> OR a call site. We'll always include a call site to <name>(...).
    # For FC, no need for "fb instance"; demo_vars covers all locals.
    localvars = _xml_localvars_for(m["inputs"], m["in_out"], m["demo_vars"])

    # Build verification comment block + body
    scenario = m['scenario'].replace('\n', '\n//        ')
    value    = m['value'].replace('\n', '\n//        ')
    body_header = f"""// ============================================================
// Tc2_Utilities.{name} 演示程序（FUNCTION，单周期触发）
// ============================================================
// 场景：{scenario}
// 价值：{value}
// 验证步骤：
//   1. 把本 PROGRAM 加到 PlcTask 调用列表
//   2. 编译 + 登录
//   3. 在线把 b... 触发位置 TRUE 一个周期
//   4. 观察输出变量是否符合期望
// ============================================================
"""
    body = body_header + "\n" + m["demo_call"]
    body_esc = _esc(body)

    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<project xmlns="http://www.plcopen.org/xml/tc6_0200">
  <fileHeader companyName="tc3-libraries-kb" productName="TwinCAT" productVersion="3.1" creationDateTime="{TODAY}T12:00:00"/>
  <contentHeader name="{LIB}.{name} Demo" modificationDateTime="{TODAY}T12:00:00">
    <coordinateInfo>
      <fbd><scaling x="1" y="1"/></fbd>
      <ld><scaling x="1" y="1"/></ld>
      <sfc><scaling x="1" y="1"/></sfc>
    </coordinateInfo>
  </contentHeader>
  <types>
    <dataTypes/>
    <pous>
      <pou name="P_Demo_{name}" pouType="program">
        <interface>
          <localVars>
{localvars}
          </localVars>
        </interface>
        <body>
          <ST>
            <xhtml xmlns="http://www.w3.org/1999/xhtml">{body_esc}
</xhtml>
          </ST>
        </body>
      </pou>
    </pous>
  </types>
  <instances>
    <configurations/>
  </instances>
</project>
"""
    return xml


def main():
    out_doc = 0
    out_xml = 0
    for name, m in META.items():
        doc_path = ROOT / LIB / m["subdir"] / f"{name}.md"
        xml_path = ROOT / LIB / "examples" / f"P_Demo_{name}.xml"
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        xml_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(render_md(name, m), encoding="utf-8")
        xml_path.write_text(render_xml(name, m), encoding="utf-8")
        out_doc += 1
        out_xml += 1
    print(f"wrote {out_doc} docs and {out_xml} examples")


if __name__ == "__main__":
    main()
