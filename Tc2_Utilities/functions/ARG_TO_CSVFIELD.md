# ARG_TO_CSVFIELD
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
| Example | [`examples/P_Demo_ARG_TO_CSVFIELD.xml`](../examples/P_Demo_ARG_TO_CSVFIELD.xml) |

---
## 1. 功能简述

**PLC 变量 → CSV 字段（byte buffer）**：把任意 PLC 变量转为 CSV 数据字段写入字节缓冲。返回成功字节数；0 = 错误。常配合 `FB_CSVMemBufferWriter`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION ARG_TO_CSVFIELD : UDINT
VAR_INPUT
    in : T_Arg;
    bQM : BOOL;
    pOutput : POINTER TO BYTE;
    cbOutput : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `T_Arg` | 源 PLC 变量（通过 F_<type> 包装为 T_Arg） |
| `bQM` | `BOOL` | TRUE = 输出加双引号包围 |
| `pOutput` | `POINTER TO BYTE` | 输出字节缓冲指针 |
| `cbOutput` | `UDINT` | 输出缓冲字节数 |

### 返回值

`UDINT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `UDINT`。

## 5. 使用注意 / 常见坑

- **优于 STRING_TO_CSVFIELD**：能处理含二进制数据的 PLC 变量。
- 单引号 → 双引号转义。
- 用 `F_<type>(value)` 包装变量为 T_Arg。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ARG_TO_CSVFIELD.xml`](../examples/P_Demo_ARG_TO_CSVFIELD.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_ARG_TO_CSVFIELD
VAR
    rResult : UDINT;
    bRun    : BOOL;
    v : DINT := 42;
    sOut : STRING(255);
END_VAR

IF bRun THEN
    rResult := ARG_TO_CSVFIELD(F_DINT(v), FALSE, ADR(sOut), SIZEOF(sOut));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
