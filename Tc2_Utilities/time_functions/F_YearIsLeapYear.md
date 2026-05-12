# F_YearIsLeapYear

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35136011.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_YearIsLeapYear.xml`](../examples/P_Demo_F_YearIsLeapYear.xml) |

---

## 1. 功能简述

判断指定年份是否是闰年。规则：能被 4 整除且不被 100 整除，或者能被 400 整除即为闰年。返回 `TRUE` = 闰年，`FALSE` = 非闰年。

## 2. 接口定义

### 函数声明

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

`BOOL` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

闰年规则（公历 / Gregorian Calendar）：

- 能被 4 整除 → 闰年（如 2024）
- 但能被 100 整除 → 非闰年（如 1900）
- 但能被 400 整除 → 还是闰年（如 2000）

返回 `BOOL`，无错误码：任意 `WORD` 输入都有定义良好的返回值。

函数纯计算、无副作用，常作为其他时间函数（`F_GetMaxMonthDays`、`F_GetDOYOfYearMonthDay` 等）的内部依赖。


本 FC 在 Tc2_Utilities 内部被 `F_GetMaxMonthDays`、`F_GetDOYOfYearMonthDay`、`F_GetMonthOfDOY` 调用作为闰年判定的统一入口；在用户代码里直接调用主要用于「2 月 29 日合法性校验」或者「按 365 / 366 天平均」的能耗 / 农业模型。函数对所有合法 `WORD` 输入都有定义良好的返回值。

## 4. 错误码 / 返回值

返回类型 `BOOL`。返回 `BOOL`：`TRUE` / `FALSE` 的语义见 §1 功能简述。无错误码。

## 5. 使用注意 / 常见坑

- **1900 不是闰年、2000 是**：常见错误是只用 `wYear MOD 4 = 0` 判定，会把 1900 / 2100 / 2200 / 2300 错误判定成闰年。
- **`WORD` 上界是 65535**：函数能处理远期年份，但实际 `DT` 类型只支持到约 2106。
- **常用搭配场景**：日期合法性检查（2 月 29 日只在闰年合法）、农业模型按 365/366 天平均。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_YearIsLeapYear.xml`](../examples/P_Demo_F_YearIsLeapYear.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
bLeap := F_YearIsLeapYear(2024);   // TRUE
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：用户输入日期时校验 2 月 29 日是否合法；或者按 ISO 8601 周计算时确认该年是否有 53 周（部分闰年情况）。
- **价值**：1 行调用避免手写 100 / 400 三段判定（最常被遗忘的是「能被 100 整除但不被 400 整除非闰年」这一段）。
- **替代方案对比**：手写 `(y MOD 4 = 0) AND (y MOD 100 <> 0 OR y MOD 400 = 0)`（容易写错优先级）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.11
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35136011.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
