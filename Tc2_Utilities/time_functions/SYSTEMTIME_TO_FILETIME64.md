# SYSTEMTIME_TO_FILETIME64
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
| Example | [`examples/P_Demo_SYSTEMTIME_TO_FILETIME64.xml`](../examples/P_Demo_SYSTEMTIME_TO_FILETIME64.xml) |

---
## 1. 功能简述

TIMESTRUCT 转 64-bit FILETIME。`wDayOfWeek` 字段被忽略；`wYear` 必须 > 1601 且 < 30827。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION SYSTEMTIME_TO_FILETIME64 : T_FILETIME64
VAR_INPUT
    systemTime : TIMESTRUCT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `systemTime` | `TIMESTRUCT` | Windows SYSTEMTIME 结构 |

### 返回值

`T_FILETIME64` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `SYSTEMTIME_TO_FILETIME64(stIn)`，返回 `T_FILETIME64`。
- 期望：`对应 FILETIME64`

## 4. 错误码 / 返回值

返回 `T_FILETIME64`。无独立错误码（部分函数用 0/全 0 结构表示参数无效）。

## 5. 使用注意 / 常见坑

- `wDayOfWeek` 字段不参与计算（FB 内部按日期重算）。
- **年份范围**：1602..30826。
- 反向：`FILETIME64_TO_SYSTEMTIME`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SYSTEMTIME_TO_FILETIME64.xml`](../examples/P_Demo_SYSTEMTIME_TO_FILETIME64.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_SYSTEMTIME_TO_FILETIME64
VAR
    rResult : T_FILETIME64;
    bRun    : BOOL;
    stIn : TIMESTRUCT;
END_VAR

stIn.wYear := 2024; stIn.wMonth := 1; stIn.wDay := 1; stIn.wHour := 12;
IF bRun THEN
    rResult := SYSTEMTIME_TO_FILETIME64(stIn);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
