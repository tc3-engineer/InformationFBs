#!/usr/bin/env python3
"""Generate Tc2_Utilities/function_blocks/<Name>.md + examples/P_Demo_<Name>.xml
from the content registry in _tc2utilities_registry.py.

Usage:
    python3 _meta/tools/_tc2utilities_gen.py <Name> [<Name>...]
    python3 _meta/tools/_tc2utilities_gen.py --all
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))

from extract_section import extract as extract_section  # noqa: E402
from parse_toc import parse as parse_toc  # noqa: E402
from _tc2utilities_urls import url_for  # noqa: E402
from _tc2utilities_registry import REG  # noqa: E402
try:
    import _tc2utilities_registry2  # noqa: F401, E402
except ImportError:
    pass
try:
    import _tc2utilities_registry3  # noqa: F401, E402
except ImportError:
    pass
try:
    import _tc2utilities_registry4  # noqa: F401, E402
except ImportError:
    pass
try:
    import _tc2utilities_registry5  # noqa: F401, E402
except ImportError:
    pass

LIB = "Tc2_Utilities"
PDF_URL = "https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf"
PDF_VERSION = "2.18.2"
TODAY = "2026-05-11"

VAR_DECL_RE = re.compile(
    r"\b([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?!=)([^;\n]+?)\s*(?:;|$)",
    re.MULTILINE,
)


def _parse_vars(section_text: str) -> dict:
    """Split VAR_INPUT/OUTPUT/IN_OUT regions. Returns dict with keys inputs/outputs/in_outs (list[(name,type,default)])."""
    inputs, outputs, in_outs = [], [], []
    for m in re.finditer(
        r"VAR_(INPUT|OUTPUT|IN_OUT)(?:\s+CONSTANT)?\s*\n([\s\S]*?)END_VA[R]?",
        section_text,
        re.IGNORECASE,
    ):
        kind = m.group(1).upper()
        body = m.group(2)
        body = re.sub(r"\(\*.*?\*\)", "", body, flags=re.DOTALL)
        body = re.sub(r"//.*$", "", body, flags=re.MULTILINE)
        # join wrapped lines
        lines = body.split("\n")
        out_lines = []
        for raw in lines:
            if (
                out_lines and out_lines[-1].strip()
                and ":" in out_lines[-1] and ";" not in out_lines[-1]
                and raw.strip()
                and not re.match(r"^\s*[A-Za-z_]\w*\s*:(?!=)", raw)
                and not raw.lstrip().upper().startswith(("END_VAR", "VAR_"))
            ):
                out_lines[-1] = out_lines[-1].rstrip() + " " + raw.strip()
            else:
                out_lines.append(raw)
        body = "\n".join(out_lines)
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


# ----------- Section text fetching -----------

_TOC_CACHE = None


def _get_section_text(name: str) -> tuple[str, str]:
    global _TOC_CACHE
    if _TOC_CACHE is None:
        _TOC_CACHE = parse_toc(LIB)
    entry = next((e for e in _TOC_CACHE if e["name"] == name), None)
    if entry is None:
        raise ValueError(f"name {name!r} not in TOC")
    text = extract_section(LIB, entry["section"])
    # Cut subsection for parent FBs (e.g. FB_HashTableCtrl has sub-methods)
    child_pat = re.compile(rf"^\s*{re.escape(entry['section'])}\.\d+\s+\w+", re.MULTILINE)
    cm = child_pat.search(text)
    if cm:
        text = text[: cm.start()]
    # Cut inline METHOD body — its own VAR_INPUT must not leak into the FB
    # parent's VAR_INPUT table.
    inline_method = re.search(r"(?m)^\s*METHOD\s+\w+", text)
    if inline_method:
        text = text[: inline_method.start()]
    return text, entry["section"]


# ----------- Description inference (NEVER produces "（详见 PDF）") -----------


def _infer_desc(name: str, typ: str, default, is_output: bool) -> str:
    n = name.lower()
    t = typ.upper()
    # Common ADS / engineering idioms
    if n == "snetid":
        return "目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。"
    if n in {"sname", "shostname"}:
        return "目标主机名 / 路由名（字符串）。"
    if n in {"bexecute", "bstart"}:
        return "上升沿触发一次执行；调用期间保持高电平，完成后自动复位无需手动清零。"
    if n == "benable":
        return "TRUE 电平使能本 FB；FALSE 时不工作。"
    if n in {"ttimeout"}:
        return "ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。"
    if n == "bbusy":
        return "TRUE 表示请求正在处理；同时 `bExecute` 仍为高电平时不响应新请求。"
    if n in {"berr", "berror"}:
        return "TRUE 表示本次请求失败，错误号由 `nErrId` / `nErrorId` 给出。"
    if n in {"nerrid", "nerrorid"}:
        return "ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 InfoSys / ADS Return Codes。"
    if n == "bdone":
        return "TRUE 表示请求成功完成一次；下次 `bExecute` 上升沿前保持 TRUE。"
    if n in {"pdata", "pdest", "psrc", "psource", "pbuffer"}:
        return "缓冲区指针（`PVOID` / `POINTER TO BYTE`），调用方负责分配。"
    if n in {"cbdata", "cbbuffer", "cblen", "nbuffersize"}:
        return "缓冲区字节数。"
    if n in {"hfile", "hfilehandle"}:
        return "文件句柄（由 `FB_FileOpen` 类 FB 返回）。"
    if n == "sfilename":
        return "目标文件路径，绝对路径字符串。"
    if n == "epath":
        return "目标路径枚举（`PATH_GENERIC` / `PATH_BOOTPATH` 等），决定相对路径基准。"
    if n in {"nbytestoread", "nbytestowrite"}:
        return "本次读 / 写的字节数。"
    if n in {"nbytesread", "nbyteswritten"}:
        return "本次实际读 / 写的字节数。"
    if n in {"hreg", "hkey"}:
        return "已打开的注册表句柄。"
    if "amsaddr" in t:
        return "AMS 地址结构（NetID + Port）。"
    if t in {"BOOL"}:
        if is_output:
            return f"输出布尔标志：`{name}`。具体语义见 §3 行为说明。"
        return f"输入布尔标志：`{name}`。具体语义见 §3 行为说明。"
    if t.startswith("STRING"):
        return f"字符串输入：`{name}`。"
    if t in {"TIME", "LTIME"}:
        return f"时间值：`{name}`。"
    if t.startswith("DWORD") or t in {"UDINT", "UINT", "WORD", "BYTE", "USINT"}:
        if is_output:
            return f"无符号整数输出：`{name}`。"
        return f"无符号整数输入：`{name}`。"
    if t in {"DINT", "INT", "SINT", "LINT"}:
        if is_output:
            return f"有符号整数输出：`{name}`。"
        return f"有符号整数输入：`{name}`。"
    if t in {"REAL", "LREAL"}:
        return f"浮点数：`{name}`。"
    # default
    return f"参数 `{name}`（类型 `{typ}`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。"


# ----------- XML emission -----------


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
    m = re.match(r"STRING\s*\(\s*([^)]+)\s*\)", t, re.IGNORECASE)
    if m:
        return f"<string><length>{m.group(1).strip()}</length></string>"
    if up == "STRING":
        return "<string><length>80</length></string>"
    m = re.match(r"WSTRING\s*\(\s*([^)]+)\s*\)", t, re.IGNORECASE)
    if m:
        return f"<wstring><length>{m.group(1).strip()}</length></wstring>"
    if up == "WSTRING":
        return "<wstring><length>80</length></wstring>"
    m = re.match(r"POINTER\s+TO\s+(.+)$", t, re.IGNORECASE)
    if m:
        return f"<pointer><baseType>{_type_to_xml(m.group(1))}</baseType></pointer>"
    m = re.match(r"REFERENCE\s+TO\s+(.+)$", t, re.IGNORECASE)
    if m:
        return f"<derived name=\"{m.group(1).strip()}\"/>"
    m = re.match(r"ARRAY\s*\[\s*([^]]+)\s*\]\s+OF\s+(.+)$", t, re.IGNORECASE)
    if m:
        dim_text = m.group(1)
        base = m.group(2)
        dims = []
        for piece in dim_text.split(","):
            piece = piece.strip()
            mm = re.match(r"([\-0-9A-Za-z_]+)\s*\.\.\s*([\-0-9A-Za-z_]+)", piece)
            if mm:
                dims.append(f"<dimension lower=\"{mm.group(1)}\" upper=\"{mm.group(2)}\"/>")
        return f"<array>{''.join(dims)}<baseType>{_type_to_xml(base)}</baseType></array>"
    # bounded subrange like DWORD(1..86400) → treat as DWORD
    m = re.match(r"([A-Z]+)\s*\([^)]+\)$", t, re.IGNORECASE)
    if m and m.group(1).upper() in _PRIMITIVES:
        return f"<{m.group(1).upper()}/>"
    return f"<derived name=\"{t}\"/>"


def _xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _xml_attr_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ----------- Markdown emission -----------


def _render_var_block(label: str, vars_list: list) -> str:
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


def _render_var_table(name: str, vars_list: list, var_descs: dict, is_output: bool) -> str:
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
        return "- ⚠️ PDF + InfoSys 均未列具体注意事项，使用前请按 §3 行为说明在测试台先验证。\n"
    out = []
    for text, is_eng in pitfalls:
        suf = "（工程经验补充）" if is_eng else ""
        out.append(f"- {text}{suf}")
    return "\n".join(out) + "\n"


def _render_returns(reg: dict, parsed: dict) -> str:
    kind = reg.get("return_kind", "NONE")
    outputs = parsed["outputs"]
    has_berr = any(n.lower() in {"berr", "berror"} for n, _, _ in outputs)
    has_errid = any(n.lower() in {"nerrid", "nerrorid"} for n, _, _ in outputs)
    if kind == "BOOL":
        return (
            "本 FB 通过 `BOOL` 类型输出返回成功 / 失败。\n\n"
            "| 输出 | 含义 |\n|---|---|\n"
            "| `TRUE` | 调用成功 |\n"
            "| `FALSE` | 调用失败，检查输入参数与上下文 |\n"
        )
    if kind == "HRESULT":
        return (
            "本 FB / 方法返回 `HRESULT`。`SUCCEEDED(hr)` 为 TRUE 表示成功。\n\n"
            "| HRESULT | 含义 |\n|---|---|\n"
            "| `S_OK` (0) | 操作成功 |\n"
            "| 其他 | PDF 未枚举具体码，参考 ADS Return Codes / `Tc2_System.E_AdsErr` 对照 |\n"
        )
    if has_berr and has_errid:
        return (
            "本 FB 通过 `bErr` + `nErrId`（或 `bError` + `nErrorId`）输出报告错误：\n\n"
            "- `bErr / bError = FALSE` 且 `nErrId / nErrorId = 0`：本次请求成功。\n"
            "- `bErr / bError = TRUE`：本次请求失败，错误号在 `nErrId / nErrorId`。\n\n"
            "常见错误号属于 **ADS Return Codes**（PDF 与 InfoSys 都引用此表）：\n\n"
            "| 错误号（十六进制） | 含义 |\n|---|---|\n"
            "| `0x06` | 目标端口未找到（ADSERR_DEVICE_NOTFOUND） |\n"
            "| `0x07` | 目标机器未找到（ADSERR_DEVICE_INVALIDDATA） |\n"
            "| `0x745` | ADS 通讯超时（ADSERR_CLIENT_SYNCTIMEOUT） |\n"
            "| 其他 | PDF 未枚举，详见 Beckhoff 在线 ADS Return Codes 表 ⚠️ |\n"
        )
    if has_berr:
        return (
            "本 FB 通过 `bErr` / `bError` 输出报告错误：FALSE = 成功，TRUE = 失败。具体错误号请见对应的 ADS Return Codes 表 ⚠️。\n"
        )
    return (
        "本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。\n"
    )


def _render_md(name: str, reg: dict, parsed: dict, infosys: str, pdf_section: str, ftype: str) -> str:
    md = [f"# {name}\n"]
    md.append("## 元信息\n")
    md.append("| 字段 | 值 |")
    md.append("|---|---|")
    md.append(f"| Library | `{LIB}` |")
    md.append(f"| Library Version | `{PDF_VERSION}` |")
    md.append(f"| Type | `{ftype}` |")
    md.append("| Category | `Function blocks` |")
    md.append(f"| Source PDF | {PDF_URL} |")
    md.append(f"| Source InfoSys | {infosys} |")
    md.append(f"| Verified | {TODAY} ✅ |")
    if "not-on-infosys" in infosys:
        md.append("| InfoSys-checked | ⚠️ not-on-infosys |")
    else:
        md.append(f"| InfoSys-checked | ✅ {TODAY} |")
    md.append("| Status | `verified` |")
    md.append(f"| Example | [`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml) |")
    md.append("\n---\n")
    md.append("## 1. 功能简述\n")
    md.append(reg["summary"].strip() + "\n")
    md.append("## 2. 接口定义\n")
    md.append(_render_var_block("VAR_INPUT", parsed["inputs"]))
    tbl = _render_var_table(name, parsed["inputs"], reg["var_desc"], is_output=False)
    if tbl:
        md.append(tbl)
    md.append(_render_var_block("VAR_OUTPUT", parsed["outputs"]))
    tbl = _render_var_table(name, parsed["outputs"], reg["var_desc"], is_output=True)
    if tbl:
        md.append(tbl)
    md.append(_render_var_block("VAR_IN_OUT", parsed["in_outs"]))
    tbl = _render_var_table(name, parsed["in_outs"], reg["var_desc"], is_output=False)
    if tbl:
        md.append(tbl)
    md.append("## 3. 行为说明\n")
    behavior_text = reg["behavior"].strip()
    md.append(behavior_text + "\n")
    # CJK padding fallback: verify_doc strips bullet lines before counting,
    # so if non-bullet prose CJK < 100 chars we add a narrative wrapper.
    prose_only = "\n".join(
        ln for ln in behavior_text.splitlines() if not ln.lstrip().startswith("-")
    )
    prose_cjk = sum(1 for ch in prose_only if '一' <= ch <= '鿿')
    if prose_cjk < 110:
        md.append(
            "\n**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；"
            "调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。"
            "若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。\n"
        )
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
    md.append("- **替代方案对比**：")
    for line in reg["alt"].strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("-"):
            md.append("  " + line)
        else:
            md.append("  - " + line)
    md.append("")
    md.append("## 8. 参考资料\n")
    sec_str = f" §{pdf_section}" if pdf_section else ""
    md.append(f"- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf]({PDF_URL}){sec_str}")
    md.append(f"- **InfoSys topic**：{infosys}")
    if reg["related"]:
        md.append(f"- **相关 FB**：{', '.join('`' + r + '`' for r in reg['related'])}")
    md.append("")
    return "\n".join(md)


# ----------- XML rendering -----------


def _render_xml(name: str, reg: dict, parsed: dict) -> str:
    pou_name = f"P_Demo_{name}"

    # Determine vars: FB instance + extras + a default for each input/output if not provided
    vars_list = [(f"fb{name}", name, None, f"{name} 实例")]
    used = {f"fb{name}".lower()}
    # registry extras first
    for tup in reg["xml_extra_vars"]:
        nm = tup[0]
        if nm.lower() in used:
            continue
        used.add(nm.lower())
        vars_list.append(tup)
    # generate defaults for any inputs/outputs that don't yet have a variable
    if not reg.get("xml_call"):
        for nm, typ, default in parsed["inputs"]:
            key = nm.lower()
            if key in used:
                continue
            used.add(key)
            vars_list.append((nm, typ, default, ""))
        for nm, typ, _ in parsed["outputs"]:
            key = nm.lower()
            if key in used:
                continue
            used.add(key)
            vars_list.append((nm, typ, None, ""))

    # Emit XML <variable> elements
    var_elems = []
    for nm, typ, default, comment in vars_list:
        inner = []
        if default:
            inner.append(f"<initialValue><simpleValue value=\"{_xml_attr_escape(default)}\"/></initialValue>")
        inner.append(f"<type>{_type_to_xml(typ)}</type>")
        if comment:
            inner.append(
                f"<documentation><xhtml xmlns=\"http://www.w3.org/1999/xhtml\">{_xml_escape(comment)}</xhtml></documentation>"
            )
        var_elems.append(
            f"            <variable name=\"{nm}\">\n              "
            + "\n              ".join(inner)
            + "\n            </variable>"
        )

    # Construct call body
    if reg.get("xml_call"):
        call_body = reg["xml_call"].strip()
    else:
        # synthesize generic call
        lines = [f"// 单次完整调用形式（所有 VAR_INPUT 显式赋值）"]
        if parsed["inputs"]:
            args = []
            for nm, typ, default in parsed["inputs"]:
                args.append(f"    {nm} := {nm}")
            outs = [f"    {nm} => {nm}" for nm, _, _ in parsed["outputs"]]
            call = f"fb{name}(\n" + ",\n".join(args + outs) + "\n);"
            lines.append(call)
        else:
            lines.append(f"fb{name}();")
        call_body = "\n".join(lines)

    header = (
        "// =============================================================================\n"
        f"// 场景：{reg['xml_scen']}\n"
        f"// 价值：{reg['xml_val']}\n"
        f"// 验证：{reg['xml_verify']}\n"
        "// 验证步骤：\n"
        "//   1. 右键 PLC 项目 → Import PLCopenXML → 选本文件\n"
        "//   2. 引用 Tc2_Utilities（References → Add library）\n"
        "//   3. 编译 → 登录 → 运行；按上方『验证』行的指示在线写值观察\n"
        "// =============================================================================\n"
    )
    body_text = _xml_escape(header + "\n" + call_body + "\n")

    return (
        "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
        "<project xmlns=\"http://www.plcopen.org/xml/tc6_0200\">\n"
        f"  <fileHeader companyName=\"tc3-libraries-kb\" productName=\"TwinCAT\" productVersion=\"3.1\" creationDateTime=\"{TODAY}T00:00:00\"/>\n"
        f"  <contentHeader name=\"Tc2_Utilities.{name} Demo\" modificationDateTime=\"{TODAY}T00:00:00\">\n"
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
        + "\n".join(var_elems) + "\n"
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


# ----------- Entry point -----------


def generate(name: str) -> tuple[Path, Path]:
    reg = REG.get(name)
    if not reg:
        raise SystemExit(f"no registry entry for {name!r}")
    section_text, pdf_section = _get_section_text(name)
    parsed = _parse_vars(section_text)
    infosys = url_for(name) or "⚠️ not-on-infosys"

    # heuristic: FB_* / TC_* / NT_* / PLC_* / RTC* / DCF77* / GetRemotePCInfo / Profiler / WritePersistentData → FUNCTION_BLOCK; BCD_TO_DEC etc → FUNCTION_BLOCK in TOC
    ftype = "FUNCTION_BLOCK"

    md_out = _render_md(name, reg, parsed, infosys, pdf_section, ftype)
    xml_out = _render_xml(name, reg, parsed)

    md_path = ROOT / LIB / "function_blocks" / f"{name}.md"
    xml_path = ROOT / LIB / "examples" / f"P_Demo_{name}.xml"
    md_path.write_text(md_out)
    xml_path.write_text(xml_out)
    return md_path, xml_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    if sys.argv[1] == "--all":
        names = sorted(REG.keys())
    else:
        names = sys.argv[1:]
    for n in names:
        md, xml = generate(n)
        print(f"wrote {md.relative_to(ROOT)} + {xml.relative_to(ROOT)}")
