# GetAllRtCoreThrottling
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `METHOD` |
| Category | `TC_CoreBoostMonitor` |
| Parent FB | [`TC_CoreBoostMonitor`](TC_CoreBoostMonitor.md) |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_GetAllRtCoreThrottling.xml`](../examples/P_Demo_GetAllRtCoreThrottling.xml) |

---
## 1. 功能简述

**方法（METHOD on TC_CoreBoostMonitor）**：检查**所有实时核**是否有任何核因温度/功率超限正在限频。返回 HRESULT；具体限频原因通过两个 REFERENCE TO BOOL 出参返回。
## 2. 接口定义

### VAR_INPUT

```iecst
METHOD GetAllRtCoreThrottling : HRESULT
VAR_INPUT
    bRtInThermalThrottling : REFERENCE TO BOOL;
    bRtInPowerThrottling : REFERENCE TO BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bRtInThermalThrottling` | `REFERENCE TO BOOL` | 出参：任一实时核因温度超限而限频时为 TRUE |
| `bRtInPowerThrottling` | `REFERENCE TO BOOL` | 出参：任一实时核因功率超限而限频时为 TRUE |

### 返回值

`HRESULT` —— 错误时返回 HRESULT 错误码。

### VAR_IN_OUT

无（输出通过 VAR_INPUT 中的 REFERENCE TO 参数返回）。

## 3. 行为说明

- 见上方功能简述 + VAR 描述。

## 4. 错误码 / 返回值

返回 `HRESULT` HRESULT。出错时返回错误码（具体码值表见 InfoSys / Beckhoff 在线文档）。

## 5. 使用注意 / 常见坑

- **这是方法**，不能独立实例化——必须通过 `TC_CoreBoostMonitor` 实例调用：`fbCBM.GetAllRtCoreThrottling(bThermal, bPower);`。
- REFERENCE TO 参数：调用时传变量本身，FB 写入。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GetAllRtCoreThrottling.xml`](../examples/P_Demo_GetAllRtCoreThrottling.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_GetAllRtCoreThrottling
VAR
    fbCBM     : TC_CoreBoostMonitor;
    hrResult  : HRESULT;
    out_bRtInThermalThrottling : BOOL;
    out_bRtInPowerThrottling : BOOL;
END_VAR

// 仅在 11+ 代 Intel Core i CPU 上有效
hrResult := fbCBM.GetAllRtCoreThrottling(out_bRtInThermalThrottling, out_bRtInPowerThrottling);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目
- 父 FB：[`TC_CoreBoostMonitor`](TC_CoreBoostMonitor.md)

## 8. 待确认项

无。
