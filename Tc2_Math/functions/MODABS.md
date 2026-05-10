# MODABS
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Math` |
| Library Version | `1.3.3` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_MODABS.xml`](../examples/P_Demo_MODABS.xml) |

---
## 1. 功能简述

**无符号浮点取模**：返回 `lr_val` 在模数 `lr_mod` 内的非负值（NC 轴常用，返回 [0, lr_mod) 区间）。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION MODABS : LREAL
VAR_INPUT
    lr_val : LREAL;
    lr_mod : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `lr_val` | `LREAL` | 输入值 |
| `lr_mod` | `LREAL` | 模数范围 |

### 返回值

`LREAL` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- `MODABS(400.56, 360)` = `40.56`
- `MODABS(-400.56, 360)` = `319.44`

## 4. 错误码 / 返回值

返回 `LREAL` 类型的计算结果。无错误码。
## 5. 使用注意 / 常见坑

- NC 轴模运行设定位置用法：`ModuloSetPosition := MODABS(NcToPlc.fPosSoll, 360);`
- **和 LMOD 的区别**：MODABS 总是返回非负值；LMOD 保留输入符号。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MODABS.xml`](../examples/P_Demo_MODABS.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_MODABS
VAR
    rResult : LREAL;
    bRun    : BOOL;
END_VAR

IF bRun THEN
    rResult := MODABS(400.56, 360.0);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Math README`](../README.md) 同库其他条目

## 8. 待确认项

无。
