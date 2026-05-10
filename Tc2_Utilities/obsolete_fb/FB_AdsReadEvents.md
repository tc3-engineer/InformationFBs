# FB_AdsReadEvents
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
| Example | [`examples/P_Demo_FB_AdsReadEvents.xml`](../examples/P_Demo_FB_AdsReadEvents.xml) |

---
## 1. 功能简述

⚠️ **已废弃** —— 仅 TwinCAT 3.1 Build 4024 之前可用。

通过 ADS 查询 EventLogger 的活动消息，结果填入 `aEvents` 数组（最多 80 条）。可绑定到可视化 Event table 的 Message data array 属性。

消息文本长度限制：≤255 字符全文输出；255~1023 字符截断；>1023 字符返回错误。
## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AMSNetId;
    bReadEvents : BOOL;
    nLanguageId : DWORD;
    eDateAndTimeFormat : E_DateAndTimeFormat;
    tRefreshTime : TIME;
    tTimeout : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sNetId` | `T_AMSNetId` | 目标 AmsNetId（空字符串=本地） |
| `bReadEvents` | `BOOL` | 使能读消息；下降沿同时复位错误输出 |
| `nLanguageId` | `DWORD` | Language ID（决定查哪种语言的消息文本） |
| `eDateAndTimeFormat` | `E_DateAndTimeFormat` | 时间戳格式（de_De / en_GB / en_US） |
| `tRefreshTime` | `TIME` | 消息查询周期 |
| `tTimeout` | `TIME` | ADS 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    aEvents : ARRAY[1..80] OF ST_ReadEvent;
    nNumberOfEvents : UDINT;
    bBusy : BOOL;
    bDone : BOOL;
    bError : BOOL;
    nErrorId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `aEvents` | `ARRAY[1..80] OF ST_ReadEvent` | 查到的消息数组（最多 80 条） |
| `nNumberOfEvents` | `UDINT` | 实际消息数量 |
| `bBusy` | `BOOL` | 执行中 |
| `bDone` | `BOOL` | 完成 |
| `bError` | `BOOL` | 出错 |
| `nErrorId` | `UDINT` | 错误号 |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述 + VAR 描述。

## 4. 错误码 / 返回值

出错时 `bError = TRUE`，错误码在 `nErrorId`/`hrErrorCode`（具体码表见 InfoSys 在线文档，⚠️ 待人工补充）。

## 5. 使用注意 / 常见坑

- **已废弃**——新代码请用 Tc3_EventLogger 提供的 `FB_RequestEventDetails` / `FB_TcEventLogger` 等。
- 数组限制 80 条——超出会丢失。
- 字符长度限制：255 / 1023 字符是硬上限。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_AdsReadEvents.xml`](../examples/P_Demo_FB_AdsReadEvents.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_AdsReadEvents
VAR
    fbFB_AdsReadEvents : FB_AdsReadEvents;
    arg_sNetId : T_AMSNetId;
    arg_bReadEvents : BOOL;
    arg_nLanguageId : DWORD;
    arg_eDateAndTimeFormat : E_DateAndTimeFormat;
    arg_tRefreshTime : TIME;
    arg_tTimeout : TIME;
    out_aEvents : ARRAY[1..80] OF ST_ReadEvent;
    out_nNumberOfEvents : UDINT;
    out_bBusy : BOOL;
    out_bDone : BOOL;
    out_bError : BOOL;
    out_nErrorId : UDINT;
END_VAR

fbFB_AdsReadEvents(
        sNetId := arg_sNetId,
        bReadEvents := arg_bReadEvents,
        nLanguageId := arg_nLanguageId,
        eDateAndTimeFormat := arg_eDateAndTimeFormat,
        tRefreshTime := arg_tRefreshTime,
        tTimeout := arg_tTimeout,
        aEvents => out_aEvents,
        nNumberOfEvents => out_nNumberOfEvents,
        bBusy => out_bBusy,
        bDone => out_bDone,
        bError => out_bError,
        nErrorId => out_nErrorId
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 本 FB 已废弃，仅供兼容旧代码。
