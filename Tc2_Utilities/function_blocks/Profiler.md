# Profiler
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
| Example | [`examples/P_Demo_Profiler.xml`](../examples/P_Demo_Profiler.xml) |

---
## 1. 功能简述

This functionality is not available in the PLC under Windows CE! The function block Profiler can be used to allow the execution time of PLC code to be measured. Internally, an instance of the GETCPUACCOUNT function block is called. The measurement is started by a rising edge at the START input, and is stopped by a falling edge. The measurements are evaluated internally, and are then made available for further processing at the DATA output in a structure of type PROFILERSTRUCT. In addition to the current, minimum and maximum execution times, the function block calculates the mean execution time for the last 10 measurements. The number of averaged measured values can be configured via the global variable MAX_AVERAGE_MEASURES [ }   379 ]  between 2 and 100. The times measured are given in microseconds. The output variable DATA.MeasureCycle [ }   360 ]  provides information about the number of measurements that have already been carried out. In order to measure the execution time for a specific segment of the PLC program the measurement must be started by a rising edge at the START input when the segment to be measured starts, and stopped by a falling edge at the START input at the end

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    START : BOOL;
    RESET : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `START` | `BOOL` | （详见 PDF） |
| `RESET` | `BOOL` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    DATA : PROFILERSTRUCT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | （详见 PDF） |
| `DATA` | `PROFILERSTRUCT` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.78 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.78 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Profiler.xml`](../examples/P_Demo_Profiler.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_Profiler
VAR
    fbProfiler : Profiler;
    arg_START : BOOL;
    arg_RESET : BOOL;
    out_BUSY : BOOL;
    out_DATA : PROFILERSTRUCT;
END_VAR

fbProfiler(
    START := arg_START,
    RESET := arg_RESET,
    BUSY => out_BUSY,
    DATA => out_DATA
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
