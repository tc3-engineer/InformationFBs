# F_LARGE
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
| Example | [`examples/P_Demo_F_LARGE.xml`](../examples/P_Demo_F_LARGE.xml) |

---
## 1. 功能简述

**typed wrapper**：把一个 `T_LARGE_INTEGER` 变量包装成 `T_Arg` 结构（含 type/length/value 三元组），供 `F_ARGCMP`/`F_ARGCPY`/`IsFinite` 等通用工具消费。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_LARGE : T_Arg
```

无 VAR_INPUT。

### 返回值

`T_Arg` —— 函数计算结果。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    in : T_LARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `T_LARGE_INTEGER` | 待包装的 T_LARGE_INTEGER 变量 |

## 3. 行为说明

- 调用 `F_LARGE(v)`，返回 `T_Arg`。

## 4. 错误码 / 返回值

返回 `T_Arg`。无独立错误码。

## 5. 使用注意 / 常见坑

- **VAR_IN_OUT** 风格：传变量本身（不是值），FB 不复制，只读出地址/长度。
- 返回 `T_Arg` 结构（见 Tc2_Utilities Data types）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_LARGE.xml`](../examples/P_Demo_F_LARGE.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_LARGE
VAR
    rResult : T_Arg;
    bRun    : BOOL;
    v : T_LARGE_INTEGER;
END_VAR

IF bRun THEN
    rResult := F_LARGE(in := v);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
