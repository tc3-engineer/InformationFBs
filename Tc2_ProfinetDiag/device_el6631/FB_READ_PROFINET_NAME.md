# FB_READ_PROFINET_NAME

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ProfinetDiag` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `device_el6631` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/15019056267.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_READ_PROFINET_NAME.TcPOU`](../examples/P_Demo_FB_READ_PROFINET_NAME.TcPOU) |

---

## 1. 功能简述

读取 EL6631-0010（PROFINET 设备端子）的 PROFINET 名称；若配置了虚拟 EL6631-0010，也一并读出。输出 `nCntEL6631_Slave` 指示当前是物理还是虚拟端子，`arPROFINET_NAME`（`ARRAY [1..2] OF STRING(240)`）给出名称。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  bStart  : BOOL;
  NETID   : T_AmsNetId;
  PORT    : T_AmsPort;
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
  bBusy                 : BOOL;
  bError                : BOOL;
  nCntEL6631_Slave      : BYTE
  arPROFINET_NAME       : ARRAY [1..2] OF STRING(240)
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 功能块使能后该输出置位，并一直保持到收到设备反馈为止。`bBusy = TRUE` 期间不接受输入端的新命令（不响应新的触发）。 |
| `bError` | `BOOL` | 命令传输过程中发生错误时，在 `bBusy` 复位（落沿）之后置位该输出。 |
| `nCntEL6631_Slave` | `BYTE` | 指示 EL6631-0010 的呈现方式：`0` = 物理 EL6631-0010，`1` = 虚拟 EL6631-0010。 |
| `arPROFINET_NAME` | `ARRAY [1..2] OF STRING(240)` | EL6631-0010 及（若配置）虚拟 EL6631-0010 的 PROFINET 名称。 |

### VAR_IN_OUT

无。

## 3. 行为说明

本功能块是基于 ADS 的异步功能块，内部维护「空闲 → 忙 → 完成」三态状态机。`bStart` 由 FALSE 变为 TRUE 的上升沿触发一次操作：触发后 `bBusy` 立即置 TRUE，功能块通过 ADS 把请求发往 PROFINET 控制器（由 `NETID` 与 `PORT` 寻址到目标设备）；收到设备应答后 `bBusy` 落回 FALSE，此时 `nCntEL6631_Slave` 与 `arPROFINET_NAME` 数组 才有效，若过程出错则 `bError` 在 `bBusy` 落沿之后置 TRUE、`（本 FB 输出 `bError` 但无 `iErrorID`）` 给出 ADS 错误号。`bBusy = TRUE` 期间功能块忽略输入端的任何新触发，必须等到本次完成才能再次发起。

**调用周期**：必须在每个 PLC 周期持续调用本实例（不是只在触发那一帧调一次），否则内部 ADS 状态机无法推进、`bBusy` 不会落沿。**清错语义**：错误状态保持到下一次 `bStart` 上升沿被接受时才更新，因此读 `bError`/`（本 FB 输出 `bError` 但无 `iErrorID`）` 要在 `bBusy` 落沿之后、下一次触发之前读。**电平 vs 边沿**：`bStart` 保持高电平不会反复执行，只在跳变沿触发一次；要重复操作必须先把 `bStart` 拉回 FALSE 再拉高。

**设备侧 FB**：本 FB 用于 EtherCAT 上的 EL6631-0010 PROFINET Device 端子（设备端，区别于 §3.1 的控制器端 FB）。**双名数组**：一个 EL6631-0010 可映射物理 + 虚拟两个 PROFINET 设备，故名称用 2 元数组返回，`nCntEL6631_Slave` 指明类型。**注意本 FB 无 `iErrorID` 输出**，只能靠 `bError` 判断成败。

## 4. 错误码 / 返回值

本功能块没有错误号输出端，仅通过 `bError`（若有）/ `bBusy` 反馈执行状态：`bError = TRUE` 表示传输过程出错（在 `bBusy` 落沿后置位）。⚠️ PDF 与 InfoSys 均未给出本 FB 的具体错误码取值。

## 5. 使用注意 / 常见坑

- **专用于 EL6631-0010**：设备端 PROFINET 端子，不是控制器侧 FB。
- **无 `iErrorID`**：本 FB 仅有 `bError`，没有错误号输出（与库内多数 FB 不同）。
- **PDF 排版怪字**：`nCntEL6631_Slave` 与 `arPROFINET_NAME` 两行末尾在 PDF 中缺分号，按逐字保留。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_READ_PROFINET_NAME.TcPOU`](../examples/P_Demo_FB_READ_PROFINET_NAME.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_READ_PROFINET_NAME
VAR
    fbReadPnName  : FB_READ_PROFINET_NAME;
    bReadReq      : BOOL := FALSE;            // 在线上升沿触发
    bBusy         : BOOL;
    bErr          : BOOL;
    nSlaveKind    : BYTE;                     // 0=物理 EL6631 / 1=虚拟
    aPnNames      : ARRAY [1..2] OF STRING(240);   // [1]=物理 [2]=虚拟 名称
END_VAR

// 上升沿触发；读 EL6631-0010 的 PROFINET 名称（无 iErrorID，靠 bError 判错）
fbReadPnName(
    bStart := bReadReq,
    NETID  := '',
    PORT   := 16#1001,
    bBusy  => bBusy,
    bError => bErr,
    nCntEL6631_Slave => nSlaveKind,
    arPROFINET_NAME => aPnNames
);
```

## 7. 业务场景与实际价值

- **场景**：用 EL6631-0010 把 EtherCAT 工位接入上级 PROFINET 网络时，设备端 PLC 需要知道本端子当前的 PROFINET 名称（供 HMI 显示或与上位组态核对）。
- **价值**：直接读出端子的 PROFINET 名称（含虚拟设备），免去查工程组态。
- **替代方案对比**：从 EtherCAT CoE/工程软件查名称繁琐；本 FB 在运行时一次读出。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf) 第 3.2.1.1 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/15019056267.html
- **相关 FB / FC**：`FB_Read_IuM_EL6631_0010` / `FB_Write_IuM_EL6631_0010`（EL6631 的 I&M 读写）
