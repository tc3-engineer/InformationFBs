# FindAndDeleteChar
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
| Example | [`examples/P_Demo_FindAndDeleteChar.xml`](../examples/P_Demo_FindAndDeleteChar.xml) |

---
## 1. 功能简述

**查找并删除单字符**：移除 src 中所有出现的 `sDeleteChar`。返回删除次数。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FindAndDeleteChar : UDINT
VAR_INPUT
    pSrcString : POINTER TO STRING;
    sDeleteChar : STRING(1);
    pDstString : POINTER TO STRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pSrcString` | `POINTER TO STRING` | 源 STRING 指针 |
| `sDeleteChar` | `STRING(1)` | 要删除的字符 |
| `pDstString` | `POINTER TO STRING` | 目标 STRING 指针 |
| `nDstSize` | `UDINT` | 目标缓冲字节数 |

### 返回值

`UDINT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`FindAndDeleteChar(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `UDINT`。无独立错误码。

## 5. 使用注意 / 常见坑

- 针对单字符比 `FindAndDelete` 更快。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FindAndDeleteChar.xml`](../examples/P_Demo_FindAndDeleteChar.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FindAndDeleteChar
VAR
    rResult : UDINT;
    bRun    : BOOL;
    sIn  : STRING(255) := 'a-b-c-d-e';
    sOut : STRING(255);
END_VAR

IF bRun THEN
    rResult := FindAndDeleteChar(ADR(sIn), '-', ADR(sOut), SIZEOF(sOut));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
