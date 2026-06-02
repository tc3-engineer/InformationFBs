# F_GetWeekOfTheYear

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35123723.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetWeekOfTheYear.TcPOU`](../examples/P_Demo_F_GetWeekOfTheYear.TcPOU) |

---

## 1. 功能简述

按 **DIN 1355 / ISO 8601** 返回指定日期所在的日历周（1 ~ 53）。第 1 周定义为：包含新年至少 4 天的那一周；周从周一开始；12 月 29-31 日可能属于下年第 1 周，1 月 1-3 日可能属于上年最后一周。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION F_GetWeekOfTheYear : WORD
VAR_INPUT
    in : DT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `DT` | 待求周数的日期 |

### 返回值

`WORD` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

ISO 8601 周编号规则比「年初到现在第几周」复杂：

- 周从周一开始（不是 Sunday）
- 第 1 周必须包含至少 4 天属于新年（等价于：包含本年第一个周四的那一周）
- 12 月 29 ~ 31 日如果其所在周第 4 天落在次年 1 月，则该日期属于次年第 1 周
- 1 月 1 ~ 3 日如果其所在周第 4 天落在上年 12 月，则该日期属于上年第 52 / 53 周

返回值 1 ~ 53。函数内部按 ISO 算法（基于 Zeller 公式 + 周四调整）计算。


实际工程中 ISO 周编号广泛用于制造业排产：MES 系统按 "CW12" 这样的 ISO 周做交付计划，PLC 端用本 FC 把当前 `DT` 转成 ISO 周后与 MES 下发的计划比对，决定是否进入"赶工模式"。处理跨年情形（12 月底 / 1 月初）一定要把"年份"和"周数"一起记录，单独的周数不能跨年比较。

## 4. 错误码 / 返回值

返回类型 `WORD`。函数语义详见 §3。某些 FC（返回 `WORD` / `T_FILETIME64` / `TOD` 的）以 0 作为「参数错误」哨兵值——调用方必须先检查 > 0；具体见 §5 使用注意。

## 5. 使用注意 / 常见坑

- **1 ~ 53 不是 1 ~ 52**：闰年或 1 月 1 日是周四时会有 53 周。
- **12 月底 / 1 月初的跨年现象**：2026-01-01（周四）是 2026 第 1 周；但 2027-01-01（周五）属于 2026 第 53 周。**周数 + 年份要一起记录**，不然跨年统计会乱。
- **与 Windows GetWeekOfYear 行为有差异**：Windows 默认用「First Day」规则，本 FC 用 ISO，调用方应明确告诉客户用的是哪个标准。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetWeekOfTheYear.TcPOU`](../examples/P_Demo_F_GetWeekOfTheYear.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
weekOfYear := F_GetWeekOfTheYear(DT#2008-03-17-12:00);   // 期望 12
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：工厂周报 / 周排产用 ISO 周编号；与 SAP / MES / ERP 等上层系统对接时都用 ISO 周（「CW12 投产」是欧洲制造业标准说法）。
- **价值**：1 行调用拿到 ISO 周，避免手写第 1 周判定（错过 4-day 规则容易把 1 月 1 日错算成第 1 周）。
- **替代方案对比**：手写 ISO 算法（容易出错，特别是跨年情形）/ 用 `DT_TO_FILETIME64` + Windows API（更复杂）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35123723.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
