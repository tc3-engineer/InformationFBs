# LEN2
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
| Example | [`examples/P_Demo_LEN2.xml`](../examples/P_Demo_LEN2.xml) |

---
## 1. 功能简述

**任意长 STRING 长度**：返回字符数（不含末尾 NUL）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LEN2 : UDINT
VAR_INPUT
    pSTRING : POINTER TO STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pSTRING` | `POINTER TO STRING` | 源 STRING 指针 |

### 返回值

`UDINT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`LEN2(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `UDINT`。无独立错误码。

## 5. 使用注意 / 常见坑

- 对应 `Tc2_Standard.LEN` 的 UDINT 返回扩展版。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LEN2.xml`](../examples/P_Demo_LEN2.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_LEN2
VAR
    rResult : UDINT;
    bRun    : BOOL;
    sIn : STRING(255) := 'hello';
END_VAR

IF bRun THEN
    rResult := LEN2(ADR(sIn));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
