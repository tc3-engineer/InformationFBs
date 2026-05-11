# FB_MemBufferSplit
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
| Example | [`examples/P_Demo_FB_MemBufferSplit.xml`](../examples/P_Demo_FB_MemBufferSplit.xml) |

---
## 1. 功能简述

This function block splits a memory area (data buffer) into several smaller segments of certain maximum length as required. The function block returns a smaller partial segment, if the length of the last segment is smaller than required.

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    eCmd : E_EnumCmdType := eEnumCmd_First;
    pBuffer : POINTER TO BYTE;
    cbBuffer : UDINT;
    cbSize : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `eCmd` | `E_EnumCmdType` | （详见 PDF） |
| `pBuffer` | `POINTER TO BYTE` | （详见 PDF） |
| `cbBuffer` | `UDINT` | （详见 PDF） |
| `cbSize` | `UDINT` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bOk : BOOL;
    pSegment : POINTER TO BYTE;
    cbSegment : UDINT;
    bEOS : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bOk` | `BOOL` | （详见 PDF） |
| `pSegment` | `POINTER TO BYTE` | （详见 PDF） |
| `cbSegment` | `UDINT` | （详见 PDF） |
| `bEOS` | `BOOL` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.49 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.49 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_MemBufferSplit.xml`](../examples/P_Demo_FB_MemBufferSplit.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_MemBufferSplit
VAR
    fbFB_MemBufferSplit : FB_MemBufferSplit;
    arg_eCmd : E_EnumCmdType;
    arg_pBuffer : POINTER TO BYTE;
    arg_cbBuffer : UDINT;
    arg_cbSize : UDINT;
    out_bOk : BOOL;
    out_pSegment : POINTER TO BYTE;
    out_cbSegment : UDINT;
    out_bEOS : BOOL;
END_VAR

fbFB_MemBufferSplit(
    eCmd := arg_eCmd,
    pBuffer := arg_pBuffer,
    cbBuffer := arg_cbBuffer,
    cbSize := arg_cbSize,
    bOk => out_bOk,
    pSegment => out_pSegment,
    cbSegment => out_cbSegment,
    bEOS => out_bEOS
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
