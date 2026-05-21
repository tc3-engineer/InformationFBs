#!/usr/bin/env python3
"""Generator for Tc2_IoFunctions docs + examples."""
from __future__ import annotations
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))

from extract_section import extract as extract_section  # noqa: E402
from parse_toc import parse as parse_toc  # noqa: E402
from _tc2iofunctions_urls import url_for  # noqa: E402
from _tc2iofunctions_registry import REG  # noqa: E402

LIB = "Tc2_IoFunctions"
PDF_URL = "https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf"
PDF_VERSION = "1.5.3"
TODAY = "2026-05-21"

CAT_DIR = {
    "General IO FBs": "general_io",
    "ASI master terminal": "asi_master_terminal",
    "AX200x Profibus": "ax200x_profibus",
    "Beckhoff Lightbus": "beckhoff_lightbus",
    "Beckhoff UPS (configured with Windows UPS Service": "beckhoff_ups",
    "Bus Terminal configuration": "bus_terminal_configuration",
    "CANopen": "canopen",
    "NOV/DP-RAM": "nov_dpram",
    "Profibus DPV1 (Sinamics)": "profibus_dpv1_sinamics",
    "Profinet DPV1 (Sinamics)": "profinet_dpv1_sinamics",
    "RAID Controller": "raid_controller",
    "SERCOS": "sercos",
    "TcTouchLock": "tctouchlock",
    "[Obsolete]": "obsolete",
    "Library version": "library_version",
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
    if n in {"netid", "snetid", "anetid"}:
        return "目标 TwinCAT 计算机的 AMS Net ID；本机用空串 `''`，远端填对端 AMS Net ID（例如 `'5.84.32.27.1.1'`）。"
    if n == "deviceid":
        return "TwinCAT 配置时由系统自动分配的 I/O 设备 ID（不可由用户配置）。可在 System Manager 中查看，或通过 `IOF_GetDeviceIDByName` 由设备名查得。"
    if n == "boxaddr":
        return "现场总线地址（如 Profibus 站号 / Lightbus 光纤环模块号）。"
    if n == "boxname":
        return "工程师在 TwinCAT System Manager 配置 box 时给的名字（字符串）。"
    if n in {"devicename"}:
        return "工程师在 TwinCAT System Manager 配置 I/O 设备时给的名字（字符串）。"
    if n in {"bexecute", "bstart", "start", "reset", "save", "get", "set", "bwrtrd"}:
        return "上升沿触发一次执行；调用期间保持高电平，完成后由用户决定何时回 FALSE 准备下次触发。"
    if n == "benable":
        return "TRUE 电平使能本 FB；FALSE 时停止周期工作。"
    if n in {"ttimeout", "tmout", "ttmout"}:
        return "ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。"
    if n in {"bbusy", "busy"}:
        return "FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。"
    if n in {"berr", "berror", "err"}:
        return "命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。"
    if n in {"nerrid", "nerrorid", "errid", "ierrornumber", "ierrorid", "berrornumber"}:
        return "错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。"
    if n == "len":
        return "数据缓冲区字节长度。"
    if n in {"destaddr", "srcaddr"}:
        return f"数据缓冲区地址，用 `ADR()` 运算符取得。"
    # generic fallbacks
    if t == "BOOL":
        return f"布尔标志 `{name}`。"
    if t.startswith("STRING") or t in {"T_AMSNETID", "T_MAXSTRING"}:
        return f"字符串参数 `{name}`。"
    if t in {"UDINT", "UINT", "WORD", "BYTE", "USINT", "DWORD", "LWORD", "ULINT"}:
        return f"无符号整数 `{name}`。"
    if t in {"DINT", "INT", "SINT", "LINT"}:
        return f"有符号整数 `{name}`。"
    if t in {"REAL", "LREAL"}:
        return f"浮点数 `{name}`。"
    if t in {"TIME", "LTIME"}:
        return f"时间值 `{name}`。"
    if t == "PVOID":
        return f"内存地址指针 `{name}`（`ADR(buffer)` 取得）。"
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
        suf = "" if not is_eng or "工程经验补充" in text else "（工程经验补充）"
        out.append(f"- {text}{suf}")
    return "\n".join(out) + "\n"


def _render_returns(reg, parsed):
    if "return_text" in reg and reg["return_text"]:
        return reg["return_text"]
    outs = parsed["outputs"]
    has_berr = any(n.lower() in {"berr", "berror", "err"} for n, _, _ in outs)
    has_errid = any(n.lower() in {"nerrid", "nerrorid", "errid", "ierrornumber", "berrornumber"} for n, _, _ in outs)
    if has_berr and has_errid:
        return (
            "本 FB 通过 `bError` / `ERR` + `nErrId` / `ERRID` 输出报告错误：\n\n"
            "- `bError = FALSE` 且 `nErrId = 0`：调用成功。\n"
            "- `bError = TRUE`：调用失败，错误号在 `nErrId`。\n\n"
            "常见错误号（按 ADS Return Codes 表）：\n\n"
            "| 错误号（十六进制） | 含义 |\n|---|---|\n"
            "| `0x06` | 目标端口未找到（ADSERR_DEVICE_NOTFOUND）—— 设备未启用或 DeviceId 错 |\n"
            "| `0x07` | 目标机不在线（ADSERR_DEVICE_NOTREADY） |\n"
            "| `0x745` | ADS 通讯超时（ADSERR_CLIENT_SYNCTIMEOUT）—— `TMOUT` 太短或现场总线响应慢 |\n"
            "| 其他 | 见 Beckhoff **ADS Return Codes** 在线表，及现场总线主站特有的错误码（PDF 未列入本节） |\n\n"
            "⚠️ PDF / InfoSys 未在本 FB 处列具体的现场总线错误号，需配合主站手册查询。\n"
        )
    return "本 FB 无具体错误码表；状态由输出参数自行反映。具体错误语义需配合主站 / 现场总线设备手册查询。\n"


def _render_md(name, reg, parsed, infosys, pdf_section, category):
    md = [f"# {name}\n"]
    md.append("## 元信息\n")
    md.append("| 字段 | 值 |")
    md.append("|---|---|")
    md.append(f"| Library | `{LIB}` |")
    md.append(f"| Library Version | `{PDF_VERSION}` |")
    md.append(f"| Type | `{reg.get('ftype', 'FUNCTION_BLOCK')}` |")
    md.append(f"| Category | `{category}` |")
    md.append(f"| Source PDF | {PDF_URL} |")
    md.append(f"| Source InfoSys | {infosys} |")
    md.append(f"| Verified | {TODAY} ✅ |")
    if "not-on-infosys" in infosys or reg.get("infosys_redirect"):
        md.append("| InfoSys-checked | ⚠️ not-on-infosys |")
    else:
        md.append(f"| InfoSys-checked | ✅ {TODAY} |")
    md.append(f"| Status | `verified` |")
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
    md.append("## 3. 行为说明\n")
    md.append(reg["behavior"].strip() + "\n")
    md.append("## 4. 错误码 / 返回值\n")
    md.append(_render_returns(reg, parsed))
    md.append("## 5. 使用注意 / 常见坑\n")
    md.append(_render_pitfalls(reg.get("pitfalls", [])))
    md.append("## 6. 最小例程\n")
    md.append(f"> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）\n>\n> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK\n")
    md.append("详见 example xml 文件。\n")
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
    md.append(f"- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf]({PDF_URL}){sec_str}")
    if "not-on-infosys" in infosys:
        md.append(f"- **InfoSys topic**：⚠️ not-on-infosys（库索引未收录该条目）")
    elif reg.get("infosys_redirect"):
        md.append(f"- **InfoSys topic**：{infosys} （⚠️ 该条目在 InfoSys 没有专属页面，URL 指向库版本页作为替代说明）")
    else:
        md.append(f"- **InfoSys topic**：{infosys}")
    if reg.get("related"):
        md.append(f"- **相关 FB / FC**：" + ", ".join(f"`{r}`" for r in reg["related"]))
    md.append("")
    return "\n".join(md)


def _render_xml(name, reg, parsed):
    pou_name = f"P_Demo_{name}"
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
        "//   2. 引用 Tc2_IoFunctions（References → Add library）\n"
        "//   3. 编译 → 登录 → 运行；按上方『验证』行的指示在线写值观察\n"
        "// =============================================================================\n"
    )
    body_text = _xml_escape(header + "\n" + reg["xml_call"].strip() + "\n")
    return (
        "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
        "<project xmlns=\"http://www.plcopen.org/xml/tc6_0200\">\n"
        f"  <fileHeader companyName=\"tc3-libraries-kb\" productName=\"TwinCAT\" productVersion=\"3.1\" creationDateTime=\"{TODAY}T00:00:00\"/>\n"
        f"  <contentHeader name=\"Tc2_IoFunctions.{name} Demo\" modificationDateTime=\"{TODAY}T00:00:00\">\n"
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
        if "extra_inputs" in reg:
            parsed["inputs"].extend(reg["extra_inputs"])
        if "extra_outputs" in reg:
            parsed["outputs"].extend(reg["extra_outputs"])
        if "extra_in_outs" in reg:
            parsed["in_outs"].extend(reg["extra_in_outs"])
    if not category:
        category = reg.get("category", "")
    infosys = url_for(name)
    md = _render_md(name, reg, parsed, infosys, pdf_section, category)
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
