# F_GetMaxMonthDays

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35117579.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetMaxMonthDays.TcPOU`](../examples/P_Demo_F_GetMaxMonthDays.TcPOU) |

---

## 1. 功能简述

返回指定年月有多少天。考虑闰年规则（2 月在闰年返回 29，普通年 28）。返回 0 = 参数错误，> 0 = 该月天数。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION F_GetMaxMonthDays : WORD
VAR_INPUT
    wYear : WORD;
    wMonth : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `wYear` | `WORD` | 年份 |
| `wMonth` | `WORD` | 月份（1 ~ 12） |

### 返回值

`WORD` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

函数按 30 天月 / 31 天月 / 闰年 2 月 / 平年 2 月 四种情况返回结果：

- 1、3、5、7、8、10、12 月 → 31
- 4、6、9、11 月 → 30
- 2 月：闰年返回 29，平年返回 28
- 月份越界 → 返回 0（错误）

闰年判定与 `F_YearIsLeapYear` 一致：能被 4 整除且不被 100 整除，或者能被 400 整除。

函数纯计算、无错误码、无副作用。


常作为「日期合法性校验」管线的一环：先校验月份在 1 ~ 12，再用本 FC 取该月最大天数，再校验输入 day ≤ 最大天数。整条校验链下来只有 3 个分支，比手写"30 天月 / 31 天月 / 闰年 2 月 / 平年 2 月"四段判断更简洁、更不易漏改。

## 4. 错误码 / 返回值

返回类型 `WORD`。函数语义详见 §3。某些 FC（返回 `WORD` / `T_FILETIME64` / `TOD` 的）以 0 作为「参数错误」哨兵值——调用方必须先检查 > 0；具体见 §5 使用注意。

## 5. 使用注意 / 常见坑

- **返回 0 表示错误**：传入月份 0 或 > 12 时返回 0，**不要把 0 当成「该月 0 天」使用**。
- **年份在合法范围内是不会报错的**：年份 PDF 没明确范围检查，传任意 `WORD` 都会按闰年规则计算。
- **典型用法：日期合法性校验**：判断用户输入的 (年, 月, 日) 是否合法，先看月份合法再用本 FC 比较 day ≤ 返回值。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetMaxMonthDays.TcPOU`](../examples/P_Demo_F_GetMaxMonthDays.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
wDays := F_GetMaxMonthDays(2024, 2);   // 闰年 → 29
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：用户输入 (年, 月, 日) 后做合法性检查（避免接受 2 月 30 日）；或者按月生成日报，需要知道该月有多少天来算累计 / 平均。
- **价值**：1 行调用即得月长，无需手写 `IF wMonth IN {1,3,5,7,8,10,12} ...` 一长串判断。
- **替代方案对比**：用 30/31 月份的硬编码表（不处理闰年）/ 手写 IF-ELSE 链（11 行代码）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35117579.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
