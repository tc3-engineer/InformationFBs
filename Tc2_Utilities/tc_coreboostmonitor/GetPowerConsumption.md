# GetPowerConsumption
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
| Example | [`examples/P_Demo_GetPowerConsumption.xml`](../examples/P_Demo_GetPowerConsumption.xml) |

---
## 1. 功能简述

**方法**：返回 platform **package 总功耗**与功率限值（瓦特）。注意：**整个 package 共享**这个值，所以同 package 内的所有实时核返回值相同。
## 2. 接口定义

### VAR_INPUT

```iecst
METHOD GetPowerConsumption : HRESULT
VAR_INPUT
    nCurrentPackagePowerConsumption : REFERENCE TO UDINT;
    nPackagePowerLimit : REFERENCE TO UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nCurrentPackagePowerConsumption` | `REFERENCE TO UDINT` | 出参：platform package 当前功耗（瓦特） |
| `nPackagePowerLimit` | `REFERENCE TO UDINT` | 出参：package 功率限值（瓦特，超过会限频） |

### 返回值

`HRESULT` —— 错误时返回 HRESULT 错误码。

### VAR_IN_OUT

无（输出通过 VAR_INPUT 中的 REFERENCE TO 参数返回）。

## 3. 行为说明

- 见上方功能简述 + VAR 描述。

## 4. 错误码 / 返回值

返回 `HRESULT` HRESULT。出错时返回错误码（具体码值表见 InfoSys / Beckhoff 在线文档）。

## 5. 使用注意 / 常见坑

- 同 package 共享读数——该 package 内任一核调用本方法都得到相同值。
- package 概念：通常一颗 CPU 物理芯片是一个 package（含多核）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GetPowerConsumption.xml`](../examples/P_Demo_GetPowerConsumption.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_GetPowerConsumption
VAR
    fbCBM     : TC_CoreBoostMonitor;
    hrResult  : HRESULT;
    out_nCurrentPackagePowerConsumption : UDINT;
    out_nPackagePowerLimit : UDINT;
END_VAR

// 仅在 11+ 代 Intel Core i CPU 上有效
hrResult := fbCBM.GetPowerConsumption(out_nCurrentPackagePowerConsumption, out_nPackagePowerLimit);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目
- 父 FB：[`TC_CoreBoostMonitor`](TC_CoreBoostMonitor.md)

## 8. 待确认项

无。
