# GuidsEqualByVal
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
| Example | [`examples/P_Demo_GuidsEqualByVal.xml`](../examples/P_Demo_GuidsEqualByVal.xml) |

---
## 1. 功能简述

**按值比较两个 GUID**：相等返回 TRUE。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION GuidsEqualByVal : BOOL
VAR_INPUT
    guidA : GUID;
    guidB : GUID;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `guidA` | `GUID` | 比较 GUID A |
| `guidB` | `GUID` | 比较 GUID B |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 见上方功能简述。

## 4. 错误码 / 返回值

返回 `BOOL`。

## 5. 使用注意 / 常见坑

- 按值比较——结构体所有字节都相等才算相等。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GuidsEqualByVal.xml`](../examples/P_Demo_GuidsEqualByVal.xml)
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_GuidsEqualByVal
VAR
    rResult : BOOL;
    bRun    : BOOL;
    a, b : GUID;
END_VAR

IF bRun THEN
    rResult := GuidsEqualByVal(a, b);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
