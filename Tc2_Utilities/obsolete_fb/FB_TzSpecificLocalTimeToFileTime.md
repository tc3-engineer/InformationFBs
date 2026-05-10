# FB_TzSpecificLocalTimeToFileTime
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
| Example | [`examples/P_Demo_FB_TzSpecificLocalTimeToFileTime.xml`](../examples/P_Demo_FB_TzSpecificLocalTimeToFileTime.xml) |

---
## 1. 功能简述

⚠️ **已废弃** —— 请用 `FB_TzSpecificLocalTimeToFileTime64`。

本地 FILETIME → UTC FILETIME 转换。本地时间因 DST 会发生跳变，UTC 应连续——本 FB 处理 DST 切换并把结果转回连续 UTC。

**建议**：时间戳本身**应始终用 UTC**，仅在显示（如 HMI）时再转本地——避免 DST 跳变带来的转换难题。
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
| `in` | `T_FILETIME` | 要转换的本地时间（旧 FILETIME 结构） |
| `tzInfo` | `ST_TimeZoneInformation` | 源时区信息 |

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
| `out` | `T_FILETIME` | 转换出的 UTC 时间（连续） |
| `eTzID` | `E_TimeZoneID` | 夏令时/标准时标识 |
| `bB` | `BOOL` | B 时刻标记 |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述 + VAR 描述。

## 4. 错误码 / 返回值

出错时 `bError = TRUE`，错误码在 `nErrorId`/`hrErrorCode`（具体码表见 InfoSys 在线文档，⚠️ 待人工补充）。

## 5. 使用注意 / 常见坑

- **已废弃**——新代码用 `FB_TzSpecificLocalTimeToFileTime64`。
- **工程惯例**：内部时间戳用 UTC（连续），仅显示时转本地。本 FB 处理反向（local→UTC）较为脆弱。
- B 时刻含义同 `FB_FileTimeToTzSpecificLocalTime`。
- 重置内部状态：调用 `A_Reset()`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TzSpecificLocalTimeToFileTime.xml`](../examples/P_Demo_FB_TzSpecificLocalTimeToFileTime.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_TzSpecificLocalTimeToFileTime
VAR
    fbFB_TzSpecificLocalTimeToFileTime : FB_TzSpecificLocalTimeToFileTime;
    arg_in : T_FILETIME;
    arg_tzInfo : ST_TimeZoneInformation;
    out_out : T_FILETIME;
    out_eTzID : E_TimeZoneID;
    out_bB : BOOL;
END_VAR

fbFB_TzSpecificLocalTimeToFileTime(
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
