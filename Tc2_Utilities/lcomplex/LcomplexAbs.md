# LcomplexAbs
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `LCOMPLEX functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_LcomplexAbs.xml`](../examples/P_Demo_LcomplexAbs.xml) |

---
## 1. 功能简述

返回复数 `Z` 的绝对值（模长，sqrt(re² + im²)）。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LcomplexAbs : LREAL
VAR_INPUT
    Z : LCOMPLEX;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Z` | `LCOMPLEX` | 输入复数 |

### 返回值

`LREAL` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- 调用 `LcomplexAbs(lcZ)`，返回 `LREAL` 类型结果。
- 期望：`5.0（当 lcZ=(3,4)）`

## 4. 错误码 / 返回值

返回 `LREAL`。无错误码。

## 5. 使用注意 / 常见坑

- **值传递**（不是 REFERENCE TO）。
- 返回 LREAL（双精度浮点）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LcomplexAbs.xml`](../examples/P_Demo_LcomplexAbs.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_LcomplexAbs
VAR
    bResult : LREAL;
    bRun    : BOOL;
    lcZ : LCOMPLEX;
END_VAR

lcZ.r := 3.0; lcZ.i := 4.0;
IF bRun THEN
    bResult := LcomplexAbs(lcZ);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
