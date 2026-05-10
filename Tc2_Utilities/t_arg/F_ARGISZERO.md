# F_ARGISZERO
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
| Example | [`examples/P_Demo_F_ARGISZERO.xml`](../examples/P_Demo_F_ARGISZERO.xml) |

---
## 1. 功能简述

若 `T_Arg` 的任一成员（type/length/value 三者之一）为 0 或未初始化 → 返回 TRUE。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_ARGISZERO : BOOL
VAR_INPUT
    arg : T_Arg;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `arg` | `T_Arg` | 待检查的 T_Arg |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `F_ARGISZERO(a)`，返回 `BOOL`。
- 期望：`TRUE（未初始化）`

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码。

## 5. 使用注意 / 常见坑

- 可用作 未赋值 探测——刚声明的 T_Arg 变量返回 TRUE。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ARGISZERO.xml`](../examples/P_Demo_F_ARGISZERO.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_ARGISZERO
VAR
    rResult : BOOL;
    bRun    : BOOL;
    a : T_Arg;
END_VAR

IF bRun THEN
    rResult := F_ARGISZERO(a);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
