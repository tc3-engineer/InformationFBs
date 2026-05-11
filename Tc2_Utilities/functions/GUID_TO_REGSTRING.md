# GUID_TO_REGSTRING
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
| Example | [`examples/P_Demo_GUID_TO_REGSTRING.xml`](../examples/P_Demo_GUID_TO_REGSTRING.xml) |

---
## 1. 功能简述

**GUID → 注册表字符串**：返回带花括号的 `'{xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}'`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION GUID_TO_REGSTRING : STRING(38)
VAR_INPUT
    in : GUID;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `GUID` | 源 GUID 结构 |

### 返回值

`STRING(38)` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `STRING(38)`。

## 5. 使用注意 / 常见坑

- 包含花括号；不含的版本用 `GUID_TO_STRING`（STRING(36)）。
- 全 0 GUID → `'{00000000-0000-0000-0000-000000000000}'`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GUID_TO_REGSTRING.xml`](../examples/P_Demo_GUID_TO_REGSTRING.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_GUID_TO_REGSTRING
VAR
    rResult : STRING(38);
    bRun    : BOOL;
    g : GUID;
END_VAR

IF bRun THEN
    rResult := GUID_TO_REGSTRING(g);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
