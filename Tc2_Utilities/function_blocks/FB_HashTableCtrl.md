# FB_HashTableCtrl
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
| Example | [`examples/P_Demo_FB_HashTableCtrl.xml`](../examples/P_Demo_FB_HashTableCtrl.xml) |

---
## 1. 功能简述

The hash table can be used to find an individual data element quickly among a larger number of data elements. The data objects must have a unique key. The key enables the data objects to be identified unambiguously and found quickly in the table. The function block FB_HashTableCtrl can be used to realize a simple hash table in the PLC project. The hashing with chaining (separate chaining) procedure is used. The maximum number of data elements cannot be changed at runtime and must be specified in advance. Adding/removing/finding of data elements is controlled through action calls. The function block features the following tasks: • A_Add  (adds a new data element to the table (key/value). If an element with the same key already exists, it is overwritten! ) • A_GetFirst  (reads the first table data element. If successful, getValue  supplies the associated value.) • A_GetNext  (reads the next table data element. The address: putPosPtr  must point to the previous data element!) • A_Lookup  (looks for a data element matching the key. If successful, getValue  supplies the associated value.) • A_Remove  (removes a data element matching the key.) • A_RemoveAll  (removes all data elements) •

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    key : DWORD;
    putValue : PVOID;
    putPosPtr : POINTER TO T_HashTableEntry;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `key` | `DWORD` | （详见 PDF） |
| `putValue` | `PVOID` | （详见 PDF） |
| `putPosPtr` | `POINTER TO T_HashTableEntry` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bOk : BOOL;
    getValue : PVOID;
    getPosPtr : POINTER TO T_HashTableEntry;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bOk` | `BOOL` | （详见 PDF） |
| `getValue` | `PVOID` | （详见 PDF） |
| `getPosPtr` | `POINTER TO T_HashTableEntry` | （详见 PDF） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    hTable : T_HHASHTABLE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hTable` | `T_HHASHTABLE` | （详见 PDF） |

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.39 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.39 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_HashTableCtrl.xml`](../examples/P_Demo_FB_HashTableCtrl.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_HashTableCtrl
VAR
    fbFB_HashTableCtrl : FB_HashTableCtrl;
    arg_key : DWORD;
    arg_putValue : PVOID;
    arg_putPosPtr : POINTER TO T_HashTableEntry;
    out_bOk : BOOL;
    out_getValue : PVOID;
    out_getPosPtr : POINTER TO T_HashTableEntry;
    io_hTable : T_HHASHTABLE;
END_VAR

fbFB_HashTableCtrl(
    key := arg_key,
    putValue := arg_putValue,
    putPosPtr := arg_putPosPtr,
    bOk => out_bOk,
    getValue => out_getValue,
    getPosPtr => out_getPosPtr,
    hTable := io_hTable
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
