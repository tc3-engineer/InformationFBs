# PVOID_TO_STRING
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
| Example | [`examples/P_Demo_PVOID_TO_STRING.xml`](../examples/P_Demo_PVOID_TO_STRING.xml) |

---
## 1. 功能简述

**PVOID → 字符串**：带 `'16#'` 前缀的 hex 字符串。**长度自适应位宽**：32 位系统 8 位 hex，64 位系统 16 位 hex。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION PVOID_TO_STRING : T_MaxString
VAR_INPUT
    in : PVOID;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `PVOID` | 待转换的指针 |

### 返回值

`T_MaxString` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_MaxString`。

## 5. 使用注意 / 常见坑

- 格式固定（不接受 iPrecision）；调试输出指针值时用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_PVOID_TO_STRING.xml`](../examples/P_Demo_PVOID_TO_STRING.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_PVOID_TO_STRING
VAR
    rResult : T_MaxString;
    bRun    : BOOL;
    p : PVOID;
    v : DINT := 42;
END_VAR

p := ADR(v);
IF bRun THEN
    rResult := PVOID_TO_STRING(p);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
