# FB_AddRouteEntry
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
| Example | [`examples/P_Demo_FB_AddRouteEntry.xml`](../examples/P_Demo_FB_AddRouteEntry.xml) |

---
## 1. 功能简述

The function block can be used to add a new AMS router connection (remote route) to a TwinCAT system. AMS router connection list Both communication partners of an AMS router connection have an AMS router connection list. These lists contain AMS router connections. An AMS router connection is functional when both communication partners have entered each other in their respective connection list. When using the function block, only the list of the communication partner is extended.

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID : T_AmsNetID;
    stRoute : ST_AmsRouteEntry;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sNetID` | `T_AmsNetID` | （详见 PDF） |
| `stRoute` | `ST_AmsRouteEntry` | （详见 PDF） |
| `bExecute` | `BOOL` | （详见 PDF） |
| `tTimeout` | `TIME` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | （详见 PDF） |
| `bError` | `BOOL` | （详见 PDF） |
| `nErrId` | `UDINT` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.6 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.6 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_AddRouteEntry.xml`](../examples/P_Demo_FB_AddRouteEntry.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_AddRouteEntry
VAR
    fbFB_AddRouteEntry : FB_AddRouteEntry;
    arg_sNetID : T_AmsNetID;
    arg_stRoute : ST_AmsRouteEntry;
    arg_bExecute : BOOL;
    arg_tTimeout : TIME;
    out_bBusy : BOOL;
    out_bError : BOOL;
    out_nErrId : UDINT;
END_VAR

fbFB_AddRouteEntry(
    sNetID := arg_sNetID,
    stRoute := arg_stRoute,
    bExecute := arg_bExecute,
    tTimeout := arg_tTimeout,
    bBusy => out_bBusy,
    bError => out_bError,
    nErrId => out_nErrId
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
