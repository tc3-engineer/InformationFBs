# F_GetDayOfMonthEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35125259.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetDayOfMonthEx.xml`](../examples/P_Demo_F_GetDayOfMonthEx.xml) |

---

## 1. 功能简述

计算指定年月里「第 N 个星期 X」对应的日期。例如：2011 年 8 月第 2 个周一的日期是 8 号。返回 0 表示参数错误，> 0 表示该月的日（DOM）。

## 2. 接口定义

### 函数声明

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
| `wYear` | `WORD(1601..30827)` | 年份（1601 ~ 30827） |
| `wMonth` | `WORD(1..12)` | 月份（1 ~ 12） |
| `wWOM` | `WORD(1..5)` | 月内第几周（1 ~ 5）；5 表示最后一周（即使该月不足 5 周） |
| `wDOW` | `WORD(0..6)` | 星期几（0 = 周日，1 = 周一 ... 6 = 周六） |

### 返回值

`WORD` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

函数按公历规则查表 + 计算返回该月第 wWOM 个 wDOW 的日数；wWOM = 5 表示「最后一个 wDOW」——即使该月该星期只出现 4 次也返回最后一次的日期，而不是返回 0。

`wDOW` 用 Windows 约定（0 = Sunday），与 `F_GetDayOfWeek` 的 DIN/ISO 约定（1 = Monday）**不同**，调用前要确认源头。

返回 `WORD`：0 = 错误（年 / 月 / 周 / 星期参数任一越界），≥ 1 = 该月的日（1 ~ 31）。

## 4. 错误码 / 返回值

返回类型 `WORD`。函数语义详见 §3。某些 FC（返回 `WORD` / `T_FILETIME64` / `TOD` 的）以 0 作为「参数错误」哨兵值——调用方必须先检查 > 0；具体见 §5 使用注意。

## 5. 使用注意 / 常见坑

- **返回值与错误编码混在同一类型**：必须检查 `result > 0` 才能用，0 表示错误。常见错误是把 0 当成「1 号前一天」。
- **`wDOW` 用 0-6 而非 1-7**：跨 FC 调用时要做星期编号映射。
- **wWOM = 5 不是绝对第 5 周**：含义是「最后一周」，月内若有第 5 个该 DOW 就返回它，否则返回第 4 个；不会返回下个月的日期。
- **典型用例：节假日 / 计划排期**：「每月第 2 个周一开例会」/「每月最后一个周五结算」等公历日期计算。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetDayOfMonthEx.xml`](../examples/P_Demo_F_GetDayOfMonthEx.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
wDay := F_GetDayOfMonthEx(2011, 8, 2, 1);   // 2011 年 8 月第 2 个周一 = 8 号
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：排产 / 维护计划：「每月最后一个周日设备深度保养」、「每月第一个周一汇报数据」。机器需要在运行时算出该规则下次触发的具体日期。
- **价值**：1 行调用拿到日历日，不必手写「循环遍历该月所有日子找匹配星期」。
- **替代方案对比**：用 `F_GetDayOfWeek` + 循环遍历该月每天找匹配（要 31 次调用）/ 手写公式（容易错）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35125259.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
