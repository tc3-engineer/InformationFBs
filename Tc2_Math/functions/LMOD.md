# LMOD
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
| Example | [`examples/P_Demo_LMOD.xml`](../examples/P_Demo_LMOD.xml) |

---
## 1. 功能简述

**带符号浮点取模**：返回 `lr_Value mod lr_Arg`，结果保留 `lr_Value` 符号、可为非整数。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LMOD : LREAL
VAR_INPUT
    lr_Value : LREAL;
    lr_Arg : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `lr_Value` | `LREAL` | 输入值 |
| `lr_Arg` | `LREAL` | 模数范围 |

### 返回值

`LREAL` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- `LMOD(400.56, 360)` = `40.56`
- `LMOD(-400.56, 360)` = `-40.56`

## 4. 错误码 / 返回值

返回 `LREAL` 类型的计算结果。无错误码。
## 5. 使用注意 / 常见坑

- **与 `MOD` 的区别**：`MOD` 只接受整数；LMOD 接受浮点。
- **与 `MODABS` 的区别**：LMOD 保留符号；`MODABS` 取绝对值（NC 轴常用 MODABS）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LMOD.xml`](../examples/P_Demo_LMOD.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_LMOD
VAR
    rResult : LREAL;
    bRun    : BOOL;
END_VAR

IF bRun THEN
    rResult := LMOD(400.56, 360.0);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Math README`](../README.md) 同库其他条目

## 8. 待确认项

无。
