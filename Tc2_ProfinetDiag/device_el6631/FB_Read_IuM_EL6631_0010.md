# FB_Read_IuM_EL6631_0010

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ProfinetDiag` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `device_el6631` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/15095820299.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_Read_IuM_EL6631_0010.TcPOU`](../examples/P_Demo_FB_Read_IuM_EL6631_0010.TcPOU) |

---

## 1. 功能简述

从 PROFINET 设备（EL6631-0010）经 EtherCAT 以字符串形式读取 I&M1、I&M2、I&M3、I&M4 数据；I&M0 数据则通过 CoE（CAN over EtherCAT）读取。`iNumber` 选择端子映射的两台设备之一（0 或 1），读回的功能/位置/日期/描述/签名分别通过各 STRING 输出给出。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  bRead             : BOOL;;
  NETID             : T_AmsNetId;
  PORT              : T_AmsPort;
  iNumber           : INT:=0;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bRead` | `BOOL` | 上升沿使能功能块，从 PROFINET 设备读取 I&M 数据。⚠️ PDF 原文此行印作 `bRead : BOOL;;`（多一分号）。 |
| `NETID` | `T_AmsNetId` | 控制器（PROFINET Controller）的 AMS Net ID。本机控制器填空串 `''`。 |
| `PORT` | `T_AmsPort` | 控制器与设备通讯所用的 ADS 端口（port = Device ID + 1000hex）。 |
| `iNumber` | `INT` | 一个端子可映射两个 PROFINET 设备，用 `iNumber`（`0` 或 `1`）选择读哪个设备。默认 `0`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  iErrorID                : UDINT;
  st_IM_TagFunction       : STRING; (* I&M1 *)
  st_IM_TagLocation       : STRING; (* I&M1 *)
  st_IM_Date              : STRING; (* I&M2 *)
  st_IM_Descriptor        : STRING; (* I&M3 *)
  st_IM_Signature         : STRING; (* I&M4 *)
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 功能块使能后该输出置位，并一直保持到收到设备反馈为止。`bBusy = TRUE` 期间不接受输入端的新命令（不响应新的触发）。 |
| `bError` | `BOOL` | 命令传输过程中发生错误时，在 `bBusy` 复位（落沿）之后置位该输出。 |
| `iErrorID` | `UDINT` | `bError` 置位时返回 ADS 错误号（见 §4 错误码表）。 |
| `st_IM_TagFunction` | `STRING` | 读回的设备功能标签（I&M1）。 |
| `st_IM_TagLocation` | `STRING` | 读回的设备安装位置标签（I&M1）。 |
| `st_IM_Date` | `STRING` | 读回的设备安装日期（I&M2）。 |
| `st_IM_Descriptor` | `STRING` | 读回的厂商描述（I&M3）。 |
| `st_IM_Signature` | `STRING` | 读回的厂商签名（I&M4）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

本功能块是基于 ADS 的异步功能块，内部维护「空闲 → 忙 → 完成」三态状态机。`bRead` 由 FALSE 变为 TRUE 的上升沿触发一次操作：触发后 `bBusy` 立即置 TRUE，功能块通过 ADS 把请求发往 PROFINET 控制器（由 `NETID` 与 `PORT` 寻址到目标设备）；收到设备应答后 `bBusy` 落回 FALSE，此时 五个 I&M 字符串输出（功能/位置/日期/描述/签名） 才有效，若过程出错则 `bError` 在 `bBusy` 落沿之后置 TRUE、`iErrorID` 给出 ADS 错误号。`bBusy = TRUE` 期间功能块忽略输入端的任何新触发，必须等到本次完成才能再次发起。

**调用周期**：必须在每个 PLC 周期持续调用本实例（不是只在触发那一帧调一次），否则内部 ADS 状态机无法推进、`bBusy` 不会落沿。**清错语义**：错误状态保持到下一次 `bRead` 上升沿被接受时才更新，因此读 `bError`/`iErrorID` 要在 `bBusy` 落沿之后、下一次触发之前读。**电平 vs 边沿**：`bRead` 保持高电平不会反复执行，只在跳变沿触发一次；要重复操作必须先把 `bRead` 拉回 FALSE 再拉高。

**一次读齐 I&M1~I&M4**：本 FB 一次把 I&M1~I&M4 五段文本全部读回（不像控制器侧按记录分多个 FB）。I&M0 走 CoE 单独读取（不在本 FB 输出里）。**双设备选择**：`iNumber` 选 0/1。**经 EtherCAT 读取**：设备端 FB。

## 4. 错误码 / 返回值

`iErrorID` 在 `bError = TRUE` 时返回 ADS 错误号（`bError = FALSE` 时无意义）。下表摘自 PDF §5.1「ADS Return Codes」的常见取值：

| `iErrorID` (dec) | Hex | 名称 | 含义 / 处理建议 |
|---|---|---|---|
| `0` | `0x0` | `ERR_NOERROR` | 无错误，操作成功；读取输出结果 |
| `6` | `0x6` | `ERR_TARGETPORTNOTFOUND` | 目标端口未找到——`PORT` 错误，或目标 ADS 服务未启动/不可达。检查 `PORT` 与设备状态 |
| `7` | `0x7` | `ERR_TARGETMACHINENOTFOUND` | 目标设备未找到——AMS 路由不存在。检查 `NETID` 与路由表 |
| `16` | `0x10` | `ERR_LOWINSTLEVEL` | 授权等级过低（许可证问题） |
| `1280` | `0x500` | `ROUTERERR_NOLOCKEDMEMORY` | 路由锁定内存不足 |
| `1792`+ | `0x700`+ | 一般 ADS 错误 | 命令相关错误（如设备拒绝、参数非法）；可对照 PDF §5.1「General ADS error codes」一节查全 |

> 完整 ADS 返回码表（Global / Router / General ADS / RTime 四组）参见 PDF §5.1 章节。⚠️ PDF 与 InfoSys 均未给出本库各 FB 专属的错误码子集，上表为 ADS 通用码。

## 5. 使用注意 / 常见坑

- **一次读齐**：I&M1~I&M4 全部经一次调用读回（设备端便利封装）。
- **I&M0 走 CoE**：本 FB 不含 I&M0；I&M0 通过 CoE 单独读。
- **PDF 排版怪字**：输入 `bRead` 行 PDF 印作 `bRead : BOOL;;`（多一个分号），按逐字保留，类型为 `BOOL`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_Read_IuM_EL6631_0010.TcPOU`](../examples/P_Demo_FB_Read_IuM_EL6631_0010.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_Read_IuM_EL6631_0010
VAR
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
END_VAR

// 上升沿触发；一次读齐 I&M1~I&M4（iNumber=0 选第一台）
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
);
```

## 7. 业务场景与实际价值

- **场景**：EL6631-0010 设备端 PLC 读回自身或对端写入的电子铭牌，做自检或上报 HMI。
- **价值**：一次读齐 I&M1~I&M4 五段文本，免去逐项读取。
- **替代方案对比**：逐项读需多次调用；本 FB 一次完成，配合 `FB_Write_IuM_EL6631_0010` 形成读写对。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf) 第 3.2.1.3 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/15095820299.html
- **相关 FB / FC**：`FB_Write_IuM_EL6631_0010`（写 EL6631 的 I&M）、`FB_READ_PROFINET_NAME`
