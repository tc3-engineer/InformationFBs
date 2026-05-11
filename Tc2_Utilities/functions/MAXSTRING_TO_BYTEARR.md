# MAXSTRING_TO_BYTEARR
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
| Example | [`examples/P_Demo_MAXSTRING_TO_BYTEARR.xml`](../examples/P_Demo_MAXSTRING_TO_BYTEARR.xml) |

---
## 1. 功能简述

**字符串 → 字节数组**：拆成 ASCII 字节数组。反向：`BYTEARR_TO_MAXSTRING`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION MAXSTRING_TO_BYTEARR : ARRAY[0..MAX_STRING_LENGTH] OF BYTE
VAR_INPUT
    in : T_MaxString;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `T_MaxString` | 源字符串 |

### 返回值

`ARRAY[0..MAX_STRING_LENGTH] OF BYTE` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `ARRAY[0..MAX_STRING_LENGTH] OF BYTE`。

## 5. 使用注意 / 常见坑

- 返回类型为定长数组——调用方需提前声明同类型变量接收。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MAXSTRING_TO_BYTEARR.xml`](../examples/P_Demo_MAXSTRING_TO_BYTEARR.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_MAXSTRING_TO_BYTEARR
VAR
    rResult : ARRAY[0..MAX_STRING_LENGTH] OF BYTE;
    bRun    : BOOL;
    s : T_MaxString := 'Hi';
    ar : ARRAY[0..MAX_STRING_LENGTH] OF BYTE;
END_VAR

IF bRun THEN
    rResult := MAXSTRING_TO_BYTEARR(s);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
