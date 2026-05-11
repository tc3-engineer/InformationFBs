# F_DATA_TO_CRC16_CCITT
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
| Example | [`examples/P_Demo_F_DATA_TO_CRC16_CCITT.xml`](../examples/P_Demo_F_DATA_TO_CRC16_CCITT.xml) |

---
## 1. 功能简述

**任意数据 CRC-16 CCITT**：内部循环调用 `F_BYTE_TO_CRC16_CCITT`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_DATA_TO_CRC16_CCITT : WORD
VAR_INPUT
    pData : POINTER TO BYTE; (* Pointer to first data byte *)
    cbData : UDINT; (* Length of data *)
    crc : WORD; (* Initial value (16#FFFF or 16#0000) or previous CRC-16 result *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pData` | `POINTER TO BYTE` | 源缓冲指针 |
| `cbData` | `UDINT` | 源字节数 |
| `crc` | `WORD` | 初始值 |

### 返回值

`WORD` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `WORD`。

## 5. 使用注意 / 常见坑

- 算法详见 `F_BYTE_TO_CRC16_CCITT`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_DATA_TO_CRC16_CCITT.xml`](../examples/P_Demo_F_DATA_TO_CRC16_CCITT.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_DATA_TO_CRC16_CCITT
VAR
    rResult : WORD;
    bRun    : BOOL;
    ar : ARRAY[0..3] OF BYTE := [1,2,3,4];
END_VAR

IF bRun THEN
    rResult := F_DATA_TO_CRC16_CCITT(ADR(ar), SIZEOF(ar), 16#FFFF);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
