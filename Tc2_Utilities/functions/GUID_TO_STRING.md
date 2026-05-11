# GUID_TO_STRING
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
| Example | [`examples/P_Demo_GUID_TO_STRING.xml`](../examples/P_Demo_GUID_TO_STRING.xml) |

---
## 1. 功能简述

**GUID → 字符串**：返回不带花括号的 `'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION GUID_TO_STRING : STRING
VAR_INPUT
    stIn : GUID;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stIn` | `GUID` | 源 GUID 结构 |

### 返回值

`STRING` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `STRING`。

## 5. 使用注意 / 常见坑

- **VAR_INPUT 参数名是 `stIn` 不是 `in`**（PDF 原样）。
- 带花括号的注册表版本用 `GUID_TO_REGSTRING`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GUID_TO_STRING.xml`](../examples/P_Demo_GUID_TO_STRING.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_GUID_TO_STRING
VAR
    rResult : STRING;
    bRun    : BOOL;
    g : GUID;
END_VAR

IF bRun THEN
    rResult := GUID_TO_STRING(g);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
