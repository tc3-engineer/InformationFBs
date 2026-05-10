# F_GetDayOfMonthEx
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
| Example | [`examples/P_Demo_F_GetDayOfMonthEx.xml`](../examples/P_Demo_F_GetDayOfMonthEx.xml) |

---
## 1. 功能简述

计算指定年月、第 N 个、星期 X 对应的具体日期（如「2011 年 1 月的第二个周一」）。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_GetDayOfMonthEx : WORD
VAR_INPUT
    wYear : WORD(1601..30827);
    wMonth : WORD(1..12);
    wWOM : WORD(1..5);
    wDOW : WORD(0..6);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `wYear` | `WORD(1601..30827)` | 年份（1601..30827） |
| `wMonth` | `WORD(1..12)` | 月份（1..12） |
| `wWOM` | `WORD(1..5)` | 本月第几周（1..5；5 = 最后一周即使月不足 5 周） |
| `wDOW` | `WORD(0..6)` | 星期几（0=周日, 1=周一, ..., 6=周六） |

### 返回值

`WORD` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `F_GetDayOfMonthEx(WORD#2011, WORD#1, WORD#2, WORD#1)`，返回 `WORD`。
- 期望：`10（2011-01-10 是 1 月第二个周一）`

## 4. 错误码 / 返回值

返回 `WORD`。无独立错误码（部分函数用 0/全 0 结构表示参数无效）。

## 5. 使用注意 / 常见坑

- **返回 WORD**：那一天的日（1..31）；如果当月没有那么多个该星期则返回 0。
- wWOM = 5 表示「最后一个」，对月份不足 5 周的情况会返回最后一个的日期。
- wDOW 用美式编号（0=Sun），与 `F_GetDayOfWeek` 的 ISO 编号（1=Mon..7=Sun）不同——容易踩坑。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetDayOfMonthEx.xml`](../examples/P_Demo_F_GetDayOfMonthEx.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_GetDayOfMonthEx
VAR
    rResult : WORD;
    bRun    : BOOL;
END_VAR

IF bRun THEN
    rResult := F_GetDayOfMonthEx(WORD#2011, WORD#1, WORD#2, WORD#1);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
