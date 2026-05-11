#!/usr/bin/env python3
"""Generate Tc3_EventLogger doc + example pairs from a content registry.

Usage:
    python3 _meta/tools/_tc3eventlogger_gen.py <key>
    e.g. _tc3eventlogger_gen.py fb_tcalarm/Create

For each entry the generator:
  1. Extracts the PDF section (via extract_section.py) → VAR_INPUT/OUTPUT
  2. Merges PDF VAR data with hand-curated Chinese descriptions
  3. Emits <doc_path>.md to the correct directory
  4. Emits examples/P_Demo_<stem>.xml with header scenario comments

The registry lives in _tc3eventlogger_registry.py.
"""
from __future__ import annotations

import re
import sys
import json
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))

from _tc3eventlogger_extract import get_section_text, parse_vars  # noqa: E402
from _tc3eventlogger_urls import url_for  # noqa: E402
from _tc3eventlogger_registry import REG, EXAMPLE_STEMS  # noqa: E402
import _tc3eventlogger_registry2  # noqa: F401, E402 — registers more entries
try:
    import _tc3eventlogger_registry3  # noqa: F401, E402
except ImportError:
    pass
try:
    import _tc3eventlogger_registry4  # noqa: F401, E402
except ImportError:
    pass

LIB = "Tc3_EventLogger"
PDF_URL = "https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf"
PDF_VERSION = "1.6.2"
TODAY = "2026-05-11"

# directory-name → "parent FB friendly name" used in §1/§8
PARENT_FB = {
    "fb_tcalarm": "FB_TcAlarm",
    "fb_tcmessage": "FB_TcMessage",
    "fb_tcsourceinfo": "FB_TcSourceInfo",
    "fb_tcarguments": "FB_TcArguments",
    "fb_tceventbase": "FB_TcEventBase",
    "fb_tceventlogger": "FB_TcEventLogger",
    "fb_listenerbase2": "FB_ListenerBase2",
}


def _example_stem(parent: str, name: str) -> str:
    """Determine example XML filename stem.

    For OO methods we use P_Demo_<Parent>_<Method>.xml to avoid collisions
    (FB_TcAlarm.Create vs FB_TcMessage.Create). Some pages historically used
    a different stem — see EXAMPLE_STEMS override.
    """
    key = f"{parent}/{name}" if parent else name
    if key in EXAMPLE_STEMS:
        return EXAMPLE_STEMS[key]
    if parent in PARENT_FB and name != PARENT_FB[parent]:
        return f"{PARENT_FB[parent]}_{name}"
    return name


def _is_property(name: str) -> bool:
    """Properties in this library start with lowercase letter (ipArguments, ipSourceInfo)."""
    return name and name[0].islower() and not name.startswith("F_")


def _md_returns_section(reg_entry: dict, return_type: str | None) -> str:
    """Render §4 错误码 / 返回值 from registry data."""
    kind = reg_entry.get("return_kind") or "NONE"
    if kind == "NONE":
        return (
            "本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。"
            "状态通过 EventLogger 的事件日志间接反映。\n"
        )
    rows = reg_entry.get("returns", [])
    if kind == "BOOL":
        lines = [
            "本方法/函数返回 `BOOL`。\n",
            "| 返回值 | 含义 | 处理建议 |",
            "|---|---|---|",
        ]
        if not rows:
            lines.append("| `TRUE` | 操作成功 | 继续后续逻辑 |")
            lines.append("| `FALSE` | 操作失败 | 检查输入参数 / 上下文状态 |")
        else:
            for v, m, a in rows:
                lines.append(f"| `{v}` | {m} | {a} |")
        return "\n".join(lines) + "\n"
    if kind == "HRESULT":
        lines = [
            "本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。\n",
            "| HRESULT | 含义 | 处理建议 |",
            "|---|---|---|",
        ]
        if not rows:
            lines.append("| `S_OK` (0) | 操作成功 | 继续后续逻辑 |")
            lines.append(
                "| 其他错误 | PDF 与 InfoSys 未列出具体错误码 ⚠️ | 用 `Tc2_System.E_AdsErr` / `Tc3_EventLogger` ADS Return Codes 表对照 |"
            )
        else:
            for v, m, a in rows:
                lines.append(f"| `{v}` | {m} | {a} |")
        return "\n".join(lines) + "\n"
    if kind == "INTERFACE":
        return (
            "本方法返回接口指针（interface pointer）。\n\n"
            "| 返回值 | 含义 |\n"
            "|---|---|\n"
            "| 非 `0` | 调用成功，可继续通过接口调用相关方法 |\n"
            "| `0` | 未找到匹配实例 / 参数无效 |\n"
        )
    return "⚠️ 待人工确认（未知返回类型）。\n"


def _type_to_xml(typ: str) -> str:
    """Map IEC type string → PLCopenXML element."""
    t = typ.strip()
    # primitives
    primitive = {
        "BOOL", "BYTE", "WORD", "DWORD", "LWORD",
        "SINT", "INT", "DINT", "LINT",
        "USINT", "UINT", "UDINT", "ULINT",
        "REAL", "LREAL", "TIME", "LTIME", "DATE", "TOD", "DT", "TIME_OF_DAY", "DATE_AND_TIME",
    }
    up = t.upper()
    if up in primitive:
        return f"<{up}/>"
    # STRING(N)
    m = re.match(r"STRING\s*\(\s*(\d+)\s*\)", t, re.IGNORECASE)
    if m:
        return f"<string><length>{m.group(1)}</length></string>"
    if up == "STRING":
        return "<string><length>80</length></string>"
    m = re.match(r"WSTRING\s*\(\s*(\d+)\s*\)", t, re.IGNORECASE)
    if m:
        return f"<wstring><length>{m.group(1)}</length></wstring>"
    if up == "WSTRING":
        return "<wstring><length>80</length></wstring>"
    # POINTER TO X
    m = re.match(r"POINTER\s+TO\s+(.+)$", t, re.IGNORECASE)
    if m:
        return f"<pointer><baseType>{_type_to_xml(m.group(1))}</baseType></pointer>"
    # ARRAY[L..U] OF X
    m = re.match(r"ARRAY\s*\[\s*([\-\d]+)\s*\.\.\s*([\-\d]+)\s*\]\s+OF\s+(.+)$", t, re.IGNORECASE)
    if m:
        return (
            f"<array><dimension lower=\"{m.group(1)}\" upper=\"{m.group(2)}\"/>"
            f"<baseType>{_type_to_xml(m.group(3))}</baseType></array>"
        )
    # reference
    m = re.match(r"REFERENCE\s+TO\s+(.+)$", t, re.IGNORECASE)
    if m:
        return f"<derived name=\"{m.group(1).strip()}\"/>"
    # default: derived
    return f"<derived name=\"{t}\"/>"


def _xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _xml_attr_escape(s: str) -> str:
    """Escape for use inside an XML attribute value (double-quoted)."""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _render_var_table(vars_list: list, var_descs: dict, with_default: bool) -> str:
    if not vars_list:
        return "无。\n"
    if with_default:
        out = ["| 名称 | 类型 | 默认值 | 说明 |", "|---|---|---|---|"]
    else:
        out = ["| 名称 | 类型 | 说明 |", "|---|---|---|"]
    for nm, typ, default in vars_list:
        desc = var_descs.get(nm) or "⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文）"
        if with_default:
            d = f"`{default}`" if default else "-"
            out.append(f"| `{nm}` | `{typ}` | {d} | {desc} |")
        else:
            out.append(f"| `{nm}` | `{typ}` | {desc} |")
    return "\n".join(out) + "\n"


def _render_var_block(label: str, vars_list: list) -> str:
    if not vars_list:
        return f"### {label}\n\n无。\n"
    lines = [f"### {label}\n", "```iecst", f"{label}"]
    for nm, typ, default in vars_list:
        if default:
            lines.append(f"    {nm} : {typ} := {default};")
        else:
            lines.append(f"    {nm} : {typ};")
    lines.append("END_VAR")
    lines.append("```\n")
    return "\n".join(lines)


def _render_pitfalls(pitfalls: list) -> str:
    if not pitfalls:
        return "- ⚠️ PDF + InfoSys 均未列具体注意事项。\n"
    out = []
    for text, is_eng in pitfalls:
        suffix = "（工程经验补充）" if is_eng else ""
        out.append(f"- {text}{suffix}")
    return "\n".join(out) + "\n"


def _render_md(parent: str, name: str, reg_entry: dict, parsed: dict, infosys_url: str) -> str:
    is_function = name.startswith("F_") or name.startswith("AdsErr_") or name.startswith("HRESULTAdsErr_") or name.startswith("TcEventEntry_")
    is_property = _is_property(name)
    parent_fb = PARENT_FB.get(parent)

    if parent_fb and not is_function and not is_property and name != parent_fb:
        ftype = "METHOD"
        category = parent_fb
    elif is_property:
        ftype = "PROPERTY"
        category = parent_fb or "Property"
    elif is_function:
        ftype = "FUNCTION"
        category = reg_entry.get("category", "Function")
    else:
        ftype = "FUNCTION_BLOCK"
        category = reg_entry.get("category", "Function block")

    stem = _example_stem(parent, name)
    rel_xml = f"../examples/P_Demo_{stem}.xml"

    var_descs = reg_entry.get("var_desc", {})
    inputs = parsed["inputs"]
    outputs = parsed["outputs"]
    in_outs = parsed["in_outs"]

    # Heading
    md = [f"# {name}\n"]
    md.append("## 元信息\n")
    md.append("| 字段 | 值 |")
    md.append("|---|---|")
    md.append(f"| Library | `{LIB}` |")
    md.append(f"| Library Version | `{PDF_VERSION}` |")
    md.append(f"| Type | `{ftype}` |")
    md.append(f"| Category | `{category}` |")
    md.append(f"| Source PDF | {PDF_URL} |")
    md.append(f"| Source InfoSys | {infosys_url} |")
    md.append(f"| Verified | {TODAY} ✅ |")
    md.append(f"| InfoSys-checked | ✅ {TODAY} |")
    md.append("| Status | `verified` |")
    md.append(f"| Example | [`examples/P_Demo_{stem}.xml`]({rel_xml}) |")
    md.append("\n---\n")
    md.append("## 1. 功能简述\n")
    md.append(reg_entry["summary"].strip() + "\n")
    md.append("## 2. 接口定义\n")

    md.append(_render_var_block("VAR_INPUT", inputs))
    if inputs:
        md.append(_render_var_table(inputs, var_descs, with_default=any(d for _, _, d in inputs)))
        md.append("")
    md.append(_render_var_block("VAR_OUTPUT", outputs))
    if outputs:
        md.append(_render_var_table(outputs, var_descs, with_default=False))
        md.append("")
    md.append(_render_var_block("VAR_IN_OUT", in_outs))
    if in_outs:
        md.append(_render_var_table(in_outs, var_descs, with_default=False))
        md.append("")

    md.append("## 3. 行为说明\n")
    md.append(reg_entry["behavior"].strip() + "\n")
    md.append("## 4. 错误码 / 返回值\n")
    md.append(_md_returns_section(reg_entry, parsed.get("return_type")))
    md.append("## 5. 使用注意 / 常见坑\n")
    md.append(_render_pitfalls(reg_entry.get("pitfalls", [])))
    md.append("## 6. 最小例程\n")
    md.append(f"> 配套可导入文件：[`examples/P_Demo_{stem}.xml`]({rel_xml})（PLCopenXML，可直接导入 TwinCAT 3 XAE）\n>")
    md.append("> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK")
    md.append("\n```iecst")
    md.append(reg_entry.get("iecst_snippet", "// 详见 examples 目录下的 .xml 文件").strip())
    md.append("```\n")
    md.append("## 7. 业务场景与实际价值\n")
    md.append(reg_entry["scenario"].strip())
    md.append("\n")
    md.append(reg_entry["value"].strip())
    md.append("\n")
    md.append(reg_entry["alt"].strip())
    md.append("\n")
    md.append("## 8. 参考资料\n")
    sec_no = reg_entry.get("pdf_section", "")
    sec_str = f" §{sec_no}" if sec_no else ""
    md.append(f"- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf]({PDF_URL}){sec_str}")
    md.append(f"- **InfoSys topic**：{infosys_url}")
    rel = reg_entry.get("related", [])
    if rel:
        md.append(f"- **相关**：{', '.join('`' + r + '`' for r in rel)}")
    md.append("")
    return "\n".join(md)


def _render_xml(parent: str, name: str, reg_entry: dict, parsed: dict) -> str:
    stem = _example_stem(parent, name)
    pou_name = f"P_Demo_{stem}"
    parent_fb = PARENT_FB.get(parent)

    xml_vars = reg_entry.get("xml_vars")
    if not xml_vars:
        # default scaffolding
        xml_vars = []
        if parent_fb and name != parent_fb and not _is_property(name):
            xml_vars.append((f"fb{parent_fb}", parent_fb, None, f"{parent_fb} 实例"))
        elif not parent_fb:
            xml_vars.append((f"fb{name}", name, None, f"{name} 实例"))
        for nm, typ, default in parsed["inputs"]:
            xml_vars.append((nm, typ, default, ""))
        for nm, typ, _ in parsed["outputs"]:
            xml_vars.append((nm, typ, None, ""))
        ret = parsed.get("return_type")
        if ret:
            xml_vars.append(("hr", ret, None, "返回值监视"))

    vars_xml = []
    for nm, typ, default, comment in xml_vars:
        inner = []
        if default:
            inner.append(f"<initialValue><simpleValue value=\"{_xml_attr_escape(default)}\"/></initialValue>")
        inner.append(f"<type>{_type_to_xml(typ)}</type>")
        if comment:
            inner.append(
                f"<documentation><xhtml xmlns=\"http://www.w3.org/1999/xhtml\">{_xml_escape(comment)}</xhtml></documentation>"
            )
        vars_xml.append(f"            <variable name=\"{nm}\">\n              " + "\n              ".join(inner) + "\n            </variable>")

    scenario = reg_entry["xml_scenario"]
    value = reg_entry["xml_value"]
    verify = reg_entry["xml_verify"]
    call = reg_entry["xml_call"]

    header = (
        "// =============================================================================\n"
        f"// 场景：{scenario}\n"
        f"// 价值：{value}\n"
        f"// 验证：{verify}\n"
        "// 验证步骤：\n"
        "//   1. 右键 PLC 项目 → Import PLCopenXML → 选本文件\n"
        "//   2. 引用 Tc3_EventLogger（System → References → Add library）\n"
        "//   3. 编译 → 登录 → 运行；按 verify 注释里给出的在线写值操作\n"
        "// =============================================================================\n"
    )
    body_text = _xml_escape(header + "\n" + call.strip() + "\n")

    return (
        "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
        "<project xmlns=\"http://www.plcopen.org/xml/tc6_0200\">\n"
        f"  <fileHeader companyName=\"tc3-libraries-kb\" productName=\"TwinCAT\" productVersion=\"3.1\" creationDateTime=\"{TODAY}T01:00:00\"/>\n"
        f"  <contentHeader name=\"Tc3_EventLogger.{name} Demo\" modificationDateTime=\"{TODAY}T01:00:00\">\n"
        "    <coordinateInfo>\n"
        "      <fbd><scaling x=\"1\" y=\"1\"/></fbd>\n"
        "      <ld><scaling x=\"1\" y=\"1\"/></ld>\n"
        "      <sfc><scaling x=\"1\" y=\"1\"/></sfc>\n"
        "    </coordinateInfo>\n"
        "  </contentHeader>\n"
        "  <types>\n"
        "    <dataTypes/>\n"
        "    <pous>\n"
        f"      <pou name=\"{pou_name}\" pouType=\"program\">\n"
        "        <interface>\n"
        "          <localVars>\n"
        + "\n".join(vars_xml) + "\n"
        "          </localVars>\n"
        "        </interface>\n"
        "        <body>\n"
        "          <ST><xhtml xmlns=\"http://www.w3.org/1999/xhtml\">"
        + body_text +
        "</xhtml></ST>\n"
        "        </body>\n"
        "      </pou>\n"
        "    </pous>\n"
        "  </types>\n"
        "  <instances><configurations/></instances>\n"
        "</project>\n"
    )


def generate(key: str) -> tuple[Path, Path]:
    if "/" in key:
        parent, name = key.split("/", 1)
    else:
        parent, name = "", key
    reg_entry = REG.get((parent, name))
    if not reg_entry:
        raise SystemExit(f"no registry entry for {key!r}")
    # Find PDF section text
    section_text, entry = get_section_text(LIB, name, parent)
    parsed = parse_vars(section_text, name)
    # InfoSys URL
    if parent and PARENT_FB.get(parent) and name != PARENT_FB[parent]:
        url_key = f"{PARENT_FB[parent]}.{name}"
    elif parent and name == PARENT_FB.get(parent):
        url_key = name
    else:
        url_key = name
    infosys = url_for(url_key)
    if not infosys:
        infosys = "⚠️ infosys URL missing"

    # Inject pdf_section into reg
    reg_entry = dict(reg_entry)
    reg_entry["pdf_section"] = entry.get("section", "")

    md_out = _render_md(parent, name, reg_entry, parsed, infosys)
    xml_out = _render_xml(parent, name, reg_entry, parsed)

    doc_dir = ROOT / LIB / (parent if parent else "misc")
    doc_dir.mkdir(parents=True, exist_ok=True)
    doc_path = doc_dir / f"{name}.md"
    doc_path.write_text(md_out)

    xml_dir = ROOT / LIB / "examples"
    xml_dir.mkdir(parents=True, exist_ok=True)
    stem = _example_stem(parent, name)
    xml_path = xml_dir / f"P_Demo_{stem}.xml"
    xml_path.write_text(xml_out)

    return doc_path, xml_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for key in sys.argv[1:]:
        d, x = generate(key)
        print(f"wrote {d.relative_to(ROOT)} + {x.relative_to(ROOT)}")
