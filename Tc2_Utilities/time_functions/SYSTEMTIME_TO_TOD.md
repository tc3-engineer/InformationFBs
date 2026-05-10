# SYSTEMTIME_TO_TOD
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
| Example | [`examples/P_Demo_SYSTEMTIME_TO_TOD.xml`](../examples/P_Demo_SYSTEMTIME_TO_TOD.xml) |

---
## 1. 功能简述

从 TIMESTRUCT 提取「时间部分」（TOD），丢掉日期。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION SYSTEMTIME_TO_TOD : TOD
VAR_INPUT
    systemTime : TIMESTRUCT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `systemTime` | `TIMESTRUCT` | SYSTEMTIME 结构 |

### 返回值

`TOD` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `SYSTEMTIME_TO_TOD(stIn)`，返回 `TOD`。
- 期望：`TOD#12:34:56`

## 4. 错误码 / 返回值

返回 `TOD`。无独立错误码（部分函数用 0/全 0 结构表示参数无效）。

## 5. 使用注意 / 常见坑

- 返回 0 = 错误（参数无效）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SYSTEMTIME_TO_TOD.xml`](../examples/P_Demo_SYSTEMTIME_TO_TOD.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_SYSTEMTIME_TO_TOD
VAR
    rResult : TOD;
    bRun    : BOOL;
    stIn : TIMESTRUCT;
END_VAR

stIn.wYear := 2024; stIn.wMonth := 1; stIn.wDay := 1; stIn.wHour := 12; stIn.wMinute := 34; stIn.wSecond := 56;
IF bRun THEN
    rResult := SYSTEMTIME_TO_TOD(stIn);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
