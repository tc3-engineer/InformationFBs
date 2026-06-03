# I_PMLUnitStateActing

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
| Example | [`examples/P_Demo_I_PMLUnitStateActing.TcPOU`](../examples/P_Demo_I_PMLUnitStateActing.TcPOU) |

---

## 1. 功能简述

`I_PMLUnitStateActing` 是 PackML V3 状态模型的**动作态（Acting）子接口**，只声明 PackML V3 中的 12 个过渡态（Transition State）回调：`M_Aborting` / `M_Clearing` / `M_Completing` / `M_Execute` / `M_Holding` / `M_Resetting` / `M_Starting` / `M_StateComplete` / `M_Stopping` / `M_Suspending` / `M_Unholding` / `M_Unsuspending`。

**V3 与 V2 的关键差异**：
- **接口命名**：V2 叫 `I_UnitStateActing`，V3 改名 `I_PMLUnitStateActing`（统一加 PML 前缀）。
- **V3 不再有 `I_UnitState` 全集接口**：V2 提供"全集 19 方法"的 `I_UnitState` + 两个子接口（Acting/Waiting）；V3 简化为只保留两个子接口，应用 FB 想覆盖全部 19 方法骨架时直接 `IMPLEMENTS I_PMLUnitStateActing, I_PMLUnitStateWaiting` 两个一起实现。

设计目的：让单元 FB 专注于"做事"——启动序列、清料、加热保持过渡、急停断电序列、生产主循环。等待态（Idle / Stopped / Complete / Held 等稳态）的代码可以放到 `I_PMLUnitStateWaiting` 实现的伴生 FB 里。

## 2. 接口定义

### VAR_INPUT

无（INTERFACE 不声明 VAR_INPUT/OUTPUT/IN_OUT）。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

### 方法列表（12 个）

| 方法 | 含义 |
|---|---|
| `M_Aborting` | 急停过渡：紧急切电、停止运动、释放工件、关闭加热 |
| `M_Clearing` | Aborted → Stopped 过渡：清除故障锁存、复位安全继电器、清理残留 |
| `M_Completing` | 生产末批收尾：执行最后清吹、归零、断料计数提交（V3 新增的"批结束"序列）|
| `M_Execute` | 生产主循环：加工每件产品的核心代码（搬运、加工、计数）|
| `M_Holding` | Execute → Held 过渡：减速到工艺允许的暂停位、关阀、维持工件温度 |
| `M_Resetting` | Stopped/Complete/Aborted → Idle 过渡：归位、清缓存、传感器自检 |
| `M_Starting` | Idle → Execute 过渡：预热、加压、上料准备 |
| `M_StateComplete` | Acting 状态完成脉冲：告诉状态机本过渡结束、允许进入下一稳态 |
| `M_Stopping` | 操作员停机过渡：受控减速、安全断料、关辅助 |
| `M_Suspending` | Execute → Suspended 过渡：临时停料、保持工件 |
| `M_Unholding` | Held → Execute 过渡：重新加热、加速到生产速度 |
| `M_Unsuspending` | Suspended → Execute 过渡：恢复进料、重启传感器扫描 |

## 3. 行为说明

`I_PMLUnitStateActing` 把所有 PackML V3 定义的"过渡阶段"封装成 12 个独立钩子。每个 Acting 方法在 `FB_PMLStateMachine` 检测到对应过渡条件后被周期调用，直到本方法（或外部条件）置位 `M_StateComplete` 表示过渡结束。

**Acting 方法的责任**：(1) 做有方向的动作（启动、停机、急停）；(2) 检测动作是否完成；(3) 在完成时把状态机引到下一稳态——这通过 `M_StateComplete` 一次性脉冲实现。

**与状态机协作的关键时序**：
- 状态机检测到命令 `E_PMLCommand.Start` → 切到 `E_PMLState.Starting` → 每周期调用 `M_Starting()` → 应用层做启动序列（如预热到达温度）→ 完成时置 `M_StateComplete` 返回 TRUE → 状态机切到 `E_PMLState.Execute` → 周期调用 `M_Execute()`。
- 急停命令 `E_PMLCommand.Abort` 优先级最高、可从任意状态切到 `E_PMLState.Aborting` → 调用 `M_Aborting()` → 完成后调用 `M_StateComplete` → 进入 `E_PMLState.Aborted` 稳态（由 `I_PMLUnitStateWaiting.M_Aborted` 维持）。
- V3 新增 Complete 流程：`E_PMLCommand.Complete` → `E_PMLState.Completing` → 调用 `M_Completing()` → 完成后进入 `E_PMLState.Completed` 稳态。

**典型陷阱**：Acting 方法里如果完成条件永远不满足（例如等温度上升但加热丝坏掉）状态机就卡死；建议每个 Acting 方法配看门狗定时器，超时后向 `FB_PMLAdminAlarm` 写故障并触发 Abort。

## 4. 错误码 / 返回值

INTERFACE 类型本身不返回值；PackML V3 建议各方法声明为无返回值的 `METHOD <name>`。

PDF 未列错误码（INTERFACE 无运行时错误码概念）。

## 5. 使用注意 / 常见坑

- `M_StateComplete` 是 Acting 状态的结束信号——必须由应用层设置。忘了写它状态机会永远卡在过渡态。（工程经验补充）
- 不同 Acting 方法共享的中间变量（如温度上升中间值）放在 FB 的 VAR 段、不要做成全局变量，避免多实例污染。（工程经验补充）
- 急停 `M_Aborting` 优先级最高，应在 1 个 PLC 周期内完成关键输出复位（继电器掉电、阀门归位）；后续清理动作可以拖几个周期。（工程经验补充）
- V3 没有 `I_UnitState` 全集接口——想覆盖全部 19 方法直接 `IMPLEMENTS I_PMLUnitStateActing, I_PMLUnitStateWaiting`。
- 与 `I_PMLUnitStateWaiting` 一同实现：一个 FB 同时 `IMPLEMENTS I_PMLUnitStateActing, I_PMLUnitStateWaiting` = 显式声明覆盖 19 状态（12 Acting + 7 Waiting）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_I_PMLUnitStateActing.TcPOU`](../examples/P_Demo_I_PMLUnitStateActing.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：一条贴标流水线包含主贴标模块（`FB_LabelActor`）。设计阶段把"做事"集中到这个 FB——启动序列写在 `M_Starting`（贴头预热到 80°C、传送带启动到额定速度）；生产主循环写在 `M_Execute`（每个工件到位时下发贴标动作）；急停写在 `M_Aborting`（贴头抬起、传送带停止、留下当前工件位置）。维持类逻辑（Idle 待命态、Stopped 停机态）由独立的 `FB_LabelKeeper` 实现 `I_PMLUnitStateWaiting`。
- **价值**：本接口让"过渡动作"模块化。新工艺只需替换 Acting FB，状态机和 Waiting FB 都不动。代码审阅时一眼看出"启动序列怎么走、急停时序怎么排"。V3 比 V2 简化了接口体系——少一个 I_UnitState 全集，应用模型更清晰。
- **替代方案对比**：直接 `IMPLEMENTS` 全集 19 方法骨架（V3 没了，V2 有）文件冗长；自己写 case 状态机不强制覆盖、容易遗漏分支。本子接口在编译期就把"只能做动作"的责任固化，是 PackML V3 推荐用法。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §8.1
- **InfoSys 参考 topic（同 FB_PMLStateMachine）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003677835.html （状态机 topic 包含 PML 状态语义介绍；本 INTERFACE 自身 InfoSys topic 页面未公网检索到，已标 ⚠️ not-on-infosys）
- **相关**：`I_PMLUnitStateWaiting`（等待态 7 方法，与本接口互补）、`FB_PMLStateMachine`、`E_PMLState`、`E_PMLCommand`

## 9. 待确认项 (⚠️)

- V3 INTERFACE 各方法的具体签名（参数列表、返回类型）PDF 只列出方法名清单，未给签名 ⚠️——实测以 PLC 编辑器自动生成的方法骨架为准。
- V3 InfoSys 本 INTERFACE 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
