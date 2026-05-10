# CONCAT2
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
| Example | [`examples/P_Demo_CONCAT2.xml`](../examples/P_Demo_CONCAT2.xml) |

---
## 1. 功能简述

**任意长度 STRING 拼接**（不限于 STRING(255)）。返回 TRUE = 完全拼接成功；FALSE = 结果超长被截断。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION CONCAT2 : BOOL
VAR_INPUT
    pSrcString1 : POINTER TO STRING;
    pSrcString2 : POINTER TO STRING;
    pDstString : POINTER TO STRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pSrcString1` | `POINTER TO STRING` | 前段 STRING 指针 |
| `pSrcString2` | `POINTER TO STRING` | 后段 STRING 指针 |
| `pDstString` | `POINTER TO STRING` | 目标 STRING 指针（输出） |
| `nDstSize` | `UDINT` | 目标缓冲字节数（用 SIZEOF） |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`CONCAT2(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码。

## 5. 使用注意 / 常见坑

- **安全检查**：当结果长度超过 nDstSize 会截断并返回 FALSE。
- 解决 `Tc2_Standard.CONCAT` 限制 255 字符的问题。
- 无限循环防护：内部最多检查 `Parameterlist.cMaxCharacters` 个字符。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CONCAT2.xml`](../examples/P_Demo_CONCAT2.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_CONCAT2
VAR
    rResult : BOOL;
    bRun    : BOOL;
    sA, sB, sC : STRING(255);
END_VAR

sA := 'Hello, '; sB := 'World!';
IF bRun THEN
    rResult := CONCAT2(ADR(sA), ADR(sB), ADR(sC), SIZEOF(sC));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
