# TC_CoreBoostMonitor
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_TC_CoreBoostMonitor.xml`](../examples/P_Demo_TC_CoreBoostMonitor.xml) |

---
## 1. 功能简述

**TwinCAT Core Boost 监视器**——用于在启用 Core Boost 时监视 CPU 各核的频率/温度/功率/限频状态。Core Boost 会提高单核时钟，导致更高功耗与温度，需要监视以确保不持续超限。
## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nCoreId : DINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nCoreId` | `DINT` | 要监视的 CPU 核 ID（0..n 0 起；-1 = 当前调用所在核） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError : BOOL;
    hrErrorCode : HRESULT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | 出错时为 TRUE |
| `hrErrorCode` | `HRESULT` | 错误码（HRESULT） |

### VAR_IN_OUT

无。

### 方法（Methods）

| 方法 | 描述 |
|---|---|
| [`GetAllRtCoreThrottling`](GetAllRtCoreThrottling.md) | 见方法文档 |
| [`GetCoreFrequency`](GetCoreFrequency.md) | 见方法文档 |
| [`GetCoreTemperature`](GetCoreTemperature.md) | 见方法文档 |
| [`GetCoreThrottling`](GetCoreThrottling.md) | 见方法文档 |
| [`GetPowerConsumption`](GetPowerConsumption.md) | 见方法文档 |

## 3. 行为说明

- 见上方功能简述 + VAR 描述。

## 4. 错误码 / 返回值

出错时 `bError = TRUE`，错误码在 `nErrorId`/`hrErrorCode`（具体码表见 InfoSys 在线文档，⚠️ 待人工补充）。

## 5. 使用注意 / 常见坑

- **硬件要求**：当前仅支持 Intel® Core™ i CPU **>= 第 11 代**。
- **nCoreId = -1** 时自动取当前 FB 调用所在核。
- 本 FB 提供 5 个方法（见下表），每个方法返回 HRESULT，输出值通过 **REFERENCE TO** 引用参数返回（语法上是 VAR_INPUT 但实际是数据出口）。
- FB 主体 VAR_OUTPUT 的 `bError` / `hrErrorCode` 反映**最近一次**方法调用的结果。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TC_CoreBoostMonitor.xml`](../examples/P_Demo_TC_CoreBoostMonitor.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_TC_CoreBoostMonitor
VAR
    fbCBM           : TC_CoreBoostMonitor(nCoreId := -1);
    hrResult        : HRESULT;
    bThermalAny     : BOOL;
    bPowerAny       : BOOL;
END_VAR

// 调用某个方法（这里以 GetAllRtCoreThrottling 为例）
hrResult := fbCBM.GetAllRtCoreThrottling(bThermalAny, bPowerAny);
// 在线监视 fbCBM.bError / fbCBM.hrErrorCode 与本地 hrResult
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目
- 各方法见上方方法表。

## 8. 待确认项

无。
