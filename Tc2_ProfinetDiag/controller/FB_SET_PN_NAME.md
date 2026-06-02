# FB_SET_PN_NAME

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ProfinetDiag` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `controller` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/15018588555.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SET_PN_NAME.TcPOU`](../examples/P_Demo_FB_SET_PN_NAME.TcPOU) |

---

## 1. 功能简述

给指定 PROFINET 设备分配 PROFINET 名称（device name）。分配时必须只使用 PROFINET 合规字符。通过 `MAC_ID`（设备 MAC 地址）定位目标设备、`PROFINET_NAME` 给出待写名称，控制器经 ADS 把名称写入。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  bExecute        : BOOL;
  NETID           : T_AmsNetId;
  PROFINET_NAME   : STRING(51);
  MAC_ID          : ARRAY [0..5] OF BYTE;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bExecute` | `BOOL` | 上升沿（FALSE→TRUE）触发功能块执行一次。 |
| `NETID` | `T_AmsNetId` | 控制器（PROFINET Controller）的 AMS Net ID。本机控制器填空串 `''`。 |
| `PROFINET_NAME` | `STRING(51)` | 要分配给 PROFINET 设备的名称。最多 240 字符，仅允许字符 `a..z`、`0..9`、`.`、`-`。 |
| `MAC_ID` | `ARRAY [0..5] OF BYTE` | 目标设备的 MAC ID（6 字节）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  iErrorID                : UDINT;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 功能块使能后该输出置位，并一直保持到收到设备反馈为止。`bBusy = TRUE` 期间不接受输入端的新命令（不响应新的触发）。 |
| `bError` | `BOOL` | 命令传输过程中发生错误时，在 `bBusy` 复位（落沿）之后置位该输出。 |
| `iErrorID` | `UDINT` | `bError` 置位时返回 ADS 错误号（见 §4 错误码表）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

本功能块是基于 ADS 的异步功能块，内部维护「空闲 → 忙 → 完成」三态状态机。`bExecute` 由 FALSE 变为 TRUE 的上升沿触发一次操作：触发后 `bBusy` 立即置 TRUE，功能块通过 ADS 把请求发往 PROFINET 控制器（由 `NETID` 与 `PORT` 寻址到目标设备）；收到设备应答后 `bBusy` 落回 FALSE，此时 （无数据输出，仅写入反馈） 才有效，若过程出错则 `bError` 在 `bBusy` 落沿之后置 TRUE、`iErrorID` 给出 ADS 错误号。`bBusy = TRUE` 期间功能块忽略输入端的任何新触发，必须等到本次完成才能再次发起。

**调用周期**：必须在每个 PLC 周期持续调用本实例（不是只在触发那一帧调一次），否则内部 ADS 状态机无法推进、`bBusy` 不会落沿。**清错语义**：错误状态保持到下一次 `bExecute` 上升沿被接受时才更新，因此读 `bError`/`iErrorID` 要在 `bBusy` 落沿之后、下一次触发之前读。**电平 vs 边沿**：`bExecute` 保持高电平不会反复执行，只在跳变沿触发一次；要重复操作必须先把 `bExecute` 拉回 FALSE 再拉高。

**命名规则**：PROFINET 名称只能含小写字母 `a..z`、数字 `0..9`、点 `.` 和连字符 `-`，不能含大写、空格、下划线等；违规字符会被设备拒绝。**靠 MAC 定位**：本 FB 通过 `MAC_ID` 而非 IP 寻址设备，因此可在设备尚未配 IP / 名称的「裸」状态下完成首次命名。

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

- **只用合规字符**：`a..z 0..9 . -`，否则写入失败。
- **靠 MAC 寻址**：把 6 字节 MAC 填入 `MAC_ID` 数组（设备铭牌或扫描结果 `str_PN_Scan.MacID` 可得）。
- **`PROFINET_NAME` 类型为 `STRING(51)`** 但描述允许最多 240 字符——以代码块声明的 `STRING(51)` 为实际上限。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SET_PN_NAME.TcPOU`](../examples/P_Demo_FB_SET_PN_NAME.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_SET_PN_NAME
VAR
    fbSetName     : FB_SET_PN_NAME;
    bSetNameReq   : BOOL := FALSE;            // 在线上升沿触发命名
    sNewName      : STRING(51) := 'line3-io-04';      // 合规名称：小写/数字/.-
    aTargetMac    : ARRAY [0..5] OF BYTE := [16#00,16#01,16#05,16#0A,16#1B,16#2C];  // 目标设备 MAC
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
END_VAR

// 上升沿触发；按 MAC 给设备写入 PROFINET 名称
fbSetName(
    bExecute := bSetNameReq,
    NETID    := '',
    PROFINET_NAME := sNewName,
    MAC_ID   := aTargetMac,
    bBusy    => bBusy,
    bError   => bErr,
    iErrorID => nErrId
);
```

## 7. 业务场景与实际价值

- **场景**：新设备上线或更换备件时，PROFINET 设备出厂无名或名称不符，需要按工位规范分配名称（如 `line3-io-04`）。
- **价值**：PLC 程序在投运流程里按 MAC 自动给设备命名，免去逐台用 TwinCAT/PRONETA 手工设名。
- **替代方案对比**：手工命名易出错、难批量；本 FB 可脚本化批量命名，配合 `FB_PN_SCAN` 扫到 MAC 后自动设名。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf) 第 3.1.4 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/15018588555.html
- **相关 FB / FC**：`FB_PN_SCAN`（扫描得到设备 MAC）、`FB_RESET_PN_TO_FACTORY_SETTINGS`（按 MAC 复位）、`FB_PROFINET_SET_NAME`（设备侧改名）
