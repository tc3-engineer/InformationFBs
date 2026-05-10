# FindAndSplitChar
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
| Example | [`examples/P_Demo_FindAndSplitChar.xml`](../examples/P_Demo_FindAndSplitChar.xml) |

---
## 1. 功能简述

**按单字符拆分为左右两半**。比 `FindAndSplit` 更快（针对单字符）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FindAndSplitChar : BOOL
VAR_INPUT
    sSeparatorChar : STRING(1);
    pSrcString : POINTER TO STRING;
    pLeftString : POINTER TO STRING;
    nLeftSize : UDINT;
    pRightString : POINTER TO STRING;
    nRightSize : UDINT;
    bSearchFromRight : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sSeparatorChar` | `STRING(1)` | 分隔字符 |
| `pSrcString` | `POINTER TO STRING` | 源 |
| `pLeftString` | `POINTER TO STRING` | 左半 |
| `nLeftSize` | `UDINT` | 左半字节数 |
| `pRightString` | `POINTER TO STRING` | 右半 |
| `nRightSize` | `UDINT` | 右半字节数 |
| `bSearchFromRight` | `BOOL` | TRUE 从右搜 |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`FindAndSplitChar(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码。

## 5. 使用注意 / 常见坑

- 与 `FindAndSplit` 行为一致；性能更好。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FindAndSplitChar.xml`](../examples/P_Demo_FindAndSplitChar.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FindAndSplitChar
VAR
    rResult : BOOL;
    bRun    : BOOL;
    sIn   : STRING(255) := 'a/b/c';
    sL,sR : STRING(255);
END_VAR

IF bRun THEN
    rResult := FindAndSplitChar('/', ADR(sIn), ADR(sL), SIZEOF(sL), ADR(sR), SIZEOF(sR), FALSE);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
