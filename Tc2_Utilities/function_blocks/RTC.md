# RTC
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_RTC.xml`](../examples/P_Demo_RTC.xml) |

---
## 1. 功能简述

The function block RTC (Real Time Clock) can be used to realize an internal software clock in the TwinCAT PLC. The clock must be initialized with a starting date and time. After the initialization the time and date are updated with each call of the function block. A CPU system clock is used to calculate the current time and date. The function block should be called in every PLC cycle, so that the current time can be calculated. The current date and time are available in the usual DATE_AND_TIME (DT) format at the function block's output. Multiple instances of the RTC function block can be created within one PLC program. Deviation of the RTC time from a reference time The way the system works means that the RTC time can differ from the reference time. The deviation depends on the PLC's cycle time, the value of the basic system ticks, and on the hardware being used. In order to avoid larger deviations the RTC instance should be synchronized cyclically (e.g. with a radio clock or with the local Windows system time). The local Windows system time you can be synchronized with a reference time via the SNTP protocol.

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    EN : BOOL;
    PDT : DATE_AND_TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `EN` | `BOOL` | （详见 PDF） |
| `PDT` | `DATE_AND_TIME` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q : BOOL;
    CDT : DATE_AND_TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | （详见 PDF） |
| `CDT` | `DATE_AND_TIME` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.79 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.79 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_RTC.xml`](../examples/P_Demo_RTC.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_RTC
VAR
    fbRTC : RTC;
    arg_EN : BOOL;
    arg_PDT : DATE_AND_TIME;
    out_Q : BOOL;
    out_CDT : DATE_AND_TIME;
END_VAR

fbRTC(
    EN := arg_EN,
    PDT := arg_PDT,
    Q => out_Q,
    CDT => out_CDT
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
