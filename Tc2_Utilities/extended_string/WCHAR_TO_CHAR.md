# WCHAR_TO_CHAR
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_WCHAR_TO_CHAR.xml`](../examples/P_Demo_WCHAR_TO_CHAR.xml) |

---
## 1. 功能简述

**单字符转换**：WSTRING(1) → STRING(1)（带 null 结束）。仅当对应 ASCII 字符存在时成功，否则返回空。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WCHAR_TO_CHAR : STRING(1)
VAR_INPUT
    sTextIn : WSTRING(1);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sTextIn` | `WSTRING(1)` | 要转换的 WSTRING(1) 字符 |

### 返回值

`STRING(1)` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`WCHAR_TO_CHAR(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `STRING(1)`。无独立错误码。

## 5. 使用注意 / 常见坑

- 字符必须有 STRING 等价（基本上是 ASCII / Windows-1252）。
- 多字符用 `WSTRING_TO_STRING2`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WCHAR_TO_CHAR.xml`](../examples/P_Demo_WCHAR_TO_CHAR.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_WCHAR_TO_CHAR
VAR
    rResult : STRING(1);
    bRun    : BOOL;
    wsIn : WSTRING(1) := "A";
END_VAR

IF bRun THEN
    rResult := WCHAR_TO_CHAR(wsIn);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
