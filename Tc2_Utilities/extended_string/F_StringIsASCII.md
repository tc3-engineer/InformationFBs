# F_StringIsASCII
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
| Example | [`examples/P_Demo_F_StringIsASCII.xml`](../examples/P_Demo_F_StringIsASCII.xml) |

---
## 1. 功能简述

**ASCII 检查**：返回 TRUE = 字符串只含 ASCII（0x00..0x7F）。同时输出字符数。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_StringIsASCII : BOOL
VAR_INPUT
    pSTRING : POINTER TO STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pSTRING` | `POINTER TO STRING` | 源 STRING 指针 |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    nLen : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nLen` | `UDINT` | 字符数（如全 ASCII，即字节数） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`F_StringIsASCII(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码。

## 5. 使用注意 / 常见坑

- PDF 表格里写 `pString` 小写 's'，VAR_INPUT 用 `pSTRING`——文档以 VAR_INPUT 为准。
- 全 ASCII 的字符串可直接当作 UTF-8 用（兼容）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_StringIsASCII.xml`](../examples/P_Demo_F_StringIsASCII.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_StringIsASCII
VAR
    rResult : BOOL;
    bRun    : BOOL;
    sIn : STRING(255) := 'Hello';
    nLen : UDINT;
END_VAR

IF bRun THEN
    rResult := F_StringIsASCII(pSTRING := ADR(sIn), nLen => nLen);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
