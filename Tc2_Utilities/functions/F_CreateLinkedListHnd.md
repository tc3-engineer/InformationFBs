# F_CreateLinkedListHnd
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CreateLinkedListHnd.xml`](../examples/P_Demo_F_CreateLinkedListHnd.xml) |

---
## 1. 功能简述

**初始化链表句柄**：和 `F_CreateHashTableHnd` 类似但用于链表。供 `FB_LinkedListCtrl` 使用。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_CreateLinkedListHnd : BOOL
VAR_INPUT
    pEntries : POINTER TO T_LinkedListEntry; (* := 0 *)
    cbEntries : UDINT; (* := 0 *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pEntries` | `POINTER TO T_LinkedListEntry` | 条目数组指针 |
| `cbEntries` | `UDINT` | 数组字节数 |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    hList : T_HLINKEDLIST;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hList` | `T_HLINKEDLIST` | **初始化的链表句柄**（出参） |

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `BOOL`。

## 5. 使用注意 / 常见坑

- 调用一次即可。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CreateLinkedListHnd.xml`](../examples/P_Demo_F_CreateLinkedListHnd.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_CreateLinkedListHnd
VAR
    rResult : BOOL;
    bRun    : BOOL;
    ar : ARRAY[0..15] OF T_LinkedListEntry;
    h  : T_HLINKEDLIST;
END_VAR

IF bRun THEN
    rResult := F_CreateLinkedListHnd(pEntries := ADR(ar), cbEntries := SIZEOF(ar), hList := h);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
