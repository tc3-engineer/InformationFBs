# FindAndDelete
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
| Example | [`examples/P_Demo_FindAndDelete.xml`](../examples/P_Demo_FindAndDelete.xml) |

---
## 1. 功能简述

**查找并删除所有出现**：删除 `*pDeleteString` 在 src 中的全部出现，写入 dst。返回成功删除的次数。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FindAndDelete : UDINT
VAR_INPUT
    pSrcString : POINTER TO STRING;
    pDeleteString : POINTER TO STRING;
    pDstString : POINTER TO STRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pSrcString` | `POINTER TO STRING` | 源 STRING 指针 |
| `pDeleteString` | `POINTER TO STRING` | 要删除的子串指针 |
| `pDstString` | `POINTER TO STRING` | 目标 STRING 指针 |
| `nDstSize` | `UDINT` | 目标缓冲字节数 |

### 返回值

`UDINT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`FindAndDelete(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `UDINT`。无独立错误码。

## 5. 使用注意 / 常见坑

- 未找到返回 0。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FindAndDelete.xml`](../examples/P_Demo_FindAndDelete.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FindAndDelete
VAR
    rResult : UDINT;
    bRun    : BOOL;
    sIn  : STRING(255) := 'foo bar foo baz foo';
    sDel : STRING(31)  := 'foo';
    sOut : STRING(255);
END_VAR

IF bRun THEN
    rResult := FindAndDelete(ADR(sIn), ADR(sDel), ADR(sOut), SIZEOF(sOut));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
