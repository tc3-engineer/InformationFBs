# F_BA_DaysInMonth

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION` |
| Category | `Functions / Types / Date and Time` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785447051.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BA_DaysInMonth.TcPOU`](../examples/P_Demo_F_BA_DaysInMonth.TcPOU) |

---

## 1. 功能简述

返回指定年月的天数。考虑闰年。返回 BYTE（28..31）。

## 2. 接口定义

### 完整声明

```iecst
FUNCTION F_BA_DaysInMonth : UDINT
VAR_INPUT
  stBACnetDate    : ST_BA_Date;
END_VAR
```

### VAR_INPUT 引脚

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stBACnetDate` | `ST_BA_Date` | - | Date from whose month the number of days is to be determined. |

### VAR_IN_OUT

无。


## 3. 行为说明

返回指定年月的天数。考虑闰年。返回 BYTE（28..31）。 接入参数：`stBACnetDate`。每个参数的类型与默认值见 §2 接口定义。 本 FC 是 *无状态* 的纯函数：每次调用独立计算结果，不维护任何内部历史；多任务 / 多线程调用安全；可在 PRG / FB / METHOD / 表达式中任意位置使用。 典型工程场景：日历视图渲染当月的格子数。

## 4. 错误码 / 返回值

本 FC 返回类型为 `UDINT`。

本 FC 返回 `UDINT`：通常 0 = 失败 / 无结果，> 0 = 成功 / 实际值。具体语义见 §1 功能简述。

## 5. 使用注意 / 常见坑

- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BA_DaysInMonth.TcPOU`](../examples/P_Demo_F_BA_DaysInMonth.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：日历视图渲染当月的格子数。
- **价值**：一行 FC 替代 CASE 月份 + 闰年判断。
- **替代方案对比**：`CASE month OF 1,3,5,7,8,10,12: 31; 4,6,9,11: 30; 2: IF leap THEN 29 ELSE 28; END_CASE;`（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.1.3.3.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785447051.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
