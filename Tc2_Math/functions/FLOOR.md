# FLOOR
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
| Example | [`examples/P_Demo_FLOOR.xml`](../examples/P_Demo_FLOOR.xml) |

---
## 1. 功能简述

**向下取整**：返回不大于输入的最大整数（结果为 LREAL 类型，不受 INT 范围限制）。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FLOOR : LREAL
VAR_INPUT
    lr_in : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `lr_in` | `LREAL` | LREAL 类型的输入参数 |

### 返回值

`LREAL` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- `FLOOR(2.8)` = `2`
- `FLOOR(-2.8)` = `-3`

## 4. 错误码 / 返回值

返回 `LREAL` 类型的计算结果。无错误码。
## 5. 使用注意 / 常见坑

- 返回 `LREAL`，不受 INT 范围限制。
- **符号无关**：始终向 -∞ 方向取，所以 FLOOR(-2.8) = -3。
- 对比：`CEIL` 向上、`LTRUNC` 朝零截断、`TO_LINT` 四舍五入。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FLOOR.xml`](../examples/P_Demo_FLOOR.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FLOOR
VAR
    rResult : LREAL;
    bRun    : BOOL;
END_VAR

IF bRun THEN
    rResult := FLOOR(2.8);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Math README`](../README.md) 同库其他条目

## 8. 待确认项

无。
