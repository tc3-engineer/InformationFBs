# F_ARGCPY
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
| Example | [`examples/P_Demo_F_ARGCPY.xml`](../examples/P_Demo_F_ARGCPY.xml) |

---
## 1. 功能简述

把一个 `T_Arg` 的值复制到另一个，返回成功复制的字节数。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_ARGCPY : UDINT
VAR_INPUT
    typeSafe : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `typeSafe` | `BOOL` | TRUE = 类型安全；FALSE = 不限 |

### 返回值

`UDINT` —— 函数计算结果。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    dest : T_Arg;
    src : T_Arg;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `dest` | `T_Arg` | 复制目标 |
| `src` | `T_Arg` | 复制源 |

## 3. 行为说明

- 调用 `F_ARGCPY(TRUE)`，返回 `UDINT`。
- 期望：`成功字节数（如 8）`

## 4. 错误码 / 返回值

返回 `UDINT`。无独立错误码。

## 5. 使用注意 / 常见坑

- 返回 0 = 参数无效（dest/src 的 type/length/value 任一为 0）。
- 返回 > 0 = 复制成功的字节数。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ARGCPY.xml`](../examples/P_Demo_F_ARGCPY.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_ARGCPY
VAR
    rResult : UDINT;
    bRun    : BOOL;
    a, b : T_Arg;
END_VAR

IF bRun THEN
    rResult := F_ARGCPY(TRUE, dest := a, src := b);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
