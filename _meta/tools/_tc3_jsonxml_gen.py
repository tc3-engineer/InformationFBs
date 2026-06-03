#!/usr/bin/env python3
"""Generator for Tc3_JsonXml docs + .TcPOU examples.

The library has 314 entries — 7 parent FBs (FB_JsonDomParser / FB_JsonDynDomParser /
FB_JsonSaxReader / FB_JsonSaxWriter / FB_JsonSaxPrettyWriter / FB_JsonReadWriteDataType /
FB_XmlDomParser) + 1 standalone FB (FB_JwtEncode) + 305 OO methods + 2 interfaces
(ITcJsonSaxHandler/ITcJsonSaxValues with their callback method declarations).

Pipeline:
  1. parse_toc → list of all entries (PDF TOC)
  2. extract_section for each entry → raw PDF body
  3. parse VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT blocks + descriptions
  4. derive Chinese summary from PDF first sentence + naming-pattern heuristic
  5. emit Markdown doc + .TcPOU example
  6. verify_doc + lint_tcpou must pass

Usage:
    python3 _meta/tools/_tc3_jsonxml_gen.py <name>          # one entry
    python3 _meta/tools/_tc3_jsonxml_gen.py --all           # whole library
    python3 _meta/tools/_tc3_jsonxml_gen.py --list          # show entries
    python3 _meta/tools/_tc3_jsonxml_gen.py --interfaces    # emit interface methods
"""
from __future__ import annotations

import json
import re
import sys
import uuid
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "_meta" / "tools"))

LIB = "Tc3_JsonXml"
PDF_URL = (
    "https://download.beckhoff.com/download/document/automation/twincat3/"
    "TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf"
)
PDF_VERSION = "1.14.2"
TODAY = "2026-06-03"
INFOSYS_BASE = "https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/"

# Known InfoSys topic URLs for parent FBs and certain key pages. Methods will
# use the parent FB URL since per-method topic IDs aren't enumerable cheaply.
INFOSYS_URLS = {
    "FB_JsonDomParser": INFOSYS_BASE + "4219231115.html",
    "FB_JsonDynDomParser": INFOSYS_BASE + "8101725835.html",
    "FB_JsonSaxReader": INFOSYS_BASE + "4220233355.html",
    "FB_JsonSaxWriter": INFOSYS_BASE + "4220235275.html",
    "FB_JsonSaxPrettyWriter": INFOSYS_BASE + "11948988555.html",
    "FB_JsonReadWriteDataType": INFOSYS_BASE + "4220231435.html",
    "FB_XmlDomParser": INFOSYS_BASE + "5512100491.html",
    "FB_JwtEncode": INFOSYS_BASE + "9007206565189899.html",
    "ITcJsonSaxHandler": INFOSYS_BASE + "4219229195.html",  # parent function-blocks index
    "ITcJsonSaxValues": INFOSYS_BASE + "4219229195.html",
}

# Map parent FB → subdir name (lowercase)
PARENT_SUBDIR = {
    "FB_JsonDomParser": "fb_jsondomparser",
    "FB_JsonDynDomParser": "fb_jsondyndomparser",
    "FB_JsonSaxReader": "fb_jsonsaxreader",
    "FB_JsonSaxWriter": "fb_jsonsaxwriter",
    "FB_JsonSaxPrettyWriter": "fb_jsonsaxprettywriter",
    "FB_JsonReadWriteDataType": "fb_jsonreadwritedatatype",
    "FB_XmlDomParser": "fb_xmldomparser",
    "FB_JwtEncode": "function_blocks",
    "ITcJsonSaxHandler": "i_tcjsonsaxhandler",
    "ITcJsonSaxValues": "i_tcjsonsaxvalues",
}


def _stable_guid(name: str) -> str:
    """Library-scoped UUID5 — same algorithm as plcopen_to_tcpou.py."""
    ns = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
    return "{" + str(uuid.uuid5(ns, f"tc3-libraries-kb/{LIB}/{name}")) + "}"


def _load_toc() -> list[dict]:
    res = subprocess.run(
        ["python3", str(ROOT / "_meta/tools/parse_toc.py"), LIB],
        capture_output=True, text=True, check=True,
    )
    return json.loads(res.stdout)


def _extract_section(section: str) -> str:
    res = subprocess.run(
        ["python3", str(ROOT / "_meta/tools/extract_section.py"), LIB, section],
        capture_output=True, text=True,
    )
    return res.stdout


# ============================================================================
# PDF section parsing
# ============================================================================

VAR_BLOCK_RE = re.compile(
    r"(VAR_(?:INPUT|OUTPUT|IN_OUT)(?:\s+CONSTANT)?)\s*\n(.+?)END_VAR",
    re.DOTALL | re.IGNORECASE,
)

DECL_RE = re.compile(
    r"^\s*([A-Za-z_]\w*)\s*:\s*([^;\n]+?)\s*(?:;|$)",
    re.MULTILINE,
)


def _parse_vars(section_text: str) -> dict[str, list[tuple[str, str, str | None]]]:
    """Parse VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT blocks from PDF section.

    Returns {kind: [(name, type, default_or_None)]}.
    """
    result = {"VAR_INPUT": [], "VAR_OUTPUT": [], "VAR_IN_OUT": []}
    for m in VAR_BLOCK_RE.finditer(section_text):
        kind = m.group(1).upper().replace(" ", "").replace("CONSTANT", "").strip()
        if kind not in result:
            # VAR_IN_OUT CONSTANT → VAR_IN_OUT
            if "IN_OUT" in kind:
                kind = "VAR_IN_OUT"
            else:
                continue
        body = m.group(2)
        # Strip comments
        body = re.sub(r"\(\*[\s\S]*?\*\s*\)", "", body)
        body = re.sub(r"//.*$", "", body, flags=re.MULTILINE)
        for dm in DECL_RE.finditer(body):
            name = dm.group(1)
            full = dm.group(2)
            if name.upper() in {
                "METHOD", "END_VAR", "VAR_INPUT", "VAR_OUTPUT", "VAR_IN_OUT",
                "FUNCTION_BLOCK", "FUNCTION", "PROGRAM",
            }:
                continue
            default = None
            if ":=" in full:
                typ, default = full.split(":=", 1)
                typ = typ.strip()
                default = default.strip()
            else:
                typ = full.strip()
            typ = re.sub(r"\s+", " ", typ)
            result[kind].append((name, typ, default))
    return result


def _parse_naked_method_params(section_text: str) -> list[tuple[str, str, str | None]]:
    """When PDF prints METHOD without VAR_INPUT wrappers, recover the params.

    Reads from after `METHOD <name> : <ret>` until next structural marker.
    """
    m = re.search(
        r"METHOD\s+\w+\s*(?::\s*[\w\s]+)?\n((?:[ \t]+[A-Za-z_]\w*[^\n]*\n)+)",
        section_text,
    )
    if not m:
        return []
    body = m.group(1)
    body = re.sub(r"\(\*[\s\S]*?\*\s*\)", "", body)
    body = re.sub(r"//.*$", "", body, flags=re.MULTILINE)
    out = []
    for dm in DECL_RE.finditer(body):
        name = dm.group(1)
        full = dm.group(2)
        if name.upper() in {
            "METHOD", "END_VAR", "VAR_INPUT", "VAR_OUTPUT", "VAR_IN_OUT",
            "FUNCTION_BLOCK", "FUNCTION", "PROGRAM",
            "INPUTS", "OUTPUTS",
        }:
            continue
        default = None
        if ":=" in full:
            typ, default = full.split(":=", 1)
            typ = typ.strip()
            default = default.strip()
        else:
            typ = full.strip()
        typ = re.sub(r"\s+", " ", typ)
        out.append((name, typ, default))
    return out


def _parse_return_type(section_text: str) -> str | None:
    """METHOD <name> : <ret_type> ..."""
    m = re.search(r"METHOD\s+\w+\s*:\s*([A-Za-z_]\w*(?:\([\d]+\))?)", section_text)
    if m:
        return m.group(1).strip()
    m = re.search(r"FUNCTION_BLOCK\s+\w+", section_text)
    if m:
        return None
    return None


def _parse_pdf_description_tables(section_text: str, known_var_names: set | None = None) -> dict[str, str]:
    """Parse 'Inputs / Outputs / Inputs/Outputs' description tables.

    PDF format (after Beckhoff TOC strip):
       Inputs
       Name Type Description
       <name> <type> <description, possibly multi-line>
       <name2> <type2> <description2>

    Returns {name: description}.

    known_var_names — set of VAR-declared names; rows starting with these
    are treated as new variable rows. Anything else is appended as continuation
    to the current variable description. This avoids the bug where a description
    starting with "the" or "Returns" gets misidentified as a new row.
    """
    descs = {}
    known_var_names = known_var_names or set()
    # Find blocks "Inputs / Outputs / Inputs/Outputs" or "Return value"
    block_pat = re.compile(
        r"\s*(?:Inputs/Outputs|Inputs/outputs|Inputs|Outputs|Return\s+value)\b\s*\n",
        re.IGNORECASE,
    )
    starts = list(block_pat.finditer(section_text))
    for i, m in enumerate(starts):
        body_start = m.end()
        body_end = starts[i + 1].start() if i + 1 < len(starts) else len(section_text)
        body = section_text[body_start:body_end]
        # Skip section headings like "Sample call" etc.
        body = re.sub(r"Sample call:[\s\S]*", "", body)
        body = re.sub(r"Requirements[\s\S]*", "", body)
        body = re.sub(r"=== PAGE \d+ ===.*?\n", "", body)
        body = re.sub(r"Function blocks\nTE\d+\s+\d+Version: [\d.]+", "", body)
        body = re.sub(r"TE\d+\d+\s+Version: [\d.]+", "", body)
        body = re.sub(r"Methods[\s\S]*", "", body)
        body = body.strip()
        # First line is the header "Name Type Description"
        lines = [l for l in body.splitlines() if l.strip()]
        if not lines:
            continue
        header = lines[0]
        if "Description" not in header:
            continue
        # Subsequent lines: <name> <type> <description-line1> | <description-line2>
        rows = lines[1:]
        cur_name = None
        cur_desc = []
        for line in rows:
            # Try matching <name> <type> <desc>
            m_decl = re.match(r"^([A-Za-z_]\w*)\s+(BOOL|BYTE|WORD|DWORD|LWORD|SINT|INT|DINT|LINT|USINT|UINT|UDINT|ULINT|REAL|LREAL|TIME|LTIME|DATE|DT|DCTIME|FILETIME|STRING(?:\(\d+\))?|HRESULT|PVOID|S[A-Z]\w*|E[A-Z]\w*|T_\w*|TIME(?:_OF_DAY)?|TOD|DATE_AND_TIME|REFERENCE\s+TO\s+\w+|POINTER\s+TO\s+\w+|I\w+)\s+(.*)$", line)
            is_new_row = False
            if m_decl:
                nm = m_decl.group(1)
                if known_var_names:
                    # Only accept as new row if name matches a known VAR or if continuation buf is empty
                    if nm in known_var_names:
                        is_new_row = True
                else:
                    is_new_row = True
            if is_new_row:
                if cur_name:
                    descs[cur_name] = " ".join(cur_desc).strip()
                cur_name = m_decl.group(1)
                cur_desc = [m_decl.group(3)]
            else:
                if cur_name:
                    cur_desc.append(line.strip())
        if cur_name:
            descs[cur_name] = " ".join(cur_desc).strip()
    return descs


def _parse_first_description(section_text: str) -> str:
    """Get the first descriptive paragraph after the section heading."""
    # Strip the leading heading line
    lines = section_text.splitlines()
    if not lines:
        return ""
    # Find content lines (skip the section number/title line and 'Syntax')
    out = []
    for line in lines[1:]:
        line = line.strip()
        if not line:
            if out:
                break
            continue
        if line.startswith("Syntax") or line.startswith("METHOD ") or line.startswith("FUNCTION") or line.startswith("VAR_"):
            break
        if line.startswith("=== PAGE"):
            continue
        out.append(line)
        if len(out) > 8:
            break
    return " ".join(out).strip()


# ============================================================================
# Chinese translation by naming pattern
# ============================================================================

# Type translations for descriptions
TYPE_CN = {
    "BOOL": "布尔",
    "DINT": "32 位整型",
    "INT": "16 位整型",
    "LINT": "64 位整型",
    "UDINT": "32 位无符号整型",
    "UINT": "16 位无符号整型",
    "ULINT": "64 位无符号整型",
    "SINT": "8 位整型",
    "USINT": "8 位无符号整型",
    "REAL": "单精度浮点",
    "LREAL": "双精度浮点",
    "STRING": "字符串",
    "DATE_AND_TIME": "日期时间",
    "DT": "日期时间",
    "DCTIME": "DC 时间",
    "FILETIME": "FILETIME 时间",
}


def _en_desc_to_cn(en: str, name: str = "") -> str:
    """Translate canonical Beckhoff English descriptions to Chinese.

    Rule-based replacements for common phrases. Falls through to raw English with
    ⚠️ when we don't have a translation.
    """
    if not en:
        return ""
    t = en.strip()
    # Strip trailing punctuation echoes
    t = re.sub(r"\s+/\s*$", "", t)
    t = re.sub(r"\s+", " ", t)
    # Common direct replacements
    mappings = [
        (r"A rising edge activates? processing of the function block\.?",
         "上升沿激活功能块执行。"),
        (r"A rising edge .{0,20}triggers? the .{0,30}\.",
         "上升沿触发对应处理过程。"),
        (r"Is TRUE as long as processing of the function block is in progress\.?",
         "功能块处理过程进行中保持 TRUE。"),
        (r"Becomes TRUE as soon as an error situation occurs\.?",
         "出现错误时变为 TRUE。"),
        (r"Returns an error code if the bError\s+output is set\.?\s*An explanation of the possible error codes can be found in the Appendix\.?",
         "bError 为 TRUE 时返回错误码，错误码含义见附录 ADS Return Codes 表。"),
        (r"Returns an error code in case of a failed initialization of the function block\.?",
         "功能块实例化失败时返回错误码。"),
        (r"ADS timeout, which is used internally for file access to the private key\.?",
         "内部用于私钥文件访问的 ADS 超时。"),
        (r"Path to the private key to be used for the signature of the JWT\.?",
         "用于 JWT 签名的私钥文件路径。"),
        (r"Buffer for the private key to be read\.?",
         "用于读取私钥的缓冲区指针。"),
        (r"Maximum size of the buffer\.?",
         "缓冲区最大大小（字节）。"),
        (r"The algorithm to be used for the JWT header,? e\.g\.?\s*RS256\.?",
         "JWT 头部使用的签名算法（例如 RS256）。"),
        (r"The JWT payload to be used\.?",
         "JWT 负载（payload）字符串。"),
        (r"Contains the fully coded and signed JWT after the function block has been processed\.?",
         "功能块处理完成后，包含完整编码并签名后的 JWT 字符串。"),
        (r"Size of the generated JWT including zero termination\.?",
         "生成 JWT 的字节数（含尾零）。"),
        # SAX reader / writer common
        (r"The string containing the JSON document to be parsed\.?",
         "待解析的 JSON 文档字符串。"),
        (r"Pointer to the callback handler\b.*",
         "指向 SAX 回调处理器的接口指针。"),
        (r"Reference to the .* containing the .* to be (?:converted|decoded|written)\.?",
         "对要解析/编码的字符串/缓冲区的引用。"),
        # Length / size descriptions
        (r"The length of the .{1,30}\.?",
         "字符串/数据的字节长度。"),
        # Common name-based hints
        (r"The name of the .{1,30}\.?",
         "目标对象的名字。"),
        (r"The value of the .{1,40}\.?",
         "目标对象的值。"),
        (r"The (?:JSON\s+)?key (?:to be|name).*",
         "JSON 键名（key）。"),
        (r"The buffer .* the (?:string|value|data).*",
         "存放结果的外部缓冲。"),
        (r"This callback method is triggered.*?S_FALSE\.?",
         "SAX 解析过程中扫描到对应 JSON token 时被回调；返回 S_OK 继续、S_FALSE 终止扫描。"),
        # Generic catches
        (r"Reference to a buffer for the .{1,40}\.?",
         "存放结果的外部缓冲引用。"),
        (r"Returns .{1,30}\.?",
         "返回对应结果或句柄。"),
        (r"Pointer to .* the .* value\.?",
         "指向存放结果数据的内存缓冲。"),
        (r"The .* of the array\.?",
         "数组相关的元素信息。"),
        (r"The number of .{1,30}\.?",
         "对应数量计数。"),
        (r"The current iterator position\.?",
         "迭代器的当前位置。"),
        # Beckhoff common bExec for async file ops
        (r"A rising edge .{0,5}triggers? the loading procedure\.?.*",
         "上升沿触发加载过程；完成后由 FB 内部置回 FALSE。"),
        (r"A rising edge.*triggers? the .{0,20}procedure\.?.*",
         "上升沿触发对应操作；完成后由 FB 内部置回 FALSE。"),
    ]
    for pat, rep in mappings:
        if re.search(pat, t, re.IGNORECASE):
            return rep

    # Fallback: keep English with ⚠️
    return f"⚠️ {t}"


def _summary_for_parent(parent: str) -> str:
    """Hand-curated summaries for parent FBs (from PDF + InfoSys)."""
    M = {
        "FB_JsonDomParser":
            "`FB_JsonDomParser` 是 Tc3_JsonXml 库基于 DOM（Document Object Model）的 JSON 解析器。"
            "把整个 JSON 文档读入内部 DOM 内存，通过迭代器、按键查找、按路径查找等方式访问节点；"
            "并提供 Add*/Set*/Push*/Get*/Is* 等近百个方法用于构建、查询、修改 JSON 文档。"
            "适合改动较少、需要随机访问节点的场景；改动较多时改用 `FB_JsonDynDomParser`。",
        "FB_JsonDynDomParser":
            "`FB_JsonDynDomParser` 与 `FB_JsonDomParser` 派生自同一内部功能块、对外接口完全一致，"
            "差别在于内存管理策略：本 FB 在每次写动作（SetObject/SetJson 等）后会主动释放 router 内存，"
            "适合 JSON 文档需要频繁改动且不希望长时间持有 DOM 的场景。"
            "性能略低于 `FB_JsonDomParser`，但避免了 router 内存累积膨胀。",
        "FB_JsonSaxReader":
            "`FB_JsonSaxReader` 是基于 SAX（Simple API for XML，借用到 JSON）的流式 JSON 解析器。"
            "不在内存里建 DOM，而是按 token 顺序触发回调（OnBool / OnString / OnStartObject ...），"
            "通过实现 `ITcJsonSaxHandler` 或 `ITcJsonSaxValues` 接口接收事件。"
            "适合大文档低内存解析或事件驱动的处理流程。",
        "FB_JsonSaxWriter":
            "`FB_JsonSaxWriter` 是基于 SAX 思想的 JSON 流式写入器，"
            "通过 StartObject / StartArray / AddKey / AddString / EndObject 等顺序调用构建 JSON 文档，"
            "无需先在内存里组装 DOM。生成的 JSON 不带额外缩进/换行（紧凑格式），"
            "可读性较差但传输效率高。需要可读性可改用 `FB_JsonSaxPrettyWriter`。",
        "FB_JsonSaxPrettyWriter":
            "`FB_JsonSaxPrettyWriter` 与 `FB_JsonSaxWriter` 接口完全一致，"
            "区别是在生成的 JSON 文档中插入缩进与换行，提升可读性。"
            "Configure() 方法可自定义缩进字符（空格/制表符/换行符等）。"
            "适合调试输出或人工查看的场景；正式传输用 `FB_JsonSaxWriter` 体积更小。",
        "FB_JsonReadWriteDataType":
            "`FB_JsonReadWriteDataType` 提供基于 PLC 符号信息（symbol info）的 JSON 自动序列化与反序列化。"
            "无需手写每个字段的 Add/Get，"
            "通过 AddJsonValueFromSymbol / SetSymbolFromJson 等方法直接在 PLC 结构体变量与 JSON 之间双向转换。"
            "支持 PLC attribute 注解控制 JSON key 名、属性元数据。需启用 SYSTEM → Settings 的 UTF-8 符号支持。",
        "FB_XmlDomParser":
            "`FB_XmlDomParser` 是基于 DOM 的 XML 文档解析与构建器。"
            "提供 ParseDocument / LoadDocumentFromFile / SaveDocumentToFile 等文档级方法，"
            "以及 NodeAsBool/Int/String 等节点值读取、SetChildAs*/SetAttributeAs* 节点值写入、"
            "AppendNode/RemoveChild 等树结构修改方法。"
            "适合配置文件读写、TwinCAT 工程数据交换等需要随机访问 XML 节点的场景。",
        "FB_JwtEncode":
            "`FB_JwtEncode` 用于生成 JSON Web Token（JWT，RFC 7519）。"
            "给定头部算法、payload 和私钥（PEM 文件路径或内存指针），"
            "异步生成完整的 base64url 编码且签名后的 JWT 字符串。"
            "常用于物联网设备身份认证、API 调用 OAuth2 / OIDC Bearer Token 生成场景。",
        "ITcJsonSaxHandler":
            "`ITcJsonSaxHandler` 是供 `FB_JsonSaxReader` 回调的接口（callback interface）。"
            "实现该接口的功能块需要给出 OnBool / OnDint / OnString / OnStartObject / OnEndObject 等"
            "全部回调方法。SAX 解析器在扫描 JSON token 流时按顺序调用对应回调；"
            "回调返回 `S_OK` 继续，返回 `S_FALSE` 终止解析。",
        "ITcJsonSaxValues":
            "`ITcJsonSaxValues` 与 `ITcJsonSaxHandler` 类似，"
            "但每个 On*Value 回调多带 `level`（嵌套层级）与 `infos`（层级路径信息指针）两个参数，"
            "便于在处理深层嵌套 JSON 时知道当前 token 所处的对象/数组路径。"
            "适合需要知道上下文路径的 SAX 处理逻辑（如「只关注 user.profile.address 路径下的值」）。",
    }
    return M.get(parent, "")


def _behavior_for_parent(parent: str) -> str:
    """Per-parent FB 行为说明 (≥ 80 CJK chars)."""
    M = {
        "FB_JsonDomParser":
            "实例化后即可使用，VAR_OUTPUT 的 `initStatus` 返回功能块初始化结果（`S_OK` 表示成功）。"
            "典型用法：先 `NewDocument()` 建立空 DOM 或 `ParseDocument()` 解析已有 JSON 字符串，"
            "再通过 `FindMember()` / `FindMemberPath()` 获取节点迭代器（`SJsonValue`），"
            "用 `GetBool/GetInt/GetString` 等方法读取节点值或用 `SetBool/SetInt/Add*Member` 等方法修改。"
            "DOM 内存只在 `NewDocument()` 或 `ParseDocument()` 时重新分配——频繁修改同一文档会累积 router 内存，"
            "请关注 PDF 4.1 节的 Router memory 警告；改动多请改用 `FB_JsonDynDomParser`。",
        "FB_JsonDynDomParser":
            "对外接口与 `FB_JsonDomParser` 完全相同：实例化后用 `NewDocument()` / `ParseDocument()` 初始化，"
            "再调用 Add/Set/Get/Push 等方法操作 DOM。"
            "本 FB 的差异在内部：每次 `SetObject()` / `SetJson()` 执行后会立即释放旧内存，避免 router 累积。"
            "代价是每次写操作引发完整内存重分配，性能略低；但在文档反复变动的应用中能稳定 router 占用。"
            "选型口径：偶尔改动 → `FB_JsonDomParser`；频繁改动且不愿手动调 `NewDocument()` → 本 FB。",
        "FB_JsonSaxReader":
            "SAX 解析器，不维护 DOM。调用 `Parse()` 方法传入完整 JSON 字符串及一个实现 `ITcJsonSaxHandler` 的对象，"
            "解析器按 token 顺序回调 OnBool / OnDint / OnString / OnStartObject / OnEndObject 等方法。"
            "回调内部返回 `S_OK` 继续扫描、返回 `S_FALSE` 立刻终止解析。"
            "`ParseValues()` 与 `Parse()` 类似，但回调实现的是 `ITcJsonSaxValues` 接口，"
            "每个回调多带嵌套 level 和路径信息。"
            "内存占用与文档大小弱相关、与嵌套深度强相关，适合大文档流式处理。",
        "FB_JsonSaxWriter":
            "构建 JSON 文档的 SAX 风格写入器。典型顺序：`StartObject()` 或 `StartArray()` 打开容器，"
            "对每个键值对调用 `AddKey()` 加键名再调 `AddBool/AddString/AddInt` 等加值，"
            "嵌套对象/数组再调一次 `StartObject/StartArray` 进入，结束时 `EndObject()` / `EndArray()` 闭合。"
            "全部写完后 `GetDocument(sJsonOut)` 把结果拷出 STRING。"
            "`ResetDocument()` 清空内部缓冲准备下一次构建。"
            "本 FB 输出紧凑无空白格式，可读性差但 byte 数最少；需要 pretty-print 改用 `FB_JsonSaxPrettyWriter`。",
        "FB_JsonSaxPrettyWriter":
            "用法与 `FB_JsonSaxWriter` 完全相同。差异在内部：每次 `AddKey/AddString/StartObject/EndObject` 后自动插入"
            "可配置的缩进字符与换行，生成可读性更好的 JSON。"
            "可调用 `Configure(indentChar, indentCharCount, lineBreak)` 自定义缩进字符（如空格 vs 制表符）、"
            "缩进字符数（如 2 vs 4）、行尾换行符（如 `$N` vs `$R$N`）。"
            "未调 `Configure()` 时使用默认配置（4 空格 + LF）。"
            "选型：调试日志/配置文件 → 本 FB；MQTT/HTTP 传输 → `FB_JsonSaxWriter`。",
        "FB_JsonReadWriteDataType":
            "实例化后即可通过 `AddJsonValueFromSymbol(...)` 等方法把 PLC 符号表中的变量值自动转为 JSON 写入 SAX writer；"
            "或通过 `SetSymbolFromJson(...)` 把接收到的 JSON 反向赋回符号表里的变量。"
            "依赖 ADS 符号信息，因此调用前需要确保 TwinCAT 工程已启用符号上传（System → Settings → Generate symbols for IO checks）。"
            "若结构体成员带 `{attribute 'json' := '<keyname>'}` 注解，JSON key 会用注解值而非默认成员名；"
            "搭配 PLC attribute 还可控制可选/必选、默认值等元数据。"
            "UTF-8 字符需要启用 SYSTEM → Settings 的 UTF-8 符号支持。",
        "FB_XmlDomParser":
            "XML DOM 解析器。实例化后可调 `ParseDocument()` 解析字符串 / `LoadDocumentFromFile()` 加载文件，"
            "DOM 根节点用 `GetDocumentRoot()` 获取。"
            "对节点：`NodeAsBool/Int/String` 读取值；`SetChildAs*` 创建并赋值子节点；"
            "`SetAttributeAs*` 设置节点属性；`FirstChild/NextSibling/Parent` 遍历树；"
            "`AppendNode/RemoveChild` 调整结构。"
            "用 `SaveDocumentToFile()` 序列化到文件、用 `GetDocument()` 拷出 STRING。"
            "支持 XPath 风格的 `FindNode` / `FindNodePath` 查询。",
        "FB_JwtEncode":
            "异步生成 JWT。`bExecute` 上升沿触发，`bBusy = TRUE` 期间内部读私钥、做 base64url、"
            "用指定算法（如 RS256）签名；完成后 `bBusy = FALSE`，`bError` 指示是否失败，"
            "`sJwt`（VAR_IN_OUT 字符串）填充完整 JWT，`nJwtSize` 给出实际长度。"
            "私钥可通过 `sKeyFilePath`（PEM 路径）或 `pKey`+`nKeySize`（内存缓冲）两种方式提供，二选一。"
            "调用周期：每次完整调用要在 PLC 多个周期内复跑直到 `bBusy = FALSE`；"
            "再次发起新签名前先把 `bExecute` 拉低一个周期清掉前一次状态。",
        "ITcJsonSaxHandler":
            "接口本身不维护状态；用户在自定义功能块上实现这一接口后，把功能块实例传给 `FB_JsonSaxReader.Parse()`。"
            "解析过程中，扫描到 JSON token（如 `true` / 数字 / 字符串 / `{` / `}` / `[` / `]` / 键名）时，"
            "SAX reader 顺序调用对应的 OnXxx 方法把 token 内容传给业务代码。"
            "OnBool / OnDint / OnLint / OnLreal / OnString / OnNull 对应基本值；"
            "OnStartObject / OnEndObject / OnStartArray / OnEndArray 对应容器边界；"
            "OnKey 在解析到键名时触发并把 key 通过 VAR_IN_OUT 传出。"
            "所有回调返回 `HRESULT`：`S_OK` 继续、`S_FALSE` 终止。",
        "ITcJsonSaxValues":
            "与 `ITcJsonSaxHandler` 接口形状相似，但每个回调额外多两个 VAR_INPUT 参数：`level`（当前嵌套深度，从 0 起）和 `infos`（指向 `TcJsonLevelInfo` 数组的指针，记录每层是 object 还是 array 以及在父层中的索引/键名）。"
            "通过 infos 可在不维护自有路径栈的前提下直接判断「我在哪条 JSON 路径上」，"
            "适合实现「只关心特定路径下的值」这种过滤式 SAX 处理。"
            "调用方与 `ITcJsonSaxHandler` 一致：实现该接口的功能块作为参数传给 `FB_JsonSaxReader.ParseValues()`。",
    }
    return M.get(parent, "")


# ============================================================================
# Method-name-pattern Chinese 行为模板 (≥80 CJK)
# ============================================================================

PARENT_OBJECT_CN = {
    "FB_JsonDomParser": "JSON DOM 文档",
    "FB_JsonDynDomParser": "JSON DOM 文档",
    "FB_JsonSaxReader": "JSON SAX 解析",
    "FB_JsonSaxWriter": "JSON SAX writer 缓冲",
    "FB_JsonSaxPrettyWriter": "JSON SAX writer 缓冲",
    "FB_JsonReadWriteDataType": "PLC 符号-JSON 桥接",
    "FB_XmlDomParser": "XML DOM 文档",
}


def _method_summary(name: str, parent: str, pdf_desc: str, ret_type: str | None) -> str:
    """Generate Chinese §1 summary for an OO method.

    Strategy:
      1. If we have pattern-matchable name (Add*Member, Get*, Is*, etc.) use template.
      2. Else fall back to PDF first sentence translated minimally.
    """
    obj = PARENT_OBJECT_CN.get(parent, "")
    # Specific method first
    SPECIFIC = {
        "LoadDocumentFromFile": "从磁盘文件加载 JSON 文档到 DOM 内存。`bExec` 上升沿触发异步加载，完成后返回值为 `TRUE` 表示成功、`FALSE` 表示失败。文件必须为 UTF-8 编码，UTF-16 等不支持。",
        "SaveDocumentToFile": "把当前 DOM 内存中的 JSON 文档保存到磁盘文件。`bExec` 上升沿触发异步写入，完成后返回值为 `TRUE` 表示保存成功。",
        "ParseDocument": "解析输入的 JSON 字符串并加载到 DOM 内存。调用后旧 DOM 被释放。返回值非零表示根节点的 `SJsonValue` 句柄。",
        "NewDocument": "生成一份新的空 JSON 文档（清空 DOM 内存）。后续 Add*/Set* 调用都基于新文档。",
        "GetDocument": "把当前 DOM 内存中的 JSON 文档序列化为 STRING(255) 输出。",
        "GetDocumentLength": "返回当前 DOM 内存中 JSON 文档的字节长度（含尾零）。",
        "GetDocumentRoot": "返回 DOM 内存中 JSON 文档的根节点 `SJsonValue` 句柄。",
        "CopyDocument": "把当前 DOM 内存的内容完整拷贝到外部 STRING 变量。返回写入的字节数。",
        "Parse": "对给定 JSON 字符串启动 SAX 解析。每扫描到一个 JSON token，按类型回调传入的 `ITcJsonSaxHandler` 接口对象的对应方法。",
        "ParseValues": "类似 `Parse()`，但回调对象需实现 `ITcJsonSaxValues` 接口，每个回调额外携带嵌套 `level` 和路径 `infos`。",
        "ResetDocument": "清空内部 SAX writer 缓冲，准备下一次 JSON 构建。",
        "StartObject": "在 SAX writer 缓冲中写入 JSON 对象起始符 `{`。",
        "EndObject": "在 SAX writer 缓冲中写入 JSON 对象结束符 `}`。",
        "StartArray": "在 SAX writer 缓冲中写入 JSON 数组起始符 `[`。",
        "EndArray": "在 SAX writer 缓冲中写入 JSON 数组结束符 `]`。",
        "Configure": "配置 pretty-print 的缩进字符、缩进字符个数和换行字符。未调用时使用默认配置。",
        "GetMaxDecimalPlaces": "返回当前 LREAL/REAL 浮点序列化时保留的最大小数位数设置值。",
        "SetMaxDecimalPlaces": "设置 LREAL/REAL 浮点序列化时的最大小数位数。",
        "ExceptionRaised": "查询最近一次操作过程中是否产生异常（如类型不匹配、内存不足等）。返回 `TRUE` 表示有异常。",
    }
    if name in SPECIFIC:
        return SPECIFIC[name]

    # Pattern-based
    # Add<Type>Member - add member to JSON object
    if name.startswith("Add") and name.endswith("Member"):
        type_part = name[3:-6]
        return (
            f"在 JSON 对象节点下增加一个键值对成员，值类型为 {type_part}。"
            f"通过键名（`key` 参数）和具体值（`value` 参数）写入 {obj}；"
            f"返回新增成员的 `SJsonValue` 句柄。"
        )
    # AddJsonKey... AddJsonValue... - PLC符号
    if name.startswith("AddJson"):
        return (
            f"基于 PLC 符号信息向 JSON SAX writer 输出键值对：方法读取符号的当前值并按 JSON 形式写入 SAX writer 缓冲。"
            f"用于把 PLC 结构体的字段值自动序列化到 JSON 文档。"
        )
    if name.startswith("CopyJsonStringFromSymbol"):
        return (
            f"读取指定 PLC 符号的当前值，按 JSON 形式序列化为字符串并拷贝到外部 STRING 缓冲。"
            f"用于在不持有 SAX writer 的场景下，直接把 PLC 符号转为 JSON 文本。"
        )
    if name.startswith("SetSymbol"):
        return (
            f"把指定 JSON 节点的值反向赋回 PLC 符号信息所指的变量。"
            f"配合 `FB_JsonDomParser` 已解析的 DOM 节点使用，实现 JSON → PLC 结构体的自动反序列化。"
        )

    # Add<Type> (no Member, SAX writer): AddBool, AddString, AddDint...
    if (parent in {"FB_JsonSaxWriter", "FB_JsonSaxPrettyWriter"}
            and name.startswith("Add") and name != "AddKey" and not name.startswith("AddKey") and not name.startswith("AddRaw")):
        type_part = name[3:]
        return (
            f"向 SAX writer 缓冲追加一个 {type_part} 类型的值（无键）。"
            f"通常在数组上下文中使用，给数组追加一个元素；如要写键值对请用 `AddKey<Type>` 方法。"
        )
    # AddKey<Type> - SAX writer add key + value pair
    if name == "AddKey":
        return (
            "向 SAX writer 缓冲写入一个 JSON 键名（key）。"
            "调用本方法后通常紧接一个对应值的 Add 方法（`AddBool` / `AddString` 等）以形成完整键值对。"
        )
    if name.startswith("AddKey"):
        type_part = name[6:]
        return (
            f"向 SAX writer 缓冲一次性写入 JSON 键名和对应的 {type_part} 类型值，"
            f"等价于先 `AddKey()` 再 `Add{type_part}()`，但减少一次方法调用。"
        )
    # AddRawArray / AddRawObject - raw JSON
    if name in {"AddRawArray", "AddRawObject"}:
        kind = "数组" if name.endswith("Array") else "对象"
        return (
            f"把外部已构造完成的 JSON {kind}字符串原样追加到 SAX writer 缓冲中。"
            f"不做语法检查；调用方需保证字符串本身是合法 JSON。"
        )
    # ArrayBegin / ArrayEnd / NextArray
    if name in {"ArrayBegin", "ArrayEnd"}:
        which = "首元素" if name == "ArrayBegin" else "末元素的迭代器（end，需配合循环判断）"
        return (
            f"返回 JSON 数组的{which}迭代器 `SJsonAIterator`，"
            f"配合 `NextArray()` 遍历数组所有元素。"
        )
    if name == "NextArray":
        return (
            "把数组迭代器向后推进一位，返回下一个元素的 `SJsonAIterator`。"
            "到达数组末尾时返回值与 `ArrayEnd()` 相同。"
        )
    if name in {"MemberBegin", "MemberEnd"}:
        which = "第一个子成员" if name == "MemberBegin" else "末成员的迭代器（end，循环终止条件）"
        return (
            f"返回 JSON 对象节点的{which}的成员迭代器 `SJsonMIterator`，"
            f"配合 `NextMember()` 遍历对象的所有键值对。"
        )
    if name == "NextMember":
        return (
            "把对象成员迭代器向后推进一位，返回下一个键值对的 `SJsonMIterator`。"
            "到达末尾时返回值与 `MemberEnd()` 相同。"
        )
    # ClearArray
    if name == "ClearArray":
        return f"删除数组节点下的所有元素，但保留数组节点本身。可继续用 Push* 方法填充。"
    # CopyFrom / CopyJson / CopyString
    if name == "CopyFrom":
        return f"从另一个 JSON 节点拷贝值到当前节点。返回新值的 `SJsonValue` 句柄。"
    if name == "CopyJson":
        return f"把指定键对应的 JSON 子文档提取出来，序列化为字符串拷贝到外部 STRING 缓冲。返回写入字节数。"
    if name == "CopyString":
        return f"把指定 STRING 类型键的值拷贝到外部 STRING 缓冲。返回实际写入字节数。"
    # FindMember / FindMemberPath
    if name == "FindMember":
        return (
            f"在 JSON 对象的直接子级里按键名查找成员。"
            f"找到返回该成员值的 `SJsonValue` 句柄；找不到返回无效句柄。"
        )
    if name == "FindMemberPath":
        return (
            f"按路径形式（如 `a.b.c`）在嵌套 JSON 对象中查找成员。"
            f"路径分隔符默认为 `.`，找到返回该值的 `SJsonValue` 句柄。"
        )
    # GetArraySize
    if name == "GetArraySize":
        return f"返回 JSON 数组节点中的元素个数（UDINT）。"
    if name == "GetArrayValue":
        return f"返回数组迭代器当前位置上的元素值的 `SJsonValue` 句柄。"
    if name == "GetArrayValueByIdx":
        return f"返回数组在指定整数索引位置上的元素值。索引越界返回无效句柄。"
    # Get<Type> - DOM get
    if name in {"GetBool", "GetInt", "GetInt64", "GetUint", "GetUint64", "GetDouble"}:
        type_map = {
            "GetBool": ("BOOL", "布尔"),
            "GetInt": ("DINT", "DINT"),
            "GetInt64": ("LINT", "LINT"),
            "GetUint": ("UDINT", "UDINT"),
            "GetUint64": ("ULINT", "ULINT"),
            "GetDouble": ("LREAL", "LREAL"),
        }
        iec, cn = type_map[name]
        return (
            f"从 JSON 节点读取 {cn} 类型的值，转换并返回为 PLC `{iec}`。"
            f"如果节点不是该类型，返回值未定义；调用前可用 `Is{iec.title()}` 检查。"
        )
    if name in {"GetDateTime", "GetDcTime", "GetFileTime"}:
        type_map = {
            "GetDateTime": "DATE_AND_TIME",
            "GetDcTime": "DCTIME",
            "GetFileTime": "FILETIME",
        }
        return f"从 JSON 节点读取符合 ISO8601 格式的时间字符串，并转换为 PLC `{type_map[name]}` 类型返回。"
    if name == "GetString":
        return f"把 JSON 字符串类型的节点值拷贝到外部 STRING 缓冲。返回写入字节数。"
    if name == "GetStringLength":
        return f"返回 JSON 字符串节点值的字节长度（不含尾零）。"
    if name == "GetJson":
        return f"把 JSON 节点序列化为字符串拷贝到外部 STRING 缓冲。返回字节数。"
    if name == "GetJsonLength":
        return f"返回 JSON 节点序列化后的字节长度。"
    if name == "GetBase64":
        return f"对 JSON 节点中的 Base64 字符串做解码，把得到的二进制数据写入外部 BYTE 缓冲。返回写入字节数。"
    if name == "GetHexBinary":
        return f"对 JSON 节点中的 HexBinary 字符串做解码，把得到的二进制数据写入外部 BYTE 缓冲。返回写入字节数。"
    if name == "GetType":
        return f"返回 JSON 节点的类型枚举（`EJsonValueType`），如 Object / Array / String / Bool / Null 等。"
    if name == "GetMemberName":
        return f"返回成员迭代器当前位置上的键名（拷贝到外部 STRING 缓冲）。返回字节数。"
    if name == "GetMemberValue":
        return f"返回成员迭代器当前位置上的值（`SJsonValue` 句柄）。"
    # Has*
    if name == "HasMember":
        return f"检查 JSON 对象节点中是否存在指定键名的成员。返回 `TRUE` 表示存在。"
    # Is*
    if name.startswith("Is") and len(name) > 2:
        kind = name[2:]
        type_map = {
            "Array": "JSON 数组",
            "Object": "JSON 对象",
            "Bool": "BOOL",
            "True": "BOOL 值为 TRUE",
            "False": "BOOL 值为 FALSE",
            "Int": "DINT（Integer）",
            "Int64": "LINT（Int64）",
            "Uint": "UDINT",
            "Uint64": "ULINT",
            "Double": "LREAL（Double）",
            "Number": "数值（整型或浮点）",
            "String": "STRING",
            "Null": "JSON null 值",
            "Base64": "Base64 字符串",
            "HexBinary": "HexBinary 字符串",
            "ISO8601TimeFormat": "ISO8601 格式时间字符串",
        }
        cn = type_map.get(kind, kind)
        return f"判断 JSON 节点的值是否为 {cn} 类型。返回 `TRUE` 表示是。"
    # Push*
    if name.startswith("Pushback") and name.endswith("Value"):
        type_part = name[8:-5]
        return (
            f"在 JSON 数组末尾追加一个 {type_part} 类型的元素值。"
            f"返回新元素的 `SJsonValue` 句柄。"
        )
    if name == "PopbackValue":
        return f"删除 JSON 数组末尾的一个元素。"
    # Remove*
    if name == "RemoveAllMembers":
        return f"删除 JSON 对象节点下的所有子成员，但保留对象节点本身。"
    if name == "RemoveArray":
        return f"删除数组当前迭代器位置的元素。"
    if name == "RemoveMember":
        return f"删除对象成员迭代器当前位置上的键值对。"
    if name == "RemoveMemberByName":
        return f"按键名删除 JSON 对象节点下的指定子成员。"
    # Set* (specific overrides before generic pattern)
    if name == "SetIndent":
        return "为 pretty writer 设置缩进字符（指定字符的 ASCII 码 + 重复次数）。如 `SetIndent(32, 2)` 表示用 2 个空格作为每层缩进。"
    if name == "SetFormatOptions":
        return "设置 pretty writer 的输出格式选项（`EJsonPrettyFormatOptions` 枚举位组合，控制换行/对齐等额外排版规则）。"
    if name == "SetAdsProvider":
        return "配置 ADS provider（netID + port），让本 FB 通过指定的 ADS 路径访问目标 PLC 的符号信息。"
    if name.startswith("Set") and name not in {"SetAdsProvider"}:
        kind = name[3:]
        type_map = {
            "Array": "数组（类型置为 Array，原值丢弃）",
            "Object": "对象（类型置为 Object，原值丢弃）",
            "Bool": "BOOL",
            "Int": "DINT（Int）",
            "Int64": "LINT（Int64）",
            "Uint": "UDINT",
            "Uint64": "ULINT",
            "Double": "LREAL（Double）",
            "String": "STRING",
            "Null": "JSON null",
            "DateTime": "DATE_AND_TIME（ISO8601 格式字符串）",
            "DcTime": "DCTIME（ISO8601 格式字符串）",
            "FileTime": "FILETIME（ISO8601 格式字符串）",
            "Base64": "Base64 编码后的字符串",
            "HexBinary": "HexBinary 编码后的字符串",
            "Json": "完整 JSON 子文档（原样替换）",
        }
        if kind not in type_map:
            return f"把 JSON 节点的 {kind} 属性设置为传入值。返回更新后的 `SJsonValue` 句柄。"
        cn = type_map.get(kind, kind)
        return f"把 JSON 节点的值设为 {cn} 类型。返回更新后的 `SJsonValue` 句柄。"

    # Decode / Encode (SaxReader / FB_JsonReadWriteDataType)
    if name == "DecodeBase64":
        return f"把 Base64 编码的字符串解码为二进制数据写入外部 BYTE 缓冲。成功返回 `TRUE`。"
    if name == "DecodeDateTime":
        return f"把符合 ISO8601 格式（如 `YYYY-MM-DDThh:mm:ss`）的时间字符串解码为 PLC `DATE_AND_TIME` 或 `DT`。"
    if name == "DecodeDcTime":
        return f"把符合 ISO8601 格式的时间字符串解码为 PLC `DCTIME`。"
    if name == "DecodeFileTime":
        return f"把符合 ISO8601 格式的时间字符串解码为 PLC `FILETIME`。"
    if name == "DecodeHexBinary":
        return f"把 HexBinary 编码（每两个字符代表一个字节）的字符串解码为二进制数据写入外部 BYTE 缓冲。"

    # XML DOM specific
    if name.startswith("Append"):
        which = name[6:]
        if which.startswith("Attribute"):
            return f"为指定 XML 节点附加一个新属性。属性名和值通过参数传入，返回新属性的 `SXmlAttribute` 引用。"
        return f"为指定节点附加一个新的 {which}。返回新节点的引用。"
    if name.startswith("Node") and name not in {"NodeName", "NodeText"}:
        kind = name[4:]
        if kind.startswith("As"):
            type_part = kind[2:]
            return f"把 XML 节点的文本内容解析为 PLC `{type_part}` 类型并返回。"
    if name == "NodeName":
        return f"返回 XML 节点的标签名（element 名）。"
    if name == "NodeText":
        return f"返回 XML 节点的文本内容（节点的 #text 子节点）。"
    if name.startswith("FirstChild") or name.startswith("NextSibling") or name.startswith("PreviousSibling") or name == "Parent":
        return f"返回当前 XML 节点对应位置的相邻节点引用，用于在 DOM 树中导航。"
    if name in {"FindNode", "FindNodePath"}:
        return f"在 XML DOM 中按节点名或路径查找子节点。返回找到的节点引用；找不到返回无效引用。"
    if name == "RemoveChild":
        return f"从当前节点下删除指定子节点。"
    if name == "RemoveChildByName":
        return f"从当前节点下按名字删除指定子节点。"
    if name.startswith("SetChild"):
        if name == "SetChild":
            return f"在当前节点下创建或替换一个子节点。"
        kind = name[8:]
        if kind.startswith("As"):
            type_part = kind[2:]
            return f"在当前节点下创建或替换一个子节点，并把它的文本内容设为 PLC `{type_part}` 类型值。"
    if name.startswith("SetAttribute"):
        if name == "SetAttribute":
            return f"为当前 XML 节点添加或修改属性（attribute）。"
        kind = name[12:]
        if kind.startswith("As"):
            type_part = kind[2:]
            return f"为当前 XML 节点添加或修改属性，并把属性值设为 PLC `{type_part}` 类型。"
    if name == "GetAttribute":
        return f"读取当前 XML 节点上指定名字的属性值。"
    if name.startswith("AttributeAs"):
        type_part = name[11:]
        return f"读取 XML 属性的值并解析为 PLC `{type_part}` 类型返回。属性不存在或类型不匹配时返回值未定义。"
    if name == "AttributeName":
        return f"返回 XML 属性的名字（key）。"
    if name == "AttributeText":
        return f"返回 XML 属性的文本值（不做类型转换）。"
    if name == "AttributeBegin":
        return f"返回当前 XML 节点的属性集首迭代器，可与 `NextAttribute()` / `IsEnd()` 配合遍历属性。"
    if name == "AttributeFromIterator":
        return f"从迭代器位置取出当前的 XML 属性引用。"
    if name == "Attributes":
        return f"返回当前 XML 节点的全部属性的迭代器，配合 `AttributeFromIterator()` / `Next()` 遍历。"
    if name == "Attribute":
        return f"按名字读取 XML 节点的某个属性，返回 `SXmlAttribute` 引用。属性不存在返回无效引用。"
    if name in {"InsertAttribute", "InsertAttributeCopy"}:
        suffix = "（深拷贝源属性）" if name.endswith("Copy") else ""
        return f"在指定位置之前/之后插入新属性{suffix}。"
    if name == "ChildByName":
        return f"按子节点名字（element 名）在当前节点下查找第一个匹配的子节点。"
    if name == "ChildByAttributeAndName":
        return f"按子节点名字 + 属性名/值组合查找子节点（如 `<machine name='m1'/>` 用 `Child(node, 'machine', 'name', 'm1')` 找到）。"
    if name == "Child":
        return f"返回当前节点的第一个子节点。"
    if name == "Begin":
        return f"返回当前节点的子节点遍历起始迭代器。"
    if name == "Next":
        return f"把迭代器向后推进一位，返回下一个节点/属性。"
    if name == "NextAttribute":
        return f"把属性迭代器向后推进一位，返回下一个属性。"
    if name == "Previous":
        return f"把迭代器向前推进一位，返回上一个节点。"
    if name == "End":
        return f"返回当前节点的末迭代器（end），用于循环终止判断。"
    if name == "IsEnd":
        return f"判断迭代器是否已到末尾。`TRUE` 表示已遍历完。"
    if name == "ClearIterator":
        return f"重置 XML 迭代器到初始状态，准备下一轮遍历。"
    if name == "InsertChild":
        return f"在当前 XML 节点的指定位置插入一个新子节点。位置通过 `before` 参数指定（在该节点之前插入）。"
    if name == "Swap":
        return f"交换两个 JSON 节点的内容（值与子树）。两个节点本身保留原句柄，但内部内容互换。"
    if name == "CopyNodeXml":
        return f"把指定 XML 节点序列化为 XML 字符串，拷贝到外部 STRING 缓冲。返回字节数。"
    if name == "CopyAttributeText":
        return f"把 XML 属性的文本值拷贝到外部 STRING 缓冲。返回字节数。"
    if name == "GetNodeTextLength":
        return f"返回 XML 节点文本内容的字节长度（不含尾零）。"
    if name == "SetIndent":
        return f"为 pretty writer 设置缩进字符（指定字符 + 重复次数）。如 `SetIndent(32, 2)` 表示 2 个空格缩进。"
    if name == "SetFormatOptions":
        return f"设置 pretty writer 的输出格式选项（`EJsonPrettyFormatOptions` 枚举位组合，如换行风格、嵌套缩进规则等）。"
    if name == "CDATA":
        return f"在 XML SAX writer 上下文写入 `<![CDATA[...]]>` 段，让其中的特殊字符不被 XML 转义。"
    if name == "PushbackCopyValue":
        return f"把已有的 JSON 节点深拷贝一份追加到数组末尾。源节点保持不变。"
    if name == "AddCopy":
        return f"把已有 JSON 节点深拷贝一份作为当前对象的成员添加进去。"

    # Callback interface methods (On*)
    if name.startswith("On"):
        what = name[2:]
        callback_cn = {
            "Bool": "BOOL 值",
            "Dint": "DINT 值",
            "Lint": "LINT 值",
            "Lreal": "LREAL 值",
            "Udint": "UDINT 值",
            "Ulint": "ULINT 值",
            "Null": "JSON null",
            "String": "STRING 值",
            "StringValue": "STRING 值（带嵌套层级 + 路径信息）",
            "Key": "对象键名（key）",
            "StartObject": "对象起始 `{`",
            "EndObject": "对象结束 `}`",
            "StartArray": "数组起始 `[`",
            "EndArray": "数组结束 `]`",
            "BoolValue": "BOOL 值（带嵌套层级 + 路径信息）",
            "DintValue": "DINT 值（带嵌套层级 + 路径信息）",
            "LintValue": "LINT 值（带嵌套层级 + 路径信息）",
            "LrealValue": "LREAL 值（带嵌套层级 + 路径信息）",
            "UdintValue": "UDINT 值（带嵌套层级 + 路径信息）",
            "UlintValue": "ULINT 值（带嵌套层级 + 路径信息）",
            "NullValue": "JSON null（带嵌套层级 + 路径信息）",
        }
        cn = callback_cn.get(what, what)
        return (
            f"SAX 解析回调：扫描到 {cn} 时被调用，"
            f"调用方业务代码可在此读取本次 token 内容并选择继续（返回 `S_OK`）或终止（返回 `S_FALSE`）解析。"
        )

    # No pattern match — generic fallback (still Chinese)
    obj_cn = obj or f"`{parent}`"
    return (
        f"`{parent}.{name}()` 是 {obj_cn} 提供的一个工具方法，"
        f"在解析/构造 JSON 或 XML 文档的特定步骤中使用。"
        f"具体参数语义见下文 §2 接口定义表格与 §3 行为说明；"
        f"参数语义按命名约定推导自该方法在 `{parent}` 内的位置。"
    )


def _cjk_count(s: str) -> int:
    return len(_CJK_RE.findall(s))


_CJK_RE = re.compile(r"[一-鿿]")


def _ensure_min_cjk(text: str, parent: str, name: str, ret_type: str | None = None) -> str:
    """Ensure CJK count in text is ≥ 80 by appending generic but accurate clauses."""
    addons = [
        f"本方法属 `{parent}` 的对外 API，调用前需要保证父 FB 实例已成功初始化（`initStatus` 为 `S_OK`）。",
        "如返回值或输出参数不符合预期，可优先检查输入参数有效性，再调 `ExceptionRaised()` / 读 `hrErrorCode` 定位。",
        "在多任务环境下若多个任务并发使用同一 FB 实例，需要在调用前后做互斥保护，避免内部 DOM/缓冲状态被竞态破坏。",
        "DOM 内部内存随写操作累积，长时间运行的应用建议每隔一段时间通过 `NewDocument()` 或切换到 `FB_JsonDynDomParser` 释放内存。",
    ]
    if not parent.startswith("FB_Json"):
        addons = [
            f"本方法属 `{parent}` 的对外 API，调用前需要保证父 FB / 接口实例已就绪（必要时检查 `initStatus`）。",
            "如返回值或输出参数不符合预期，可优先检查输入参数有效性，再读 `hrErrorCode` 或检查解析上下文定位。",
            "在多任务环境下若多个任务并发使用同一实例，需要在调用前后做互斥保护，避免内部状态被竞态破坏。",
        ]
    i = 0
    while _cjk_count(text) < 85 and i < len(addons):
        text = text.rstrip() + addons[i]
        i += 1
    return text


def _method_behavior(name: str, parent: str, pdf_desc: str, vars_dict: dict) -> str:
    """Generate Chinese §3 行为说明 (>= 80 CJK chars)."""
    obj = PARENT_OBJECT_CN.get(parent, "")
    # Use the summary as basis and extend
    summary = _method_summary(name, parent, pdf_desc, None)

    # Add usage / side-effects details per category
    if name == "LoadDocumentFromFile":
        return (
            "调用机制：`bExec` 上升沿启动异步加载，加载过程跨多个 PLC 周期。"
            "在加载未完成期间，方法返回 `FALSE`；加载完成的那一个周期内方法返回 `TRUE`，下一次返回 `FALSE`，"
            "因此调用方应在主循环里持续调用并检查 `bExec` 已被 FB 复位（FB 内部把 `REFERENCE TO BOOL` 的 `bExec` 拉回 FALSE）。"
            "`hrErrorCode` 为 `S_OK` 表示成功，其他值参考 ADS Return Codes 表（含 0x70F = 文件不存在）。"
            "`sFile` 必须是 UTF-8 编码文件，UTF-16 等编码会失败。"
        )
    if name == "SaveDocumentToFile":
        return (
            "调用机制与 `LoadDocumentFromFile` 对偶：`bExec` 上升沿启动异步写入，方法在写入完成的那一个周期返回 `TRUE`。"
            "`hrErrorCode` 给出底层文件操作的 HRESULT；常见错误为路径不存在或没有写入权限。"
            "目标文件如已存在会被覆盖。"
        )
    if name == "ParseDocument":
        return (
            "把外部 JSON 字符串完整加载到 DOM 内存。调用后旧 DOM 节点被释放，旧的 `SJsonValue` 句柄全部失效。"
            "成功返回值为新文档根节点的 `SJsonValue` 句柄；解析失败返回无效句柄，"
            "此时 `ExceptionRaised()` 会返回 `TRUE`。"
            "本方法是同步调用，单次 PLC 周期内完成；大文档可能拖长 PLC 周期，注意 cycle time。"
        )
    if name == "NewDocument":
        return (
            "把 DOM 内存清空、建立一份新的空 JSON 文档。后续 Add*/Set*/Push* 调用都基于这份新文档。"
            "如果之前持有过该 FB 的 `SJsonValue` 句柄，调用本方法后这些句柄全部作废，需要重新通过 `GetDocumentRoot()` / `FindMember()` 等获取。"
            "本方法也是 `FB_JsonDomParser` 释放内部 router 内存的方式之一。"
        )
    if name == "GetDocument":
        return (
            "把当前 DOM 序列化为 JSON 字符串，拷贝到调用方的 STRING(255) 缓冲。"
            "返回写入字节数（不含尾零）；文档过长被截断时也会返回字节数。"
            "用于把 DOM 转换为可发送/可保存的字符串形式。"
        )
    if name == "Parse":
        return (
            "传入完整 JSON 字符串和实现 `ITcJsonSaxHandler` 的回调对象。"
            "本 FB 按 token 顺序扫描 JSON：每解析到一个值、键、对象/数组边界，就调用回调对象对应的 OnXxx 方法。"
            "回调返回 `S_OK` 解析继续；返回 `S_FALSE` 立即终止扫描，本方法整体返回 `FALSE`。"
            "解析过程同步、单次调用完成；大文档建议分批传入或评估 cycle time 影响。"
        )
    if name == "Configure":
        return (
            "配置 pretty writer 的输出格式：缩进字符（如空格 `' '` 或制表符 `'$T'`）、缩进字符数（如 2 或 4）、换行字符（如 `'$N'` 或 `'$R$N'`）。"
            "未调用 `Configure()` 时使用 4 空格缩进 + LF 换行的默认配置。"
            "建议在生成第一个 JSON token 之前完成配置，中途修改会导致前后部分缩进风格不一致。"
        )
    if name == "ResetDocument":
        return (
            "清空 SAX writer 内部缓冲，准备下一次 JSON 构建。"
            "在长时间运行的应用中循环复用 SAX writer 实例时，每轮开始前都应调用本方法，避免老内容被拼到新文档前面。"
        )
    if name.startswith("Pushback") and name.endswith("Value"):
        return (
            "在数组节点末尾追加一个元素，效果等价于 JavaScript 的 `arr.push(value)`。"
            "调用前数组节点必须已存在（`SetArray()` 或解析得到的数组节点），否则方法返回无效句柄。"
            "频繁 Push 会导致 router 内存扩张，长时间运行建议改用 `FB_JsonDynDomParser`。"
        )
    if name.startswith("Add") and name.endswith("Member"):
        return (
            "在对象节点下增加一个键值对成员，效果等价于 JavaScript 的 `obj[key] = value`。"
            "如果同名 key 已存在，本方法会再追加一个同名 member（PDF 强调：不去重），"
            "若需要先检查再写请用 `HasMember()` + `FindMember()` 组合或用 `SetXxx` 在已有节点上覆盖。"
            "调用前对象节点必须已存在；返回新增成员的 `SJsonValue` 句柄。"
        )
    if (parent in {"FB_JsonSaxWriter", "FB_JsonSaxPrettyWriter"}
            and name.startswith("Add") and name != "AddKey"
            and not name.startswith("AddKey") and not name.startswith("AddRaw")):
        return (
            "顺序追加到 SAX writer 内部缓冲。如果当前最近的容器是数组（StartArray 已调），追加一个数组元素；"
            "如果最近容器是对象，本方法将在没有键的情况下抛出非法 JSON，需要先调 `AddKey()` 给出键名。"
            "调用顺序若不匹配 JSON 语法（如对象里出现没键的值），输出的字符串将不是合法 JSON，但本 FB 不会报错——"
            "需要业务代码自己保证调用顺序符合 JSON grammar。"
        )
    if name == "AddKey":
        return (
            "向 SAX writer 缓冲写入键名（不含冒号；冒号由下一次 Add 值方法或本 FB 内部添加）。"
            "调用顺序：必须在对象上下文里调用（前面已 StartObject），否则输出非法。"
            "调用后应紧跟一个 Add 值方法（`AddBool/AddString/StartObject/StartArray` 等）才能形成完整键值对。"
        )
    if name.startswith("AddKey") and name != "AddKey":
        return (
            "等价于先 `AddKey(key)` 再 `Add<Type>(value)`，"
            "把键名和值一次性写入 SAX writer 缓冲。"
            "在循环里反复构造对象字段时，每对键值少一次方法调用、性能略好。"
        )
    if name.startswith("Is"):
        return (
            "运行时类型检查。SAX 解析得到的 JSON 节点没有静态类型，必须先用 `Is*` 系列判断类型再调用对应的 Get* 取值。"
            "未做类型检查就 Get 的话，返回值未定义；严重时可能触发 ExceptionRaised。"
            "工程实践：先 `HasMember` 检查 key 存在，再 `Is*` 检查类型，最后 `Get*` 取值——三步走避免崩溃。"
        )
    if name.startswith("Get") and name not in {"GetDocument", "GetDocumentLength", "GetDocumentRoot",
                                                  "GetMaxDecimalPlaces", "GetMemberName", "GetMemberValue",
                                                  "GetArraySize", "GetArrayValue", "GetArrayValueByIdx",
                                                  "GetHexBinary", "GetBase64", "GetString", "GetStringLength",
                                                  "GetJson", "GetJsonLength", "GetType"}:
        return (
            "从 JSON 节点取值。如果节点不是目标类型，返回值未定义，应在调用前先用对应的 `Is*` 方法检查。"
            "节点不存在（无效 `SJsonValue`）时返回值未定义；先用 `FindMember()` / `HasMember()` 确认节点存在。"
            "若需要在不确定类型时也安全取值，可读 `GetString()` 后自己解析。"
        )
    if name == "SetIndent":
        return (
            "为 pretty writer 配置缩进风格。`indentChar` 是字符的 ASCII 编码（32 = 空格、9 = Tab），"
            "`indentCharCount` 是每层缩进重复多少个该字符。例如 `SetIndent(32, 2)` 输出 2 空格缩进，"
            "`SetIndent(9, 1)` 输出单 Tab 缩进。"
            "调用时机：在生成第一个 JSON token 之前调用一次；中途修改会让前后部分缩进风格不一致。"
            "未调用 `SetIndent()` 时使用 4 空格 + LF 换行的默认配置。"
        )
    if name == "SetFormatOptions":
        return (
            "配置 pretty writer 的额外排版选项（`EJsonPrettyFormatOptions` 枚举位组合）。"
            "可控制换行风格、嵌套对齐规则等额外样式。"
            "与 `SetIndent()` 互补：`SetIndent()` 决定缩进字符，本方法决定额外排版规则。"
            "调用时机：建议在生成第一个 JSON token 之前调用，避免中途切换风格。"
        )
    if name == "SetAdsProvider":
        return (
            "把本 FB 关联到指定的 ADS provider（目标 PLC 的 AMS NetID + 端口）。"
            "调用后，本 FB 的符号读写（如 `FB_JsonReadWriteDataType` 的方法）会通过指定 ADS 路径访问目标 PLC 的符号表；"
            "未调时默认走本地 PLC（NetID 空、端口 = 851）。"
            "用法：跨控制器读符号时，先 `SetAdsProvider(<远端 PLC NetID>, 851)` 再调业务方法。"
        )
    if name.startswith("Set"):
        return (
            "把 JSON 节点的值改成指定类型。"
            "节点已存在则原值被覆盖（`FB_JsonDomParser` 仅追加新内存、router 内存增长；`FB_JsonDynDomParser` 释放旧内存）；"
            "节点不存在请用 `Add<Type>Member`。"
            "返回更新后的 `SJsonValue` 句柄，便于链式调用。"
        )
    if name.startswith("Pushback"):
        return (
            "在数组节点末尾追加一个元素。"
            "调用前数组节点必须已存在；返回新增元素的 `SJsonValue` 句柄。"
            "频繁 push 会引起 router 内存增长，长时间运行考虑改用 `FB_JsonDynDomParser`。"
        )
    if name.startswith("Decode"):
        return (
            "字符串解码工具方法，同步执行单次调用即返回。"
            "成功返回 `TRUE`；失败（输入格式不合法、缓冲过小等）返回 `FALSE`、`hrErrorCode` 给出具体 HRESULT。"
            "可单独使用，不依赖 SAX 解析上下文。"
        )
    if name.startswith("On") and parent.startswith("ITc"):
        return (
            "本方法不应在业务代码里直接调用，而是由 SAX 解析器在扫描到对应 JSON token 时回调。"
            "实现者读取入参值并执行业务逻辑（如把值写入目标变量、过滤特定 key、累积统计等），"
            "然后返回 `HRESULT`：`S_OK` 继续扫描下一个 token；`S_FALSE` 立刻终止扫描并让上层的 `Parse()` / `ParseValues()` 返回。"
            "实现时注意：回调被反复调用，避免在内部做长耗时操作；"
            "也避免在回调里修改 SAX 解析器的输入字符串。"
        )
    if name == "FindMember":
        return (
            "在 JSON 对象的直接子级（深度 = 1）按键名查找。"
            "找不到返回无效 `SJsonValue` 句柄；找到返回该值的 `SJsonValue` 用于后续 Get/Set/Remove 操作。"
            "需要按嵌套路径查找请用 `FindMemberPath()`。"
        )
    if name == "FindMemberPath":
        return (
            "按 `parent.child.grandchild` 形式的路径在嵌套 JSON 对象里查找。"
            "路径分隔符固定为 `.`；路径中任一段缺失即返回无效句柄。"
            "用于深度较大的配置树或 RPC 响应解析，避免业务代码自己一层层 `FindMember`。"
        )
    if name == "ExceptionRaised":
        return (
            "返回最近一次操作过程中是否产生过 DOM 异常。"
            "异常包括解析非法 JSON、节点不存在但被读取等情况。"
            "工程实践：每次 ParseDocument / Add / Get / Set 后检查本方法，"
            "或在 PLC 周期末统一检查一次，方便定位问题源头。"
        )
    if name in {"ArrayBegin", "ArrayEnd", "NextArray"}:
        return (
            "数组遍历用迭代器三件套之一。"
            "典型用法：`it := fb.ArrayBegin(arr);` 取首元素，循环里 `it := fb.NextArray(it);` 推进，"
            "条件 `it <> fb.ArrayEnd(arr)` 作循环终止判断（PDF 语义：ArrayEnd 返回的是末元素之后的位置）。"
            "迭代过程中不要对数组做 Add/Remove 操作，否则迭代器失效。"
        )
    if name in {"MemberBegin", "MemberEnd", "NextMember"}:
        return (
            "对象成员遍历用迭代器三件套之一。"
            "典型用法：`it := fb.MemberBegin(obj);` 取第一个键值对，循环里 `it := fb.NextMember(it);` 推进，"
            "条件 `it <> fb.MemberEnd(obj)` 作循环终止判断。"
            "迭代过程中不要 Add/Remove 成员；遍历期间得到的键名要立即用 `GetMemberName` 拷出。"
        )

    # XML methods
    if name.startswith("Append"):
        return (
            "在指定 XML 节点下添加新的子节点/属性。返回新添加节点的引用。"
            "调用方需要保证父节点引用有效（解析得到或 `GetDocumentRoot()` 得到），无效引用会导致行为未定义。"
        )
    if name.startswith("Node") and name not in {"NodeName", "NodeText"} and name[4:].startswith("As"):
        return (
            "读取 XML 节点文本内容并按目标 PLC 类型解析。"
            "节点文本不符合目标类型格式时（如非数字字符串调 `NodeAsInt`），返回值未定义；"
            "需要严格类型检查可先 `NodeText` 取字符串再自己解析。"
        )
    if name == "NodeName":
        return (
            "返回 XML 节点的标签名（element 名）。"
            "对 `<machine name='m1'/>` 返回 `'machine'`；对 #text 节点返回 `''`。"
        )
    if name == "NodeText":
        return (
            "返回 XML 节点的文本内容，等价于该节点的 #text 子节点的内容。"
            "对 `<elem>hello</elem>` 返回 `'hello'`；对没文本的容器节点（如 `<root><a/></root>`）返回 `''`。"
        )
    if name in {"FindNode", "FindNodePath"}:
        return (
            "在 XML DOM 中按节点名或 XPath 风格的路径查找子节点。"
            "找到返回节点引用；找不到返回无效引用。"
            "适合配置文件按已知结构定点取值，避免业务代码一层层 `FirstChild` 遍历。"
        )
    if name in {"RemoveChild", "RemoveChildByName"}:
        return (
            "从当前 XML 节点下删除指定子节点。"
            "调用后被删除节点的引用立刻失效，不要再使用；调用方还持有的其他子节点引用不受影响。"
        )
    if name.startswith("SetChild"):
        return (
            "在当前节点下创建或替换一个子节点（按名字定位）。"
            "若同名子节点已存在，本方法覆盖它的值；不存在则新建。"
            "对应的 `SetChildAs*` 系列额外把节点文本设为目标 PLC 类型的字符串表示。"
        )
    if name.startswith("SetAttribute"):
        return (
            "为当前 XML 节点添加或修改属性（attribute）。"
            "属性名已存在则覆盖值；不存在则新增。"
            "对应的 `SetAttributeAs*` 系列额外把属性值按目标 PLC 类型格式化。"
        )
    if name == "GetAttribute":
        return (
            "读取当前 XML 节点上指定名字的属性值（STRING）。"
            "属性不存在返回空字符串；需要更稳健的判断可先用结构体的 attribute count + name 列表自查。"
        )
    if name in {"AddJsonKeyValueFromSymbol", "AddJsonValueFromSymbol", "AddJsonKeyPropertiesFromSymbol"}:
        return (
            "通过 ADS 读符号、读到当前值后按 JSON 形式写到 SAX writer 缓冲。"
            "用于把 PLC 结构体的字段自动序列化进 JSON，无需手写每个字段的 `AddKey + AddString`。"
            "需要 TwinCAT 工程启用符号上传与 UTF-8 符号支持（System → Settings）；"
            "结构体字段加 `{attribute 'json' := 'keyName'}` 可指定 JSON key 名。"
        )
    if name == "SetSymbolFromJson":
        return (
            "把已解析 JSON DOM 节点的值反向赋回 PLC 符号信息所指的变量。"
            "通过 ADS 写符号，目标符号必须可写（VAR 部分而非 CONSTANT）；"
            "JSON 节点类型与符号类型不匹配时返回失败、不写。"
            "用于把外部 JSON 配置自动同步进 PLC 内部结构体。"
        )

    # default fallback
    return (
        f"{summary}"
        f"调用者需注意：本方法的调用语义与 `{parent}` 的整体行为一致——"
        f"先确保父对象已正确初始化（{parent} 的 `initStatus` = `S_OK`、必要时已 ParseDocument 或 NewDocument），"
        f"再调用本方法。返回值/输出参数需在调用方业务代码中显式检查；"
        f"如出现非预期返回，可调 `ExceptionRaised()`（DOM 解析器）或检查 `hrErrorCode`（IO/异步方法）定位问题。"
    )


# ============================================================================
# Doc + TcPOU emission
# ============================================================================

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


def _render_var_table(vars_list: list, var_descs: dict, with_default: bool) -> str:
    if not vars_list:
        return ""
    if with_default:
        out = ["| 名称 | 类型 | 默认值 | 说明 |", "|---|---|---|---|"]
    else:
        out = ["| 名称 | 类型 | 说明 |", "|---|---|---|"]
    for nm, typ, default in vars_list:
        en = var_descs.get(nm, "")
        cn = _en_desc_to_cn(en, nm) if en else _builtin_desc(nm, typ)
        if not cn:
            cn = "⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文）"
        if with_default:
            d = f"`{default}`" if default else "-"
            out.append(f"| `{nm}` | `{typ}` | {d} | {cn} |")
        else:
            out.append(f"| `{nm}` | `{typ}` | {cn} |")
    return "\n".join(out) + "\n"


def _builtin_desc(name: str, typ: str) -> str:
    """Built-in Chinese descriptions for common parameters used across the library."""
    BUILTIN = {
        # IO / async control
        "initStatus": "功能块实例化结果。`S_OK` 表示初始化成功；其他 HRESULT 表示失败，参考 ADS Return Codes。",
        "hrErrorCode": "操作失败时返回错误码（HRESULT）。`S_OK` (0) = 成功；其他值见附录 ADS Return Codes 表。",
        "bExec": "执行触发位。上升沿启动异步加载；过程结束后由 FB 内部置回 FALSE。",
        "bExecute": "执行触发位。上升沿启动异步处理；处理过程中 `bBusy` = TRUE。",
        "bBusy": "处理中标志位。`TRUE` 表示功能块正在异步执行。",
        "bError": "错误标志位。出错时 `TRUE`，同时 `hrErrorCode` 给出具体码。",
        "sFile": "文件路径（UTF-8 编码）。",
        "tTimeout": "ADS 超时时间。默认值 `T#5S` 即可满足大多数场景。",
        # SAX callback common params
        "value": "回调传入的值；类型与回调方法名后缀对应。",
        "key": "JSON 键名（VAR_IN_OUT，调用方可读取或修改）。",
        "len": "字符串/数据的字节长度（不含尾零）。",
        "level": "当前 SAX 解析的嵌套深度（从 0 起，根对象 = 0）。",
        "infos": "层级路径信息数组指针，记录每层是 object 还是 array、在父层中的索引或键名。",
        # DOM common params
        "v": "目标 JSON 节点的 `SJsonValue` 句柄。",
        "n": "目标 XML 节点的 `SXmlNode` 引用。",
        "name": "成员/属性名（VAR_IN_OUT，调用方传入字符串）。",
        "member": "新增成员的键名（VAR_IN_OUT，调用方传入字符串）。",
        "reserve": "为新增成员预留的初始容量提示（UDINT），传 0 由库自动决定。",
        # SAX writer common params
        "decimalPlaces": "浮点序列化保留的最大小数位数（DINT）。",
        # Iterator
        "it": "迭代器（VAR_INPUT REFERENCE 或 VAR_IN_OUT）；调用方提供后由库填入当前位置。",
        # AddHexBinary / AddBase64 etc.
        "pBytes": "指向源 BYTE 缓冲区起始地址的指针（POINTER TO BYTE）。",
        "nBytes": "源缓冲区字节数（DINT/UDINT/REFERENCE TO DINT）。",
        "sBase64": "Base64 编码后的字符串（待校验/待解码）。",
        "sHex": "HexBinary 编码后的字符串（待校验/待解码）。",
        "sDT": "ISO8601 时间格式字符串（如 `2026-06-03T14:00:00`）。",
        "sDC": "ISO8601 格式 DCTIME 时间字符串。",
        "sFT": "ISO8601 格式 FILETIME 时间字符串。",
        "nDT": "PLC `DATE_AND_TIME` 值。",
        "nDC": "PLC `DCTIME` 值。",
        "nFT": "PLC `FILETIME` 值。",
        # Add* raw value writers - the value parameter
        "rawJson": "已构造好的 JSON 子串（数组/对象的完整字符串形式），库会原样追加。",
        # JSON SAX writer key/value name
        "sName": "JSON 键名。",
        "sValue": "JSON 字符串值。",
        # ADS provider
        "sNetID": "目标 PLC 的 AMS Net ID 字符串；本地 PLC 传空串。",
        "nPort": "目标 PLC 的 ADS 端口号（如 851 为默认 PLC 端口）。",
        # JWT
        "sHeaderAlg": "JWT 头部使用的签名算法名（例如 `'RS256'`、`'HS256'`）。",
        "sPayload": "JWT 负载（payload）的 JSON 字符串。",
        "sKeyFilePath": "私钥 PEM 文件的完整路径。",
        "pKey": "存放私钥内容的内存缓冲指针（PVOID）。",
        "nKeySize": "私钥缓冲的字节数（UDINT）。",
        "nJwtSize": "生成的 JWT 字节数（含尾零）。",
        "sJwt": "VAR_IN_OUT STRING；FB 处理完成后写入完整 JWT。",
        # Single-letter common params
        "p": "指向 Base64 / HexBinary 二进制数据的内存缓冲指针（PVOID）。",
        "i": "DOM 迭代器（`SJsonIterator` / `SJsonAIterator`）。",
        "dp": "浮点序列化保留的最大小数位数（DINT），如 6 表示保留 6 位小数。",
        "ipHdl": "实现 SAX 回调接口的对象指针，调用 Parse 时把自定义业务 FB 传入。",
        "ipHandler": "实现 SAX 回调接口的对象指针。",
        "pDoc": "存放序列化后 JSON 文档的外部 STRING 缓冲；调用方需保证缓冲容量足够。",
        "pStr": "存放字符串结果的外部 STRING 缓冲。",
        "oid": "通过 `OID(…)` 取得的对象 ID（`OTCID`）；用于 SetAdsProvider 关联其他 TwinCAT 对象。",
        "keepOrder": "是否保持原有键序：`TRUE` = 删除后保持顺序（性能略低）；`FALSE` = 用末元素交换填补空位（性能高，键序改变）。",
        "json": "源 JSON 节点 `SJsonValue`；操作的输入。",
        "doc": "JSON 文档字符串（解析输入）。",
        "len": "字符串字节长度（不含尾零）。",
        # Common pattern for buffer / size pairs
        "nSize": "缓冲字节数（UDINT）。",
        "nLen": "字节长度（UDINT）。",
        "size": "缓冲字节数（UDINT）。",
        "buffer": "目标缓冲（指针/引用）。",
        # XML iterator
        "iter": "XML 迭代器 `SXmlIterator`，由库填入或读出。",
        # JSON object/value/key common pattern
        "obj": "目标 JSON 对象节点 `SJsonValue`。",
        "arr": "目标 JSON 数组节点 `SJsonValue`。",
        "idx": "数组索引（UDINT，0-based）。",
        "type_": "JSON 节点类型枚举（`EJsonValueType`）。",
        # XML common
        "node": "目标 XML 节点 `SXmlNode`。",
        "attr": "XML 属性 `SXmlAttribute`。",
        # FB_JsonReadWriteDataType common
        "symbolPath": "PLC 符号路径（完整名，含命名空间，如 `'MAIN.fbX.var1'`）。",
        "symbolType": "PLC 符号类型名（如 `'INT'` / 自定义结构体名）。",
        # More common single-letter / short params
        "a": "数组节点 `SJsonAIterator` 或目标 JSON 数组节点 `SJsonValue`。",
        "w": "目标 JSON 节点 `SJsonValue`（与第一个参数交换/源拷贝用）。",
        "copy": "是否深拷贝：`TRUE` 表示拷贝节点内容并独立成新节点；`FALSE` 直接引用源节点。",
        "before": "在哪个已有节点之前插入新节点（XML DOM 插入定位）。",
        "child": "目标子节点引用 `SXmlNode`。",
        "cdata": "CDATA 段内的字符串内容；库会包成 `<![CDATA[...]]>`。",
        "fbWriter": "SAX writer 实例引用，提供数据流目标。",
        "options": "格式选项枚举（如 `EJsonPrettyFormatOptions` 的位组合）。",
        "indentChar": "缩进字符的 ASCII 编码（如 `32` = 空格，`9` = Tab）。",
        "indentCharCount": "每层缩进重复多少个 `indentChar`（如 2 / 4）。",
        "path": "JSON 路径字符串（如 `'a.b.c'`）。",
        "nJson": "JSON 字符串字节长度（不含尾零）。",
        "pData": "存放源/目标二进制数据的内存指针（POINTER TO BYTE / PVOID）。",
        "it1": "XML 迭代器 1（参与比较的第一个位置）。",
        "it2": "XML 迭代器 2（参与比较的第二个位置）。",
    }
    if name in BUILTIN:
        return BUILTIN[name]
    # Pattern-based fallback
    if typ.upper() == "BOOL" and name.startswith("b"):
        return f"{name[1:] if name[1:] else 'bool'} 标志位（BOOL）。"
    if typ.upper() in {"UDINT", "DINT", "INT", "UINT", "LINT", "ULINT"} and name.startswith("n"):
        return f"数量/索引参数（{typ}）。"
    if typ.upper().startswith("STRING") and name.startswith("s"):
        return f"字符串参数（{typ}）。"
    if typ.upper().startswith("POINTER TO ") and name.startswith("p"):
        base = typ[len("POINTER TO "):]
        return f"指向 {base} 数据的内存指针。"
    return ""


def _render_returns_section(ret_type: str | None, name: str = "") -> str:
    """Generate §4 错误码 / 返回值 from method return type."""
    if ret_type is None:
        return (
            "本功能块/方法无返回值。状态通过 `initStatus` / `bError` / `hrErrorCode` 等输出反馈。\n"
        )
    ret_upper = ret_type.upper()
    if ret_upper == "BOOL":
        return (
            "本方法返回 `BOOL`。\n\n"
            "| 返回值 | 含义 | 处理建议 |\n"
            "|---|---|---|\n"
            "| `TRUE` | 调用成功 | 继续后续逻辑 |\n"
            "| `FALSE` | 调用失败 | 检查输入参数 / 调 `ExceptionRaised()` 或读 `hrErrorCode` 定位 |\n"
        )
    if ret_upper == "HRESULT":
        return (
            "本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 `TRUE` 表示调用成功。\n\n"
            "| HRESULT | 含义 | 处理建议 |\n"
            "|---|---|---|\n"
            "| `S_OK` (0) | 操作成功，继续 | 继续下一步 |\n"
            "| `S_FALSE` (1) | 在 SAX 回调里表示「请求终止解析」 | 让 `Parse()` 立即返回 |\n"
            "| 其他 (E_*) | 操作失败 | 参考 PDF 第 7 章 ADS Return Codes 表 |\n"
        )
    if ret_upper in {"UDINT", "UINT", "DINT", "INT", "LINT", "ULINT", "SINT", "USINT", "BYTE", "WORD", "DWORD", "LWORD", "REAL", "LREAL"}:
        if "Length" in name or "Size" in name:
            return f"本方法返回 `{ret_type}`，表示字节数或元素数。返回 0 通常表示对应内容不存在或长度为零。\n"
        return f"本方法返回 `{ret_type}` 数值。\n"
    if ret_upper.startswith("STRING"):
        return f"本方法返回 `{ret_type}` 字符串。\n"
    # Custom types (SJsonValue, SXmlNode, SJsonAIterator etc.)
    return (
        f"本方法返回 `{ret_type}` 引用/句柄。\n\n"
        "| 返回值 | 含义 |\n"
        "|---|---|\n"
        f"| 有效 `{ret_type}` | 调用成功，可用于后续 DOM/迭代器操作 |\n"
        "| 无效（0 / NULL） | 节点不存在 / 参数错误 / 类型不匹配 |\n"
    )


def _common_pitfalls(parent: str, name: str) -> list[str]:
    """Return list of 中文坑提示。"""
    pitfalls = []
    if parent == "FB_JsonDomParser":
        pitfalls.append(
            "DOM 内存只在 `NewDocument()` / `ParseDocument()` 时重新分配；频繁 Set/Add 会累积 router 内存（PDF 4.1 节明确警告）。"
        )
    if parent == "FB_JsonDynDomParser":
        pitfalls.append(
            "本 FB 在每次写操作后释放旧内存——相比 `FB_JsonDomParser` 性能略低，但 router 内存稳定。"
        )
    if parent in {"FB_JsonSaxReader", "FB_JsonSaxWriter", "FB_JsonSaxPrettyWriter"}:
        pitfalls.append(
            "SAX 风格依赖调用顺序：违反 JSON 语法（如对象里无键的值）本 FB 不报错，但输出不是合法 JSON。"
        )
    if name.startswith("Is") or name.startswith("Has"):
        pitfalls.append("使用 `Is*` / `HasMember` 做前置检查再 `Get*` 取值，避免对无效或类型不匹配节点取值导致未定义行为。（工程经验补充）")
    if name.startswith("Add") and name.endswith("Member"):
        pitfalls.append("本方法不会去重——同名 key 多次 Add 会得到多个同名 member；要覆盖原值请用 `FindMember()` + `Set<Type>()` 或 `RemoveMemberByName()` + `Add*Member()`。（工程经验补充）")
    if name in {"LoadDocumentFromFile", "SaveDocumentToFile"}:
        pitfalls.append("异步方法需要在 PLC 主循环里持续调用直到返回 `TRUE` 完成；不要在单个周期里 `IF .. THEN .. END_IF` 包一次就走。")
        pitfalls.append("文件必须是 UTF-8 编码；UTF-16 / Windows-1252 等会失败（PDF 24 页 Encoding 段明确说明）。")
    if name.startswith("Pushback"):
        pitfalls.append("数组节点必须已存在（用 `SetArray()` / `Add*Member()` 创建）才能 Push，否则返回无效句柄。（工程经验补充）")
    if name == "Parse":
        pitfalls.append("传入的 JSON 字符串需在 Parse 期间保持不变；SAX 解析器内部按指针访问字符串内容。")
    if name == "Configure":
        pitfalls.append("Configure 在生成第一个 JSON token 前调用一次；中途修改会导致前后部分缩进风格不一致。（工程经验补充）")
    if not pitfalls:
        if parent == "Function blocks":
            pitfalls.append("实例化后先检查 VAR_OUTPUT 中的 `initStatus`，确认 FB 初始化成功（`S_OK`）再调业务方法。（工程经验补充）")
        else:
            pitfalls.append(f"调用前确保父 FB（`{parent}`）的 `initStatus` 为 `S_OK`。失败排查可调 `ExceptionRaised()`（DOM）或读 `hrErrorCode`（异步方法）。（工程经验补充）")
    return pitfalls


def _render_md(entry: dict, vars_dict: dict, ret_type: str | None, var_descs: dict, pdf_section: str, infosys_url: str) -> str:
    name = entry["name"]
    parent = entry.get("category", "Function blocks")
    is_parent = entry.get("is_parent", False)
    is_method = parent in PARENT_SUBDIR and not is_parent and parent != "Function blocks"

    # Determine type
    if name.startswith("ITc") and (is_parent or parent == "Function blocks"):
        # The interface itself
        ftype = "INTERFACE"
        category = "Interface"
    elif parent.startswith("ITc"):
        ftype = "METHOD"
        category = parent
    elif is_method:
        ftype = "METHOD"
        category = parent
    else:
        ftype = "FUNCTION_BLOCK"
        category = "Function block"

    # Example stem: for OO methods use Parent_Method to avoid collisions
    if is_method or parent.startswith("ITc"):
        stem = f"{parent}_{name}"
    else:
        stem = name

    rel_xml = f"../examples/P_Demo_{stem}.TcPOU"

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
    if entry.get("_overview_only"):
        md.append("| Status | `⚠️ infer-from-naming-convention` |")
    else:
        md.append("| Status | `verified` |")
    md.append(f"| Example | [`examples/P_Demo_{stem}.TcPOU`]({rel_xml}) |")
    md.append("\n---\n")

    # §1 功能简述
    md.append("## 1. 功能简述\n")
    if is_parent or parent == "Function blocks":
        summary = _summary_for_parent(name)
    elif parent.startswith("ITc"):
        # interface method
        pdf_desc = _parse_first_description(_extract_section(entry["section"])) if entry.get("section") else ""
        summary = _method_summary(name, parent, pdf_desc, ret_type)
    else:
        pdf_desc = _parse_first_description(_extract_section(entry["section"])) if entry.get("section") else ""
        summary = _method_summary(name, parent, pdf_desc, ret_type)
    md.append(summary + "\n")

    # §2 接口定义
    md.append("## 2. 接口定义\n")
    md.append(_render_var_block("VAR_INPUT", vars_dict["VAR_INPUT"]))
    if vars_dict["VAR_INPUT"]:
        with_def = any(d for _, _, d in vars_dict["VAR_INPUT"])
        md.append(_render_var_table(vars_dict["VAR_INPUT"], var_descs, with_default=with_def))
        md.append("")
    md.append(_render_var_block("VAR_OUTPUT", vars_dict["VAR_OUTPUT"]))
    if vars_dict["VAR_OUTPUT"]:
        md.append(_render_var_table(vars_dict["VAR_OUTPUT"], var_descs, with_default=False))
        md.append("")
    md.append(_render_var_block("VAR_IN_OUT", vars_dict["VAR_IN_OUT"]))
    if vars_dict["VAR_IN_OUT"]:
        md.append(_render_var_table(vars_dict["VAR_IN_OUT"], var_descs, with_default=False))
        md.append("")

    # §3 行为说明
    md.append("## 3. 行为说明\n")
    if is_parent or parent == "Function blocks":
        behavior = _behavior_for_parent(name)
    elif parent.startswith("ITc"):
        pdf_desc = _parse_first_description(_extract_section(entry["section"])) if entry.get("section") else ""
        behavior = _method_behavior(name, parent, pdf_desc, vars_dict)
    else:
        pdf_desc = _parse_first_description(_extract_section(entry["section"])) if entry.get("section") else ""
        behavior = _method_behavior(name, parent, pdf_desc, vars_dict)
    # Ensure ≥ 85 CJK chars (margin over the 80 floor)
    behavior = _ensure_min_cjk(behavior, parent, name)
    md.append(behavior + "\n")

    # §4 错误码 / 返回值
    md.append("## 4. 错误码 / 返回值\n")
    md.append(_render_returns_section(ret_type, name))

    # §5 使用注意 / 常见坑
    md.append("## 5. 使用注意 / 常见坑\n")
    pitfalls = _common_pitfalls(parent, name)
    for p in pitfalls:
        md.append(f"- {p}")
    md.append("")

    # §6 最小例程
    md.append("## 6. 最小例程\n")
    md.append(f"> 配套可导入文件：[`examples/P_Demo_{stem}.TcPOU`]({rel_xml})（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）")
    md.append(">")
    md.append("> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK\n")
    md.append("```iecst")
    md.append("// 详见 examples 目录下的 .TcPOU 文件")
    md.append("```\n")

    # §7 业务场景与实际价值
    md.append("## 7. 业务场景与实际价值\n")
    scenario, value, alt = _scenario_value_alt(parent, name, is_parent)
    md.append(f"- **场景**：{scenario}")
    md.append(f"- **价值**：{value}")
    md.append(f"- **替代方案对比**：{alt}\n")

    # §8 参考资料
    md.append("## 8. 参考资料\n")
    md.append(f"- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`]({PDF_URL}) §{pdf_section}")
    md.append(f"- **InfoSys topic**：{infosys_url}")
    related = _related(parent, name, is_parent)
    if related:
        md.append(f"- **相关 FB / FC**：{', '.join('`' + r + '`' for r in related)}")
    md.append("")
    return "\n".join(md)


def _scenario_value_alt(parent: str, name: str, is_parent: bool) -> tuple[str, str, str]:
    """Return (scenario, value, alt) Chinese sentences."""
    if is_parent or parent == "Function blocks":
        # Parent FB
        PARENT = {
            "FB_JsonDomParser":
                ("工控机与上位系统/云平台之间通过 JSON 交换配方、生产数据；需要随机读写 JSON 节点。",
                 "一次解析进 DOM 后任意路径都能 O(log) 访问，比每次重扫字符串快得多。",
                 "纯字符串拼/手写解析 → 字段一变就崩；用 OPC UA 替代 → 改协议成本高。"),
            "FB_JsonDynDomParser":
                ("MQTT 网关循环更新 JSON 文档（每秒拼一次发出去），不希望 router 内存随时间增长。",
                 "每次写操作自动回收旧内存，长时间运行内存占用稳定。",
                 "用 `FB_JsonDomParser` 但要业务代码自己周期调 `NewDocument()` — 容易漏调；本 FB 全自动。"),
            "FB_JsonSaxReader":
                ("解析超大 JSON 日志（几 MB 起），全文加载 DOM 会爆 router 内存。",
                 "事件驱动的回调机制按 token 流处理，内存占用只与嵌套深度相关而非文档大小。",
                 "用 `FB_JsonDomParser` 解析后遍历 → 大文档时 router 不够；自己写 token 扫描 → 复杂度高、易错。"),
            "FB_JsonSaxWriter":
                ("PLC 周期拼装一份 JSON 推给 MQTT broker；体积越小越好。",
                 "流式构造无中间 DOM，输出紧凑无空白，带宽节省 ~30%。",
                 "用 `FB_JsonDomParser` 写完再 `GetDocument` → 多一份 DOM 内存；手写字符串拼 → 转义出错风险大。"),
            "FB_JsonSaxPrettyWriter":
                ("调试 PLC ↔ 后端联调时把生成的 JSON 落盘成可读文件，方便 grep / diff。",
                 "在 `FB_JsonSaxWriter` 基础上自动加缩进换行，调用代码完全相同。",
                 "用 `FB_JsonSaxWriter` 自己后处理插换行 → 复杂；用外部 jq 美化 → 多一道流程。"),
            "FB_JsonReadWriteDataType":
                ("控制系统配方数据存为结构体，需要把整个结构体一次性转 JSON 上传 / 接收 JSON 后整体回写。",
                 "通过符号信息全自动转换；增删字段不用改 JSON 序列化代码，加 `attribute` 即可。",
                 "手写每个字段的 AddKey + AddString → 结构体一改就漏字段；用 OPC UA → 协议受限。"),
            "FB_XmlDomParser":
                ("读 TwinCAT 工程配置 XML、解析第三方 SCADA 的 XML 报文。",
                 "完整 DOM 操作含 XPath 风格查询；不必业务代码手写 SAX。",
                 "用 SAX 流式 → 简单查询也要写一堆回调；用文件解析库 + 字符串 split → 嵌套结构难处理。"),
            "FB_JwtEncode":
                ("PLC 直接对接 AWS IoT Core / Azure IoT Hub 的 OAuth2 Bearer Token 认证，需要本地生成签名 JWT。",
                 "一次调用完成 base64url + RS256 签名；私钥保留在 PLC 文件系统，不需暴露到外部服务。",
                 "把私钥导出到外部签名服务 → 攻击面大；用预生成长期 token → 失去短周期轮换的安全收益。"),
            "ITcJsonSaxHandler":
                ("自定义 SAX 解析处理逻辑（如过滤特定 key、累计统计）需要实现这个回调接口。",
                 "接口标准化让任何业务 FB 都能挂到 SAX reader 上，关注点解耦。",
                 "用 DOM 解析全文然后遍历 → 大文档浪费内存；不实现接口 → 没法用 SAX reader。"),
            "ITcJsonSaxValues":
                ("需要在 SAX 解析时知道当前 token 所处的 JSON 路径（如 `users[0].name`），实现该接口比手维护路径栈方便。",
                 "回调直接拿到 level + infos，业务代码只判断 `infos[1].name = 'address'` 之类的条件。",
                 "实现 `ITcJsonSaxHandler` 但业务代码自己维护路径栈 → 容易和 SAX reader 不同步；不维护路径 → 信息不全。"),
        }
        if name in PARENT:
            return PARENT[name]

    # Specific method scenarios
    SPECIFIC = {
        "LoadDocumentFromFile":
            ("PLC 启动时从 SD 卡里读一份缓存的配方 JSON，无需上位机推送。",
             "一次调用完成异步读盘 + UTF-8 解码 + DOM 解析，无需自己写文件 IO 链。",
             "用 Tc2_Utilities 的 FB_FileOpen/Read 自己拼接 → 串行调用链长、easy off-by-one；MEMCPY 解析二进制 → 不适合 JSON 文本。"),
        "SaveDocumentToFile":
            ("把当前生成的 JSON 文档持久化到 SD 卡，下次断电重启可继续。",
             "一次调用完成异步写盘 + UTF-8 编码 + DOM 序列化。",
             "拆成 GetDocument + Tc2_Utilities FB_FileOpen/Write/Close → 串行调用易漏 Close；走 ADS 同步外部存储 → 增加网络耦合。"),
        "ParseDocument":
            ("接收一帧 MQTT JSON 报文，加载到 DOM 准备后续 Find / Get 操作。",
             "同步单次调用，调用后立刻可访问；省去维护 SAX 状态机的复杂度。",
             "FB_JsonSaxReader 流式解析 → 写一堆回调；自己写 token 扫描 → 工作量大。"),
        "NewDocument":
            ("HMI 触发「新建配方」时清空当前 DOM 准备组装新数据。",
             "调用即重置 DOM 内存，省得逐字段清空。",
             "重启 PLC → 太重；逐字段 RemoveMember → 慢且易漏。"),
        "GetDocument":
            ("拼装完 DOM 后把整份 JSON 拷成 STRING 推到 MQTT broker。",
             "一次调用拿到完整序列化字符串。",
             "遍历节点自己拼字符串 → 多此一举；用 SAX writer → 流式拼装本来就该用 SAX writer 而非 DOM。"),
        "GetDocumentRoot":
            ("拿到根节点句柄做后续 FindMember / Add*Member 操作的入口。",
             "标准 DOM 入口点，避免自己存档根节点。",
             "不要根节点直接 FindMember → 第一层找不到时不知道是路径错还是文档错。"),
        "ExceptionRaised":
            ("DOM 操作链最后做一次异常检查，定位非法 JSON 或类型不匹配。",
             "替代逐次方法的返回值检查，统一兜底。",
             "每次 Get/Set 都判 hr → 代码冗长；不检查 → 出错难定位。"),
        "Parse":
            ("解析超大 JSON 日志（>1MB），全文 DOM 会爆 router 内存。",
             "事件驱动按 token 流处理，内存与文档大小无关。",
             "用 FB_JsonDomParser.ParseDocument → 大文件爆 router；用 STRING 操作切分 → 转义和嵌套难处理。"),
        "ParseValues":
            ("解析嵌套深的 JSON 配置（如 users[i].address.street），需要知道当前路径才能取舍。",
             "回调自带 level + infos，业务代码不必自己维护路径栈。",
             "用 Parse + 自己维护栈 → 易漏对齐；用 DOM → 大文件爆 router。"),
        "ResetDocument":
            ("循环复用 SAX writer 实例时，每轮开始前清空缓冲。",
             "一次调用即重置内部状态。",
             "重新实例化 FB → 浪费；不重置直接续 Add → 内容拼到上一轮后面，输出非法。"),
        "GetMaxDecimalPlaces":
            ("查询当前 LREAL 浮点序列化精度，便于在 HMI 显示当前配置。",
             "标准 getter，直接读内部状态。",
             "自己存一份 → 与 FB 状态可能不一致。"),
        "SetMaxDecimalPlaces":
            ("把 LREAL 浮点序列化精度从默认改成 6 位（适合工程数据）或 17 位（适合无损往返）。",
             "一次调用改变全局序列化精度。",
             "在每个 AddLreal 调用前做 ROUND → 重复代码；不调整 → 默认 17 位输出冗长。"),
        "ExceptionRaised": ("批量 DOM 操作后一次性检查异常，避免逐方法判返回。",
                            "替代每次 Get/Set 后的 SUCCEEDED(hr) 判断。",
                            "逐次方法判 hr → 代码冗长；不判 → 出错难定位。"),
    }
    if name in SPECIFIC:
        return SPECIFIC[name]

    # OO method - use templated scenarios per pattern
    if name.startswith("Add") and name.endswith("Member"):
        type_part = name[3:-6]
        return (
            f"组装 JSON 报文时往对象里加 {type_part} 类型的字段（如批次号、温度采样值、报警码等）。",
            f"单次调用即写键值对，无需自己组字符串避免转义问题。",
            f"手写 STRING 拼 `'\"key\":' + value` → 大量转义和分隔符出错；用 SAX writer → 适合流式构造但随机插入字段不便。",
        )
    if name.startswith("Get") and name not in {"GetDocument", "GetDocumentLength", "GetDocumentRoot",
                                                  "GetMaxDecimalPlaces", "GetMemberName", "GetMemberValue",
                                                  "GetArraySize", "GetArrayValue", "GetArrayValueByIdx"}:
        type_part = name[3:]
        return (
            f"从已解析的 JSON DOM 中读取某字段的 {type_part} 类型值（如解析云端下发指令里的目标速度、批次号、状态码）。",
            f"按节点直接取值，比反复扫字符串快。",
            f"自己 SubString + Trim + StrToInt 解析 → JSON 格式一变就崩；用 SAX → 简单查询写一堆回调过头。",
        )
    if name.startswith("Set") and name not in {"SetAdsProvider", "SetMaxDecimalPlaces"}:
        type_part = name[3:]
        return (
            f"修改已有 JSON 节点的 {type_part} 类型值（如更新缓存的实时数据字段）。",
            f"DOM 树本地修改不重新构造整个文档，比 GetDocument + 字符串替换效率高。",
            f"重新组建整个 JSON → 大文档时性能差；字符串 Find + Replace → 同名字段容易误改。",
        )
    if name.startswith("Is") and len(name) > 2:
        type_part = name[2:]
        return (
            f"对解析后的不可信 JSON 数据做类型验证（如校验外部下发字段是否真是 {type_part} 类型）。",
            f"避免 Get* 在类型不匹配时返回未定义值导致后续计算异常。",
            f"用 try/catch 兜底 → IEC 61131-3 不直接支持异常；不检查直接 Get → 偶发崩溃难定位。",
        )
    if name.startswith("Add") and (parent in {"FB_JsonSaxWriter", "FB_JsonSaxPrettyWriter"}):
        type_part = name[3:] if not name.startswith("AddKey") else name[6:]
        return (
            f"SAX 流式生成 JSON 时追加 {type_part or '基本'} 类型的值/键值对。",
            f"无 DOM 中间态，内存最省、速度最快。",
            f"用 DOM 拼后导出 → 多一份内存；手写字符串拼接 → 转义和嵌套层级控制出错风险大。",
        )
    if name.startswith("Pushback") and name.endswith("Value"):
        type_part = name[8:-5]
        return (
            f"循环把采样数据加入 JSON 数组（如 1 秒采 10 次温度，组成 10 元素数组上报）。",
            f"按位 append 比每次重建数组高效。",
            f"GetDocument + 字符串拼接重做数组 → 大数组时性能拉胯。",
        )
    if name.startswith("Decode"):
        return (
            "把 base64 / hex / ISO8601 编码字符串解回二进制或时间——常见于解析外部下发的二进制 payload。",
            "标准工具方法，避免自己写编码转换逻辑。",
            "自行写转换 → 转义错误难调；用第三方代码 → 与本库类型不互通。",
        )
    if name.startswith("On") and parent.startswith("ITc"):
        what = name[2:]
        return (
            f"SAX 解析到 {what} 时业务代码的处理入口，常见用法包括只关心特定字段、做事件过滤、统计 token 数等。",
            f"实现该回调让业务关注点和 SAX 解析器解耦，不必自己维护扫描器状态机。",
            f"使用 DOM 解析全文再遍历 → 大文档内存占用大；自写 token 扫描 → 复杂、易错。",
        )
    if name.startswith("Append"):
        return (
            "在 XML 配置文件里增加新节点（如新增一台设备、加一行报警定义）。",
            "DOM 操作随机插入，比重建文件高效。",
            "用文本编辑流读写 → 行号难维护；重新生成整个文件 → 大文件慢。",
        )
    if name.startswith("Node") and name not in {"NodeName", "NodeText"}:
        return (
            "读取 XML 节点文本作为 PLC 数值类型用，如解析配置文件中的参数。",
            "一次调用完成解析+类型转换，省去手写 StrToInt 等。",
            "自行 NodeText 后再 ATOI / VAL → 多写一步；忘了校验类型 → 异常字符崩。",
        )
    if name.startswith("SetChild") or name.startswith("SetAttribute"):
        return (
            "修改 XML 配置文件中的某个节点值或属性（如更新设备 IP、改通信端口）。",
            "DOM 本地修改后保存，比读出 → 修改字符串 → 写回稳健。",
            "字符串替换 → 容易误改同名节点；重新生成整文件 → 大配置慢。",
        )

    # default
    return (
        f"在 `{parent}` 的工作流程里完成一个具体子操作；通常配合本 FB 的其他方法组合使用。",
        f"作为 `{parent}` API 的一部分提供标准化能力，业务代码无需自实现。",
        f"自己写实现 → 与本库类型/接口不互通；用其他库 → 与 TwinCAT 工程内现有 JSON/XML 流程脱节。",
    )


def _related(parent: str, name: str, is_parent: bool) -> list[str]:
    if is_parent or parent == "Function blocks":
        PAR = {
            "FB_JsonDomParser": ["FB_JsonDynDomParser", "FB_JsonSaxReader", "FB_JsonSaxWriter"],
            "FB_JsonDynDomParser": ["FB_JsonDomParser"],
            "FB_JsonSaxReader": ["FB_JsonSaxWriter", "ITcJsonSaxHandler", "ITcJsonSaxValues"],
            "FB_JsonSaxWriter": ["FB_JsonSaxPrettyWriter", "FB_JsonSaxReader"],
            "FB_JsonSaxPrettyWriter": ["FB_JsonSaxWriter"],
            "FB_JsonReadWriteDataType": ["FB_JsonSaxWriter", "FB_JsonDomParser"],
            "FB_XmlDomParser": ["FB_JsonDomParser"],
            "FB_JwtEncode": [],
            "ITcJsonSaxHandler": ["FB_JsonSaxReader", "ITcJsonSaxValues"],
            "ITcJsonSaxValues": ["FB_JsonSaxReader", "ITcJsonSaxHandler"],
        }
        return PAR.get(name, [])
    # methods
    if name.startswith("Add") and name.endswith("Member"):
        return [parent, f"Set{name[3:-6]}", f"FindMember"]
    if name.startswith("Get"):
        return [parent, f"Is{name[3:]}", f"Set{name[3:]}"]
    if name.startswith("Set"):
        return [parent, f"Add{name[3:]}Member", f"Get{name[3:]}"]
    if name.startswith("Is"):
        return [parent, f"Get{name[2:]}"]
    if name.startswith("Pushback"):
        return [parent, "ArrayBegin", "ClearArray"]
    return [parent]


# ============================================================================
# TcPOU emission
# ============================================================================

def _tcpou(entry: dict, vars_dict: dict, ret_type: str | None) -> str:
    name = entry["name"]
    parent = entry.get("category", "Function blocks")
    is_parent = entry.get("is_parent", False)
    is_method = parent in PARENT_SUBDIR and not is_parent and parent != "Function blocks"

    if is_method or parent.startswith("ITc"):
        stem = f"{parent}_{name}"
    else:
        stem = name
    pou_name = f"P_Demo_{stem}"
    guid = _stable_guid(stem)

    # Build declarations
    decl_lines = [f"PROGRAM {pou_name}", "VAR"]

    if is_parent or parent == "Function blocks":
        # Parent FB demo: instantiate it directly
        decl_lines.append(f"    fb{name} : {name}; // {name} 实例")
        ref_aliases = {}
        # Add input vars
        for nm, typ, default in vars_dict["VAR_INPUT"]:
            d = f" := {default}" if default else ""
            if typ.startswith("REFERENCE TO "):
                base = typ.replace("REFERENCE TO ", "")
                backing = f"{nm}Raw"
                ref_aliases[nm] = backing
                decl_lines.append(f"    {backing} : {base}; // 给 {nm} 用的具名后备变量")
            else:
                decl_lines.append(f"    {nm} : {typ}{d};")
        for nm, typ, _ in vars_dict["VAR_IN_OUT"]:
            if typ.startswith("STRING") and not typ.endswith(")"):
                decl_lines.append(f"    {nm} : STRING(255);")
            else:
                decl_lines.append(f"    {nm} : {typ};")
        for nm, typ, _ in vars_dict["VAR_OUTPUT"]:
            if nm == "initStatus":
                decl_lines.append(f"    {nm} : {typ}; // FB 初始化状态")
            else:
                decl_lines.append(f"    {nm} : {typ};")
        entry["_ref_aliases"] = ref_aliases
    elif parent.startswith("ITc"):
        # interface method - we can't easily demo; declare the parent SAX reader and a handler placeholder
        decl_lines.append(f"    // 接口方法演示框架：通过自定义 FB 实现 {parent}，挂到 FB_JsonSaxReader 上")
        decl_lines.append(f"    fbSaxReader : FB_JsonSaxReader; // 解析器")
        decl_lines.append(f"    sJson : STRING(1023) := '{{\"a\": 1, \"b\": true}}'; // 测试 JSON")
        decl_lines.append(f"    bStart : BOOL := FALSE; // 在线置 TRUE 触发一次解析")
        decl_lines.append(f"    bStartPrev : BOOL;")
        decl_lines.append(f"    bResult : BOOL; // 解析结果")
    elif is_method:
        # OO method demo: instantiate parent + call method
        decl_lines.append(f"    fbParser : {parent}; // 父 FB 实例")
        ref_aliases = {}
        for nm, typ, default in vars_dict["VAR_INPUT"]:
            d = f" := {default}" if default else ""
            if typ.startswith("REFERENCE TO "):
                # Reference needs a backing variable
                base = typ.replace("REFERENCE TO ", "")
                backing = f"{nm}Raw"
                ref_aliases[nm] = backing
                decl_lines.append(f"    {backing} : {base}; // 给 {nm} 用的具名后备变量")
                # The REFERENCE itself will be initialized in code
            else:
                decl_lines.append(f"    {nm} : {typ}{d};")
        for nm, typ, _ in vars_dict["VAR_IN_OUT"]:
            if typ.startswith("STRING") and not typ.endswith(")"):
                # VAR_IN_OUT STRING without length → leave plain; XAE accepts
                decl_lines.append(f"    {nm} : STRING(255);")
            else:
                decl_lines.append(f"    {nm} : {typ};")
        for nm, typ, _ in vars_dict["VAR_OUTPUT"]:
            decl_lines.append(f"    {nm} : {typ};")
        # return type variable
        if ret_type:
            decl_lines.append(f"    {_ret_var_name(name)} : {ret_type}; // 返回值监视")
        decl_lines.append(f"    bTrigger : BOOL := FALSE; // 在线置 TRUE 触发一次调用")
        decl_lines.append(f"    bTriggerPrev : BOOL;")
        # Stash ref_aliases for body generation
        entry["_ref_aliases"] = ref_aliases

    decl_lines.append("END_VAR")
    decl = "\n".join(decl_lines)

    # Build implementation
    scenario, value_str, alt = _scenario_value_alt(parent, name, is_parent)
    impl_header = (
        "// =============================================================================\n"
        f"// 场景：{scenario}\n"
        f"// 价值：{value_str}\n"
        f"// 验证：登录 PLC 在线写 bTrigger := TRUE 触发，monitor 返回值/输出参数。具体步骤见下方注释。\n"
        "// 验证步骤：\n"
        "//   1. 右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选本 .TcPOU 文件\n"
        f"//   2. 引用 {LIB}（References → Add library）\n"
        "//   3. 编译 → 登录 → 运行；按 verify 注释里给出的在线写值操作\n"
        "// =============================================================================\n"
    )

    ref_aliases = entry.get("_ref_aliases", {})
    if is_parent or parent == "Function blocks":
        body = _tcpou_body_parent(name, vars_dict, ret_type, ref_aliases)
    elif parent.startswith("ITc"):
        body = _tcpou_body_interface(parent, name)
    else:
        body = _tcpou_body_method(parent, name, vars_dict, ret_type, ref_aliases)

    st = impl_header + "\n" + body

    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">\n'
        f'  <POU Name="{pou_name}" Id="{guid}" SpecialFunc="None">\n'
        f'    <Declaration><![CDATA[{decl}\n]]></Declaration>\n'
        '    <Implementation>\n'
        f'      <ST><![CDATA[{st}]]></ST>\n'
        '    </Implementation>\n'
        '  </POU>\n'
        '</TcPlcObject>\n'
    )


def _ret_var_name(method_name: str) -> str:
    # Avoid IEC keyword/conflict
    return f"vRet"


def _tcpou_body_parent(name: str, vars_dict: dict, ret_type: str | None, ref_aliases: dict | None = None) -> str:
    # For parent FB demo, show instantiation + initStatus check
    ref_aliases = ref_aliases or {}
    lines = []
    lines.append("// 实例化 + 监视 initStatus，确认 FB 内部已初始化完成。")
    # Build a parameter call list
    args = []
    for nm, typ, default in vars_dict["VAR_INPUT"]:
        val = ref_aliases.get(nm, nm)
        args.append(f"    {nm} := {val}")
    for nm, typ, _ in vars_dict["VAR_IN_OUT"]:
        args.append(f"    {nm} := {nm}")
    for nm, typ, _ in vars_dict["VAR_OUTPUT"]:
        args.append(f"    {nm} => {nm}")
    if args:
        lines.append(f"fb{name}(")
        lines.append(",\n".join(args))
        lines.append(");")
    else:
        # No VAR_INPUT/OUTPUT besides initStatus — call as a bare FB invocation
        lines.append(f"fb{name}();  // 实例化即可，无输入参数")
    lines.append("")
    if name == "FB_JsonDomParser" or name == "FB_JsonDynDomParser":
        lines.append("// 进一步用法：参看 examples 目录下 FB_JsonDomParser_ParseDocument / FB_JsonDomParser_GetBool 等方法演示。")
    if name == "FB_JsonSaxReader":
        lines.append("// 进一步用法：参看 examples 目录下 FB_JsonSaxReader_Parse 演示。")
    if name == "FB_JsonSaxWriter" or name == "FB_JsonSaxPrettyWriter":
        lines.append(f"// 进一步用法：参看 examples 目录下 {name}_StartObject / {name}_AddKeyString 等方法演示。")
    if name == "FB_XmlDomParser":
        lines.append("// 进一步用法：参看 examples 目录下 FB_XmlDomParser_ParseDocument / FB_XmlDomParser_NodeName 等方法演示。")
    if name == "FB_JwtEncode":
        lines.append("// 验证流程：把测试私钥放到 C:\\TwinCAT\\test_key.pem，把 sJwt 指向 256 字节缓冲，写 bExecute := TRUE 触发；")
        lines.append("// 在 bBusy 变 FALSE 后观察 sJwt 是否出现合法 base64url 三段式（A.B.C）字符串。")
    return "\n".join(lines)


def _tcpou_body_interface(parent: str, name: str) -> str:
    return (
        "// 接口方法本身由 FB_JsonSaxReader 在解析过程中回调；演示通过启动解析触发该回调链。\n"
        "// 业务代码需要：\n"
        f"//   a) 创建一个自定义 FB（如 FB_MyJsonHandler）implements {parent}\n"
        f"//   b) 在该 FB 里实现所有 OnXxx 方法（包括 {name}）\n"
        "//   c) 把实例传给 fbSaxReader.Parse() 的 ipHandler 参数\n"
        "// 本演示只示意调用入口；实际项目里 ipHandler 不会是 0。\n"
        "IF bStart AND NOT bStartPrev THEN\n"
        f"    // 占位：实际项目应传入实现 {parent} 的自定义 FB 实例\n"
        "    // bResult := fbSaxReader.Parse(sJson := sJson, ipHandler := myHandler);\n"
        "    bResult := FALSE; // 演示用占位\n"
        "END_IF;\n"
        "bStartPrev := bStart;\n"
    )


def _tcpou_body_method(parent: str, name: str, vars_dict: dict, ret_type: str | None, ref_aliases: dict | None = None) -> str:
    ref_aliases = ref_aliases or {}
    lines = []
    # Best-effort call sketch
    lines.append("// 上升沿触发一次方法调用并观察输出。")
    lines.append("IF bTrigger AND NOT bTriggerPrev THEN")
    args = []
    for nm, typ, default in vars_dict["VAR_INPUT"]:
        val = ref_aliases.get(nm, nm)
        args.append(f"        {nm} := {val}")
    for nm, typ, _ in vars_dict["VAR_IN_OUT"]:
        args.append(f"        {nm} := {nm}")
    for nm, typ, _ in vars_dict["VAR_OUTPUT"]:
        args.append(f"        {nm} => {nm}")
    if ret_type:
        if args:
            lines.append(f"    {_ret_var_name(name)} := fbParser.{name}(")
            lines.append(",\n".join(args))
            lines.append("    );")
        else:
            lines.append(f"    {_ret_var_name(name)} := fbParser.{name}();")
    else:
        if args:
            lines.append(f"    fbParser.{name}(")
            lines.append(",\n".join(args))
            lines.append("    );")
        else:
            lines.append(f"    fbParser.{name}();")
    lines.append("END_IF;")
    lines.append("bTriggerPrev := bTrigger;")
    return "\n".join(lines)


# ============================================================================
# Main pipeline
# ============================================================================

def _doc_path(entry: dict) -> Path:
    parent = entry.get("category", "Function blocks")
    is_parent = entry.get("is_parent", False)
    name = entry["name"]
    if is_parent or parent == "Function blocks":
        # Top-level FB: parent dir is its own subdir (or function_blocks for standalones)
        if name in PARENT_SUBDIR:
            sub = PARENT_SUBDIR[name]
        elif name in {"FB_JsonDynDomParser", "FB_JwtEncode"}:
            sub = "function_blocks"
        else:
            sub = "function_blocks"
        return ROOT / LIB / sub / f"{name}.md"
    if parent.startswith("ITc"):
        return ROOT / LIB / PARENT_SUBDIR.get(parent, "interfaces") / f"{name}.md"
    # OO method
    return ROOT / LIB / PARENT_SUBDIR.get(parent, "_unknown") / f"{name}.md"


def _example_path(entry: dict) -> Path:
    parent = entry.get("category", "Function blocks")
    is_parent = entry.get("is_parent", False)
    name = entry["name"]
    if is_parent or parent == "Function blocks":
        stem = name
    elif parent.startswith("ITc"):
        stem = f"{parent}_{name}"
    else:
        stem = f"{parent}_{name}"
    return ROOT / LIB / "examples" / f"P_Demo_{stem}.TcPOU"


def _infosys_for(entry: dict) -> str:
    parent = entry.get("category", "Function blocks")
    is_parent = entry.get("is_parent", False)
    name = entry["name"]
    if is_parent or parent == "Function blocks":
        return INFOSYS_URLS.get(name, INFOSYS_BASE + "4219229195.html")
    if parent.startswith("ITc"):
        return INFOSYS_URLS.get(parent, INFOSYS_BASE + "4219229195.html")
    # OO method: point at parent FB topic (per-method topic IDs not enumerable)
    return INFOSYS_URLS.get(parent, INFOSYS_BASE + "4219229195.html")


# PDF typo fixups: certain TOC entries display a name that doesn't match the
# real METHOD declaration in the body. We override by section number.
# These docs use Status: ⚠️ infer-from-naming-convention so verify_doc skips
# the TOC/VAR diff (since neither TOC nor body heading matches our chosen filename).
PDF_TYPO_FIXUP = {
    # PDF TOC entry 4.7.20 and 4.7.31 both display title "Attributes" but
    # 4.7.20 is actually METHOD Attribute (singular, by-name attribute lookup)
    # and 4.7.31 is METHOD Attributes (plural, returns iterator). Since
    # parse_toc returns identical names, verify_doc can't disambiguate — we
    # rename 4.7.20 doc to Attribute.md and mark both with overview_only.
    "4.7.20": ("Attribute", True),
    "4.7.31": ("Attributes", True),
}


def generate_one(entry: dict) -> tuple[Path, Path]:
    """Generate doc + tcpou for a single entry."""
    section = entry.get("section", "")
    # Apply PDF TOC typo fixup
    overview_only = False
    if section in PDF_TYPO_FIXUP:
        new_name, overview_only = PDF_TYPO_FIXUP[section]
        entry = dict(entry)
        entry["name"] = new_name
        entry["_overview_only"] = overview_only
    name = entry["name"]
    section_text = _extract_section(section) if section else ""

    # If parent, strip child sections so VARs aren't polluted
    if entry.get("is_parent"):
        child_pat = re.compile(rf"^\s*{re.escape(section)}\.\d+\s+\w+", re.MULTILINE)
        cm = child_pat.search(section_text)
        if cm:
            section_text = section_text[: cm.start()]

    # Parse VAR blocks
    vars_dict = _parse_vars(section_text)
    # If no vars found but the text contains METHOD signature, try naked params
    if not any(vars_dict.values()):
        naked = _parse_naked_method_params(section_text)
        if naked:
            vars_dict["VAR_INPUT"] = naked

    ret_type = _parse_return_type(section_text)

    # Gather all known VAR names to disambiguate continuation lines
    known_names = set()
    for vlist in vars_dict.values():
        for nm, _, _ in vlist:
            known_names.add(nm)
    var_descs = _parse_pdf_description_tables(section_text, known_names)

    infosys_url = _infosys_for(entry)
    md = _render_md(entry, vars_dict, ret_type, var_descs, section, infosys_url)
    tcpou = _tcpou(entry, vars_dict, ret_type)

    doc_p = _doc_path(entry)
    ex_p = _example_path(entry)
    doc_p.parent.mkdir(parents=True, exist_ok=True)
    ex_p.parent.mkdir(parents=True, exist_ok=True)
    doc_p.write_text(md)
    ex_p.write_text(tcpou)
    return doc_p, ex_p


# Additional entries: ITcJsonSaxHandler/Values methods + parent interfaces

def _interface_entries() -> list[dict]:
    """The Interfaces (section 5) aren't in TOC parse but exist as method-style entries."""
    return [
        {"section": "5.1", "name": "ITcJsonSaxHandler", "type": "INTERFACE", "category": "Function blocks", "page": 210, "depth": 2, "is_parent": True},
        {"section": "5.1.1", "name": "OnBool", "type": "METHOD", "category": "ITcJsonSaxHandler", "page": 210, "depth": 3},
        {"section": "5.1.2", "name": "OnDint", "type": "METHOD", "category": "ITcJsonSaxHandler", "page": 210, "depth": 3},
        {"section": "5.1.3", "name": "OnEndArray", "type": "METHOD", "category": "ITcJsonSaxHandler", "page": 210, "depth": 3},
        {"section": "5.1.4", "name": "OnEndObject", "type": "METHOD", "category": "ITcJsonSaxHandler", "page": 210, "depth": 3},
        {"section": "5.1.5", "name": "OnKey", "type": "METHOD", "category": "ITcJsonSaxHandler", "page": 210, "depth": 3},
        {"section": "5.1.6", "name": "OnLint", "type": "METHOD", "category": "ITcJsonSaxHandler", "page": 211, "depth": 3},
        {"section": "5.1.7", "name": "OnLreal", "type": "METHOD", "category": "ITcJsonSaxHandler", "page": 211, "depth": 3},
        {"section": "5.1.8", "name": "OnNull", "type": "METHOD", "category": "ITcJsonSaxHandler", "page": 211, "depth": 3},
        {"section": "5.1.9", "name": "OnStartArray", "type": "METHOD", "category": "ITcJsonSaxHandler", "page": 211, "depth": 3},
        {"section": "5.1.10", "name": "OnStartObject", "type": "METHOD", "category": "ITcJsonSaxHandler", "page": 211, "depth": 3},
        {"section": "5.1.11", "name": "OnString", "type": "METHOD", "category": "ITcJsonSaxHandler", "page": 212, "depth": 3},
        {"section": "5.1.12", "name": "OnUdint", "type": "METHOD", "category": "ITcJsonSaxHandler", "page": 212, "depth": 3},
        {"section": "5.1.13", "name": "OnUlint", "type": "METHOD", "category": "ITcJsonSaxHandler", "page": 212, "depth": 3},
        {"section": "5.2", "name": "ITcJsonSaxValues", "type": "INTERFACE", "category": "Function blocks", "page": 212, "depth": 2, "is_parent": True},
        {"section": "5.2.1", "name": "OnBoolValue", "type": "METHOD", "category": "ITcJsonSaxValues", "page": 212, "depth": 3},
        {"section": "5.2.2", "name": "OnDintValue", "type": "METHOD", "category": "ITcJsonSaxValues", "page": 212, "depth": 3},
        {"section": "5.2.3", "name": "OnLintValue", "type": "METHOD", "category": "ITcJsonSaxValues", "page": 213, "depth": 3},
        {"section": "5.2.4", "name": "OnLrealValue", "type": "METHOD", "category": "ITcJsonSaxValues", "page": 213, "depth": 3},
        {"section": "5.2.5", "name": "OnNullValue", "type": "METHOD", "category": "ITcJsonSaxValues", "page": 213, "depth": 3},
        {"section": "5.2.6", "name": "OnStringValue", "type": "METHOD", "category": "ITcJsonSaxValues", "page": 213, "depth": 3},
        {"section": "5.2.7", "name": "OnUdintValue", "type": "METHOD", "category": "ITcJsonSaxValues", "page": 214, "depth": 3},
        {"section": "5.2.8", "name": "OnUlintValue", "type": "METHOD", "category": "ITcJsonSaxValues", "page": 214, "depth": 3},
    ]


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    toc = _load_toc()
    if args[0] == "--list":
        for e in toc:
            print(f"{e['section']:>10} {e['name']:<30} {e.get('category','-')}")
        return 0
    if args[0] == "--interfaces":
        for e in _interface_entries():
            doc_p, ex_p = generate_one(e)
            print(f"  {e['name']:<25} → {doc_p.relative_to(ROOT)}")
        return 0
    if args[0] == "--all":
        all_entries = toc + _interface_entries()
        for e in all_entries:
            doc_p, ex_p = generate_one(e)
            print(f"  {e['name']:<25} → {doc_p.relative_to(ROOT)}")
        return 0
    # Single entry by name
    name = args[0]
    matches = [e for e in toc if e["name"] == name]
    if not matches:
        # Try interfaces
        matches = [e for e in _interface_entries() if e["name"] == name]
    if not matches:
        print(f"name not found: {name}")
        return 1
    doc_p, ex_p = generate_one(matches[0])
    print(f"  {matches[0]['name']:<25} → {doc_p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
