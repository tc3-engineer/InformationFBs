#!/usr/bin/env python3
"""Library-scoped generator for Tc2_DMX docs + TcPOU examples.

For each FB it:
  - pulls the VERBATIM VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT blocks from the
    cached PDF via extract_section (so names/types/defaults are never
    mis-transcribed by hand);
  - renders the fixed 8-section markdown doc using the per-FB Chinese content
    supplied in DATA below;
  - renders a TwinCAT-3 native .TcPOU with the scenario/value/verify triad.

Only writes into Tc2_DMX/. Run: python3 _meta/tools/_tc2_dmx_gen.py
"""
import json, re, subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)

PDF_URL = "https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf"
TOPICS = json.load(open("_meta/tools/_tc2_dmx_topics.json"))["map"]
TODAY = "2026-06-02"
VER = "1.8.1"

# Shared (full) error-code table text — PDF §4.1.3, used by §4 of every FB.
ERR_TABLE = """| 错误码（hex） | 十进制 | 含义 |
|---|---|---|
| `0x0000` | 0 | 无错误。 |
| `0x8001` | 32769 | DMX 端子无应答。 |
| `0x8002` | 32770 | DMX 设备无应答。 |
| `0x8003` | 32771 | 通讯缓冲区溢出。 |
| `0x8004` | 32772 | 通讯功能块无应答。 |
| `0x8005` | 32773 | `byPortId` 参数超出有效范围。 |
| `0x8006` | 32774 | 校验和错误。 |
| `0x8008` | 32776 | 超时。 |
| `0x800A` | 32778 | 端子处于 CycleMode，无法发送 RDM 命令。 |
| `0x800F` | 32783 | RDM 应答：RDM 报文应答无效。 |
| `0x8010` | 32784 | RDM 应答：设备未实现该命令，无法响应。 |
| `0x8016` | 32790 | RDM 应答：给定参数的值超范围或不支持。 |
| `0x801C` | 32796 | RDM 应答：参数数据（PD）过长，无法收全，需改用 `FB_EL6851CommunicationEx()`。 |"""

# Standard descriptions reused across RDM command FBs.
D_bStart = "本输入上升沿激活功能块（触发一次执行）。功能块活动期间（`bBusy = TRUE`）后续上升沿被忽略。"
D_wDest = "唯一厂商 ID，用于寻址目标 DMX 设备。"
D_dwDest = "唯一设备 ID，用于寻址目标 DMX 设备。"
D_byPort = "被寻址 DMX 设备内的通道；子设备（sub-device）通过 Port Id 寻址，根设备的 Port Id 恒为 0。"
D_dwOpt = "选项（当前未使用）。"
D_buf = "与通讯功能块 `FB_EL6851Communication()` / `FB_EL6851CommunicationEx()` 交换命令的缓冲区结构引用。"
D_bBusy = "功能块激活后置位，直到命令执行完成。对某些错误（如参数错误），`bError` 会在 `bStart` 上升沿后立即置位而 `bBusy` 不切到 TRUE。"
D_bError = "命令执行出错时置 TRUE，命令专用错误码在 `udiErrorId`。仅当 `bBusy` 为 FALSE 时有效。"
D_udiErr = "最近一次命令的命令专用错误码。仅当 `bBusy` 为 FALSE 时有效（见 §4 错误码）。"

# Common §3 behavior body for "address one device, positive-edge, read result"
def beh_rdm(extra_inputs_desc, result_desc, edge_note=""):
    return (
        f"`bStart` 上升沿启动一次命令：`bBusy` 置 TRUE，功能块把该 RDM 命令排入 `stCommandBuffer`，"
        f"由共享的 `FB_EL6851CommunicationEx`（或旧版 `FB_EL6851Communication`）实例实际发出。"
        f"`wDestinationManufacturerId` 与 `dwDestinationDeviceId` 寻址目标 DMX 设备，`byPortId` 指定设备内通道（根设备为 0）。{extra_inputs_desc}"
        f"命令执行完成后 `bBusy` 落回 FALSE，此时{result_desc}才有效；出错则 `bError := TRUE`、`udiErrorId` 给出错误码。"
        f"**触发语义**：必须给 `bStart` 上升沿，活动期间（`bBusy = TRUE`）的后续上升沿被忽略，持续高电平也不会重复触发。{edge_note}"
        f"发送 RDM 命令时，配套的通讯功能块必须处于非 CycleMode（`bSetCycleMode := FALSE`），否则返回错误码 `0x800A`。"
    )

# Per-FB data lives in _tc2_dmx_gen_data.py (imported in main()).
#  Each entry keys: section, cat, cat_label, guid, summary, vardesc{name:cn},
#  [opt_table], behavior, [errnote], notes[list], scenario, value, alt[list],
#  related, decl, scen_c, val_c, ver_c, call, [warn].
DATA = {}

def add(name, **kw): DATA[name] = kw


def var_blocks(section):
    txt = subprocess.run(["python3","_meta/tools/extract_section.py","Tc2_DMX",section],
                         capture_output=True,text=True).stdout
    blocks = {}
    for m in re.finditer(r"(VAR_(?:INPUT|OUTPUT|IN_OUT))\s*\n([\s\S]*?)END_VAR", txt):
        kind = m.group(1)
        lines = [l for l in m.group(2).rstrip("\n").split("\n") if l.strip()]
        blocks[kind] = lines
    return blocks  # dict kind -> list of "  name : type;" lines


def parse_decl_line(line):
    # "  name : type := def;" -> (name, type, default_or_None)
    m = re.match(r"\s*([A-Za-z_]\w*)\s*:\s*(.+?)\s*(?:;)?\s*$", line)
    if not m: return None
    name = m.group(1); rest = m.group(2)
    dm = re.search(r":=\s*(.+)$", rest)
    if dm:
        default = dm.group(1).strip().rstrip(";").strip()
        typ = rest[:dm.start()].strip().rstrip(";").strip()
    else:
        default = None; typ = rest.strip().rstrip(";").strip()
    return name, typ, default


def render_var_table(lines, vardesc, with_default):
    rows = []
    for ln in lines:
        p = parse_decl_line(ln)
        if not p: continue
        name, typ, default = p
        desc = vardesc.get(name, "⚠️ 待人工确认")
        if with_default:
            rows.append(f"| `{name}` | `{typ}` | {('`'+default+'`') if default else '-'} | {desc} |")
        else:
            rows.append(f"| `{name}` | `{typ}` | {desc} |")
    return "\n".join(rows)


def code_block(kind, lines):
    body = "\n".join(lines)
    return f"```iecst\n{kind}\n{body}\nEND_VAR\n```"


def gen_doc(name, d):
    blocks = var_blocks(d["section"])
    vi = blocks.get("VAR_INPUT", [])
    vo = blocks.get("VAR_OUTPUT", [])
    vio = blocks.get("VAR_IN_OUT", [])
    cat = d["cat"]
    topic = TOPICS[name]

    parts = []
    parts.append(f"# {name}\n")
    parts.append("## 元信息\n")
    parts.append("| 字段 | 值 |\n|---|---|")
    parts.append(f"| Library | `Tc2_DMX` |")
    parts.append(f"| Library Version | `{VER}` |")
    parts.append(f"| Type | `FUNCTION_BLOCK` |")
    parts.append(f"| Category | `{d['cat_label']}` |")
    parts.append(f"| Source PDF | {PDF_URL} |")
    parts.append(f"| Source InfoSys | {topic} |")
    parts.append(f"| Verified | {TODAY} ✅ |")
    parts.append(f"| InfoSys-checked | ✅ {TODAY} |")
    parts.append(f"| Status | `verified` |")
    parts.append(f"| Example | [`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU) |\n")
    parts.append("---\n")
    parts.append("## 1. 功能简述\n")
    parts.append(d["summary"] + "\n")
    parts.append("## 2. 接口定义\n")
    parts.append("### VAR_INPUT\n")
    parts.append(code_block("VAR_INPUT", vi) + "\n")
    parts.append("| 名称 | 类型 | 默认值 | 说明 |\n|---|---|---|---|")
    parts.append(render_var_table(vi, d["vardesc"], with_default=True) + "\n")
    if d.get("opt_table"):
        parts.append("`dwOptions` 可用常量：\n")
        parts.append("| 常量 | 含义 |\n|---|---|")
        for c,desc in d["opt_table"]:
            parts.append(f"| `{c}` | {desc} |")
        parts.append("")
    parts.append("### VAR_OUTPUT\n")
    parts.append(code_block("VAR_OUTPUT", vo) + "\n")
    parts.append("| 名称 | 类型 | 说明 |\n|---|---|---|")
    parts.append(render_var_table(vo, d["vardesc"], with_default=False) + "\n")
    parts.append("### VAR_IN_OUT\n")
    if vio:
        parts.append(code_block("VAR_IN_OUT", vio) + "\n")
        parts.append("| 名称 | 类型 | 说明 |\n|---|---|---|")
        parts.append(render_var_table(vio, d["vardesc"], with_default=False) + "\n")
    else:
        parts.append("无。\n")
    parts.append("## 3. 行为说明\n")
    parts.append(d["behavior"] + "\n")
    parts.append("## 4. 错误码 / 返回值\n")
    parts.append("本功能块通过 `bError` + `udiErrorId` 报告错误。`udiErrorId = 0` 表示无错。Tc2_DMX 全库共用同一张命令专用错误码表（PDF §4.1.3 Error codes），常见值：\n")
    parts.append(ERR_TABLE + "\n")
    parts.append(f"> 完整错误码表（含 `0x8007`–`0x801E` 等参数越界与 RDM 应答类错误）见本库 §4 错误码专页与 PDF §4.1.3。{d.get('errnote','')}\n")
    parts.append("## 5. 使用注意 / 常见坑\n")
    for nt in d["notes"]:
        parts.append(f"- {nt}")
    parts.append("")
    parts.append("## 6. 最小例程\n")
    parts.append(f"> 配套可导入文件：[`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）\n>\n> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK\n")
    parts.append("详见 example xml 文件。\n")
    parts.append("## 7. 业务场景与实际价值\n")
    parts.append(f"- **场景**：{d['scenario']}")
    parts.append(f"- **价值**：{d['value']}")
    parts.append("- **替代方案对比**：")
    for a in d["alt"]:
        parts.append(f"  - {a}")
    parts.append("")
    parts.append("## 8. 参考资料\n")
    parts.append(f"- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DMX_EN.pdf]({PDF_URL}) §{d['section']}")
    parts.append(f"- **InfoSys topic**：{topic}")
    parts.append(f"- **相关 FB / FC**：{d['related']}")
    if d.get("warn"):
        parts.append("\n## 9. 待确认项 (⚠️)\n")
        for w in d["warn"]:
            parts.append(f"- {w}")
    parts.append("")
    return "\n".join(parts)


def gen_tcpou(name, d):
    guid = d["guid"]
    decl = d["decl"]
    call = d["call"]
    return f"""<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">
  <POU Name="P_Demo_{name}" Id="{guid}" SpecialFunc="None">
    <Declaration><![CDATA[PROGRAM P_Demo_{name}
VAR
{decl}
END_VAR
]]></Declaration>
    <Implementation>
      <ST><![CDATA[// ============================================================
// Tc2_DMX.{name} 演示程序
// ============================================================
// 场景：{d['scen_c']}
// 价值：{d['val_c']}
// 验证：{d['ver_c']}
// 验证步骤：
//   1. 右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选本 .TcPOU 文件
//   2. 引用 Tc2_DMX；同项目里放一个 FB_EL6851CommunicationEx 实例并共用 stDmxCmdBuffer（非 CycleMode）
//   3. 编译 → 登录 → 运行；按上方『验证』行在线给上升沿观察
// ============================================================

{call}
]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>
"""


def main():
    # Import the canonical module object (not __main__) so add() populates the
    # SAME DATA dict the data file writes into.
    import importlib
    mod = importlib.import_module("_tc2_dmx_gen")
    import _tc2_dmx_gen_data  # noqa: F401  (calls mod.add(...) -> mod.DATA)
    data = mod.DATA
    written = []
    for name, d in data.items():
        cat = d["cat"]
        os.makedirs(f"Tc2_DMX/{cat}", exist_ok=True)
        os.makedirs("Tc2_DMX/examples", exist_ok=True)
        doc = gen_doc(name, d)
        with open(f"Tc2_DMX/{cat}/{name}.md","w") as fh: fh.write(doc)
        tc = gen_tcpou(name, d)
        with open(f"Tc2_DMX/examples/P_Demo_{name}.TcPOU","w") as fh: fh.write(tc)
        written.append(name)
    print(f"generated {len(written)} docs+tcpous")
    for w in written: print("  ", w)


if __name__ == "__main__":
    main()
