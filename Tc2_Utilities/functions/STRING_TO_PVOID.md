# STRING_TO_PVOID
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
| Example | [`examples/P_Demo_STRING_TO_PVOID.xml`](../examples/P_Demo_STRING_TO_PVOID.xml) |

---
## 1. 功能简述

**字符串 → PVOID**：解析含 hex 数值的字符串得到指针。错误时返回 0。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION STRING_TO_PVOID : PVOID
VAR_INPUT
    in : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `STRING` | hex 形式字符串（如 `'16#89345678'`） |

### 返回值

`PVOID` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `PVOID`。

## 5. 使用注意 / 常见坑

- 反向：`PVOID_TO_STRING`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_STRING_TO_PVOID.xml`](../examples/P_Demo_STRING_TO_PVOID.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_STRING_TO_PVOID
VAR
    rResult : PVOID;
    bRun    : BOOL;
    s : STRING := '16#89345678';
END_VAR

IF bRun THEN
    rResult := STRING_TO_PVOID(s);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
