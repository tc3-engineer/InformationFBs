# F_GetClassIdVersioned
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
| Example | [`examples/P_Demo_F_GetClassIdVersioned.xml`](../examples/P_Demo_F_GetClassIdVersioned.xml) |

---
## 1. 功能简述

**C++ 模块带版本号的 Class ID 生成**：根据 `sLibraryId` 与 `clsId` 计算版本化 Class ID（通过 `clsIdVersioned` 引用出参）。仅用于版本化 C++ 项目。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_GetClassIdVersioned : BOOL
VAR_INPUT
    sLibraryId : STRING(255); // 'vendorName|libraryName|libraryVersion' (e.g. 'C++ Module Vendor|IncrementerCpp|0.0.0.1' )
    clsId : CLSID;
    clsIdVersioned : REFERENCE TO CLSID;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sLibraryId` | `STRING(255)` | 形如 `'vendorName|libraryName|libraryVersion'` |
| `clsId` | `CLSID` | 原 Class ID |
| `clsIdVersioned` | `REFERENCE TO CLSID` | **出参**：版本化 Class ID（按引用） |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `BOOL`。

## 5. 使用注意 / 常见坑

- **PDF VAR_INPUT 中 `sLibraryId : STRING(255),` 末尾有多余逗号**——这是 PDF 排版瑕疵，文档逐字保留。
- `sLibraryId` 格式：`vendorName|libraryName|libraryVersion`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetClassIdVersioned.xml`](../examples/P_Demo_F_GetClassIdVersioned.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_GetClassIdVersioned
VAR
    rResult : BOOL;
    bRun    : BOOL;
    id : CLSID;
    idv : CLSID;
END_VAR

IF bRun THEN
    rResult := F_GetClassIdVersioned('vendor|lib|0.0.0.1', id, idv);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
