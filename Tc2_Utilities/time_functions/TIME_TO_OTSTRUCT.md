# TIME_TO_OTSTRUCT
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
| Example | [`examples/P_Demo_TIME_TO_OTSTRUCT.xml`](../examples/P_Demo_TIME_TO_OTSTRUCT.xml) |

---
## 1. 功能简述

把 `TIME` 拆为 `OTSTRUCT`（含 milliseconds/seconds/minutes/hours/days/weeks 各分量）。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION TIME_TO_OTSTRUCT : OTSTRUCT
VAR_INPUT
    TIN : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `TIN` | `TIME` | 要转换的 TIME 变量 |

### 返回值

`OTSTRUCT` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `TIME_TO_OTSTRUCT(tIn)`，返回 `OTSTRUCT`。
- 期望：`OTSTRUCT(minutes=1, seconds=30, milliseconds=500, ...)`

## 4. 错误码 / 返回值

返回 `OTSTRUCT`。无独立错误码（部分函数用 0/全 0 结构表示参数无效）。

## 5. 使用注意 / 常见坑

- 用于把 TIME 字面量分解为可读字段。
- 反向：`OTSTRUCT_TO_TIME`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TIME_TO_OTSTRUCT.xml`](../examples/P_Demo_TIME_TO_OTSTRUCT.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_TIME_TO_OTSTRUCT
VAR
    rResult : OTSTRUCT;
    bRun    : BOOL;
    tIn : TIME := T#1m30s500ms;
END_VAR

IF bRun THEN
    rResult := TIME_TO_OTSTRUCT(tIn);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
