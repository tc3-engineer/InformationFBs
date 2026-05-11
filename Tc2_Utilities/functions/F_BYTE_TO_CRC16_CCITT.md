# F_BYTE_TO_CRC16_CCITT
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
| Example | [`examples/P_Demo_F_BYTE_TO_CRC16_CCITT.xml`](../examples/P_Demo_F_BYTE_TO_CRC16_CCITT.xml) |

---
## 1. 功能简述

**单字节 CRC-16 CCITT 滚动累加**：对单字节计算 CRC-16-CCITT，可累积调用。多字节用 `F_DATA_TO_CRC16_CCITT`。

生成多项式：`x¹⁶ + x¹² + x⁵ + 1`（值 `0x1021`，ITU X.25/T.30/HDLC 等标准）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_BYTE_TO_CRC16_CCITT : WORD
VAR_INPUT
    value : BYTE; (* Data value *)
    crc : WORD; (* Initial value (16#FFFF or 16#0000) or previous CRC-16 result *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `value` | `BYTE` | 数据字节 |
| `crc` | `WORD` | 初始值 / 上次 CRC |

### 返回值

`WORD` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `WORD`。

## 5. 使用注意 / 常见坑

- **初始值**：`16#FFFF` 或 `16#0000`，按目标协议选择。
- 累积调用：上次返回值喂回 `crc`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BYTE_TO_CRC16_CCITT.xml`](../examples/P_Demo_F_BYTE_TO_CRC16_CCITT.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_BYTE_TO_CRC16_CCITT
VAR
    rResult : WORD;
    bRun    : BOOL;
    crc : WORD;
END_VAR

IF bRun THEN
    rResult := F_BYTE_TO_CRC16_CCITT(16#41, 16#FFFF);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
