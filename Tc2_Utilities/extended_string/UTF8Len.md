# UTF8Len
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
| Example | [`examples/P_Demo_UTF8Len.xml`](../examples/P_Demo_UTF8Len.xml) |

---
## 1. 功能简述

**UTF-8 字符数**：返回字符数（注意：UTF-8 字节数 ≥ 字符数）。同时输出全 ASCII 标志和字节长度。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UTF8Len : UDINT
VAR_INPUT
    pUTF8 : PVOID;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pUTF8` | `PVOID` | 源 UTF-8 字符串指针（NUL 结束） |

### 返回值

`UDINT` —— 函数计算结果。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bASCII : BOOL;
    nSize : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bASCII` | `BOOL` | TRUE = 全部为 ASCII |
| `nSize` | `UDINT` | 字节长度（不含 NUL，可能 > 字符数） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`UTF8Len(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `UDINT`。无独立错误码。

## 5. 使用注意 / 常见坑

- 若不是合法 UTF-8 → 返回 0。
- ASCII 字符串在 UTF-8 中字节数 = 字符数。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UTF8Len.xml`](../examples/P_Demo_UTF8Len.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_UTF8Len
VAR
    rResult : UDINT;
    bRun    : BOOL;
    sUtf8 : STRING(511);
    bAsc : BOOL;
    nSz  : UDINT;
END_VAR

sUtf8 := sLiteral_TO_UTF8('café');
IF bRun THEN
    rResult := UTF8Len(pUTF8 := ADR(sUtf8), bASCII => bAsc, nSize => nSz);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
