# DEG_TO_RAD
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_DEG_TO_RAD.xml`](../examples/P_Demo_DEG_TO_RAD.xml) |

---
## 1. 功能简述

**度 → 弧度**：返回 `ANGLE × π / 180`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION DEG_TO_RAD : LREAL
VAR_INPUT
    ANGLE : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ANGLE` | `LREAL` | 角度（度） |

### 返回值

`LREAL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `LREAL`。

## 5. 使用注意 / 常见坑

- 反向：`RAD_TO_DEG`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DEG_TO_RAD.xml`](../examples/P_Demo_DEG_TO_RAD.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_DEG_TO_RAD
VAR
    rResult : LREAL;
    bRun    : BOOL;
    deg : LREAL := 180.0;
END_VAR

IF bRun THEN
    rResult := DEG_TO_RAD(deg);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
