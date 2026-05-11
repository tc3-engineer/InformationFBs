# HEXSTR_TO_DATA
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_HEXSTR_TO_DATA.xml`](../examples/P_Demo_HEXSTR_TO_DATA.xml) |

---
## 1. 功能简述

**HEX 文本 → 二进制**：解析 hex 字符串到 byte buffer，返回成功字节数；遇错返回 0。**仅空格作分隔符**。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION HEXSTR_TO_DATA : UDINT
VAR_INPUT
    sHex : T_MaxString;
    pData : POINTER TO BYTE;
    cbData : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sHex` | `T_MaxString` | 源 hex 字符串（如 'AB CD 01 23'） |
| `pData` | `POINTER TO BYTE` | 目标 binary 缓冲指针 |
| `cbData` | `UDINT` | 目标缓冲字节数 |

### 返回值

`UDINT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `UDINT`。

## 5. 使用注意 / 常见坑

- **仅空格分隔**——其他分隔字符（逗号、连字符）被当作非法。
- 大小写都接受。
- 长字符串用 `HEXSTR_TO_DATA2`（Round 6）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_HEXSTR_TO_DATA.xml`](../examples/P_Demo_HEXSTR_TO_DATA.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_HEXSTR_TO_DATA
VAR
    rResult : UDINT;
    bRun    : BOOL;
    sHex : STRING(63) := 'AB CD 01 23';
    ar : ARRAY[0..3] OF BYTE;
END_VAR

IF bRun THEN
    rResult := HEXSTR_TO_DATA(sHex, ADR(ar), SIZEOF(ar));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
