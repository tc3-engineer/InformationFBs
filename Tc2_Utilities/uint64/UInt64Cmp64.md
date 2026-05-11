# UInt64Cmp64
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `64 bit integer functions (unsigned)` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_UInt64Cmp64.xml`](../examples/P_Demo_UInt64Cmp64.xml) |

---
## 1. 功能简述

**比较**：返回 -1（a<b）/ 0（a=b）/ 1（a>b）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION UInt64Cmp64 : DINT
VAR_INPUT
    ui64a : T_ULARGE_INTEGER;
    ui64b : T_ULARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ui64a` | `T_ULARGE_INTEGER` | 比较 a |
| `ui64b` | `T_ULARGE_INTEGER` | 比较 b |

### 返回值

`DINT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `DINT`。无独立错误码。

## 5. 使用注意 / 常见坑

- 三态返回，类似 memcmp。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UInt64Cmp64.xml`](../examples/P_Demo_UInt64Cmp64.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_UInt64Cmp64
VAR
    rResult : DINT;
    bRun    : BOOL;
    a, b : T_ULARGE_INTEGER;
END_VAR

a := ULARGE_INTEGER(0, 1); b := ULARGE_INTEGER(0, 2);
IF bRun THEN
    rResult := UInt64Cmp64(a, b);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
