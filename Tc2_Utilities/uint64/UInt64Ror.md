# UInt64Ror
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt64Ror.xml`](../examples/P_Demo_UInt64Ror.xml) |

---
## 1. 功能简述

**按位右旋（rotate right）**：循环移位，bit 出去后从 bit 63 进来。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64Ror : T_ULARGE_INTEGER
VAR_INPUT
    ui64 : T_ULARGE_INTEGER;
    n : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ui64` | `T_ULARGE_INTEGER` | 源 |
| `n` | `DWORD` | 右旋位数 |

### 返回值

`T_ULARGE_INTEGER` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_ULARGE_INTEGER`。无独立错误码。

## 5. 使用注意 / 常见坑

- 对 n ≥ 64 的行为以 PDF 实现为准——⚠️ 待人工确认。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64Ror.xml`](../examples/P_Demo_UInt64Ror.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_UInt64Ror
VAR
    rResult : T_ULARGE_INTEGER;
    bRun    : BOOL;
    a : T_ULARGE_INTEGER;
END_VAR

a := ULARGE_INTEGER(16#80000000, 0);
IF bRun THEN
    rResult := UInt64Ror(a, 4);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 见上方使用注意中标 ⚠️ 的项。
