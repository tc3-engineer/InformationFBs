# FB_GetLocalAmsNetId
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
| Example | [`examples/P_Demo_FB_GetLocalAmsNetId.xml`](../examples/P_Demo_FB_GetLocalAmsNetId.xml) |

---
## 1. 功能简述

This function block can be used to read the network address (AmsNetID) of a local TwinCAT PC.

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute : BOOL;
    tTimeOut : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bExecute` | `BOOL` | （详见 PDF） |
| `tTimeOut` | `TIME` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    AddrString : T_AmsNetId;
    AddrBytes : T_AmsNetIdArr;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | （详见 PDF） |
| `bError` | `BOOL` | （详见 PDF） |
| `nErrId` | `UDINT` | （详见 PDF） |
| `AddrString` | `T_AmsNetId` | （详见 PDF） |
| `AddrBytes` | `T_AmsNetIdArr` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.33 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.33 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetLocalAmsNetId.xml`](../examples/P_Demo_FB_GetLocalAmsNetId.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_GetLocalAmsNetId
VAR
    fbFB_GetLocalAmsNetId : FB_GetLocalAmsNetId;
    arg_bExecute : BOOL;
    arg_tTimeOut : TIME;
    out_bBusy : BOOL;
    out_bError : BOOL;
    out_nErrId : UDINT;
    out_AddrString : T_AmsNetId;
    out_AddrBytes : T_AmsNetIdArr;
END_VAR

fbFB_GetLocalAmsNetId(
    bExecute := arg_bExecute,
    tTimeOut := arg_tTimeOut,
    bBusy => out_bBusy,
    bError => out_bError,
    nErrId => out_nErrId,
    AddrString => out_AddrString,
    AddrBytes => out_AddrBytes
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
