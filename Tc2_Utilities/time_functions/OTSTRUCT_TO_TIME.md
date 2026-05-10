# OTSTRUCT_TO_TIME
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-10 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_OTSTRUCT_TO_TIME.xml`](../examples/P_Demo_OTSTRUCT_TO_TIME.xml) |

---
## 1. 功能简述

把 `OTSTRUCT`（含 weeks/days/hours/minutes/seconds/milliseconds 各字段）转回 TIME 字面量。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION OTSTRUCT_TO_TIME : TIME
VAR_INPUT
    OTIN : OTSTRUCT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `OTIN` | `OTSTRUCT` | 要转换的结构（含周/日/时/分/秒/毫秒分量） |

### 返回值

`TIME` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `OTSTRUCT_TO_TIME(otIn)`，返回 `TIME`。
- 期望：`T#1m30s`

## 4. 错误码 / 返回值

返回 `TIME`。无独立错误码（部分函数用 0/全 0 结构表示参数无效）。

## 5. 使用注意 / 常见坑

- `OTSTRUCT` 是 Tc2_Utilities 自定义结构（见 Data types 章节）。
- 反向：`TIME_TO_OTSTRUCT`（拆分 TIME 到各时间分量）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_OTSTRUCT_TO_TIME.xml`](../examples/P_Demo_OTSTRUCT_TO_TIME.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_OTSTRUCT_TO_TIME
VAR
    rResult : TIME;
    bRun    : BOOL;
    otIn : OTSTRUCT;
END_VAR

otIn.minutes := 1; otIn.seconds := 30;
IF bRun THEN
    rResult := OTSTRUCT_TO_TIME(otIn);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
