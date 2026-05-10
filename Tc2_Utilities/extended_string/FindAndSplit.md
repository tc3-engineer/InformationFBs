# FindAndSplit
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
| Example | [`examples/P_Demo_FindAndSplit.xml`](../examples/P_Demo_FindAndSplit.xml) |

---
## 1. 功能简述

**按分隔字符串拆分为左右两半**。默认从左找首次出现，bSearchFromRight=TRUE 时从右找最后出现。返回 TRUE = 找到分隔符并成功拆分。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FindAndSplit : BOOL
VAR_INPUT
    pSeparator : POINTER TO STRING;
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
| `pSeparator` | `POINTER TO STRING` | 分隔字符串 |
| `pSrcString` | `POINTER TO STRING` | 源 STRING |
| `pLeftString` | `POINTER TO STRING` | 左半结果 |
| `nLeftSize` | `UDINT` | 左半缓冲字节数 |
| `pRightString` | `POINTER TO STRING` | 右半结果 |
| `nRightSize` | `UDINT` | 右半缓冲字节数 |
| `bSearchFromRight` | `BOOL` | TRUE 从右向左搜（取最后出现的分隔符） |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`FindAndSplit(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码。

## 5. 使用注意 / 常见坑

- 典型用途：解析路径 `'C:\dir\file.txt'` 用 `'\\'` 分割。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FindAndSplit.xml`](../examples/P_Demo_FindAndSplit.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FindAndSplit
VAR
    rResult : BOOL;
    bRun    : BOOL;
    sIn   : STRING(255) := 'a/b/c';
    sSep  : STRING(7)   := '/';
    sL,sR : STRING(255);
END_VAR

IF bRun THEN
    rResult := FindAndSplit(ADR(sSep), ADR(sIn), ADR(sL), SIZEOF(sL), ADR(sR), SIZEOF(sR), FALSE);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
