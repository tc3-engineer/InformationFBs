# F_GetDOYOfYearMonthDay
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
| Example | [`examples/P_Demo_F_GetDOYOfYearMonthDay.xml`](../examples/P_Demo_F_GetDOYOfYearMonthDay.xml) |

---
## 1. 功能简述

**计算一年中的第几天**（DOY = Day Of Year，1~366）。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_GetDOYOfYearMonthDay : WORD
VAR_INPUT
    wYear : WORD;
    wMonth : WORD;
    wDay : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `wYear` | `WORD` | 年份（0~2999） |
| `wMonth` | `WORD` | 月份（1~12） |
| `wDay` | `WORD` | 日（1~31） |

### 返回值

`WORD` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `F_GetDOYOfYearMonthDay(WORD#2024, WORD#3, WORD#1)`，返回 `WORD`。
- 期望：`61（2024 闰年，3 月 1 日是第 61 天）`

## 4. 错误码 / 返回值

返回 `WORD`。无独立错误码（部分函数用 0/全 0 结构表示参数无效）。

## 5. 使用注意 / 常见坑

- 计算时考虑闰年。
- 未列出错误时的返回值（⚠️ 待人工确认参数越界行为）。
- 反向：`F_GetMonthOfDOY` 由 DOY 推月份。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetDOYOfYearMonthDay.xml`](../examples/P_Demo_F_GetDOYOfYearMonthDay.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_GetDOYOfYearMonthDay
VAR
    rResult : WORD;
    bRun    : BOOL;
END_VAR

IF bRun THEN
    rResult := F_GetDOYOfYearMonthDay(WORD#2024, WORD#3, WORD#1);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

- 见上方使用注意中标 ⚠️ 的项。
