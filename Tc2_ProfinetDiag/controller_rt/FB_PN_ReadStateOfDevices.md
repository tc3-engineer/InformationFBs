# FB_PN_ReadStateOfDevices

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ProfinetDiag` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `controller_rt` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/14977342347.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PN_ReadStateOfDevices.TcPOU`](../examples/P_Demo_FB_PN_ReadStateOfDevices.TcPOU) |

---

## 1. 功能简述

读取 PROFINET RT 控制器下所有从站的总体状态。调用后返回已组态设备数、处于错误/诊断状态的设备数、以及带诊断的设备数，用于一眼掌握整条 PROFINET 网络的健康度。仅适用于 PROFINET RT Controller 驱动版本 v03（v0.21）及以上（XAE 的 PROFINET RT Controller I/O 设备里可查驱动版本）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  bExecute               : BOOL;
  NETID                  : T_AmsNetIdArr;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bExecute` | `BOOL` | 上升沿（FALSE→TRUE）触发功能块执行一次。 |
| `NETID` | `T_AmsNetIdArr` | PROFINET RT 控制器的 AMS Net ID。⚠️ PDF/InfoSys 代码块中类型印作 `T_AmsNetIdArr`（描述表写 `T_AmsNetId`），以代码块声明 `T_AmsNetIdArr` 为准。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bBusy                      : BOOL;
  bError                     : BOOL;
  nErrorID                   : UDINT;
  nDevices                   : UINT;
  PnIoError                  : UINT;
  PnIoDiag                   : UINT
  sControllerDriverVersion   : STRING;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 功能块使能后该输出置位，并一直保持到收到设备反馈为止。`bBusy = TRUE` 期间不接受输入端的新命令（不响应新的触发）。 |
| `bError` | `BOOL` | 命令传输过程中发生错误时，在 `bBusy` 复位（落沿）之后置位该输出。 |
| `nErrorID` | `UDINT` | `bError` 置位时返回 ADS 错误号（见 §4）。 |
| `nDevices` | `UINT` | 已组态的设备数（最多 255）。 |
| `PnIoError` | `UINT` | 处于错误状态或带诊断的设备数。 |
| `PnIoDiag` | `UINT` | 带诊断的设备数。 |
| `sControllerDriverVersion` | `STRING` | PROFINET 控制器驱动版本（需 03 / V00.21 及以上）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

本功能块是基于 ADS 的异步功能块，内部维护「空闲 → 忙 → 完成」三态状态机。`bExecute` 由 FALSE 变为 TRUE 的上升沿触发一次操作：触发后 `bBusy` 立即置 TRUE，功能块通过 ADS 把请求发往 PROFINET 控制器（由 `NETID` 与 `PORT` 寻址到目标设备）；收到设备应答后 `bBusy` 落回 FALSE，此时 `nDevices` / `PnIoError` / `PnIoDiag` / `sControllerDriverVersion` 才有效，若过程出错则 `bError` 在 `bBusy` 落沿之后置 TRUE、`nErrorID` 给出 ADS 错误号。`bBusy = TRUE` 期间功能块忽略输入端的任何新触发，必须等到本次完成才能再次发起。

**调用周期**：必须在每个 PLC 周期持续调用本实例（不是只在触发那一帧调一次），否则内部 ADS 状态机无法推进、`bBusy` 不会落沿。**清错语义**：错误状态保持到下一次 `bExecute` 上升沿被接受时才更新，因此读 `bError`/`nErrorID` 要在 `bBusy` 落沿之后、下一次触发之前读。**电平 vs 边沿**：`bExecute` 保持高电平不会反复执行，只在跳变沿触发一次；要重复操作必须先把 `bExecute` 拉回 FALSE 再拉高。

**版本前提**：本 FB 仅在 PROFINET RT Controller 驱动版本 v03（V00.21）或更高时可用，低版本驱动调用会报错。可在 TwinCAT XAE 的 PROFINET RT Controller I/O 设备属性里查看实际驱动版本。

## 4. 错误码 / 返回值

`nErrorID` 在 `bError = TRUE` 时返回 ADS 错误号（`bError = FALSE` 时无意义）。下表摘自 PDF §5.1「ADS Return Codes」的常见取值：

| `nErrorID` (dec) | Hex | 名称 | 含义 / 处理建议 |
|---|---|---|---|
| `0` | `0x0` | `ERR_NOERROR` | 无错误，操作成功；读取输出结果 |
| `6` | `0x6` | `ERR_TARGETPORTNOTFOUND` | 目标端口未找到——`PORT` 错误，或目标 ADS 服务未启动/不可达。检查 `PORT` 与设备状态 |
| `7` | `0x7` | `ERR_TARGETMACHINENOTFOUND` | 目标设备未找到——AMS 路由不存在。检查 `NETID` 与路由表 |
| `16` | `0x10` | `ERR_LOWINSTLEVEL` | 授权等级过低（许可证问题） |
| `1280` | `0x500` | `ROUTERERR_NOLOCKEDMEMORY` | 路由锁定内存不足 |
| `1792`+ | `0x700`+ | 一般 ADS 错误 | 命令相关错误（如设备拒绝、参数非法）；可对照 PDF §5.1「General ADS error codes」一节查全 |

> 完整 ADS 返回码表（Global / Router / General ADS / RTime 四组）参见 PDF §5.1 章节。⚠️ PDF 与 InfoSys 均未给出本库各 FB 专属的错误码子集，上表为 ADS 通用码。

## 5. 使用注意 / 常见坑

- **驱动版本要求**：v03（V00.21）以上。低版本会调用失败。
- **适合做总览**：本 FB 给的是「计数级」总览（多少设备、多少报错），要看具体哪个设备出问题，再用 `FB_PN_ReadCompleteInfoOfDevices` 取每台明细。
- **PDF 类型怪字**：`NETID` 在代码块印作 `T_AmsNetIdArr`，输出 `PnIoDiag` 行末缺分号——均按 PDF 逐字保留。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PN_ReadStateOfDevices.TcPOU`](../examples/P_Demo_FB_PN_ReadStateOfDevices.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_PN_ReadStateOfDevices
VAR
    fbReadState   : FB_PN_ReadStateOfDevices;
    bReadOverview : BOOL := FALSE;            // 在线上升沿触发一次总览读取
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
    nCfgDevices   : UINT;                     // 已组态设备数
    nErrDevices   : UINT;                     // 错误/诊断设备数
    nDiagDevices  : UINT;                     // 带诊断设备数
    sDrvVer       : STRING;                   // 控制器驱动版本
END_VAR

// 上升沿触发；读出整网总览计数（需 RT Controller 驱动 v03/V00.21+）
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

// IF nErrDevices > 0 THEN 下钻调用 FB_PN_ReadCompleteInfoOfDevices 查明细
```

## 7. 业务场景与实际价值

- **场景**：HMI 首页放一个「PROFINET 网络健康」仪表盘，显示「组态 X 台 / 异常 Y 台 / 诊断 Z 台」。
- **价值**：一次调用拿到三个计数，免去逐台轮询；异常计数 > 0 时再下钻查明细。
- **替代方案对比**：逐台读状态既慢又繁；本 FB 由控制器汇总，一次返回总览。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf) 第 3.1.3.1 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/14977342347.html
- **相关 FB / FC**：`FB_PN_ReadCompleteInfoOfDevices`（逐台明细）、`ST_PN_DeviceInfo`（设备信息结构）
