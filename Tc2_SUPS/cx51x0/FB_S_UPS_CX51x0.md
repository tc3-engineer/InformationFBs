# FB_S_UPS_CX51x0

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SUPS` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `CX51x0` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/2250113931.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_S_UPS_CX51x0.xml`](../examples/P_Demo_FB_S_UPS_CX51x0.xml) |

---

## 1. 功能简述

`FB_S_UPS_CX51x0` 是面向 **CX51x0 系列 Embedded PC（CX5130 / CX5140 等）+ 1-second UPS** 的「断电保护管家」。每个 PLC 周期被调用一次，通过 `iUPSPort`（CX51x0 默认 `16#588`）读取 UPS 状态；一旦检测到掉电，按 `eUpsMode` 自动**用 `SPDM_2PASS` 把 retain 数据写入存储介质** 并**调用内部 `FB_NT_QuickShutdown` 完成安全关机**。

CX51x0 与 CX50x0 的接口几乎完全一致，唯一差别是 `iUPSPort` 默认值不同：**CX50x0 默认 `16#4A8`、CX51x0 默认 `16#588`**——这是因为两代主板上 UPS 子设备的 ADS 端口编号不同。换言之，把同样的业务代码从 CX50x0 移植到 CX51x0，只需要换 FB 类型 + 让 `iUPSPort` 走默认值。

**默认输入值由 Beckhoff 针对 CX51x0 调好，不应改动**；运行在 Windows Embedded 7P 上的同样需要正确配置 EWF/FBWF 写过滤器，详见 §3。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID          : T_AmsNetId:= ''; (* '' = local netid *)
    iPLCPort        : UINT; (* PLC Runtime System for writing persistent data *)
    iUPSPort        : UINT := 16#588; (* Port for reading Power State of UPS *)
    tTimeout        : TIME := DEFAULT_ADS_TIMEOUT; (* ADS Timeout *)
    eUpsMode        : E_S_UPS_Mode := eSUPS_WrPersistData_Shutdown; (* UPS mode (w/wo writing persistent data, w/wo shutdown) *)
    ePersistentMode : E_PersistentMode := SPDM_2PASS; (* mode for writing persistent data *)
    tRecoverTime    : TIME := T#10s; (* ON time to recover from short power failure in mode eSUPS_WrPersistData_NoShutdown/eSUPS_CheckPowerStatus *)
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetId` | `''` | 控制器 AmsNetID。空串表示本机；跨机控制 UPS 在本平台无意义 |
| `iPLCPort` | `UINT` | — | 写 retain 时寻址的 PLC runtime 端口（`851` / `852` / ……）。填 `0` 让 FB 自动探测 |
| `iUPSPort` | `UINT` | `16#588` | 读取 UPS 状态使用的 ADS 端口，CX51x0 默认 `16#588`。**不应改动** |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 写 retain / 触发 quick shutdown 的 ADS 超时 |
| `eUpsMode` | `E_S_UPS_Mode` | `eSUPS_WrPersistData_Shutdown` | UPS 工作模式：是否写 retain、是否关机。默认是「写 retain 后立刻关机」 |
| `ePersistentMode` | `E_PersistentMode` | `SPDM_2PASS` | 写 retain 的模式。**必须 `SPDM_2PASS`**（fast 2-pass），其它模式时间不够 |
| `tRecoverTime` | `TIME` | `T#10s` | 「无关机」模式下电压恢复后多久才回 `eSUPS_PowerOK`。**必须大于电容最大充电时间**，否则连续短时掉电会让电容来不及回满 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bPowerFailDetect  : BOOL; (* TRUE while powerfailure is detected *)
    eState            : E_S_UPS_State := eSUPS_PowerOK; (* current ups state *)
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bPowerFailDetect` | `BOOL` | — | 实时电源标志：掉电中 `TRUE`，恢复后立即 `FALSE`。瞬时位 |
| `eState` | `E_S_UPS_State` | `eSUPS_PowerOK` | FB 当前状态机阶段（见 §4） |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用约定**：必须每个 PLC 周期调用一次。FB 内部按 `iUPSPort` 周期性读 UPS 状态字。

**eUpsMode 决定的四种工作流**（与 CB3011 / CX50x0 版完全一致）：

1. **`eSUPS_WrPersistData_Shutdown`（默认）**：检测掉电 → `eState := eSUPS_WritePersistentData` 用 `SPDM_2PASS` 推 retain 到 CF → `eState := eSUPS_QuickShutdown` 调用 `FB_NT_QuickShutdown` 重启 → `eSUPS_WaitForPowerOFF` 等电容耗尽硬断电。生产现场最常用。
2. **`eSUPS_WrPersistData_NoShutdown`**：只写 retain 不关机，进入 `eSUPS_WaitForRecover` 等电压恢复；`tRecoverTime` 内回来则切 `eSUPS_PowerOK`，否则继续等。适合"短时晃电要存盘但不允许停产"。
3. **`eSUPS_ImmediateShutdown`**：跳过 retain，直接 quick shutdown。用于"全是过程量、断电直接重启"。
4. **`eSUPS_CheckPowerStatus`**：纯监视，只把 `bPowerFailDetect`/`eState` 报给业务，自己决策。

**Windows Embedded Standard 7P 的写过滤器配置**（PDF 明确要求）：

- 用 **EWF**：`TwinCAT\Boot` 必须放在不受 EWF 保护的分区（查注册表 `HKEY_LOCAL_MACHINE\SOFTWARE\Beckhoff\TwinCAT\System\BootPrjPath`）
- 用 **FBWF**：必须在 Beckhoff FBWF Manager → Exclusion Settings 把 `TwinCAT\Boot` 排除

不配 → retain 落在 RAM 覆盖层 → 重启后丢失。FB 不会报这种错。

**关键时序约束**：CX51x0 上 1-second UPS 电容只够数秒；retain 必须 `SPDM_2PASS`；Router Memory 必须配到 retain 总量的 1.5-2 倍；本 FB 内部已经组合好 retain 写入 + QuickShutdown 顺序，**业务不要自己再调 `FB_NT_QuickShutdown`**。

**与 CX50x0 版唯一行为差异**：仅 `iUPSPort` 默认值不同（`16#588` vs `16#4A8`），其它语义完全相同。

## 4. 错误码 / 返回值

本 FB 不暴露 `bError` / `nErrID`。所有运行状态体现在 `eState : E_S_UPS_State`，PDF §5.2 列出的取值：

| 取值 | 含义 |
|---|---|
| `eSUPS_PowerOK` | 所有模式：供电正常 |
| `eSUPS_PowerFailure` | 所有模式：检测到掉电（仅一个周期） |
| `eSUPS_WritePersistentData` | `eSUPS_WrPersistData_Shutdown` / `eSUPS_WrPersistData_NoShutdown` 模式下：正在写 retain |
| `eSUPS_QuickShutdown` | `eSUPS_WrPersistData_Shutdown` / `eSUPS_ImmediateShutdown` 模式下：quick shutdown 执行中 |
| `eSUPS_WaitForRecover` | `eSUPS_WrPersistData_NoShutdown` / `eSUPS_CheckPowerStatus` 模式下：等电压恢复 |
| `eSUPS_WaitForPowerOFF` | `eSUPS_WrPersistData_Shutdown` / `eSUPS_ImmediateShutdown` 模式下：等 UPS 电容耗尽 |

⚠️ PDF 与 InfoSys 均未列具体 ADS 错误号表；retain 写入失败、读 `iUPSPort` 失败等问题不通过 FB 输出报出。可通过 SYSLOG / TwinCAT Event Viewer 间接观察。

## 5. 使用注意 / 常见坑

- **`iUPSPort` 默认 `16#588`，不要套用 CX50x0 的 `16#4A8`**：移植代码时这是最容易踩的坑。错值会导致读 UPS 状态全 0，永远检测不到掉电。
- **EWF/FBWF 必须把 `TwinCAT\Boot` 排除**：CX51x0 出厂 Windows Embedded 7P 通常默认开了写过滤器；不排除目录 → retain 写到 RAM 覆盖层 → 重启全丢。
- **Router Memory 配到 retain 总量的 1.5-2 倍**：配不够 retain 写一半失败，FB 不报错。
- **存储介质必须是 CF**：CX51x0 标配 CF；不要外挂硬盘期望 retain 写过去。
- **默认参数不要改**：尤其 `ePersistentMode` 必须保持 `SPDM_2PASS`。
- **多 runtime 时 `iPLCPort` 显式填**（工程经验补充）：单 runtime 让 FB 自动探测即可；多 runtime 工程建议手动 `851`/`852`/`853` 避免上电探测顺序不稳。
- **每周期都要调**：不要塞 IF / CASE 里。漏几个周期就漏一次电压采样。
- **不要自己调 `FB_NT_QuickShutdown`**（工程经验补充）：PDF 警告会导致数据丢失。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_S_UPS_CX51x0.xml`](../examples/P_Demo_FB_S_UPS_CX51x0.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：某 CX5140 控制器跑装配线主程序，掉电时要保留当前订单号 sOrderIdRetain
//       和「该订单已完成件数」nDoneCountRetain，重启后无需人工补录就能接着干。
//
// 价值：CX51x0 的 UPS 状态在 ADS 端口 16#588。不用本 FB 要自己写 ADS 客户端 +
//       端口读 + SPDM_2PASS 触发 + QuickShutdown 调度。本 FB 全包，业务侧只
//       看 eUpsState 进度。约省 70-90 行手写代码 + 边界测试。
//
// 验证：登录运行 → 在线把 sOrderIdRetain 写成 'ORDER-123'、nDoneCountRetain
//       写成 47 → 模拟掉电（台架拔 24V） → 观察 eUpsState 走过
//       eSUPS_PowerFailure → eSUPS_WritePersistentData → eSUPS_QuickShutdown
//       → 系统重启 → 上电后两个 retain 变量仍是掉电前的值。
PROGRAM P_Demo_FB_S_UPS_CX51x0
VAR
    fbSUPS               : FB_S_UPS_CX51x0;
    sOrderIdRetain       : STRING(40);     // 工程里加 RETAIN
    nDoneCountRetain     : UDINT;
    bPowerFailNow        : BOOL;
    eUpsState            : E_S_UPS_State;
END_VAR
// CX51x0 上 iUPSPort 默认 16#588，与 CX50x0 (16#4A8) 不同
fbSUPS(
    sNetID           := '',
    iPLCPort         := 0,
    iUPSPort         := 16#588,
    tTimeout         := DEFAULT_ADS_TIMEOUT,
    eUpsMode         := eSUPS_WrPersistData_Shutdown,
    ePersistentMode  := SPDM_2PASS,
    tRecoverTime     := T#10s,
    bPowerFailDetect => bPowerFailNow,
    eState           => eUpsState
);
```

## 7. 业务场景与实际价值

- **场景**：CX5130 / CX5140 高端嵌入式控制器在 MES 工作站、半自动装配线、AGV 调度上位机这类需要"掉电不丢任务上下文"的场合。多核 Atom + 工业 CF + 1-second UPS 是 Beckhoff 主推的中高端嵌入控制平台。
- **价值**：用 vs 不用的差别是「重启后从掉电前的订单第 47 件继续」vs「重启后订单号丢失，工人要翻 MES 系统对单或电话联系」。技术层面节省自写 ADS 客户端 + 双段持久化 + QuickShutdown 集成（约 70-90 行），以及"连续掉电 / 写一半电压恢复 / EWF 配置错误"等多个边界场景的回归测试。
- **替代方案对比**：
  - **不用 UPS**：retain 关键字只在「软停 PLC」时被刷盘，硬掉电时一律丢
  - **手写 ADS 客户端 + 自调 QuickShutdown**：能做，但容易在「写过滤器排除路径配置」「`tRecoverTime` 与电容充电时间的关系」上踩坑
  - **本 FB**：Beckhoff 维护，针对 CX51x0 的 UPS 端口 `16#588` 已经写死正确默认
- **与 CX50x0 / CB3011 版的取舍**：换平台时只需换 FB 类型并核对 `iUPSPort` 默认值；业务代码其它部分（`eUpsMode` / 持久化变量声明）原样可用。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf) §4.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/2250113931.html
- **相关枚举**：`E_S_UPS_Mode`（PDF §5.1）、`E_S_UPS_State`（PDF §5.2）
- **相关 FB**：`FB_NT_QuickShutdown`（本 FB 内部使用）、其它平台变体（`FB_S_UPS_CB3011`、`FB_S_UPS` / CX50x0、`FB_S_UPS_CX9020_U900`、`FB_S_UPS_BAPI`）
