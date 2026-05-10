# LrealIsNaN
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `FLOAT functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_LrealIsNaN.xml`](../examples/P_Demo_LrealIsNaN.xml) |

---
## 1. 功能简述

测试 LREAL 是否为 NaN（Not a Number）。返回 TRUE 表示是 NaN。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LrealIsNaN : BOOL
VAR_INPUT
    x : REFERENCE TO LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `x` | `REFERENCE TO LREAL` | 待测值（按引用） |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- 调用 `LrealIsNaN(rX)`，返回 `BOOL` 类型结果。
- 期望：`FALSE（rX=3.14）`

## 4. 错误码 / 返回值

返回 `BOOL`。无错误码。

## 5. 使用注意 / 常见坑

- NaN 的关键特性（PDF 总结）：所有算术运算 NaN→NaN；所有关系运算（=/!=/>/</>=/<=）任意一端为 NaN 都返回 FALSE；`isnan(a) ≡ NOT(a = a)`。
- ⚠️ **CAUTION**：NaN 可能导致危险的软件故障——只在明确允许（如运动控制）时使用。
- ⚠️ **NOTICE**：NaN 比较可能引发 FP exception 致使 runtime 停止 → 处理 NaN 前先关 FP exception。
- 对应早期废弃名 `FLOATIsNaN`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LrealIsNaN.xml`](../examples/P_Demo_LrealIsNaN.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_LrealIsNaN
VAR
    bResult : BOOL;
    bRun    : BOOL;
    rX : LREAL;
END_VAR

rX := 3.14;
IF bRun THEN
    bResult := LrealIsNaN(rX);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 见上方使用注意中标 ⚠️ 的项。
