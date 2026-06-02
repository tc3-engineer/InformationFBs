# FB_PN_SCAN

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ProfinetDiag` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `controller` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/15015749387.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PN_SCAN.TcPOU`](../examples/P_Demo_FB_PN_SCAN.TcPOU) |

---

## 1. 功能简述

扫描 PROFINET 网络并返回找到的设备数量及其信息列表。输出 `iFind_Devices` 给出找到的设备数，`ar_PN_DEVICE`（`ARRAY [1..100] OF str_PN_SCAN`）逐台给出每个设备的 IP/掩码/网关/MAC/厂商 ID/设备 ID/PROFINET 名称。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  bExecute        : BOOL;
  NETID           : T_AmsNetId;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bExecute` | `BOOL` | 上升沿（FALSE→TRUE）触发功能块执行一次。 |
| `NETID` | `T_AmsNetId` | 控制器（PROFINET Controller）的 AMS Net ID。本机控制器填空串 `''`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  iFind_Devices     : INT;
  ar_PN_DEVICE      : ARRAY [1..100] OF str_PN_SCAN;
  bBusy             : BOOL;
  bError            : BOOL;
  iErrorID          : UDINT;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `iFind_Devices` | `INT` | 扫描到的 PROFINET 设备数。 |
| `ar_PN_DEVICE` | `ARRAY [1..100] OF str_PN_SCAN` | 各 PROFINET 设备的 PROFINET/IP 设置（逐台一项）。 |
| `bBusy` | `BOOL` | 功能块使能后该输出置位，并一直保持到收到设备反馈为止。`bBusy = TRUE` 期间不接受输入端的新命令（不响应新的触发）。 |
| `bError` | `BOOL` | 命令传输过程中发生错误时，在 `bBusy` 复位（落沿）之后置位该输出。 |
| `iErrorID` | `UDINT` | `bError` 置位时返回 ADS 错误号（见 §4 错误码表）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

本功能块是基于 ADS 的异步功能块，内部维护「空闲 → 忙 → 完成」三态状态机。`bExecute` 由 FALSE 变为 TRUE 的上升沿触发一次操作：触发后 `bBusy` 立即置 TRUE，功能块通过 ADS 把请求发往 PROFINET 控制器（由 `NETID` 与 `PORT` 寻址到目标设备）；收到设备应答后 `bBusy` 落回 FALSE，此时 `iFind_Devices` 与 `ar_PN_DEVICE` 数组 才有效，若过程出错则 `bError` 在 `bBusy` 落沿之后置 TRUE、`iErrorID` 给出 ADS 错误号。`bBusy = TRUE` 期间功能块忽略输入端的任何新触发，必须等到本次完成才能再次发起。

**调用周期**：必须在每个 PLC 周期持续调用本实例（不是只在触发那一帧调一次），否则内部 ADS 状态机无法推进、`bBusy` 不会落沿。**清错语义**：错误状态保持到下一次 `bExecute` 上升沿被接受时才更新，因此读 `bError`/`iErrorID` 要在 `bBusy` 落沿之后、下一次触发之前读。**电平 vs 边沿**：`bExecute` 保持高电平不会反复执行，只在跳变沿触发一次；要重复操作必须先把 `bExecute` 拉回 FALSE 再拉高。

**数组容量 100**：`ar_PN_DEVICE` 固定 100 项，只有前 `iFind_Devices` 项有效。若网络设备可能超过 100 台，请改用 `FB_PN_SCAN_UpTo255`（容量 255）。**扫描得到的 MAC** 可直接喂给 `FB_SET_PN_NAME` / `FB_RESET_PN_TO_FACTORY_SETTINGS` 做命名/复位。

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

- **遍历以 `iFind_Devices` 为界**：数组 100 项固定，超出部分无效。
- **容量上限 100**：设备多于 100 台用 `FB_PN_SCAN_UpTo255`。
- **扫描 ≠ 组态**：扫到的是网络上物理在线的设备（含未组态的），用于发现/命名，不等于 TwinCAT 已组态列表。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PN_SCAN.TcPOU`](../examples/P_Demo_FB_PN_SCAN.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_PN_SCAN
VAR
    fbScan        : FB_PN_SCAN;
    bScanReq      : BOOL := FALSE;            // 在线上升沿触发扫描
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
    iFound        : INT;                      // 扫描到的设备数
    aDevices      : ARRAY [1..100] OF str_PN_SCAN;   // 逐台设备信息
END_VAR

// 上升沿触发；扫描全网（最多 100 台）
fbScan(
    bExecute := bScanReq,
    NETID    := '',
    iFind_Devices => iFound,
    ar_PN_DEVICE => aDevices,
    bBusy    => bBusy,
    bError   => bErr,
    iErrorID => nErrId
);

// 遍历 1..iFound 取 aDevices[i].MacID / PN_NAME，可喂给 FB_SET_PN_NAME
```

## 7. 业务场景与实际价值

- **场景**：调试或运维时「现场到底挂了哪些 PROFINET 设备」，扫描全网拿到每台的 MAC/IP/名称，做设备发现。
- **价值**：一次扫描拿到全网在线设备清单（含未命名的裸设备），是「扫描→命名→组态」自动化投运的第一步。
- **替代方案对比**：PRONETA 等工具能扫但脱离 PLC 逻辑；本 FB 让扫描结果直接进 PLC，可联动自动命名。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf) 第 3.1.6 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/15015749387.html
- **相关 FB / FC**：`FB_PN_SCAN_UpTo255`（容量 255 版）、`str_PN_Scan`（数据结构）、`FB_SET_PN_NAME`（用扫描 MAC 命名）
