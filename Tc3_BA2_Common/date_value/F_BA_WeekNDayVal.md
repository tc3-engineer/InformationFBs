# F_BA_WeekNDayVal

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION` |
| Category | `Functions / Types / DateValue` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/9917933707.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BA_WeekNDayVal.TcPOU`](../examples/P_Demo_F_BA_WeekNDayVal.TcPOU) |

---

## 1. 功能简述

把"第 N 个星期 X" `ST_BA_WeekNDay` 按 `eChoice` 封装为 `U_BA_DateVal`。例："每月第二个星期日"。

## 2. 接口定义

### 完整声明

```iecst
FUNCTION F_BA_WeekNDayVal : U_BA_DateVal
VAR_INPUT
  eWeekday        : E_BA_Weekday  := E_BA_Weekday.Invalid;
  eWeekOfMonth    : E_BA_Week     := E_BA_Week.Invalid;
  eMonth          : E_BA_Month    := E_BA_Month.Invalid;
END_VAR
```

### VAR_INPUT 引脚

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `eWeekday` | `E_BA_Weekday` | `E_BA_Weekday.Invalid` | 星期几（eMonday..eSunday）。 |
| `eWeekOfMonth` | `E_BA_Week` | `E_BA_Week.Invalid` | Entry of the week within the month. |
| `eMonth` | `E_BA_Month` | `E_BA_Month.Invalid` | Entry of the month. |

### VAR_IN_OUT

无。


## 3. 行为说明

把"第 N 个星期 X" `ST_BA_WeekNDay` 按 `eChoice` 封装为 `U_BA_DateVal`。例："每月第二个星期日"。 接入参数：`eWeekday`, `eWeekOfMonth`, `eMonth`。每个参数的类型与默认值见 §2 接口定义。 本 FC 是 *无状态* 的纯函数：每次调用独立计算结果，不维护任何内部历史；多任务 / 多线程调用安全；可在 PRG / FB / METHOD / 表达式中任意位置使用。 典型工程场景："每月第二个星期日为夏令时切换" —— 把 WeekNDay 打包供调度引擎。

## 4. 错误码 / 返回值

本 FC 返回类型为 `U_BA_DateVal`。

本 FC 返回 `U_BA_DateVal` 类型：表示对应的时间 / 日期 / 时间戳值。

## 5. 使用注意 / 常见坑

- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BA_WeekNDayVal.TcPOU`](../examples/P_Demo_F_BA_WeekNDayVal.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**："每月第二个星期日为夏令时切换" —— 把 WeekNDay 打包供调度引擎。
- **价值**：同上：统一接口让调度引擎处理。
- **替代方案对比**：调度引擎需要分类型处理（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.1.3.4.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/9917933707.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
