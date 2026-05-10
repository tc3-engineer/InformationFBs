# F_YearIsLeapYear
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
| Example | [`examples/P_Demo_F_YearIsLeapYear.xml`](../examples/P_Demo_F_YearIsLeapYear.xml) |

---
## 1. 功能简述

判断**是否为闰年**。返回 TRUE = 闰年，FALSE = 平年。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_YearIsLeapYear : BOOL
VAR_INPUT
    wYear : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `wYear` | `WORD` | 年份 |

### 返回值

`BOOL` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `F_YearIsLeapYear(WORD#2024)`，返回 `BOOL`。
- 期望：`TRUE`

## 4. 错误码 / 返回值

返回 `BOOL`。无独立错误码（部分函数用 0/全 0 结构表示参数无效）。

## 5. 使用注意 / 常见坑

- 实现使用标准格里历规则（4 整除且非 100 整除，或 400 整除）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_YearIsLeapYear.xml`](../examples/P_Demo_F_YearIsLeapYear.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_YearIsLeapYear
VAR
    rResult : BOOL;
    bRun    : BOOL;
END_VAR

IF bRun THEN
    rResult := F_YearIsLeapYear(WORD#2024);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
