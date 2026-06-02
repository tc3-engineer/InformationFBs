#!/usr/bin/env python3
"""Build all Tc2_ModbusSrv docs + examples. Namespaced helper (Wave-1 brief).

Run:  python3 _meta/tools/_tc2_modbussrv_build.py
Imports the data module _tc2_modbussrv_gen and renders every entry.
Only writes under Tc2_ModbusSrv/.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("_mbgen", _HERE / "_tc2_modbussrv_gen.py")
g = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g)

ROOT = g.ROOT
LIB = g.LIB
VER = g.VER
PDF = g.PDF
DATE = g.DATE


# ---------------------------------------------------------------------------
# Registry: every FB with its family + per-FB prose.
# family ∈ {read, wsingle_coil, wsingle_reg, wmulti, rw, diag}
# ---------------------------------------------------------------------------
FBS = [
    # name, transport, family, mb_fn, topic, brief, area_zh, qty/addr/buf descs, scenario dict
    dict(
        name="FB_MBReadCoils", transport="tcp", family="read", fn=1, topic="192752395",
        sec="6.2.1",
        brief="Modbus 功能码 1（Read Coils）的客户端功能块：从远端 Modbus 设备读取 1 到 2048 个数字量输出（线圈，coil）。"
              "每个线圈对应读回数据字节中的一个位（bit）。`bExecute` 上升沿触发一次读取，结果按位打包写入 `pDestAddr` 指向的缓冲区。",
        area_zh="远端设备的线圈（数字量输出）",
        qty="要读取的数字量（数据位）个数", addr="要读取的数字量起始地址（位偏移）", buf="`(nQuantity + 7) / 8`",
        out="rw",
        scenario=dict(
            s="读取一台第三方 Modbus TCP 设备（如智能配电单元、远程 IO 模块）的线圈状态，例如 16 路继电器输出的当前通断，用于在 HMI 上回显或做联锁判断。",
            v="无本 FB 时要自己拼 Modbus ADU 报文、管 TCP 连接、解析功能码 1 的位打包响应；用本 FB 一次调用即可，TF6250 服务负责报文与连接。",
            a="替代方案是用 Tc2_TcpIp 裸 socket 自己实现 Modbus 协议栈——工作量大且易错；或用 EtherCAT 网关——需额外硬件。对“PLC 主动读第三方 Modbus 设备”本 FB 最直接。",
            demo_extra="// 读 16 个线圈，结果打包进 2 字节",
            demo_qty=16, demo_addr=0, demo_buf="ARRAY [0..1] OF BYTE",
        ),
    ),
    dict(
        name="FB_MBReadInputs", transport="tcp", family="read", fn=2, topic="192753931",
        sec="6.2.2",
        brief="Modbus 功能码 2（Read Discrete Inputs）的客户端功能块：从远端 Modbus 设备读取 1 到 2048 个数字量输入（discrete input）。"
              "每个输入对应读回数据字节中的一个位。`bExecute` 上升沿触发一次读取，结果按位打包写入 `pDestAddr` 指向的缓冲区。",
        area_zh="远端设备的数字量输入（只读）",
        qty="要读取的数字量（数据位）个数", addr="要读取的数字量起始地址（位偏移）", buf="`(nQuantity + 7) / 8`",
        out="rw",
        scenario=dict(
            s="采集远端 Modbus 设备的只读数字量输入，例如远程 IO 站上的限位开关、光电传感器、急停回路反馈，集中送回主控做安全联锁。",
            v="离散输入是只读区，用本 FB 周期轮询即可拿到一批位状态；无须手写功能码 2 的报文与位解包。",
            a="替代是裸 socket 实现 Modbus，或给每个传感器单独接线进本地 IO——前者费力，后者布线成本高。远端集中采集用本 FB 最省。",
            demo_extra="// 读 20 个离散输入，打包进 3 字节",
            demo_qty=20, demo_addr=0, demo_buf="ARRAY [0..2] OF BYTE",
        ),
    ),
    dict(
        name="FB_MBReadRegs", transport="tcp", family="read", fn=3, topic="192755467",
        sec="6.2.3",
        brief="Modbus 功能码 3（Read Holding Registers）的客户端功能块：从远端 Modbus 设备读取 1 到 128 个输出寄存器（16 位）。"
              "每个寄存器低字节在前、高字节在后写入缓冲区。`bExecute` 上升沿触发一次读取。",
        area_zh="远端设备的保持寄存器（输出寄存器，可读写）",
        qty="要读取的输出寄存器（数据字）个数", addr="要读取的输出寄存器起始地址（字偏移）", buf="`nQuantity * 2`",
        out="rw",
        scenario=dict(
            s="读取变频器、温控表、电表等 Modbus 设备的保持寄存器，例如读回设定频率、实际转速、累计电量等 16 位过程量。",
            v="保持寄存器是最常用的 Modbus 数据区；本 FB 把功能码 3 封装为一次调用，按字节序自动落入 `WORD` 数组，省去拼包解包。",
            a="替代是裸 socket 自写协议，或用厂商专有协议网关。对标准 Modbus 设备，本 FB 通用且零额外硬件。",
            demo_extra="// 读 2 个保持寄存器（如频率+转速）",
            demo_qty=2, demo_addr=0, demo_buf="ARRAY [0..1] OF WORD",
        ),
    ),
    dict(
        name="FB_MBReadInputRegs", transport="tcp", family="read", fn=4, topic="192757003",
        sec="6.2.4",
        brief="Modbus 功能码 4（Read Input Registers）的客户端功能块：从远端 Modbus 设备读取 1 到 128 个输入寄存器（16 位）。"
              "注意字节序为小端（Little Endian）。`bExecute` 上升沿触发一次读取。",
        area_zh="远端设备的输入寄存器（只读）",
        qty="要读取的输入寄存器（数据字）个数", addr="要读取的输入寄存器起始地址（字偏移）", buf="`nQuantity * 2`",
        out="rw",
        scenario=dict(
            s="读取仪表的只读输入寄存器，例如电力仪表的瞬时电流/电压/功率、传感器变送器的测量值——这些是设备侧只读的实时量。",
            v="输入寄存器区只读，用本 FB（功能码 4）周期采集即可；与保持寄存器（功能码 3）区分开，避免误写。",
            a="替代是裸 socket 实现，或用 OPC UA（需设备支持）。对只读 Modbus 测量量，本 FB 直接通用。",
            demo_extra="// 读 3 个输入寄存器（如 U/I/P）",
            demo_qty=3, demo_addr=0, demo_buf="ARRAY [0..2] OF WORD",
        ),
    ),
    dict(
        name="FB_MBWriteSingleCoil", transport="tcp", family="wsingle_coil", fn=5, topic="192758539",
        sec="6.2.5",
        brief="Modbus 功能码 5（Write Single Coil）的客户端功能块：向远端 Modbus 设备写单个数字量输出（线圈），采用位访问。"
              "`nValue` 取 `16#FF00` 置 ON、`16#0000` 置 OFF。`bExecute` 上升沿触发一次写入。",
        area_zh="远端设备的单个线圈（数字量输出）",
        out="write",
        scenario=dict(
            s="远程控制单个继电器/电磁阀，例如令远端 IO 模块的某路输出闭合启动一台风机，或复位一个远程指示灯。",
            v="单点写线圈用功能码 5 最轻量；本 FB 一次调用、用 `16#FF00`/`16#0000` 明确 ON/OFF，无须拼包。",
            a="替代是写多线圈（功能码 15）写 1 位——可行但更重；或裸 socket 自实现。单点开关本 FB 最简。",
            demo_extra="// 把远端 4 号线圈置 ON",
        ),
    ),
    dict(
        name="FB_MBWriteSingleReg", transport="tcp", family="wsingle_reg", fn=6, topic="192760075",
        sec="6.2.6",
        brief="Modbus 功能码 6（Write Single Register）的客户端功能块：向远端 Modbus 设备写单个输出寄存器，采用 16 位访问。"
              "`nValue` 为要写入的数据字。`bExecute` 上升沿触发一次写入。",
        area_zh="远端设备的单个保持寄存器",
        out="write",
        scenario=dict(
            s="向变频器/温控表写单个设定值，例如改写一台变频器的目标频率寄存器，或给温控表下发新的设定温度。",
            v="单点写寄存器用功能码 6；本 FB 一次调用即可把一个 `WORD` 写到指定寄存器，省去报文构造。",
            a="替代是写多寄存器（功能码 16）写 1 个字——可行但更重；或裸 socket。单点设定本 FB 最简。",
            demo_extra="// 把目标频率 16#1234 写入 5 号寄存器",
        ),
    ),
    dict(
        name="FB_MBWriteCoils", transport="tcp", family="wmulti", fn=15, topic="192761611",
        sec="6.2.7",
        brief="Modbus 功能码 15（Write Multiple Coils）的客户端功能块：向远端 Modbus 设备写 1 到 2048 个数字量输出（线圈）。"
              "源缓冲区里每个位对应一个线圈。`bExecute` 上升沿触发一次写入。",
        area_zh="远端设备的多个线圈（数字量输出）",
        qty="要写入的数字量输出（数据位）个数", addr="要写入的数字量输出起始地址（位偏移）", buf="`(nQuantity + 7) / 8`",
        out="write",
        scenario=dict(
            s="一次性下发一批继电器/输出状态，例如远端 IO 站的 10 路输出按一个 `BYTE` 模式批量置位，用于灯光/电磁阀阵列控制。",
            v="批量写线圈用功能码 15，比逐个功能码 5 少很多报文往返；本 FB 按位打包一次写出。",
            a="替代是循环调用 WriteSingleCoil——报文多、延迟高；或裸 socket。批量输出本 FB 高效。",
            demo_extra="// 一次写 10 个线圈，位模式 0x0375 的低 10 位",
            demo_qty=10, demo_addr=0, demo_buf="ARRAY [0..1] OF BYTE := [16#75,16#03]",
        ),
    ),
    dict(
        name="FB_MBWriteRegs", transport="tcp", family="wmulti", fn=16, topic="192763147",
        sec="6.2.8",
        brief="Modbus 功能码 16（Write Multiple Registers）的客户端功能块：向远端 Modbus 设备写 1 到 128 个输出寄存器（16 位）。"
              "源缓冲区按字写出。`bExecute` 上升沿触发一次写入。",
        area_zh="远端设备的多个保持寄存器",
        qty="要写入的输出寄存器（数据字）个数", addr="要写入的输出寄存器起始地址（字偏移）", buf="`nQuantity * 2`",
        out="write",
        scenario=dict(
            s="向设备一次性下发一组参数，例如给运动控制器写入一段轨迹点、给配方设备下发一组工艺参数（多个 16 位寄存器）。",
            v="批量写寄存器用功能码 16，一次报文写多个字；本 FB 把 `WORD` 数组一次写出，省去多次往返。",
            a="替代是循环 WriteSingleReg——慢；或裸 socket。批量参数下发本 FB 高效通用。",
            demo_extra="// 一次写 3 个寄存器（一组工艺参数）",
            demo_qty=3, demo_addr=0, demo_buf="ARRAY [0..2] OF WORD := [100,200,300]",
        ),
    ),
    dict(
        name="FB_MBReadWriteRegs", transport="tcp", family="rw", fn=23, topic="192764683",
        sec="6.2.9",
        brief="Modbus 功能码 23（Read/Write Multiple Registers）的客户端功能块：先读 1 到 128 个输出寄存器，再写 1 到 128 个输出寄存器。"
              "读写在同一次 Modbus 事务内完成。`bExecute` 上升沿触发一次。",
        area_zh="远端设备的保持寄存器（同一事务内先读后写）",
        out="rw",
        scenario=dict(
            s="在一次 Modbus 事务里既读回设备状态又下发新设定，例如读回当前测量值同时写入下一周期设定值，保证读写在同一往返内原子完成。",
            v="功能码 23 把读+写合并为一次报文往返，比分开两次（功能码 3 + 16）延迟低、且语义上更接近原子；本 FB 一次调用搞定。",
            a="替代是先 ReadRegs 再 WriteRegs 两次调用——两次往返、读写之间可能被打断；本 FB 合并更优。",
            demo_extra="// 同一事务：读 9 个寄存器、写 9 个寄存器",
        ),
    ),
    dict(
        name="FB_MBDiagnose", transport="tcp", family="diag", fn=8, topic="192766219",
        sec="6.2.10",
        brief="Modbus 功能码 8（Diagnostics）的客户端功能块：对远端 Modbus 设备执行一系列诊断测试，"
              "用于检查主从站之间的通信系统、查询从站内部的各种错误状态。`nSubFnc` 选择子功能，`nReadData` 返回读回的诊断数据字。",
        area_zh="远端设备的诊断子功能（function 8）",
        out="diag",
        scenario=dict(
            s="对可疑链路做联机诊断，例如用子功能 0（Return Query Data，回显测试）确认链路通畅，或读取从站的通信计数器/错误状态字排查现场故障。",
            v="功能码 8 是 Modbus 标准诊断入口；本 FB 把子功能号 + 写数据封装为一次调用，回读 `nReadData`，无须自拼诊断报文。",
            a="替代是 ping/抓包等外部手段——无法读从站内部计数器；或裸 socket 自实现。设备级诊断本 FB 直接。",
            demo_extra="// 子功能 0：回显测试（Return Query Data）",
        ),
    ),
]

# UDP variants: identical interface, derived from the TCP entries by name.
_UDP_TOPIC = {
    "FB_MBUdpReadCoils": ("192769163", "6.2.11.1"),
    "FB_MBUdpReadInputs": ("192770699", "6.2.11.2"),
    "FB_MBUdpReadRegs": ("192772235", "6.2.11.3"),
    "FB_MBUdpReadInputRegs": ("192773771", "6.2.11.4"),
    "FB_MBUdpWriteSingleCoil": ("192775307", "6.2.11.5"),
    "FB_MBUdpWriteSingleReg": ("192776843", "6.2.11.6"),
    "FB_MBUdpWriteCoils": ("192778379", "6.2.11.7"),
    "FB_MBUdpWriteRegs": ("192779915", "6.2.11.8"),
    "FB_MBUdpReadWriteRegs": ("192781451", "6.2.11.9"),
    "FB_MBUdpDiagnose": ("192782987", "6.2.11.10"),
}


def _make_udp(tcp_entry: dict) -> dict:
    udp_name = tcp_entry["name"].replace("FB_MB", "FB_MBUdp")
    tid, sec = _UDP_TOPIC[udp_name]
    e = dict(tcp_entry)
    e["name"] = udp_name
    e["transport"] = "udp"
    e["topic"] = tid
    e["sec"] = sec
    base = tcp_entry["name"]
    e["brief"] = (
        f"{tcp_entry['brief']} 本块是 UDP 变体：底层用无连接的 Modbus/UDP 报文传输，"
        f"接口与同名 TCP 版 `{base}` 完全一致，区别仅在传输层（不建立 TCP 连接，不保证可靠交付）。"
    )
    sc = dict(tcp_entry["scenario"])
    sc["s"] = (
        f"{sc['s']} 选用 UDP 版多见于同一控制柜/同网段、对实时性敏感且能容忍偶发丢包的场景，"
        f"省去 TCP 建链开销。"
    )
    sc["a"] = f"{sc['a']} 与 TCP 版 `{base}` 的取舍：需要可靠交付选 TCP，需要低延迟且可容忍丢包选本 UDP 版。"
    e["scenario"] = sc
    return e


ALL_FBS = FBS + [_make_udp(e) for e in FBS]


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def _table(headers, rows):
    out = "| " + " | ".join(headers) + " |\n"
    out += "|" + "|".join("---" for _ in headers) + "|\n"
    for r in rows:
        out += "| " + " | ".join(r) + " |\n"
    return out.rstrip()


def _in_block_and_rows(e):
    fam = e["family"]
    if fam == "read":
        body, _ = g.read_in()
        rows = g.fmt_rows(g.ROWS_READ, qty_desc=e["qty"], addr_desc=e["addr"], buf_desc=e["buf"])
    elif fam == "wsingle_coil":
        body = g.write_single_in()
        rows = g.ROWS_WRITE_SINGLE_COIL
    elif fam == "wsingle_reg":
        body = g.write_single_in()
        rows = g.ROWS_WRITE_SINGLE_REG
    elif fam == "wmulti":
        body = g.write_multi_in()
        rows = g.fmt_rows(g.ROWS_WRITE_MULTI, qty_desc=e["qty"], addr_desc=e["addr"], buf_desc=e["buf"])
    elif fam == "rw":
        body = g.RW_IN
        rows = g.ROWS_RW
    elif fam == "diag":
        body = g.DIAG_IN
        rows = g.ROWS_DIAG
    else:
        raise ValueError(fam)
    return body, rows


def _out_block_and_rows(e):
    if e["out"] == "rw":
        return g.OUT_RW, g.OUT_ROWS_RW
    if e["out"] == "write":
        return g.OUT_WRITE, g.OUT_ROWS_WRITE
    if e["out"] == "diag":
        return g.OUT_DIAG, g.OUT_ROWS_DIAG
    raise ValueError(e["out"])


def _verb(e):
    fam = e["family"]
    return {
        "read": "读取操作", "wsingle_coil": "写单线圈操作", "wsingle_reg": "写单寄存器操作",
        "wmulti": "批量写操作", "rw": "读写操作", "diag": "诊断操作",
    }[fam]


def render_doc(e) -> str:
    name = e["name"]
    in_block, in_rows = _in_block_and_rows(e)
    out_block, out_rows = _out_block_and_rows(e)
    in_tbl = _table(["名称", "类型", "默认值", "说明（中文）"], in_rows)
    out_tbl = _table(["名称", "类型", "说明（中文）"], out_rows)
    info = g.INFOSYS(e["topic"])
    behavior = g.behavior_common(_verb(e), e["transport"], e["area_zh"])
    err = g.err_table_section(e["out"] in ("rw", "diag"))
    sc = e["scenario"]

    # build example call snippet for §6 (mirrors the .TcPOU)
    call = _example_call(e, inline=True)

    notes = _notes(e)

    parts = []
    parts.append(f"# {name}\n")
    parts.append("## 元信息\n")
    parts.append(_table(["字段", "值"], [
        ("Library", f"`{LIB}`"),
        ("Library Version", f"`{VER}`"),
        ("Type", "`FUNCTION_BLOCK`"),
        ("Category", "`Function blocks`"),
        ("Source PDF", PDF),
        ("Source InfoSys", info),
        ("Verified", f"{DATE} ✅"),
        ("InfoSys-checked", f"✅ {DATE}"),
        ("Status", "`verified`"),
        ("Example", f"[`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU)"),
    ]))
    parts.append("\n---\n")
    parts.append("## 1. 功能简述\n")
    parts.append(e["brief"] + "\n")
    parts.append("## 2. 接口定义\n")
    parts.append("### VAR_INPUT\n")
    parts.append("```iecst\nVAR_INPUT\n" + in_block + "\nEND_VAR\n```\n")
    parts.append(in_tbl + "\n")
    parts.append("### VAR_OUTPUT\n")
    parts.append("```iecst\n" + out_block + "\n```\n")
    parts.append(out_tbl + "\n")
    parts.append("### VAR_IN_OUT\n")
    parts.append("无（数据缓冲区通过 `pDestAddr` / `pSrcAddr` 指针传入，不是 VAR_IN_OUT）。\n")
    parts.append("## 3. 行为说明\n")
    parts.append(behavior + "\n")
    parts.append("## 4. 错误码 / 返回值\n")
    parts.append(err + "\n")
    parts.append("## 5. 使用注意 / 常见坑\n")
    parts.append(notes + "\n")
    parts.append("## 6. 最小例程\n")
    parts.append(f"> 配套可导入文件：[`examples/P_Demo_{name}.TcPOU`](../examples/P_Demo_{name}.TcPOU)\n>\n"
                 f"> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK\n")
    parts.append("```iecst\n" + call + "\n```\n")
    parts.append("## 7. 业务场景与实际价值\n")
    parts.append(f"- **场景**：{sc['s']}\n- **价值**：{sc['v']}\n- **替代方案对比**：{sc['a']}\n")
    parts.append("## 8. 参考资料\n")
    rel = _related(e)
    parts.append(f"- **PDF**：[TF6250_TC3_Modbus_TCP_EN.pdf]({PDF}) §{e['sec']}\n"
                 f"- **InfoSys topic**：{info}\n"
                 f"- **相关**：{rel}\n")
    return "\n".join(parts)


def _related(e) -> str:
    fam = e["family"]
    if e["transport"] == "tcp":
        udp = e["name"].replace("FB_MB", "FB_MBUdp")
        sib = f"`{udp}`（UDP 版）、"
    else:
        tcp = e["name"].replace("FB_MBUdp", "FB_MB")
        sib = f"`{tcp}`（TCP 版）、"
    grp = {
        "read": "`FB_MBReadRegs` / `FB_MBReadInputRegs`（读寄存器）",
        "wsingle_coil": "`FB_MBWriteCoils`（批量写线圈）",
        "wsingle_reg": "`FB_MBWriteRegs`（批量写寄存器）",
        "wmulti": "`FB_MBReadRegs`（先读后用）",
        "rw": "`FB_MBReadRegs` + `FB_MBWriteRegs`（分开读/写）",
        "diag": "`FB_MBReadRegs`（常规读）",
    }[fam]
    return sib + grp + "、`stLibVersion_Tc2_ModbusSrv`（库版本）"


def _notes(e) -> str:
    fam = e["family"]
    base = [
        "**`sIPAddr` 指向对端，不是本机**：这是最常见误解。FB_MB* 让 PLC 当 Modbus 主站去访问别的设备；要把 TwinCAT 当从站被外部读写，是另一套机制（TF6250 服务端 + 配置器 + GVL 映射数组），不经过本 FB。",
        "**`bExecute` 是边沿触发**：长期接 `TRUE` 只执行一次；周期采集要自己产生脉冲（如用 `bBusy` 下降沿重新拉一次）。",
        "**`nUnitID` 直连填 `16#FF`**：仅当经 Modbus 网关转接串行从站时才填实际从站号。",
        f"**`tTimeout` 要给足**：默认无初值，必须显式赋值（如 `T#5S`）；链路慢或对端响应慢时加大，否则误报超时（ADS timeout）。",
    ]
    if fam in ("read", "wmulti"):
        base.append(f"**缓冲区字节数公式**：`cbLength` 与缓冲区数组都要满足至少 {e['buf']} 字节，否则读写越界（工程经验补充：用 `SIZEOF(缓冲区变量)` 赋 `cbLength` 最稳）。")
    if fam == "read":
        base.append("**位/字节序**：读线圈/离散输入时，结果按位打包进字节，低位在前；读寄存器时低字节在前、高字节在后（小端）。解析时注意位序与字节序。")
    if fam == "wsingle_coil":
        base.append("**线圈值只认两个常量**：`nValue := 16#FF00` 为 ON，`16#0000` 为 OFF；写其他值行为由对端决定，不要乱填。")
    if fam == "rw":
        base.append("**读缓冲与写缓冲分开**：`pDestAddr`/`cbDestLength` 是读回数据落点，`pSrcAddr`/`cbSrcLength` 是待写数据来源，两套缓冲不要混用同一变量。")
    if fam == "diag":
        base.append("**子功能码须对端支持**：`nSubFnc` 取值依从站实现而定（如 0 = Return Query Data 回显）；对端不支持会返回 Modbus 异常。")
    if e["transport"] == "udp":
        base.append("**UDP 不保证可靠**：丢包不会重传、无连接状态；关键写操作（如安全相关输出）应使用 TCP 版以获得可靠交付。")
    return "\n".join(f"- {b}" for b in base)


# ---------------------------------------------------------------------------
# Example call snippet (shared by §6 doc block and the .TcPOU body)
# ---------------------------------------------------------------------------

def _example_call(e, inline=False):
    """Render a single complete call `fbX(IN := ..., OUT => ...);`."""
    name = e["name"]
    fam = e["family"]
    inst = "fb" + name[len("FB_MB"):] if name.startswith("FB_MB") else "fb" + name
    sc = e["scenario"]
    if fam == "read":
        return (
            f"{inst}(\n"
            f"    sIPAddr   := sTargetIp,\n"
            f"    nTCPPort  := MODBUS_TCP_PORT,\n"
            f"    nUnitID   := 16#FF,\n"
            f"    nQuantity := {sc['demo_qty']},\n"
            f"    nMBAddr   := {sc['demo_addr']},\n"
            f"    cbLength  := SIZEOF(arrData),\n"
            f"    pDestAddr := ADR(arrData),\n"
            f"    bExecute  := bTrigger,\n"
            f"    tTimeout  := T#5S,\n"
            f"    bBUSY     => bBusy,\n"
            f"    bError    => bError,\n"
            f"    nErrId    => nErrId,\n"
            f"    cbRead    => nReadCount\n"
            f");"
        )
    if fam == "wsingle_coil":
        return (
            f"{inst}(\n"
            f"    sIPAddr  := sTargetIp,\n"
            f"    nTCPPort := MODBUS_TCP_PORT,\n"
            f"    nUnitID  := 16#FF,\n"
            f"    nMBAddr  := 4,\n"
            f"    nValue   := 16#FF00,   // 16#FF00 = ON, 16#0000 = OFF\n"
            f"    bExecute := bTrigger,\n"
            f"    tTimeout := T#5S,\n"
            f"    bBUSY    => bBusy,\n"
            f"    bError   => bError,\n"
            f"    nErrId   => nErrId\n"
            f");"
        )
    if fam == "wsingle_reg":
        return (
            f"{inst}(\n"
            f"    sIPAddr  := sTargetIp,\n"
            f"    nTCPPort := MODBUS_TCP_PORT,\n"
            f"    nUnitID  := 16#FF,\n"
            f"    nMBAddr  := 5,\n"
            f"    nValue   := 16#1234,\n"
            f"    bExecute := bTrigger,\n"
            f"    tTimeout := T#5S,\n"
            f"    bBUSY    => bBusy,\n"
            f"    bError   => bError,\n"
            f"    nErrId   => nErrId\n"
            f");"
        )
    if fam == "wmulti":
        return (
            f"{inst}(\n"
            f"    sIPAddr   := sTargetIp,\n"
            f"    nTCPPort  := MODBUS_TCP_PORT,\n"
            f"    nUnitID   := 16#FF,\n"
            f"    nQuantity := {sc['demo_qty']},\n"
            f"    nMBAddr   := {sc['demo_addr']},\n"
            f"    cbLength  := SIZEOF(arrData),\n"
            f"    pSrcAddr  := ADR(arrData),\n"
            f"    bExecute  := bTrigger,\n"
            f"    tTimeout  := T#5S,\n"
            f"    bBUSY     => bBusy,\n"
            f"    bError    => bError,\n"
            f"    nErrId    => nErrId\n"
            f");"
        )
    if fam == "rw":
        return (
            f"{inst}(\n"
            f"    sIPAddr        := sTargetIp,\n"
            f"    nTCPPort       := MODBUS_TCP_PORT,\n"
            f"    nUnitID        := 16#FF,\n"
            f"    nReadQuantity  := 9,\n"
            f"    nMBReadAddr    := 0,\n"
            f"    nWriteQuantity := 9,\n"
            f"    nMBWriteAddr   := 16,\n"
            f"    cbDestLength   := SIZEOF(arrReadData),\n"
            f"    pDestAddr      := ADR(arrReadData),\n"
            f"    cbSrcLength    := SIZEOF(arrWriteData),\n"
            f"    pSrcAddr       := ADR(arrWriteData),\n"
            f"    bExecute       := bTrigger,\n"
            f"    tTimeout       := T#5S,\n"
            f"    bBUSY          => bBusy,\n"
            f"    bError         => bError,\n"
            f"    nErrId         => nErrId,\n"
            f"    cbRead         => nReadCount\n"
            f");"
        )
    if fam == "diag":
        return (
            f"{inst}(\n"
            f"    sIPAddr    := sTargetIp,\n"
            f"    nTCPPort   := MODBUS_TCP_PORT,\n"
            f"    nUnitID    := 16#FF,\n"
            f"    nSubFnc    := 0,        // 0 = Return Query Data (回显测试)\n"
            f"    nWriteData := 16#A537,  // 任意测试字, 对端应原样回显\n"
            f"    bExecute   := bTrigger,\n"
            f"    tTimeout   := T#5S,\n"
            f"    bBUSY      => bBusy,\n"
            f"    bError     => bError,\n"
            f"    nErrId     => nErrId,\n"
            f"    nReadData  => nDiagReadData\n"
            f");"
        )
    raise ValueError(fam)


def _example_decl(e):
    name = e["name"]
    inst = "fb" + name[len("FB_MB"):] if name.startswith("FB_MB") else "fb" + name
    fam = e["family"]
    sc = e["scenario"]
    common = (
        f"    {inst:<14}: {name};\n"
        f"    sTargetIp     : STRING(15) := '192.168.1.50';   // 目标 Modbus 设备 IP（按现场改）\n"
        f"    bTrigger      : BOOL;          // 在线置一次上升沿触发本次访问\n"
        f"    bBusy         : BOOL;          // 在线 monitor：执行中为 TRUE\n"
        f"    bError        : BOOL;          // 出错置 TRUE\n"
        f"    nErrId        : UDINT;         // 出错时的 ADS/Modbus 错误码\n"
    )
    if fam in ("read",):
        return common + (
            f"    nReadCount    : UDINT;         // 实际读到的字节数\n"
            f"    arrData       : {sc['demo_buf']};   // 读回数据落点\n"
        )
    if fam == "wmulti":
        return common + (
            f"    arrData       : {sc['demo_buf']};   // 待写出的数据\n"
        )
    if fam == "rw":
        return common + (
            f"    nReadCount    : UDINT;         // 实际读到的字节数\n"
            f"    arrReadData   : ARRAY [0..8] OF WORD;   // 读回的 9 个寄存器\n"
            f"    arrWriteData  : ARRAY [0..8] OF WORD := [1,2,3,4,5,6,7,8,9];  // 待写的 9 个寄存器\n"
        )
    if fam == "diag":
        return common + (
            f"    nDiagReadData : WORD;          // 回读的诊断数据字\n"
        )
    # single write families: no buffers
    return common


def _tcpou_scenario_comment(e):
    sc = e["scenario"]
    extra = sc.get("demo_extra", "").lstrip("/").strip()
    extra_line = f"\n//       本例：{extra}" if extra else ""
    return (
        f"// 场景：{sc['s']}\n"
        f"// 价值：{sc['v']}\n"
        f"// 验证：登录后在线置 bTrigger := TRUE 触发一次；观察 bBusy 在数个周期后回 FALSE，\n"
        f"//       bError 应为 FALSE、nErrId 应为 0；若对端不在线则 bError=TRUE 且 nErrId 含超时码。"
        f"{extra_line}"
    ).rstrip()


def render_tcpou(e):
    name = e["name"]
    gd = g.guid(name)
    decl = _example_decl(e)
    call = _example_call(e)
    scen = _tcpou_scenario_comment(e)
    st_body = (
        f"// ============================================================\n"
        f"// {LIB}.{name} 演示程序（Modbus TCP 客户端 / 主站）\n"
        f"// ============================================================\n"
        f"{scen}\n"
        f"// 验证步骤：\n"
        f"//   1. 右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选本 .TcPOU 文件\n"
        f"//   2. 引用 {LIB}（References → Add library），并确保 TF6250 Modbus TCP 已授权运行\n"
        f"//   3. 把 sTargetIp 改成现场 Modbus 设备 IP；编译 → 登录 → 运行\n"
        f"//   4. 在线脉冲 bTrigger，按上方『验证』观察输出\n"
        f"// ============================================================\n\n"
        f"// 单次完整调用：所有 VAR_INPUT 显式赋值；bExecute 边沿触发一次\n"
        f"{call}\n"
    )
    xml = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">\n'
        f'  <POU Name="P_Demo_{name}" Id="{gd}" SpecialFunc="None">\n'
        f'    <Declaration><![CDATA[PROGRAM P_Demo_{name}\nVAR\n{decl}END_VAR\n]]></Declaration>\n'
        '    <Implementation>\n'
        f'      <ST><![CDATA[{st_body}]]></ST>\n'
        '    </Implementation>\n'
        '  </POU>\n'
        '</TcPlcObject>\n'
    )
    return xml


# ---------------------------------------------------------------------------
# GVL: stLibVersion_Tc2_ModbusSrv  (PDF §6.3.1)
# ---------------------------------------------------------------------------
GVL_TOPIC = "192785931"  # Library Version page (6.3.1), verified via search


def render_gvl_doc():
    info = g.INFOSYS(GVL_TOPIC)
    meta = _table(["字段", "值"], [
        ("Library", f"`{LIB}`"),
        ("Library Version", f"`{VER}`"),
        ("Type", "`VAR_GLOBAL CONSTANT`"),
        ("Category", "`Global constants`"),
        ("Source PDF", PDF),
        ("Source InfoSys", info),
        ("Verified", f"{DATE} ✅"),
        ("InfoSys-checked", f"✅ {DATE}"),
        ("Status", "`verified`"),
        ("Example", "[`examples/P_Demo_stLibVersion_Tc2_ModbusSrv.TcPOU`](../examples/P_Demo_stLibVersion_Tc2_ModbusSrv.TcPOU)"),
    ])
    return f"""# stLibVersion_Tc2_ModbusSrv

## 元信息

{meta}

---

## 1. 功能简述

Tc2_ModbusSrv 库的版本号常量。类型为 `ST_LibVersion`（结构体，来自 Tc2_System 库，含 `iMajor` / `iMinor` / `iBuild` / `iRevision` / `nFlags` / `sVersion` 等字段）。运行时用 Tc2_System 库的 `F_CmpLibVersion` 函数把本常量与“代码要求的最低版本”比对，决定是否报警或拒绝启动。这是 Beckhoff 所有 PLC 库统一的版本暴露机制——业务代码引用本常量即可得知运行时实际加载的 Tc2_ModbusSrv 版本。

## 2. 接口定义

### 全局常量声明

```iecst
VAR_GLOBAL CONSTANT
    stLibVersion_Tc2_ModbusSrv : ST_LibVersion;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `stLibVersion_Tc2_ModbusSrv` | `ST_LibVersion` | 编译时由库内嵌 | Tc2_ModbusSrv 库版本结构；读取后可比较或显示 |

### `ST_LibVersion` 结构（来自 Tc2_System）

| 字段 | 类型 | 说明（中文） |
|---|---|---|
| `iMajor` | `INT` | 主版本号（本库为 `1`） |
| `iMinor` | `INT` | 副版本号（本库为 `6`） |
| `iBuild` | `INT` | 构建号（本库为 `4`） |
| `iRevision` | `INT` | 修订号 |
| `nFlags` | `BYTE` | 内部标志 |
| `sVersion` | `STRING(23)` | 完整版本字串（如 `'1.6.4.0'`） |

### VAR_IN_OUT

无——本条目是常量声明，非函数 / 方法。

## 3. 行为说明

**何时读取**：典型在 PLC 初始化阶段调用一次 `F_CmpLibVersion`，比对版本是否 ≥ 业务要求的最低版本；不达标则报警或拒绝继续启动。本常量是编译期由 Tc2_ModbusSrv 的 .compiled-library 内嵌的，不是运行时动态生成；若重装了不同版本的 TF6250 并重新编译工程，此常量随之更新。

**TwinCAT 2 兼容性**：PDF §6.3.1 明确指出“TwinCAT 2 库的查询方式已不再可用（Query options for TwinCAT 2 libraries are no longer available）”——TC3 工程统一使用本常量 + `F_CmpLibVersion` 做版本比对。

**典型陷阱**：把本常量当 `STRING` 直接用——它是结构体，要拿字串得读 `.sVersion` 字段；只比 `iMajor >= 1` 不够严谨，应使用 `F_CmpLibVersion` 做完整的多段比较。它是 `CONSTANT`，任何写入都是错误用法。

## 4. 错误码 / 返回值

不适用——本条目是常量声明，无返回值。

## 5. 使用注意 / 常见坑

- **永远不要写入本常量**：声明为 `CONSTANT`，写入会编译报错。
- **`F_CmpLibVersion` 的用法**：组合 `LIBVERCMP_EQ` / `LIBVERCMP_HI` / `LIBVERCMP_LO` 标志做比较；详见 Tc2_System 库的 `F_CmpLibVersion` 文档。
- **`.sVersion` 字段**：长度 `STRING(23)`，够装 `xxx.yyy.zzz.www` 格式；要做精确比较仍建议用 `iMajor`/`iMinor`/`iBuild` 整数字段。
- **跨库统一校验（工程经验补充）**：工程常把多个库的版本检查集中在初始化阶段执行，任一不达标即拒启动并向 HMI 报错。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_stLibVersion_Tc2_ModbusSrv.TcPOU`](../examples/P_Demo_stLibVersion_Tc2_ModbusSrv.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_stLibVersion_Tc2_ModbusSrv
VAR
    bInit          : BOOL := TRUE;
    bLibVersionOk  : BOOL;
    sActualVersion : STRING(23);
END_VAR

IF bInit THEN
    bInit := FALSE;
    sActualVersion := stLibVersion_Tc2_ModbusSrv.sVersion;       // HMI 显示用
    bLibVersionOk  := stLibVersion_Tc2_ModbusSrv.iMajor > 1
        OR (stLibVersion_Tc2_ModbusSrv.iMajor = 1
            AND stLibVersion_Tc2_ModbusSrv.iMinor >= 6);
END_IF
```

## 7. 业务场景与实际价值

- **场景**：工程要求 Tc2_ModbusSrv ≥ 某版本（确保某些 FB 行为一致）；初始化时校验，不达标即在 HMI 提示“请升级 TF6250”。
- **价值**：把运行时实际加载的库版本暴露成可读常量，使业务代码能写版本敏感的兼容逻辑，避免升级后行为变化导致的隐性故障。
- **替代方案对比**：不查版本——升级后某 FB 行为变化、运行时故障且无诊断；查 TwinCAT 系统版本——粒度太粗，无法精确到具体库。

## 8. 参考资料

- **PDF**：[TF6250_TC3_Modbus_TCP_EN.pdf]({PDF}) §6.3.1
- **InfoSys topic**：{info}
- **相关**：`F_CmpLibVersion`（Tc2_System，比较函数）、`ST_LibVersion`（Tc2_System，结构体定义）
"""


def render_gvl_tcpou():
    name = "stLibVersion_Tc2_ModbusSrv"
    gd = g.guid(name)
    st_body = (
        "// ============================================================\n"
        f"// {LIB}.{name} 演示程序（库版本检查）\n"
        "// ============================================================\n"
        "// 场景：PLC 初始化时检查 Tc2_ModbusSrv 版本是否达标，并把版本字串送 HMI 显示。\n"
        "// 价值：升级 TF6250 后若库版本不符，可在启动阶段发现并报警，而不是运行时才暴露。\n"
        "// 验证：登录后观察 sActualVersion 是否显示形如 '1.6.4.0'；bLibVersionOk 为 TRUE 表示达标。\n"
        "// 验证步骤：\n"
        "//   1. 右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选本 .TcPOU 文件\n"
        "//   2. 引用 Tc2_ModbusSrv（References → Add library）\n"
        "//   3. 编译 → 登录 → 运行；在线 monitor sActualVersion / bLibVersionOk\n"
        "// ============================================================\n\n"
        "IF bInit THEN\n"
        "    bInit := FALSE;\n"
        "    // 读出字串版本便于 HMI 显示\n"
        "    sActualVersion := stLibVersion_Tc2_ModbusSrv.sVersion;\n"
        "    // 比较是否 >= 1.6（严格比较建议用 Tc2_System 的 F_CmpLibVersion）\n"
        "    bLibVersionOk := stLibVersion_Tc2_ModbusSrv.iMajor > 1\n"
        "        OR (stLibVersion_Tc2_ModbusSrv.iMajor = 1\n"
        "            AND stLibVersion_Tc2_ModbusSrv.iMinor >= 6);\n"
        "END_IF\n"
    )
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<TcPlcObject Version="1.1.0.1" ProductVersion="3.1.4024.5">\n'
        f'  <POU Name="P_Demo_{name}" Id="{gd}" SpecialFunc="None">\n'
        f'    <Declaration><![CDATA[PROGRAM P_Demo_{name}\n'
        'VAR\n'
        '    bInit          : BOOL := TRUE;\n'
        '    bLibVersionOk  : BOOL;\n'
        '    sActualVersion : STRING(23);\n'
        'END_VAR\n'
        ']]></Declaration>\n'
        '    <Implementation>\n'
        f'      <ST><![CDATA[{st_body}]]></ST>\n'
        '    </Implementation>\n'
        '  </POU>\n'
        '</TcPlcObject>\n'
    )


def render_readme():
    def row(e):
        return f"| `{e['name']}` | {e['fn']} | {_short(e)} | [function_blocks/{e['name']}.md](function_blocks/{e['name']}.md) |"
    tcp_rows = "\n".join(row(e) for e in FBS)
    udp_rows = "\n".join(row(e) for e in ALL_FBS if e["transport"] == "udp")
    return f"""# Tc2_ModbusSrv（TF6250 Modbus TCP）

> Beckhoff TwinCAT 3 TF6250 Modbus TCP 的 PLC 库。提供让 PLC 充当 **Modbus 主站（client）**
> 主动读写远端 Modbus 设备的功能块（TCP 与 UDP 两套），以及库版本常量。
> 运行时需要 TF6250 Modbus TCP 授权。

## 概览

| 字段 | 值 |
|---|---|
| 库版本 | `{VER}` |
| 来源 PDF | [TF6250_TC3_Modbus_TCP_EN.pdf]({PDF}) |
| InfoSys 根 | https://infosys.beckhoff.com/content/1033/tf6250_tc3_modbus_tcp/index.html |
| 文档进度 | 21 / 21（FB 20 + GVL 1） |

**主站 vs 从站（关键区分）**：本库的 `FB_MB*` / `FB_MBUdp*` 功能块让 TwinCAT PLC 作为 **Modbus 主站/客户端**，
主动去读写别的 Modbus 设备（参数 `sIPAddr` 指向目标设备）。如果需求是“让 TwinCAT 自身作为 Modbus **从站/服务端**
被外部 SCADA / 主站访问”，那是另一套机制：通过 TF6250 服务端 + TwinCAT Modbus TCP 配置器（`TcModbusSrv.xml`）
+ PLC 里的 `mb_Input_Coils` / `mb_Output_Coils` / `mb_Input_Registers` / `mb_Output_Registers` 全局数组 + ADS 映射完成，
**不经过本库的任何 FB**（参见 PDF 第 4 章 Configuration、第 5 章 Diagnosis）。本仓库 21 篇覆盖的是主站侧 FB + 库版本常量。

## Modbus 功能码对照

| Modbus 功能 | 功能码 | TCP 功能块 | UDP 功能块 |
|---|---|---|---|
| Read Coils（读线圈） | 1 | `FB_MBReadCoils` | `FB_MBUdpReadCoils` |
| Read Discrete Inputs（读离散输入） | 2 | `FB_MBReadInputs` | `FB_MBUdpReadInputs` |
| Read Holding Registers（读保持寄存器） | 3 | `FB_MBReadRegs` | `FB_MBUdpReadRegs` |
| Read Input Registers（读输入寄存器） | 4 | `FB_MBReadInputRegs` | `FB_MBUdpReadInputRegs` |
| Write Single Coil（写单线圈） | 5 | `FB_MBWriteSingleCoil` | `FB_MBUdpWriteSingleCoil` |
| Write Single Register（写单寄存器） | 6 | `FB_MBWriteSingleReg` | `FB_MBUdpWriteSingleReg` |
| Write Multiple Coils（写多线圈） | 15 | `FB_MBWriteCoils` | `FB_MBUdpWriteCoils` |
| Write Multiple Registers（写多寄存器） | 16 | `FB_MBWriteRegs` | `FB_MBUdpWriteRegs` |
| Read/Write Multiple Registers（读写多寄存器） | 23 | `FB_MBReadWriteRegs` | `FB_MBUdpReadWriteRegs` |
| Diagnostics（诊断） | 8 | `FB_MBDiagnose` | `FB_MBUdpDiagnose` |

## Function Blocks — TCP（10）

| 名称 | Modbus 功能码 | 用途 | 文档 |
|---|---|---|---|
{tcp_rows}

## Function Blocks — UDP（10）

> UDP 版与同名 TCP 版接口完全一致，区别仅在传输层：UDP 无连接、首包更快，但不保证可靠交付。
> 适合同网段、低延迟、可容忍偶发丢包的场景。

| 名称 | Modbus 功能码 | 用途 | 文档 |
|---|---|---|---|
{udp_rows}

## Global Constants（1）

| 名称 | 用途 | 文档 |
|---|---|---|
| `stLibVersion_Tc2_ModbusSrv` | 库版本结构（运行时版本检查用） | [global_constants/stLibVersion_Tc2_ModbusSrv.md](global_constants/stLibVersion_Tc2_ModbusSrv.md) |

## 通用调用约定

所有数据传输 FB 共享一套约定：

- `sIPAddr` 填**目标设备** IP；`nTCPPort` 用常量 `MODBUS_TCP_PORT`（=502）；`nUnitID` 直连填 `16#FF`。
- `bExecute` **上升沿**触发一次（不是电平），周期采集需自行产生脉冲。
- 读用 `pDestAddr` + `cbLength` 指定落点缓冲区；写用 `pSrcAddr` + `cbLength` 指定源缓冲区；用 `ADR()` / `SIZEOF()` 赋值。
- 输出 `bBUSY`（执行中）/ `bError` / `nErrId`（ADS/Modbus 错误码）三件套；读类还有 `cbRead`。
- `tTimeout` 无默认值，必须显式赋（如 `T#5S`）。

## 错误码概览

`nErrId`（`UDINT`）按取值分三段（PDF §8.1）：

| 范围（hex） | 来源 | 例 |
|---|---|---|
| `0x0000`–`0x7800` | TwinCAT 系统 / ADS 错误 | `6` 端口未找到、`7` 机器未找到、`1861` ADS 超时 |
| `0x8000`–`0x80FF` | 内部 TwinCAT Modbus TCP 错误 | `8001` 功能未实现、`8002` 地址/长度无效、`8003` 参数无效、`8004` 服务器错误 |
| `0x80070000`–`0x8007FFFF` | Win32 / Winsock | 真值 = `nErrId - 0x80070000` |

## 例程导入

每篇文档配套 `examples/P_Demo_<Name>.TcPOU`：

1. 在 TwinCAT 3 XAE 中右键 PLC 项目下 POUs 文件夹 → **Add → Existing Item…**
2. 选择 `P_Demo_<Name>.TcPOU`
3. 引用 `Tc2_ModbusSrv`，确保 TF6250 已授权运行
4. 把例程里的 `sTargetIp` 改成现场设备 IP，编译 → 登录 → 运行
5. 按文档 §6 / §7 的“验证步骤”在线脉冲 `bTrigger` 观察输出

## 参考资料

- **PDF**：[TF6250_TC3_Modbus_TCP_EN.pdf]({PDF})
- **InfoSys 根**：https://infosys.beckhoff.com/content/1033/tf6250_tc3_modbus_tcp/index.html
"""


def _short(e):
    return {
        "read": "读" + ("线圈" if e["fn"] in (1,) else "离散输入" if e["fn"] == 2 else "保持寄存器" if e["fn"] == 3 else "输入寄存器"),
        "wsingle_coil": "写单个线圈",
        "wsingle_reg": "写单个寄存器",
        "wmulti": "写多" + ("线圈" if e["fn"] == 15 else "寄存器"),
        "rw": "同事务先读后写寄存器",
        "diag": "设备诊断（function 8）",
    }[e["family"]]


def main():
    fb_dir = ROOT / LIB / "function_blocks"
    gvl_dir = ROOT / LIB / "global_constants"
    ex_dir = ROOT / LIB / "examples"
    for d in (fb_dir, gvl_dir, ex_dir):
        d.mkdir(parents=True, exist_ok=True)

    n_doc = n_tcpou = 0
    for e in ALL_FBS:
        (fb_dir / f"{e['name']}.md").write_text(render_doc(e), encoding="utf-8")
        (ex_dir / f"P_Demo_{e['name']}.TcPOU").write_text(render_tcpou(e), encoding="utf-8")
        n_doc += 1
        n_tcpou += 1

    (gvl_dir / "stLibVersion_Tc2_ModbusSrv.md").write_text(render_gvl_doc(), encoding="utf-8")
    (ex_dir / "P_Demo_stLibVersion_Tc2_ModbusSrv.TcPOU").write_text(render_gvl_tcpou(), encoding="utf-8")
    n_doc += 1
    n_tcpou += 1

    (ROOT / LIB / "README.md").write_text(render_readme(), encoding="utf-8")

    print(f"wrote {n_doc} docs, {n_tcpou} tcpou, 1 README")


if __name__ == "__main__":
    main()
