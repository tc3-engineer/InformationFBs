# FB_BasicPID
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
| Example | [`examples/P_Demo_FB_BasicPID.xml`](../examples/P_Demo_FB_BasicPID.xml) |

---
## 1. 功能简述

The function block is a simple discretized PID element. Transfer function: Functional diagram:

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    fSetpointValue : LREAL;
    fActualValue : LREAL;
    bReset : BOOL;
    fCtrlCycleTime : LREAL;
    fKp : LREAL;
    fTn : LREAL;
    fTv : LREAL;
    fTd : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `fSetpointValue` | `LREAL` | （详见 PDF） |
| `fActualValue` | `LREAL` | （详见 PDF） |
| `bReset` | `BOOL` | （详见 PDF） |
| `fCtrlCycleTime` | `LREAL` | （详见 PDF） |
| `fKp` | `LREAL` | （详见 PDF） |
| `fTn` | `LREAL` | （详见 PDF） |
| `fTv` | `LREAL` | （详见 PDF） |
| `fTd` | `LREAL` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    fCtrlOutput : LREAL;
    nErrorStatus : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `fCtrlOutput` | `LREAL` | （详见 PDF） |
| `nErrorStatus` | `UINT` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.9 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.9 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_BasicPID.xml`](../examples/P_Demo_FB_BasicPID.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_BasicPID
VAR
    fbFB_BasicPID : FB_BasicPID;
    arg_fSetpointValue : LREAL;
    arg_fActualValue : LREAL;
    arg_bReset : BOOL;
    arg_fCtrlCycleTime : LREAL;
    arg_fKp : LREAL;
    arg_fTn : LREAL;
    arg_fTv : LREAL;
    arg_fTd : LREAL;
    out_fCtrlOutput : LREAL;
    out_nErrorStatus : UINT;
END_VAR

fbFB_BasicPID(
    fSetpointValue := arg_fSetpointValue,
    fActualValue := arg_fActualValue,
    bReset := arg_bReset,
    fCtrlCycleTime := arg_fCtrlCycleTime,
    fKp := arg_fKp,
    fTn := arg_fTn,
    fTv := arg_fTv,
    fTd := arg_fTd,
    fCtrlOutput => out_fCtrlOutput,
    nErrorStatus => out_nErrorStatus
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
