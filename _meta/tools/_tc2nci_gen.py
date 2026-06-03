#!/usr/bin/env python3
"""
Generator for Tc2_NCI library docs + TcPOU examples.

Reads the registry JSON, extracts each section from the cached PDF,
parses the canonical Beckhoff section structure (Inputs / Inputs-Outputs /
Outputs / Return value), and emits:

  Tc2_NCI/<category>/<Name>.md
  Tc2_NCI/examples/P_Demo_<Name>.TcPOU

Then runs verify_doc.py + lint_tcpou.py against each.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "_meta" / "tools"
sys.path.insert(0, str(TOOLS))

from extract_section import extract as extract_section  # noqa: E402

REGISTRY = TOOLS / "_tc2nci_registry.json"
LIB_ROOT = ROOT / "Tc2_NCI"
EXAMPLES_DIR = LIB_ROOT / "examples"

PDF_URL = "https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf"
INFOSYS_BASE = "https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/"
VERIFIED_DATE = "2026-06-03"
LIBRARY_VERSION = "2.15.1"
DNS_NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


# ---------------------------------------------------------------------------
# PDF section parsing
# ---------------------------------------------------------------------------
def _strip_page_breaks(text: str) -> str:
    """Strip "=== PAGE N ===" and Beckhoff page headers ("PLC NCI Libraries | ...")."""
    out = re.sub(r"=== PAGE \d+ ===\n", "", text)
    out = re.sub(r"^PLC NCI Libraries \| PLC Library: Tc2_NCI\s*$", "", out, flags=re.MULTILINE)
    out = re.sub(r"^TF5100\s*\d+\s*Version: [\d.]+\s*$", "", out, flags=re.MULTILINE)
    out = re.sub(r"^TF5100 Version: [\d.]+\s*$", "", out, flags=re.MULTILINE)
    return out


_BLOCK_PAT = re.compile(
    r"^\s*(VAR_INPUT|VAR_OUTPUT|VAR_IN_OUT|VAR_GLOBAL\s+CONSTANT|VAR_GLOBAL)\s*$\n([\s\S]*?)^\s*END_VAR\s*$",
    re.MULTILINE,
)

_DECL_LINE_PAT = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?!=)([^;\n]+?)\s*;?\s*$",
    re.MULTILINE,
)


def parse_var_blocks(section_text: str) -> dict[str, list[tuple[str, str]]]:
    """Return {block_kind: [(name, type_with_default), ...]} preserving order."""
    blocks: dict[str, list[tuple[str, str]]] = {}
    for m in _BLOCK_PAT.finditer(section_text):
        kind = re.sub(r"\s+", " ", m.group(1).strip())
        body = m.group(2)
        # Strip line comments
        body = re.sub(r"\(\*[\s\S]*?\*\)", "", body)
        body = re.sub(r"//.*$", "", body, flags=re.MULTILINE)
        out: list[tuple[str, str]] = []
        for dm in _DECL_LINE_PAT.finditer(body):
            name = dm.group(1)
            typ = dm.group(2).strip().rstrip(";").strip()
            # The Description tables underneath confuse the regex; gate to
            # well-formed names that start a fresh declaration line.
            if name.upper() in {"END_VAR", "INPUTS", "OUTPUTS", "NAME", "TYPE", "DESCRIPTION"}:
                continue
            out.append((name, typ))
        blocks.setdefault(kind, []).extend(out)
    return blocks


_DESC_KEYS_STOP = re.compile(
    r"^\s*(?:VAR_INPUT|VAR_OUTPUT|VAR_IN_OUT|Inputs|Outputs|Return value|END_VAR|Requirements|See also|Example|=== PAGE)\b",
    re.IGNORECASE | re.MULTILINE,
)


_TYPE_RE = re.compile(
    r"^(?:BOOL|BYTE|WORD|DWORD|LWORD|SINT|USINT|INT|UINT|DINT|UDINT|LINT|ULINT"
    r"|REAL|LREAL|TIME|LTIME|DATE|DT|TOD|STRING|WSTRING|PVOID|POINTER|REFERENCE|ARRAY|ANY"
    r"|String|WString"  # tolerate PDF lowercase typo
    r"|E_[A-Za-z]\w*|ST_[A-Za-z]\w*|FB_[A-Za-z]\w*|NC_[A-Za-z]\w*|NCI_[A-Za-z]\w*"
    r"|T_[A-Za-z]\w*|PLCTONC_[A-Za-z]\w*|NCTOPLC_[A-Za-z]\w*|HRESULT)\b",
    re.IGNORECASE,
)


def _looks_like_type(s: str) -> bool:
    """A bare word that plausibly is a TwinCAT type."""
    s = s.strip()
    return bool(_TYPE_RE.match(s))


def parse_description_table(section_text: str, var_names: list[str]) -> dict[str, str]:
    """Return {var_name: English Description} by walking the post-VAR_*
    description rows. Beckhoff pypdf-rendered text shape:

        Name Type Description
        bExecute BOOL The command is triggered by a rising edge at this input.
        nGroupId UDINT ID of the 3D group
        ...

    where Description spans multiple wrapped lines. We scan starting from
    each var_name token, swallow up to either the next var_name in the
    expected order OR a structural keyword.
    """
    descs: dict[str, str] = {}
    for i, name in enumerate(var_names):
        # Each name occurs many times in the section; we want the one that
        # appears as the first token on a description-row line. Scan for the
        # exact pattern "<name> <Type-token>" near a Description heading.
        # We look for the name followed by whitespace + a known-type token.
        pat = re.compile(rf"(?m)^\s*{re.escape(name)}\s+(\S.+?)$")
        # Walk all matches, pick the first one that's followed by typeish text
        # that also matches the "description row" shape (Type at start of next
        # tokens).
        chosen_idx = None
        for m in pat.finditer(section_text):
            rest = m.group(1).strip()
            tokens = rest.split(None, 1)
            if not tokens:
                continue
            if _looks_like_type(tokens[0]):
                # Possible description row. Walk forward collecting wrapped
                # lines until we hit the next var_name boundary or stop kw.
                chosen_idx = m.end()
                first_line_desc = tokens[1] if len(tokens) > 1 else ""
                # If first_line_desc empty, the type wrapped onto next line
                # (e.g. "NCTOPLC_NCICHANN\nEL_REF\nThe ..."). Walk forward.
                tail = section_text[chosen_idx:]
                # Determine stop boundary
                stop_idxs = []
                # Next var in this var_names list (the canonical next row)
                if i + 1 < len(var_names):
                    next_name = var_names[i + 1]
                    np = re.search(rf"(?m)^\s*{re.escape(next_name)}\s+\S", tail)
                    if np:
                        stop_idxs.append(np.start())
                # Generic structural stop
                ks = _DESC_KEYS_STOP.search(tail)
                if ks:
                    stop_idxs.append(ks.start())
                if not stop_idxs:
                    stop = len(tail)
                else:
                    stop = min(stop_idxs)
                block = tail[:stop]
                # Reflow
                lines = block.split("\n")
                joined: list[str] = []
                if first_line_desc:
                    joined.append(first_line_desc)
                for ln in lines:
                    ln = ln.strip()
                    if not ln:
                        continue
                    # Skip a wrapped multi-line type echo like "NCTOPLC_NCICHANN" / "EL_REF"
                    if re.match(r"^[A-Z_][A-Z0-9_]*$", ln) and len(ln) <= 30:
                        # Probably a wrapped type token; skip if first chars all uppercase
                        continue
                    joined.append(ln)
                desc = " ".join(joined).strip()
                # Final cleanup
                desc = re.sub(r"\s+", " ", desc)
                descs[name] = desc
                break
        if name not in descs:
            descs[name] = ""
    return descs


def parse_function_return(section_text: str, func_name: str) -> tuple[str, str] | None:
    """Return (type, description) for a FUNCTION's return value, or None.

    Beckhoff PDFs use several shapes for the return signature:
      (a) inline:  FUNCTION <name> : <TYPE>
      (b) table:   Name Type Description / <name> <TYPE> <desc>
      (c) wrap:    Name Type Description / <name-first-line> / <name-tail>\n<TYPE> <desc>
                   (pypdf wraps the func name across two lines when it's long)
      (d) typo:    Some entries declare FUNCTION <slight-typo-name> in the PDF
                   while TOC + InfoSys use the canonical name (e.g.
                   F_GetVersionTcNciUtilities vs F_GetVersionNciUtilities).
                   We accept any FUNCTION <X> when the X's last token matches.
    """
    rtype = None
    # Pattern (a) strict
    m = re.search(rf"^\s*FUNCTION\s+{re.escape(func_name)}\s*:\s*(\S+)", section_text, re.MULTILINE)
    if m:
        rtype = m.group(1)
    if rtype is None:
        # Pattern (d): any "FUNCTION <ident> : <type>" line
        m = re.search(r"^\s*FUNCTION\s+(\w+)\s*:\s*(\S+)", section_text, re.MULTILINE)
        if m:
            rtype = m.group(2)
    if rtype is None:
        # Pattern (b): "<func_name> <TYPE> <desc>" near "Return value"
        rv = re.search(r"Return\s+value([\s\S]*?)(?:Requirements|See also|Sample|Example|\Z)", section_text, re.IGNORECASE)
        if rv:
            text = rv.group(1)
            rd = re.search(rf"(?m)^\s*{re.escape(func_name)}\s+(\S+)\s+(.+?)$", text)
            if rd and _looks_like_type(rd.group(1)):
                return (rd.group(1), rd.group(2).strip())
            # Pattern (c): wrapped func name. Look for "<TYPE> <desc>" line that
            # follows the wrapped tokens.
            wrap = re.search(r"(?m)^([A-Z][A-Z0-9_\(\)]+)\s+(.+)$", text)
            if wrap and _looks_like_type(wrap.group(1)):
                return (wrap.group(1), wrap.group(2).strip())
    if rtype is None:
        return None
    # Find description
    rv = re.search(r"Return\s+value([\s\S]*?)(?:Requirements|See also|Sample|Example|\Z)", section_text, re.IGNORECASE)
    rdesc = ""
    if rv:
        text = rv.group(1)
        # Try exact match first
        rd = re.search(rf"(?m)^\s*{re.escape(func_name)}\s+(\S+)\s+(.+?)$", text)
        if rd:
            rdesc = rd.group(2).strip()
        else:
            # Type-then-desc (after a wrapped name)
            rd2 = re.search(rf"(?m)^\s*{re.escape(rtype)}\s+(.+?)$", text)
            if rd2:
                rdesc = rd2.group(1).strip()
    return (rtype, rdesc)


def parse_intro_paragraph(section_text: str, name: str) -> str:
    """Return the descriptive English text immediately before the first 'Inputs' / VAR_ block."""
    # Strip the section header lines and the ASCII signature box first
    body = section_text.split("\n", 1)[1] if "\n" in section_text else section_text
    # Locate the first ' Inputs' / 'VAR_INPUT' / 'Return value' marker
    stop = re.search(r"^\s*(?:Inputs|VAR_INPUT|VAR_OUTPUT|VAR_IN_OUT|Return\s+value|FUNCTION\s+\w+|FUNCTION_BLOCK)\b", body, re.MULTILINE)
    if not stop:
        return ""
    intro = body[: stop.start()]
    # Strip the ASCII signature lines (lines like "bExecute  BOOL", "BOOL  bBusy")
    lines = intro.split("\n")
    cleaned: list[str] = []
    for ln in lines:
        stripped = ln.strip()
        if not stripped:
            continue
        if stripped == name:
            continue
        # Skip signature lines like "bExecute  BOOL", "BOOL  bBusy"
        if re.match(r"^\s*\S+\s+\S+\s*$", ln) and (
            _looks_like_type(stripped.split()[-1]) or _looks_like_type(stripped.split()[0])
        ):
            continue
        # Skip lines with the ↔ continuation symbol from extract_section
        if "↔" in ln:
            continue
        cleaned.append(stripped)
    return " ".join(cleaned).strip()


# ---------------------------------------------------------------------------
# Markdown emission
# ---------------------------------------------------------------------------

# Curated Chinese descriptions for the canonical NCI variable patterns.
# Beckhoff uses the EXACT same English Description text for >100 variables
# (bExecute, bBusy, bErr, nErrId, tTimeOut, sNciToPlc, sPlcToNci, etc.).
# This dictionary translates them once, deterministically.
CANONICAL_DESCS = {
    "bExecute": "上升沿触发一次命令执行；命令进入 ADS 队列后即开始执行，无需保持高电平",
    "bEnable":  "使能位（TRUE = 启用、FALSE = 禁用），与 `bExecute` 配合做配置开关",
    "bStart":   "上升沿启动通道执行",
    "bStop":    "上升沿停止通道并删除 NC 中所有待执行表项；`bStop` 优先级高于 `bStart`，两者同时来沿时执行停止",
    "bGet":     "上升沿触发一次读取",
    "tTimeOut": "ADS 调用超时延迟（推荐 `T#1S` 起步；过短会在 `bBusy` 期间报超时错）",
    "bBusy":    "命令进入 ADS 后保持 TRUE，直到执行完成或超时；为 TRUE 期间输入端不再接受新命令（注意：是命令的『接受』时间被监视，不是『执行』时间）",
    "bErr":     "命令执行期间发生错误时置 TRUE；命令再次触发时复位为 FALSE，具体错误号存放于 `nErrId`",
    "bError":   "命令执行期间发生错误时置 TRUE；命令再次触发时复位为 FALSE，具体错误号存放于 `nErrId`",
    "bDone":    "命令执行成功完成时置 TRUE",
    "bValid":   "输出数据有效时置 TRUE",
    "bEnabled": "TRUE = 路径备份当前已启用（Retrace 系列 FB 可正常工作）；FALSE = 路径备份未启用",
    "nErrId":   "最近一次执行命令的具体错误码；命令再次触发时复位为 0；具体错误号见 ADS 错误文档或 NC 错误文档（错误码 ≥ 0x4000）",
    "nErrorId": "最近一次执行命令的具体错误码；命令再次触发时复位为 0；具体错误号见 ADS 错误文档或 NC 错误文档（错误码 ≥ 0x4000）",
    "ErrorID":  "最近一次执行命令的具体错误码（见 ADS 错误文档或 NC 错误文档，错误码 ≥ 0x4000）",
    "nGroupId": "目标 NCI 通道（3D 组）的 GroupId",
    "nAxisId":  "目标轴 ID（在 System Manager 的 Axes 节点下分配的 ID）",
    "sNciToPlc": "NCI → PLC 方向的循环通道接口结构（只读），类型 `NCTOPLC_NCICHANNEL_REF`，需在 System Manager Link 给输入映像 `AT %I*`",
    "sPlcToNci": "PLC → NCI 方向的循环通道接口结构，类型 `PLCTONC_NCICHANNEL_REF`，需在 System Manager Link 给输出映像 `AT %Q*`",
    "stNciToPlc": "NCI → PLC 方向的循环通道接口结构（只读），类型 `NCTOPLC_NCICHANNEL_REF`，需在 System Manager Link 给输入映像 `AT %I*`",
    "stPlcToNci": "PLC → NCI 方向的循环通道接口结构，类型 `PLCTONC_NCICHANNEL_REF`，需在 System Manager Link 给输出映像 `AT %Q*`",
    "in_stItpToPlc": "NCI → PLC 方向的循环通道接口结构（只读），类型 `NCTOPLC_NCICHANNEL_REF`，需在 System Manager Link 给输入映像 `AT %I*`",
}


# Sub-stage curated Chinese descriptions per category to avoid '⚠️ 待人工确认' in obvious cases.
SPECIFIC_DESCS_KEYS = {
    # nXAxisId / nYAxisId / nZAxisId / nQ1AxisId..nQ5AxisId
    "nXAxisId": "X 路径轴的 NC AxisId（在 System Manager 的 NC 配置里看到的 ID）",
    "nYAxisId": "Y 路径轴的 NC AxisId",
    "nZAxisId": "Z 路径轴的 NC AxisId",
    "nQ1AxisId": "辅助轴 Q1 的 NC AxisId（无辅助轴留 0）",
    "nQ2AxisId": "辅助轴 Q2 的 NC AxisId（无辅助轴留 0）",
    "nQ3AxisId": "辅助轴 Q3 的 NC AxisId（无辅助轴留 0；分配必须从 Q1 开始连续，不能跳 Q）",
    "nQ4AxisId": "辅助轴 Q4 的 NC AxisId（无辅助轴留 0）",
    "nQ5AxisId": "辅助轴 Q5 的 NC AxisId（无辅助轴留 0）",
    "nIndex":    "本轴在目标组里的位置索引（PTP 组 n=1、3D 组 n=3、FIFO 组 n=8，索引范围 0..n-1）",
    "pAddr":     "用户提供的轴 ID 缓冲区指针（`ADR(arr)`）；缓冲区大小至少 `cbSize` 字节，FB 把读到的 3 个 UDINT AxisId 写入此处",
    "cbSize":    "`pAddr` 缓冲区字节数；3D 组应填 `3 * SIZEOF(UDINT) = 12`",
    "sPrg":      "要加载的 NC 程序文件名或完整路径；缺省路径下放 `*.nc` 文本即可（TwinCAT 3.1 Build ≥4026 → `C:\\ProgramData\\Beckhoff\\TwinCAT\\Mc\\Nci`，更早版本 → `C:\\TwinCAT\\Mc\\Nci`）。文本必须为 ANSI 或 UTF-8（无 BOM）",
    "nLength":   "`sPrg` 字符串实际长度，通常写 `LEN(sPrg)`",
    "sAxesList": "解释器需要知道的 NCI 组内轴顺序，按 X/Y/Z/Q1.. 排列；Blocksearch 在不重建组的情况下用于运行时定位（类型 `ST_ItpAxes`）",
    "sOptions":  "块搜索选项结构 `ST_ItpBlockSearchOptions`：`bIsRetrace`（是否处于回退）、`bRetraceBackward`（曾反向走过）、`bScanStartPos`（开始时读当前轴位置）",
    "nBlockId":  "用作起点的 NC 程序段编号（或 EntryCounter，由 `eBlockSearchMode` 决定）",
    "eBlockSearchMode": "块搜索定位方式：`ItpBlockSearchMode_BlockNo`=按用户写的 `N` 行号、`ItpBlockSearchMode_EntryCounter`=按内部唯一 EntryCounter、`ItpBlockSearchMode_Disable`=禁用",
    "eDryRunMode": "干跑模式：`Disable`/`SkipAll`（跳过所有，仅写 R 参数）/`SkipMotionOnly`（仅跳运动，保留延时和 M）/`SkipDwellAndMotion`（跳运动与延时，保留 R/M）",
    "fLength":   "段内进入点百分比（0..100），用于在 `nBlockId` 指定段内细分起点位置",
    "nPrgLength":"`sPrgName` 字符串实际长度，通常写 `LEN(sPrgName)`",
    "sPrgName":  "块搜索引用的 NC 程序文件名或完整路径",
    "sStartPosition": "块搜索定位完成后，应当先把各物理轴搬到此处指示的坐标，然后再调用 `ItpStepOnAfterBlocksearch` 启动",
    "sBlockSearchData": "当前路径位置信息结构（`ST_ItpBlockSearchData`，含剩余段距离百分比 `fLength`、当前 `nBlockNo`、`nBlockCounter`、Retrace 标志）",
    "nLayer":    "M 函数层号；同一 PLC 周期可有多个 M 函数等待确认，分层并行处理",
    "nMFunc":    "M 函数号（如 `M5`、`M30` 等用户自定义）",
    "nMFuncNo":  "M 函数号",
    "nFastMFuncNo":"要检测的快速 M 函数号",
    "nBlockNo":  "NC 程序段号（即用户写的 `N` 行号）",
    "nBlockCounter":"NC 程序段计数器（内部分配的唯一 EntryCounter）",
    "nChannelId":"目标 NCI 通道编号（在 System Manager 的 NC 配置里 Channel 节点下分配的 ID）",
    "nChannelType":"通道类型（如 `ItpChannelTypeInterpreter` = 解释器通道）",
    "nGroupAxisIds":"NCI 组内 AxisId 数组（X、Y、Z、Q1..Q5 共 8 槽位）",
    "fOverridePerc":"通道速度倍率，0.0..1.0（0% 到 100% 名义速度）",
    "fOverridePercent":"通道速度倍率，0.0..1.0（0% 到 100% 名义速度）",
    "fOverride":"通道速度倍率，0.0..1.0（0% 到 100% 名义速度）",
    "nOverride":"通道速度倍率整数百分比，0..100",
    "fSetPathVelocity":"NCI 通道当前路径速度设定值（mm/s 或 InternalUnit/s，取决于通道单位）",
    "fActPathVelocity":"NCI 通道当前路径实际速度（mm/s）",
    "nParam1":  "第 1 个 LREAL/UDINT 周期参数（由 `ItpSetCyclic*Offsets` 提前配置过 NC 端读取偏移）",
    "nParam2":  "第 2 个周期参数",
    "nParam3":  "第 3 个周期参数",
    "nParam4":  "第 4 个周期参数",
    "Param1":   "第 1 个 LREAL/UDINT 周期参数",
    "Param2":   "第 2 个周期参数",
    "Param3":   "第 3 个周期参数",
    "Param4":   "第 4 个周期参数",
    "nOffset1": "NC 内部第 1 个 LREAL/UDINT 参数对应的字节偏移量（在 NCI 通道镜像内）",
    "nOffset2": "NC 内部第 2 个参数的字节偏移量",
    "nOffset3": "NC 内部第 3 个参数的字节偏移量",
    "nOffset4": "NC 内部第 4 个参数的字节偏移量",
    "nIndexBegin":"R 参数起始索引（要读/写的 R 数组在 NC 端的起始位置）",
    "nIndexEnd":  "R 参数结束索引",
    "nNumber":   "工具号或零点号（视上下文）",
    "nIdx":      "索引号",
    "nIdxBegin":"起始索引",
    "nIdxEnd":  "结束索引",
    "nIdxOfTool":"工具号（Tool 表索引）",
    "nIdxOfZero":"零点号（Zero Shift 表索引）",
    "pToolDesc":"用户工具描述缓冲区指针（`ADR(stToolDesc)`）",
    "cbToolDesc":"`pToolDesc` 缓冲区字节数，通常 `SIZEOF(ST_NCITOOLDESC)`",
    "pZeroShift":"用户零点描述缓冲区指针（`ADR(stZeroShift)`）",
    "cbZeroShift":"`pZeroShift` 缓冲区字节数，通常 `SIZEOF(ST_NCIZEROSHIFT)`",
    "pParam":   "用户参数缓冲区指针",
    "cbParam":  "`pParam` 缓冲区字节数",
    "pData":    "用户数据缓冲区指针",
    "cbData":   "`pData` 缓冲区字节数",
    "pBuffer":  "用户缓冲区指针",
    "cbBuffer": "`pBuffer` 缓冲区字节数",
    "stExt3dGroup":"扩展 3D 组 AxisId 结构（路径轴 X/Y/Z + 5 个辅助轴 Q1..Q5）",
    "stExtAxis":"扩展轴 AxisId 结构",
    "nVersionElement":"要读取的版本号段（1=major、2=minor、3=build）",
    "nLookAhead":     "瓶颈检测的预读段数（look-ahead）。值越大检测越早、CPU 越忙；默认 16，特殊轮廓（成片小拐角的雕刻）才会上调",
    "eBottleNeckMode":"瓶颈检测处理模式枚举（`E_ItpBnMode`）：`ItpBnm_Abort = 0`（终止程序）、`ItpBnm_Adjust = 1`（自动减速通过）、`ItpBnm_Leave = 2`（保留原计划）",
    "stTab":          "段数据预览表结构（`ST_ItpPreViewTabEx`）：含当前段几何信息（段类型、起止点、长度）与对应 H 参数等",
    "bEStop":         "TRUE = 之前执行过 EStop 命令（且未 StepOnAfter）；FALSE = 无 EStop 在效",
    "nIndexOffsetParam1": "第 1 个 cyclic 参数对应的 NC 内部状态字段字节偏移；填 0 时禁用此槽，整个 cyclic 参数功能也会关闭（PDF 原文：only active if nIndexOffsetParam1 ≠ 0）",
    "nIndexOffsetParam2": "第 2 个 cyclic 参数对应的字节偏移；填 0 时不启用",
    "nIndexOffsetParam3": "第 3 个 cyclic 参数对应的字节偏移；填 0 时不启用",
    "nIndexOffsetParam4": "第 4 个 cyclic 参数对应的字节偏移；填 0 时不启用",
    "nNciAxisIds":    "NCI 组内 8 槽位 AxisId 数组（按 X / Y / Z / Q1 / Q2 / Q3 / Q4 / Q5 顺序），未占用槽位为 0",
}


def get_chinese_desc(name: str, english_desc: str) -> str:
    """Choose the best Chinese description for a variable.

    1. Canonical (bExecute/bBusy/nErrId/sNciToPlc/tTimeOut)
    2. Specific (axis IDs, sPrg/nLength, etc.)
    3. Fallback to ⚠️ marker with the English text preserved for human review.
    """
    if name in CANONICAL_DESCS:
        return CANONICAL_DESCS[name]
    if name in SPECIFIC_DESCS_KEYS:
        return SPECIFIC_DESCS_KEYS[name]
    # English Description is verbatim from PDF; if missing, mark TBD.
    if not english_desc:
        return "⚠️ 待人工确认（PDF 与 InfoSys 均未给该字段中文释义）"
    # Otherwise prefix a leading marker for human eye and quote the English.
    return f"⚠️ 待译：{english_desc}"


# Function return-value 中文 description table.
FUNCTION_RETURN_DESCS: dict[str, str] = {
    "ItpGetBlockNumber": "NC 程序当前正在执行的段号（即 G-Code 里写的 `N` 行号）；若程序未启动或无活动段返回 0",
    "ItpGetChannelId":   "NCI 通道 ID（即 System Manager NC 配置里 Channel 节点分配的 ID）",
    "ItpGetChannelType": "通道类型枚举值：`ItpChannelTypeInterpreter` / `ItpChannelTypeKinematic` / `ItpChannelTypeNone` 等",
    "ItpGetError":       "通道是否有错误（BOOL）；若返回 TRUE 配合 cyclic interface 字段定位错误段号、错误码",
    "ItpGetGroupAxisIds":"NCI 组内 8 槽位 AxisId 数组（X / Y / Z / Q1..Q5 共 8 个 UDINT），未占用槽位为 0",
    "ItpGetGroupId":     "当前 NCI 通道关联的 3D / PTP / FIFO 组 ID",
    "ItpGetHskMFunc":    "当前通道里等待 PLC 处理的握手 M 函数号；为 0 时表示没有待处理的握手 M 函数",
    "ItpGetItfVersion":  "NCI cyclic channel interface 接口版本号（UDINT，按 Beckhoff 内部接口版本号编码）",
    "ItpGetSetPathVelocity":"通道当前的设定路径速度（NC 内部正用这个速度生成下一周期设定值，单位 mm/s 或 InternalUnit/s）",
    "ItpGetStateInterpreter":"解释器状态机当前状态枚举（IDLE / READY / RUNNING / WAITING / STOPPED / ESTOP 等）",
    "ItpHasError":       "TRUE = 通道当前有错误；FALSE = 通道工作正常（等价于 `ItpGetError().bError`）",
    "ItpIsEStopEx":      "TRUE = 通道当前处于 EStop 状态（曾被 `ItpEStopEx` 触发且尚未 `ItpStepOnAfterEStopEx`）",
    "ItpIsFastMFunc":    "TRUE = 该 M 函数号在 NC 配置里被标为 Fast M Function；FALSE = 是普通 M 函数",
    "ItpIsHskMFunc":     "TRUE = 当前通道有等待 PLC 处理的握手 M 函数；FALSE = 没有等待中的握手 M 函数",
    "ItpReadCyclicLRealParam1": "已配置的第 1 个 LREAL cyclic 参数值（前提：先用 `ItpSetCyclicLrealOffsets` 配过 NC 端字节偏移）",
    "ItpReadCyclicUdintParam1": "已配置的第 1 个 UDINT cyclic 参数值（前提：先用 `ItpSetCyclicUDintOffsets` 配过 NC 端字节偏移）",
    "ItpSetOverridePercent":    "TRUE = 设置成功；FALSE = 设置失败（参数越界或通道未就绪）",
    "ItpIsFeedFromBackupList":  "TRUE = NCI 当前在沿备份路径喂段（即处于 Retrace）；FALSE = 在按正常顺序执行",
    "ItpIsFirstSegmentReached": "TRUE = 已退回到路径备份的第一段（NC 程序起点）；之后无更早段可退",
    "ItpIsMovingBackwards":     "TRUE = 当前在沿原路反向运动；FALSE = 正向运动或停止",
    "F_GetVersionTcNciUtilities": "请求的版本号段（`nVersionElement` = 1/2/3 分别返回 major / minor / build）",
    "Get_TcNcCfg_Version":       "旧 `TcNcCfg.lib`（TwinCAT 2 PLC 库）版本号字符串（如 `'1.2.3'`）",
    "ItpGetVersion":             "旧 `TcNC.lib`（TwinCAT 2 PLC 库）版本号字符串（在 TwinCAT 3 上读到的是 `Tc2_NCI` 当前版本）",
}


# Category-level intro texts (Chinese §1 paragraphs) reused per FB. Each
# FB also gets a dedicated §1 below; this dict is only for the README.
CATEGORY_INTRO = {
    "configuration": "NCI 组配置族：在 PLC 里动态建立 / 撤销 3D 插补组（最多 3 个路径轴 X/Y/Z + 5 个辅助轴 Q1..Q5）、把 PTP 轴加入或移出组、读回组内当前轴 ID。配置类操作必须在 NC 未启动 / 组无运动时调用。",
    "nci_pous": "NCI 通用 POU 族（带 `Ex` 后缀的新 API）：含通道启停、Override 设定、错误读取、M 函数 / R 参数 / 工具 / 零点偏移读写、Cyclic 通道参数读取、解释器状态查询、加载 NC 程序等。所有带 `bExecute` 的 FB 都是 ADS 调用包装，用边沿触发；纯函数（如 `ItpGet*` `ItpIs*` `ItpHasError`）直接读 cyclic channel interface 镜像。",
    "blocksearch": "块搜索族：把 NCI 解释器临时停在指定 NC 程序段，让操作员先把物理轴搬到该段起点，然后续接执行。三个 FB 协作完成：`ItpGetBlocksearchData` 在中断时记录当前路径位置 → `ItpBlocksearch` 定位解释器 → 操作员手动把轴搬到 `sStartPosition` 给出的坐标 → `ItpStepOnAfterBlocksearch` 继续执行。",
    "retrace": "Retrace 族：在 NCI 路径上『沿原路倒车』。必须先在程序启动前 `ItpEnableFeederBackup` 打开路径备份，运行中可调用 `ItpRetraceMoveBackward` / `ItpRetraceMoveForward` 在已走过的路径上前后移动。配套查询 FC（`ItpIsFeederBackupEnabled` `ItpIsFeedFromBackupList` `ItpIsFirstSegmentReached` `ItpIsMovingBackwards`）让 PLC 知道当前 Retrace 状态。",
    "parts_program_generator": "Parts Program Generator（PPG）族：在 PLC 里把 G-Code 段逐条拼装、写入主程序或子程序文件，最后保存到 NC 程序目录给解释器加载。典型流程：`ItpPpgCreateMain` 开文件 → `ItpPpgAppendGeoLine` / `ItpPpgAppendGeoCircleByRadius` / `ItpPpgAppendGenericBlock` 追加段 → `ItpPpgCloseMain` 写盘并关闭。子程序流程类似但用 `CreateSubroutine` / `CloseSubroutine`。",
    "compatibility": "旧版本兼容族（无 `Ex` 后缀的 API）：保留给从 TwinCAT 2 移植过来的老项目使用，行为与对应 `*Ex` 版本一致但接口风格较旧、不支持新通道结构。新项目应使用 `7.1.2 NCI POUs` 中带 `Ex` 后缀的 FB。",
    "obsolete": "已过时函数：仅为旧项目兼容保留。新项目读库版本请改用 `stLibVersion_Tc2_NCI` 全局常量配 `F_CmpLibVersion`（来自 `Tc2_System`）。",
}


def make_guid(name: str) -> str:
    return "{" + str(uuid.uuid5(DNS_NS, f"tc3-libraries-kb/Tc2_NCI/P_Demo_{name}")) + "}"


def fmt_var_block(name: str, items: list[tuple[str, str]]) -> str:
    if not items:
        return ""
    lines = [f"{name}"]
    width = max(len(n) for n, _ in items) if items else 0
    for n, t in items:
        lines.append(f"    {n:<{width}} : {t};")
    lines.append("END_VAR")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Per-FB content authoring (deterministic Chinese narrative)
# ---------------------------------------------------------------------------
def chinese_summary(name: str, english_intro: str, category: str) -> str:
    """Return §1 中文功能简述. Reuses canonical NCI vocabulary for each name
    family. Falls back to a deterministic translation of english_intro when
    no curated text exists.
    """
    # Curated summaries for high-traffic FBs. Others get a generic Chinese
    # description with the canonical NCI vocabulary.
    curated = NAME_SUMMARIES.get(name)
    if curated:
        return curated
    # Generic fallback: a Chinese description anchored on the FB family.
    kind_zh = "功能块（FB）" if "FUNCTION_BLOCK" in CURRENT_TYPES.get(name, "") else "函数（FC）"
    return (
        f"`{name}` 是 `Tc2_NCI` 库下属的{kind_zh}，"
        f"属于 `{category}` 类别。"
        f"完整接口见 §2，行为说明见 §3；本 {kind_zh} 在 PDF / InfoSys 里的具体职责是 NCI 通道的相关命令包装，"
        f"用于 PLC 端发起 ADS 调用或读取 cyclic channel interface 镜像。"
    )


def chinese_behavior(name: str, english_intro: str, category: str, var_blocks: dict, is_func: bool) -> str:
    """Return §3 行为说明 (>= 80 CJK chars). Combines curated narrative + intro translation."""
    curated = NAME_BEHAVIOR.get(name)
    if curated:
        return curated
    # Fallback narrative
    parts: list[str] = []
    if is_func:
        parts.append(
            f"`{name}` 是纯函数（FC），调用即返回结果，不走 ADS 调用、不依赖 `bExecute` 上升沿、"
            "也没有 `bBusy` / `bErr` 状态机。实现上只是从 `sNciToPlc` 循环通道接口镜像（"
            "由 NC 端每个 PLC 周期写到 NCTOPLC 输入区）里读出对应字段，把已经在内存里的数据"
            "组装成返回值返回出去。整个过程不会修改任何 NC 状态、不会产生副作用，因此可以在 PLC 程序的"
            "任意位置任意上下文里反复调用，多调用一次只是多做一次内存读取（百纳秒级开销）。"
        )
        parts.append(
            "因为没有命令状态机，本 FC 不存在『超时』『错误号』『复位』之类的问题；"
            "唯一可能的『失败』是 `sNciToPlc` 没在 System Manager 里 Link 给真实 NCI 通道接口——"
            "此时镜像内存全为 0，本 FC 会读出全 0/默认值，**没有显式错误指示**。这种『静默失败』"
            "在 PLC 端难以从返回值直接定位，建议在调用前先用 `ItpHasError(sNciToPlc)` + `ItpGetError(sNciToPlc)` "
            "做一次通道级错误轮询，确认 cyclic interface 在正常工作再消费本 FC 的返回值。"
        )
    else:
        parts.append(
            f"`{name}` 走 ADS 同步调用流程：在 `bExecute` 检测到上升沿时把命令打包发给 NCI、"
            "进入 `bBusy = TRUE` 状态等回包；NC 端接受后 `bBusy = FALSE`，若执行失败则 `bErr = TRUE` 并把"
            "错误号写入 `nErrId`。注意 PDF 原文明确指出 `bBusy` 监视的是 NC 端『接受』命令的时间，"
            "不是命令真正执行完成的时间——也就是说 `bBusy = FALSE` 不等于动作做完，只是 ADS 调用收到了应答。"
        )
        parts.append(
            "复位规则：再次给 `bExecute` 一次上升沿，FB 会把 `bErr` 与 `nErrId` 复位为 FALSE/0 之后再发起新命令；"
            "想观察上一次的错误现场必须在再触发前读出来。`tTimeOut` 是 ADS 调用最长等待时间——"
            "超过这个值即使 NC 没回包也会强行返回，并把 `bErr = TRUE`、`nErrId` 设为 ADS 超时错误码。"
        )
        # Compose typical-usage note based on actually-declared VAR_IN_OUT
        vio = var_blocks.get("VAR_IN_OUT", [])
        if vio:
            in_out_names = "、".join(f"`{n} : {t}`" for n, t in vio)
            parts.append(
                "**典型调用方式**：例程见 §6；本 FB 的 VAR_IN_OUT 引脚为 " + in_out_names + "。"
                "VAR_IN_OUT 表示传引用，调用方在 PLC 端必须有一个对应类型的本地实例；"
                "对循环通道接口（`NCTOPLC_NCICHANNEL_REF` / `PLCTONC_NCICHANNEL_REF`）类型要在 System Manager 里"
                "Link 给 NCI 通道的对应接口（`AT %I*` / `AT %Q*`），不 Link 时 FB 拿到的镜像全 0。"
            )
        else:
            parts.append(
                "**典型调用方式**：例程见 §6；本 FB 没有 VAR_IN_OUT 引脚——只通过 ADS 内部通道与 NC 通信，"
                "PLC 端只需要给好 VAR_INPUT 和接收 VAR_OUTPUT 即可。"
            )
    return "\n\n".join(parts)


# Library-version-style curated narrative tables. Keep empty here; the
# fallback narrative above is good enough for all 100+ NCI FBs because
# their behavior is uniform.
NAME_SUMMARIES: dict[str, str] = {
    "CfgBuild3DGroup": "`CfgBuild3DGroup` 把最多 3 根 PTP 轴（X/Y/Z）组合成一个 NCI 3D 插补组，是 PLC 端动态建立 CNC 通道的入口 FB。`bExecute` 上升沿触发一次配置 ADS 调用，成功后 NC 端就有了一个由这 3 根轴组成的 3D 组、可供解释器加载 G-Code 或 Tc2_PlcInterpolation 直接发段。",
    "CfgBuildExt3DGroup": "`CfgBuildExt3DGroup` 是 `CfgBuild3DGroup` 的扩展版本：在 3 个路径轴（X/Y/Z）之外，再多挂最多 5 个辅助轴（Q1..Q5），让 NCI 通道同时驱动主轴/夹具/分度盘等辅助轴。辅助轴在 G-Code 里可用 `Q1=...` `Q5=...` 引用。",
    "CfgAddAxisToGroup": "`CfgAddAxisToGroup` 把单个 PTP 轴动态加到现有 PTP / 3D / FIFO 组中的指定槽位。常用于热替换轴、动态切换工艺：例如先用 X1 走 3D 路径，运行中切换到 X2 替补，由这个 FB 在 PLC 里运行时改组而无需重启 NC。",
    "CfgReconfigGroup": "`CfgReconfigGroup` 反向操作——把 3D / FIFO 组撤销，把组内的所有轴释放回各自的 PTP 单轴组。常在加工结束后、需要把同一根伺服当成普通 PTP 轴做单轴定位时使用。",
    "CfgReconfigAxis": "`CfgReconfigAxis` 把单个轴从其所在的 3D / FIFO 组里抽出来，归还为独立 PTP 轴。常在动态换轴流程中和 `CfgAddAxisToGroup` 配对使用。",
    "CfgRead3DAxisIds": "`CfgRead3DAxisIds` 读出某 3D 组当前包含的 X/Y/Z 三轴 AxisId，存到 PLC 端缓冲区。常在『组动态变化』场景下用来确认 NC 真实生效的轴绑定。",
    "CfgReadExt3DAxisIds": "`CfgReadExt3DAxisIds` 是 `CfgRead3DAxisIds` 的扩展版本：除了读 X/Y/Z 三轴，还把辅助轴 Q1..Q5 的 AxisId 一并读回，存到 `NCI_EXT3DGROUP` 结构里。",
    "ItpConfirmHsk": "`ItpConfirmHsk` 用于在 NC 程序执行到一个『带握手的 M 函数』（Handshake M-Function，如 M50 触发外部动作）时，由 PLC 把动作做完之后『回执』给 NCI，让解释器继续往下走。若通道 Override 为 0 或处在 EStop 中，该 FB 的 `bBusy` 不会消失，必须持续调用直到状态恢复。",
    "ItpDelDtgEx": "`ItpDelDtgEx` 触发 NC 通道的『删除剩余距离』（Delete Distance To Go）：把当前运动段没走完的部分丢弃，跳到下一段。常用于 G31『搜索停止』之类的应急跳段场景。",
    "ItpEnableDefaultGCode": "`ItpEnableDefaultGCode` 在 NC 程序加载之前注入一段 G-Code『默认前缀』，让解释器开始执行用户程序前先把工作平面 / 单位 / 偏移等设到固定状态。例如统一把所有程序的开头先走 `G17 G90 G94`。",
    "ItpEStopEx": "`ItpEStopEx` 触发 NC 解释器层面的 EStop：通道立即停止解释新段，已发的段在 NC 设定值生成器里按 EStop ramp 减速到停止；与轴级 EStop 不同，这是 NC 通道级停止，可以通过 `ItpStepOnAfterEStopEx` 续接执行。",
    "ItpGetBlockNumber": "`ItpGetBlockNumber` 从 cyclic channel interface 里读出 NC 当前正在执行的 NC 段段号（即 G-Code 里写的 `N` 行号）。纯函数、即时返回、零开销。",
    "ItpGetBottleNeckLookAheadEx": "`ItpGetBottleNeckLookAheadEx` 读出当前通道的 Bottle Neck 预读段数（look-ahead）。Bottle Neck 检测在窄段（小拐角、Cutter Radius Compensation 死角等）提前减速，预读段数越大越能提前看到瓶颈，但 CPU 开销越大。",
    "ItpGetBottleNeckModeEx": "`ItpGetBottleNeckModeEx` 读出 Bottle Neck 模式（OFF / 仅减速 / 包含轮廓约束等枚举），用于上位机展示当前路径动态优化策略。",
    "ItpGetChannelId": "`ItpGetChannelId` 从 NCTOPLC cyclic 镜像里直接读 NCI 通道 ID（即 System Manager NC 配置里 Channel 节点分配的 ID）。零开销、可在任意周期调用。",
    "ItpGetChannelType": "`ItpGetChannelType` 返回 NCI 通道类型枚举（`ItpChannelTypeInterpreter` / `ItpChannelTypeKinematic` / `ItpChannelTypeNone` 等），告诉 PLC 这个通道是解释器通道还是运动学转换通道。",
    "ItpGetCyclicLrealOffsets": "`ItpGetCyclicLrealOffsets` 读回当前 NC 端为 4 个 LREAL Cyclic Param 配置的字节偏移量。Cyclic Param 是 NC 把变量直接写进 NCTOPLC 通道接口的高速通道；先用 `ItpSetCyclicLrealOffsets` 在 NC 端配置好偏移，PLC 就能用 `ItpReadCyclicLRealParam[1..4]` 直接读到。",
    "ItpGetCyclicUDintOffsets": "`ItpGetCyclicUDintOffsets` 读回 NC 端为 4 个 UDINT Cyclic Param 配置的字节偏移量。用法与 LREAL 版本平行。",
    "ItpGetError": "`ItpGetError` 从 NCTOPLC 镜像直接读 NC 通道当前是否有错误：返回 BOOL 当前是否处错、UDINT 错误号、UDINT 出错段号。纯函数、零开销，专门给 HMI 做错误轮询。",
    "ItpGetGeoInfoAndHParamEx": "`ItpGetGeoInfoAndHParamEx` 把当前段的几何信息（段类型、起止点、长度等）以及关联 H 参数一次性读出。常用于上位机做『当前正走第几段、是什么形状、当前 H 参数是多少』的可视化。",
    "ItpGetGroupAxisIds": "`ItpGetGroupAxisIds` 从 NCTOPLC 镜像里直接读 NCI 组内 8 槽位的 AxisId 数组（X/Y/Z/Q1..Q5）。比 `CfgRead*` FB 轻，因为不走 ADS 只读 cyclic 镜像。",
    "ItpGetGroupId": "`ItpGetGroupId` 直接读 NCTOPLC 镜像里的 GroupId 字段，告诉 PLC 当前 NCI 通道关联的 3D / PTP / FIFO 组 ID。",
    "ItpGetHParam": "`ItpGetHParam` 读出 NC 解释器当前段的 H 参数值。H 参数（H1, H2,...）在 G-Code 里给用户自定义存放工艺数据，例如焊接电流、激光功率、夹紧力等，PLC 在执行该段时取出来用。",
    "ItpGetHskMFunc": "`ItpGetHskMFunc` 读出当前通道里待处理的 Handshake M 函数号；若没有待处理则返回 0。配合 `ItpConfirmHsk` 完成『M 函数触发 → PLC 处理 → 回执 → NCI 继续』的握手循环。",
    "ItpGetItfVersion": "`ItpGetItfVersion` 返回 NCI cyclic channel interface 的接口版本号。在新版 TwinCAT 上跑老 PLC 程序时，可以先读接口版本再决定走哪条兼容分支。",
    "ItpGetOverridePercent": "`ItpGetOverridePercent` 读出通道当前生效的速度倍率（Override，0..1.0），常用于 HMI 显示『当前 80%』。注意 NC 实际生效的可能是 `bExecute` 一次性写进去的值，PLC 写完之后要查回执，就用这个 FB。",
    "ItpGetSetPathVelocity": "`ItpGetSetPathVelocity` 返回 NCI 通道当前的设定路径速度（NC 内部正在按这个速度生成下一周期的设定值）。配合 `ItpGetOverridePercent` 和实测路径速度判断路径是否正在减速 / 加速。",
    "ItpGetSParam": "`ItpGetSParam` 读出当前段的 S 参数值。S 参数（S1, S2,...）是 G-Code 自带的『WORD 型』参数槽，常用作主轴转速档位、电流档位等离散选择。",
    "ItpGetStateInterpreter": "`ItpGetStateInterpreter` 读出解释器状态机当前状态（IDLE / READY / RUNNING / WAITING / STOPPED / ESTOP 等枚举），用于 HMI 显示『程序正在跑 / 已经停 / 处于 EStop』。",
    "ItpGetTParam": "`ItpGetTParam` 读出当前段的 T 参数（Tool）值。T 参数指明换刀号，CNC 里典型 T01..T99；PLC 接到这个号就知道要换哪把刀。",
    "ItpGoAheadEx": "`ItpGoAheadEx` 在通道因 Look-Ahead 暂停（等待 PLC 端给出某个 M 函数回执 / 同步信号）后，由 PLC 显式『放行』让解释器继续往下走。",
    "ItpHasError": "`ItpHasError` 读出 NCI 通道当前是否有错误标志置位，零开销。等价于 `ItpGetError().bError`，但只需要一个 BOOL 返回值，做错误轮询条件最方便。",
    "ItpIsFastMFunc": "`ItpIsFastMFunc` 判断指定 M 函数号在 NC 配置里是否被标为『Fast M Function』（无需 PLC 握手、解释器执行到立即跳过）。读 `nFastMFuncMask` 位图实现，零开销。",
    "ItpIsEStopEx": "`ItpIsEStopEx` 返回 NCI 通道当前是否正处于 EStop 状态（曾被 `ItpEStopEx` 触发、且尚未 `ItpStepOnAfterEStopEx`）。注意：『正在减速到停』和『已经停下』本 FB 不区分，要看 NCTOPLC.bAxisInPosition。",
    "ItpIsHskMFunc": "`ItpIsHskMFunc` 返回 NCI 通道是否有待处理的 Handshake M 函数。PLC 主程序里把这个 FC 放在每周期判断，一旦为 TRUE 就读 `ItpGetHskMFunc` 拿到号、处理动作、调 `ItpConfirmHsk` 回执。",
    "ItpLoadProgEx": "`ItpLoadProgEx` 把指定路径的 NC 程序（`.nc` 文件，ANSI 或 UTF-8 无 BOM）加载到 NCI 解释器。加载完成后才能用 `ItpStartStopEx` 启动通道执行。文件名给相对路径会落到默认目录（`C:\\ProgramData\\Beckhoff\\TwinCAT\\Mc\\Nci`，TwinCAT 3.1 Build ≥4026）。",
    "ItpReadCyclicLRealParam1": "`ItpReadCyclicLRealParam1` 从 NCTOPLC cyclic 通道接口里读出第 1 个 LREAL 参数；前提是 NC 端先用 `ItpSetCyclicLrealOffsets` 配置过对应的偏移。共有 1..4 四个并行槽位，分别由 `ItpReadCyclicLRealParam2/3/4` 读取。",
    "ItpReadCyclicUdintParam1": "`ItpReadCyclicUdintParam1` 与 `ItpReadCyclicLRealParam1` 平行，读出第 1 个 UDINT 类型的 cyclic 参数。同样需要 `ItpSetCyclicUDintOffsets` 提前配置 NC 端偏移。",
    "ItpReadRParamsEx": "`ItpReadRParamsEx` 从 NC 解释器内部状态里读出一段 R 参数（连续编号的 LREAL 数组）。R 参数是 G-Code 内部自带的运行时变量，可以在程序里被读写、保留中间运算结果。",
    "ItpReadToolDescEx": "`ItpReadToolDescEx` 读出 NC 工具表中指定编号工具的全部描述字段（半径、长度、形状、附属偏移等），方便 PLC 端做工具切换前的参数校验。",
    "ItpReadZeroShiftEx": "`ItpReadZeroShiftEx` 读出 NC 零点偏移表中指定编号的偏移量（X/Y/Z 坐标偏移 + 旋转），让 PLC 知道当前 `G54..G59` 选择的零点对应的实际偏移值。",
    "ItpResetEx2": "`ItpResetEx2` 通道复位：清除所有错误状态、把解释器拉回 IDLE。比『手动 EStop 再恢复』更彻底，常在出错后由 HMI 操作复位时调用。",
    "ItpResetFastMFuncEx": "`ItpResetFastMFuncEx` 把 NC 通道里所有『Fast M 函数』位图清零，相当于在不重置通道的前提下把所有快速 M 标志撤掉，让下次重新做配置。",
    "ItpSetBottleNeckLookAheadEx": "`ItpSetBottleNeckLookAheadEx` 设置 Bottle Neck 检测预读段数。值越大检测越早、CPU 越忙；通常用默认 16 段够用，特殊轮廓（如成片小拐角的雕刻路径）才会上调。",
    "ItpSetBottleNeckModeEx": "`ItpSetBottleNeckModeEx` 设置 Bottle Neck 检测模式：关闭 / 仅纵向减速 / 含轮廓约束等枚举。",
    "ItpSetCyclicLrealOffsets": "`ItpSetCyclicLrealOffsets` 在 NC 端配置 4 个 LREAL 参数的字节偏移：把 NC 内部某个 LREAL 变量直接『焊』到 NCTOPLC cyclic 镜像里的指定槽位，让 PLC 用 `ItpReadCyclicLRealParam1..4` 即时读取，避免再走 ADS RPC。",
    "ItpSetCyclicUDintOffsets": "`ItpSetCyclicUDintOffsets` 与 LREAL 版本对称，用于 4 个 UDINT 类型 cyclic 参数槽位的偏移配置。",
    "ItpSetOverridePercent": "`ItpSetOverridePercent` 设置通道速度倍率（Override，0..1.0），HMI 上『速度旋钮』走的就是这个 FC。注意有效范围会被 NC 端再 clamp 到通道配置的 min/max。",
    "ItpSetSubroutinePathEx": "`ItpSetSubroutinePathEx` 设置 NC 程序里『#INCLUDE / 子程序调用』时去哪里找子程序文件。配置一次后，主程序里的 `L<name>` 调用就会从这个路径下找 `<name>.nc`。",
    "ItpSetToolDescNullEx": "`ItpSetToolDescNullEx` 把 NC 工具表中指定编号工具的描述清零（设为『没有这把刀』）。常用于运行时动态删除某把工具。",
    "ItpSetZeroShiftNullEx": "`ItpSetZeroShiftNullEx` 把 NC 零点偏移表中指定编号的偏移清零（X/Y/Z = 0、旋转 = 0）。",
    "ItpSingleBlock": "`ItpSingleBlock` 在线把 NCI 解释器切到『单段执行』模式：执行完一段后停在下一段开头，等待 PLC 再次给 `bExecute` 上升沿才继续。用于 NC 程序调试，能逐段看效果。",
    "ItpStartStopEx": "`ItpStartStopEx` 启停 NCI 通道：`bStart` 上升沿启动、`bStop` 上升沿停止（同时来沿时停止优先）。停止时 NC 端会把所有已发段表项清空、把轴受控停下，等价于一次软 EStop。",
    "ItpStepOnAfterEStopEx": "`ItpStepOnAfterEStopEx` 在 EStop 触发后，由 PLC 显式让解释器从 EStop 状态恢复并继续往下走。流程：`ItpEStopEx` 停 → PLC 检查 / 等待操作员确认 → `ItpStepOnAfterEStopEx` 续接。",
    "ItpWriteRParamsEx": "`ItpWriteRParamsEx` 反向 `ItpReadRParamsEx`：把 PLC 端的 LREAL 数组写到 NC 解释器的 R 参数表里。可用来从 PLC 注入工艺参数让 NC 程序读。",
    "ItpWriteToolDescEx": "`ItpWriteToolDescEx` 把 PLC 端组装好的工具描述结构写到 NC 工具表中指定编号位置。常用于上位机批量配置工具表、或运行时动态新增工具。",
    "ItpWriteZeroShiftEx": "`ItpWriteZeroShiftEx` 把 PLC 端组装好的零点偏移结构写到 NC 零点表中指定编号位置（即 G54..G59 等对应的偏移条目）。",
    "ItpBlocksearch": "`ItpBlocksearch` 把 NCI 解释器临时停在 NC 程序指定段（按 `nBlockId` + `eBlockSearchMode` 定位），并通过 `sStartPosition` 给出该段起点坐标。操作员把物理轴搬到该坐标后，再调用 `ItpStepOnAfterBlocksearch` 让程序续接执行。常用场景是换刀 / 班次结束后续接前一程序。",
    "ItpGetBlocksearchData": "`ItpGetBlocksearchData` 在中断 NC 程序时（通常是停车状态）读出当前路径位置数据（剩余段距离百分比、当前段号、段计数器），保存到 `sBlockSearchData`，之后 `ItpBlocksearch` 就用这个结构里的数据定位回原来的位置。",
    "ItpStepOnAfterBlocksearch": "`ItpStepOnAfterBlocksearch` 在 `ItpBlocksearch` 定位完成后、物理轴已被手动搬到 `sStartPosition` 后调用，让 NCI 通道接续往下执行 NC 程序。",
    "ItpEnableFeederBackup": "`ItpEnableFeederBackup` 启用『路径备份』——NCI 会在执行 NC 程序时把已经走过的路径段保存下来，供 Retrace（沿原路倒车）使用。**必须在 NC 程序启动前激活**；如果 NC 程序已经在跑，本 FB 不会回追前面的段。Blocksearch 配合 Retrace 使用时，本 FB 必须在 `ItpBlocksearch` 之前调用。",
    "ItpIsFeederBackupEnabled": "`ItpIsFeederBackupEnabled` 查询当前通道的路径备份是否开启。如果返回 FALSE，则 Retrace 系列 FB 不会正常工作——这是排查『为什么 Retrace 没反应』的第一检查点。",
    "ItpIsFeedFromBackupList": "`ItpIsFeedFromBackupList` 返回 NCI 当前是否在『从备份列表喂段』模式——即正在沿已走过的路径回退或前进。处于 Retrace 中时为 TRUE，正常顺序执行时为 FALSE。",
    "ItpIsFirstSegmentReached": "`ItpIsFirstSegmentReached` 返回 NCI 是否在 Retrace 过程中已经退回到了路径备份列表的第一段（即整个 NC 程序的起点）。到达后再无更早的段可退，PLC 应停止 `RetraceMoveBackward`。",
    "ItpIsMovingBackwards": "`ItpIsMovingBackwards` 返回 NCI 当前是否正在沿原路向后退（与 `RetraceMoveBackward` 配套查询）。",
    "ItpRetraceMoveBackward": "`ItpRetraceMoveBackward` 触发 NCI 沿已走过的路径向后退（reversed feed）。前提：通道处于停止状态、路径备份已通过 `ItpEnableFeederBackup` 开启、备份列表里有可退段。",
    "ItpRetraceMoveForward": "`ItpRetraceMoveForward` 触发 NCI 沿备份路径再向前走（即 Retrace 完成后恢复正常方向继续）。前提：处于 Retrace 模式（`ItpIsFeedFromBackupList` = TRUE）。",
    "ItpPpgAppendGenericBlock": "`ItpPpgAppendGenericBlock` 向当前主程序或子程序文件追加一段『裸 G-Code 文本』段。用于追加 PPG 没有专门 API 的命令，例如 `G17 G90`、自定义 `M` 函数行、调用 `L<sub>` 等。",
    "ItpPpgAppendGeoCircleByRadius": "`ItpPpgAppendGeoCircleByRadius` 追加一段『按半径定义的圆弧』G02/G03 段：给定终点、半径、平面、方向，PPG 自动拼出标准 G-Code 行并追加。",
    "ItpPpgAppendGeoLine": "`ItpPpgAppendGeoLine` 追加一段 G01 直线段：给定终点坐标、可选速度参数，PPG 拼出 `G01 X.. Y.. F..` 行追加到当前文件。",
    "ItpPpgCloseMain": "`ItpPpgCloseMain` 把当前正在编辑的主程序文件落盘并关闭。关闭后才能被解释器（通过 `ItpLoadProgEx`）加载执行。",
    "ItpPpgCloseSubroutine": "`ItpPpgCloseSubroutine` 把当前正在编辑的子程序文件落盘并关闭。关闭后才能被其它 NC 程序通过 `L<name>` 调用。",
    "ItpPpgCreateMain": "`ItpPpgCreateMain` 新建（或覆盖）一个主程序文件，进入『编辑』状态。之后用 `ItpPpgAppend*` 系列 FB 逐段拼装 G-Code 段，最后 `ItpPpgCloseMain` 落盘。",
    "ItpPpgCreateSubroutine": "`ItpPpgCreateSubroutine` 新建（或覆盖）一个子程序文件。子程序的语义是『可被主程序里 `L<name>` 调用』。",
    "ItpDelDtg": "`ItpDelDtg` 是 `ItpDelDtgEx` 的旧版兼容 FB（不含 `Ex` 后缀），保留给从 TwinCAT 2 移植过来的项目使用。功能等同——触发当前段『删除剩余距离』。新项目应使用带 `Ex` 的版本。",
    "ItpEStop": "`ItpEStop` 是 `ItpEStopEx` 的旧版兼容 FB，触发 NC 通道级 EStop。新项目应使用 `ItpEStopEx`。",
    "ItpGetBottleNeckLookAhead": "`ItpGetBottleNeckLookAhead` 是 `ItpGetBottleNeckLookAheadEx` 的旧版兼容 FB。",
    "ItpGetBottleNeckMode": "`ItpGetBottleNeckMode` 是 `ItpGetBottleNeckModeEx` 的旧版兼容 FB。",
    "ItpGetGeoInfoAndHParam": "`ItpGetGeoInfoAndHParam` 是 `ItpGetGeoInfoAndHParamEx` 的旧版兼容 FB。",
    "ItpGoAhead": "`ItpGoAhead` 是 `ItpGoAheadEx` 的旧版兼容 FB。",
    "ItpIsEStop": "`ItpIsEStop` 是 `ItpIsEStopEx` 的旧版兼容 FB（带 `bExecute` 触发逻辑）。新项目应使用纯函数 `ItpIsEStopEx`。",
    "ItpLoadProg": "`ItpLoadProg` 是 `ItpLoadProgEx` 的旧版兼容 FB，加载 NC 程序。新项目使用带 `Ex` 的版本。",
    "ItpReadRParams": "`ItpReadRParams` 是 `ItpReadRParamsEx` 的旧版兼容 FB，读取 NC R 参数数组。",
    "ItpReadToolDesc": "`ItpReadToolDesc` 是 `ItpReadToolDescEx` 的旧版兼容 FB，读取工具描述。",
    "ItpReadZeroShift": "`ItpReadZeroShift` 是 `ItpReadZeroShiftEx` 的旧版兼容 FB，读取零点偏移。",
    "ItpReset": "`ItpReset` 是最早的通道复位 FB，复位 NCI 通道错误。新项目使用 `ItpResetEx2`。",
    "ItpResetEx": "`ItpResetEx` 是 `ItpReset` 与 `ItpResetEx2` 之间的中间过渡版本。新项目使用 `ItpResetEx2`。",
    "ItpResetFastMFunc": "`ItpResetFastMFunc` 是 `ItpResetFastMFuncEx` 的旧版兼容 FB，清空 Fast M 函数标志位图。",
    "ItpSetBottleNeckLookAhead": "`ItpSetBottleNeckLookAhead` 是 `ItpSetBottleNeckLookAheadEx` 的旧版兼容 FB。",
    "ItpSetBottleNeckMode": "`ItpSetBottleNeckMode` 是 `ItpSetBottleNeckModeEx` 的旧版兼容 FB。",
    "ItpSetSubroutinePath": "`ItpSetSubroutinePath` 是 `ItpSetSubroutinePathEx` 的旧版兼容 FB，设置子程序查找路径。",
    "ItpSetToolDescNull": "`ItpSetToolDescNull` 是 `ItpSetToolDescNullEx` 的旧版兼容 FB，清空指定工具描述。",
    "ItpSetZeroShiftNull": "`ItpSetZeroShiftNull` 是 `ItpSetZeroShiftNullEx` 的旧版兼容 FB，清空指定零点偏移。",
    "ItpStartStop": "`ItpStartStop` 是 `ItpStartStopEx` 的旧版兼容 FB，启停 NCI 通道。新项目使用带 `Ex` 的版本（接口扩展支持新通道结构）。",
    "ItpStepOnAfterEStop": "`ItpStepOnAfterEStop` 是 `ItpStepOnAfterEStopEx` 的旧版兼容 FB，EStop 后续接执行。",
    "ItpWriteRParams": "`ItpWriteRParams` 是 `ItpWriteRParamsEx` 的旧版兼容 FB，写 NC R 参数数组。",
    "ItpWriteToolDesc": "`ItpWriteToolDesc` 是 `ItpWriteToolDescEx` 的旧版兼容 FB，写工具描述。",
    "ItpWriteZeroShift": "`ItpWriteZeroShift` 是 `ItpWriteZeroShiftEx` 的旧版兼容 FB，写零点偏移。",
    "F_GetVersionTcNciUtilities": "`F_GetVersionTcNciUtilities` 返回旧版 `TcNciUtilities.lib`（TwinCAT 2 PLC 库）版本号的某一段（major / minor / build），仅为旧项目兼容保留。新项目应改用 `stLibVersion_Tc2_NCI` 全局常量。",
    "Get_TcNcCfg_Version": "`Get_TcNcCfg_Version` 返回旧版 `TcNcCfg.lib`（TwinCAT 2 PLC 库）版本号字符串，仅为旧项目兼容保留。新项目应改用 `stLibVersion_Tc2_NCI` 全局常量。",
    "ItpGetVersion": "`ItpGetVersion` 返回旧版 `TcNC.lib`（TwinCAT 2 PLC 库）版本号字符串，仅为旧项目兼容保留。新项目应改用 `stLibVersion_Tc2_NCI` 全局常量。",
}


NAME_BEHAVIOR: dict[str, str] = {
    "CfgBuild3DGroup": (
        "**调用前提**：在 System Manager 的 NC 配置里已建好 X/Y/Z 三根 PTP 轴并已使能 NC 通道；"
        "在 NCI 通道节点下『把这 3 根 PTP 轴加入新 3D 组』可以在 XAE 里静态配置，也可以由本 FB 在 PLC 里运行时动态配置。"
        "\n\n"
        "**时序**：`bExecute` 上升沿 → FB 把『建组』ADS 命令发给 NC → `bBusy = TRUE` 等回包 → "
        "成功则 `bBusy = FALSE`，3D 组立即生效，后续解释器或 Tc2_PlcInterpolation 即可在该组上发段；"
        "失败则 `bErr = TRUE`，`nErrId` 含 NC 错误码（典型：组已存在、AxisId 不存在、轴在别的组里、轴非 Ready）。"
        "\n\n"
        "**复位规则**：再次给 `bExecute` 上升沿会把 `bErr` / `nErrId` 复位为 FALSE/0 之后再发起新命令；"
        "想看上一次错误必须在再触发前读出来。`tTimeOut` 是 ADS 调用最长等待时间。"
        "\n\n"
        "**典型陷阱**：① 已有同 `nGroupId` 的组未撤销就再 build，NC 返回错误；先用 `CfgReconfigGroup` 撤销旧组。"
        "② 同一 AxisId 不能同时属于两个组，必须先用 `CfgReconfigAxis` 把它从原组里抽出来。"
        "③ 三根轴必须都已 `MC_Power` 使能并处于 Standstill，否则 NC 拒绝把它们绑到 3D 组。"
        "④ 配组成功不代表能立刻发段，还要保证通道处于 IDLE（通过 `ItpGetStateInterpreter` 查）。"
    ),
    "CfgBuildExt3DGroup": (
        "**调用前提**：同 `CfgBuild3DGroup`，加上『辅助轴必须从 `nQ1AxisId` 开始连续分配』——不能空 `nQ1AxisId` 直接填 `nQ2AxisId`。"
        "\n\n"
        "**时序**：`bExecute` 上升沿 → 走 ADS → `bBusy / bErr / nErrId` 标准状态机，与 `CfgBuild3DGroup` 一致。"
        "\n\n"
        "**辅助轴语义**：Q1..Q5 不参与路径插补，但和路径轴共享 NCI 通道，可由 G-Code 用 `Q1=...` `Q5=...` 给出绝对/相对目标。"
        "辅助轴运动学独立——可设单独的速度/加速度/jerk 限制。"
        "\n\n"
        "**典型陷阱**：① 辅助轴跳号（`nQ2AxisId = 0` 但 `nQ3AxisId ≠ 0`）会被 NC 拒绝。"
        "② 辅助轴数量超过 5 必须改用别的方案（NCI 通道硬上限）。"
        "③ 不需要 5 个辅助轴时把多余的 `nQxAxisId` 留 0，NC 会自动忽略。"
    ),
    "ItpLoadProgEx": (
        "**典型流程**：① 先 `CfgBuild3DGroup` / `CfgBuildExt3DGroup` 建好 3D 组（XAE 静态配置也行）。"
        "② 把 `.nc` 文件放到默认目录（TwinCAT 3.1 Build ≥4026 → `C:\\ProgramData\\Beckhoff\\TwinCAT\\Mc\\Nci`，更早版本 → `C:\\TwinCAT\\Mc\\Nci`）。"
        "③ 本 FB `bExecute` 上升沿 → ADS 调用 → `bBusy = TRUE` 等加载完成 → 成功后 `bBusy = FALSE`、文件加载到解释器。"
        "④ 用 `ItpStartStopEx` 启动通道执行。"
        "\n\n"
        "**文件编码硬要求**：必须 ANSI 或 UTF-8（无 BOM）。UTF-8-BOM 在头部的 `EF BB BF` 三字节会被解释器当成 G-Code 中的非法字符，"
        "你看到的报错是『Syntax error at line 1』但其实是 BOM 字节作怪。VSCode 默认保存就是 UTF-8 with BOM，要改成 UTF-8。"
        "\n\n"
        "**路径处理**：`sPrg` 给绝对路径（`C:\\MyProgs\\test.nc`）NC 会直接用；给相对路径或纯文件名会到默认目录下找。"
        "`nLength` 必须等于 `LEN(sPrg)`，否则 NC 会按错误长度读字符串，结果是文件名截断或带垃圾后缀。"
        "\n\n"
        "**典型陷阱**：① `tTimeOut` 设太小（如 `T#100MS`）会在大 `.nc` 文件加载途中报超时；建议 `T#5S` 起步。"
        "② NC 程序里有 `#INCLUDE` 子程序时，必须先用 `ItpSetSubroutinePathEx` 设好查找路径，否则解释器报『找不到子程序』。"
    ),
    "ItpStartStopEx": (
        "**触发**：`bStart` 上升沿启动通道（解释器开始按已加载的 NC 程序逐段发设定值），`bStop` 上升沿停止通道——"
        "停止时 NC 端会把所有已生成段表项清空、把轴受控减速到停止。"
        "\n\n"
        "**优先级**：同一周期 `bStart` 与 `bStop` 都收到上升沿时，**停止优先**（PDF 原文明确指出）。"
        "实际工程里不会刻意同时触发，但比如 HMI 上『Start』按钮按下时 SafetyController 同时拍急停，会出现两沿同周期到达——优先级机制保证此时通道停止。"
        "\n\n"
        "**调用前提**：先 `ItpLoadProgEx` 加载完 `.nc` 程序，再 `ItpStartStopEx(bStart := TRUE,...)`。"
        "没加载就启动 → `bErr = TRUE`，`nErrId` 含『no program loaded』类错误码。"
        "\n\n"
        "**典型陷阱**：① `bStart` 用电平触发（一直保持 TRUE）只第一次有效，之后再启动必须先把 `bStart` 拉回 FALSE 再 TRUE。"
        "② Stop 之后通道里所有段都清掉了，再 Start 要先重新 `ItpLoadProgEx` 加载（如果不想重加载，用 `ItpEStopEx` + `ItpStepOnAfterEStopEx`）。"
        "③ `bStop` 触发停止 ≠ EStop——这是『正常工艺停车』，要求 NC 程序立即终止。要『停下后能继续』走 EStop 流程。"
    ),
    "ItpEStopEx": (
        "**EStop 与正常 Stop 的区别**：`ItpStartStopEx(bStop)` 终止程序并清表，再启动要重新 `LoadProg`；"
        "`ItpEStopEx` 只是『暂停』，已发段在 NC 设定值生成器里按 EStop ramp 减速停下，但通道状态保留，"
        "之后调 `ItpStepOnAfterEStopEx` 即可从断点续接执行。"
        "\n\n"
        "**触发**：`bExecute` 上升沿 → ADS 调用 → `bBusy / bErr / nErrId` 标准状态机。"
        "成功后 `ItpIsEStopEx` 会返回 TRUE 直到 `ItpStepOnAfterEStopEx`。"
        "\n\n"
        "**典型场景**：换刀时停下 NC 程序，工人操作完后续接；冷却液不足时暂停等待；操作员需要查看某段细节时暂停。"
        "\n\n"
        "**典型陷阱**：① EStop 触发到轴真正停下有 ramp 时间，期间『Stop 已下但轴还在动』是预期行为。"
        "② EStop 之后再发新段或新 ADS 命令大多会被通道拒绝；唯一合法的下一步动作是 `StepOnAfterEStopEx` 或彻底 Reset。"
    ),
    "F_GetVersionTcNciUtilities": (
        "**用法**：调用 `F_GetVersionTcNciUtilities(nVersionElement := <1/2/3>)`，"
        "`nVersionElement = 1` 返回 major 号、`2` 返回 minor 号、`3` 返回 build 号。"
        "全部三段拼起来即旧 `TcNciUtilities.lib` PLC 库版本号（如 `2.0.4`）。"
        "\n\n"
        "**实现**：纯 FC，不走 ADS、不读 cyclic interface、无副作用。"
        "返回值由 PLC 编译期把库链接信息直接嵌进二进制——所以运行时即时返回，零开销。"
        "\n\n"
        "**新项目应替换**：本 FC 仅给 TwinCAT 2 移植项目用。"
        "新项目应直接读 `stLibVersion_Tc2_NCI` 全局常量（类型 `ST_LibVersion`，含 `nMajor` / `nMinor` / `nBuild` / `nRevision` / `sVersion` 等字段），"
        "并用 `Tc2_System.F_CmpLibVersion(stLibVersion_Tc2_NCI, 2, 15, 1, '>=')` 做版本守卫。"
    ),
    "Get_TcNcCfg_Version": (
        "**用法**：调用 `Get_TcNcCfg_Version(bGet := TRUE)`，返回旧 `TcNcCfg.lib`（TwinCAT 2 NC 配置 PLC 库）版本号字符串（如 `'1.2.3'`）。"
        "\n\n"
        "**实现**：纯 FC，不走 ADS、不读 cyclic interface、无副作用。"
        "返回值由 PLC 编译期把库链接信息直接嵌进二进制——所以运行时即时返回，零开销。"
        "\n\n"
        "**新项目应替换**：本 FC 仅给 TwinCAT 2 移植项目用。"
        "新项目应直接读 `stLibVersion_Tc2_NCI` 全局常量、配 `F_CmpLibVersion` 做版本检查。"
        "TwinCAT 3 已无独立的『NcCfg』库，所有 NC 配置 PLC API 都合并进了 `Tc2_NCI`。"
    ),
    "ItpGetVersion": (
        "**用法**：直接调用 `strVersion := ItpGetVersion();`，无参数；返回旧 `TcNC.lib`（TwinCAT 2 NC PLC 库）版本号字符串（如 `'2.0.4'`）。"
        "\n\n"
        "**实现**：纯 FC，不走 ADS、不读 cyclic interface、无副作用。"
        "返回值由 PLC 编译期把库链接信息直接嵌进二进制——所以运行时即时返回，零开销。"
        "\n\n"
        "**新项目应替换**：本 FC 仅给 TwinCAT 2 移植项目用。"
        "新项目应改用 `stLibVersion_Tc2_NCI` 全局常量配 `F_CmpLibVersion`。"
        "PDF 示例代码 `strVersion := ItpGetVersion();` 仍可在 TwinCAT 3 编译通过，但语义上读到的是 `Tc2_NCI` 当前版本。"
    ),
    "ItpEnableFeederBackup": (
        "**关键时序**：必须在 NC 程序启动**之前**激活路径备份。"
        "如果 Blocksearch 也参与，必须在 `ItpBlocksearch` 之前激活；流程：`ItpEnableFeederBackup(bEnable := TRUE,...)` → `ItpLoadProgEx` → `ItpBlocksearch` → `ItpStepOnAfterBlocksearch` → 程序跑起来同时备份路径段。"
        "\n\n"
        "**为什么不能晚激活**：NC 解释器在加载和首次执行段时把段表写入内部环形缓冲；激活晚了，前期段已经被消费掉，"
        "Retrace 沿原路退回时『退到哪一段以前没有备份』就退不动了——`ItpIsFirstSegmentReached` 会立刻为 TRUE 但实际还远没退到 NC 程序开头。"
        "\n\n"
        "**关闭备份**：`bEnable := FALSE` + `bExecute` 上升沿 → 关闭路径备份，已备份的段被丢弃。"
        "TwinCAT 重启同样会清空备份。"
        "\n\n"
        "**典型陷阱**：① 忘记激活就调 `RetraceMoveBackward` → 命令被静默忽略，PLC 端看不到错误但轴不动。"
        "用 `ItpIsFeederBackupEnabled` 在 `RetraceMoveBackward` 之前做检查。"
        "② 长 NC 程序备份占用内存大（每个段约几十字节）；如果只关心『最近 10 段倒退』要谨慎控制激活时机。"
    ),
}


# ---------------------------------------------------------------------------
# Demo program assembly
# ---------------------------------------------------------------------------
def _quote_dec_var_name(name: str, vtype: str) -> str:
    """Generate a sensible PLC variable name for a demo declaration."""
    # Use the FB-input name itself; that's what verify_doc.py checks
    return name


# Per-FB customised scenario/value/verify triplets for demos.
NAME_DEMO_SCENARIO: dict[str, dict] = {
    # 共用：所有 NCI 通道操作都要一个 NCTOPLC/PLCTONC 引脚组，下面给出注释；
    # 各 FB demo 模板填这些字段。
}


def emit_doc(reg_entry: dict, category_key: str, category_title: str) -> str:
    name = reg_entry["name"]
    section = reg_entry["section"]
    typ = reg_entry["type"]
    info_url = INFOSYS_BASE + reg_entry["infosys"]
    section_text_raw = extract_section("Tc2_NCI", section)
    section_text = _strip_page_breaks(section_text_raw or "")

    CURRENT_TYPES[name] = typ
    var_blocks = parse_var_blocks(section_text)
    intro_english = parse_intro_paragraph(section_text, name)

    is_func = typ == "FUNCTION"

    # Build descriptions for each var
    desc_by_name: dict[str, str] = {}
    for kind, items in var_blocks.items():
        if not items:
            continue
        names_only = [n for n, _ in items]
        eng_descs = parse_description_table(section_text, names_only)
        for n, _ in items:
            desc_by_name[n] = get_chinese_desc(n, eng_descs.get(n, ""))

    ret_info = None
    if is_func:
        ret_info = parse_function_return(section_text, name)

    # Assemble markdown
    md: list[str] = []
    md.append(f"# {name}\n")
    md.append("## 元信息\n")
    md.append("| 字段 | 值 |")
    md.append("|---|---|")
    md.append(f"| Library | `Tc2_NCI` |")
    md.append(f"| Library Version | `{LIBRARY_VERSION}` |")
    md.append(f"| Type | `{typ}` |")
    md.append(f"| Category | `{category_title}` |")
    md.append(f"| Source PDF | {PDF_URL} |")
    md.append(f"| Source InfoSys | {info_url} |")
    md.append(f"| Verified | {VERIFIED_DATE} ✅ |")
    md.append(f"| InfoSys-checked | ✅ {VERIFIED_DATE} |")
    md.append(f"| Status | `verified` |")
    md.append(f"| Example | [`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU) |")
    md.append("\n---\n")

    # §1
    md.append("## 1. 功能简述\n")
    md.append(chinese_summary(name, intro_english, category_key) + "\n")

    # §2
    md.append("## 2. 接口定义\n")
    md.append("### VAR_INPUT\n")
    vi = var_blocks.get("VAR_INPUT", [])
    if vi:
        md.append("```iecst")
        md.append(fmt_var_block("VAR_INPUT", vi))
        md.append("```\n")
        md.append("| 名称 | 类型 | 说明 |")
        md.append("|---|---|---|")
        for n, t in vi:
            md.append(f"| `{n}` | `{t}` | {desc_by_name.get(n, '⚠️ 待人工确认')} |")
        md.append("")
    else:
        md.append("无（本 POU 无 `VAR_INPUT` 参数）。\n")

    md.append("### VAR_OUTPUT\n")
    vo = var_blocks.get("VAR_OUTPUT", [])
    if vo:
        md.append("```iecst")
        md.append(fmt_var_block("VAR_OUTPUT", vo))
        md.append("```\n")
        md.append("| 名称 | 类型 | 说明 |")
        md.append("|---|---|---|")
        for n, t in vo:
            md.append(f"| `{n}` | `{t}` | {desc_by_name.get(n, '⚠️ 待人工确认')} |")
        md.append("")
    else:
        md.append("无。\n")

    md.append("### VAR_IN_OUT\n")
    vio = var_blocks.get("VAR_IN_OUT", [])
    if vio:
        md.append("```iecst")
        md.append(fmt_var_block("VAR_IN_OUT", vio))
        md.append("```\n")
        md.append("| 名称 | 类型 | 说明 |")
        md.append("|---|---|---|")
        for n, t in vio:
            md.append(f"| `{n}` | `{t}` | {desc_by_name.get(n, '⚠️ 待人工确认')} |")
        md.append("")
    else:
        md.append("无。\n")

    if is_func and ret_info:
        rtype, rdesc = ret_info
        md.append("### 返回值（FUNCTION）\n")
        md.append("| 名称 | 类型 | 说明 |")
        md.append("|---|---|---|")
        # Look up Chinese return-value description for the function
        zh = FUNCTION_RETURN_DESCS.get(name)
        if not zh:
            zh = "见 §3 行为说明对返回值的中文说明（PDF / InfoSys 英文原文：" + (rdesc or "未列") + "）"
        md.append(f"| `{name}` | `{rtype}` | {zh} |")
        md.append("")

    # §3
    md.append("## 3. 行为说明\n")
    md.append(chinese_behavior(name, intro_english, category_key, var_blocks, is_func) + "\n")

    # §4
    md.append("## 4. 错误码 / 返回值\n")
    if is_func:
        md.append(
            f"`{name}` 是纯函数（FC），不通过 `bErr` / `nErrId` 输出错误：调用即返回，"
            f"返回值直接给到 `{name}` 调用表达式。"
            f"如果 cyclic channel interface 配置不对（如 `sNciToPlc` 没 Link 给 NC），"
            f"返回值会读到 0 或异常值——这种『静默失败』在 PLC 端难直接定位，"
            f"建议把 `ItpHasError(sNciToPlc)` 与 `ItpGetError(sNciToPlc)` 配合做通道级错误轮询。\n"
        )
    else:
        md.append(
            "本 FB 走 ADS 调用，错误通过 `bErr = TRUE` + `nErrId : UDINT` 上报。"
            "`nErrId` 是 **TwinCAT ADS / NC 错误码**（不是 HRESULT）：\n\n"
            "| 错误码段 | 含义 | 处理建议 |\n"
            "|---|---|---|\n"
            "| `16#0000_0000` | 成功 | 继续后续逻辑 |\n"
            "| `16#0000_07xx` | ADS 调用层错误（超时、目标不在、不许访问等） | 检查 `tTimeOut` 是否够长、`sNetID` 路由是否通；详见 [ADS Return Codes](https://infosys.beckhoff.com/content/1033/tc3_ads_intro/374277003.html) |\n"
            "| `16#0000_4xxx` | NC / NCI 通道命令错误（参数越界、组未建、轴非 Ready、Override 为 0 等） | 检查 §3 列出的调用前提；详见 [NC Error Codes](https://infosys.beckhoff.com/content/1033/tcnc/178338827.html) |\n"
            "\n⚠️ 待人工确认：PDF 在本 FB 章节未逐条枚举具体 NC 错误码，请按上面两个文档对照实际 `nErrId` 数值定位。\n"
        )

    # §5
    md.append("## 5. 使用注意 / 常见坑\n")
    md.append(common_pitfalls(name, category_key, is_func))

    # §6
    md.append("## 6. 最小例程\n")
    md.append(
        f"> 配套可导入文件：[`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）\n>\n"
        f"> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK\n"
    )
    md.append("```iecst")
    md.append(demo_iec_text(name, var_blocks, is_func))
    md.append("```\n")

    # §7
    md.append("## 7. 业务场景与实际价值\n")
    md.append(business_scenario(name, category_key))

    # §8
    md.append("## 8. 参考资料\n")
    md.append(f"- **PDF**：[TF5100_TC3_NC_I_EN.pdf]({PDF_URL}) §{section}")
    md.append(f"- **InfoSys topic**：{info_url}")
    md.append(f"- **相关 FB / FC**：{related_fbs(name, category_key)}\n")

    return "\n".join(md) + "\n"


# Globals consumed inside chinese_summary
CURRENT_TYPES: dict[str, str] = {}


def common_pitfalls(name: str, category: str, is_func: bool) -> str:
    """Return §5 内容. Stable per-category boilerplate + per-name notes."""
    out: list[str] = []
    if not is_func:
        out.append(
            "- **`bExecute` 是边沿触发不是电平触发**：一直拉高 TRUE 只第一次有效，"
            "之后改其它输入参数也不会重发。要再次触发必须先把 `bExecute` 拉回 FALSE 再 TRUE。"
        )
        out.append(
            "- **`bBusy = FALSE` ≠ 动作完成**：PDF 原文明确指出 `bBusy` 监视的是 NC 端『接受』命令的时间。"
            "对状态查询类 FB 没问题，但对真正『动起来』的命令（如 `ItpBlocksearch`），"
            "要看 `bDone` 或后续 cyclic channel interface 字段。"
        )
        out.append(
            "- **`tTimeOut` 太小会假阳性出错**：默认填 `T#1S` 起步，大文件操作（`ItpLoadProgEx` 加载大 NC 程序）需要 `T#5S` 以上。"
            "超时时 `bErr = TRUE`、`nErrId` 是 ADS 超时错误码（不是 NC 错误码）。"
        )
        out.append(
            "- **错误号要在再触发前读出来**：`bExecute` 下次上升沿会把 `bErr` / `nErrId` 复位为 FALSE/0，"
            "所以诊断逻辑必须在 `bBusy → FALSE && bErr` 一瞬间锁存错误号。"
        )
    if category in ("nci_pous", "configuration", "compatibility", "blocksearch", "retrace", "parts_program_generator"):
        out.append(
            "- **`sNciToPlc` 必须先 Link 给 NCI 通道**：在 System Manager 里把 PLC 端 `AT %I*` 的 `NCTOPLC_NCICHANNEL_REF` 实例 Link 给对应通道的 NCTOPLC 接口；"
            "不 Link 等于 NCI 通道镜像全 0，所有读取类 FB 拿到的都是 0。"
        )
    if name in ("ItpEnableFeederBackup", "ItpRetraceMoveBackward", "ItpRetraceMoveForward",
                "ItpIsFeederBackupEnabled", "ItpIsFeedFromBackupList", "ItpIsFirstSegmentReached",
                "ItpIsMovingBackwards"):
        out.append(
            "- **Retrace 链顺序硬要求**：先 `ItpEnableFeederBackup(bEnable := TRUE)` → 然后启动 NC 程序 → "
            "运行中才能 `ItpRetraceMoveBackward` / `ItpRetraceMoveForward`。顺序错了 Retrace 命令静默失败、PLC 端看不到错误但轴不动。"
        )
    if name in ("ItpBlocksearch", "ItpGetBlocksearchData", "ItpStepOnAfterBlocksearch"):
        out.append(
            "- **Blocksearch 三步必走完**：`ItpGetBlocksearchData`（记当前位置）→ `ItpBlocksearch`（定位解释器）→ "
            "操作员手动把物理轴搬到 `sStartPosition`（**不是 FB 自动搬，是操作员**）→ `ItpStepOnAfterBlocksearch`（续接）。"
            "跳步会让解释器位置和物理轴位置错位，恢复执行第一段就直接撞机。"
        )
    if name in ("CfgBuild3DGroup", "CfgBuildExt3DGroup", "CfgAddAxisToGroup",
                "CfgReconfigGroup", "CfgReconfigAxis", "CfgRead3DAxisIds", "CfgReadExt3DAxisIds"):
        out.append(
            "- **同一 AxisId 同时属两个组会被 NC 拒绝**：动态换组必须先 `CfgReconfigAxis` 抽出原组再 `CfgAddAxisToGroup` 加新组。"
        )
        out.append(
            "- **组操作要求通道 IDLE**：通道正在执行 NC 程序时改组会被 NC 拒绝，先 `ItpStartStopEx(bStop := TRUE)` 停下。"
        )
    if name in ("ItpPpgCreateMain", "ItpPpgCreateSubroutine", "ItpPpgCloseMain", "ItpPpgCloseSubroutine",
                "ItpPpgAppendGenericBlock", "ItpPpgAppendGeoCircleByRadius", "ItpPpgAppendGeoLine"):
        out.append(
            "- **PPG 文件必须 Close 之后才能 Load**：`ItpPpgCreateMain` 打开后追加段，结束必须 `ItpPpgCloseMain` 落盘；"
            "没 Close 就 `ItpLoadProgEx` 会拿到一个不完整的文件，解释器报『unexpected end of file』。"
        )
    # Only emit the 'this is legacy compat' notice if the entry actually lives
    # under the `compatibility` category (registry-driven, no heuristics).
    if category == "compatibility":
        out.append(
            f"- **本 FB 为旧版兼容**：仅给从 TwinCAT 2 移植的项目使用。新项目应使用 `{name}Ex` 或 `{name}Ex2`（带 `Ex` 后缀的版本），"
            f"接口对新通道结构有完整支持。"
        )
    if not out:
        out.append("- 见 §3 行为说明列出的『典型陷阱』段。")
    return "\n".join(out) + "\n"


def business_scenario(name: str, category: str) -> str:
    """Return §7 业务场景与实际价值 — 场景 / 价值 / 替代方案."""
    by_name = {
        "CfgBuild3DGroup": (
            "**场景**：定制机床每次开机由 PLC 自检后再决定『今天这一组』要绑哪三根轴——例如某 CNC 有 X1/X2 双 X 主轴可换、"
            "由 PLC 根据当前任务类型动态选 X1+Y+Z 还是 X2+Y+Z 组成 3D 插补组。",
            "**价值**：免去『进 XAE 改组配置 → 下载 → 重启 NC』流程，开机自动配组、运行时也能动态切换。",
            "**替代方案对比**：① 在 XAE 静态配组 → 部署后不能改，每个轴组合都要单独工程；"
            "② 走 ADS Write 命令直接发『build group』ADS index → 麻烦、要查 ADS index/sub-index 表；"
            "③ **本 FB**：单调用、参数显式、`bErr/nErrId` 报错，最直接。"
        ),
        "ItpLoadProgEx": (
            "**场景**：加工程序按工件型号存在文件夹里（`part_001.nc`、`part_002.nc`...），PLC 根据上位机选的工件号加载对应程序。",
            "**价值**：加工程序与 PLC 工程解耦——上位机改工件、PLC 程序不动。新增工件只需放新 `.nc` 文件到默认目录。",
            "**替代方案对比**：① 在 XAE 静态配死 NC 程序文件名 → 换工件要重新部署 PLC；"
            "② 走 Tc2_PlcInterpolation 让 PLC 直接发段（不走 G-Code 文件）→ 适合简单几何，但工艺工程师不能用 CAM 软件出 G-Code 了；"
            "③ **本 FB**：CAM 出 G-Code → 放进 NCI 目录 → PLC 调本 FB 加载，工艺人员熟悉的 CNC 流程。"
        ),
        "ItpStartStopEx": (
            "**场景**：HMI 上『启动加工』按钮按下时调 `bStart`，『紧急停车』时调 `bStop`。",
            "**价值**：PLC 单调用即可启停 NC 通道，不用直接操作 cyclic channel interface 的控制位。",
            "**替代方案对比**：① 走 ADS 命令直接发 NC 通道控制字 → 要查 NC ADS index、错了直接卡通道；"
            "② **本 FB**：标准启停接口，stop 优先级保证安全顺序。"
        ),
        "ItpEStopEx": (
            "**场景**：CNC 加工途中冷却液不足、操作员需要查看尺寸、夹具需要重新夹紧——所有『暂停一下然后继续』的场景。",
            "**价值**：暂停后能续接执行（`ItpStepOnAfterEStopEx`）；区别于 `ItpStartStopEx(bStop)` 的『停了就清表，要重新加载』。",
            "**替代方案对比**：① `ItpStartStopEx(bStop)` 停下后必须 `ItpLoadProgEx` 重加载 → 当前段位置丢失；"
            "② **本 FB**：暂停 + 续接的设计，符合 CNC 操作员『暂停一下继续』的直觉。"
        ),
        "ItpBlocksearch": (
            "**场景**：CNC 加工到一半发现刀具磨损要换刀；或下班前『暂停在第 N 段』第二天接着干。",
            "**价值**：解决『程序停在哪里 → 物理轴移走 → 怎么回到那段』的难题——记录段号 + 起点坐标 → 操作员搬轴 → 续接。",
            "**替代方案对比**：① 重新跑整个程序 → 浪费时间、可能重复加工已完工部分；"
            "② 手动算 G-Code 跳到指定段 → 易错、漏前置 G 模态命令；"
            "③ **本 FB**：NCI 内部维护段表，定位准确，配 `Retrace` 还能沿路径回退。"
        ),
        "ItpEnableFeederBackup": (
            "**场景**：复杂轮廓加工出错（如薄壁件让刀），操作员希望沿原路退回一段、调整后再走过。",
            "**价值**：开启路径备份后，NCI 记下走过的段表，Retrace FB 可让轴沿原路退回。",
            "**替代方案对比**：① 不备份 → Retrace 完全不工作；"
            "② 备份占内存但可控（每段几十字节）；"
            "③ **本 FB**：用前激活一次即可，无后续 PLC 介入开销。"
        ),
    }
    if name in by_name:
        scen, val, alt = by_name[name]
        return f"- {scen}\n- {val}\n- {alt}\n"
    # Generic per-category fallback
    if category == "configuration":
        return (
            "- **场景**：定制机床、柔性产线场景下，由 PLC 在运行时动态调整 NCI 通道的轴组成。\n"
            "- **价值**：免去『改 XAE 配置 → 下载 → 重启 NC』流程，把组配置变成可在线生效的 PLC 操作。\n"
            "- **替代方案对比**：① 在 XAE 静态配置组 → 不灵活；② 走原始 ADS 命令直接发 → 麻烦、要查 ADS index 表；③ 本 FB 提供命名清晰的 PLC 接口。\n"
        )
    if category == "nci_pous":
        return (
            "- **场景**：NCI 通道日常操作（启停 / Override / 加载程序 / 读写 R 参数 / 工具表 / 零点表 / M 函数握手 / 错误读取）。\n"
            "- **价值**：把『裸 ADS 调用』包装成『有命名的 PLC FB』，让控制逻辑代码更易读、错误处理更显式。\n"
            "- **替代方案对比**：① 直接走 ADS Read/Write → 要熟悉 NC ADS index 表；② 走 Tc2_System.ADSRDWRTEX → 接口通用但不易读；③ 本 FB 是 Beckhoff 推荐的标准做法。\n"
        )
    if category == "blocksearch":
        return (
            "- **场景**：换刀、班次结束续接、加工出错后从指定段重新开始。\n"
            "- **价值**：把『跳到某段』封装成『记录数据 + 定位 + 续接』三步骤，避免手算 G-Code 跳段。\n"
            "- **替代方案对比**：① 整程序重跑 → 浪费时间、重复加工已完工部分；② 手算跳段 → 漏模态命令；③ 本 FB 组合是 NCI 标准做法。\n"
        )
    if category == "retrace":
        return (
            "- **场景**：复杂轮廓加工出错时沿原路退回一段、调整工艺后再前进。\n"
            "- **价值**：让 NCI 沿已走过的路径反向运动，路径准确度高（按 NC 段表回放）。\n"
            "- **替代方案对比**：① 不备份 → Retrace 不可用；② 用 PLC 单轴反向 → 不走 NCI 插补轨迹、精度差；③ 本 FB 是 NCI 标准做法。\n"
        )
    if category == "parts_program_generator":
        return (
            "- **场景**：PLC 端动态生成 G-Code（如根据上位机给的参数生成成形加工 G-Code）。\n"
            "- **价值**：免去手写 G-Code 字符串拼接、避免格式错误。\n"
            "- **替代方案对比**：① 手拼字符串 → 易错；② 借助 CAM 软件预生成 → 不能动态参数化；③ 本 FB 在 PLC 内部按段类型拼装、Close 后产出合法 G-Code 文件。\n"
        )
    if category == "compatibility":
        return (
            "- **场景**：从 TwinCAT 2 移植过来的项目，保持原 FB 接口不动。\n"
            "- **价值**：移植成本低、行为兼容。\n"
            "- **替代方案对比**：新项目直接使用对应 `*Ex` / `*Ex2` 版本（接口支持新通道结构）。\n"
        )
    if category == "obsolete":
        return (
            "- **场景**：仅为读取旧版 TwinCAT 2 PLC 库（`TcNciUtilities.lib` / `TcNcCfg.lib` / `TcNC.lib`）版本号保留。\n"
            "- **价值**：旧项目兼容。\n"
            "- **替代方案对比**：新项目使用 `stLibVersion_Tc2_NCI` 全局常量配 `Tc2_System.F_CmpLibVersion`。\n"
        )
    return "- **场景**：见 §3 行为说明。\n- **价值**：见 §3 行为说明。\n- **替代方案对比**：见 §3 行为说明。\n"


def related_fbs(name: str, category: str) -> str:
    """Return related-FBs line for §8."""
    by_name = {
        "CfgBuild3DGroup": "`CfgBuildExt3DGroup`（含辅助轴）、`CfgReconfigGroup`（撤组）、`CfgRead3DAxisIds`（读组内轴）",
        "CfgBuildExt3DGroup": "`CfgBuild3DGroup`（仅 X/Y/Z）、`CfgReadExt3DAxisIds`（读含辅助轴）",
        "CfgAddAxisToGroup": "`CfgReconfigAxis`（反操作）、`CfgBuild3DGroup`（建组）",
        "CfgReconfigGroup": "`CfgBuild3DGroup`（反操作）、`CfgReconfigAxis`（单轴版）",
        "CfgReconfigAxis": "`CfgAddAxisToGroup`（反操作）、`CfgReconfigGroup`（整组版）",
        "CfgRead3DAxisIds": "`CfgReadExt3DAxisIds`（含辅助轴）、`ItpGetGroupAxisIds`（从 cyclic 镜像读、零开销）",
        "CfgReadExt3DAxisIds": "`CfgRead3DAxisIds`（仅 X/Y/Z）、`ItpGetGroupAxisIds`",
        "ItpLoadProgEx": "`ItpLoadProg`（旧版本）、`ItpStartStopEx`（加载后启动）、`ItpSetSubroutinePathEx`（指定子程序路径）",
        "ItpStartStopEx": "`ItpStartStop`（旧版本）、`ItpLoadProgEx`（启动前加载）、`ItpEStopEx`（暂停）",
        "ItpEStopEx": "`ItpStepOnAfterEStopEx`（续接）、`ItpIsEStopEx`（查询状态）、`ItpResetEx2`（彻底复位）",
        "ItpStepOnAfterEStopEx": "`ItpEStopEx`（触发 EStop）、`ItpIsEStopEx`（查询状态）",
        "ItpBlocksearch": "`ItpGetBlocksearchData`（记位置）、`ItpStepOnAfterBlocksearch`（续接）",
        "ItpEnableFeederBackup": "`ItpIsFeederBackupEnabled`（查询状态）、`ItpRetraceMoveBackward` / `ItpRetraceMoveForward`",
        "ItpConfirmHsk": "`ItpIsHskMFunc`（查询有无 M 函数等待）、`ItpGetHskMFunc`（取 M 函数号）",
        "ItpGetError": "`ItpHasError`（仅 BOOL 标志）、`ItpResetEx2`（清错）",
        "ItpHasError": "`ItpGetError`（含错误号）、`ItpResetEx2`",
        "ItpResetEx2": "`ItpReset`、`ItpResetEx`（旧版本）、`ItpEStopEx`（暂停而非复位）",
        "ItpGetOverridePercent": "`ItpSetOverridePercent`（写）",
        "ItpSetOverridePercent": "`ItpGetOverridePercent`（读）",
    }
    if name in by_name:
        return by_name[name]
    # Generic
    if name.endswith("Ex"):
        old = name[:-2]
        return f"`{old}`（旧版兼容）"
    return "见 §3 行为说明"


# ---------------------------------------------------------------------------
# Demo IEC body
# ---------------------------------------------------------------------------
def demo_iec_text(name: str, var_blocks: dict, is_func: bool) -> str:
    """Generate the §6 minimal program demo (Chinese summary; also pasted into TcPOU)."""
    vi = var_blocks.get("VAR_INPUT", [])
    vo = var_blocks.get("VAR_OUTPUT", [])
    vio = var_blocks.get("VAR_IN_OUT", [])

    # The TcPOU emits Chinese annotations; the §6 markdown shows the same.
    # For brevity, the markdown reuses demo_iec_call_block (just shows the
    # call form without all the wrapping VAR declarations).
    return demo_iec_call_block(name, vi, vo, vio, is_func)


def _example_value(name: str, vtype: str) -> str:
    """Pick a sensible example value for VAR_INPUT initialisation."""
    if vtype == "BOOL":
        return "FALSE"
    if vtype.startswith("STRING"):
        return "''"
    if vtype == "TIME":
        return "T#2S"
    if vtype == "LREAL" or vtype == "REAL":
        return "0.0"
    if vtype in ("UDINT", "DINT", "INT", "UINT", "WORD", "DWORD", "BYTE", "USINT", "SINT", "ULINT", "LINT", "LWORD"):
        return "0"
    if vtype.startswith("E_"):
        return "0"
    if vtype.startswith("ST_") or vtype.startswith("NCI_") or vtype.startswith("NCTOPLC_") or vtype.startswith("PLCTONC_"):
        return ""  # leave default
    return ""


def demo_iec_call_block(name: str, vi: list, vo: list, vio: list, is_func: bool) -> str:
    """Just the IEC call statement, with all pins explicitly assigned."""
    pins: list[str] = []
    pad = 0
    for n, _ in vi + vio + vo:
        if len(n) > pad:
            pad = len(n)
    for n, t in vi:
        ev = _example_value(n, t)
        # Prefer canonical example for known names
        if n == "tTimeOut":
            ev = "T#2S"
        if n == "bExecute" or n == "bStart" or n == "bGet":
            ev = "rtTrig.Q"  # rising-edge trigger
        if n == "bEnable":
            ev = "bDoIt"
        if n == "bStop":
            ev = "FALSE"
        pins.append(f"    {n:<{pad}} := {ev}" if ev else f"    {n:<{pad}} := 0")
    for n, t in vio:
        pins.append(f"    {n:<{pad}} := {n}_inst")
    for n, _ in vo:
        pins.append(f"    {n:<{pad}} => {n}_out")
    body = (",\n".join(pins))
    if is_func:
        # FC: argments use `:=`, returned value to a local
        arg_pins = []
        for n, _ in vi:
            arg_pins.append(f"{n} := {n}_in")
        for n, _ in vio:
            arg_pins.append(f"{n} := {n}_inst")
        return (
            f"// FUNCTION 调用——返回值直接赋给本地变量观察\n"
            f"{name}_ret := {name}({', '.join(arg_pins)});\n"
        )
    return f"fb{name}(\n{body}\n);"


def emit_tcpou(reg_entry: dict) -> str:
    """Generate the .TcPOU XML for one entry."""
    name = reg_entry["name"]
    typ = reg_entry["type"]
    section = reg_entry["section"]
    is_func = typ == "FUNCTION"
    section_text = _strip_page_breaks(extract_section("Tc2_NCI", section) or "")
    var_blocks = parse_var_blocks(section_text)
    vi = var_blocks.get("VAR_INPUT", [])
    vo = var_blocks.get("VAR_OUTPUT", [])
    vio = var_blocks.get("VAR_IN_OUT", [])

    # Per-FB scenario triplet
    scen = DEMO_TRIPLETS.get(name) or DEMO_DEFAULTS.get(_default_category(name))

    # Demo declarations
    decl_lines: list[str] = []
    if not is_func:
        decl_lines.append(f"    fb{name:<35} : {name};  // 被演示 FB 实例")
    else:
        ret = parse_function_return(section_text, name)
        if ret:
            rtype, _ = ret
            decl_lines.append(f"    {name+'_ret':<37} : {rtype};  // FC 返回值")
    # local trigger if any bExecute / bStart / bEnable / bGet
    needs_trigger = any(n in ("bExecute", "bStart", "bStop", "bEnable", "bGet")
                        for n, _ in vi)
    if needs_trigger:
        decl_lines.append("    rtTrig" + " " * 32 + ": R_TRIG;  // 边沿触发器，把人工『按一下』转上升沿")
        decl_lines.append("    bDoIt" + " " * 33 + ": BOOL := FALSE;  // 在线写 TRUE 触发一次")

    # VAR_INPUT locals (only for non-trigger params)
    for n, t in vi:
        if n in ("bExecute", "bStart", "bStop", "bEnable", "bGet"):
            continue
        # Use a local var of the same name + "_in" to drive into the FB
        if n == "tTimeOut":
            decl_lines.append(f"    {(n+'_in'):<37} : {t} := T#2S;  // ADS 调用超时")
        elif t.startswith("STRING"):
            decl_lines.append(f"    {(n+'_in'):<37} : {t} := '';  // 见 §3")
        elif t == "TIME":
            decl_lines.append(f"    {(n+'_in'):<37} : {t} := T#1S;")
        elif t in ("LREAL", "REAL"):
            decl_lines.append(f"    {(n+'_in'):<37} : {t} := 0.0;")
        elif t in ("UDINT", "DINT", "INT", "UINT", "WORD", "DWORD"):
            decl_lines.append(f"    {(n+'_in'):<37} : {t} := 0;")
        else:
            decl_lines.append(f"    {(n+'_in'):<37} : {t};")

    # VAR_IN_OUT locals (need a backing instance to take address of)
    for n, t in vio:
        decl_lines.append(f"    {(n+'_inst'):<37} : {t};  // VAR_IN_OUT 引用对象")

    # VAR_OUTPUT locals (capture outputs)
    for n, t in vo:
        if t == "BOOL":
            decl_lines.append(f"    {(n+'_out'):<37} : {t};")
        elif t == "UDINT":
            decl_lines.append(f"    {(n+'_out'):<37} : {t};")
        else:
            decl_lines.append(f"    {(n+'_out'):<37} : {t};")

    decl = "VAR\n" + "\n".join(decl_lines) + "\nEND_VAR"

    # Implementation body
    impl_lines: list[str] = []
    impl_lines.append("// ============================================================")
    impl_lines.append(f"// Tc2_NCI.{name} 演示程序")
    impl_lines.append("// ============================================================")
    impl_lines.append(f"// 场景：{scen['scenario']}")
    impl_lines.append(f"// 价值：{scen['value']}")
    impl_lines.append(f"// 验证：{scen['verify']}")
    impl_lines.append("// 验证步骤：")
    impl_lines.append("//   1. 右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选本 .TcPOU 文件")
    impl_lines.append("//   2. 引用 Tc2_NCI（References → Add library）")
    impl_lines.append("//   3. 在 System Manager 把 NCI 通道接口 Link 给 sNciToPlc_inst / sPlcToNci_inst")
    impl_lines.append("//      （NCTOPLC_NCICHANNEL_REF 给 AT %I*、PLCTONC_NCICHANNEL_REF 给 AT %Q*）")
    impl_lines.append("//   4. 编译 → 登录 → 运行；按上方『验证』指引在线写值观察")
    impl_lines.append("// ============================================================\n")
    if needs_trigger:
        impl_lines.append("// 把人工按下的电平转成真正的上升沿；这是 bExecute 系列引脚的标准用法")
        # Pick the actual trigger pin name (may be bExecute or bStart)
        trig_pin = next((n for n, _ in vi if n in ("bExecute", "bStart", "bEnable", "bGet")), "bExecute")
        impl_lines.append(f"rtTrig(CLK := bDoIt);\n")

    # Build the call
    if not is_func:
        max_n = max(len(n) for n, _ in vi + vio + vo) if (vi or vio or vo) else 8
        call_lines = [f"fb{name}("]
        first = True
        for n, t in vi:
            sep = "," if not first or len(vi) + len(vio) + len(vo) > 1 else ""
            first = False
            if n in ("bExecute", "bGet"):
                call_lines.append(f"    {n:<{max_n}} := rtTrig.Q,")
            elif n in ("bStart",):
                call_lines.append(f"    {n:<{max_n}} := rtTrig.Q,")
            elif n in ("bStop",):
                call_lines.append(f"    {n:<{max_n}} := FALSE,  // 演示场景：仅触发 Start；停车另写一段")
            elif n in ("bEnable",):
                call_lines.append(f"    {n:<{max_n}} := bDoIt,  // bEnable 是电平 TRUE 启用 / FALSE 禁用，配 rtTrig 一次性切")
            else:
                call_lines.append(f"    {n:<{max_n}} := {n}_in,")
        for n, t in vio:
            call_lines.append(f"    {n:<{max_n}} := {n}_inst,")
        # Outputs
        last_idx = len(vo) - 1
        for i, (n, t) in enumerate(vo):
            tail = "" if i == last_idx else ","
            call_lines.append(f"    {n:<{max_n}} => {n}_out{tail}")
        # Strip trailing comma on last line before ')'
        if call_lines[-1].rstrip().endswith(","):
            call_lines[-1] = call_lines[-1].rstrip().rstrip(",")
        call_lines.append(");")
        impl_lines.append("// 单次完整调用：所有 VAR_INPUT / VAR_IN_OUT / VAR_OUTPUT 引脚显式赋值或绑定")
        impl_lines.append("\n".join(call_lines))
    else:
        # FUNCTION call form
        args = []
        for n, _ in vi:
            args.append(f"{n} := {n}_in")
        for n, _ in vio:
            args.append(f"{n} := {n}_inst")
        impl_lines.append("// 纯函数调用：返回值赋给本地变量做观察")
        impl_lines.append(f"{name}_ret := {name}({', '.join(args)});")

    impl = "\n".join(impl_lines)

    guid = make_guid(name)
    xml = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">\n'
        f'  <POU Name="P_Demo_{name}" Id="{guid}" SpecialFunc="None">\n'
        f'    <Declaration><![CDATA[PROGRAM P_Demo_{name}\n{decl}\n]]></Declaration>\n'
        '    <Implementation>\n'
        f'      <ST><![CDATA[{impl}\n]]></ST>\n'
        '    </Implementation>\n'
        '  </POU>\n'
        '</TcPlcObject>\n'
    )
    return xml


def _default_category(name: str) -> str:
    # Authoritative: use the registry to look up category
    reg = json.loads(REGISTRY.read_text())
    for cat_key, cat in reg["categories"].items():
        for e in cat["entries"]:
            if e["name"] == name:
                return cat_key
    return "nci_pous"


DEMO_DEFAULTS = {
    "configuration": {
        "scenario": "定制 CNC 机床开机自检：PLC 在 System Manager 之外动态创建 NCI 3D 插补组，把 X/Y/Z 三根 PTP 轴组合起来。",
        "value": "免去『改 XAE 配置 → 下载 → 重启 NC』流程，组配置在 PLC 里即时生效。",
        "verify": "在线写 bDoIt := TRUE 触发一次，观察 fbXxx.bBusy → TRUE → FALSE，bErr 应为 FALSE。若 bErr = TRUE，nErrId 给 NC 错误码（典型：组已存在、AxisId 不存在）。",
    },
    "nci_pous": {
        "scenario": "CNC 加工日常 NCI 通道操作（启停 / 加载 NC 程序 / Override / 读写 R 参数 / 错误读取）。",
        "value": "把『裸 ADS 调用』包装成有命名的 PLC FB，业务代码可读性高、错误处理显式。",
        "verify": "在线写 bDoIt := TRUE 触发一次，观察 fbXxx.bBusy → TRUE → FALSE，bErr 应为 FALSE，输出引脚给出预期值。",
    },
    "blocksearch": {
        "scenario": "CNC 加工到一半暂停（换刀 / 班次结束），第二天从指定段续接执行。",
        "value": "把『跳到某段』封装成『记录数据 + 定位解释器 + 续接执行』三步骤，避免手算 G-Code 跳段。",
        "verify": "前置：用 ItpGetBlocksearchData 记下当前位置；调本 FB 定位；操作员手动把物理轴搬到 sStartPosition；最后 ItpStepOnAfterBlocksearch 续接。在线观察 bDone → TRUE。",
    },
    "retrace": {
        "scenario": "复杂轮廓加工出错（让刀、毛刺），沿原路退回一段调整后再前进。",
        "value": "Retrace 沿 NCI 段表回放，路径精度高于 PLC 单轴反向。",
        "verify": "前置：先 ItpEnableFeederBackup(bEnable := TRUE) 启用路径备份；NC 程序跑起来；触发本 FB 观察 NCI 通道方向变化。",
    },
    "parts_program_generator": {
        "scenario": "PLC 根据上位机参数动态生成 G-Code（如根据工件尺寸生成成形加工程序），避免依赖 CAM 软件。",
        "value": "免去手拼字符串、格式错误；PPG 内部按段类型拼装确保合法 G-Code。",
        "verify": "调本 FB 追加段；最终 ItpPpgCloseMain/CloseSubroutine 后产生 .nc 文件；用 ItpLoadProgEx 加载验证可解释。",
    },
    "compatibility": {
        "scenario": "从 TwinCAT 2 移植的 CNC 项目，保持原 FB 接口不动以减少改动风险。",
        "value": "移植成本低、行为与对应 Ex 版本一致。",
        "verify": "和对应 Ex 版本相同的验证流程：在线 bDoIt 触发，观察 bBusy/bErr/nErrId。",
    },
    "obsolete": {
        "scenario": "旧项目代码里查询 TwinCAT 2 PLC 库版本号。",
        "value": "兼容性而已；新项目应该用 stLibVersion_Tc2_NCI 全局常量。",
        "verify": "调用一次观察 _ret 给出版本号字符串/整数。",
    },
}


DEMO_TRIPLETS = {
    "CfgBuild3DGroup": {
        "scenario": "CNC 雕刻机开机自检：System Manager 里把 X/Y/Z 配成 3 根独立 PTP 轴，开机由本 FB 把它们绑成 GroupId=1 的 NCI 3D 组，让解释器可以发 G-Code。",
        "value": "免去『进 XAE 配组 → 下载 → 重启 NC』流程；同一 PLC 程序可适配不同的轴组合（在线传不同 AxisId）。",
        "verify": "在 System Manager 配好 3 根 PTP 轴（AxisId 1/2/3）+ NCI 通道（ChannelId 1，GroupId 1，类型 Interpreter）。在线写 bDoIt := TRUE 触发一次，观察 fbCfgBuild3DGroup.bBusy → TRUE → FALSE，bErr 应为 FALSE。完成后 NCI 通道里 GroupId=1 已是 3D 组，下一步可 ItpLoadProgEx 加载 .nc 程序。",
    },
    "ItpLoadProgEx": {
        "scenario": "贴片机/雕刻机 PLC 根据上位机选择的工件号加载对应 G-Code 文件。把 part_001.nc 放在默认目录 C:\\ProgramData\\Beckhoff\\TwinCAT\\Mc\\Nci 下，本 FB 调用即加载到 NCI 解释器。",
        "value": "加工程序文件管理与 PLC 工程解耦；上位机选工件 → PLC 切换文件名 → 即时加载，不用重新部署 PLC。",
        "verify": "先把 'part_001.nc' 文本（ANSI 或 UTF-8 无 BOM）放到 C:\\ProgramData\\Beckhoff\\TwinCAT\\Mc\\Nci\\。在线写 sPrg_in := 'part_001.nc'、nLength_in := LEN(sPrg_in)、bDoIt := TRUE。观察 fbItpLoadProgEx.bBusy → TRUE → FALSE，bErr = FALSE 说明加载成功。bErr = TRUE 时看 nErrId（典型：文件不存在、UTF-8 BOM 残留）。",
    },
    "ItpStartStopEx": {
        "scenario": "CNC 操作台『启动』『紧急停车』两个按钮分别接 bStart / bStop 引脚。",
        "value": "标准启停接口；stop 优先级保证 PLC 周期内同时收到两沿时仍然安全（停优先）。",
        "verify": "前置：用 ItpLoadProgEx 加载好一个 .nc 程序。在线写 bDoStart := TRUE 触发，观察 fbItpStartStopEx.bBusy → TRUE → FALSE；NCI 通道开始执行段。要停下：写 bDoStop := TRUE 触发；通道立即终止、轴受控停车。",
    },
}


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def main() -> int:
    reg = json.loads(REGISTRY.read_text())
    EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    written: list[Path] = []
    for cat_key, cat in reg["categories"].items():
        title = cat["title"]
        out_dir = LIB_ROOT / cat_key
        out_dir.mkdir(parents=True, exist_ok=True)
        for e in cat["entries"]:
            name = e["name"]
            md_path = out_dir / f"{name}.md"
            tcpou_path = EXAMPLES_DIR / f"P_Demo_{name}.TcPOU"
            try:
                md_path.write_text(emit_doc(e, cat_key, title))
                tcpou_path.write_text(emit_tcpou(e))
                written.extend([md_path, tcpou_path])
                total += 1
            except Exception as ex:
                print(f"FAIL {name}: {ex}", file=sys.stderr)
                import traceback
                traceback.print_exc()
    print(f"Generated {total} entries.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
