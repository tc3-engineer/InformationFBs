# SYSTEMTIME_TO_ISO8601
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
| Example | [`examples/P_Demo_SYSTEMTIME_TO_ISO8601.xml`](../examples/P_Demo_SYSTEMTIME_TO_ISO8601.xml) |

---
## 1. 功能简述

TIMESTRUCT 转 **ISO 8601 字符串** `YYYY-MM-DDThh:mm:ss.xxxTZD`（同 `FILETIME64_TO_ISO8601` 但接受 SYSTEMTIME 输入）。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION SYSTEMTIME_TO_ISO8601 : STRING(39)
VAR_INPUT
    systemTime : TIMESTRUCT; (* Input time in system time format (struct) *)
    nBias : INT; (* Specifies the current bias, in minutes, for local time translation on this computer. The bias is the difference between Coordinated Universal Time (UTC) and local time. UTC = local time + bias *)
    bUTC : BOOL; (* Specifies whether the systemTime is UTC or local time. *)
    nPrecision : USINT(0..9); (* Precision. Number of decimal places of seconds. (0..9) *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `systemTime` | `TIMESTRUCT` | SYSTEMTIME 结构 |
| `nBias` | `INT` | 时区偏移（分钟） |
| `bUTC` | `BOOL` | systemTime 是 UTC 还是本地时 |
| `nPrecision` | `USINT(0..9)` | 秒小数位精度（0..9） |

### 返回值

`STRING(39)` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `SYSTEMTIME_TO_ISO8601(stIn, 60, FALSE, 3)`，返回 `STRING(39)`。
- 期望：`'2024-01-01T13:00:00.000+01:00'`

## 4. 错误码 / 返回值

返回 `STRING(39)`。无独立错误码（部分函数用 0/全 0 结构表示参数无效）。

## 5. 使用注意 / 常见坑

- 参数语义见 `FILETIME64_TO_ISO8601`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SYSTEMTIME_TO_ISO8601.xml`](../examples/P_Demo_SYSTEMTIME_TO_ISO8601.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_SYSTEMTIME_TO_ISO8601
VAR
    rResult : STRING(39);
    bRun    : BOOL;
    stIn : TIMESTRUCT;
END_VAR

stIn.wYear := 2024; stIn.wMonth := 1; stIn.wDay := 1; stIn.wHour := 12;
IF bRun THEN
    rResult := SYSTEMTIME_TO_ISO8601(stIn, 60, FALSE, 3);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
