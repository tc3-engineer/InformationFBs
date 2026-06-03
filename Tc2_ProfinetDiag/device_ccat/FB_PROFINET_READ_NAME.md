# FB_PROFINET_READ_NAME

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ProfinetDiag` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `device_ccat` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/15958916491.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PROFINET_READ_NAME.TcPOU`](../examples/P_Demo_FB_PROFINET_READ_NAME.TcPOU) |

---

## 1. 功能简述

返回指定 PROFINET 设备的 PROFINET 名称，以及该名称是否可被 PROFINET 控制器修改的信息。输出 `sProfinetName` 给出设备名，`bNotChangeable = TRUE` 表示控制器不能改这个名称。

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
| `NETID` | `T_AmsNetId` | PROFINET 设备的 AMS Net ID。 |
| `PORT` | `T_AmsPort` | PROFINET 设备的 ADS 端口号；默认 `0xFFFF`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  nErrorID                : UDINT;
  sProfinetName           : STRING(240);
  bNotChangeable          : BOOL;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 功能块使能后该输出置位，并一直保持到收到设备反馈为止。`bBusy = TRUE` 期间不接受输入端的新命令（不响应新的触发）。 |
| `bError` | `BOOL` | 命令传输过程中发生错误时，在 `bBusy` 复位（落沿）之后置位该输出。 |
| `nErrorID` | `UDINT` | `bError` 置位时返回 ADS 错误号（见 §4）。 |
| `sProfinetName` | `STRING(240)` | PROFINET 设备名。最多 240 字符，仅允许 `a..z`、`0..9`、`.`、`-`。 |
| `bNotChangeable` | `BOOL` | 为 `TRUE` 时表示 PROFINET 控制器不能更改该设备的 PROFINET 名称。 |

### VAR_IN_OUT

无。

## 3. 行为说明

本功能块是基于 ADS 的异步功能块，内部维护「空闲 → 忙 → 完成」三态状态机。`bStart` 由 FALSE 变为 TRUE 的上升沿触发一次操作：触发后 `bBusy` 立即置 TRUE，功能块通过 ADS 把请求发往 PROFINET 控制器（由 `NETID` 与 `PORT` 寻址到目标设备）；收到设备应答后 `bBusy` 落回 FALSE，此时 `sProfinetName` 与 `bNotChangeable` 才有效，若过程出错则 `bError` 在 `bBusy` 落沿之后置 TRUE、`nErrorID` 给出 ADS 错误号。`bBusy = TRUE` 期间功能块忽略输入端的任何新触发，必须等到本次完成才能再次发起。

**调用周期**：必须在每个 PLC 周期持续调用本实例（不是只在触发那一帧调一次），否则内部 ADS 状态机无法推进、`bBusy` 不会落沿。**清错语义**：错误状态保持到下一次 `bStart` 上升沿被接受时才更新，因此读 `bError`/`nErrorID` 要在 `bBusy` 落沿之后、下一次触发之前读。**电平 vs 边沿**：`bStart` 保持高电平不会反复执行，只在跳变沿触发一次；要重复操作必须先把 `bStart` 拉回 FALSE 再拉高。

**端口默认 `0xFFFF`**：本组（CCAT/TF6270 设备）FB 的 `PORT` 默认值为 `0xFFFF`（与控制器侧 FB 的 `Device ID + 1000hex` 寻址不同，注意区分）。**`bNotChangeable` 用途**：在调用 `FB_PROFINET_SET_NAME` 改名前先读该位，若为 TRUE 说明设备锁定了名称，改名会失败。

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

- **`PORT` 默认 `0xFFFF`**：CCAT/TF6270 设备组的端口语义与控制器侧不同。
- **先查 `bNotChangeable` 再改名**：避免对锁定名称的设备做无效改名。
- **版本要求**：本 FB 需库版本 >= v1.5.1.0（开发环境 TwinCAT v3.1.4024.55 及以上）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PROFINET_READ_NAME.TcPOU`](../examples/P_Demo_FB_PROFINET_READ_NAME.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_PROFINET_READ_NAME
VAR
    fbReadName    : FB_PROFINET_READ_NAME;
    bReadReq      : BOOL := FALSE;            // 在线上升沿触发
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
    sPnName       : STRING(240);              // 设备 PROFINET 名
    bLocked       : BOOL;                     // TRUE=控制器不能改名
END_VAR

// 上升沿触发；读设备名 + 可改性标志（PORT 默认 0xFFFF）
fbReadName(
    bStart := bReadReq,
    NETID  := '',
    PORT   := 16#FFFF,
    bBusy  => bBusy,
    bError => bErr,
    nErrorID => nErrId,
    sProfinetName => sPnName,
    bNotChangeable => bLocked
);
```

## 7. 业务场景与实际价值

- **场景**：CCAT/TF6270 设备端读自身 PROFINET 名称并判断是否允许被上位改名，供 HMI 显示与改名前校验。
- **价值**：一次拿到名称 + 可改性标志，改名流程更安全。
- **替代方案对比**：盲目改名可能失败；先读 `bNotChangeable` 可避免。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf) 第 3.2.2.2 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/15958916491.html
- **相关 FB / FC**：`FB_PROFINET_SET_NAME`（改名）、`FB_READ_PROFINET_NAME`（EL6631 设备名）
