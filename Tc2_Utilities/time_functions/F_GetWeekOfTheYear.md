# F_GetWeekOfTheYear
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
| Example | [`examples/P_Demo_F_GetWeekOfTheYear.xml`](../examples/P_Demo_F_GetWeekOfTheYear.xml) |

---
## 1. 功能简述

返回 ISO 8601 / DIN 1355 周数。**第 1 周**定义为「本年至少占 4 天」的第一周（即 1/1~1/3 可能仍属上一年最后一周）。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_GetWeekOfTheYear : WORD
VAR_INPUT
    in : DT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `DT` | 日期 |

### 返回值

`WORD` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `F_GetWeekOfTheYear(dtNow)`，返回 `WORD`。
- 期望：`12`

## 4. 错误码 / 返回值

返回 `WORD`。无独立错误码（部分函数用 0/全 0 结构表示参数无效）。

## 5. 使用注意 / 常见坑

- ISO 周从周一开始。
- 12 月底（29/30/31）可能算下一年第 1 周；1 月初（1/2/3）可能算上一年最后一周。
- PDF 例子：`F_GetWeekOfTheYear(DT#2008-03-17)` = 12。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetWeekOfTheYear.xml`](../examples/P_Demo_F_GetWeekOfTheYear.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_GetWeekOfTheYear
VAR
    rResult : WORD;
    bRun    : BOOL;
    dtNow : DT := DT#2008-03-17-12:00;
END_VAR

IF bRun THEN
    rResult := F_GetWeekOfTheYear(dtNow);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
