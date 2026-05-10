# GetCoreFrequency
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
| Example | [`examples/P_Demo_GetCoreFrequency.xml`](../examples/P_Demo_GetCoreFrequency.xml) |

---
## 1. 功能简述

**方法**：返回所选核（`nCoreId` 指定）的**当前频率**与**配置频率**。两者不同 = 该核被限频。
## 2. 接口定义

### VAR_INPUT

```iecst
METHOD GetCoreFrequency : HRESULT
VAR_INPUT
    nCurrentCoreFrequency : REFERENCE TO UDINT;
    nConfiguredCoreFrequency : REFERENCE TO UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nCurrentCoreFrequency` | `REFERENCE TO UDINT` | 出参：当前频率 |
| `nConfiguredCoreFrequency` | `REFERENCE TO UDINT` | 出参：配置频率（可能高于 current 表示限频中） |

### 返回值

`HRESULT` —— 错误时返回 HRESULT 错误码。

### VAR_IN_OUT

无（输出通过 VAR_INPUT 中的 REFERENCE TO 参数返回）。

## 3. 行为说明

- 见上方功能简述 + VAR 描述。

## 4. 错误码 / 返回值

返回 `HRESULT` HRESULT。出错时返回错误码（具体码值表见 InfoSys / Beckhoff 在线文档）。

## 5. 使用注意 / 常见坑

- 若 nCoreId = -1（默认），返回当前调用所在核的频率。
- 频率单位以 PDF 为准（**未明确**——⚠️ 可能是 MHz）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GetCoreFrequency.xml`](../examples/P_Demo_GetCoreFrequency.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_GetCoreFrequency
VAR
    fbCBM     : TC_CoreBoostMonitor;
    hrResult  : HRESULT;
    out_nCurrentCoreFrequency : UDINT;
    out_nConfiguredCoreFrequency : UDINT;
END_VAR

// 仅在 11+ 代 Intel Core i CPU 上有效
hrResult := fbCBM.GetCoreFrequency(out_nCurrentCoreFrequency, out_nConfiguredCoreFrequency);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目
- 父 FB：[`TC_CoreBoostMonitor`](TC_CoreBoostMonitor.md)

## 8. 待确认项

- 见上方使用注意中标 ⚠️ 的项。
