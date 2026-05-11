# FB_RegQueryValue
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
| Example | [`examples/P_Demo_FB_RegQueryValue.xml`](../examples/P_Demo_FB_RegQueryValue.xml) |

---
## 1. 功能简述

The system registry is a hierarchically structured tree. A node in the tree is referred to as a key. Each key may contain subkeys and data values. The function block "FB_RegQueryValue" can be used to read individual system registry values from the branch with the predefined handle HKEY_LOCAL_MACHINE . If successful cbData  data bytes are copied into the buffer with the address pData . The function block can be used to read any value types (e.g. REG_DWORD, REG_SZ) or binary data with unlimited byte length (REG_BINARY). Comment: The sSubKey  and sValueName  strings may not be empty! HKEY_LOCAL_MACHINE\SOFTWARE\ for 64 bit operating systems In a 64 bit Windows operating system all registry entries of and for 32 bit applications are not stored under HKEY_LOCAL_MACHINE\SOFTWARE\ but under HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\. The function blocks FB_RegQueryValue and FB_RegSetValue work automatically below the WOW6432Node folder like any 32 bit application when a registry entry below the SOFTWARE folder is selected. The redirection is performed automatically by the operating system.

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    sSubKey : T_MaxString;
    sValName : T_MaxString;
    cbData : UDINT;
    pData : POINTER TO BYTE;
    bExecute : BOOL;
    tTimeOut : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sNetId` | `T_AmsNetId` | （详见 PDF） |
| `sSubKey` | `T_MaxString` | （详见 PDF） |
| `sValName` | `T_MaxString` | （详见 PDF） |
| `cbData` | `UDINT` | （详见 PDF） |
| `pData` | `POINTER TO BYTE` | （详见 PDF） |
| `bExecute` | `BOOL` | （详见 PDF） |
| `tTimeOut` | `TIME` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    cbRead : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | （详见 PDF） |
| `bError` | `BOOL` | （详见 PDF） |
| `nErrId` | `UDINT` | （详见 PDF） |
| `cbRead` | `UDINT` | （详见 PDF） |

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.53 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.53 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_RegQueryValue.xml`](../examples/P_Demo_FB_RegQueryValue.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_RegQueryValue
VAR
    fbFB_RegQueryValue : FB_RegQueryValue;
    arg_sNetId : T_AmsNetId;
    arg_sSubKey : T_MaxString;
    arg_sValName : T_MaxString;
    arg_cbData : UDINT;
    arg_pData : POINTER TO BYTE;
    arg_bExecute : BOOL;
    arg_tTimeOut : TIME;
    out_bBusy : BOOL;
    out_bError : BOOL;
    out_nErrId : UDINT;
    out_cbRead : UDINT;
END_VAR

fbFB_RegQueryValue(
    sNetId := arg_sNetId,
    sSubKey := arg_sSubKey,
    sValName := arg_sValName,
    cbData := arg_cbData,
    pData := arg_pData,
    bExecute := arg_bExecute,
    tTimeOut := arg_tTimeOut,
    bBusy => out_bBusy,
    bError => out_bError,
    nErrId => out_nErrId,
    cbRead => out_cbRead
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
