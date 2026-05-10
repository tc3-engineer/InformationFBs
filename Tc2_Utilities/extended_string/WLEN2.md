# WLEN2
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
| Example | [`examples/P_Demo_WLEN2.xml`](../examples/P_Demo_WLEN2.xml) |

---
## 1. 功能简述

**任意长 WSTRING 长度**：返回字符数（Unicode 字符）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WLEN2 : UDINT
VAR_INPUT
    pWSTRING : POINTER TO WSTRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pWSTRING` | `POINTER TO WSTRING` | 源 WSTRING 指针 |

### 返回值

`UDINT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`WLEN2(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `UDINT`。无独立错误码。

## 5. 使用注意 / 常见坑

- 对应 `Tc2_Standard.WLEN` 的 UDINT 返回扩展版。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WLEN2.xml`](../examples/P_Demo_WLEN2.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_WLEN2
VAR
    rResult : UDINT;
    bRun    : BOOL;
    ws : WSTRING(255);
END_VAR

ws := "hello";
IF bRun THEN
    rResult := WLEN2(ADR(ws));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
