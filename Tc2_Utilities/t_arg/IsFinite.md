# IsFinite
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
| Example | [`examples/P_Demo_IsFinite.xml`](../examples/P_Demo_IsFinite.xml) |

---
## 1. 功能简述

检查 `REAL`/`LREAL` 的内存格式是否符合 IEEE 754 有限数。返回 TRUE = 有限（INF < x < +INF），FALSE = ±∞ 或 NaN。

**为什么要这函数**：在 PC（x86/x64）上对 NaN/INF 做转换会触发 **FPU exception** → PLC runtime 停止。先用 IsFinite 守门可避免崩溃。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION IsFinite : BOOL
VAR_INPUT
    x : T_Arg;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `x` | `T_Arg` | 对 REAL/LREAL 变量的 T_Arg 包装 |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `IsFinite(F_LREAL(fX))`，返回 `BOOL`。
- 期望：`TRUE`

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码。

## 5. 使用注意 / 常见坑

- **调用必须配 typed wrapper**：`IsFinite(F_LREAL(fX))` 或 `IsFinite(F_REAL(rX))`——直接传 T_Arg 不可。
- INF 由数学运算溢出产生（如 `fX := fX * 2;` 反复迭代）；NaN 通常由内存非法写入产生（MEMSET/MEMCPY 误写浮点变量）。
- **注意陷阱**：IsFinite 只检查存储格式，不检查数值范围——`bigFloat=3.0E100` 是有效 LREAL，但转 INT 仍会触发 FPU 异常（PDF Example 2）。
- 见相关：`LrealIsFinite`（直接接受 LREAL，无需 wrapper，更现代）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IsFinite.xml`](../examples/P_Demo_IsFinite.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_IsFinite
VAR
    rResult : BOOL;
    bRun    : BOOL;
    fX : LREAL := 3.14;
END_VAR

IF bRun THEN
    rResult := IsFinite(F_LREAL(fX));
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
