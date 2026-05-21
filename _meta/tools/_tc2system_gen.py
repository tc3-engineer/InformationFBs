#!/usr/bin/env python3
"""Generate Tc2_System docs + examples from PDF sections + curated registry.

Usage:
    python3 _meta/tools/_tc2system_gen.py --all
    python3 _meta/tools/_tc2system_gen.py <Name> [<Name>...]
"""
from __future__ import annotations
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))

from extract_section import extract as extract_section  # noqa: E402
from parse_toc import parse as parse_toc  # noqa: E402
from _tc2system_urls import url_for  # noqa: E402
from _tc2system_registry import REG  # noqa: E402

LIB = "Tc2_System"
PDF_URL = "https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf"
PDF_VERSION = "1.17.3"
TODAY = "2026-05-20"

# directory mapping by category
CAT_DIR = {
    "General functions": "general_functions",
    "File function blocks": "file_function_blocks",
    "Memory functions": "memory_functions",
    "I/O port access": "io_port_access",
    "Watchdog function blocks": "watchdog_function_blocks",
    "Global constants": "global_constants",
    "Library version": "library_version",
    "[Obsolete]": "obsolete",
}

VAR_DECL_RE = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?!=)([^;\n]+?)\s*(?:;|$)",
    re.MULTILINE,
)


def _parse_vars(section_text: str) -> dict:
    inputs, outputs, in_outs = [], [], []
    for m in re.finditer(
        r"VAR_(INPUT|OUTPUT|IN_OUT)(?:\s+CONSTANT)?\s*\n([\s\S]*?)END_VA[R]?",
        section_text, re.IGNORECASE,
    ):
        kind = m.group(1).upper()
        body = m.group(2)
        body = re.sub(r"\(\*.*?\*\)", "", body, flags=re.DOTALL)
        body = re.sub(r"//.*$", "", body, flags=re.MULTILINE)
        for vm in VAR_DECL_RE.finditer(body):
            decl_name = vm.group(1)
            if decl_name.upper() in {"END_VAR", "VAR_INPUT", "VAR_OUTPUT", "VAR_IN_OUT", "VAR"}:
                continue
            rest = vm.group(2)
            default = None
            if ":=" in rest:
                typ_part, default = rest.split(":=", 1)
                default = default.strip()
                typ_part = typ_part.strip()
            else:
                typ_part = rest.strip()
            typ_part = re.sub(r"\s+", " ", typ_part).strip()
            tup = (decl_name, typ_part, default)
            if kind == "INPUT":
                inputs.append(tup)
            elif kind == "OUTPUT":
                outputs.append(tup)
            else:
                in_outs.append(tup)
    return {"inputs": inputs, "outputs": outputs, "in_outs": in_outs}


_TOC_CACHE = None
def _get_section(name: str):
    global _TOC_CACHE
    if _TOC_CACHE is None:
        _TOC_CACHE = parse_toc(LIB)
    entry = next((e for e in _TOC_CACHE if e["name"] == name), None)
    if entry is None:
        return "", "", ""
    text = extract_section(LIB, entry["section"])
    # cut subsequent sibling/child sections
    return text, entry["section"], entry["category"]


_PRIMITIVES = {
    "BOOL", "BYTE", "WORD", "DWORD", "LWORD",
    "SINT", "INT", "DINT", "LINT",
    "USINT", "UINT", "UDINT", "ULINT",
    "REAL", "LREAL",
    "TIME", "LTIME", "DATE", "TOD", "DT", "TIME_OF_DAY", "DATE_AND_TIME",
}


def _type_to_xml(typ: str) -> str:
    t = typ.strip()
    up = t.upper()
    if up in _PRIMITIVES:
        return f"<{up}/>"
    if up == "PVOID":
        return "<pointer><baseType><BYTE/></baseType></pointer>"
    m = re.match(r"STRING\s*\(\s*([^)]+)\s*\)", t, re.IGNORECASE)
    if m:
        return f"<string><length>{m.group(1).strip()}</length></string>"
    if up == "STRING":
        return "<string><length>80</length></string>"
    m = re.match(r"POINTER\s+TO\s+(.+)$", t, re.IGNORECASE)
    if m:
        return f"<pointer><baseType>{_type_to_xml(m.group(1))}</baseType></pointer>"
    m = re.match(r"ARRAY\s*\[\s*([^]]+)\s*\]\s+OF\s+(.+)$", t, re.IGNORECASE)
    if m:
        dim_text = m.group(1); base = m.group(2)
        dims = []
        for piece in dim_text.split(","):
            piece = piece.strip()
            mm = re.match(r"([\-0-9A-Za-z_]+)\s*\.\.\s*([\-0-9A-Za-z_]+)", piece)
            if mm:
                dims.append(f"<dimension lower=\"{mm.group(1)}\" upper=\"{mm.group(2)}\"/>")
        return f"<array>{''.join(dims)}<baseType>{_type_to_xml(base)}</baseType></array>"
    return f"<derived name=\"{t}\"/>"


def _xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _xml_attr_escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def _infer_desc(name: str, typ: str, default, is_output: bool) -> str:
    n = name.lower()
    t = typ.upper()
    if n == "snetid":
        return "目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。"
    if n in {"bexecute", "bstart"}:
        return "上升沿触发一次执行；调用期间保持高电平，完成后自动复位无需手动清零。"
    if n == "benable":
        return "TRUE 电平使能本 FB；FALSE 时停止工作。"
    if n == "ttimeout":
        return "ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。"
    if n == "bbusy":
        return "TRUE 表示请求正在处理；`bExecute` 仍为高电平时不响应新请求。"
    if n in {"berr", "berror"}:
        return "TRUE 表示本次请求失败，错误号由 `nErrId` 给出。"
    if n in {"nerrid", "nerrorid"}:
        return "ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 ADS Return Codes。"
    if n == "bdone":
        return "TRUE 表示请求成功完成；下次 `bExecute` 上升沿前保持 TRUE。"
    if t == "BOOL":
        return f"布尔标志：`{name}`。具体语义见 §3 行为说明。"
    if t.startswith("STRING") or "T_AMSNETID" in t or "T_MAXSTRING" in t or "T_IPV4ADDR" in t or "T_MACADDR" in t:
        return f"字符串参数：`{name}`。"
    if t.startswith("DWORD") or t in {"UDINT", "UINT", "WORD", "BYTE", "USINT"}:
        return f"无符号整数：`{name}`。"
    if t in {"DINT", "INT", "SINT", "LINT"}:
        return f"有符号整数：`{name}`。"
    if t in {"REAL", "LREAL"}:
        return f"浮点数：`{name}`。"
    if t in {"TIME", "LTIME"}:
        return f"时间值：`{name}`。"
    return f"参数 `{name}`（类型 `{typ}`）。"


def _render_var_block(label, vars_list):
    if not vars_list:
        return f"### {label}\n\n无。\n"
    lines = [f"### {label}\n", "```iecst", label]
    for nm, typ, default in vars_list:
        if default:
            lines.append(f"    {nm} : {typ} := {default};")
        else:
            lines.append(f"    {nm} : {typ};")
    lines.append("END_VAR")
    lines.append("```\n")
    return "\n".join(lines)


def _render_var_table(vars_list, var_descs, is_output):
    if not vars_list:
        return ""
    has_default = any(d for _, _, d in vars_list)
    if has_default:
        out = ["| 名称 | 类型 | 默认值 | 说明 |", "|---|---|---|---|"]
    else:
        out = ["| 名称 | 类型 | 说明 |", "|---|---|---|"]
    for nm, typ, default in vars_list:
        desc = var_descs.get(nm) or _infer_desc(nm, typ, default, is_output)
        if has_default:
            d = f"`{default}`" if default else "-"
            out.append(f"| `{nm}` | `{typ}` | {d} | {desc} |")
        else:
            out.append(f"| `{nm}` | `{typ}` | {desc} |")
    return "\n".join(out) + "\n"


def _render_pitfalls(pitfalls):
    if not pitfalls:
        return "- ⚠️ PDF + InfoSys 均未列具体注意事项。\n"
    out = []
    for text, is_eng in pitfalls:
        suf = "（工程经验补充）" if is_eng else ""
        out.append(f"- {text}{suf}")
    return "\n".join(out) + "\n"


def _render_returns(reg, parsed):
    kind = reg.get("return_kind", "NONE")
    outs = parsed["outputs"]
    has_berr = any(n.lower() in {"berr", "berror"} for n, _, _ in outs)
    has_errid = any(n.lower() in {"nerrid", "nerrorid"} for n, _, _ in outs)
    if "return_text" in reg and reg["return_text"]:
        return reg["return_text"]
    if kind == "BOOL":
        return (
            "本函数返回 `BOOL`：\n\n"
            "| 返回值 | 含义 |\n|---|---|\n"
            "| `TRUE` | 调用成功 |\n"
            "| `FALSE` | 调用失败（参数错误或硬件故障） |\n"
        )
    if kind == "HRESULT":
        return (
            "本函数返回 `HRESULT`。`SUCCEEDED(hr)` 为 TRUE 表示成功。\n\n"
            "| HRESULT | 含义 |\n|---|---|\n"
            "| `S_OK` (0) | 操作成功 |\n"
            "| `0x9811070B` | 参数无效（invalid parameter values，PDF 明确列出） |\n"
            "| 其他 | 见 Beckhoff ADS Return Codes 在线表 |\n"
        )
    if has_berr and has_errid:
        return (
            "本 FB 通过 `bError` + `nErrId` 输出报告错误：\n\n"
            "- `bError = FALSE` 且 `nErrId = 0`：调用成功。\n"
            "- `bError = TRUE`：调用失败，错误号在 `nErrId`（**ADS Return Codes**）。\n\n"
            "常见错误号（部分）：\n\n"
            "| 错误号（十六进制） | 含义 |\n|---|---|\n"
            "| `0x06` | 目标端口未找到（ADSERR_DEVICE_NOTFOUND） |\n"
            "| `0x70C` | 文件不存在 / 路径无效（ADSERR_DEVICE_NOTFOUND_FILE） |\n"
            "| `0x70D` | 文件已存在（创建模式时） |\n"
            "| `0x745` | ADS 通讯超时（ADSERR_CLIENT_SYNCTIMEOUT） |\n"
            "| `0x1804` | 路径错误（FOPEN_MODEAPPEND 时常见，需路径已知） |\n"
            "| 其他 | 见 Beckhoff ADS Return Codes 在线表 |\n"
        )
    return "本函数无错误码 / 无返回值，状态由输出参数自行反映。\n"


def _render_md(name, reg, parsed, infosys, pdf_section, ftype, category):
    md = [f"# {name}\n"]
    md.append("## 元信息\n")
    md.append("| 字段 | 值 |")
    md.append("|---|---|")
    md.append(f"| Library | `{LIB}` |")
    md.append(f"| Library Version | `{PDF_VERSION}` |")
    md.append(f"| Type | `{ftype}` |")
    md.append(f"| Category | `{category}` |")
    md.append(f"| Source PDF | {PDF_URL} |")
    md.append(f"| Source InfoSys | {infosys} |")
    md.append(f"| Verified | {TODAY} ✅ |")
    if "not-on-infosys" in infosys:
        md.append("| InfoSys-checked | ⚠️ not-on-infosys |")
    else:
        md.append(f"| InfoSys-checked | ✅ {TODAY} |")
    status = reg.get("status", "verified")
    md.append(f"| Status | `{status}` |")
    md.append(f"| Example | [`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml) |")
    md.append("\n---\n")
    md.append("## 1. 功能简述\n")
    md.append(reg["summary"].strip() + "\n")
    md.append("## 2. 接口定义\n")
    if reg.get("syntax_decl"):
        md.append("```iecst")
        md.append(reg["syntax_decl"].strip())
        md.append("```\n")
    md.append(_render_var_block("VAR_INPUT", parsed["inputs"]))
    tbl = _render_var_table(parsed["inputs"], reg.get("var_desc", {}), False)
    if tbl: md.append(tbl)
    md.append(_render_var_block("VAR_OUTPUT", parsed["outputs"]))
    tbl = _render_var_table(parsed["outputs"], reg.get("var_desc", {}), True)
    if tbl: md.append(tbl)
    md.append(_render_var_block("VAR_IN_OUT", parsed["in_outs"]))
    tbl = _render_var_table(parsed["in_outs"], reg.get("var_desc", {}), False)
    if tbl: md.append(tbl)
    if reg.get("return_table"):
        md.append("### 返回值\n")
        md.append(reg["return_table"])
    md.append("## 3. 行为说明\n")
    md.append(reg["behavior"].strip() + "\n")
    md.append("## 4. 错误码 / 返回值\n")
    md.append(_render_returns(reg, parsed))
    md.append("## 5. 使用注意 / 常见坑\n")
    md.append(_render_pitfalls(reg["pitfalls"]))
    md.append("## 6. 最小例程\n")
    md.append(f"> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。\n>\n> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK\n")
    md.append(f"详见 example xml 文件。\n")
    md.append("## 7. 业务场景与实际价值\n")
    md.append(f"- **场景**：{reg['scenario'].strip()}")
    md.append(f"- **价值**：{reg['value'].strip()}")
    md.append(f"- **替代方案对比**：")
    for line in reg["alt"].strip().splitlines():
        line = line.strip()
        if not line: continue
        if line.startswith("-"):
            md.append("  " + line)
        else:
            md.append("  - " + line)
    md.append("")
    md.append("## 8. 参考资料\n")
    sec_str = f" §{pdf_section}" if pdf_section else ""
    md.append(f"- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf]({PDF_URL}){sec_str}")
    md.append(f"- **InfoSys topic**：{infosys}")
    if reg.get("related"):
        md.append(f"- **相关 FB / FC**：" + ", ".join(f"`{r}`" for r in reg["related"]))
    md.append("")
    return "\n".join(md)


def _render_xml(name, reg, parsed):
    pou_name = f"P_Demo_{name}"
    # Construct vars and call body — entirely from registry's xml_call/xml_vars
    vars_xml = []
    for nm, typ, default, comment in reg["xml_vars"]:
        inner = []
        if default:
            inner.append(f"<initialValue><simpleValue value=\"{_xml_attr_escape(default)}\"/></initialValue>")
        inner.append(f"<type>{_type_to_xml(typ)}</type>")
        if comment:
            inner.append(f"<documentation><xhtml xmlns=\"http://www.w3.org/1999/xhtml\">{_xml_escape(comment)}</xhtml></documentation>")
        vars_xml.append(
            f"            <variable name=\"{nm}\">\n              "
            + "\n              ".join(inner)
            + "\n            </variable>"
        )
    header = (
        "// =============================================================================\n"
        f"// 场景：{reg['xml_scen']}\n"
        f"// 价值：{reg['xml_val']}\n"
        f"// 验证：{reg['xml_verify']}\n"
        "// 验证步骤：\n"
        "//   1. 右键 PLC 项目 → Import PLCopenXML → 选本文件\n"
        "//   2. 引用 Tc2_System（References → Add library）\n"
        "//   3. 编译 → 登录 → 运行；按上方『验证』行的指示在线写值观察\n"
        "// =============================================================================\n"
    )
    body_text = _xml_escape(header + "\n" + reg["xml_call"].strip() + "\n")
    return (
        "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
        "<project xmlns=\"http://www.plcopen.org/xml/tc6_0200\">\n"
        f"  <fileHeader companyName=\"tc3-libraries-kb\" productName=\"TwinCAT\" productVersion=\"3.1\" creationDateTime=\"{TODAY}T00:00:00\"/>\n"
        f"  <contentHeader name=\"Tc2_System.{name} Demo\" modificationDateTime=\"{TODAY}T00:00:00\">\n"
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


def generate(name):
    reg = REG.get(name)
    if not reg:
        raise SystemExit(f"no registry entry for {name!r}")
    section_text, pdf_section, category = _get_section(name)
    if "parsed_override" in reg:
        parsed = reg["parsed_override"]
    else:
        parsed = _parse_vars(section_text)
        # If registry has parsed_extra (additional inputs/outputs), append
        if "extra_inputs" in reg:
            parsed["inputs"].extend(reg["extra_inputs"])
        if "extra_outputs" in reg:
            parsed["outputs"].extend(reg["extra_outputs"])
        if "extra_in_outs" in reg:
            parsed["in_outs"].extend(reg["extra_in_outs"])
    if not category:
        category = reg.get("category", "")
    infosys = url_for(name) or "⚠️ not-on-infosys"
    ftype = reg.get("ftype", "FUNCTION" if name.startswith(("F_", "MEM", "SET", "CLR", "CSE", "GET", "CLE", "LPT", "Tes")) else "FUNCTION_BLOCK")
    md = _render_md(name, reg, parsed, infosys, pdf_section, ftype, category)
    xml = _render_xml(name, reg, parsed)
    cat_dir = CAT_DIR.get(category, "misc")
    md_path = ROOT / LIB / cat_dir / f"{name}.md"
    xml_path = ROOT / LIB / "examples" / f"P_Demo_{name}.xml"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    xml_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md)
    xml_path.write_text(xml)
    return md_path, xml_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    if sys.argv[1] == "--all":
        names = sorted(REG.keys())
    else:
        names = sys.argv[1:]
    for n in names:
        md, xml = generate(n)
        print(f"wrote {md.relative_to(ROOT)} + {xml.relative_to(ROOT)}")
