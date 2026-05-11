# ROUTETRANSPORT_TO_STRING
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
| Example | [`examples/P_Demo_ROUTETRANSPORT_TO_STRING.xml`](../examples/P_Demo_ROUTETRANSPORT_TO_STRING.xml) |

---
## 1. 功能简述

**AMS 路由传输层枚举 → 字符串**：用于显示/日志。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION ROUTETRANSPORT_TO_STRING : STRING
VAR_INPUT
    eType : E_RouteTransportType;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `eType` | `E_RouteTransportType` | 传输层类型枚举 |

### 返回值

`STRING` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `STRING`。

## 5. 使用注意 / 常见坑

- 枚举 `E_RouteTransportType` 见 Tc2_Utilities Data types。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ROUTETRANSPORT_TO_STRING.xml`](../examples/P_Demo_ROUTETRANSPORT_TO_STRING.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_ROUTETRANSPORT_TO_STRING
VAR
    rResult : STRING;
    bRun    : BOOL;
    et : E_RouteTransportType;
END_VAR

IF bRun THEN
    rResult := ROUTETRANSPORT_TO_STRING(et);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
