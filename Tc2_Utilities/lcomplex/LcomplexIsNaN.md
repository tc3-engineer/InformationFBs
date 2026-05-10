# LcomplexIsNaN
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
| Example | [`examples/P_Demo_LcomplexIsNaN.xml`](../examples/P_Demo_LcomplexIsNaN.xml) |

---
## 1. 功能简述

若复数 `Z`（LCOMPLEX 类型）含 NaN（未定义）值则返回 TRUE。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LcomplexIsNaN : BOOL
VAR_INPUT
    Z : REFERENCE TO LCOMPLEX;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Z` | `REFERENCE TO LCOMPLEX` | 复数实例（按引用传入） |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- 调用 `LcomplexIsNaN(lcZ)`，返回 `BOOL` 类型结果。
- 期望：`FALSE（正常值）`

## 4. 错误码 / 返回值

返回 `BOOL`。无错误码。

## 5. 使用注意 / 常见坑

- **按引用传入**：`Z : REFERENCE TO LCOMPLEX`——调用时传变量本身，FB 内部不复制。
- `LCOMPLEX` 是 Tc2_Utilities 自带的复数结构体（实部 + 虚部，均为 LREAL）。
- 见同库 `LcomplexAbs` 取模长。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LcomplexIsNaN.xml`](../examples/P_Demo_LcomplexIsNaN.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_LcomplexIsNaN
VAR
    bResult : BOOL;
    bRun    : BOOL;
    lcZ : LCOMPLEX;
END_VAR

// 不赋 NaN 时 IsNaN = FALSE；可手动写 lcZ.r := 0.0/0.0; 测 TRUE
IF bRun THEN
    bResult := LcomplexIsNaN(lcZ);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
