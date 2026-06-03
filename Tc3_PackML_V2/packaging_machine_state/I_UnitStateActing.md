# I_UnitStateActing

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `INTERFACE` |
| Category | `Packaging Machine State / Interfaces` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6298430859.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_I_UnitStateActing.TcPOU`](../examples/P_Demo_I_UnitStateActing.TcPOU) |

---

## 1. 功能简述

`I_UnitStateActing` 是 PackML 状态模型的**动作态（Acting）子接口**，只声明 PackML V3 中的 12 个过渡态（Transition State）回调：`M_Aborting` / `M_Clearing` / `M_Completing` / `M_Execute` / `M_Holding` / `M_Resetting` / `M_Starting` / `M_StateComplete` / `M_Stopping` / `M_Suspending` / `M_Unholding` / `M_Unsuspending`。

设计目的：让单元 FB 专注于"做事"——启动序列、清料、加热保持过渡、急停断电序列、生产主循环。等待态（Idle/Stopped/Complete/Held 等稳态）的代码可以放到 `I_UnitStateWaiting` 实现的伴生 FB 里。

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
| `M_Completing` | 生产末批收尾：执行最后清吹、归零、断料计数提交 |
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

`I_UnitStateActing` 把所有 PackML V3 定义的"过渡阶段"封装成 12 个独立钩子。每个 Acting 方法在 `PML_StateMachine` 检测到对应过渡条件后被周期调用，直到本方法（或外部条件）置位 `M_StateComplete` 表示过渡结束。

**Acting 方法的责任**：(1) 做有方向的动作（启动、停机、急停）；(2) 检测动作是否完成；(3) 在完成时把状态机引到下一稳态——这通过 `M_StateComplete` 一次性脉冲实现。

**与状态机协作的关键时序**：
- 状态机检测到命令 `ePMLCommand_Start` → 切到 `ePMLState_Starting` → 每周期调用 `M_Starting()` → 应用层做启动序列（如预热到达温度）→ 完成时置 `M_StateComplete` 返回 TRUE → 状态机切到 `ePMLState_Execute` → 周期调用 `M_Execute()`。
- 急停命令 `ePMLCommand_Abort` 优先级最高、可从任意状态切到 `ePMLState_Aborting` → 调用 `M_Aborting()` → 完成后调用 `M_StateComplete` → 进入 `ePMLState_Aborted` 稳态（由 `I_UnitStateWaiting.M_Aborted` 维持）。

**典型陷阱**：Acting 方法里如果完成条件永远不满足（例如等温度上升但加热丝坏掉）状态机就卡死；建议每个 Acting 方法配看门狗定时器，超时后向 `PML_AdminAlarm` 写故障并触发 Abort。

## 4. 错误码 / 返回值

INTERFACE 类型本身不返回值；PackML V3 建议各方法声明为无返回值的 `METHOD <name>`。

PDF + InfoSys 均未列错误码（INTERFACE 无运行时错误码概念）。

## 5. 使用注意 / 常见坑

- `M_StateComplete` 是 Acting 状态的结束信号——必须由应用层设置。忘了写它状态机会永远卡在过渡态。（工程经验补充）
- 不同 Acting 方法共享的中间变量（如温度上升中间值）放在 FB 的 VAR 段、不要做成全局变量，避免多实例污染。（工程经验补充）
- 急停 `M_Aborting` 优先级最高，应在 1 个 PLC 周期内完成关键输出复位（继电器掉电、阀门归位）；后续清理动作可以拖几个周期。（工程经验补充）
- 与 `I_UnitStateWaiting` 一同实现：一个 FB 同时 `IMPLEMENTS I_UnitStateActing, I_UnitStateWaiting` = 显式声明覆盖 19 状态，比直接 `IMPLEMENTS I_UnitState` 语义更清晰。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_I_UnitStateActing.TcPOU`](../examples/P_Demo_I_UnitStateActing.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：一条贴标流水线包含主贴标模块（`FB_LabelActor`）。设计阶段把"做事"集中到这个 FB——启动序列写在 `M_Starting`（贴头预热到 80°C、传送带启动到额定速度）；生产主循环写在 `M_Execute`（每个工件到位时下发贴标动作）；急停写在 `M_Aborting`（贴头抬起、传送带停止、留下当前工件位置）。维持类逻辑（Idle 待命态、Stopped 停机态）由独立的 `FB_LabelKeeper` 实现 `I_UnitStateWaiting`。
- **价值**：本接口让"过渡动作"模块化。新工艺只需替换 Acting FB，状态机和 Waiting FB 都不动。代码审阅时一眼看出"启动序列怎么走、急停时序怎么排"。
- **替代方案对比**：直接 `IMPLEMENTS I_UnitState` 强制 19 方法骨架，文件冗长；自己写 case 状态机不强制覆盖、容易遗漏分支。本子接口在编译期就把"只能做动作"的责任固化，是 PackML V3 推荐用法。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6298430859.html
- **相关**：`I_UnitState`（完整 19 方法）、`I_UnitStateWaiting`（等待态 7 方法，与本接口互补）、`PML_StateMachine`、`E_PMLState`、`E_PMLCommand`
