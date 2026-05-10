# F_ARGCMP
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `T_Arg help functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_F_ARGCMP.xml`](../examples/P_Demo_F_ARGCMP.xml) |

---
## 1. 功能简述

比较两个 `T_Arg`，返回比较结果（基于第一处不同的字节：类型/长度/值）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_ARGCMP : DINT
VAR_INPUT
    typeSafe : BOOL;
    arg1 : T_Arg;
    arg2 : T_Arg;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `typeSafe` | `BOOL` | TRUE = 类型安全比较；FALSE = 跨类型比较 |
| `arg1` | `T_Arg` | 第一个比较项 |
| `arg2` | `T_Arg` | 第二个比较项 |

### 返回值

`DINT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `F_ARGCMP(TRUE, a, b)`，返回 `DINT`。
- 期望：`0（同值同类型）`

## 4. 错误码 / 返回值

返回 `DINT`。无独立错误码。

## 5. 使用注意 / 常见坑

- 返回值含义（PDF 原表）：-3 = arg1 长度小于 arg2；-2 = arg1 类型小于 arg2；-1 = arg1 值小于 arg2；0 = 相等；1/2/3 = 反向（值/类型/长度大于）。
- `typeSafe = TRUE` 时不同类型直接判定不等。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ARGCMP.xml`](../examples/P_Demo_F_ARGCMP.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_ARGCMP
VAR
    rResult : DINT;
    bRun    : BOOL;
    a, b : T_Arg;
END_VAR

IF bRun THEN
    rResult := F_ARGCMP(TRUE, a, b);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
