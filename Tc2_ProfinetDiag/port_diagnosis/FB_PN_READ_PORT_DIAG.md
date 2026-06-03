# FB_PN_READ_PORT_DIAG

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ProfinetDiag` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `port_diagnosis` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/14966195083.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PN_READ_PORT_DIAG.TcPOU`](../examples/P_Demo_FB_PN_READ_PORT_DIAG.TcPOU) |

---

## 1. 功能简述

读取 PROFINET 设备各端口的诊断信息。调用后通过 `str_RemotePort_1` / `str_RemotePort_2` 给出端口 1、端口 2 的诊断/邻居信息。注：PDF 中本 FB 的输出结构类型印作 `str_GetPortStatistic`（逐字保留），承载端口的统计/诊断数据。

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
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 功能块使能后该输出置位，并一直保持到收到设备反馈为止。`bBusy = TRUE` 期间不接受输入端的新命令（不响应新的触发）。 |
| `str_RemotePort_1` | `str_GetPortStatistic` | 端口 1 的诊断数据结构。⚠️ PDF/InfoSys 此输出类型印作 `str_GetPortStatistic`（端口诊断帧 `str_PortDiag` 含 PortId/邻居名/描述等，类型以代码块逐字为准）。 |
| `str_RemotePort_2` | `str_GetPortStatistic` | 端口 2 的诊断数据结构（同上）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

本功能块是基于 ADS 的异步功能块，内部维护「空闲 → 忙 → 完成」三态状态机。`bStart` 由 FALSE 变为 TRUE 的上升沿触发一次操作：触发后 `bBusy` 立即置 TRUE，功能块通过 ADS 把请求发往 PROFINET 控制器（由 `NETID` 与 `PORT` 寻址到目标设备）；收到设备应答后 `bBusy` 落回 FALSE，此时 `str_RemotePort_1` / `str_RemotePort_2` 才有效，若过程出错则 `bError` 在 `bBusy` 落沿之后置 TRUE、`（本 FB 无错误号输出）` 给出 ADS 错误号。`bBusy = TRUE` 期间功能块忽略输入端的任何新触发，必须等到本次完成才能再次发起。

**调用周期**：必须在每个 PLC 周期持续调用本实例（不是只在触发那一帧调一次），否则内部 ADS 状态机无法推进、`bBusy` 不会落沿。**清错语义**：错误状态保持到下一次 `bStart` 上升沿被接受时才更新，因此读 `bError`/`（本 FB 无错误号输出）` 要在 `bBusy` 落沿之后、下一次触发之前读。**电平 vs 边沿**：`bStart` 保持高电平不会反复执行，只在跳变沿触发一次；要重复操作必须先把 `bStart` 拉回 FALSE 再拉高。

**与 `FB_PN_GET_PORT_STATISTIC` 的区别**：后者侧重端口流量统计（含 link 标志 `bPort1/2`），本 FB 侧重端口诊断/拓扑邻居信息。**注意本 FB 同样无 `bError`/`iErrorID` 输出**，且无 `bPort1/2` 链路标志。**PDF 类型怪字**：输出结构在 PDF 中印作 `str_GetPortStatistic`（库里另有 `str_PortDiag` 结构含 PortId/SystemName/ChassisId 等拓扑字段），代码块按 PDF 逐字保留。

## 4. 错误码 / 返回值

本功能块无错误码 / 错误号输出端。⚠️ PDF 与 InfoSys 均未给出本 FB 的错误反馈机制。

## 5. 使用注意 / 常见坑

- **无错误/链路输出**：仅 `bBusy` + 两个端口结构。
- **侧重拓扑/邻居诊断**：与端口统计 FB 互补，一个看流量、一个看诊断。
- **PDF 类型印为 `str_GetPortStatistic`**：库内另有 `str_PortDiag`（PortId/邻居信息），代码块逐字保留 PDF 写法。
- **必须每周期调用**：本 FB 异步执行，只在触发沿那一帧调一次会导致 `bBusy` 永远不落沿。请放在周期任务里无条件调用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PN_READ_PORT_DIAG.TcPOU`](../examples/P_Demo_FB_PN_READ_PORT_DIAG.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_PN_READ_PORT_DIAG
VAR
    fbReadDiag    : FB_PN_READ_PORT_DIAG;
    bReadReq      : BOOL := FALSE;            // 在线上升沿触发
    bBusy         : BOOL;
    stPort1       : str_GetPortStatistic;     // 端口1诊断
    stPort2       : str_GetPortStatistic;     // 端口2诊断
END_VAR

// 上升沿触发；读两个端口的诊断信息（无错误号输出，按 PDF 类型为 str_GetPortStatistic）
fbReadDiag(
    bStart := bReadReq,
    NETID  := '',
    PORT   := 16#1001,
    bBusy  => bBusy,
    str_RemotePort_1 => stPort1,
    str_RemotePort_2 => stPort2
);
```

## 7. 业务场景与实际价值

- **场景**：排查 PROFINET 拓扑接错（某端口接到了非预期邻居）或链路诊断，读出端口诊断信息核对实际拓扑。
- **价值**：把端口诊断读进 PLC，可与组态拓扑比对，自动发现接线错误。
- **替代方案对比**：靠人对照接线图易错；本 FB 让 PLC 读实际端口诊断做自动核对。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf) 第 3.4 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/14966195083.html
- **相关 FB / FC**：`FB_PN_GET_PORT_STATISTIC`（端口流量统计）、`str_PortDiag` / `str_GetPortStatistic`（数据结构）
