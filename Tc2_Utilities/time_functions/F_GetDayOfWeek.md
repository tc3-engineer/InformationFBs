# F_GetDayOfWeek

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35122187.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetDayOfWeek.xml`](../examples/P_Demo_F_GetDayOfWeek.xml) |

---

## 1. 功能简述

返回给定 `DT` 日期是星期几，按 **DIN 1355 / ISO 8601 标准**：周一 = 1，周二 = 2 ... 周日 = 7。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION F_GetDayOfWeek : WORD
VAR_INPUT
    in : DT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `DT` | 待求星期几的日期 |

### 返回值

`WORD` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

函数对 `DT` 做日历计算（基于 Zeller 公式或等价算法）得到星期几。

**注意编号约定**：本 FC 用 DIN 1355 / ISO 8601 的 1 = Monday；而 Windows `TIMESTRUCT.wDayOfWeek` 与 `F_GetDayOfMonthEx` 的 `wDOW` 参数用 0 = Sunday。两种约定混用极易出错。

例如 2008-01-01 是周二 → 返回 2。函数无副作用、纯计算、可在任意任务上下文调用。


实际工程中常把本 FC 与 `F_GetActualDateTime`（取当前 `DT`）配合使用，在循环里每天判断一次是否周末；或用作排班逻辑的入口——把当前日期映射到 1 ~ 7，再用 `CASE` 决定该班次的工艺参数。本 FC 是日历类函数中最高频使用的一个。

## 4. 错误码 / 返回值

返回类型 `WORD`。函数语义详见 §3。某些 FC（返回 `WORD` / `T_FILETIME64` / `TOD` 的）以 0 作为「参数错误」哨兵值——调用方必须先检查 > 0；具体见 §5 使用注意。

## 5. 使用注意 / 常见坑

- **1 = Monday，不是 0 = Sunday**：与 Windows API 约定不同。
- **没有错误返回**：永远返回 1-7，输入超出 `DT` 范围会得到无意义结果但不报错。
- **`DT` 上限约 2106-02**：`DT` 类型最大值会限制可查询的最远日期。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetDayOfWeek.xml`](../examples/P_Demo_F_GetDayOfWeek.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
dayOfWeek := F_GetDayOfWeek(DT#2008-01-01-00:00);   // 期望 2
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：在排班 / 排产逻辑里需要知道当前是周几——周末跳过、工作日运行、第 N 个周三例行任务。
- **价值**：比手写 Zeller 公式不容易出错；比换算到 `TIMESTRUCT.wDayOfWeek` 再做「+1 mod 7」修正更直接。
- **替代方案对比**：用 `DT_TO_SYSTEMTIME(...).wDayOfWeek + 1 modulo 7`（要做约定换算）/ 手写 Zeller（容易错）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35122187.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
