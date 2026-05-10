# RealIsNaN
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `FLOAT functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_RealIsNaN.xml`](../examples/P_Demo_RealIsNaN.xml) |

---
## 1. 功能简述

测试 REAL 是否为 NaN。返回 TRUE 表示是 NaN。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION RealIsNaN : BOOL
VAR_INPUT
    x : REFERENCE TO REAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `x` | `REFERENCE TO REAL` | 待测值（按引用） |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。
## 3. 行为说明

- 调用 `RealIsNaN(rX)`，返回 `BOOL` 类型结果。
- 期望：`FALSE（rX=3.14）`

## 4. 错误码 / 返回值

返回 `BOOL`。无错误码。

## 5. 使用注意 / 常见坑

- REAL 单精度版。
- NaN 注意事项见同库 `LrealIsNaN`（包含 CAUTION/NOTICE 详述）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_RealIsNaN.xml`](../examples/P_Demo_RealIsNaN.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_RealIsNaN
VAR
    bResult : BOOL;
    bRun    : BOOL;
    rX : REAL;
END_VAR

rX := 3.14;
IF bRun THEN
    bResult := RealIsNaN(rX);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
