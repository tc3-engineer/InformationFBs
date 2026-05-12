# F_GetDOYOfYearMonthDay

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35119115.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetDOYOfYearMonthDay.xml`](../examples/P_Demo_F_GetDOYOfYearMonthDay.xml) |

---

## 1. 功能简述

把 (年, 月, 日) 转换为「年内第几天」（Day Of Year，1 ~ 366）。返回 0 表示参数无效，> 0 是 DOY。

## 2. 接口定义

### 函数声明

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
| `wYear` | `WORD` | 年份（0 ~ 2999） |
| `wMonth` | `WORD` | 月份（1 ~ 12） |
| `wDay` | `WORD` | 日（1 ~ 31） |

### 返回值

`WORD` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

函数按公历规则计算输入日期在该年的累计天数。考虑闰年：闰年 2 月有 29 天，普通年 28 天；2 月 28 日在闰年是 DOY 59，普通年是 DOY 59，但 2 月 29 日在闰年是 DOY 60、普通年无效返回 0。

闰年判定规则：能被 4 整除且不被 100 整除，或者能被 400 整除（与 `F_YearIsLeapYear` 一致）。

返回 0 = 参数错误（年 / 月 / 日任一越界或日数超过该月最大天数），≥ 1 = 该年第几天。

## 4. 错误码 / 返回值

返回类型 `WORD`。函数语义详见 §3。某些 FC（返回 `WORD` / `T_FILETIME64` / `TOD` 的）以 0 作为「参数错误」哨兵值——调用方必须先检查 > 0；具体见 §5 使用注意。

## 5. 使用注意 / 常见坑

- **返回 0 表示错误**：必须先检查 > 0 才能使用。
- **闰年 2 月 29 日**：在闰年返回 60，普通年返回 0。
- **与 `F_GetMonthOfDOY` 互逆**：组合可用于「年中第 N 天对应日期」的查询场景。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetDOYOfYearMonthDay.xml`](../examples/P_Demo_F_GetDOYOfYearMonthDay.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
wDOY := F_GetDOYOfYearMonthDay(2009, 3, 1);   // 期望 60（非闰年）
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：气象 / 农业 / 能耗统计场景需要按「年内第几天」做归档（DOY 是国际通用的天序号）；或者把(年, 月, 日)折叠成单个 WORD 用作哈希键。
- **价值**：1 行调用避免手写「累加各月天数 + 闰年判定」，特别是 2 月闰年判定容易写漏 400 年规则。
- **替代方案对比**：手写 12 个月天数累加 + 闰年判定（容易出错）/ 用 `DT_TO_FILETIME64` 减去年初差再除 86400（要 3 步）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35119115.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
