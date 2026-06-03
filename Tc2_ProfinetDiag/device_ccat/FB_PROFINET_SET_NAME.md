# FB_PROFINET_SET_NAME

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ProfinetDiag` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `device_ccat` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/15959467915.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PROFINET_SET_NAME.TcPOU`](../examples/P_Demo_FB_PROFINET_SET_NAME.TcPOU) |

---

## 1. 功能简述

更改指定 PROFINET 设备的 PROFINET 名称（用于 CCAT/TF6270 设备）。要求 PROFINET 驱动版本 06（V00.34）及以上、TF6270、CCAT PN Interface(B930)。`sProfinetName` 给出新名，`bNotChangeable` 可设置名称是否禁止再被控制器更改。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  bStart           : BOOL;
  NETID            : T_AmsNetId;
  PORT             : T_AmsPort;
  sProfinetName    : STRING(240);
  bNotChangeable   : BOOL;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bStart` | `BOOL` | 上升沿（FALSE→TRUE）触发功能块执行一次。 |
| `NETID` | `T_AmsNetId` | PROFINET 设备的 AMS Net ID。 |
| `PORT` | `T_AmsPort` | PROFINET 设备的 ADS 端口号；默认 `0xFFFF`。 |
| `sProfinetName` | `STRING(240)` | PROFINET 设备名。最多 240 字符，仅允许 `a..z`、`0..9`、`.`、`-`。 |
| `bNotChangeable` | `BOOL` | 为 `TRUE` 时表示 PROFINET 控制器今后不能再更改该 PROFINET 名称。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  nErrorID                : UDINT;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 功能块使能后该输出置位，并一直保持到收到设备反馈为止。`bBusy = TRUE` 期间不接受输入端的新命令（不响应新的触发）。 |
| `bError` | `BOOL` | 命令传输过程中发生错误时，在 `bBusy` 复位（落沿）之后置位该输出。 |
| `nErrorID` | `UDINT` | `bError` 置位时返回 ADS 错误号（见 §4）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

本功能块是基于 ADS 的异步功能块，内部维护「空闲 → 忙 → 完成」三态状态机。`bStart` 由 FALSE 变为 TRUE 的上升沿触发一次操作：触发后 `bBusy` 立即置 TRUE，功能块通过 ADS 把请求发往 PROFINET 控制器（由 `NETID` 与 `PORT` 寻址到目标设备）；收到设备应答后 `bBusy` 落回 FALSE，此时 （无数据输出，仅改名反馈） 才有效，若过程出错则 `bError` 在 `bBusy` 落沿之后置 TRUE、`nErrorID` 给出 ADS 错误号。`bBusy = TRUE` 期间功能块忽略输入端的任何新触发，必须等到本次完成才能再次发起。

**调用周期**：必须在每个 PLC 周期持续调用本实例（不是只在触发那一帧调一次），否则内部 ADS 状态机无法推进、`bBusy` 不会落沿。**清错语义**：错误状态保持到下一次 `bStart` 上升沿被接受时才更新，因此读 `bError`/`nErrorID` 要在 `bBusy` 落沿之后、下一次触发之前读。**电平 vs 边沿**：`bStart` 保持高电平不会反复执行，只在跳变沿触发一次；要重复操作必须先把 `bStart` 拉回 FALSE 再拉高。

**命名规则同 `FB_SET_PN_NAME`**：只允许 `a..z 0..9 . -`。**`bNotChangeable` 是写锁**：写 TRUE 后该名称被锁定，控制器无法再改（可先用 `FB_PROFINET_READ_NAME` 读该位确认状态）。**版本/硬件门槛**：需 PROFINET 驱动 06（V00.34）+、TF6270、CCAT PN Interface(B930)。

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

- **版本/硬件要求**：驱动 06（V00.34）以上 + TF6270 + CCAT B930；库版本 >= v1.5.1.0。
- **`bNotChangeable` 慎用**：置 TRUE 会锁死名称，后续无法用控制器改名。
- **`PORT` 默认 `0xFFFF`**（设备组语义）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PROFINET_SET_NAME.TcPOU`](../examples/P_Demo_FB_PROFINET_SET_NAME.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_PROFINET_SET_NAME
VAR
    fbSetName     : FB_PROFINET_SET_NAME;
    bSetReq       : BOOL := FALSE;            // 在线上升沿触发改名
    sNewName      : STRING(240) := 'b930-dev-01';     // 合规新名
    bLockName     : BOOL := FALSE;            // 是否锁定名称（慎用）
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
END_VAR

// 上升沿触发；设备端自改 PROFINET 名（需驱动 06/V00.34+、TF6270、CCAT B930）
fbSetName(
    bStart := bSetReq,
    NETID  := '',
    PORT   := 16#FFFF,
    sProfinetName := sNewName,
    bNotChangeable := bLockName,
    bBusy  => bBusy,
    bError => bErr,
    nErrorID => nErrId
);
```

## 7. 业务场景与实际价值

- **场景**：CCAT/TF6270 设备端在投运时给自身写入规范的 PROFINET 名称，并可选地锁定防止误改。
- **价值**：设备端自助改名，免去依赖上位控制器命名；可锁名防误操作。
- **替代方案对比**：控制器侧 `FB_SET_PN_NAME` 靠 MAC 改名；本 FB 是设备端自改名（CCAT/TF6270 专用）。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf) 第 3.2.2.5 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/15959467915.html
- **相关 FB / FC**：`FB_PROFINET_READ_NAME`（读名+可改性）、`FB_SET_PN_NAME`（控制器侧按 MAC 命名）
