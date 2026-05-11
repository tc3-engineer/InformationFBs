# CSVFIELD_TO_ARG
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
| Example | [`examples/P_Demo_CSVFIELD_TO_ARG.xml`](../examples/P_Demo_CSVFIELD_TO_ARG.xml) |

---
## 1. 功能简述

**CSV 字段（byte buffer）→ PLC 变量**：解析 CSV 字段写入目标变量。返回成功字节数；0 = 错误。常配合 `FB_CSVMemBufferReader`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION CSVFIELD_TO_ARG : UDINT
VAR_INPUT
    pInput : POINTER TO BYTE;
    cbInput : UDINT;
    bQM : BOOL;
    out : T_Arg;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pInput` | `POINTER TO BYTE` | 源字节缓冲指针（CSV 字段） |
| `cbInput` | `UDINT` | 源字节数 |
| `bQM` | `BOOL` | TRUE = 去除外层双引号 |
| `out` | `T_Arg` | **输出**：目标 PLC 变量（通过 F_<type> 包装） |

### 返回值

`UDINT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `UDINT`。

## 5. 使用注意 / 常见坑

- **注意**：PDF 把目标变量 `out` 列在 VAR_INPUT（用 T_Arg 包装传递地址+类型），不是 VAR_OUTPUT。
- **优于 CSVFIELD_TO_STRING**：能解析含二进制数据的字段。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CSVFIELD_TO_ARG.xml`](../examples/P_Demo_CSVFIELD_TO_ARG.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_CSVFIELD_TO_ARG
VAR
    rResult : UDINT;
    bRun    : BOOL;
    v : DINT;
    sCsv : STRING := '42';
END_VAR

IF bRun THEN
    rResult := CSVFIELD_TO_ARG(ADR(sCsv), LEN(sCsv), FALSE, F_DINT(v));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
