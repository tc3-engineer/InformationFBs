# HEXCHRNIBBLE_TO_BYTE
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
| Example | [`examples/P_Demo_HEXCHRNIBBLE_TO_BYTE.xml`](../examples/P_Demo_HEXCHRNIBBLE_TO_BYTE.xml) |

---
## 1. 功能简述

**hex 字符 → 半字节**：返回 0..15；非法字符返回 255。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION HEXCHRNIBBLE_TO_BYTE : BYTE
VAR_INPUT
    chr : STRING(1);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `chr` | `STRING(1)` | hex 半字节字符 |

### 返回值

`BYTE` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `BYTE`。

## 5. 使用注意 / 常见坑

- 输入是 STRING(1) 字符；ASCII 码输入版本用 `HEXASCNIBBLE_TO_BYTE`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_HEXCHRNIBBLE_TO_BYTE.xml`](../examples/P_Demo_HEXCHRNIBBLE_TO_BYTE.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_HEXCHRNIBBLE_TO_BYTE
VAR
    rResult : BYTE;
    bRun    : BOOL;
END_VAR

IF bRun THEN
    rResult := HEXCHRNIBBLE_TO_BYTE('A');
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
