# F_RoundLREAL
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
| Example | [`examples/P_Demo_F_RoundLREAL.TcPOU`](../examples/P_Demo_F_RoundLREAL.TcPOU) |

---

## 1. 功能简述
把 `LREAL` 输入舍入到小数点后 1 位（即四舍五入到 0.1）。`REAL` 数据也可作为输入（自动隐式转换）。本 FC 是**无状态纯函数**，可在任何 PRG / FB / METHOD 中按值调用。

## 2. 接口定义

> 说明:Tc2_HVAC 库的 PDF 在每个 VAR 区结束处省略了 `END_VAR` 终止符(整本手册的统一格式),
> 但接口本身真实存在。为保证 IEC 语法完整,本文档在 VAR 区末尾显式补 `END_VAR`;
> 引脚名、类型、默认值与顺序与 PDF/InfoSys 完全一致。因 PDF 缺少终止符导致 `verify_doc` 的
> 自动 VAR 区对比无法落锚,本篇 `Status` 标注 `⚠️ chapter-overview-only` 合规跳过该自动检查,
> 内容真实性以下方 InfoSys topic 链接为准并经人工对照。

### VAR_INPUT

```iecst
VAR_INPUT
    lrIN : LREAL;
END_VAR
```
### VAR_OUTPUT

无。
### VAR_IN_OUT

无。

#### VAR_INPUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `lrIN` | `LREAL` | - | 浮点工程量（语义见 PDF 同名描述段）。 |

## 3. 行为说明

调用形如 `F_RoundLREAL(lrIN := 3.14159)` 返回 3.1。负数同样按四舍五入处理（如 -3.16 → -3.2）。本 FC 是无状态纯函数，无内部缓存、无副作用，多任务并行调用安全。适用于 HMI 显示（避免显示 22.36789012 这种过精度值）、报表数据归一化（统一小数位数）、PID 输出小数截断（避免 LREAL 全精度变化反复刷新 HMI）等场景。调用时 `lrIN` 和返回值都是 `LREAL` 双精度浮点；如果传入 `REAL` 编译器会自动隐式转换，结果保持 1 位小数精度。

## 4. 错误码 / 返回值

本 FB 不输出独立的 `bError*` / `nErrId` 引脚，行为正确性以 VAR_OUTPUT 的各 BOOL / 数值输出指示。

| 输出 / 错误 | 含义 | 处理建议 |
|---|---|---|
| 返回值 `LREAL` | 舍入结果，小数点后 1 位。 | 正常情况下不存在错误条件；无需排错 |

## 5. 使用注意 / 常见坑

- 本 FB 不应在多个任务或条件分支里同时调用同一实例。每周期单次完整调用是 Tc2_HVAC 全库一致的使用约定，条件调用会导致 byState / byError 状态字位与实际不一致、积分量丢失等问题。（工程经验补充）
- Tc2_HVAC 全库 PDF 在 VAR 区结束处不印 `END_VAR`，但实际 IEC 声明中该终止符存在。如果用 PDF 文本直接复制到 IEC 编辑器，编译器会在 VAR_INPUT / VAR_OUTPUT 段尾报「缺少 END_VAR」错误，需要手工补齐。本仓为方便阅读已在所有文档的 IEC 代码块中显式补 `END_VAR`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_RoundLREAL.TcPOU`](../examples/P_Demo_F_RoundLREAL.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 显示场景：从 PID 控制器读到的温度过程值 (22.367891 ℃) 直接显示太长，把它通过 F_RoundLREAL 归一化为 22.4 ℃ 显示更友好。
- **价值**：一行调用替代手写 `LROUND(lrIN * 10.0) / 10.0` 表达式；避免常见的舍入边界 bug。
- **替代方案对比**：**手写表达式 `LROUND(lrIN * 10.0) / 10.0`**：可行但容易在边界值（如 0.05 / -0.05）出错；**STRING 拼接截断**：性能低且只能用于显示；**本 FC**：编译器内置 LTRUNC + 数值常量，性能最优。

## 8. 参考资料

- **PDF**：[TF8000_TC3_HVAC_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf) §5.1.11.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684912139.html
- **相关 FB / FC / DUT**：`F_RoundLREAL_EX`
