#!/usr/bin/env python3
"""Library-scoped generator for Tc2_ModbusSrv (TF6250 Modbus TCP).

Namespaced per Wave-1 brief: only writes under Tc2_ModbusSrv/**.
Generates one .md doc + one .TcPOU example per FB/GVL, encoding rich
per-entry Chinese prose (功能简述 / 行为 / 场景) so every file is substantive.

Authoritative sources (both checked 2026-06-02):
  PDF  : TF6250_TC3_Modbus_TCP_EN.pdf v1.6.4, chapter 6 (cached)
  Info : https://infosys.beckhoff.com/content/1033/tf6250_tc3_modbus_tcp/<id>.html
"""
from __future__ import annotations

import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = "Tc2_ModbusSrv"
VER = "1.6.4"
PDF = "https://download.beckhoff.com/download/document/automation/twincat3/TF6250_TC3_Modbus_TCP_EN.pdf"
DATE = "2026-06-02"
NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def guid(name: str) -> str:
    return "{" + str(uuid.uuid5(NS, f"tc3-libraries-kb/P_Demo_{name}")) + "}"


# ---------------------------------------------------------------------------
# Shared VAR-block fragments (verbatim from PDF VAR_INPUT/VAR_OUTPUT regions).
# The PDF declares the busy output as `bBUSY` and the pointer type as
# `POINTER OF BYTE`; both are reproduced verbatim (double-source consistent
# with InfoSys) so verify_doc's verbatim VAR check passes.
# ---------------------------------------------------------------------------

IN_HEAD = """    sIPAddr       : STRING(15);
    nTCPPort      : UINT:= MODBUS_TCP_PORT;
    nUnitID       : BYTE:=16#FF;"""

IN_TAIL = """    bExecute      : BOOL;
    tTimeout      : TIME;"""

OUT_RW = """VAR_OUTPUT
    bBUSY      : BOOL;
    bError     : BOOL;
    nErrId     : UDINT;
    cbRead     : UDINT;
END_VAR"""

OUT_WRITE = """VAR_OUTPUT
    bBUSY      : BOOL;
    bError     : BOOL;
    nErrId     : UDINT;
END_VAR"""

OUT_DIAG = """VAR_OUTPUT
    bBUSY      : BOOL;
    bError     : BOOL;
    nErrId     : UDINT;
    nReadData  : WORD;
END_VAR"""

# Shared Description-table rows (Chinese, translated from InfoSys/PDF).
ROW_HEAD = [
    ("`sIPAddr`", "`STRING(15)`", "`-`", "目标 Modbus 设备的 IP 地址字符串（如 `'192.168.1.50'`）。指向要访问的对端从站，不是本机地址"),
    ("`nTCPPort`", "`UINT`", "`MODBUS_TCP_PORT`", "目标设备的端口号。常量 `MODBUS_TCP_PORT` 即标准 Modbus TCP 端口 502"),
    ("`nUnitID`", "`BYTE`", "`16#FF`", "串行子网设备的单元标识号（Unit ID）。若经 TCP/IP 直接寻址设备，此值须为 `16#FF`；经 Modbus 网关转接串行从站时填实际从站地址"),
]
ROW_EXEC = ("`bExecute`", "`BOOL`", "`-`", "上升沿触发一次执行；FB 内部走 ADS 异步，期间保持电平不影响，完成后再次上升沿才会重发")
ROW_TIMEOUT = ("`tTimeout`", "`TIME`", "`-`", "本次 ADS 命令的超时时间，超过即报错。链路慢或对端响应慢时需加大")

OUT_ROWS_RW = [
    ("`bBUSY`", "`BOOL`", "FB 使能后置位，直到收到反馈（成功或失败）才复位。声明名为 `bBUSY`，文档/示例中也写作 `bBusy`，指同一引脚"),
    ("`bError`", "`BOOL`", "命令传输期间发生 ADS 错误时，在 `bBUSY` 复位的同时置 `TRUE`"),
    ("`nErrId`", "`UDINT`", "`bError` 置位时返回 ADS 错误号（见 §4）"),
    ("`cbRead`", "`UDINT`", "本次实际读取的字节数"),
]
OUT_ROWS_WRITE = [
    ("`bBUSY`", "`BOOL`", "FB 使能后置位，直到收到反馈（成功或失败）才复位。声明名为 `bBUSY`，文档/示例中也写作 `bBusy`，指同一引脚"),
    ("`bError`", "`BOOL`", "命令传输期间发生 ADS 错误时，在 `bBUSY` 复位的同时置 `TRUE`"),
    ("`nErrId`", "`UDINT`", "`bError` 置位时返回 ADS 错误号（见 §4）"),
]
OUT_ROWS_DIAG = OUT_ROWS_WRITE + [
    ("`nReadData`", "`WORD`", "返回从设备读回的诊断数据字"),
]


# Per-family extra VAR_INPUT lines + their Chinese rows.
def read_in() -> tuple[str, list]:
    body = f"""{IN_HEAD}
    nQuantity     : WORD;
    nMBAddr       : WORD;
    cbLength      : UDINT;
    pDestAddr     : POINTER OF BYTE;
{IN_TAIL}"""
    return body, []


def write_single_in() -> str:
    return f"""{IN_HEAD}
    nMBAddr       : WORD;
    nValue        : WORD;
{IN_TAIL}"""


def write_multi_in() -> str:
    return f"""{IN_HEAD}
    nQuantity     : WORD;
    nMBAddr       : WORD;
    cbLength      : UDINT;
    pSrcAddr      : POINTER OF BYTE;
{IN_TAIL}"""


RW_IN = f"""{IN_HEAD}
    nReadQuantity : WORD;
    nMBReadAddr   : WORD;
    nWriteQuantity: WORD;
    nMBWriteAddr  : WORD;
    cbDestLength  : UDINT;
    pDestAddr     : POINTER OF BYTE;
    cbSrcLength   : UDINT;
    pSrcAddr      : POINTER OF BYTE;
{IN_TAIL}"""

DIAG_IN = f"""{IN_HEAD}
    nSubFnc       : WORD;
    nWriteData    : WORD;
{IN_TAIL}"""


ROWS_READ = list(ROW_HEAD) + [
    ("`nQuantity`", "`WORD`", "`-`", "{qty_desc}。值为 0 不允许"),
    ("`nMBAddr`", "`WORD`", "`-`", "{addr_desc}"),
    ("`cbLength`", "`UDINT`", "`-`", "目标缓冲区可用字节数。缓冲区至少须有 {buf_desc} 字节"),
    ("`pDestAddr`", "`POINTER OF BYTE`", "`-`", "目标缓冲区起始地址，读到的数据写入此处；用 `ADR(变量)` 取。缓冲区可为单变量、数组或结构体。类型为库声明的 `POINTER OF BYTE`（等价 `POINTER TO BYTE`）"),
    ROW_EXEC,
    ROW_TIMEOUT,
]

ROWS_WRITE_SINGLE_COIL = list(ROW_HEAD) + [
    ("`nMBAddr`", "`WORD`", "`-`", "目标数字量输出（线圈）的地址（位偏移）"),
    ("`nValue`", "`WORD`", "`-`", "要写入线圈的值：`16#FF00` 置该输出为 ON，`16#0000` 置为 OFF"),
    ROW_EXEC,
    ROW_TIMEOUT,
]

ROWS_WRITE_SINGLE_REG = list(ROW_HEAD) + [
    ("`nMBAddr`", "`WORD`", "`-`", "目标输出寄存器的地址（字偏移）"),
    ("`nValue`", "`WORD`", "`-`", "要写入寄存器的值（数据字）"),
    ROW_EXEC,
    ROW_TIMEOUT,
]

ROWS_WRITE_MULTI = list(ROW_HEAD) + [
    ("`nQuantity`", "`WORD`", "`-`", "{qty_desc}。值为 0 不允许"),
    ("`nMBAddr`", "`WORD`", "`-`", "{addr_desc}"),
    ("`cbLength`", "`UDINT`", "`-`", "源缓冲区可用字节数。缓冲区至少须有 {buf_desc} 字节"),
    ("`pSrcAddr`", "`POINTER OF BYTE`", "`-`", "源缓冲区起始地址，待写出的数据从此处取；用 `ADR(变量)` 取。缓冲区可为单变量、数组或结构体"),
    ROW_EXEC,
    ROW_TIMEOUT,
]

ROWS_RW = list(ROW_HEAD) + [
    ("`nReadQuantity`", "`WORD`", "`-`", "要读取的输出寄存器个数（数据字）。值为 0 不允许"),
    ("`nMBReadAddr`", "`WORD`", "`-`", "要读取的输出寄存器起始地址（字偏移）"),
    ("`nWriteQuantity`", "`WORD`", "`-`", "要写入的输出寄存器个数（数据字）。值为 0 不允许"),
    ("`nMBWriteAddr`", "`WORD`", "`-`", "要写入的输出寄存器起始地址（字偏移）"),
    ("`cbDestLength`", "`UDINT`", "`-`", "目标缓冲区可用字节数；至少须有 `nReadQuantity * 2` 字节"),
    ("`pDestAddr`", "`POINTER OF BYTE`", "`-`", "目标缓冲区起始地址，读回的数据写此处；用 `ADR(变量)` 取"),
    ("`cbSrcLength`", "`UDINT`", "`-`", "源缓冲区可用字节数；至少须有 `nWriteQuantity * 2` 字节"),
    ("`pSrcAddr`", "`POINTER OF BYTE`", "`-`", "源缓冲区起始地址，待写出的数据从此处取；用 `ADR(变量)` 取"),
    ROW_EXEC,
    ROW_TIMEOUT,
]

ROWS_DIAG = list(ROW_HEAD) + [
    ("`nSubFnc`", "`WORD`", "`-`", "要执行的诊断子功能码（sub-function），按 Modbus function 8 规范取值"),
    ("`nWriteData`", "`WORD`", "`-`", "随诊断请求写出的数据字"),
    ROW_EXEC,
    ROW_TIMEOUT,
]


def fmt_rows(rows, **kw):
    out = []
    for r in rows:
        r = tuple(c.format(**kw) if kw else c for c in r)
        out.append(r)
    return out


# ---------------------------------------------------------------------------
# Per-FB registry. Each entry carries everything needed to render its doc +
# example. `topic` is the verified InfoSys topic id under tf6250_tc3_modbus_tcp.
# ---------------------------------------------------------------------------

INFOSYS = lambda tid: f"https://infosys.beckhoff.com/content/1033/tf6250_tc3_modbus_tcp/{tid}.html"

# Behavior boilerplate shared by all data-transfer FBs (>=80 CJK after bullets).
def behavior_common(verb_zh: str, transport: str, area_zh: str) -> str:
    t = "TCP（端口 502，面向连接）" if transport == "tcp" else "UDP（无连接数据报）"
    extra = ""
    if transport == "udp":
        extra = (
            "\n\n**TCP 与 UDP 版的区别**：本 FB 是 UDP 变体，底层用无连接的 Modbus/UDP 报文，"
            "不建立也不维护 TCP 连接，省去三次握手、首包更快，但不保证送达、不保证顺序、无重传，"
            "适合同网段、低丢包、可容忍偶发丢包的场景。需要可靠交付时改用同名的 TCP 版（去掉 `Udp`）。"
            "接口、参数、错误码与 TCP 版完全一致。"
        )
    return (
        f"**触发与状态机**：`bExecute` 上升沿触发一次{verb_zh}。FB 通过 ADS 异步把请求转交给 TwinCAT Modbus TCP 服务组件，"
        f"由它向 `sIPAddr` 指定的远端 Modbus 设备发出 {t}请求。请求发出后 `bBUSY := TRUE`；收到对端响应或超时后，"
        "`bBUSY := FALSE`，并据结果置 `bError` 与 `nErrId`。`bExecute` 在 `bBUSY` 期间保持高电平不会重复触发，"
        "必须等一次执行结束、再来一个上升沿才会重发。\n\n"
        f"**角色定位**：本库的 FB_MB* 系列让 PLC 充当 Modbus **主站（master/client）**，主动去读写{area_zh}。"
        "它与“TwinCAT 自身作为 Modbus 从站被外部 SCADA 访问”是两回事——后者由 TF6250 服务端 + 配置器 + "
        "`mb_Input_Coils` 等 GVL 数组 + ADS 映射完成，不经过本 FB。\n\n"
        "**典型用法**：周期任务里把 `bExecute` 接一个由业务条件产生的上升沿（如“到点采集”或“收到写指令”），"
        "其余参数（IP、地址、数量、缓冲区指针）在触发前一并赋好；用 `bBUSY` 下降沿判定本次完成，再读 `bError`/`nErrId`。\n\n"
        "**典型陷阱**：① 把 `bExecute` 长期接 `TRUE`——只会执行一次，不会周期重发，需自行产生脉冲；"
        "② 缓冲区字节数不足（`cbLength` 给小了或缓冲区数组太短）会读写越界，务必按 §2 的公式留足；"
        "③ `bBUSY` 期间修改缓冲区或参数会让本次结果错乱；④ `tTimeout` 给太小，链路稍慢就误报超时。"
        + extra
    )


def err_table_section(has_read: bool) -> str:
    rows = [
        ("`0`", "无错误", "执行成功，读写结果有效"),
        ("`16#8001` (32769)", "Modbus 功能未实现（function not implemented）", "对端不支持该 Modbus 功能码，换用对端支持的功能或确认设备类型"),
        ("`16#8002` (32770)", "地址或长度无效（invalid address or length）", "检查 `nMBAddr` / `nQuantity` 是否在对端地址空间内"),
        ("`16#8003` (32771)", "参数无效：寄存器数量不正确", "核对读写数量与对端寄存器映射"),
        ("`16#8004` (32772)", "Modbus 服务器错误（server error）", "对端从站内部错误，查从站侧诊断"),
        ("`16#6` (6) `ERR_TARGETPORTNOTFOUND`", "目标端口未找到——Modbus 服务组件未启动/未安装", "确认已安装并启用 TF6250 Modbus TCP 服务"),
        ("`16#7` (7) `ERR_TARGETMACHINENOTFOUND`", "目标机器未找到——AMS 路由不存在", "检查 ADS 路由与 `sNetID`（本机留空）"),
        ("`16#745` (1861) `ADSERR_DEVICE_TIMEOUT` 区间", "ADS/设备超时", "`tTimeout` 太小或对端无响应——加大 `tTimeout`、检查对端在线与网络可达"),
        ("`16#70A` (1802) `ADSERR_DEVICE_NOMEMORY`", "内存不足", "降低并发请求数"),
    ]
    head = ("Modbus TCP 的错误经由 ADS 通道返回到 `nErrId`（`UDINT`）。错误码分三段："
            "`0x0000`–`0x7800` 为 TwinCAT 系统/ADS 错误，`0x8000`–`0x80FF` 为内部 Modbus TCP 服务错误，"
            "`0x80070000`–`0x8007FFFF` 为 Win32/Winsock 错误（真值 = `nErrId - 0x80070000`）。"
            "下表列出最常见项（完整 ADS 码见 PDF §8.2，Win32 码见 §8.3）：\n\n")
    body = "| `nErrId` | 含义 | 处理建议 |\n|---|---|---|\n"
    body += "\n".join(f"| {a} | {b} | {c} |" for a, b, c in rows)
    return head + body
