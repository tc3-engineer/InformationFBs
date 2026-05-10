# INSERT2
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
| Example | [`examples/P_Demo_INSERT2.xml`](../examples/P_Demo_INSERT2.xml) |

---
## 1. 功能简述

**插入子串（任意长 STRING）**：把 `*pInsertString` 插入到 `*pSrcString` 第 nPos 字符之后。返回 TRUE = 成功，FALSE = 结果超 dst。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION INSERT2 : BOOL
VAR_INPUT
    pSrcString : POINTER TO STRING;
    pInsertString : POINTER TO STRING;
    pDstString : POINTER TO STRING;
    nDstSize : UDINT;
    nPos : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pSrcString` | `POINTER TO STRING` | 源 STRING 指针 |
| `pInsertString` | `POINTER TO STRING` | 要插入的子串 |
| `pDstString` | `POINTER TO STRING` | 目标 |
| `nDstSize` | `UDINT` | 目标字节数 |
| `nPos` | `UDINT` | 在第 nPos 字符之后插入；nPos = 0 → 头部插入 |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`INSERT2(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码。

## 5. 使用注意 / 常见坑

- 对应 `Tc2_Standard.INSERT` 的扩展版。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_INSERT2.xml`](../examples/P_Demo_INSERT2.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_INSERT2
VAR
    rResult : BOOL;
    bRun    : BOOL;
    sIn  : STRING(255) := 'foobar';
    sIns : STRING(31)  := 'XYZ';
    sOut : STRING(255);
END_VAR

IF bRun THEN
    rResult := INSERT2(ADR(sIn), ADR(sIns), ADR(sOut), SIZEOF(sOut), 3);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
