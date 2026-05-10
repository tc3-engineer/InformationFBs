# F_GetDayOfWeek
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
| Example | [`examples/P_Demo_F_GetDayOfWeek.xml`](../examples/P_Demo_F_GetDayOfWeek.xml) |

---
## 1. 功能简述

返回某日期的**星期几（ISO 8601 / DIN 1355 编号）**：周一=1、周二=2、…、周日=7。
## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_GetDayOfWeek : WORD
VAR_INPUT
    in : DT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `DT` | 日期（DT 格式） |

### 返回值

`WORD` —— 函数计算结果。

### VAR_IN_OUT

无。

## 3. 行为说明

- 调用 `F_GetDayOfWeek(dtFirst)`，返回 `WORD`。
- 期望：`2（周二）`

## 4. 错误码 / 返回值

返回 `WORD`。无独立错误码（部分函数用 0/全 0 结构表示参数无效）。

## 5. 使用注意 / 常见坑

- ISO 编号（1=Mon..7=Sun），与 `F_GetDayOfMonthEx` 的 wDOW 美式编号（0=Sun）不同。
- PDF 例子：`F_GetDayOfWeek(DT#2008-01-01)` = 2（周二）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetDayOfWeek.xml`](../examples/P_Demo_F_GetDayOfWeek.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_GetDayOfWeek
VAR
    rResult : WORD;
    bRun    : BOOL;
    dtFirst : DT := DT#2008-01-01-00:00;
END_VAR

IF bRun THEN
    rResult := F_GetDayOfWeek(dtFirst);
    bRun := FALSE;
END_IF;
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目

## 8. 待确认项

无。
