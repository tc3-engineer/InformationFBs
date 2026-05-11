# STRING_TO_UINT64
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
| Example | [`examples/P_Demo_STRING_TO_UINT64.xml`](../examples/P_Demo_STRING_TO_UINT64.xml) |

---
## 1. 功能简述

**STRING(21) → T_ULARGE_INTEGER**：把十进制字符串解析为 legacy 64-bit 无符号整数。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION STRING_TO_UINT64 : T_ULARGE_INTEGER
VAR_INPUT
    in : STRING(21);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `STRING(21)` | 源字符串（最多 21 字符，足够 UINT64 十进制） |

### 返回值

`T_ULARGE_INTEGER` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_ULARGE_INTEGER`。无独立错误码。

## 5. 使用注意 / 常见坑

- 字符串长度上限 21（UINT64 最大值 18446744073709551615 共 20 位 + NUL）。
- 非法字符（非数字）的行为以 PDF 实现为准——⚠️ 待人工确认。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_STRING_TO_UINT64.xml`](../examples/P_Demo_STRING_TO_UINT64.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_STRING_TO_UINT64
VAR
    rResult : T_ULARGE_INTEGER;
    bRun    : BOOL;
    s : STRING(21) := '12345';
END_VAR

IF bRun THEN
    rResult := STRING_TO_UINT64(s);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 见上方使用注意中标 ⚠️ 的项。
