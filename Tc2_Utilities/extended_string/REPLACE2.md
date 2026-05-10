# REPLACE2
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
| Example | [`examples/P_Demo_REPLACE2.xml`](../examples/P_Demo_REPLACE2.xml) |

---
## 1. 功能简述

**位置替换（任意长 STRING）**：从第 nPos 起替换 nLen 个字符为 `*pInsertString`。返回 TRUE 成功 / FALSE 超长。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION REPLACE2 : BOOL
VAR_INPUT
    pSrcString : POINTER TO STRING;
    pInsertString : POINTER TO STRING;
    pDstString : POINTER TO STRING;
    nDstSize : UDINT;
    nLen : UDINT;
    nPos : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pSrcString` | `POINTER TO STRING` | 源 |
| `pInsertString` | `POINTER TO STRING` | 替换为的子串 |
| `pDstString` | `POINTER TO STRING` | 目标 |
| `nDstSize` | `UDINT` | 目标字节数 |
| `nLen` | `UDINT` | 要替换的字符数 |
| `nPos` | `UDINT` | 起始位置（1 起） |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`REPLACE2(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码。

## 5. 使用注意 / 常见坑

- 对应 `Tc2_Standard.REPLACE` 的扩展版。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_REPLACE2.xml`](../examples/P_Demo_REPLACE2.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_REPLACE2
VAR
    rResult : BOOL;
    bRun    : BOOL;
    sIn  : STRING(255) := 'abcDEFghi';
    sIns : STRING(31)  := 'XYZ';
    sOut : STRING(255);
END_VAR

IF bRun THEN
    rResult := REPLACE2(ADR(sIn), ADR(sIns), ADR(sOut), SIZEOF(sOut), 3, 4);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
