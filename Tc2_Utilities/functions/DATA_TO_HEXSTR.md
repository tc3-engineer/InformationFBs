# DATA_TO_HEXSTR
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
| Example | [`examples/P_Demo_DATA_TO_HEXSTR.xml`](../examples/P_Demo_DATA_TO_HEXSTR.xml) |

---
## 1. 功能简述

**二进制数据 → HEX 字符串**：返回 hex 文本。`cbData > 85` 时结果末尾加 `.` 并中断转换。`pData` 或 `cbData` 为 0 → 返回空字符串。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION DATA_TO_HEXSTR : T_MaxString
VAR_INPUT
    pData : POINTER TO BYTE;
    cbData : UDINT(0..85);
    bLoCase : BOOL := FALSE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pData` | `POINTER TO BYTE` | 源数据指针 |
| `cbData` | `UDINT(0..85)` | 字节数（**最大 85**） |
| `bLoCase` | `BOOL` | TRUE = 小写 |

### 返回值

`T_MaxString` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `T_MaxString`。

## 5. 使用注意 / 常见坑

- **单次最大 85 字节**——更长用 `DATA_TO_HEXSTR2`（Round 6）。
- **字节序提示**：小端格式（Intel）下 DWORD/LWORD 的字节顺序在 hex 输出中相反。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DATA_TO_HEXSTR.xml`](../examples/P_Demo_DATA_TO_HEXSTR.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_DATA_TO_HEXSTR
VAR
    rResult : T_MaxString;
    bRun    : BOOL;
    ar : ARRAY[0..3] OF BYTE := [16#AB, 16#CD, 16#01, 16#23];
END_VAR

IF bRun THEN
    rResult := DATA_TO_HEXSTR(ADR(ar), SIZEOF(ar), FALSE);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
