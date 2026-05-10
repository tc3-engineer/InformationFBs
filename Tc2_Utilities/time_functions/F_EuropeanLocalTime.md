# F_EuropeanLocalTime
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
| Example | [`examples/P_Demo_F_EuropeanLocalTime.xml`](../examples/P_Demo_F_EuropeanLocalTime.xml) |

---
## 1. 功能简述

**仅适用于欧洲**：把 UTC 时间转为本地时间，并指示是否处于夏令时。比 `FB_SystemTimeToTzSpecificLocalTime` 更轻——适合小型控制器。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_EuropeanLocalTime : TIMESTRUCT
VAR_INPUT
    UTC : TIMESTRUCT;
    UTC_Offset : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `UTC` | `TIMESTRUCT` | UTC 时间（system time 结构） |
| `UTC_Offset` | `INT` | 时区偏移（分钟） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bDaylightSavingTime : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bDaylightSavingTime` | `BOOL` | TRUE = 当前是夏令时；FALSE = 标准时 |

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `F_EuropeanLocalTime(stUtc, 60)`，返回 `TIMESTRUCT`。
- 期望：`本地时（DST 期 +120 分钟）`

## 4. 错误码 / 返回值

返回 `TIMESTRUCT`。无独立错误码（部分函数用 0/全 0 结构表示参数无效）。

## 5. 使用注意 / 常见坑

- ⚠️ **仅欧洲时区**——其他时区行为未定义。全球用法请用 `FB_SystemTimeToTzSpecificLocalTime`。
- FB 内部根据 UTC_Offset 与日期自动计算 DST 切换点。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_EuropeanLocalTime.xml`](../examples/P_Demo_F_EuropeanLocalTime.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_EuropeanLocalTime
VAR
    rResult : TIMESTRUCT;
    bRun    : BOOL;
    stUtc : TIMESTRUCT;
    bDST  : BOOL;
    out_bDaylightSavingTime : BOOL;
END_VAR

stUtc.wYear := 2024; stUtc.wMonth := 7; stUtc.wDay := 15; stUtc.wHour := 10;
IF bRun THEN
    rResult := F_EuropeanLocalTime(stUtc, 60);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 见上方使用注意中标 ⚠️ 的项。
