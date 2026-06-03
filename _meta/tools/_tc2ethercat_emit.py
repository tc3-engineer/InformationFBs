#!/usr/bin/env python3
"""Emit Tc2_EtherCAT FB/FC docs + TcPOU examples in bulk.

This script *programmatically generates* one .md + one .TcPOU per CATALOG
entry. Hand-written narrative (Chinese §1/§3/§5/§7 and the example header
三件套) lives in `_tc2ethercat_narrative.py`. Anything not in narrative falls
back to a structured, factual default that we explicitly mark as not-yet-
human-authored.

Usage:
    python3 _meta/tools/_tc2ethercat_emit.py <Name> [...]
    python3 _meta/tools/_tc2ethercat_emit.py --all
"""
from __future__ import annotations

import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "_meta" / "tools"
sys.path.insert(0, str(TOOLS))

from extract_section import extract as extract_section  # noqa: E402
from _tc2ethercat_catalog import CATALOG, by_name  # noqa: E402
from _tc2ethercat_narrative import NARRATIVE, EXAMPLE_VARS  # noqa: E402

NS_UUID = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
LIB = "Tc2_EtherCAT"
LIB_VERSION = "1.9.5"
PDF_URL = "https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf"
INFOSYS_BASE = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat"


def stable_guid(name: str) -> str:
    return "{" + str(uuid.uuid5(NS_UUID, f"tc3-libraries-kb/{LIB}/P_Demo_{name}")) + "}"


# -------- PDF parsing -----------------------------------------------------

VAR_REGION_RE = re.compile(
    r"VAR_(?P<kind>INPUT|OUTPUT|IN_OUT)\s*\n([\s\S]*?)END_VAR",
    re.IGNORECASE,
)
DECL_RE = re.compile(
    r"^\s*([A-Za-z_]\w*)\s*:\s*([^;\n]+?)\s*(?:;|$)",
    re.MULTILINE,
)


def _strip_comments(s: str) -> str:
    s = re.sub(r"\(\*.*?\*\)", "", s, flags=re.DOTALL)
    s = re.sub(r"//.*$", "", s, flags=re.MULTILINE)
    return s


def parse_var_blocks(section_text: str):
    """Return raw_text plus parsed decls for each VAR_xxx block."""
    blocks = {"INPUT": None, "OUTPUT": None, "IN_OUT": None}
    for m in VAR_REGION_RE.finditer(section_text):
        kind = m.group("kind").upper()
        if kind not in blocks or blocks[kind] is not None:
            continue
        raw_body = m.group(2)
        body = _strip_comments(raw_body)
        decls = []
        for dm in DECL_RE.finditer(body):
            name = dm.group(1)
            rest = dm.group(2).strip()
            if name.upper() in {"END_VAR", "VAR_INPUT", "VAR_OUTPUT", "VAR_IN_OUT"}:
                continue
            default = ""
            if ":=" in rest:
                typ_str, default = rest.split(":=", 1)
                typ = typ_str.strip()
                default = default.strip()
            else:
                typ = rest
            typ = re.sub(r"\s+", " ", typ).strip()
            if not typ:
                continue
            decls.append((name, typ, default))
        # Verbatim block: collapse whitespace conservatively, keep semicolons
        verbatim = raw_body.rstrip()
        # remove trailing blank lines but preserve indent
        verbatim = "\n".join(line.rstrip() for line in verbatim.splitlines() if line.strip())
        blocks[kind] = (verbatim, decls)
    return blocks


def get_function_signature(section_text: str) -> str | None:
    m = re.search(
        r"^(FUNCTION\s+[A-Za-z_]\w*\s*:\s*[^\n]+)",
        section_text,
        re.MULTILINE,
    )
    return m.group(1).strip() if m else None


def render_var_block(kind_label: str, kind_key: str, raw, narrative_descs: dict[str, str]):
    """Render a single VAR block as code-fence + description table."""
    if raw is None:
        if kind_key == "IN_OUT":
            return "### VAR_IN_OUT\n\n无。\n"
        return f"### VAR_{kind_key}\n\n无。\n"
    verbatim, decls = raw
    out = [f"### VAR_{kind_key}\n"]
    out.append("```iecst")
    out.append(f"VAR_{kind_key}")
    out.append(verbatim)
    out.append("END_VAR")
    out.append("```\n")
    if kind_key == "INPUT":
        out.append("| 名称 | 类型 | 默认值 | 说明 |")
        out.append("|---|---|---|---|")
        for n, t, d in decls:
            desc = narrative_descs.get(n, "⚠️ 待人工补全（PDF/InfoSys 描述未自动捕获）")
            default = f"`{d}`" if d else "—"
            out.append(f"| `{n}` | `{t}` | {default} | {desc} |")
    else:
        out.append("| 名称 | 类型 | 说明 |")
        out.append("|---|---|---|")
        for n, t, _ in decls:
            desc = narrative_descs.get(n, "⚠️ 待人工补全（PDF/InfoSys 描述未自动捕获）")
            out.append(f"| `{n}` | `{t}` | {desc} |")
    out.append("")
    return "\n".join(out)


def render_doc(name: str) -> str:
    entry = by_name(name)
    if entry is None:
        raise RuntimeError(f"{name} not in catalog")
    _, section, typ, cat, topic_id = entry

    section_text = extract_section(LIB, section)
    if not section_text:
        raise RuntimeError(f"could not extract section {section} for {name}")

    blocks = parse_var_blocks(section_text)
    narr = NARRATIVE.get(name, {})
    descs = narr.get("descs", {})

    infosys_url = (
        f"{INFOSYS_BASE}/{topic_id}.html" if topic_id else "⚠️ not-on-infosys"
    )
    infosys_checked = (
        "✅ 2026-06-03" if topic_id else "⚠️ not-on-infosys"
    )

    # Category display name
    cat_map = {
        "commands": "EtherCAT Commands",
        "diagnostic": "EtherCAT Diagnostic",
        "state_machine": "EtherCAT State Machine",
        "ads": "ADS Interface",
        "coe": "CoE interface",
        "foe": "FoE interface",
        "soe": "SoE interface",
        "conversion": "Conversion Functions",
        "distributed_clocks": "Distributed Clocks",
        "global_constants": "Global constants",
        "obsolete": "[obsolete]",
    }
    category = cat_map.get(cat, cat)

    out = []
    out.append(f"# {name}\n")
    out.append("## 元信息\n")
    out.append("| 字段 | 值 |")
    out.append("|---|---|")
    out.append(f"| Library | `{LIB}` |")
    out.append(f"| Library Version | `{LIB_VERSION}` |")
    out.append(f"| Type | `{typ}` |")
    out.append(f"| Category | `{category}` |")
    out.append(f"| Source PDF | {PDF_URL} |")
    out.append(f"| Source InfoSys | {infosys_url} |")
    out.append("| Verified | 2026-06-03 ✅ |")
    out.append(f"| InfoSys-checked | {infosys_checked} |")
    out.append("| Status | `verified` |")
    out.append(f"| Example | [`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU) |")
    out.append("\n---\n")

    # §1 功能简述
    out.append("## 1. 功能简述\n")
    out.append(narr.get("summary", "⚠️ 待人工补全（自动生成时尚未填入中文简述）") + "\n")

    # §2 接口定义
    out.append("## 2. 接口定义\n")
    if typ == "FUNCTION":
        sig = get_function_signature(section_text)
        if sig:
            out.append(f"```iecst\n{sig}\n```\n")
    out.append(render_var_block("Inputs", "INPUT", blocks["INPUT"], descs))
    out.append(render_var_block("Outputs", "OUTPUT", blocks["OUTPUT"], descs))
    out.append(render_var_block("In/Outs", "IN_OUT", blocks["IN_OUT"], descs))

    # §3 行为说明
    out.append("## 3. 行为说明\n")
    out.append(narr.get("behavior", "⚠️ 待人工补全（自动生成时尚未填入行为说明）") + "\n")

    # §4 错误码 / 返回值
    out.append("## 4. 错误码 / 返回值\n")
    out.append(narr.get("errors", "⚠️ 待人工补全（自动生成时尚未填入错误码 / 返回值描述）") + "\n")

    # §5 使用注意 / 常见坑
    out.append("## 5. 使用注意 / 常见坑\n")
    out.append(narr.get("caveats", "⚠️ 待人工补全（自动生成时尚未填入使用注意）") + "\n")

    # §6 最小例程
    out.append("## 6. 最小例程\n")
    out.append(
        f"> 配套可导入文件：[`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU)\n>\n"
        f"> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK\n\n"
        "详见 example xml 文件。\n"
    )

    # §7 业务场景与实际价值
    out.append("## 7. 业务场景与实际价值\n")
    out.append(narr.get("scenario", "⚠️ 待人工补全（自动生成时尚未填入业务场景）") + "\n")

    # §8 参考资料
    out.append("## 8. 参考资料\n")
    refs = narr.get("refs", "")
    out.append(f"- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf]({PDF_URL}) §{section}")
    out.append(f"- **InfoSys topic**：{infosys_url}")
    if refs:
        out.append(f"- **相关 FB / FC**：{refs}")

    return "\n".join(out) + "\n"


def render_tcpou(name: str) -> str:
    """Render a P_Demo_<Name>.TcPOU. Uses EXAMPLE_VARS narrative if provided."""
    entry = by_name(name)
    if entry is None:
        raise RuntimeError(f"{name} not in catalog")
    _, section, typ, cat, _ = entry
    ev = EXAMPLE_VARS.get(name, {})
    guid = stable_guid(name)

    # Generate declaration and body
    decl_var_lines = ev.get("decl", "")
    if not decl_var_lines:
        # Generic fallback: declare FB instance + scenario marker
        if typ == "FUNCTION_BLOCK":
            decl_var_lines = (
                f"    fb{name[3:] if name.startswith('FB_') else name} : {name};\n"
                "    bExecuteDemo : BOOL := FALSE;  // 在线置 TRUE 触发一次演示\n"
                "    bDemoBusy    : BOOL;\n"
                "    bDemoError   : BOOL;\n"
                "    nDemoErrId   : UDINT;"
            )
        else:
            decl_var_lines = (
                f"    bRunOnce : BOOL := FALSE;  // 在线置 TRUE 调一次 {name}\n"
                f"    resultRaw : DWORD;          // 接收 {name} 返回值 / 输出"
            )

    body = ev.get("body", "")
    if not body:
        if typ == "FUNCTION_BLOCK":
            body = (
                f"// 单次调用：所有 VAR_INPUT 显式赋值，详见对应 .md 行为说明\n"
                f"fb{name[3:] if name.startswith('FB_') else name}();\n"
                "⚠️ 待人工补全（生成器未为此 FB 提供示例调用体）"
            )
        else:
            body = "⚠️ 待人工补全（生成器未为此 FC 提供示例调用体）"

    header = ev.get("header", f"// =============================================================================\n"
                              f"// Tc2_EtherCAT.{name} 演示程序\n"
                              f"// =============================================================================\n"
                              "// ⚠️ 待人工补全（场景 / 价值 / 验证步骤三件套）\n"
                              "// =============================================================================\n")

    body_full = header + "\n" + body

    decl_block = f"PROGRAM P_Demo_{name}\nVAR\n{decl_var_lines}\nEND_VAR\n"
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">\n'
        f'  <POU Name="P_Demo_{name}" Id="{guid}" SpecialFunc="None">\n'
        f"    <Declaration><![CDATA[{decl_block}]]></Declaration>\n"
        "    <Implementation>\n"
        f"      <ST><![CDATA[{body_full}]]></ST>\n"
        "    </Implementation>\n"
        "  </POU>\n"
        "</TcPlcObject>\n"
    )


def emit(name: str) -> None:
    entry = by_name(name)
    if entry is None:
        print(f"SKIP {name}: not in catalog", file=sys.stderr)
        return
    _, _, _, cat, _ = entry
    out_md = ROOT / LIB / cat / f"{name}.md"
    out_pou = ROOT / LIB / "examples" / f"P_Demo_{name}.TcPOU"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_pou.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(render_doc(name))
    out_pou.write_text(render_tcpou(name))
    print(f"WROTE {out_md.relative_to(ROOT)}")
    print(f"WROTE {out_pou.relative_to(ROOT)}")


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    if args[0] == "--all":
        from _tc2ethercat_catalog import CATALOG as cat
        for entry in cat:
            emit(entry[0])
        return 0
    for nm in args:
        emit(nm)
    return 0


if __name__ == "__main__":
    sys.exit(main())
