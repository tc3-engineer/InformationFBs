# FB_PN_GET_PORT_STATISTIC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ProfinetDiag` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `port_diagnosis` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/14966141067.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PN_GET_PORT_STATISTIC.TcPOU`](../examples/P_Demo_FB_PN_GET_PORT_STATISTIC.TcPOU) |

---

## 1. 功能简述

读取 PROFINET 设备各端口的统计数据。调用后通过 `str_RemotePort_1` / `str_RemotePort_2`（`str_GetPortStatistic`）分别给出端口 1、端口 2 的速率、收发字节/包计数、坏包/丢帧数等统计；`bPort1` / `bPort2` 指示对应端口是否有链路（link）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  bStart       : BOOL;
  NETID        : T_AmsNetId;
  PORT         : T_AmsPort;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bStart` | `BOOL` | 上升沿（FALSE→TRUE）触发功能块执行一次。 |
| `NETID` | `T_AmsNetId` | 控制器（PROFINET Controller）的 AMS Net ID。本机控制器填空串 `''`。 |
| `PORT` | `T_AmsPort` | 控制器与设备通讯所用的 ADS 端口（port = Device ID + 1000hex）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bBusy             : BOOL;
  str_RemotePort_1  : str_GetPortStatistic;
  str_RemotePort_2  : str_GetPortStatistic;
  bPort1            : BOOL;
  bPort2            : BOOL;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 功能块使能后该输出置位，并一直保持到收到设备反馈为止。`bBusy = TRUE` 期间不接受输入端的新命令（不响应新的触发）。 |
| `str_RemotePort_1` | `str_GetPortStatistic` | 端口 1 的统计数据结构（速率、收发字节/包、坏包、丢帧等）。 |
| `str_RemotePort_2` | `str_GetPortStatistic` | 端口 2 的统计数据结构（同上）。 |
| `bPort1` | `BOOL` | 端口 1 有链路（link）时为 `TRUE`。 |
| `bPort2` | `BOOL` | 端口 2 有链路（link）时为 `TRUE`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

本功能块是基于 ADS 的异步功能块，内部维护「空闲 → 忙 → 完成」三态状态机。`bStart` 由 FALSE 变为 TRUE 的上升沿触发一次操作：触发后 `bBusy` 立即置 TRUE，功能块通过 ADS 把请求发往 PROFINET 控制器（由 `NETID` 与 `PORT` 寻址到目标设备）；收到设备应答后 `bBusy` 落回 FALSE，此时 `str_RemotePort_1` / `str_RemotePort_2` 与 `bPort1` / `bPort2` 才有效，若过程出错则 `bError` 在 `bBusy` 落沿之后置 TRUE、`（本 FB 无错误号输出）` 给出 ADS 错误号。`bBusy = TRUE` 期间功能块忽略输入端的任何新触发，必须等到本次完成才能再次发起。

**调用周期**：必须在每个 PLC 周期持续调用本实例（不是只在触发那一帧调一次），否则内部 ADS 状态机无法推进、`bBusy` 不会落沿。**清错语义**：错误状态保持到下一次 `bStart` 上升沿被接受时才更新，因此读 `bError`/`（本 FB 无错误号输出）` 要在 `bBusy` 落沿之后、下一次触发之前读。**电平 vs 边沿**：`bStart` 保持高电平不会反复执行，只在跳变沿触发一次；要重复操作必须先把 `bStart` 拉回 FALSE 再拉高。

**注意本 FB 无 `bError`/`iErrorID` 输出**（PDF/InfoSys 输出表仅 5 项）。**链路标志**：先看 `bPort1`/`bPort2` 判断端口是否插了线，再看对应统计结构。**统计用途**：`RxBadPackets`/`RxDroppedFrames` 等计数持续增长往往预示线缆/连接器质量问题，是诊断「偶发丢包」的关键依据。

## 4. 错误码 / 返回值

本功能块无错误码 / 错误号输出端。⚠️ PDF 与 InfoSys 均未给出本 FB 的错误反馈机制。

## 5. 使用注意 / 常见坑

- **无错误输出**：本 FB 只有 `bBusy` 三态中的 busy + 数据输出，没有 `bError`/错误号。
- **先判 link 再看统计**：`bPortN = FALSE` 时该端口统计无意义（没插线）。
- **坏包/丢帧计数是趋势量**：单次值意义不大，要看随时间增长速度判断链路质量。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PN_GET_PORT_STATISTIC.TcPOU`](../examples/P_Demo_FB_PN_GET_PORT_STATISTIC.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_PN_GET_PORT_STATISTIC
VAR
    fbGetStat     : FB_PN_GET_PORT_STATISTIC;
    bGetReq       : BOOL := FALSE;            // 在线上升沿触发读取
    bBusy         : BOOL;
    stPort1       : str_GetPortStatistic;     // 端口1统计
    stPort2       : str_GetPortStatistic;     // 端口2统计
    bP1Link       : BOOL;                     // 端口1有链路
    bP2Link       : BOOL;                     // 端口2有链路
END_VAR

// 上升沿触发；读端口统计（先看 bP1/bP2 link，再看坏包/丢帧计数）
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

// 趋势监控示例：stPort1.RxBadPackets / stPort1.RxDroppedFrames 持续增长 = 链路质量差
```

## 7. 业务场景与实际价值

- **场景**：PROFINET 网络偶发抖动/丢包，怀疑某段线缆或端口质量差。运维读取设备端口统计，看坏包/丢帧计数在哪个端口持续增长，定位物理层问题。
- **价值**：把端口级网络质量统计读进 PLC，可做趋势记录和阈值报警，免去靠交换机网管口逐个查。
- **替代方案对比**：网管交换机能看端口统计但脱离 PLC 逻辑；本 FB 让统计进 PLC，可联动报警与记录。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf) 第 3.3 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/14966141067.html
- **相关 FB / FC**：`FB_PN_READ_PORT_DIAG`（读端口诊断/拓扑）、`str_GetPortStatistic`（数据结构）
