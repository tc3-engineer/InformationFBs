# GetCoreTemperature
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
| Example | [`examples/P_Demo_GetCoreTemperature.xml`](../examples/P_Demo_GetCoreTemperature.xml) |

---
## 1. 功能简述

**方法**：返回所选核的**当前温度**、**历史最高温度**（自 XAR 启动）、**温度限值**。单位 °C。
## 2. 接口定义

### VAR_INPUT

```iecst
METHOD GetCoreTemperature : HRESULT
VAR_INPUT
    nCurrentTemp : REFERENCE TO UDINT;
    nMaxTemp : REFERENCE TO UDINT;
    nTempLimit : REFERENCE TO UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nCurrentTemp` | `REFERENCE TO UDINT` | 出参：当前温度 [°C] |
| `nMaxTemp` | `REFERENCE TO UDINT` | 出参：自 TwinCAT XAR 启动以来观察到的最高温度 [°C] |
| `nTempLimit` | `REFERENCE TO UDINT` | 出参：CPU 核温度限值 [°C]（超此值会限频） |

### 返回值

`HRESULT` —— 错误时返回 HRESULT 错误码。

### VAR_IN_OUT

无（输出通过 VAR_INPUT 中的 REFERENCE TO 参数返回）。

## 3. 行为说明

- 见上方功能简述 + VAR 描述。

## 4. 错误码 / 返回值

返回 `HRESULT` HRESULT。出错时返回错误码（具体码值表见 InfoSys / Beckhoff 在线文档）。

## 5. 使用注意 / 常见坑

- `nMaxTemp` 是 XAR 启动后最大值，重启 TwinCAT 即清零。
- 实际超过 `nTempLimit` 即触发限频（→ `GetCoreThrottling` 检测）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GetCoreTemperature.xml`](../examples/P_Demo_GetCoreTemperature.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_GetCoreTemperature
VAR
    fbCBM     : TC_CoreBoostMonitor;
    hrResult  : HRESULT;
    out_nCurrentTemp : UDINT;
    out_nMaxTemp : UDINT;
    out_nTempLimit : UDINT;
END_VAR

// 仅在 11+ 代 Intel Core i CPU 上有效
hrResult := fbCBM.GetCoreTemperature(out_nCurrentTemp, out_nMaxTemp, out_nTempLimit);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目
- 父 FB：[`TC_CoreBoostMonitor`](TC_CoreBoostMonitor.md)

## 8. 待确认项

无。
