# FB_LicFileGetStorageInfo
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
| Example | [`examples/P_Demo_FB_LicFileGetStorageInfo.xml`](../examples/P_Demo_FB_LicFileGetStorageInfo.xml) |

---
## 1. 功能简述

The function block reads the StorageInfo of the license dongle and the file directory. The StorageInfo contains administrative data of the data carrier (such as capacity, number of free bytes, number of files,…) and an array of the individual file entries (name, size, attributes,… of the file).

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    nPort : UINT;
    bExecute : BOOL;
    dwPassCode : DWORD;
    tTimeout : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sNetId` | `T_AmsNetId` | （详见 PDF） |
| `nPort` | `UINT` | （详见 PDF） |
| `bExecute` | `BOOL` | （详见 PDF） |
| `dwPassCode` | `DWORD` | （详见 PDF） |
| `tTimeout` | `TIME` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrorId : UDINT;
    nFileEntries : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | （详见 PDF） |
| `bError` | `BOOL` | （详见 PDF） |
| `nErrorId` | `UDINT` | （详见 PDF） |
| `nFileEntries` | `UDINT` | （详见 PDF） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stStorageInfo : ST_LicStorageInfo;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stStorageInfo` | `ST_LicStorageInfo` | （详见 PDF） |

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.44 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.44 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_LicFileGetStorageInfo.xml`](../examples/P_Demo_FB_LicFileGetStorageInfo.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_LicFileGetStorageInfo
VAR
    fbFB_LicFileGetStorageInfo : FB_LicFileGetStorageInfo;
    arg_sNetId : T_AmsNetId;
    arg_nPort : UINT;
    arg_bExecute : BOOL;
    arg_dwPassCode : DWORD;
    arg_tTimeout : TIME;
    out_bBusy : BOOL;
    out_bError : BOOL;
    out_nErrorId : UDINT;
    out_nFileEntries : UDINT;
    io_stStorageInfo : ST_LicStorageInfo;
END_VAR

fbFB_LicFileGetStorageInfo(
    sNetId := arg_sNetId,
    nPort := arg_nPort,
    bExecute := arg_bExecute,
    dwPassCode := arg_dwPassCode,
    tTimeout := arg_tTimeout,
    bBusy => out_bBusy,
    bError => out_bError,
    nErrorId => out_nErrorId,
    nFileEntries => out_nFileEntries,
    stStorageInfo := io_stStorageInfo
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
