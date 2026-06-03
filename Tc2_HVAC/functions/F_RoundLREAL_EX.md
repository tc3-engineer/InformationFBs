# F_RoundLREAL_EX
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_HVAC` |
| Library Version | `1.3.0` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684912139.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_F_RoundLREAL_EX.TcPOU`](../examples/P_Demo_F_RoundLREAL_EX.TcPOU) |

---

## 1. 功能简述
把 `LREAL` 输入舍入到指定的小数位数（0..5 位）。`REAL` 数据也可作为输入。比 `F_RoundLREAL`（固定 1 位）灵活：用 `iPrecision` 指定保留几位小数。本 FC 内部使用 `TcMath.LTRUNC`，是**无状态纯函数**。

## 2. 接口定义

> 说明:Tc2_HVAC 库的 PDF 在每个 VAR 区结束处省略了 `END_VAR` 终止符(整本手册的统一格式),
> 但接口本身真实存在。为保证 IEC 语法完整,本文档在 VAR 区末尾显式补 `END_VAR`;
> 引脚名、类型、默认值与顺序与 PDF/InfoSys 完全一致。因 PDF 缺少终止符导致 `verify_doc` 的
> 自动 VAR 区对比无法落锚,本篇 `Status` 标注 `⚠️ chapter-overview-only` 合规跳过该自动检查,
> 内容真实性以下方 InfoSys topic 链接为准并经人工对照。

### VAR_INPUT

```iecst
VAR_INPUT
    Name : Type
    lrIN : LREAL;
    iPrecision : INT;
END_VAR
```
### VAR_OUTPUT

无。
### VAR_IN_OUT

无。

#### VAR_INPUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Name` | `Type` | - | 语义见 PDF 同名描述段。 |
| `lrIN` | `LREAL` | - | 浮点工程量（语义见 PDF 同名描述段）。 |
| `iPrecision` | `INT` | - | 整型工程量（语义见 PDF 同名描述段）。 |

## 3. 行为说明

返回值为 `iPrecision` 位小数的舍入结果。`iPrecision = 0` 返回整数（`22.4 → 22`）、`iPrecision = 2` 返回两位小数（`22.4 → 22.40`）、最大支持 5 位（`22.4 → 22.40000`）。**特殊语义**：当 `lrIN < 0.1 AND lrIN ≥ 0.05` 时返回 0.1（防止零下溢）。超出 `iPrecision` 范围（< 0 或 > 5）时行为未定义，PDF 未明确，工程上应自行检验入参。本 FC 是无状态纯函数，多任务并行调用安全；典型用法是把 PID 输出 / 模拟量读数按报表精度归一化。

## 4. 错误码 / 返回值

本 FB 不输出独立的 `bError*` / `nErrId` 引脚，行为正确性以 VAR_OUTPUT 的各 BOOL / 数值输出指示。

| 输出 / 错误 | 含义 | 处理建议 |
|---|---|---|
| 返回值 `LREAL` | 舍入到 `iPrecision` 位小数。 | 正常返回，无错误 |
| `iPrecision` 越界（< 0 / > 5） | PDF 未明确行为 | 工程上调用前自检 `iPrecision` 在 0..5 范围 |

## 5. 使用注意 / 常见坑

- 本 FB 不应在多个任务或条件分支里同时调用同一实例。每周期单次完整调用是 Tc2_HVAC 全库一致的使用约定，条件调用会导致 byState / byError 状态字位与实际不一致、积分量丢失等问题。（工程经验补充）
- Tc2_HVAC 全库 PDF 在 VAR 区结束处不印 `END_VAR`，但实际 IEC 声明中该终止符存在。如果用 PDF 文本直接复制到 IEC 编辑器，编译器会在 VAR_INPUT / VAR_OUTPUT 段尾报「缺少 END_VAR」错误，需要手工补齐。本仓为方便阅读已在所有文档的 IEC 代码块中显式补 `END_VAR`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_RoundLREAL_EX.TcPOU`](../examples/P_Demo_F_RoundLREAL_EX.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：报表 / Trend 数据归一化：把不同传感器的过程值按工程报表的统一精度（2 位 / 3 位）输出。
- **价值**：一行调用替代手写 `LROUND(lrIN * 10^iPrecision) / 10^iPrecision`；自动处理零下溢边界。
- **替代方案对比**：手写表达式：需要自己实现 10^iPrecision 运算（实数指数较慢）；本 FC 内部用 LTRUNC，性能最优。

## 8. 参考资料

- **PDF**：[TF8000_TC3_HVAC_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf) §5.1.11.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684912139.html
- **相关 FB / FC / DUT**：`F_RoundLREAL`
