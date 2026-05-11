# FB_LinkedListCtrl
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
| Example | [`examples/P_Demo_FB_LinkedListCtrl.xml`](../examples/P_Demo_FB_LinkedListCtrl.xml) |

---
## 1. 功能简述

The function block FB_LinkedListCtrl can be used to implement a linked list in the PLC project. A double- linked list is created. A linked list allows values (known as nodes) to be stored. It is possible to iterate the list from the back to the front or the other way. Nodes can quickly be added or deleted. It is not possible to change the maximum number of nodes at runtime; it must be specified before compiling. An array of type: T_LinkedListEntry  is used as a "node pool". Adding/removing/finding of nodes is controlled through action calls. The function block features the following tasks: • A_AddHeadValue  (adds a new node with the value: putValue  to the top of the list. The same value can be added more than once. If successful, getPosPtr  returns the address while getValue  returns the value of the new node.) • A_AddTailValue  (adds a new node with the value: putValue  to the end of the list. The same value can be added more than once. If successful, getPosPtr  returns the address while getValue  returns the value of the new node.) • A_FindNext  (searches for the next node (relative to putPosPtr ) whose value is the same as putValue . If successful, getPosPtr  returns the addres

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    putValue : PVOID;
    putPosPtr : POINTER TO T_LinkedListEntry;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `putValue` | `PVOID` | （详见 PDF） |
| `putPosPtr` | `POINTER TO T_LinkedListEntry` | （详见 PDF） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bOk : BOOL;
    getValue : PVOID;
    getPosPtr : POINTER TO T_LinkedListEntry;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bOk` | `BOOL` | （详见 PDF） |
| `getValue` | `PVOID` | （详见 PDF） |
| `getPosPtr` | `POINTER TO T_LinkedListEntry` | （详见 PDF） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    hList : T_HLINKEDLIST;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hList` | `T_HLINKEDLIST` | （详见 PDF） |

## 3. 行为说明

- 见上方功能简述。
- 详细行为（时序、错误码、状态机）请对照 PDF 第 3.46 节。

## 4. 错误码 / 返回值

出错时通常 `bError`/`ERR` = TRUE，`nErrorId`/`nErrId`/`ERRID` 给出错误号（具体码表见 InfoSys 在线文档，⚠️ 待人工补全）。

## 5. 使用注意 / 常见坑

- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 已逐字从 PDF 抽取并通过 `verify_doc.py` 自检。
- 描述句、时序行为、错误码表等细节请以 PDF 第 3.46 节为准（⚠️ 待人工细化）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_LinkedListCtrl.xml`](../examples/P_Demo_FB_LinkedListCtrl.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_LinkedListCtrl
VAR
    fbFB_LinkedListCtrl : FB_LinkedListCtrl;
    arg_putValue : PVOID;
    arg_putPosPtr : POINTER TO T_LinkedListEntry;
    out_bOk : BOOL;
    out_getValue : PVOID;
    out_getPosPtr : POINTER TO T_LinkedListEntry;
    io_hList : T_HLINKEDLIST;
END_VAR

fbFB_LinkedListCtrl(
    putValue := arg_putValue,
    putPosPtr := arg_putPosPtr,
    bOk => out_bOk,
    getValue => out_getValue,
    getPosPtr => out_getPosPtr,
    hList := io_hList
);
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 详细描述/时序/错误码表待人工细化（auto-gen 阶段只确保 VAR 区与 PDF 一致）。
