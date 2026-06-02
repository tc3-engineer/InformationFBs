# FB_GetDeviceIdentification

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `[obsolete]` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34993291.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified · deprecated` |
| Example | [`examples/P_Demo_FB_GetDeviceIdentification.TcPOU`](../examples/P_Demo_FB_GetDeviceIdentification.TcPOU) |

---

## 1. 功能简述

⚠️ **本 FB 已弃用**。PDF 与 InfoSys 都明确写 "Obsolete functionality — for longer hardware model and hardware serial number strings the block `FB_GetDeviceIdentificationEx` has to be used"。**新代码请用 `FB_GetDeviceIdentificationEx`**。

`FB_GetDeviceIdentification` 通过 ADS 读取目标控制器的"设备身份信息"——硬件型号、序列号、TwinCAT 版本、Image 版本等基本信息。它的 `stDevIdent` 输出是 `ST_DeviceIdentification` 类型，**字段长度有限**（PDF 未明说具体长度，但 InfoSys 强调"longer string"——意味着新硬件型号 / 序列号字符串可能超出旧结构体能容纳的范围）。

被弃用的原因：随着 Beckhoff 硬件型号命名变长（如长序列号、扩展型号字符串），旧的 `ST_DeviceIdentification` 字段长度不够用。`FB_GetDeviceIdentificationEx` 用更长的字段替代，是同功能的现代版本。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute  : BOOL;
    tTimeout  : TIME := DEFAULT_ADS_TIMEOUT;
    sNetId    : T_AmsNetId;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bExecute` | `BOOL` | — | 上升沿触发一次 ADS 查询。调用期间保持高电平，完成后建议主动复位为下一次触发做准备 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 等待回执的超时阈值。通常 `DEFAULT_ADS_TIMEOUT` ≈ 5 s 够用 |
| `sNetId` | `T_AmsNetId` | — | 目标控制器 AmsNetId。空字符串表示本机；非空时跨网络查询远程控制器 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy      : BOOL;
    bError     : BOOL;
    nErrorId   : UDINT;
    stDevIdent : ST_DeviceIdentification;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 一次查询执行中为 `TRUE`，回执到达后翻 `FALSE` |
| `bError` | `BOOL` | `bBusy` 翻 `FALSE` 后若发生错误则为 `TRUE` |
| `nErrorId` | `UDINT` | ADS 错误号（参见 Tc2_Utilities ADS 错误号表） |
| `stDevIdent` | `ST_DeviceIdentification` | 设备身份结构体：型号、序列号、TwinCAT 版本、Image 信息等。字段长度有限——长字符串场景请改用 `FB_GetDeviceIdentificationEx` |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿。`bBusy` 立刻置 `TRUE`，FB 向 `sNetId` 指定的控制器发起 ADS 查询；回执到达后填入 `stDevIdent`，`bBusy` 翻 `FALSE`，`bError` / `nErrorId` 反映是否成功。

**典型 ADS 调用模式**（与所有 `bExecute` / `bBusy` / `bDone` 风格 FB 一致）：
1. 业务侧把 `bExecute` 拉高
2. FB `bBusy := TRUE`，发起 ADS 调用
3. 业务侧等待 `bBusy` 翻 `FALSE`
4. 检查 `bError`：`FALSE` 表示 `stDevIdent` 有效；`TRUE` 时 `nErrorId` 给故障码
5. 业务侧把 `bExecute` 拉低，FB 准备下一次触发

**单次触发，不周期查询**：与 `FB_AdsReadEvents` 的周期模式不同，本 FB 只在 `bExecute` 上升沿触发一次。设备身份信息变化频率极低（开机后基本不变），周期查询无意义。

**远程 vs 本机**：`sNetId := ''` 查询本机；`sNetId := '192.168.1.10.1.1'` 这种远程地址查询其他控制器。常用于"中央 HMI 巡检多台 PLC 健康状态"或"维护工具识别现场设备清单"。

**字段长度限制问题**（被弃用核心）：`ST_DeviceIdentification` 内部的型号 / 序列号字段定长，新硬件如果型号或序列号字符串过长，本 FB 返回的会被截断或干脆报错。`FB_GetDeviceIdentificationEx` 用更长的字段（具体长度见其文档）解决这个问题。

## 4. 错误码 / 返回值

`bError` / `nErrorId` 输出对：

| `bError` | 含义 |
|---|---|
| `FALSE` | 调用成功，`stDevIdent` 有效 |
| `TRUE` | 调用失败，`nErrorId` 给具体码 |

⚠️ PDF 标注 "Returns the ADS error number"，但未在本节列具体码。常见可能：
- `0x745` (1861)：ADS timeout（远程控制器未响应 / 网络不通）
- `0x6` / `0x7`：ADS 端口 / NETID 错（目标无 TwinCAT 服务）
- 字符串过长导致的内部缓冲错（PDF 未列具体码 ⚠️）

## 5. 使用注意 / 常见坑

- **本 FB 已弃用**：新代码请用 `FB_GetDeviceIdentificationEx`。本文档保留为 TC2 旧工程兼容文档。
- **`bExecute` 是边沿触发，不是电平**：写 `bExecute := TRUE; ...; bExecute := TRUE;` 不会触发第二次——必须让它先回 `FALSE` 再 `TRUE`。
- **结果只在 `bBusy = FALSE` 后有效**：在 `bBusy = TRUE` 期间读 `stDevIdent` 拿到的是上一次或未初始化内容。
- **`bExecute` 不要常驻 `TRUE`**：会让 FB 在每次回执后立即又触发，对目标控制器造成不必要的 ADS 负担。完成后及时复位。
- **跨网络查询 `tTimeout` 调大**：默认 5 s 对稳定 LAN 够用，对 VPN / 蜂窝链路可能不够，看见超时码先试加大。
- **若发现 `stDevIdent.sHardwareModel` 像被截断**：很可能就是被弃用的核心问题——立刻换 `FB_GetDeviceIdentificationEx`。
- **`sNetId` 必须是字符串形式**（如 `'192.168.1.10.1.1'`），不要传 `T_AmsNetId` 字节数组。
- **DEFAULT_ADS_TIMEOUT 常量**位于 `Tc2_System`——使用本 FB 必须把 `Tc2_System` 也引入工程，否则编译失败。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetDeviceIdentification.TcPOU`](../examples/P_Demo_FB_GetDeviceIdentification.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：维护一个 TC2 时代的旧 HMI 工程：开机时读本机控制器的硬件型号与序列号，
//       显示在 HMI "关于"页面上，方便操作员在现场识别设备型号 / 报修时报序列
//       号。本 FB 是这套旧 HMI 用的标准接口。
//
// 价值：在不大改工程的前提下让旧 HMI 继续工作。若发现型号字符串被截断（如新
//       Beckhoff 控制器型号过长），改用 FB_GetDeviceIdentificationEx 即可。
//
// 验证：登录后置 bReadDeviceInfo := TRUE 触发一次查询；观察 bIdentBusy 在 1-2
//       个周期内翻 TRUE 然后回 FALSE；bIdentError 应为 FALSE；展开 stDeviceIdent
//       结构体可看到型号 / 序列号等字段被填入。
PROGRAM P_Demo_FB_GetDeviceIdentification
VAR
    fbGetDeviceIdent       : FB_GetDeviceIdentification;
    sLocalNetId            : T_AmsNetId := '';
    tAdsTimeout            : TIME := DEFAULT_ADS_TIMEOUT;
    bReadDeviceInfo        : BOOL := FALSE;
    bIdentBusy             : BOOL;
    bIdentError            : BOOL;
    nIdentErrorId          : UDINT;
    stDeviceIdent          : ST_DeviceIdentification;
END_VAR

fbGetDeviceIdent(
    bExecute   := bReadDeviceInfo,
    tTimeout   := tAdsTimeout,
    sNetId     := sLocalNetId,
    bBusy      => bIdentBusy,
    bError     => bIdentError,
    nErrorId   => nIdentErrorId,
    stDevIdent => stDeviceIdent
);

// 触发后建议立刻复位 bReadDeviceInfo，避免连续触发
IF NOT bIdentBusy AND bReadDeviceInfo THEN
    bReadDeviceInfo := FALSE;
END_IF
```

## 7. 业务场景与实际价值

- **场景**：旧 HMI"关于"页面 / 维修工单显示设备身份。开机一次性读取即可，运行时不变。
- **价值**：保留旧工程的设备识别功能；让维修工单 / 现场识别照旧工作。
- **替代方案对比**：
  - **新工程 / 新硬件**：必须用 `FB_GetDeviceIdentificationEx`——支持更长字符串，无截断风险
  - **TC2 旧硬件 + 短型号串**：本 FB 仍可用，但建议在新版本计划里逐步迁移
  - 用 `F_GetVersionTcSystem`：只能拿 TwinCAT 版本号，不能拿型号 / 序列号；功能子集

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34993291.html
- **替代 FB**：`FB_GetDeviceIdentificationEx`（Tc2_Utilities，支持长字符串）
- **相关类型**：`ST_DeviceIdentification`、`T_AmsNetId`、`DEFAULT_ADS_TIMEOUT`（Tc2_System）
