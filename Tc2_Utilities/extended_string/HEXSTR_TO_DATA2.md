# HEXSTR_TO_DATA2
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
| Example | [`examples/P_Demo_HEXSTR_TO_DATA2.xml`](../examples/P_Demo_HEXSTR_TO_DATA2.xml) |

---
## 1. 功能简述

**十六进制字符串 → 二进制**：解析 'AB CD 01 23' 之类的 hex 文本（仅空格作分隔符）写入 binary buffer。返回成功转换的字节数；遇非法字符或溢出返回 0。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION HEXSTR_TO_DATA2 : UDINT
VAR_INPUT
    pSrcHexStr : POINTER TO STRING; (* hex string to convert (Example: "AF 34 55 EC") *)
    pDstData : POINTER TO BYTE; (* pointer to destination buffer *)
    nDstSize : UDINT; (* size of destination buffer in bytes *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pSrcHexStr` | `POINTER TO STRING` | 源 HEX 字符串指针（如 'AF 34 55 EC'） |
| `pDstData` | `POINTER TO BYTE` | 目标 binary 缓冲指针 |
| `nDstSize` | `UDINT` | 目标缓冲字节数 |

### 返回值

`UDINT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用：`HEXSTR_TO_DATA2(...)` 见下方例程。

## 4. 错误码 / 返回值

返回 `UDINT`。无独立错误码。

## 5. 使用注意 / 常见坑

- **仅空格分隔**——逗号/连字符等其它分隔符会被当成非法字符。
- 大小写混用允许。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_HEXSTR_TO_DATA2.xml`](../examples/P_Demo_HEXSTR_TO_DATA2.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_HEXSTR_TO_DATA2
VAR
    rResult : UDINT;
    bRun    : BOOL;
    sHex : STRING(63) := 'AF 34 55 EC';
    aData : ARRAY[0..15] OF BYTE;
END_VAR

IF bRun THEN
    rResult := HEXSTR_TO_DATA2(ADR(sHex), ADR(aData), SIZEOF(aData));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
