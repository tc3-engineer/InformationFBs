# BYTEARR_TO_MAXSTRING
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_BYTEARR_TO_MAXSTRING.xml`](../examples/P_Demo_BYTEARR_TO_MAXSTRING.xml) |

---
## 1. 功能简述

**字节数组 → 字符串**：把含 ASCII 码的字节数组拼成 STRING。反向：`MAXSTRING_TO_BYTEARR`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION BYTEARR_TO_MAXSTRING : T_MaxString
VAR_INPUT
    in : ARRAY[0..MAX_STRING_LENGTH] OF BYTE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `ARRAY[0..MAX_STRING_LENGTH] OF BYTE` | ASCII 字节数组 |

### 返回值

`T_MaxString` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_MaxString`。

## 5. 使用注意 / 常见坑

- `MAX_STRING_LENGTH` 默认 255。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_BYTEARR_TO_MAXSTRING.xml`](../examples/P_Demo_BYTEARR_TO_MAXSTRING.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_BYTEARR_TO_MAXSTRING
VAR
    rResult : T_MaxString;
    bRun    : BOOL;
    ar : ARRAY[0..MAX_STRING_LENGTH] OF BYTE;
END_VAR

ar[0] := 16#48; ar[1] := 16#69;
IF bRun THEN
    rResult := BYTEARR_TO_MAXSTRING(ar);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
