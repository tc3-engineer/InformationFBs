# I_PMLUnitStateWaiting

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V3` |
| Library Version | `1.0.0` |
| Type | `INTERFACE` |
| Category | `Interfaces` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003677835.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_I_PMLUnitStateWaiting.TcPOU`](../examples/P_Demo_I_PMLUnitStateWaiting.TcPOU) |

---

## 1. 功能简述

`I_PMLUnitStateWaiting` 是 PackML V3 状态模型的**等待态（Waiting）子接口**，只声明 PackML V3 中的 7 个稳态（Steady State）回调：`M_Aborted` / `M_Completed` / `M_Held` / `M_Idle` / `M_Stopped` / `M_Suspended` / `M_Undefined`。

**V3 与 V2 的关键差异**：
- **接口命名**：V2 叫 `I_UnitStateWaiting`，V3 改名 `I_PMLUnitStateWaiting`（统一加 PML 前缀）。
- **方法名带"d"后缀**：方法名表达"已到达某稳态"的语义，如 `M_Aborted`（已急停 ✓）/ `M_Completed`（已完成 ✓）/ `M_Held`（已保持 ✓）。Acting 用现在分词（-ing）表达"正在做"，Waiting 用过去分词（-ed）表达"已到达"。

设计目的：让单元 FB 把"维持稳态"的代码（如 Aborted 态下 LED 闪烁报警、Stopped 态下安全输出锁存、Idle 态下传感器监控）和"做事"的 Acting 代码分离。

## 2. 接口定义

### VAR_INPUT

无（INTERFACE 不声明 VAR_INPUT/OUTPUT/IN_OUT）。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

### 方法列表（7 个）

| 方法 | 含义 |
|---|---|
| `M_Aborted` | 急停稳态保持：维持急停 LED 闪烁、报警喇叭、关键输出复位锁存 |
| `M_Completed` | 批次完成稳态保持：维持"批次完成"指示、等待操作员确认 |
| `M_Held` | Held 稳态保持：保持工件温度/位置、等待 Unhold |
| `M_Idle` | Idle 稳态保持：监控传感器、等待 Start 命令、循环准备 |
| `M_Stopped` | Stopped 稳态保持：所有运动输出关闭、安全输出锁存、等待 Reset |
| `M_Suspended` | Suspended 稳态保持：保持当前工件位置、等待 Unsuspend |
| `M_Undefined` | Undefined（上电默认）稳态保持：等待第一个 Reset 命令进 Idle |

## 3. 行为说明

`I_PMLUnitStateWaiting` 把所有 PackML V3 定义的"稳态"封装成 7 个独立钩子。每个 Waiting 方法在 `FB_PMLStateMachine` 处于对应稳态时被周期调用——稳态可能持续很长时间（如 Stopped 一夜），方法每周期都被调用以维持该态需要的输出。

**Waiting 方法的责任**：(1) 维持该态需要的恒定输出（LED / 阀门 / 输出锁存）；(2) 周期性自检（在 Idle 态监控传感器是否健康）；(3) 不主动触发状态切换（切换由 HMI 命令或 Acting 完成事件驱动）。

**与状态机协作的关键时序**：
- 状态机切到 `E_PMLState.Aborted` → 每周期调用 `M_Aborted()` → 应用层维持急停指示、报警喇叭、安全输出。
- 操作员发 `E_PMLCommand.Clear` → 状态机切到 `E_PMLState.Clearing` → 调用 Acting 接口的 `M_Clearing()`（不是 Waiting）→ 完成后进入 `E_PMLState.Stopped` 稳态 → 周期调用 `M_Stopped()`。
- HMI 命令 `Reset` → Acting `M_Resetting()` → Waiting `M_Idle()` 稳态。

**与 Acting 互补**：Acting 方法做"切换中"的动作；Waiting 方法做"已到达"的维持。一个应用 FB 同时 `IMPLEMENTS I_PMLUnitStateActing, I_PMLUnitStateWaiting` 就能覆盖 PackML V3 全部 19 个状态钩子。

## 4. 错误码 / 返回值

INTERFACE 类型本身不返回值；PackML V3 建议各方法声明为无返回值的 `METHOD <name>`。

PDF 未列错误码（INTERFACE 无运行时错误码概念）。

## 5. 使用注意 / 常见坑

- Waiting 方法被**每周期调用**——里面不要做长耗时操作，只维持状态需要的恒定输出。（工程经验补充）
- `M_Stopped` 必须把所有运动输出明确关闭——这是 PackML 标准的安全约定。
- `M_Aborted` 比 `M_Stopped` 更严格——需要锁存安全输出（如急停继电器），只能通过 Acting 的 `M_Clearing` 才能解锁。
- `M_Undefined` 通常什么都不做，只等首次 Reset；应用 FB 可以选择留空实现。
- V3 没有 `I_UnitState` 全集接口——想覆盖 19 方法骨架直接 `IMPLEMENTS I_PMLUnitStateActing, I_PMLUnitStateWaiting`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_I_PMLUnitStateWaiting.TcPOU`](../examples/P_Demo_I_PMLUnitStateWaiting.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：贴标流水线的 `FB_LabelKeeper` 实现本接口——`M_Idle` 周期巡检贴头传感器是否在线、`M_Stopped` 关闭传送带输出 + 锁存安全继电器、`M_Aborted` 维持急停 LED 闪烁 + 等待 Clear、`M_Completed` 维持"批次完成"指示给 HMI。
- **价值**：稳态维持代码与过渡动作代码（Acting）分离——读 `M_Stopped` 能立刻知道停机时机器输出长什么样；不必读 `M_Stopping`（过渡）才能猜出。代码审阅和故障诊断都简单。
- **替代方案对比**：在 Acting 里既写过渡又写稳态——代码混杂、读不出"稳态时机器是什么样"；本接口强制分离责任。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §8.2
- **InfoSys 参考 topic（同 FB_PMLStateMachine）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003677835.html （状态机 topic 包含 PML 状态语义介绍；本 INTERFACE 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`I_PMLUnitStateActing`（动作态 12 方法，与本接口互补）、`FB_PMLStateMachine`、`E_PMLState`（7 个稳态分别对应本接口 7 个方法）

## 9. 待确认项 (⚠️)

- V3 INTERFACE 各方法的具体签名（参数列表、返回类型）PDF 只列出方法名清单，未给签名 ⚠️——实测以 PLC 编辑器自动生成的方法骨架为准。
- V3 InfoSys 本 INTERFACE 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
