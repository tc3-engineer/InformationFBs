# DCF77_TIME_EX
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
| Example | [`examples/P_Demo_DCF77_TIME_EX.xml`](../examples/P_Demo_DCF77_TIME_EX.xml) |

---
## 1. 功能简述

The function block "DCF77_TIME_EX" can be used to decode the DCF-77 radio clock signal. In contrast to the " DCF77_TIME [ }   34 ] " function block, this block checks two consecutive telegrams for plausibility as standard. A rising edge at the RUN input starts the decoding process, which continues as long as the RUN input remains set. In the worst case synchronization of the function block takes up to one minute and two further minutes for decoding data for the next minute. During this time, the missing 59th second marker is waited for. Internally the function block is sampling the DCF-77 signal. In order to be able to sample the edges without error the function block should be called once in each PLC cycle. Satisfactory results can be obtained with a cycle time of <= 25 ms. In case of a missing or faulty DCF-77 signal, the ERR output is set to TRUE and a corresponding error code is set at the ERRID output. The ERR and ERRID outputs are reset the next time a correct signal is received. Some receivers provide an inverted DCF-77 signal. In such cases the signal must first be inverted before being passed to the DCF_PULSE input. When operating without errors, the current time is update

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    DCF_PULSE : BOOL;
    RUN : BOOL;
    TLP : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `DCF_PULSE` | `BOOL` | （详见 PDF） |
| `RUN` | `BOOL` | （详见 PDF） |
| `TLP` | `TIME` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
    ERRCNT : UDINT;
    READY : BOOL;
    CDT : DATE_AND_TIME;
    DOW : BYTE(1..7);
    TZI : E_TimeZoneID;
    ADVTZI : BOOL;
    LEAPSEC : BOOL;
    RAWDT : ARRAY[0..60] OF BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | （详见 PDF） |
| `ERR` | `BOOL` | （详见 PDF） |
| `ERRID` | `UDINT` | （详见 PDF） |
| `ERRCNT` | `UDINT` | （详见 PDF） |
| `READY` | `BOOL` | （详见 PDF） |
| `CDT` | `DATE_AND_TIME` | （详见 PDF） |
| `DOW` | `BYTE(1..7)` | （详见 PDF） |
| `TZI` | `E_TimeZoneID` | （详见 PDF） |
| `ADVTZI` | `BOOL` | （详见 PDF） |
| `LEAPSEC` | `BOOL` | （详见 PDF） |
| `RAWDT` | `ARRAY[0..60] OF BOOL` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.4 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.4 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DCF77_TIME_EX.xml`](../examples/P_Demo_DCF77_TIME_EX.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_DCF77_TIME_EX
VAR
    fbDCF77_TIME_EX : DCF77_TIME_EX;
    arg_DCF_PULSE : BOOL;
    arg_RUN : BOOL;
    arg_TLP : TIME;
    out_BUSY : BOOL;
    out_ERR : BOOL;
    out_ERRID : UDINT;
    out_ERRCNT : UDINT;
    out_READY : BOOL;
    out_CDT : DATE_AND_TIME;
    out_DOW : BYTE(1..7);
    out_TZI : E_TimeZoneID;
    out_ADVTZI : BOOL;
    out_LEAPSEC : BOOL;
    out_RAWDT : ARRAY[0..60] OF BOOL;
END_VAR

fbDCF77_TIME_EX(
    DCF_PULSE := arg_DCF_PULSE,
    RUN := arg_RUN,
    TLP := arg_TLP,
    BUSY => out_BUSY,
    ERR => out_ERR,
    ERRID => out_ERRID,
    ERRCNT => out_ERRCNT,
    READY => out_READY,
    CDT => out_CDT,
    DOW => out_DOW,
    TZI => out_TZI,
    ADVTZI => out_ADVTZI,
    LEAPSEC => out_LEAPSEC,
    RAWDT => out_RAWDT
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
