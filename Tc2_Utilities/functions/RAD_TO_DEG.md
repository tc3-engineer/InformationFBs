# RAD_TO_DEG
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
| Example | [`examples/P_Demo_RAD_TO_DEG.xml`](../examples/P_Demo_RAD_TO_DEG.xml) |

---
## 1. 功能简述

**弧度 → 度**：返回 `ANGLE × 180 / π`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION RAD_TO_DEG : LREAL
VAR_INPUT
    ANGLE : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ANGLE` | `LREAL` | 弧度 |

### 返回值

`LREAL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `LREAL`。

## 5. 使用注意 / 常见坑

- 反向：`DEG_TO_RAD`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_RAD_TO_DEG.xml`](../examples/P_Demo_RAD_TO_DEG.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_RAD_TO_DEG
VAR
    rResult : LREAL;
    bRun    : BOOL;
    rad : LREAL := 3.14159265;
END_VAR

IF bRun THEN
    rResult := RAD_TO_DEG(rad);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
