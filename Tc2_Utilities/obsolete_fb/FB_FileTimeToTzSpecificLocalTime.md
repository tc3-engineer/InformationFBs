# FB_FileTimeToTzSpecificLocalTime
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `[obsolete]` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `⚠️ deprecated (verified)` |
| Example | [`examples/P_Demo_FB_FileTimeToTzSpecificLocalTime.xml`](../examples/P_Demo_FB_FileTimeToTzSpecificLocalTime.xml) |

---
## 1. 功能简述

⚠️ **已废弃** —— 请用 `FB_FileTime64ToTzSpecificLocalTime`（64-bit FILETIME）。

UTC FILETIME → 指定时区本地 FILETIME 转换，处理 DST 切换。

**重要**：仅适合**连续** UTC 时间戳；输入跳变会导致错误转换（FB 内部存上次结果以识别 B 时段）。配套 `A_Reset()` 动作可重置内部状态。
## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : T_FILETIME;
    tzInfo : ST_TimeZoneInformation;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `T_FILETIME` | 要转换的 UTC 时间（旧 FILETIME 结构） |
| `tzInfo` | `ST_TimeZoneInformation` | 目标时区信息（含 DST 切换规则） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    out : T_FILETIME;
    eTzID : E_TimeZoneID; (* := eTimeZoneID_Unknown *)
    bB : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `out` | `T_FILETIME` | 转换出的本地时间 |
| `eTzID` | `E_TimeZoneID` | 夏令时/标准时标识 |
| `bB` | `BOOL` | **B 时刻**标记（DST→标准时回拨期间，重复时段第二次） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述 + VAR 描述。

## 4. 错误码 / 返回值

出错时 `bError = TRUE`，错误码在 `nErrorId`/`hrErrorCode`（具体码表见 InfoSys 在线文档，⚠️ 待人工补充）。

## 5. 使用注意 / 常见坑

- **已废弃**——新代码用 `FB_FileTime64ToTzSpecificLocalTime`（64-bit FILETIME，更现代的类型）。
- **B 时刻**：DST 回拨期间出现的「重复时段」——`02:05:00 CEST A`（第一次）vs `02:05:00 CET B`（第二次回拨后）。`bB = TRUE` 标记后者。
- 输入必须**连续**——任意跳变（手动改时间）会破坏内部状态机，结果错误。
- 重置：调用关联动作 `A_Reset()` 清零内部状态。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FileTimeToTzSpecificLocalTime.xml`](../examples/P_Demo_FB_FileTimeToTzSpecificLocalTime.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_FileTimeToTzSpecificLocalTime
VAR
    fbFB_FileTimeToTzSpecificLocalTime : FB_FileTimeToTzSpecificLocalTime;
    arg_in : T_FILETIME;
    arg_tzInfo : ST_TimeZoneInformation;
    out_out : T_FILETIME;
    out_eTzID : E_TimeZoneID;
    out_bB : BOOL;
END_VAR

fbFB_FileTimeToTzSpecificLocalTime(
        in := arg_in,
        tzInfo := arg_tzInfo,
        out => out_out,
        eTzID => out_eTzID,
        bB => out_bB
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 本 FB 已废弃，仅供兼容旧代码。
