# REGSTRING_TO_GUID
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
| Example | [`examples/P_Demo_REGSTRING_TO_GUID.xml`](../examples/P_Demo_REGSTRING_TO_GUID.xml) |

---
## 1. 功能简述

**注册表 GUID 字符串 → GUID 结构**。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION REGSTRING_TO_GUID : GUID
VAR_INPUT
    in : STRING(38);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `STRING(38)` | 注册表 GUID 字符串（带花括号） |

### 返回值

`GUID` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `GUID`。

## 5. 使用注意 / 常见坑

- 格式必须 `'{xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}'`（带花括号）。
- 格式错误或全 0 → 返回全 0 GUID。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_REGSTRING_TO_GUID.xml`](../examples/P_Demo_REGSTRING_TO_GUID.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_REGSTRING_TO_GUID
VAR
    rResult : GUID;
    bRun    : BOOL;
    s : STRING(38) := '{12345678-1234-1234-1234-123456789ABC}';
END_VAR

IF bRun THEN
    rResult := REGSTRING_TO_GUID(s);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
