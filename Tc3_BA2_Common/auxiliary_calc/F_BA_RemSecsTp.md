# F_BA_RemSecsTp

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION` |
| Category | `Functions / Universal / AuxiliaryCalculation` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/16580606859.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BA_RemSecsTp.TcPOU`](../examples/P_Demo_F_BA_RemSecsTp.TcPOU) |

---

## 1. 功能简述

查询某个 `TP` 实例的剩余脉冲时长（秒粒度，向下取整）。返回 UDINT。

## 2. 接口定义

### 完整声明

```iecst
FUNCTION F_BA_RemSecsTp : UDINT
VAR_INPUT
  tpTimer    : TP;
END_VAR
```

### VAR_INPUT 引脚

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `tpTimer` | `TP` | - | 被查询的 TP 实例。 |

### VAR_IN_OUT

无。


## 3. 行为说明

查询某个 `TP` 实例的剩余脉冲时长（秒粒度，向下取整）。返回 UDINT。 接入参数：`tpTimer`。每个参数的类型与默认值见 §2 接口定义。 本 FC 是 *无状态* 的纯函数：每次调用独立计算结果，不维护任何内部历史；多任务 / 多线程调用安全；可在 PRG / FB / METHOD / 表达式中任意位置使用。 典型用法：把对应类型的定时器实例（如 `myTon : TON`）传给本 FC 的输入引脚，每周期调用一次本 FC 把剩余时间显示在 HMI 上；定时器自身的常规 IN/PT/Q 调用仍照旧。 典型工程场景：HMI 显示"脉冲还剩 X 秒"。

## 4. 错误码 / 返回值

本 FC 返回类型为 `UDINT`。

本 FC 返回 `UDINT`：通常 0 = 失败 / 无结果，> 0 = 成功 / 实际值。具体语义见 §1 功能简述。

## 5. 使用注意 / 常见坑

- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BA_RemSecsTp.TcPOU`](../examples/P_Demo_F_BA_RemSecsTp.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 显示"脉冲还剩 X 秒"。
- **价值**：一行替代手算 + 单位换算。
- **替代方案对比**：手算 + DIV 1000（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.1.4.1.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/16580606859.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
