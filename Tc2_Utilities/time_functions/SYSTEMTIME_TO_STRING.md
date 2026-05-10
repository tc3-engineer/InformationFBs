# SYSTEMTIME_TO_STRING
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_SYSTEMTIME_TO_STRING.xml`](../examples/P_Demo_SYSTEMTIME_TO_STRING.xml) |

---
## 1. 功能简述

TIMESTRUCT 转格式化字符串 `YYYY-MM-DD-hh:mm:ss.xxx`。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION SYSTEMTIME_TO_STRING : STRING(24)
VAR_INPUT
    in : TIMESTRUCT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `TIMESTRUCT` | Windows SYSTEMTIME 结构 |

### 返回值

`STRING(24)` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `SYSTEMTIME_TO_STRING(stIn)`，返回 `STRING(24)`。
- 期望：`'2024-01-01-12:00:00.000'`

## 4. 错误码 / 返回值

返回 `STRING(24)`。无独立错误码（部分函数用 0/全 0 结构表示参数无效）。

## 5. 使用注意 / 常见坑

- 格式固定（24 字符 + 终止符）。
- 反向：`STRING_TO_SYSTEMTIME`（注意输入 STRING 长度限制 23 字符）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SYSTEMTIME_TO_STRING.xml`](../examples/P_Demo_SYSTEMTIME_TO_STRING.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_SYSTEMTIME_TO_STRING
VAR
    rResult : STRING(24);
    bRun    : BOOL;
    stIn : TIMESTRUCT;
END_VAR

stIn.wYear := 2024; stIn.wMonth := 1; stIn.wDay := 1; stIn.wHour := 12;
IF bRun THEN
    rResult := SYSTEMTIME_TO_STRING(stIn);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
