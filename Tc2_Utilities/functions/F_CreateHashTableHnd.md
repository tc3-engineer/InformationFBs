# F_CreateHashTableHnd
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
| Example | [`examples/P_Demo_F_CreateHashTableHnd.xml`](../examples/P_Demo_F_CreateHashTableHnd.xml) |

---
## 1. 功能简述

**初始化哈希表句柄**：把 `T_HashTableEntry` 数组绑定到句柄上，供 `FB_HashTableCtrl` 使用。返回 TRUE = 成功。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_CreateHashTableHnd : BOOL
VAR_INPUT
    pEntries : POINTER TO T_HashTableEntry := 0;
    cbEntries : UDINT := 0;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pEntries` | `POINTER TO T_HashTableEntry` | 条目数组指针（ADR） |
| `cbEntries` | `UDINT` | 数组字节数（SIZEOF） |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    hTable : T_HHASHTABLE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hTable` | `T_HHASHTABLE` | **初始化的句柄**（出参） |

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `BOOL`。

## 5. 使用注意 / 常见坑

- 调用一次即可；之后由 `FB_HashTableCtrl` 操作。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CreateHashTableHnd.xml`](../examples/P_Demo_F_CreateHashTableHnd.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_CreateHashTableHnd
VAR
    rResult : BOOL;
    bRun    : BOOL;
    ar : ARRAY[0..15] OF T_HashTableEntry;
    h  : T_HHASHTABLE;
END_VAR

IF bRun THEN
    rResult := F_CreateHashTableHnd(pEntries := ADR(ar), cbEntries := SIZEOF(ar), hTable := h);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
