# MODTURNS
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
| Example | [`examples/P_Demo_MODTURNS.xml`](../examples/P_Demo_MODTURNS.xml) |

---
## 1. 功能简述

**带符号模数整数圈数**：返回输入值在模数范围内已经过的完整圈数（模 periods）。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION MODTURNS : DINT
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

`DINT` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- `MODTURNS(800.56, 360)` = `2`
- `MODTURNS(-400.56, 360)` = `-2`

## 4. 错误码 / 返回值

返回 `DINT` 类型的计算结果。无错误码。
## 5. 使用注意 / 常见坑

- 返回 `DINT`——若结果超出 DINT 范围，行为未定义（PDF 警告）。
- NC 轴用法：`ModuloSetTurns := MODTURNS(NcToPlc.fPosSoll, 360);` 计算模轴已转的圈数。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MODTURNS.xml`](../examples/P_Demo_MODTURNS.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_MODTURNS
VAR
    rResult : DINT;
    bRun    : BOOL;
END_VAR

IF bRun THEN
    rResult := MODTURNS(800.56, 360.0);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Math README`](../README.md) 同库其他条目

## 8. 待确认项

无。
