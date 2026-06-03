# F_BA_IsMeasuringElementValid

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION` |
| Category | `Functions / ValidationFunctions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10789677963.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BA_IsMeasuringElementValid.TcPOU`](../examples/P_Demo_F_BA_IsMeasuringElementValid.TcPOU) |

---

## 1. 功能简述

检查 `E_BA_MeasuringElement` 枚举值是否合法（传感器类型枚举：Pt100 / Ni1000 / Ohm / 等）。返回 BOOL。

## 2. 接口定义

### 完整声明

```iecst
FUNCTION F_BA_IsMeasuringElementValid : BOOL
VAR_INPUT
  eElement    : E_BA_MeasuringElement;
END_VAR
```

### VAR_INPUT 引脚

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `eElement` | `E_BA_MeasuringElement` | - | 被校验的 `E_BA_MeasuringElement` 枚举值。 |

### VAR_IN_OUT

无。


## 3. 行为说明

检查 `E_BA_MeasuringElement` 枚举值是否合法（传感器类型枚举：Pt100 / Ni1000 / Ohm / 等）。返回 BOOL。 接入参数：`eElement`。每个参数的类型与默认值见 §2 接口定义。 本 FC 是 *无状态* 的纯函数：每次调用独立计算结果，不维护任何内部历史；多任务 / 多线程调用安全；可在 PRG / FB / METHOD / 表达式中任意位置使用。 典型用法：配置加载阶段把外部传入的枚举值喂给本 FC，结果为 FALSE 时拒绝加载或回退到默认值——避免无效枚举传入下游 FB 引发运行时异常。 典型工程场景：上电时校验配置文件里的传感器类型枚举是否合法（避免传给 `FB_BA_KL32xx` 时崩溃）。

## 4. 错误码 / 返回值

本 FC 返回类型为 `BOOL`。

本 FC 返回 BOOL：`TRUE` = 判定成功 / 条件满足；`FALSE` = 判定失败 / 条件不满足。

## 5. 使用注意 / 常见坑

- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BA_IsMeasuringElementValid.TcPOU`](../examples/P_Demo_F_BA_IsMeasuringElementValid.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：上电时校验配置文件里的传感器类型枚举是否合法（避免传给 `FB_BA_KL32xx` 时崩溃）。
- **价值**：同其它 IsValid 系列。
- **替代方案对比**：范围比较（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.1.5.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10789677963.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
