# FB_PN_IM2_READ

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ProfinetDiag` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `controller_im` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/14965825419.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PN_IM2_READ.TcPOU`](../examples/P_Demo_FB_PN_IM2_READ.TcPOU) |

---

## 1. 功能简述

PROFINET 控制器用本功能块从指定 `PORT` 引用的设备读取全部 I&M2 数据。I&M2 帧结构对应 PROFINET 标准索引 `0xAFF2`，承载设备安装日期。本 FB 把安装日期以 `TIMESTRUCT` 结构（格式 `<YYYY-MM-DD HH:MM>`）输出。

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
  bBusy                   : BOOL;
  str_Date                : TIMESTRUCT; (*YYYY-MM-DD HH:MM*);
  bError                  : BOOL;
  iErrorID                : UDINT;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 功能块使能后该输出置位，并一直保持到收到设备反馈为止。`bBusy = TRUE` 期间不接受输入端的新命令（不响应新的触发）。 |
| `str_Date` | `TIMESTRUCT` | 返回设备安装日期，格式 `<YYYY-MM-DD HH:MM>`。 |
| `bError` | `BOOL` | 命令传输过程中发生错误时，在 `bBusy` 复位（落沿）之后置位该输出。 |
| `iErrorID` | `UDINT` | `bError` 置位时返回 ADS 错误号（见 §4 错误码表）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

本功能块是基于 ADS 的异步功能块，内部维护「空闲 → 忙 → 完成」三态状态机。`bStart` 由 FALSE 变为 TRUE 的上升沿触发一次操作：触发后 `bBusy` 立即置 TRUE，功能块通过 ADS 把请求发往 PROFINET 控制器（由 `NETID` 与 `PORT` 寻址到目标设备）；收到设备应答后 `bBusy` 落回 FALSE，此时 `str_Date`（安装日期） 才有效，若过程出错则 `bError` 在 `bBusy` 落沿之后置 TRUE、`iErrorID` 给出 ADS 错误号。`bBusy = TRUE` 期间功能块忽略输入端的任何新触发，必须等到本次完成才能再次发起。

**调用周期**：必须在每个 PLC 周期持续调用本实例（不是只在触发那一帧调一次），否则内部 ADS 状态机无法推进、`bBusy` 不会落沿。**清错语义**：错误状态保持到下一次 `bStart` 上升沿被接受时才更新，因此读 `bError`/`iErrorID` 要在 `bBusy` 落沿之后、下一次触发之前读。**电平 vs 边沿**：`bStart` 保持高电平不会反复执行，只在跳变沿触发一次；要重复操作必须先把 `bStart` 拉回 FALSE 再拉高。

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

- **必须每周期调用**：本 FB 异步执行，只在触发沿那一帧调一次会导致 `bBusy` 永远不落沿。请放在周期任务里无条件调用。
- **一设备一实例**：每个 PROFINET 设备用独立的 FB 实例；同一实例复用到多个目标会造成请求错乱。
- **`PORT` 的算法**：`PORT = Device ID + 16#1000`（设备 ID 加十六进制 1000）。Device ID 可在 TwinCAT XAE 的 PROFINET 设备树里查到。（工程经验补充）
- I&M2 可读可写：本 FB 读安装日期，`FB_PN_IM2_WRITE` 写。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PN_IM2_READ.TcPOU`](../examples/P_Demo_FB_PN_IM2_READ.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_PN_IM2_READ
VAR
    fbFB_PN_IM2_READ : FB_PN_IM2_READ;        // FB_PN_IM2_READ 实例
    bReadIM       : BOOL := FALSE;            // 在线上升沿触发一次读取
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
    stInstallDate : TIMESTRUCT;              // 设备安装日期 YYYY-MM-DD HH:MM
END_VAR

// 上升沿触发一次 I&M 读取；读到的数据在 bBusy 落沿后有效
fbFB_PN_IM2_READ(
    bStart := bReadIM,
    NETID  := '',
    PORT   := 16#1001,
    bBusy  => bBusy,
    str_Date => stInstallDate,
    bError => bErr,
    iErrorID => nErrId
);
```

## 7. 业务场景与实际价值

- **场景**：读设备安装/投运日期，用于计算设备役龄、安排周期性维护或质保到期提醒。
- **价值**：日期随设备存储在 PROFINET 设备里，本 FB 直接以 `TIMESTRUCT` 读出，免去日期帧解析。
- **替代方案对比**：维护台账靠人维护易脱节；I&M2 日期与物理设备绑定，更可靠。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf) 第 3.1.2.4 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/14965825419.html
- **相关 FB / FC**：`FB_PN_IM2_WRITE`（写 I&M2）、`str_IM_0xAFF2`（数据结构）
