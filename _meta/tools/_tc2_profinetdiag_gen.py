#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""库内生成器：Tc2_ProfinetDiag 全部 FB 文档 + .TcPOU 例程。

库名隔离脚本（brief 允许 `_meta/tools/_<lib>_*.py`）。不改任何公共工具。

每个 FB 的 VAR 区为逐字搬运 PDF（含 PDF 的 OCR 怪字 —— 例如 FB_PN_IM1_READ 的
`iErrorID  ; UDINT;`），这样 verify_doc 对 PDF 与本文档双向解析得到的 VAR 集合一致。
中文描述翻译自 PDF/InfoSys 的 Description 列（两端已核对一致）。
"""
from __future__ import annotations
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = "Tc2_ProfinetDiag"
VER = "1.0.2"
TODAY = "2026-06-02"
PDF_URL = ("https://download.beckhoff.com/download/document/automation/"
           "twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf")
INFOSYS_BASE = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/"

DNS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def guid(name: str) -> str:
    return "{" + str(uuid.uuid5(DNS, f"tc3-libraries-kb/P_Demo_{name}")) + "}"


# ---------------------------------------------------------------------------
# 通用描述片段（PDF 对几乎所有 FB 重复同样的英文，翻译一次复用）
# ---------------------------------------------------------------------------
D_bStart_edge = "上升沿（FALSE→TRUE）触发功能块执行一次。"
D_bEnable = "功能块使能。"
D_NETID_ctrl = "控制器（PROFINET Controller）的 AMS Net ID。本机控制器填空串 `''`。"
D_PORT = "控制器与设备通讯所用的 ADS 端口（port = Device ID + 1000hex）。"
D_bBusy = ("功能块使能后该输出置位，并一直保持到收到设备反馈为止。`bBusy = TRUE` "
           "期间不接受输入端的新命令（不响应新的触发）。")
D_bError = "命令传输过程中发生错误时，在 `bBusy` 复位（落沿）之后置位该输出。"
D_iErrorID = "`bError` 置位时返回 ADS 错误号（见 §4 错误码表）。"

# 行为说明：异步 ADS 边沿型 FB 的通用骨架（≥80 中文字，去子弹点后仍达标）
BEHAVIOR_EDGE = (
    "本功能块是基于 ADS 的异步功能块，内部维护「空闲 → 忙 → 完成」三态状态机。{trigname} 由 "
    "FALSE 变为 TRUE 的上升沿触发一次操作：触发后 `bBusy` 立即置 TRUE，功能块通过 ADS 把请求发往 "
    "PROFINET 控制器（由 `NETID` 与 `PORT` 寻址到目标设备）；收到设备应答后 `bBusy` 落回 FALSE，"
    "此时 {outname} 才有效，若过程出错则 `bError` 在 `bBusy` 落沿之后置 TRUE、`{errname}` 给出 ADS "
    "错误号。`bBusy = TRUE` 期间功能块忽略输入端的任何新触发，必须等到本次完成才能再次发起。\n\n"
    "**调用周期**：必须在每个 PLC 周期持续调用本实例（不是只在触发那一帧调一次），否则内部 ADS 状态机"
    "无法推进、`bBusy` 不会落沿。**清错语义**：错误状态保持到下一次 {trigname} 上升沿被接受时才更新，"
    "因此读 `bError`/`{errname}` 要在 `bBusy` 落沿之后、下一次触发之前读。**电平 vs 边沿**：{trigname} "
    "保持高电平不会反复执行，只在跳变沿触发一次；要重复操作必须先把 {trigname} 拉回 FALSE 再拉高。"
)


def beh(trig="bStart", out="输出结果", err="iErrorID"):
    return BEHAVIOR_EDGE.format(trigname=f"`{trig}`", outname=out, errname=err)


# 错误码表（PDF §5.1 ADS Return Codes 摘录，全 FB 共用 iErrorID/nErrorID）
ERR_TABLE = """`{err}` 在 `bError = TRUE` 时返回 ADS 错误号（`bError = FALSE` 时无意义）。下表摘自 PDF §5.1「ADS Return Codes」的常见取值：

| `{err}` (dec) | Hex | 名称 | 含义 / 处理建议 |
|---|---|---|---|
| `0` | `0x0` | `ERR_NOERROR` | 无错误，操作成功；读取输出结果 |
| `6` | `0x6` | `ERR_TARGETPORTNOTFOUND` | 目标端口未找到——`PORT` 错误，或目标 ADS 服务未启动/不可达。检查 `PORT` 与设备状态 |
| `7` | `0x7` | `ERR_TARGETMACHINENOTFOUND` | 目标设备未找到——AMS 路由不存在。检查 `NETID` 与路由表 |
| `16` | `0x10` | `ERR_LOWINSTLEVEL` | 授权等级过低（许可证问题） |
| `1280` | `0x500` | `ROUTERERR_NOLOCKEDMEMORY` | 路由锁定内存不足 |
| `1792`+ | `0x700`+ | 一般 ADS 错误 | 命令相关错误（如设备拒绝、参数非法）；可对照 PDF §5.1「General ADS error codes」一节查全 |

> 完整 ADS 返回码表（Global / Router / General ADS / RTime 四组）参见 PDF §5.1 章节。⚠️ PDF 与 InfoSys 均未给出本库各 FB 专属的错误码子集，上表为 ADS 通用码。"""


def err_table(err="iErrorID"):
    return ERR_TABLE.format(err=err)


# 通用使用注意（按 FB 类别填充）
NOTE_COMMON = [
    "**必须每周期调用**：本 FB 异步执行，只在触发沿那一帧调一次会导致 `bBusy` 永远不落沿。请放在周期任务里无条件调用。",
    "**一设备一实例**：每个 PROFINET 设备用独立的 FB 实例；同一实例复用到多个目标会造成请求错乱。",
    "**`PORT` 的算法**：`PORT = Device ID + 16#1000`（设备 ID 加十六进制 1000）。Device ID 可在 TwinCAT XAE 的 PROFINET 设备树里查到。（工程经验补充）",
]


# ---------------------------------------------------------------------------
# FB 定义表
# 每项：name, topic_id, subdir, section, summary(中文),
#       var_input(逐字 PDF), input_rows[(name,type,desc)],
#       var_output(逐字 PDF), output_rows[(name,type,desc)],
#       behavior, notes(list), scenario(场景/价值/替代),
#       demo_decl, demo_st, related, extra_reqs(可选版本备注)
# ---------------------------------------------------------------------------
FBS: list[dict] = []


def add(**kw):
    FBS.append(kw)


# ============ 3.1.1 AlarmDiag : FB_PN_ALARM_DIAG ============
add(
    name="FB_PN_ALARM_DIAG", topic="14966249099", subdir="controller_alarmdiag",
    section="3.1.1.1",
    summary=(
        "读取 PROFINET 设备诊断报警（diagnosis alarm）的功能块。每个实例提供一个 PLC 硬件输入 "
        "`PnIoBoxDiag`，须在 TwinCAT 中链接到被诊断设备的 `PnIoBoxDiag` 输入；该 WORD 状态字发生变化即"
        "表示设备有新的诊断报警挂起。报警成功读出后设备的报警状态会被自动复位。每个 PROFINET 设备需各"
        "调用一次本功能块，运行索引 `iNrAlarms` 表示本次从缓冲区读出了多少条诊断报警。"),
    var_input="""VAR_INPUT
  bEnable : BOOL;
  NETID   : T_AmsNetId;
  PORT    : T_AmsPort;
END_VAR""",
    input_rows=[
        ("bEnable", "BOOL", D_bEnable),
        ("NETID", "T_AmsNetId", D_NETID_ctrl),
        ("PORT", "T_AmsPort", D_PORT),
    ],
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  stAlarmDiagData         : ST_PN_AlarmDiagData;
  bError                  : BOOL;
  iErrorID                : UDINT;
  iNrAlarms               : INT;
END_VAR""",
    output_rows=[
        ("bBusy", "BOOL", D_bBusy),
        ("stAlarmDiagData", "ST_PN_AlarmDiagData",
         "诊断报警通过该结构输出。只要 PLC 输入上存在状态位 `0x0010`（至少一个 AlarmCR 收到诊断报警），"
         "每个周期就通过该结构输出一条报警。结构含时间戳、站名、诊断明细 `ST_PN_Diag` 与用户数据标志。"),
        ("bError", "BOOL", D_bError),
        ("iErrorID", "UDINT", D_iErrorID),
        ("iNrAlarms", "INT", "本次读出的报警条数。"),
    ],
    behavior=(
        "本功能块为电平使能型（不同于库内多数边沿触发的 FB）。`bEnable = TRUE` 期间功能块持续工作：当链接的 "
        "`PnIoBoxDiag` 硬件输入（WORD）发生变化、且其中状态位 `0x0010` 置位（表示至少一个 AlarmCR 收到诊断"
        "报警）时，功能块逐条把诊断缓冲区里的报警通过 `stAlarmDiagData` 输出，每个 PLC 周期输出一条，并用 "
        "`iNrAlarms` 累计已读条数。`bBusy` 在等待 ADS 反馈期间为 TRUE，其间不接受新命令。所有挂起报警读完后，"
        "设备侧的报警状态被自动复位，`PnIoBoxDiag` 随之回到无报警值。\n\n"
        "**链接要求**：`PnIoBoxDiag`（`AT %I* : WORD`）是硬件输入变量，必须在 TwinCAT I/O 映射里手动链接到对应 "
        "PROFINET 设备的 `PnIoBoxDiag`，否则 PLC 永远收不到「有新报警」的通知。**逐条读出**：一个设备可能同时挂"
        "多条报警，需保持 `bEnable = TRUE` 连续多个周期，逐个周期把 `stAlarmDiagData` 取走（建议每周期把结构拷入"
        "环形缓冲或报警列表）。**出错处理**：传输出错时 `bError` 在 `bBusy` 落沿后置位，`iErrorID` 给出 ADS 错误号。"),
    notes=[
        "**`PnIoBoxDiag` 必须链接**：这是本 FB 区别于其它 FB 的关键——它带一个 `AT %I*` 硬件输入。漏链接会导致功能块"
        "「看不到」设备报警，表现为永远读不到诊断数据。",
        "**每设备一实例**：报警状态复位是按设备进行的，多设备务必各用一个实例并各自链接 `PnIoBoxDiag`。",
        "**逐周期取数**：报警是逐条、逐周期通过 `stAlarmDiagData` 输出的，HMI/记录逻辑要在每个周期把结构内容搬走，"
        "否则会漏读后续报警。（工程经验补充）",
    ],
    scenario=(
        "- **场景**：一条产线上挂了若干 PROFINET 从站（如 EL663x 网关后的 IO、第三方 PN 设备）。当某个从站发生"
        "断线、模块拔出、通道短路等故障时，PROFINET 会发出诊断报警。运维需要在 HMI 上实时看到「哪个站、哪个槽、"
        "什么类型」的报警明细。\n"
        "- **价值**：不用本 FB 就得自己用 `ADSREAD` 去读 PROFINET 控制器的诊断索引、再手工解析二进制诊断帧"
        "（`ST_PN_DiagMessage` 300 字节裸数据）。本 FB 把「监听 `PnIoBoxDiag` 触发 → 读诊断帧 → 解析为可读结构 "
        "`ST_PN_AlarmDiagData`（含站名、槽号、报警类型）→ 复位报警状态」整条链路封装好，业务侧只需读结构字段。\n"
        "- **替代方案对比**：System Manager 的 Diag History 只能在工程师电脑上看，无法进 PLC 逻辑联动；自己写 "
        "`ADSREAD` 解析诊断帧工作量大且易错。本 FB 是把诊断接入 PLC 逻辑（联动声光报警、停机保护）的标准做法。"),
    demo=("""VAR
    fbAlarmDiag      : FB_PN_ALARM_DIAG;        // 诊断报警读取实例
    bDiagEnable      : BOOL := FALSE;           // 在线置 TRUE 开始监听本设备报警
    stDiag           : ST_PN_AlarmDiagData;     // 解析后的可读诊断数据
    bDiagBusy        : BOOL;
    bDiagError       : BOOL;
    nDiagErrId       : UDINT;
    iAlarmCount      : INT;                      // 本次读出的报警条数
    // 注：实际工程中 PnIoBoxDiag 由 TwinCAT I/O 映射链接到设备硬件输入，
    //     无法在纯 ST 例程里赋值，此处仅演示输出端的在线观察。
END_VAR""",
          """// 电平使能型：bDiagEnable 保持 TRUE 期间持续监听并逐条输出报警
fbAlarmDiag(
    bEnable := bDiagEnable,
    NETID   := '',                 // 本机控制器
    PORT    := 16#1001,            // 示例：Device ID 1 -> 1 + 16#1000
    bBusy   => bDiagBusy,
    stAlarmDiagData => stDiag,
    bError  => bDiagError,
    iErrorID => nDiagErrId,
    iNrAlarms => iAlarmCount
);

// 工程中应在此把 stDiag 拷入报警列表 / 推 HMI（每周期取一条）
// IF iAlarmCount > 0 THEN ... 记录 stDiag.sNameOfStation / stDiag.ST_Diag.nSlot ..."""),
    related="`FB_PN_READ_PORT_DIAG`（读端口诊断）、`ST_PN_AlarmDiagData` / `ST_PN_Diag` / `ST_PN_DiagMessage`（诊断数据结构）",
)


# ============ 3.1.2 I&M 读 FB（bStart/NETID/PORT 输入统一） ============
IM_IN_BLOCK = """VAR_INPUT
  bStart  : BOOL;
  NETID   : T_AmsNetId;
  PORT    : T_AmsPort;
END_VAR"""
IM_IN_ROWS = [
    ("bStart", "BOOL", D_bStart_edge),
    ("NETID", "T_AmsNetId", D_NETID_ctrl),
    ("PORT", "T_AmsPort", D_PORT),
]


def im_read_demo(name, outassign, outdecl):
    inst = "fb" + name  # 约定：fb<Name>
    return (
        f"""VAR
    {inst} : {name};        // {name} 实例
    bReadIM       : BOOL := FALSE;            // 在线上升沿触发一次读取
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
{outdecl}
END_VAR""",
        f"""// 上升沿触发一次 I&M 读取；读到的数据在 bBusy 落沿后有效
{inst}(
    bStart := bReadIM,
    NETID  := '',
    PORT   := 16#1001,
    bBusy  => bBusy,
{outassign}
    bError => bErr,
    iErrorID => nErrId
);""")


add(
    name="FB_PN_IM0_READ", topic="14965552779", subdir="controller_im", section="3.1.2.1",
    summary=("PROFINET 控制器用本功能块从指定 `PORT` 引用的设备读取全部 I&M0（Identification & Maintenance，"
             "标识与维护）数据。I&M0 帧结构对应 PROFINET 标准中的索引 `0xAFF0`，包含厂商 ID、订货号、序列号、"
             "硬件/软件版本等设备出厂标识信息，通过结构 `str_IM_0xAFF0` 一次性返回。"),
    var_input=IM_IN_BLOCK, input_rows=IM_IN_ROWS,
    var_output="""VAR_OUTPUT
    bBusy    : BOOL;
    IM_AFF0  : str_IM_0xAFF0;
    bError   : BOOL;
    iErrorID : UDINT;
END_VAR""",
    output_rows=[
        ("bBusy", "BOOL", D_bBusy),
        ("IM_AFF0", "str_IM_0xAFF0", "设备返回的 I&M0 帧，封装为结构输出（厂商 ID、订货号 `cOrderID`、"
         "序列号 `cSerialNumber`、硬件版本 `nHW_Rev`、软件版本 `strSW_Rev` 等）。"),
        ("bError", "BOOL", D_bError),
        ("iErrorID", "UDINT", D_iErrorID),
    ],
    behavior=beh("bStart", "`IM_AFF0` 结构", "iErrorID"),
    notes=NOTE_COMMON + [
        "I&M0 是只读的出厂标识，无对应的 WRITE 功能块（I&M1~I&M4 才可写）。",
    ],
    scenario=(
        "- **场景**：设备资产盘点 / 来料校验。PLC 在设备上线时读出每个 PROFINET 从站的厂商 ID、订货号、序列号，"
        "与 MES 里登记的 BOM 比对，防止装错型号或被掉包。\n"
        "- **价值**：把 PROFINET 标准的 `0xAFF0` 记录解析封装成结构，业务侧直接取 `cOrderID`/`cSerialNumber` 字段，"
        "不必手工拼 record index、解二进制帧。\n"
        "- **替代方案对比**：用通用 `ADSREAD` 读 record 也能拿到原始字节，但要自己按 PROFINET 规范切字段；本 FB 免去解析。"),
    demo=im_read_demo("FB_PN_IM0_READ",
                      "    IM_AFF0 => stIM0,",
                      "    stIM0         : str_IM_0xAFF0;            // I&M0 出厂标识结构"),
    related="`FB_PN_IM1_READ`~`FB_PN_IM4_READ`（其它 I&M 记录）、`str_IM_0xAFF0`（数据结构）",
)

add(
    name="FB_PN_IM1_READ", topic="14965720459", subdir="controller_im", section="3.1.2.2",
    summary=("PROFINET 控制器用本功能块从指定 `PORT` 引用的设备读取全部 I&M1 数据。I&M1 帧结构对应 PROFINET "
             "标准索引 `0xAFF1`，承载用户可写的功能标签 `st_IM_TagFunction`（设备功能描述）与安装位置标签 "
             "`st_IM_TagLocation`，本 FB 把这两个字符串读回。"),
    var_input=IM_IN_BLOCK, input_rows=IM_IN_ROWS,
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  st_IM_TagFunction       : STRING(32);
  st_IM_TagLocation       : STRING(22);
  bError                  : BOOL;
  iErrorID                ; UDINT;
END_VAR""",
    output_rows=[
        ("bBusy", "BOOL", D_bBusy),
        ("st_IM_TagFunction", "STRING(32)", "读回的设备功能标签（function tag）。"),
        ("st_IM_TagLocation", "STRING(22)", "读回的设备安装位置标签（location tag）。"),
        ("bError", "BOOL", D_bError),
        ("iErrorID", "UDINT", D_iErrorID + " ⚠️ PDF 原文此行印作 `iErrorID ; UDINT;`（冒号误印为分号），实际类型为 `UDINT`。"),
    ],
    behavior=beh("bStart", "`st_IM_TagFunction` / `st_IM_TagLocation`", "iErrorID"),
    notes=NOTE_COMMON + [
        "I&M1 可读可写：本 FB 读，`FB_PN_IM1_WRITE` 写。功能标签上限 32 字符、位置标签上限 22 字符。",
        "**PDF 排版怪字**：VAR_OUTPUT 中 `iErrorID` 那行 PDF 印成了 `iErrorID ; UDINT;`（分号代替冒号）。"
        "InfoSys 同一 topic 的描述表确认其类型为 `UDINT`。本文档代码块按 PDF 逐字保留，类型以 `UDINT` 为准。",
    ],
    scenario=(
        "- **场景**：设备投运后读出现场工程师写入的「功能描述 / 安装位置」标签（如 `\"Conveyor-Motor\"` / "
        "`\"Hall-A Line-3\"`），在 HMI 设备列表里展示，便于运维定位。\n"
        "- **价值**：I&M1 标签是 PROFINET 标准化的「电子铭牌」，本 FB 直接读出两段字符串，免去手工解析 `0xAFF1` 帧。\n"
        "- **替代方案对比**：纸质铭牌易丢、易过期；I&M1 标签随设备走、可远程读写，本 FB 是读取它的标准手段。"),
    demo=im_read_demo("FB_PN_IM1_READ",
                      "    st_IM_TagFunction => sTagFunction,\n    st_IM_TagLocation => sTagLocation,",
                      "    sTagFunction  : STRING(32);              // 功能标签\n    sTagLocation  : STRING(22);              // 位置标签"),
    related="`FB_PN_IM1_WRITE`（写 I&M1）、`str_IM_0xAFF1`（数据结构）",
)

add(
    name="FB_PN_IM2_READ", topic="14965825419", subdir="controller_im", section="3.1.2.4",
    summary=("PROFINET 控制器用本功能块从指定 `PORT` 引用的设备读取全部 I&M2 数据。I&M2 帧结构对应 PROFINET "
             "标准索引 `0xAFF2`，承载设备安装日期。本 FB 把安装日期以 `TIMESTRUCT` 结构（格式 "
             "`<YYYY-MM-DD HH:MM>`）输出。"),
    var_input=IM_IN_BLOCK, input_rows=IM_IN_ROWS,
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  str_Date                : TIMESTRUCT; (*YYYY-MM-DD HH:MM*);
  bError                  : BOOL;
  iErrorID                : UDINT;
END_VAR""",
    output_rows=[
        ("bBusy", "BOOL", D_bBusy),
        ("str_Date", "TIMESTRUCT", "返回设备安装日期，格式 `<YYYY-MM-DD HH:MM>`。"),
        ("bError", "BOOL", D_bError),
        ("iErrorID", "UDINT", D_iErrorID),
    ],
    behavior=beh("bStart", "`str_Date`（安装日期）", "iErrorID"),
    notes=NOTE_COMMON + ["I&M2 可读可写：本 FB 读安装日期，`FB_PN_IM2_WRITE` 写。"],
    scenario=(
        "- **场景**：读设备安装/投运日期，用于计算设备役龄、安排周期性维护或质保到期提醒。\n"
        "- **价值**：日期随设备存储在 PROFINET 设备里，本 FB 直接以 `TIMESTRUCT` 读出，免去日期帧解析。\n"
        "- **替代方案对比**：维护台账靠人维护易脱节；I&M2 日期与物理设备绑定，更可靠。"),
    demo=im_read_demo("FB_PN_IM2_READ",
                      "    str_Date => stInstallDate,",
                      "    stInstallDate : TIMESTRUCT;              // 设备安装日期 YYYY-MM-DD HH:MM"),
    related="`FB_PN_IM2_WRITE`（写 I&M2）、`str_IM_0xAFF2`（数据结构）",
)

add(
    name="FB_PN_IM3_READ", topic="14965931147", subdir="controller_im", section="3.1.2.6",
    summary=("PROFINET 控制器用本功能块从指定 `PORT` 引用的设备读取全部 I&M3 数据。I&M3 帧结构对应 PROFINET "
             "标准索引 `0xAFF3`，承载厂商描述文本 `st_IM_Descriptor`（最长 54 字符），本 FB 把它读回。"),
    var_input=IM_IN_BLOCK, input_rows=IM_IN_ROWS,
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  st_IM_Descriptor        : STRING(54);
  bError                  : BOOL;
  iErrorID                : UDINT;
END_VAR""",
    output_rows=[
        ("bBusy", "BOOL", D_bBusy),
        ("st_IM_Descriptor", "STRING(54)", "返回设备存储的厂商描述（descriptor）。"),
        ("bError", "BOOL", D_bError),
        ("iErrorID", "UDINT", D_iErrorID),
    ],
    behavior=beh("bStart", "`st_IM_Descriptor`（厂商描述）", "iErrorID"),
    notes=NOTE_COMMON + ["I&M3 可读可写：本 FB 读，`FB_PN_IM3_WRITE` 写。描述上限 54 字符。"],
    scenario=(
        "- **场景**：读出设备的自定义注释 / 描述文本（如维护备注、配置版本说明），在 HMI 展示。\n"
        "- **价值**：I&M3 是 PROFINET 标准的自由文本字段，本 FB 直接读出，免去帧解析。\n"
        "- **替代方案对比**：外部数据库存描述需额外维护映射；I&M3 随设备走，本 FB 是标准读取方式。"),
    demo=im_read_demo("FB_PN_IM3_READ",
                      "    st_IM_Descriptor => sDescriptor,",
                      "    sDescriptor   : STRING(54);              // 厂商描述文本"),
    related="`FB_PN_IM3_WRITE`（写 I&M3）、`str_IM_0xAFF3`（数据结构）",
)

add(
    name="FB_PN_IM4_Read", topic="14966036107", subdir="controller_im", section="3.1.2.8",
    summary=("PROFINET 控制器用本功能块从指定 `PORT` 引用的设备读取全部 I&M4 数据。I&M4 帧结构对应 PROFINET "
             "标准索引 `0xAFF4`，承载厂商签名 `st_IM_Signatur`（最长 54 字符，常用于功能安全场景的参数签名），"
             "本 FB 把它读回。"),
    var_input=IM_IN_BLOCK, input_rows=IM_IN_ROWS,
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  st_IM_Signatur          : STRING(54);
  bError                  : BOOL;
  iErrorID                : UDINT;
END_VAR""",
    output_rows=[
        ("bBusy", "BOOL", D_bBusy),
        ("st_IM_Signatur", "STRING(54)", "返回设备存储的厂商签名（signature）。"),
        ("bError", "BOOL", D_bError),
        ("iErrorID", "UDINT", D_iErrorID),
    ],
    behavior=beh("bStart", "`st_IM_Signatur`（厂商签名）", "iErrorID"),
    notes=NOTE_COMMON + [
        "I&M4 可读可写：本 FB 读，`FB_PN_IM4_WRITE` 写。签名上限 54 字符。",
        "**注意命名**：本 FB 在 PDF/InfoSys 中名为 `FB_PN_IM4_Read`（`Read` 大小写与其它 READ 系列不同，逐字保留）。",
    ],
    scenario=(
        "- **场景**：功能安全（PROFIsafe）或参数化设备投运时，读出参数签名以校验设备配置未被篡改。\n"
        "- **价值**：I&M4 签名是参数完整性校验的标准载体，本 FB 直接读出。\n"
        "- **替代方案对比**：自定义校验需双方约定算法；I&M4 是 PROFINET 标准字段，本 FB 通用。"),
    demo=im_read_demo("FB_PN_IM4_Read",
                      "    st_IM_Signatur => sSignature,",
                      "    sSignature    : STRING(54);              // 厂商签名"),
    related="`FB_PN_IM4_WRITE`（写 I&M4）、`str_IM_0xAFF4`（数据结构）",
)

# ---- I&M 写 FB ----
add(
    name="FB_PN_IM1_WRITE", topic="14965772939", subdir="controller_im", section="3.1.2.3",
    summary=("PROFINET 控制器用本功能块把全部 I&M1 数据写入指定 `PORT` 引用的设备。I&M1 帧结构对应 PROFINET "
             "标准索引 `0xAFF1`。通过输入 `st_IM_TagFunction`（功能描述）与 `st_IM_TagLocation`（安装位置）把这"
             "两段标签持久化到设备里。"),
    var_input="""VAR_INPUT
  bStart             : BOOL;
  NETID              : T_AmsNetId;
  PORT               : T_AmsPort;
  st_IM_TagFunction  : STRING(32);
  st_IM_TagLocation  : STRING(22);
END_VAR""",
    input_rows=[
        ("bStart", "BOOL", D_bStart_edge),
        ("NETID", "T_AmsNetId", D_NETID_ctrl),
        ("PORT", "T_AmsPort", D_PORT),
        ("st_IM_TagFunction", "STRING(32)", "用该字符串把设备功能描述保存到设备。"),
        ("st_IM_TagLocation", "STRING(22)", "用该字符串把设备安装位置保存到设备。"),
    ],
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  iErrorID                : UDINT;
END_VAR""",
    output_rows=[("bBusy", "BOOL", D_bBusy), ("bError", "BOOL", D_bError), ("iErrorID", "UDINT", D_iErrorID)],
    behavior=beh("bStart", "（无数据输出，仅 `bBusy`/`bError` 反馈写入结果）", "iErrorID"),
    notes=NOTE_COMMON + [
        "**写入前先备好字符串**：触发前把 `st_IM_TagFunction`/`st_IM_TagLocation` 赋好值；上升沿那一刻的值被写入。",
        "标签长度受限：功能 32 字符、位置 22 字符，超长会被截断或报错。",
    ],
    scenario=(
        "- **场景**：设备首次投运 / 整机出厂前，由调试程序统一给每个 PROFINET 从站写入功能与位置标签（电子铭牌）。\n"
        "- **价值**：批量自动写标签，免去逐台用工程软件手填；标签随设备走，后续维护可远程读回（配合 `FB_PN_IM1_READ`）。\n"
        "- **替代方案对比**：用工程软件手填费时易错；本 FB 让 PLC 在投运流程里自动化写入。"),
    demo=("""VAR
    fbIM1Write    : FB_PN_IM1_WRITE;
    bWriteTag     : BOOL := FALSE;            // 在线上升沿触发写入
    sFunction     : STRING(32) := 'Conveyor-Motor';   // 待写功能标签
    sLocation     : STRING(22) := 'HallA-Line3';      // 待写位置标签
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
END_VAR""",
          """// 触发前已备好两段标签字符串；上升沿写入设备
fbIM1Write(
    bStart := bWriteTag,
    NETID  := '',
    PORT   := 16#1001,
    st_IM_TagFunction := sFunction,
    st_IM_TagLocation := sLocation,
    bBusy  => bBusy,
    bError => bErr,
    iErrorID => nErrId
);"""),
    related="`FB_PN_IM1_READ`（读 I&M1）、`str_IM_0xAFF1`（数据结构）",
)

add(
    name="FB_PN_IM2_WRITE", topic="14965877899", subdir="controller_im", section="3.1.2.5",
    summary=("PROFINET 控制器用本功能块把全部 I&M2 数据写入指定 `PORT` 引用的设备。I&M2 帧结构对应 PROFINET "
             "标准索引 `0xAFF2`。通过输入 `str_Date`（`TIMESTRUCT`，格式 `<YYYY-MM-DD HH:MM>`）把安装日期写入设备。"),
    var_input="""VAR_INPUT
  bStart   : BOOL;
  NETID    : T_AmsNetId;
  PORT     : T_AmsPort;
  str_Date : TIMESTRUCT;(*YYYY-MM-DD HH:MM*)
END_VAR""",
    input_rows=[
        ("bStart", "BOOL", D_bStart_edge),
        ("NETID", "T_AmsNetId", D_NETID_ctrl),
        ("PORT", "T_AmsPort", D_PORT),
        ("str_Date", "TIMESTRUCT", "把日期（如设备安装日期）以 `<YYYY-MM-DD HH:MM>` 格式写入设备。"),
    ],
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  iErrorID                : UDINT;
END_VAR""",
    output_rows=[("bBusy", "BOOL", D_bBusy), ("bError", "BOOL", D_bError), ("iErrorID", "UDINT", D_iErrorID)],
    behavior=beh("bStart", "（无数据输出，仅写入反馈）", "iErrorID"),
    notes=NOTE_COMMON + ["写入前先填好 `str_Date` 的各字段（年/月/日/时/分）。"],
    scenario=(
        "- **场景**：设备投运时把当前日期写入 I&M2 作为「投运日期」，后续用于役龄统计与质保管理。\n"
        "- **价值**：投运日期随设备持久化存储，本 FB 一次写入；配合 `FB_PN_IM2_READ` 可随时读回。\n"
        "- **替代方案对比**：外部记录易与设备脱节；I&M2 与设备绑定更可靠。"),
    demo=("""VAR
    fbIM2Write    : FB_PN_IM2_WRITE;
    bWriteDate    : BOOL := FALSE;            // 在线上升沿触发写入
    stCommissionDate : TIMESTRUCT := (wYear := 2026, wMonth := 6, wDay := 2, wHour := 8, wMinute := 0);
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
END_VAR""",
          """// 把投运日期 2026-06-02 08:00 写入设备 I&M2
fbIM2Write(
    bStart := bWriteDate,
    NETID  := '',
    PORT   := 16#1001,
    str_Date := stCommissionDate,
    bBusy  => bBusy,
    bError => bErr,
    iErrorID => nErrId
);"""),
    related="`FB_PN_IM2_READ`（读 I&M2）、`str_IM_0xAFF2`（数据结构）",
)

add(
    name="FB_PN_IM3_WRITE", topic="14965983627", subdir="controller_im", section="3.1.2.7",
    summary=("PROFINET 控制器用本功能块把全部 I&M3 数据写入指定 `PORT` 引用的设备。I&M3 帧结构对应 PROFINET "
             "标准索引 `0xAFF3`。通过输入 `st_IM_Descriptor`（最长 54 字符）把厂商/自定义描述文本写入设备。"),
    var_input="""VAR_INPUT
  bStart            : BOOL;
  NETID             : T_AmsNetId;
  PORT              : T_AmsPort;
  st_IM_Descriptor  : STRING(54);
END_VAR""",
    input_rows=[
        ("bStart", "BOOL", D_bStart_edge),
        ("NETID", "T_AmsNetId", D_NETID_ctrl),
        ("PORT", "T_AmsPort", D_PORT),
        ("st_IM_Descriptor", "STRING(54)", "写入设备的描述文本。"),
    ],
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  iErrorID                : UDINT;
END_VAR""",
    output_rows=[("bBusy", "BOOL", D_bBusy), ("bError", "BOOL", D_bError), ("iErrorID", "UDINT", D_iErrorID)],
    behavior=beh("bStart", "（无数据输出，仅写入反馈）", "iErrorID"),
    notes=NOTE_COMMON + [
        "描述上限 54 字符。",
        "**PDF 排版残留**：本节描述表错误地复用了 `str_Date / TIMESTRUCT` 那一行（PDF 复制粘贴遗留），实际输入只有 "
        "`st_IM_Descriptor : STRING(54)`，VAR 代码块以本 FB 实际声明为准。",
    ],
    scenario=(
        "- **场景**：给设备写入自定义描述（如配置版本、维护备注），实现「设备自带注释」。\n"
        "- **价值**：描述随设备持久化，本 FB 一次写入，免去外部映射表。\n"
        "- **替代方案对比**：外部数据库存描述需维护设备 ID 映射；I&M3 与设备绑定更直接。"),
    demo=("""VAR
    fbIM3Write    : FB_PN_IM3_WRITE;
    bWriteDesc    : BOOL := FALSE;            // 在线上升沿触发写入
    sDescriptor   : STRING(54) := 'CfgRev=2.3 maint by EE-team';   // 待写描述
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
END_VAR""",
          """// 把自定义描述写入设备 I&M3
fbIM3Write(
    bStart := bWriteDesc,
    NETID  := '',
    PORT   := 16#1001,
    st_IM_Descriptor := sDescriptor,
    bBusy  => bBusy,
    bError => bErr,
    iErrorID => nErrId
);"""),
    related="`FB_PN_IM3_READ`（读 I&M3）、`str_IM_0xAFF3`（数据结构）",
)

add(
    name="FB_PN_IM4_WRITE", topic="14966088587", subdir="controller_im", section="3.1.2.9",
    summary=("PROFINET 控制器用本功能块把全部 I&M4 数据写入指定 `PORT` 引用的设备。I&M4 帧结构对应 PROFINET "
             "标准索引 `0xAFF4`。通过输入 `st_IM_Signatur`（最长 54 字符）把厂商签名写入设备。"),
    var_input="""VAR_INPUT
  bStart          : BOOL;
  NETID           : T_AmsNetId;
  PORT            : T_AmsPort;
  st_IM_Signatur  : STRING(54);
END_VAR""",
    input_rows=[
        ("bStart", "BOOL", D_bStart_edge),
        ("NETID", "T_AmsNetId", D_NETID_ctrl),
        ("PORT", "T_AmsPort", D_PORT),
        ("st_IM_Signatur", "STRING(54)", "写入设备的厂商签名。"),
    ],
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  iErrorID                : UDINT;
END_VAR""",
    output_rows=[("bBusy", "BOOL", D_bBusy), ("bError", "BOOL", D_bError), ("iErrorID", "UDINT", D_iErrorID)],
    behavior=beh("bStart", "（无数据输出，仅写入反馈）", "iErrorID"),
    notes=NOTE_COMMON + ["签名上限 54 字符。"],
    scenario=(
        "- **场景**：功能安全/参数化设备投运时，写入参数签名作为配置完整性凭据。\n"
        "- **价值**：签名随设备持久化，本 FB 一次写入，配合 `FB_PN_IM4_Read` 可校验。\n"
        "- **替代方案对比**：自定义签名机制需双方约定；I&M4 为标准字段，本 FB 通用。"),
    demo=("""VAR
    fbIM4Write    : FB_PN_IM4_WRITE;
    bWriteSig     : BOOL := FALSE;            // 在线上升沿触发写入
    sSignature    : STRING(54) := 'SIG-A1B2C3D4';     // 待写签名
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
END_VAR""",
          """// 把厂商签名写入设备 I&M4
fbIM4Write(
    bStart := bWriteSig,
    NETID  := '',
    PORT   := 16#1001,
    st_IM_Signatur := sSignature,
    bBusy  => bBusy,
    bError => bErr,
    iErrorID => nErrId
);"""),
    related="`FB_PN_IM4_Read`（读 I&M4）、`str_IM_0xAFF4`（数据结构）",
)

# ============ 3.1.3 PROFINET RT Controller ============
add(
    name="FB_PN_ReadStateOfDevices", topic="14977342347", subdir="controller_rt", section="3.1.3.1",
    summary=("读取 PROFINET RT 控制器下所有从站的总体状态。调用后返回已组态设备数、处于错误/诊断状态的设备数、"
             "以及带诊断的设备数，用于一眼掌握整条 PROFINET 网络的健康度。仅适用于 PROFINET RT Controller 驱动"
             "版本 v03（v0.21）及以上（XAE 的 PROFINET RT Controller I/O 设备里可查驱动版本）。"),
    var_input="""VAR_INPUT
  bExecute               : BOOL;
  NETID                  : T_AmsNetIdArr;
END_VAR""",
    input_rows=[
        ("bExecute", "BOOL", D_bStart_edge),
        ("NETID", "T_AmsNetIdArr", "PROFINET RT 控制器的 AMS Net ID。⚠️ PDF/InfoSys 代码块中类型印作 "
         "`T_AmsNetIdArr`（描述表写 `T_AmsNetId`），以代码块声明 `T_AmsNetIdArr` 为准。"),
    ],
    var_output="""VAR_OUTPUT
  bBusy                      : BOOL;
  bError                     : BOOL;
  nErrorID                   : UDINT;
  nDevices                   : UINT;
  PnIoError                  : UINT;
  PnIoDiag                   : UINT
  sControllerDriverVersion   : STRING;
END_VAR""",
    output_rows=[
        ("bBusy", "BOOL", D_bBusy),
        ("bError", "BOOL", D_bError),
        ("nErrorID", "UDINT", "`bError` 置位时返回 ADS 错误号（见 §4）。"),
        ("nDevices", "UINT", "已组态的设备数（最多 255）。"),
        ("PnIoError", "UINT", "处于错误状态或带诊断的设备数。"),
        ("PnIoDiag", "UINT", "带诊断的设备数。"),
        ("sControllerDriverVersion", "STRING", "PROFINET 控制器驱动版本（需 03 / V00.21 及以上）。"),
    ],
    behavior=(beh("bExecute", "`nDevices` / `PnIoError` / `PnIoDiag` / `sControllerDriverVersion`", "nErrorID")
              + "\n\n**版本前提**：本 FB 仅在 PROFINET RT Controller 驱动版本 v03（V00.21）或更高时可用，低版本驱动调用会报错。"
                "可在 TwinCAT XAE 的 PROFINET RT Controller I/O 设备属性里查看实际驱动版本。"),
    notes=[
        "**驱动版本要求**：v03（V00.21）以上。低版本会调用失败。",
        "**适合做总览**：本 FB 给的是「计数级」总览（多少设备、多少报错），要看具体哪个设备出问题，再用 "
        "`FB_PN_ReadCompleteInfoOfDevices` 取每台明细。",
        "**PDF 类型怪字**：`NETID` 在代码块印作 `T_AmsNetIdArr`，输出 `PnIoDiag` 行末缺分号——均按 PDF 逐字保留。",
    ],
    scenario=(
        "- **场景**：HMI 首页放一个「PROFINET 网络健康」仪表盘，显示「组态 X 台 / 异常 Y 台 / 诊断 Z 台」。\n"
        "- **价值**：一次调用拿到三个计数，免去逐台轮询；异常计数 > 0 时再下钻查明细。\n"
        "- **替代方案对比**：逐台读状态既慢又繁；本 FB 由控制器汇总，一次返回总览。"),
    demo=("""VAR
    fbReadState   : FB_PN_ReadStateOfDevices;
    bReadOverview : BOOL := FALSE;            // 在线上升沿触发一次总览读取
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
    nCfgDevices   : UINT;                     // 已组态设备数
    nErrDevices   : UINT;                     // 错误/诊断设备数
    nDiagDevices  : UINT;                     // 带诊断设备数
    sDrvVer       : STRING;                   // 控制器驱动版本
END_VAR""",
          """// 上升沿触发；读出整网总览计数（需 RT Controller 驱动 v03/V00.21+）
fbReadState(
    bExecute := bReadOverview,
    NETID    := '',
    bBusy    => bBusy,
    bError   => bErr,
    nErrorID => nErrId,
    nDevices => nCfgDevices,
    PnIoError => nErrDevices,
    PnIoDiag => nDiagDevices,
    sControllerDriverVersion => sDrvVer
);

// IF nErrDevices > 0 THEN 下钻调用 FB_PN_ReadCompleteInfoOfDevices 查明细"""),
    related="`FB_PN_ReadCompleteInfoOfDevices`（逐台明细）、`ST_PN_DeviceInfo`（设备信息结构）",
)

add(
    name="FB_PN_ReadCompleteInfoOfDevices", topic="14999239435", subdir="controller_rt", section="3.1.3.2",
    summary=("生成 TwinCAT 中已组态的全部 PROFINET 设备的完整信息列表，逐台返回 `ST_PN_DeviceInfo`（BOX 地址、"
             "设备名、IP/掩码/网关、PN 状态、诊断、输入/输出 CR 数、循环时间）。适用于 PROFINET RT 控制器（如 "
             "TF6271、CCAT M930 接口或 EL6631 v11(v.024)）。"),
    var_input="""VAR_INPUT
  bExecute                     : BOOL;
  sControllerName              : T_Maxstring
  tTimeout                     : TIME;
END_VAR""",
    input_rows=[
        ("bExecute", "BOOL", D_bStart_edge),
        ("sControllerName", "T_MaxString", "PROFINET RT 控制器在 TwinCAT 设备树中的名称。⚠️ PDF/InfoSys 代码块"
         "印作 `T_Maxstring`（描述表写 `T_MaxString`），以代码块逐字为准（类型大小写不影响编译别名）。"),
        ("tTimeout", "TIME", "整个读取过程的超时时长。"),
    ],
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  nErrorID                : UDINT;
  nDevices                : UINT;
  aInfoOfDevices          : ARRAY [1..255] OF st_PN_DeviceInfo;
END_VAR""",
    output_rows=[
        ("bBusy", "BOOL", D_bBusy),
        ("bError", "BOOL", D_bError),
        ("nErrorID", "UDINT", "`bError` 置位时返回 ADS 错误号（见 §4）。"),
        ("nDevices", "UINT", "组态中的 PROFINET 设备数。"),
        ("aInfoOfDevices", "ARRAY [1..255] OF st_PN_DeviceInfo", "已组态各 PROFINET 设备的设置信息数组（逐台一项）。"),
    ],
    behavior=(beh("bExecute", "`nDevices` 与 `aInfoOfDevices` 数组", "nErrorID")
              + "\n\n**与 `FB_PN_ReadStateOfDevices` 的区别**：后者只给总览计数，本 FB 给逐台完整信息（每台一个 "
                "`ST_PN_DeviceInfo`），数据量大、耗时更长，故带 `tTimeout` 输入控制整体超时。"),
    notes=[
        "**用 `nDevices` 限定遍历范围**：`aInfoOfDevices` 固定 255 项，但只有前 `nDevices` 项有效，遍历时以 `nDevices` 为上界。",
        "**`tTimeout` 要给足**：逐台读取耗时随设备数增长，超时太小会中途失败；建议按设备数留余量（如每台 1~2 秒）。（工程经验补充）",
        "**适用控制器**：TF6271 / CCAT M930 / EL6631 v11(v.024) 等 RT 控制器。",
    ],
    scenario=(
        "- **场景**：HMI 设备详情页要列出每个 PROFINET 从站的名称、IP、循环时间、PN 状态，做成可滚动的设备清单。\n"
        "- **价值**：一次调用拿回全网逐台明细，免去逐设备多次 ADS 读取与字段拼装。\n"
        "- **替代方案对比**：逐台 `FB_PROFINET_READ_*` 调用既多又慢；本 FB 由控制器一次性汇总返回数组。"),
    demo=("""VAR
    fbReadAll     : FB_PN_ReadCompleteInfoOfDevices;
    bReadAllReq   : BOOL := FALSE;            // 在线上升沿触发
    sCtrlName     : T_MaxString := 'Device 1 (PROFINET RT Controller)';  // 控制器在树里的名字
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
    nDevCount     : UINT;                     // 设备总数
    aDevInfo      : ARRAY [1..255] OF ST_PN_DeviceInfo;  // 逐台明细
END_VAR""",
          """// 上升沿触发；读全网逐台明细，超时给 10 秒
fbReadAll(
    bExecute := bReadAllReq,
    sControllerName := sCtrlName,
    tTimeout := T#10S,
    bBusy    => bBusy,
    bError   => bErr,
    nErrorID => nErrId,
    nDevices => nDevCount,
    aInfoOfDevices => aDevInfo
);

// 遍历 1..nDevCount 取每台 aDevInfo[i].sBoxName / sIP_Addr / nCycleTime"""),
    related="`FB_PN_ReadStateOfDevices`（总览计数）、`ST_PN_DeviceInfo`（设备信息结构）",
)

# ============ 3.1.4~3.1.7 Controller 顶层 ============
add(
    name="FB_SET_PN_NAME", topic="15018588555", subdir="controller", section="3.1.4",
    summary=("给指定 PROFINET 设备分配 PROFINET 名称（device name）。分配时必须只使用 PROFINET 合规字符。"
             "通过 `MAC_ID`（设备 MAC 地址）定位目标设备、`PROFINET_NAME` 给出待写名称，控制器经 ADS 把名称写入。"),
    var_input="""VAR_INPUT
  bExecute        : BOOL;
  NETID           : T_AmsNetId;
  PROFINET_NAME   : STRING(51);
  MAC_ID          : ARRAY [0..5] OF BYTE;
END_VAR""",
    input_rows=[
        ("bExecute", "BOOL", D_bStart_edge),
        ("NETID", "T_AmsNetId", D_NETID_ctrl),
        ("PROFINET_NAME", "STRING(51)", "要分配给 PROFINET 设备的名称。最多 240 字符，仅允许字符 "
         "`a..z`、`0..9`、`.`、`-`。"),
        ("MAC_ID", "ARRAY [0..5] OF BYTE", "目标设备的 MAC ID（6 字节）。"),
    ],
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  iErrorID                : UDINT;
END_VAR""",
    output_rows=[("bBusy", "BOOL", D_bBusy), ("bError", "BOOL", D_bError), ("iErrorID", "UDINT", D_iErrorID)],
    behavior=(beh("bExecute", "（无数据输出，仅写入反馈）", "iErrorID")
              + "\n\n**命名规则**：PROFINET 名称只能含小写字母 `a..z`、数字 `0..9`、点 `.` 和连字符 `-`，不能含大写、"
                "空格、下划线等；违规字符会被设备拒绝。**靠 MAC 定位**：本 FB 通过 `MAC_ID` 而非 IP 寻址设备，"
                "因此可在设备尚未配 IP / 名称的「裸」状态下完成首次命名。"),
    notes=[
        "**只用合规字符**：`a..z 0..9 . -`，否则写入失败。",
        "**靠 MAC 寻址**：把 6 字节 MAC 填入 `MAC_ID` 数组（设备铭牌或扫描结果 `str_PN_Scan.MacID` 可得）。",
        "**`PROFINET_NAME` 类型为 `STRING(51)`** 但描述允许最多 240 字符——以代码块声明的 `STRING(51)` 为实际上限。",
    ],
    scenario=(
        "- **场景**：新设备上线或更换备件时，PROFINET 设备出厂无名或名称不符，需要按工位规范分配名称（如 "
        "`line3-io-04`）。\n"
        "- **价值**：PLC 程序在投运流程里按 MAC 自动给设备命名，免去逐台用 TwinCAT/PRONETA 手工设名。\n"
        "- **替代方案对比**：手工命名易出错、难批量；本 FB 可脚本化批量命名，配合 `FB_PN_SCAN` 扫到 MAC 后自动设名。"),
    demo=("""VAR
    fbSetName     : FB_SET_PN_NAME;
    bSetNameReq   : BOOL := FALSE;            // 在线上升沿触发命名
    sNewName      : STRING(51) := 'line3-io-04';      // 合规名称：小写/数字/.-
    aTargetMac    : ARRAY [0..5] OF BYTE := [16#00,16#01,16#05,16#0A,16#1B,16#2C];  // 目标设备 MAC
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
END_VAR""",
          """// 上升沿触发；按 MAC 给设备写入 PROFINET 名称
fbSetName(
    bExecute := bSetNameReq,
    NETID    := '',
    PROFINET_NAME := sNewName,
    MAC_ID   := aTargetMac,
    bBusy    => bBusy,
    bError   => bErr,
    iErrorID => nErrId
);"""),
    related="`FB_PN_SCAN`（扫描得到设备 MAC）、`FB_RESET_PN_TO_FACTORY_SETTINGS`（按 MAC 复位）、`FB_PROFINET_SET_NAME`（设备侧改名）",
)

add(
    name="FB_RESET_PN_TO_FACTORY_SETTINGS", topic="15015894539", subdir="controller", section="3.1.5",
    summary=("把指定 PROFINET 设备复位到厂商出厂设置（factory settings）。通过 `MAC_ID` 定位目标设备，控制器经 "
             "ADS 下发复位命令；复位后设备名称、IP 等配置回到出厂默认。"),
    var_input="""VAR_INPUT
  bExecute        : BOOL;
  NETID           : T_AmsNetId;
  MAC_ID          : ARRAY [0..5] OF BYTE;
END_VAR""",
    input_rows=[
        ("bExecute", "BOOL", D_bStart_edge),
        ("NETID", "T_AmsNetId", D_NETID_ctrl),
        ("MAC_ID", "ARRAY [0..5] OF BYTE", "目标设备的 MAC ID（6 字节）。"),
    ],
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  iErrorID                : UDINT;
END_VAR""",
    output_rows=[("bBusy", "BOOL", D_bBusy), ("bError", "BOOL", D_bError), ("iErrorID", "UDINT", D_iErrorID)],
    behavior=(beh("bExecute", "（无数据输出，仅复位反馈）", "iErrorID")
              + "\n\n**靠 MAC 定位**：和 `FB_SET_PN_NAME` 一样通过 `MAC_ID` 寻址，因此即使设备名称/IP 已被改乱也能复位。"
                "**不可逆操作**：复位会清掉设备名称与 IP 配置，执行后设备需重新命名、重新组态。"),
    notes=[
        "**谨慎触发**：复位会清除设备名称与 IP，导致它暂时脱离组态；务必确认 `MAC_ID` 指向正确设备。",
        "**靠 MAC 寻址**：6 字节 MAC 填入 `MAC_ID`。",
        "**复位后需重新命名**：通常复位 → `FB_SET_PN_NAME` 重新设名 → 重新建立通讯。",
    ],
    scenario=(
        "- **场景**：设备退役/转线、或名称 IP 配错导致冲突，需要把 PROFINET 设备「恢复出厂」后重新组态。\n"
        "- **价值**：PLC 程序按 MAC 远程复位，免去现场插工程软件操作；配合命名 FB 实现「复位→重命名」自动流程。\n"
        "- **替代方案对比**：用 PRONETA/TwinCAT 手工复位需现场操作；本 FB 可远程脚本化。"),
    demo=("""VAR
    fbReset       : FB_RESET_PN_TO_FACTORY_SETTINGS;
    bResetReq     : BOOL := FALSE;            // 在线上升沿触发复位（谨慎！）
    aTargetMac    : ARRAY [0..5] OF BYTE := [16#00,16#01,16#05,16#0A,16#1B,16#2C];  // 目标设备 MAC
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
END_VAR""",
          """// 上升沿触发；按 MAC 把设备复位到出厂设置（清名称/IP）
fbReset(
    bExecute := bResetReq,
    NETID    := '',
    MAC_ID   := aTargetMac,
    bBusy    => bBusy,
    bError   => bErr,
    iErrorID => nErrId
);

// 复位完成后通常再调 FB_SET_PN_NAME 重新命名"""),
    related="`FB_SET_PN_NAME`（复位后重新命名）、`FB_PN_SCAN`（扫描确认设备 MAC）",
)

add(
    name="FB_PN_SCAN", topic="15015749387", subdir="controller", section="3.1.6",
    summary=("扫描 PROFINET 网络并返回找到的设备数量及其信息列表。输出 `iFind_Devices` 给出找到的设备数，"
             "`ar_PN_DEVICE`（`ARRAY [1..100] OF str_PN_SCAN`）逐台给出每个设备的 IP/掩码/网关/MAC/厂商 ID/"
             "设备 ID/PROFINET 名称。"),
    var_input="""VAR_INPUT
  bExecute        : BOOL;
  NETID           : T_AmsNetId;
END_VAR""",
    input_rows=[
        ("bExecute", "BOOL", D_bStart_edge),
        ("NETID", "T_AmsNetId", D_NETID_ctrl),
    ],
    var_output="""VAR_OUTPUT
  iFind_Devices     : INT;
  ar_PN_DEVICE      : ARRAY [1..100] OF str_PN_SCAN;
  bBusy             : BOOL;
  bError            : BOOL;
  iErrorID          : UDINT;
END_VAR""",
    output_rows=[
        ("iFind_Devices", "INT", "扫描到的 PROFINET 设备数。"),
        ("ar_PN_DEVICE", "ARRAY [1..100] OF str_PN_SCAN", "各 PROFINET 设备的 PROFINET/IP 设置（逐台一项）。"),
        ("bBusy", "BOOL", D_bBusy),
        ("bError", "BOOL", D_bError),
        ("iErrorID", "UDINT", D_iErrorID),
    ],
    behavior=(beh("bExecute", "`iFind_Devices` 与 `ar_PN_DEVICE` 数组", "iErrorID")
              + "\n\n**数组容量 100**：`ar_PN_DEVICE` 固定 100 项，只有前 `iFind_Devices` 项有效。若网络设备可能超过 "
                "100 台，请改用 `FB_PN_SCAN_UpTo255`（容量 255）。**扫描得到的 MAC** 可直接喂给 `FB_SET_PN_NAME` / "
                "`FB_RESET_PN_TO_FACTORY_SETTINGS` 做命名/复位。"),
    notes=[
        "**遍历以 `iFind_Devices` 为界**：数组 100 项固定，超出部分无效。",
        "**容量上限 100**：设备多于 100 台用 `FB_PN_SCAN_UpTo255`。",
        "**扫描 ≠ 组态**：扫到的是网络上物理在线的设备（含未组态的），用于发现/命名，不等于 TwinCAT 已组态列表。（工程经验补充）",
    ],
    scenario=(
        "- **场景**：调试或运维时「现场到底挂了哪些 PROFINET 设备」，扫描全网拿到每台的 MAC/IP/名称，做设备发现。\n"
        "- **价值**：一次扫描拿到全网在线设备清单（含未命名的裸设备），是「扫描→命名→组态」自动化投运的第一步。\n"
        "- **替代方案对比**：PRONETA 等工具能扫但脱离 PLC 逻辑；本 FB 让扫描结果直接进 PLC，可联动自动命名。"),
    demo=("""VAR
    fbScan        : FB_PN_SCAN;
    bScanReq      : BOOL := FALSE;            // 在线上升沿触发扫描
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
    iFound        : INT;                      // 扫描到的设备数
    aDevices      : ARRAY [1..100] OF str_PN_SCAN;   // 逐台设备信息
END_VAR""",
          """// 上升沿触发；扫描全网（最多 100 台）
fbScan(
    bExecute := bScanReq,
    NETID    := '',
    iFind_Devices => iFound,
    ar_PN_DEVICE => aDevices,
    bBusy    => bBusy,
    bError   => bErr,
    iErrorID => nErrId
);

// 遍历 1..iFound 取 aDevices[i].MacID / PN_NAME，可喂给 FB_SET_PN_NAME"""),
    related="`FB_PN_SCAN_UpTo255`（容量 255 版）、`str_PN_Scan`（数据结构）、`FB_SET_PN_NAME`（用扫描 MAC 命名）",
)

add(
    name="FB_PN_SCAN_UpTo255", topic=None, subdir="controller", section="3.1.7",
    summary=("扫描 PROFINET 网络并返回找到的设备数量及其信息列表。功能同 `FB_PN_SCAN`，但 `ar_PN_DEVICE` 数组"
             "容量扩大到 255（`ARRAY [1..255] OF str_PN_SCAN`），适用于设备数可能超过 100 的大型网络。"),
    var_input="""VAR_INPUT
  bExecute        : BOOL;
  NETID           : T_AmsNetId;
END_VAR""",
    input_rows=[
        ("bExecute", "BOOL", D_bStart_edge),
        ("NETID", "T_AmsNetId", D_NETID_ctrl),
    ],
    var_output="""VAR_OUTPUT
  iFind_Devices     : INT;
  ar_PN_DEVICE      : ARRAY [1..255] OF str_PN_SCAN;
  bBusy             : BOOL;
  bError            : BOOL;
  iErrorID          : UDINT;
END_VAR""",
    output_rows=[
        ("iFind_Devices", "INT", "扫描到的 PROFINET 设备数。"),
        ("ar_PN_DEVICE", "ARRAY [1..255] OF str_PN_SCAN", "各 PROFINET 设备的 PROFINET/IP 设置（逐台一项，最多 255 台）。"),
        ("bBusy", "BOOL", D_bBusy),
        ("bError", "BOOL", D_bError),
        ("iErrorID", "UDINT", D_iErrorID),
    ],
    behavior=(beh("bExecute", "`iFind_Devices` 与 `ar_PN_DEVICE` 数组（最多 255 项）", "iErrorID")
              + "\n\n**与 `FB_PN_SCAN` 唯一区别是数组容量**：本 FB 为 255，`FB_PN_SCAN` 为 100。其余触发/状态机/用法完全相同。"
                "**版本要求**：本 FB 需库版本 >= v1.5.2.0（开发环境 TwinCAT v3.1.4024.57 及以上）。"),
    notes=[
        "**容量 255**：大型网络（>100 台）用本 FB；中小网络用 `FB_PN_SCAN` 即可。",
        "**遍历以 `iFind_Devices` 为界**：数组 255 项固定，超出无效。",
        "**版本门槛**：需 Tc2_ProfinetDiag >= v1.5.2.0；旧库无此 FB。",
    ],
    scenario=(
        "- **场景**：大型产线/楼宇里 PROFINET 设备数超过 100，需要一次扫全。\n"
        "- **价值**：单次扫描覆盖最多 255 台，免去分批扫描合并。\n"
        "- **替代方案对比**：`FB_PN_SCAN` 仅 100 台不够用；本 FB 是大网络的扫描首选。"),
    demo=("""VAR
    fbScan255     : FB_PN_SCAN_UpTo255;
    bScanReq      : BOOL := FALSE;            // 在线上升沿触发扫描
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
    iFound        : INT;                      // 扫描到的设备数
    aDevices      : ARRAY [1..255] OF str_PN_SCAN;   // 逐台设备信息（最多 255）
END_VAR""",
          """// 上升沿触发；扫描全网（最多 255 台，需库 >= v1.5.2.0）
fbScan255(
    bExecute := bScanReq,
    NETID    := '',
    iFind_Devices => iFound,
    ar_PN_DEVICE => aDevices,
    bBusy    => bBusy,
    bError   => bErr,
    iErrorID => nErrId
);"""),
    related="`FB_PN_SCAN`（容量 100 版）、`str_PN_Scan`（数据结构）",
    not_on_infosys=True,
)

# ============ 3.2.1 Device : EL6631-0010 ============
add(
    name="FB_READ_PROFINET_NAME", topic="15019056267", subdir="device_el6631", section="3.2.1.1",
    summary=("读取 EL6631-0010（PROFINET 设备端子）的 PROFINET 名称；若配置了虚拟 EL6631-0010，也一并读出。"
             "输出 `nCntEL6631_Slave` 指示当前是物理还是虚拟端子，`arPROFINET_NAME`（`ARRAY [1..2] OF "
             "STRING(240)`）给出名称。"),
    var_input=IM_IN_BLOCK, input_rows=IM_IN_ROWS,
    var_output="""VAR_OUTPUT
  bBusy                 : BOOL;
  bError                : BOOL;
  nCntEL6631_Slave      : BYTE
  arPROFINET_NAME       : ARRAY [1..2] OF STRING(240)
END_VAR""",
    output_rows=[
        ("bBusy", "BOOL", D_bBusy),
        ("bError", "BOOL", D_bError),
        ("nCntEL6631_Slave", "BYTE", "指示 EL6631-0010 的呈现方式：`0` = 物理 EL6631-0010，`1` = 虚拟 EL6631-0010。"),
        ("arPROFINET_NAME", "ARRAY [1..2] OF STRING(240)", "EL6631-0010 及（若配置）虚拟 EL6631-0010 的 PROFINET 名称。"),
    ],
    behavior=(beh("bStart", "`nCntEL6631_Slave` 与 `arPROFINET_NAME` 数组", "（本 FB 输出 `bError` 但无 `iErrorID`）")
              + "\n\n**设备侧 FB**：本 FB 用于 EtherCAT 上的 EL6631-0010 PROFINET Device 端子（设备端，区别于 §3.1 的"
                "控制器端 FB）。**双名数组**：一个 EL6631-0010 可映射物理 + 虚拟两个 PROFINET 设备，故名称用 2 元数组返回，"
                "`nCntEL6631_Slave` 指明类型。**注意本 FB 无 `iErrorID` 输出**，只能靠 `bError` 判断成败。"),
    notes=[
        "**专用于 EL6631-0010**：设备端 PROFINET 端子，不是控制器侧 FB。",
        "**无 `iErrorID`**：本 FB 仅有 `bError`，没有错误号输出（与库内多数 FB 不同）。",
        "**PDF 排版怪字**：`nCntEL6631_Slave` 与 `arPROFINET_NAME` 两行末尾在 PDF 中缺分号，按逐字保留。",
    ],
    scenario=(
        "- **场景**：用 EL6631-0010 把 EtherCAT 工位接入上级 PROFINET 网络时，设备端 PLC 需要知道本端子当前的 "
        "PROFINET 名称（供 HMI 显示或与上位组态核对）。\n"
        "- **价值**：直接读出端子的 PROFINET 名称（含虚拟设备），免去查工程组态。\n"
        "- **替代方案对比**：从 EtherCAT CoE/工程软件查名称繁琐；本 FB 在运行时一次读出。"),
    demo=("""VAR
    fbReadPnName  : FB_READ_PROFINET_NAME;
    bReadReq      : BOOL := FALSE;            // 在线上升沿触发
    bBusy         : BOOL;
    bErr          : BOOL;
    nSlaveKind    : BYTE;                     // 0=物理 EL6631 / 1=虚拟
    aPnNames      : ARRAY [1..2] OF STRING(240);   // [1]=物理 [2]=虚拟 名称
END_VAR""",
          """// 上升沿触发；读 EL6631-0010 的 PROFINET 名称（无 iErrorID，靠 bError 判错）
fbReadPnName(
    bStart := bReadReq,
    NETID  := '',
    PORT   := 16#1001,
    bBusy  => bBusy,
    bError => bErr,
    nCntEL6631_Slave => nSlaveKind,
    arPROFINET_NAME => aPnNames
);"""),
    related="`FB_Read_IuM_EL6631_0010` / `FB_Write_IuM_EL6631_0010`（EL6631 的 I&M 读写）",
)

add(
    name="FB_Write_IuM_EL6631_0010", topic="15095638667", subdir="device_el6631", section="3.2.1.2",
    summary=("把 I&M1、I&M2、I&M3、I&M4 数据以字符串形式、经 EtherCAT、按 PROFINET 规范写入 PROFINET 设备"
             "（EL6631-0010）。用 `byState` 的位选择要写哪几项 I&M（Bit0=I&M1…Bit3=I&M4），`iNumber` 选择端子"
             "映射的两个设备之一（0 或 1），各 I&M 文本由对应字符串输入给出。"),
    var_input="""VAR_INPUT
  bWrite            : BOOL;
  NETID             : T_AmsNetId;
  PORT              : T_AmsPort;
  byState           : BYTE;
  iNumber           : INT:=0;
  st_IM_TagFunction : STRING;
  st_IM_TagLocation : STRING;
  st_IM_Date        : STRING;
  st_IM_Descriptor  : STRING;
  st_IM_Signature   : STRING;
END_VAR""",
    input_rows=[
        ("bWrite", "BOOL", "上升沿使能功能块，把 I&M 数据写入所选 PROFINET 设备。"),
        ("NETID", "T_AmsNetId", D_NETID_ctrl),
        ("PORT", "T_AmsPort", D_PORT),
        ("byState", "BYTE", "按位选择写哪几项 I&M：Bit0→I&M1，Bit1→I&M2，Bit2→I&M3，Bit3→I&M4。"),
        ("iNumber", "INT", "一个端子可映射两个 PROFINET 设备，用 `iNumber`（`0` 或 `1`）选择写哪个设备。默认 `0`。"),
        ("st_IM_TagFunction", "STRING", "设备功能标签，写入设备（I&M1，当 `byState.0 = TRUE`）。"),
        ("st_IM_TagLocation", "STRING", "设备安装位置标签，写入设备（I&M1，当 `byState.0 = TRUE`）。"),
        ("st_IM_Date", "STRING", "设备安装日期，写入设备（I&M2，当 `byState.1 = TRUE`）。"),
        ("st_IM_Descriptor", "STRING", "厂商描述，写入设备（I&M3，当 `byState.2 = TRUE`）。"),
        ("st_IM_Signature", "STRING", "厂商签名，写入设备（I&M4，当 `byState.3 = TRUE`）。"),
    ],
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  iErrorID                : UDINT;
END_VAR""",
    output_rows=[("bBusy", "BOOL", D_bBusy), ("bError", "BOOL", D_bError), ("iErrorID", "UDINT", D_iErrorID)],
    behavior=(beh("bWrite", "（无数据输出，仅写入反馈）", "iErrorID")
              + "\n\n**一次写多项**：`byState` 是位掩码，可同时置多位一次写入多项 I&M（如 `byState := 2#0000_0001` 只写 "
                "I&M1，`byState := 2#0000_1111` 写 I&M1~I&M4）。只有被选中位对应的字符串输入才会被写入。"
                "**双设备选择**：EL6631-0010 可映射两个 PROFINET 设备，`iNumber` 选 0 或 1。**经 EtherCAT 写入**：本 FB 是"
                "设备端，数据经 EtherCAT 下发到 EL6631-0010。"),
    notes=[
        "**`byState` 位语义**：Bit0=I&M1 / Bit1=I&M2 / Bit2=I&M3 / Bit3=I&M4，可组合。",
        "**只填被选项**：未在 `byState` 选中的 I&M 对应字符串可不赋值（不会被写）。",
        "**`iNumber` 选设备**：端子映射两台时用 0/1 区分。",
    ],
    scenario=(
        "- **场景**：用 EL6631-0010 做 PROFINET 设备时，设备端 PLC 给自身写入电子铭牌（功能/位置/日期/描述/签名）。\n"
        "- **价值**：一个 FB 用位掩码一次写齐多项 I&M，免去逐项分别写；设备端自管 I&M 数据。\n"
        "- **替代方案对比**：逐项写需多个 FB/多次 ADS；本 FB 用 `byState` 合并一次完成。"),
    demo=("""VAR
    fbWriteIuM    : FB_Write_IuM_EL6631_0010;
    bWriteReq     : BOOL := FALSE;            // 在线上升沿触发
    bySelect      : BYTE := 2#0000_0001;      // 只写 I&M1（Bit0）
    sFunc         : STRING := 'PN-Coupler';
    sLoc          : STRING := 'HallA-Line3';
    sDate         : STRING := '2026-06-02 08:00';
    sDesc         : STRING := '';
    sSig          : STRING := '';
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
END_VAR""",
          """// 上升沿触发；byState=Bit0 表示只写 I&M1（功能/位置标签），iNumber=0 选第一台
fbWriteIuM(
    bWrite := bWriteReq,
    NETID  := '',
    PORT   := 16#1001,
    byState := bySelect,
    iNumber := 0,
    st_IM_TagFunction := sFunc,
    st_IM_TagLocation := sLoc,
    st_IM_Date := sDate,
    st_IM_Descriptor := sDesc,
    st_IM_Signature := sSig,
    bBusy  => bBusy,
    bError => bErr,
    iErrorID => nErrId
);"""),
    related="`FB_Read_IuM_EL6631_0010`（读 EL6631 的 I&M）、`FB_READ_PROFINET_NAME`",
)

add(
    name="FB_Read_IuM_EL6631_0010", topic="15095820299", subdir="device_el6631", section="3.2.1.3",
    summary=("从 PROFINET 设备（EL6631-0010）经 EtherCAT 以字符串形式读取 I&M1、I&M2、I&M3、I&M4 数据；"
             "I&M0 数据则通过 CoE（CAN over EtherCAT）读取。`iNumber` 选择端子映射的两台设备之一（0 或 1），"
             "读回的功能/位置/日期/描述/签名分别通过各 STRING 输出给出。"),
    var_input="""VAR_INPUT
  bRead             : BOOL;;
  NETID             : T_AmsNetId;
  PORT              : T_AmsPort;
  iNumber           : INT:=0;
END_VAR""",
    input_rows=[
        ("bRead", "BOOL", "上升沿使能功能块，从 PROFINET 设备读取 I&M 数据。⚠️ PDF 原文此行印作 `bRead : BOOL;;`（多一分号）。"),
        ("NETID", "T_AmsNetId", D_NETID_ctrl),
        ("PORT", "T_AmsPort", D_PORT),
        ("iNumber", "INT", "一个端子可映射两个 PROFINET 设备，用 `iNumber`（`0` 或 `1`）选择读哪个设备。默认 `0`。"),
    ],
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  iErrorID                : UDINT;
  st_IM_TagFunction       : STRING; (* I&M1 *)
  st_IM_TagLocation       : STRING; (* I&M1 *)
  st_IM_Date              : STRING; (* I&M2 *)
  st_IM_Descriptor        : STRING; (* I&M3 *)
  st_IM_Signature         : STRING; (* I&M4 *)
END_VAR""",
    output_rows=[
        ("bBusy", "BOOL", D_bBusy),
        ("bError", "BOOL", D_bError),
        ("iErrorID", "UDINT", D_iErrorID),
        ("st_IM_TagFunction", "STRING", "读回的设备功能标签（I&M1）。"),
        ("st_IM_TagLocation", "STRING", "读回的设备安装位置标签（I&M1）。"),
        ("st_IM_Date", "STRING", "读回的设备安装日期（I&M2）。"),
        ("st_IM_Descriptor", "STRING", "读回的厂商描述（I&M3）。"),
        ("st_IM_Signature", "STRING", "读回的厂商签名（I&M4）。"),
    ],
    behavior=(beh("bRead", "五个 I&M 字符串输出（功能/位置/日期/描述/签名）", "iErrorID")
              + "\n\n**一次读齐 I&M1~I&M4**：本 FB 一次把 I&M1~I&M4 五段文本全部读回（不像控制器侧按记录分多个 FB）。"
                "I&M0 走 CoE 单独读取（不在本 FB 输出里）。**双设备选择**：`iNumber` 选 0/1。**经 EtherCAT 读取**：设备端 FB。"),
    notes=[
        "**一次读齐**：I&M1~I&M4 全部经一次调用读回（设备端便利封装）。",
        "**I&M0 走 CoE**：本 FB 不含 I&M0；I&M0 通过 CoE 单独读。",
        "**PDF 排版怪字**：输入 `bRead` 行 PDF 印作 `bRead : BOOL;;`（多一个分号），按逐字保留，类型为 `BOOL`。",
    ],
    scenario=(
        "- **场景**：EL6631-0010 设备端 PLC 读回自身或对端写入的电子铭牌，做自检或上报 HMI。\n"
        "- **价值**：一次读齐 I&M1~I&M4 五段文本，免去逐项读取。\n"
        "- **替代方案对比**：逐项读需多次调用；本 FB 一次完成，配合 `FB_Write_IuM_EL6631_0010` 形成读写对。"),
    demo=("""VAR
    fbReadIuM     : FB_Read_IuM_EL6631_0010;
    bReadReq      : BOOL := FALSE;            // 在线上升沿触发
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
    sFunc         : STRING;                   // I&M1 功能
    sLoc          : STRING;                   // I&M1 位置
    sDate         : STRING;                   // I&M2 日期
    sDesc         : STRING;                   // I&M3 描述
    sSig          : STRING;                   // I&M4 签名
END_VAR""",
          """// 上升沿触发；一次读齐 I&M1~I&M4（iNumber=0 选第一台）
fbReadIuM(
    bRead  := bReadReq,
    NETID  := '',
    PORT   := 16#1001,
    iNumber := 0,
    bBusy  => bBusy,
    bError => bErr,
    iErrorID => nErrId,
    st_IM_TagFunction => sFunc,
    st_IM_TagLocation => sLoc,
    st_IM_Date => sDate,
    st_IM_Descriptor => sDesc,
    st_IM_Signature => sSig
);"""),
    related="`FB_Write_IuM_EL6631_0010`（写 EL6631 的 I&M）、`FB_READ_PROFINET_NAME`",
)

# ============ 3.2.2 Device via CCAT (CX-B930, TF6270) ============
add(
    name="FB_PROFINET_READ_IM", topic="15018619915", subdir="device_ccat", section="3.2.2.1",
    summary=("返回指定 PROFINET 设备的 I&M（Identification & Maintenance）数据。用于经 CCAT（CX-B930）/ TF6270 "
             "的 PROFINET 设备。读到的 I&M 信息（功能/位置/日期/描述/签名）封装在结构 `str_IuM_Data` 中一次返回。"),
    var_input=IM_IN_BLOCK, input_rows=IM_IN_ROWS,
    var_output="""VAR_OUTPUT
  str_IuM_Data            : str_IuM_Data
  bBusy                   : BOOL;
  bError                  : BOOL;
  nErrorID                : UDINT;
END_VAR""",
    output_rows=[
        ("str_IuM_Data", "str_IuM_Data", "含 I&M 数据的结构元素（功能/位置/日期/描述/签名 5 个字符串字段）。"),
        ("bBusy", "BOOL", D_bBusy),
        ("bError", "BOOL", D_bError),
        ("nErrorID", "UDINT", "`bError` 置位时返回 ADS 错误号（见 §4）。"),
    ],
    behavior=beh("bStart", "`str_IuM_Data` 结构", "nErrorID"),
    notes=[
        "**用于 CCAT/TF6270 设备**：`Device via CCAT (CX-B930, TF6270)` 这组 FB 面向 CCAT PROFINET 接口或 TF6270 软件设备。",
        "**结构一次返回**：I&M 各字段在 `str_IuM_Data` 中，免去逐项读。",
        "**PDF 排版怪字**：`str_IuM_Data` 输出行 PDF 末尾缺分号，按逐字保留。",
    ] + NOTE_COMMON[:1],
    scenario=(
        "- **场景**：基于 CX-B930（CCAT PROFINET 接口）或 TF6270 软 PLC PROFINET 的设备端，读出自身 I&M 电子铭牌。\n"
        "- **价值**：一次返回 I&M 结构，免去逐项解析。\n"
        "- **替代方案对比**：逐项读繁琐；本 FB 结构化一次返回。"),
    demo=("""VAR
    fbReadIM      : FB_PROFINET_READ_IM;
    bReadReq      : BOOL := FALSE;            // 在线上升沿触发
    stIuM         : str_IuM_Data;             // I&M 数据结构
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
END_VAR""",
          """// 上升沿触发；读 CCAT/TF6270 设备的 I&M 数据结构
fbReadIM(
    bStart := bReadReq,
    NETID  := '',
    PORT   := 16#1001,
    str_IuM_Data => stIuM,
    bBusy  => bBusy,
    bError => bErr,
    nErrorID => nErrId
);"""),
    related="`FB_PROFINET_WRITE_IM`（写 I&M）、`str_IuM_Data`（数据结构）",
)

add(
    name="FB_PROFINET_READ_NAME", topic="15958916491", subdir="device_ccat", section="3.2.2.2",
    summary=("返回指定 PROFINET 设备的 PROFINET 名称，以及该名称是否可被 PROFINET 控制器修改的信息。"
             "输出 `sProfinetName` 给出设备名，`bNotChangeable = TRUE` 表示控制器不能改这个名称。"),
    var_input=IM_IN_BLOCK,
    input_rows=[
        ("bStart", "BOOL", D_bStart_edge),
        ("NETID", "T_AmsNetId", "PROFINET 设备的 AMS Net ID。"),
        ("PORT", "T_AmsPort", "PROFINET 设备的 ADS 端口号；默认 `0xFFFF`。"),
    ],
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  nErrorID                : UDINT;
  sProfinetName           : STRING(240);
  bNotChangeable          : BOOL;
END_VAR""",
    output_rows=[
        ("bBusy", "BOOL", D_bBusy),
        ("bError", "BOOL", D_bError),
        ("nErrorID", "UDINT", "`bError` 置位时返回 ADS 错误号（见 §4）。"),
        ("sProfinetName", "STRING(240)", "PROFINET 设备名。最多 240 字符，仅允许 `a..z`、`0..9`、`.`、`-`。"),
        ("bNotChangeable", "BOOL", "为 `TRUE` 时表示 PROFINET 控制器不能更改该设备的 PROFINET 名称。"),
    ],
    behavior=(beh("bStart", "`sProfinetName` 与 `bNotChangeable`", "nErrorID")
              + "\n\n**端口默认 `0xFFFF`**：本组（CCAT/TF6270 设备）FB 的 `PORT` 默认值为 `0xFFFF`（与控制器侧 FB 的 "
                "`Device ID + 1000hex` 寻址不同，注意区分）。**`bNotChangeable` 用途**：在调用 `FB_PROFINET_SET_NAME` 改名"
                "前先读该位，若为 TRUE 说明设备锁定了名称，改名会失败。"),
    notes=[
        "**`PORT` 默认 `0xFFFF`**：CCAT/TF6270 设备组的端口语义与控制器侧不同。",
        "**先查 `bNotChangeable` 再改名**：避免对锁定名称的设备做无效改名。",
        "**版本要求**：本 FB 需库版本 >= v1.5.1.0（开发环境 TwinCAT v3.1.4024.55 及以上）。",
    ],
    scenario=(
        "- **场景**：CCAT/TF6270 设备端读自身 PROFINET 名称并判断是否允许被上位改名，供 HMI 显示与改名前校验。\n"
        "- **价值**：一次拿到名称 + 可改性标志，改名流程更安全。\n"
        "- **替代方案对比**：盲目改名可能失败；先读 `bNotChangeable` 可避免。"),
    demo=("""VAR
    fbReadName    : FB_PROFINET_READ_NAME;
    bReadReq      : BOOL := FALSE;            // 在线上升沿触发
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
    sPnName       : STRING(240);              // 设备 PROFINET 名
    bLocked       : BOOL;                     // TRUE=控制器不能改名
END_VAR""",
          """// 上升沿触发；读设备名 + 可改性标志（PORT 默认 0xFFFF）
fbReadName(
    bStart := bReadReq,
    NETID  := '',
    PORT   := 16#FFFF,
    bBusy  => bBusy,
    bError => bErr,
    nErrorID => nErrId,
    sProfinetName => sPnName,
    bNotChangeable => bLocked
);"""),
    related="`FB_PROFINET_SET_NAME`（改名）、`FB_READ_PROFINET_NAME`（EL6631 设备名）",
    not_on_infosys=False,
)

add(
    name="FB_PROFINET_READ_PRM", topic="15018720907", subdir="device_ccat", section="3.2.2.3",
    summary=("扫描 PROFINET 网络并返回找到的设备数量及其信息列表（用于 CCAT/TF6270 设备）。读到的 PROFINET/IP "
             "设置封装在结构 `str_Diag_PN_Settings` 中返回（IP/掩码/网关/PROFINET 名）。"),
    var_input="""VAR_INPUT
  NETID   : T_AmsNetId;
  PORT    : T_AmsPort;
  bStart  : BOOL;
END_VAR""",
    input_rows=[
        ("NETID", "T_AmsNetId", D_NETID_ctrl),
        ("PORT", "T_AmsPort", D_PORT),
        ("bStart", "BOOL", D_bStart_edge),
    ],
    var_output="""VAR_OUTPUT
  str_Diag_PN_Settings    : str_Diag_PN_Settings;
  bBusy                   : BOOL;
  bError                  : BOOL;
  nErrorID                : UDINT;
END_VAR""",
    output_rows=[
        ("str_Diag_PN_Settings", "str_Diag_PN_Settings", "PROFINET/IP 设置（IP 地址、子网掩码、默认网关、PROFINET 名）。"),
        ("bBusy", "BOOL", D_bBusy),
        ("bError", "BOOL", D_bError),
        ("nErrorID", "UDINT", "`bError` 置位时返回 ADS 错误号（见 §4）。"),
    ],
    behavior=(beh("bStart", "`str_Diag_PN_Settings` 结构", "nErrorID")
              + "\n\n**注意输入顺序**：本 FB 的 VAR_INPUT 顺序为 `NETID, PORT, bStart`（`bStart` 在最后），"
                "与库内多数 FB（`bStart` 在首）不同，逐字保留。**PRM = parameter**：读回设备的 PROFINET/IP 参数设置。"),
    notes=[
        "**输入顺序特殊**：`NETID → PORT → bStart`（触发在最后一位），调用时按名赋值即可避免顺序坑。",
        "**结果是 IP 设置**：`str_Diag_PN_Settings` 给 IP/掩码/网关/名称。",
    ] + NOTE_COMMON[:1],
    scenario=(
        "- **场景**：CCAT/TF6270 设备端读取本设备永久存储的 IP 参数（IP/掩码/网关/名），用于网络配置核对。\n"
        "- **价值**：一次读回 IP 设置结构，免去逐项查询。\n"
        "- **替代方案对比**：从工程组态查 IP 脱离运行时；本 FB 在线读实际值。"),
    demo=("""VAR
    fbReadPrm     : FB_PROFINET_READ_PRM;
    bReadReq      : BOOL := FALSE;            // 在线上升沿触发
    stPnSettings  : str_Diag_PN_Settings;     // IP/掩码/网关/名
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
END_VAR""",
          """// 上升沿触发；读设备 PROFINET/IP 参数设置
fbReadPrm(
    NETID  := '',
    PORT   := 16#1001,
    bStart := bReadReq,
    str_Diag_PN_Settings => stPnSettings,
    bBusy  => bBusy,
    bError => bErr,
    nErrorID => nErrId
);"""),
    related="`str_Diag_PN_Settings`（数据结构）、`FB_PN_SCAN`（控制器侧扫描）",
)

add(
    name="FB_PROFINET_WRITE_IM", topic="15018890635", subdir="device_ccat", section="3.2.2.4",
    summary=("把指定 PROFINET 设备的 I&M（Identification & Maintenance）数据写入设备（用于 CCAT/TF6270 设备）。"
             "待写的 I&M 各字段（功能/位置/日期/描述/签名）由输入结构 `str_IuM_Data` 一次给出。"),
    var_input="""VAR_INPUT
  bStart       : BOOL;
  NETID        : T_AmsNetId;
  PORT         : T_AmsPort;
  str_IuM_Data : str_IuM_Data
END_VAR""",
    input_rows=[
        ("bStart", "BOOL", D_bStart_edge),
        ("NETID", "T_AmsNetId", D_NETID_ctrl),
        ("PORT", "T_AmsPort", D_PORT),
        ("str_IuM_Data", "str_IuM_Data", "含待写 I&M 数据的结构元素（功能/位置/日期/描述/签名）。"),
    ],
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  nErrorID                : UDINT;
END_VAR""",
    output_rows=[
        ("bBusy", "BOOL", D_bBusy),
        ("bError", "BOOL", D_bError),
        ("nErrorID", "UDINT", "`bError` 置位时返回 ADS 错误号（见 §4）。"),
    ],
    behavior=(beh("bStart", "（无数据输出，仅写入反馈）", "nErrorID")
              + "\n\n**结构化一次写**：把 I&M 各字段填进 `str_IuM_Data` 结构后一次写入，免去逐项写。**与 READ 配对**："
                "通常先 `FB_PROFINET_READ_IM` 读出结构、改字段、再用本 FB 写回。**PDF 排版怪字**：输入 `str_IuM_Data` 行末缺分号，逐字保留。"),
    notes=[
        "**与 READ 配对使用**：读出结构 → 改字段 → 写回，避免漏填导致清空其它字段。（工程经验补充）",
        "**用于 CCAT/TF6270 设备**。",
    ] + NOTE_COMMON[:1],
    scenario=(
        "- **场景**：CCAT/TF6270 设备端给自身写入电子铭牌（功能/位置/日期/描述/签名）。\n"
        "- **价值**：结构化一次写齐 I&M，免去逐项写。\n"
        "- **替代方案对比**：逐项写繁琐；本 FB 结构化一次完成。"),
    demo=("""VAR
    fbReadIM      : FB_PROFINET_READ_IM;       // 先读出原 I&M 结构
    fbWriteIM     : FB_PROFINET_WRITE_IM;      // 改完字段写回
    bReadReq      : BOOL := FALSE;
    bWriteReq     : BOOL := FALSE;             // 在线上升沿触发写入
    stIuM         : str_IuM_Data;              // I&M 结构（读后改、改后写）
    bRdBusy, bWrBusy, bRdErr, bWrErr : BOOL;
    nRdErr, nWrErr : UDINT;
END_VAR""",
          """// 先读出原结构（避免写回时清空未改字段）
fbReadIM(bStart := bReadReq, NETID := '', PORT := 16#1001,
    str_IuM_Data => stIuM, bBusy => bRdBusy, bError => bRdErr, nErrorID => nRdErr);

// 改字段后写回（此处示例直接写）
stIuM.st_IM_TagFunction := 'PN-Device-B930';
fbWriteIM(
    bStart := bWriteReq,
    NETID  := '',
    PORT   := 16#1001,
    str_IuM_Data := stIuM,
    bBusy  => bWrBusy,
    bError => bWrErr,
    nErrorID => nWrErr
);"""),
    related="`FB_PROFINET_READ_IM`（读 I&M）、`str_IuM_Data`（数据结构）",
)

add(
    name="FB_PROFINET_SET_NAME", topic="15959467915", subdir="device_ccat", section="3.2.2.5",
    summary=("更改指定 PROFINET 设备的 PROFINET 名称（用于 CCAT/TF6270 设备）。要求 PROFINET 驱动版本 06"
             "（V00.34）及以上、TF6270、CCAT PN Interface(B930)。`sProfinetName` 给出新名，`bNotChangeable` 可设置"
             "名称是否禁止再被控制器更改。"),
    var_input="""VAR_INPUT
  bStart           : BOOL;
  NETID            : T_AmsNetId;
  PORT             : T_AmsPort;
  sProfinetName    : STRING(240);
  bNotChangeable   : BOOL;
END_VAR""",
    input_rows=[
        ("bStart", "BOOL", D_bStart_edge),
        ("NETID", "T_AmsNetId", "PROFINET 设备的 AMS Net ID。"),
        ("PORT", "T_AmsPort", "PROFINET 设备的 ADS 端口号；默认 `0xFFFF`。"),
        ("sProfinetName", "STRING(240)", "PROFINET 设备名。最多 240 字符，仅允许 `a..z`、`0..9`、`.`、`-`。"),
        ("bNotChangeable", "BOOL", "为 `TRUE` 时表示 PROFINET 控制器今后不能再更改该 PROFINET 名称。"),
    ],
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  nErrorID                : UDINT;
END_VAR""",
    output_rows=[
        ("bBusy", "BOOL", D_bBusy),
        ("bError", "BOOL", D_bError),
        ("nErrorID", "UDINT", "`bError` 置位时返回 ADS 错误号（见 §4）。"),
    ],
    behavior=(beh("bStart", "（无数据输出，仅改名反馈）", "nErrorID")
              + "\n\n**命名规则同 `FB_SET_PN_NAME`**：只允许 `a..z 0..9 . -`。**`bNotChangeable` 是写锁**：写 TRUE 后该名称"
                "被锁定，控制器无法再改（可先用 `FB_PROFINET_READ_NAME` 读该位确认状态）。**版本/硬件门槛**：需 PROFINET 驱动 "
                "06（V00.34）+、TF6270、CCAT PN Interface(B930)。"),
    notes=[
        "**版本/硬件要求**：驱动 06（V00.34）以上 + TF6270 + CCAT B930；库版本 >= v1.5.1.0。",
        "**`bNotChangeable` 慎用**：置 TRUE 会锁死名称，后续无法用控制器改名。",
        "**`PORT` 默认 `0xFFFF`**（设备组语义）。",
    ],
    scenario=(
        "- **场景**：CCAT/TF6270 设备端在投运时给自身写入规范的 PROFINET 名称，并可选地锁定防止误改。\n"
        "- **价值**：设备端自助改名，免去依赖上位控制器命名；可锁名防误操作。\n"
        "- **替代方案对比**：控制器侧 `FB_SET_PN_NAME` 靠 MAC 改名；本 FB 是设备端自改名（CCAT/TF6270 专用）。"),
    demo=("""VAR
    fbSetName     : FB_PROFINET_SET_NAME;
    bSetReq       : BOOL := FALSE;            // 在线上升沿触发改名
    sNewName      : STRING(240) := 'b930-dev-01';     // 合规新名
    bLockName     : BOOL := FALSE;            // 是否锁定名称（慎用）
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
END_VAR""",
          """// 上升沿触发；设备端自改 PROFINET 名（需驱动 06/V00.34+、TF6270、CCAT B930）
fbSetName(
    bStart := bSetReq,
    NETID  := '',
    PORT   := 16#FFFF,
    sProfinetName := sNewName,
    bNotChangeable := bLockName,
    bBusy  => bBusy,
    bError => bErr,
    nErrorID => nErrId
);"""),
    related="`FB_PROFINET_READ_NAME`（读名+可改性）、`FB_SET_PN_NAME`（控制器侧按 MAC 命名）",
)

# ============ 3.2.3 FB_PN_SEND_ALARM ============
add(
    name="FB_PN_SEND_ALARM", topic="15588711819", subdir="device", section="3.2.3",
    summary=("（设备侧）向 PROFINET 控制器发送一条报警。通过 `PN_ALARM_Typ`（枚举 `E_PN_ALARM_TYP`，预定义报警"
             "类型）、`PN_slotNumber`（槽号）、`PN_SubSlotNumber`（子槽号）指定报警内容，上升沿触发发送。"),
    var_input="""VAR_INPUT
  bStart           : BOOL;
  NETID            : T_AmsNetId;
  PORT             : T_AmsPort;
  PN_ALARM_Typ     : E_PN_ALARM_TYP;
  PN_slotNumber    : WORD;
  PN_SubSlotNumber : WORD;
END_VAR""",
    input_rows=[
        ("bStart", "BOOL", D_bStart_edge),
        ("NETID", "T_AmsNetId", D_NETID_ctrl),
        ("PORT", "T_AmsPort", D_PORT),
        ("PN_ALARM_Typ", "E_PN_ALARM_TYP", "报警类型，取自枚举 `E_PN_ALARM_TYP`（含 `PN_ALARM_PROCESS`、"
         "`PN_ALARM_PULL`、`PN_ALARM_PLUG` 等预定义类型）。"),
        ("PN_slotNumber", "WORD", "槽号（slot number）。"),
        ("PN_SubSlotNumber", "WORD", "子槽号（subslot number）。"),
    ],
    var_output="""VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  iErrorID                : UDINT;
END_VAR""",
    output_rows=[("bBusy", "BOOL", D_bBusy), ("bError", "BOOL", D_bError), ("iErrorID", "UDINT", D_iErrorID)],
    behavior=(beh("bStart", "（无数据输出，仅发送反馈）", "iErrorID")
              + "\n\n**设备 → 控制器方向**：本 FB 是设备端主动向控制器报警（与 `FB_PN_ALARM_DIAG` 读报警方向相反）。"
                "**报警定位**：用 `PN_slotNumber` / `PN_SubSlotNumber` 告诉控制器是哪个槽/子槽出的问题，报警类型取 "
                "`E_PN_ALARM_TYP` 枚举值。**典型场景**：模块拔出（`PN_ALARM_PULL`）、插入（`PN_ALARM_PLUG`）、过程报警"
                "（`PN_ALARM_PROCESS`）等。"),
    notes=[
        "**方向是「发」不是「收」**：设备端用本 FB 主动报警；控制器端用 `FB_PN_ALARM_DIAG` 读报警。",
        "**报警类型用枚举**：`PN_ALARM_Typ` 必须取 `E_PN_ALARM_TYP` 中的值，不要硬填裸数字。",
        "**槽/子槽要对应真实模块位置**，否则控制器侧无法正确定位报警源。（工程经验补充）",
    ],
    scenario=(
        "- **场景**：用 EL6631-0010 / CCAT 做 PROFINET 设备时，设备端检测到内部异常（如某模块被拔出、过程量越限），"
        "需要主动向上级 PROFINET 控制器报警，让上位系统记录并响应。\n"
        "- **价值**：把 PROFINET 报警发送封装为一次调用，设备端只需选报警类型 + 槽号即可，免去手工拼报警帧。\n"
        "- **替代方案对比**：自己拼 PROFINET 报警帧经 ADS 发送工作量大；本 FB 用枚举 + 槽号一次发出。"),
    demo=("""VAR
    fbSendAlarm   : FB_PN_SEND_ALARM;
    bSendReq      : BOOL := FALSE;            // 在线上升沿触发发送报警
    eAlarmType    : E_PN_ALARM_TYP := PN_ALARM_PROCESS;  // 过程报警
    wSlot         : WORD := 1;                // 报警所在槽号
    wSubSlot      : WORD := 1;                // 报警所在子槽号
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
END_VAR""",
          """// 上升沿触发；设备端向控制器发一条过程报警（槽1/子槽1）
fbSendAlarm(
    bStart := bSendReq,
    NETID  := '',
    PORT   := 16#1001,
    PN_ALARM_Typ := eAlarmType,
    PN_slotNumber := wSlot,
    PN_SubSlotNumber := wSubSlot,
    bBusy  => bBusy,
    bError => bErr,
    iErrorID => nErrId
);"""),
    related="`FB_PN_ALARM_DIAG`（控制器侧读报警）、`E_PN_ALARM_TYP`（报警类型枚举）",
)

# ============ 3.3 / 3.4 Port diagnosis ============
add(
    name="FB_PN_GET_PORT_STATISTIC", topic="14966141067", subdir="port_diagnosis", section="3.3",
    summary=("读取 PROFINET 设备各端口的统计数据。调用后通过 `str_RemotePort_1` / `str_RemotePort_2`"
             "（`str_GetPortStatistic`）分别给出端口 1、端口 2 的速率、收发字节/包计数、坏包/丢帧数等统计；"
             "`bPort1` / `bPort2` 指示对应端口是否有链路（link）。"),
    var_input="""VAR_INPUT
  bStart       : BOOL;
  NETID        : T_AmsNetId;
  PORT         : T_AmsPort;
END_VAR""",
    input_rows=[
        ("bStart", "BOOL", D_bStart_edge),
        ("NETID", "T_AmsNetId", D_NETID_ctrl),
        ("PORT", "T_AmsPort", D_PORT),
    ],
    var_output="""VAR_OUTPUT
  bBusy             : BOOL;
  str_RemotePort_1  : str_GetPortStatistic;
  str_RemotePort_2  : str_GetPortStatistic;
  bPort1            : BOOL;
  bPort2            : BOOL;
END_VAR""",
    output_rows=[
        ("bBusy", "BOOL", D_bBusy),
        ("str_RemotePort_1", "str_GetPortStatistic", "端口 1 的统计数据结构（速率、收发字节/包、坏包、丢帧等）。"),
        ("str_RemotePort_2", "str_GetPortStatistic", "端口 2 的统计数据结构（同上）。"),
        ("bPort1", "BOOL", "端口 1 有链路（link）时为 `TRUE`。"),
        ("bPort2", "BOOL", "端口 2 有链路（link）时为 `TRUE`。"),
    ],
    behavior=(beh("bStart", "`str_RemotePort_1` / `str_RemotePort_2` 与 `bPort1` / `bPort2`", "（本 FB 无错误号输出）")
              + "\n\n**注意本 FB 无 `bError`/`iErrorID` 输出**（PDF/InfoSys 输出表仅 5 项）。**链路标志**：先看 "
                "`bPort1`/`bPort2` 判断端口是否插了线，再看对应统计结构。**统计用途**：`RxBadPackets`/`RxDroppedFrames` 等"
                "计数持续增长往往预示线缆/连接器质量问题，是诊断「偶发丢包」的关键依据。"),
    notes=[
        "**无错误输出**：本 FB 只有 `bBusy` 三态中的 busy + 数据输出，没有 `bError`/错误号。",
        "**先判 link 再看统计**：`bPortN = FALSE` 时该端口统计无意义（没插线）。",
        "**坏包/丢帧计数是趋势量**：单次值意义不大，要看随时间增长速度判断链路质量。（工程经验补充）",
    ],
    scenario=(
        "- **场景**：PROFINET 网络偶发抖动/丢包，怀疑某段线缆或端口质量差。运维读取设备端口统计，看坏包/丢帧计数"
        "在哪个端口持续增长，定位物理层问题。\n"
        "- **价值**：把端口级网络质量统计读进 PLC，可做趋势记录和阈值报警，免去靠交换机网管口逐个查。\n"
        "- **替代方案对比**：网管交换机能看端口统计但脱离 PLC 逻辑；本 FB 让统计进 PLC，可联动报警与记录。"),
    demo=("""VAR
    fbGetStat     : FB_PN_GET_PORT_STATISTIC;
    bGetReq       : BOOL := FALSE;            // 在线上升沿触发读取
    bBusy         : BOOL;
    stPort1       : str_GetPortStatistic;     // 端口1统计
    stPort2       : str_GetPortStatistic;     // 端口2统计
    bP1Link       : BOOL;                     // 端口1有链路
    bP2Link       : BOOL;                     // 端口2有链路
END_VAR""",
          """// 上升沿触发；读端口统计（先看 bP1/bP2 link，再看坏包/丢帧计数）
fbGetStat(
    bStart := bGetReq,
    NETID  := '',
    PORT   := 16#1001,
    bBusy  => bBusy,
    str_RemotePort_1 => stPort1,
    str_RemotePort_2 => stPort2,
    bPort1 => bP1Link,
    bPort2 => bP2Link
);

// 趋势监控示例：stPort1.RxBadPackets / stPort1.RxDroppedFrames 持续增长 = 链路质量差"""),
    related="`FB_PN_READ_PORT_DIAG`（读端口诊断/拓扑）、`str_GetPortStatistic`（数据结构）",
)

add(
    name="FB_PN_READ_PORT_DIAG", topic="14966195083", subdir="port_diagnosis", section="3.4",
    summary=("读取 PROFINET 设备各端口的诊断信息。调用后通过 `str_RemotePort_1` / `str_RemotePort_2` 给出端口 1、"
             "端口 2 的诊断/邻居信息。注：PDF 中本 FB 的输出结构类型印作 `str_GetPortStatistic`（逐字保留），"
             "承载端口的统计/诊断数据。"),
    var_input="""VAR_INPUT
  bStart       : BOOL;
  NETID        : T_AmsNetId;
  PORT         : T_AmsPort;
END_VAR""",
    input_rows=[
        ("bStart", "BOOL", D_bStart_edge),
        ("NETID", "T_AmsNetId", D_NETID_ctrl),
        ("PORT", "T_AmsPort", D_PORT),
    ],
    var_output="""VAR_OUTPUT
  bBusy             : BOOL;
  str_RemotePort_1  : str_GetPortStatistic;
  str_RemotePort_2  : str_GetPortStatistic;
END_VAR""",
    output_rows=[
        ("bBusy", "BOOL", D_bBusy),
        ("str_RemotePort_1", "str_GetPortStatistic", "端口 1 的诊断数据结构。⚠️ PDF/InfoSys 此输出类型印作 "
         "`str_GetPortStatistic`（端口诊断帧 `str_PortDiag` 含 PortId/邻居名/描述等，类型以代码块逐字为准）。"),
        ("str_RemotePort_2", "str_GetPortStatistic", "端口 2 的诊断数据结构（同上）。"),
    ],
    behavior=(beh("bStart", "`str_RemotePort_1` / `str_RemotePort_2`", "（本 FB 无错误号输出）")
              + "\n\n**与 `FB_PN_GET_PORT_STATISTIC` 的区别**：后者侧重端口流量统计（含 link 标志 `bPort1/2`），本 FB 侧重端口"
                "诊断/拓扑邻居信息。**注意本 FB 同样无 `bError`/`iErrorID` 输出**，且无 `bPort1/2` 链路标志。**PDF 类型怪字**："
                "输出结构在 PDF 中印作 `str_GetPortStatistic`（库里另有 `str_PortDiag` 结构含 PortId/SystemName/ChassisId 等"
                "拓扑字段），代码块按 PDF 逐字保留。"),
    notes=[
        "**无错误/链路输出**：仅 `bBusy` + 两个端口结构。",
        "**侧重拓扑/邻居诊断**：与端口统计 FB 互补，一个看流量、一个看诊断。",
        "**PDF 类型印为 `str_GetPortStatistic`**：库内另有 `str_PortDiag`（PortId/邻居信息），代码块逐字保留 PDF 写法。",
    ] + NOTE_COMMON[:1],
    scenario=(
        "- **场景**：排查 PROFINET 拓扑接错（某端口接到了非预期邻居）或链路诊断，读出端口诊断信息核对实际拓扑。\n"
        "- **价值**：把端口诊断读进 PLC，可与组态拓扑比对，自动发现接线错误。\n"
        "- **替代方案对比**：靠人对照接线图易错；本 FB 让 PLC 读实际端口诊断做自动核对。"),
    demo=("""VAR
    fbReadDiag    : FB_PN_READ_PORT_DIAG;
    bReadReq      : BOOL := FALSE;            // 在线上升沿触发
    bBusy         : BOOL;
    stPort1       : str_GetPortStatistic;     // 端口1诊断
    stPort2       : str_GetPortStatistic;     // 端口2诊断
END_VAR""",
          """// 上升沿触发；读两个端口的诊断信息（无错误号输出，按 PDF 类型为 str_GetPortStatistic）
fbReadDiag(
    bStart := bReadReq,
    NETID  := '',
    PORT   := 16#1001,
    bBusy  => bBusy,
    str_RemotePort_1 => stPort1,
    str_RemotePort_2 => stPort2
);"""),
    related="`FB_PN_GET_PORT_STATISTIC`（端口流量统计）、`str_PortDiag` / `str_GetPortStatistic`（数据结构）",
)


# ---------------------------------------------------------------------------
# 渲染
# ---------------------------------------------------------------------------
def infosys_url(fb):
    if fb.get("topic"):
        return INFOSYS_BASE + fb["topic"] + ".html"
    return None


def render_doc(fb) -> str:
    name = fb["name"]
    iurl = infosys_url(fb)
    not_oi = fb.get("not_on_infosys") or (iurl is None)
    # 未单独收录的条目（如 FB_PN_SCAN_UpTo255）：Source InfoSys 指向库「Function blocks」
    # 父 topic（有效 topic URL 格式），InfoSys-checked 标 not-on-infosys。
    FB_PARENT_TOPIC = INFOSYS_BASE + "14965545483.html"
    src_info = iurl if iurl else FB_PARENT_TOPIC
    info_checked = "⚠️ not-on-infosys" if not_oi else f"✅ {TODAY}"

    # 输入表
    in_rows = "\n".join(f"| `{n}` | `{t}` | {d} |" for n, t, d in fb["input_rows"])
    out_rows = "\n".join(f"| `{n}` | `{t}` | {d} |" for n, t, d in fb["output_rows"])

    # 错误码段：用本 FB 实际错误号变量名
    errvar = "nErrorID" if any(n == "nErrorID" for n, _, _ in fb["output_rows"]) else "iErrorID"
    has_err = any(n in ("iErrorID", "nErrorID") for n, _, _ in fb["output_rows"])
    if has_err:
        err_section = err_table(errvar)
    else:
        err_section = ("本功能块没有错误号输出端，仅通过 `bError`（若有）/ `bBusy` 反馈执行状态：`bError = TRUE` "
                       "表示传输过程出错（在 `bBusy` 落沿后置位）。⚠️ PDF 与 InfoSys 均未给出本 FB 的具体错误码取值。"
                       if any(n == "bError" for n, _, _ in fb["output_rows"])
                       else "本功能块无错误码 / 错误号输出端。⚠️ PDF 与 InfoSys 均未给出本 FB 的错误反馈机制。")

    notes = "\n".join(f"- {x}" for x in fb["notes"])

    info_ref = src_info

    return f"""# {name}

## 元信息

| 字段 | 值 |
|---|---|
| Library | `{LIB}` |
| Library Version | `{VER}` |
| Type | `FUNCTION_BLOCK` |
| Category | `{fb['subdir']}` |
| Source PDF | {PDF_URL} |
| Source InfoSys | {src_info} |
| Verified | {TODAY} ✅ |
| InfoSys-checked | {info_checked} |
| Status | `verified` |
| Example | [`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU) |

---

## 1. 功能简述

{fb['summary']}

## 2. 接口定义

### VAR_INPUT

```iecst
{fb['var_input']}
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
{in_rows}

### VAR_OUTPUT

```iecst
{fb['var_output']}
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
{out_rows}

### VAR_IN_OUT

无。

## 3. 行为说明

{fb['behavior']}

## 4. 错误码 / 返回值

{err_section}

## 5. 使用注意 / 常见坑

{notes}

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_{name}
{fb['demo'][0]}

{fb['demo'][1]}
```

## 7. 业务场景与实际价值

{fb['scenario']}

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf`]({PDF_URL}) 第 {fb['section']} 节
- **InfoSys topic**：{info_ref}
- **相关 FB / FC**：{fb['related']}
"""


TCPOU_TMPL = """<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">
  <POU Name="P_Demo_{name}" Id="{guid}" SpecialFunc="None">
    <Declaration><![CDATA[PROGRAM P_Demo_{name}
{decl}
]]></Declaration>
    <Implementation>
      <ST><![CDATA[// ============================================================
// Tc2_ProfinetDiag.{name} 演示程序
// ============================================================
// 场景：{scene}
// 价值：{value}
// 验证：{verify}
// 验证步骤：
//   1. 右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选本 .TcPOU 文件
//   2. 引用 Tc2_ProfinetDiag（References → Add library）
//   3. 编译 → 登录 → 运行；按上方『验证』指引在线写值观察
// ============================================================

{st}
]]></ST>
    </Implementation>
  </POU>
</TcPlcObject>
"""

# 每个 FB 的 三件套（场景/价值/验证）一行版（用于 TcPOU 头注释）
TRIPLE = {
    "FB_PN_ALARM_DIAG": ("读 PROFINET 从站诊断报警，定位故障站/槽。", "封装监听+解析+复位，业务侧直接读结构。",
                          "登录后写 bDiagEnable:=TRUE；设备有报警时 stDiag/iAlarmCount 更新。"),
    "FB_PN_IM0_READ": ("读设备出厂标识（厂商/订货号/序列号）做资产校验。", "免手工解析 0xAFF0 帧。",
                       "登录后 bReadIM 上升沿，bBusy 一闪后 stIM0 填入设备标识。"),
    "FB_PN_IM1_READ": ("读设备 I&M1 功能/位置标签（电子铭牌）。", "免手工解析 0xAFF1 帧。",
                       "登录后 bReadIM 上升沿，sTagFunction/sTagLocation 填入。"),
    "FB_PN_IM2_READ": ("读设备 I&M2 安装日期。", "以 TIMESTRUCT 直接读出。",
                       "登录后 bReadIM 上升沿，stInstallDate 填入。"),
    "FB_PN_IM3_READ": ("读设备 I&M3 厂商描述。", "免手工解析 0xAFF3 帧。",
                       "登录后 bReadIM 上升沿，sDescriptor 填入。"),
    "FB_PN_IM4_Read": ("读设备 I&M4 厂商签名做完整性校验。", "标准签名字段直接读。",
                       "登录后 bReadIM 上升沿，sSignature 填入。"),
    "FB_PN_IM1_WRITE": ("投运时给设备写 I&M1 功能/位置标签。", "批量自动写电子铭牌。",
                        "登录后备好 sFunction/sLocation，bWriteTag 上升沿写入。"),
    "FB_PN_IM2_WRITE": ("投运时给设备写 I&M2 安装日期。", "投运日期随设备持久化。",
                        "登录后 bWriteDate 上升沿，写入 stCommissionDate。"),
    "FB_PN_IM3_WRITE": ("给设备写 I&M3 自定义描述。", "设备自带注释，免外部映射。",
                        "登录后 bWriteDesc 上升沿写入 sDescriptor。"),
    "FB_PN_IM4_WRITE": ("给设备写 I&M4 参数签名。", "标准签名字段，配合 READ 校验。",
                        "登录后 bWriteSig 上升沿写入 sSignature。"),
    "FB_PN_ReadStateOfDevices": ("读全网 PROFINET 健康总览（组态/异常/诊断计数）。", "一次拿三计数，免逐台轮询。",
                                 "登录后 bReadOverview 上升沿，nCfg/nErr/nDiag 填入。"),
    "FB_PN_ReadCompleteInfoOfDevices": ("读全网逐台设备明细（名/IP/循环时间）。", "一次返回数组，免多次读取。",
                                        "登录后 bReadAllReq 上升沿，nDevCount/aDevInfo 填入。"),
    "FB_SET_PN_NAME": ("按 MAC 给 PROFINET 设备分配名称。", "投运流程自动命名，免手工设名。",
                       "登录后备好 sNewName/aTargetMac，bSetNameReq 上升沿写名。"),
    "FB_RESET_PN_TO_FACTORY_SETTINGS": ("按 MAC 把设备复位到出厂设置。", "远程复位，免现场操作。",
                                        "登录后确认 aTargetMac，bResetReq 上升沿触发复位（谨慎）。"),
    "FB_PN_SCAN": ("扫描全网 PROFINET 设备（≤100 台）做发现。", "扫到 MAC/名可联动自动命名。",
                   "登录后 bScanReq 上升沿，iFound/aDevices 填入。"),
    "FB_PN_SCAN_UpTo255": ("扫描全网 PROFINET 设备（≤255 台）。", "大网络一次扫全，免分批。",
                           "登录后 bScanReq 上升沿，iFound/aDevices 填入（需库≥v1.5.2.0）。"),
    "FB_READ_PROFINET_NAME": ("读 EL6631-0010 的 PROFINET 名（含虚拟设备）。", "运行时直接读端子名。",
                              "登录后 bReadReq 上升沿，nSlaveKind/aPnNames 填入。"),
    "FB_Write_IuM_EL6631_0010": ("EL6631 设备端用位掩码一次写多项 I&M。", "byState 合并写，免逐项。",
                                 "登录后设 bySelect，bWriteReq 上升沿写入。"),
    "FB_Read_IuM_EL6631_0010": ("EL6631 设备端一次读齐 I&M1~I&M4。", "一次读齐五段文本。",
                                "登录后 bReadReq 上升沿，sFunc~sSig 填入。"),
    "FB_PROFINET_READ_IM": ("CCAT/TF6270 设备读自身 I&M 结构。", "结构化一次返回。",
                            "登录后 bReadReq 上升沿，stIuM 填入。"),
    "FB_PROFINET_READ_NAME": ("CCAT/TF6270 读设备名+可改性标志。", "改名前先判 bNotChangeable。",
                              "登录后 bReadReq 上升沿，sPnName/bLocked 填入。"),
    "FB_PROFINET_READ_PRM": ("CCAT/TF6270 读设备 IP 参数设置。", "一次读回 IP/掩码/网关/名。",
                             "登录后 bReadReq 上升沿，stPnSettings 填入。"),
    "FB_PROFINET_WRITE_IM": ("CCAT/TF6270 设备写自身 I&M 结构。", "先读后改再写，避免清空。",
                             "登录后 bReadReq 读出 stIuM，改字段后 bWriteReq 写回。"),
    "FB_PROFINET_SET_NAME": ("CCAT/TF6270 设备端自改 PROFINET 名。", "设备端自助改名，可锁名。",
                             "登录后备好 sNewName，bSetReq 上升沿改名（需驱动 06+）。"),
    "FB_PN_SEND_ALARM": ("设备端向控制器主动发 PROFINET 报警。", "枚举+槽号一次发出，免拼帧。",
                         "登录后选 eAlarmType/槽号，bSendReq 上升沿发送。"),
    "FB_PN_GET_PORT_STATISTIC": ("读端口流量统计排查丢包/坏包。", "统计进 PLC，可趋势报警。",
                                 "登录后 bGetReq 上升沿，stPort1/2 与 link 标志填入。"),
    "FB_PN_READ_PORT_DIAG": ("读端口诊断核对 PROFINET 拓扑接线。", "诊断进 PLC 自动核对拓扑。",
                             "登录后 bReadReq 上升沿，stPort1/2 填入。"),
}


def render_tcpou(fb) -> str:
    name = fb["name"]
    s, v, ve = TRIPLE[name]
    return TCPOU_TMPL.format(name=name, guid=guid(name), decl=fb["demo"][0],
                             st=fb["demo"][1], scene=s, value=v, verify=ve)


def main():
    base = ROOT / LIB
    docn = tcn = 0
    for fb in FBS:
        d = base / fb["subdir"]
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{fb['name']}.md").write_text(render_doc(fb), encoding="utf-8")
        docn += 1
        (base / "examples" / f"P_Demo_{fb['name']}.TcPOU").write_text(render_tcpou(fb), encoding="utf-8")
        tcn += 1
    print(f"generated {docn} docs, {tcn} tcpou; total FBs={len(FBS)}")
    # 名字唯一性检查
    names = [f["name"] for f in FBS]
    assert len(names) == len(set(names)), "duplicate FB names!"


if __name__ == "__main__":
    main()
