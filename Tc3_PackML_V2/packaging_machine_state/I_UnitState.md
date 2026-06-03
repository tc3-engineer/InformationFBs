# I_UnitState

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `INTERFACE` |
| Category | `Packaging Machine State / Interfaces` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6298407051.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_I_UnitState.TcPOU`](../examples/P_Demo_I_UnitState.TcPOU) |

---

## 1. 功能简述

`I_UnitState` 是 PackML（包装机械语言，Packaging Machine Language）状态模型的**全集接口**，声明 PackML V3 标准定义的 **19 个状态钩子方法**。应用层的"单元功能块（Unit FB）"通过实现本接口，把每个状态对应的机器动作（启动准备、清料、加热保持、急停等）填入对应方法体内。`PML_StateMachine` 中央状态机以多态方式调用这些方法，从而把"状态决策"与"机器执行代码"完全解耦。

实现 `I_UnitState` 等于一次性承诺所有 19 个状态都可能被驱动；如果某些状态不需要逻辑可使用方法体为空的占位，或改用更小的子接口 `I_UnitStateWaiting` / `I_UnitStateActing`。

## 2. 接口定义

### VAR_INPUT

无（INTERFACE 类型不声明 VAR_INPUT/OUTPUT/IN_OUT；接口只列方法签名，参数由各方法自行定义）。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

### 方法列表（19 个）

按 PackML 三态分类（Acting 动作态 / Waiting 等待态 / 公共态）：

| 方法 | PackML 分类 | 含义 |
|---|---|---|
| `M_Aborted` | Waiting | 机器进入 Aborted 安全停态后周期回调，用于维持急停后的输出状态 |
| `M_Aborting` | Acting | 收到 Abort 命令后过渡阶段：紧急切断输出、停止运动、释放工件 |
| `M_Clearing` | Acting | 从 Aborted 退出时清理残留状态、复位故障锁存、准备下一次 Reset |
| `M_Complete` | Waiting | 已完成一次生产循环、等待操作员复位的稳态 |
| `M_Completing` | Acting | 完成最后一件产品后过渡阶段：执行收尾动作（吹扫、归零等）|
| `M_Execute` | Acting | 正式生产态，加工每件产品的主循环代码 |
| `M_Held` | Waiting | 主动暂停态（材料缺料、上游故障）的稳态 |
| `M_Holding` | Acting | 进入 Held 的过渡阶段：减速、保持当前工件、关闭加热等 |
| `M_Idle` | Waiting | 准备就绪、等待 Start 的稳态 |
| `M_Resetting` | Acting | 从 Stopped/Complete/Aborted 恢复到 Idle 的过渡阶段：归位、清缓存 |
| `M_Starting` | Acting | 收到 Start 后到进入 Execute 之间的预热/启动序列 |
| `M_StateComplete` | Acting | 当前 Acting 状态执行完毕、状态机即将切换的回调（一次性脉冲）|
| `M_Stopped` | Waiting | 操作员主动停机后的稳态 |
| `M_Stopping` | Acting | 进入 Stopped 的过渡阶段：受控停机、关闭辅助 |
| `M_Suspended` | Waiting | 被外部条件挂起态（上游堵料、下游饱和）的稳态 |
| `M_Suspending` | Acting | 进入 Suspended 的过渡阶段：临时停止进料、保持工件 |
| `M_Undefined` | 公共 | 未初始化或非法状态时的兜底回调 |
| `M_Unholding` | Acting | 从 Held 恢复到 Execute 的过渡阶段：重新加热、重新加速 |
| `M_Unsuspending` | Acting | 从 Suspended 恢复到 Execute 的过渡阶段：恢复进料 |

## 3. 行为说明

`I_UnitState` 把 PackML V3 标准定义的"状态—行为"映射变成 PLC 接口契约。

**调用关系**：`PML_StateMachine` 中央状态机持有一个 `I_UnitState` 引用，每个 PLC 扫描周期根据当前状态多态分派到对应方法。例如：状态机当前 `eState = ePMLState_Execute` 时，状态机调用 `M_Execute()`；切换瞬间调用一次 `M_StateComplete()` 后才允许进入下一个状态。开发者把每个状态需要做的事情写在对应方法体里——例如把上游气缸控制、传感器扫描、产品计数等写入 `M_Execute`，把急停时的安全输出写入 `M_Aborting`。

**Acting vs Waiting 区分**：Acting（动作）方法在过渡过程中被反复调用直到 `M_StateComplete` 返回；Waiting（等待）方法在稳态期间被反复调用直到收到状态切换命令。Acting 用于做事情，Waiting 用于维持状态。

**典型用法**：在自定义 FB 头部声明 `IMPLEMENTS I_UnitState;`，IDE 自动生成 19 个方法骨架；按生产工艺往里填代码；然后在 `PML_StateMachine` 实例化时把本 FB 作为 `I_UnitState` 引用注入。这样状态机本身不需要修改、不同机型只需替换单元 FB。

**典型陷阱**：在 Acting 方法里如果忘记设置完成条件、`M_StateComplete` 永远不返回 TRUE，状态机会卡在过渡态；在 Waiting 方法里如果包含非幂等逻辑（如递增计数）会导致每周期重复执行；用 `M_Undefined` 兜住未初始化状态有助于排查上电时序问题。

## 4. 错误码 / 返回值

INTERFACE 类型本身不返回值。各方法的返回类型由实现者自定，但 PackML V3 标准建议所有钩子方法声明为 `METHOD <name>` 不带返回值（隐式 `VOID`），状态切换由中央状态机判定，不由方法返回值控制。

PDF + InfoSys 均未列错误码，因 INTERFACE 无运行时错误码概念。

## 5. 使用注意 / 常见坑

- 实现 `I_UnitState` 必须实现**全部 19 个方法**，缺一会编译报错。如果只需要 Waiting 或 Acting 子集，改用 `I_UnitStateWaiting` / `I_UnitStateActing` 缩减义务。（工程经验补充）
- 方法体里不要做长耗时操作（如阻塞 ADS 调用）——状态机在 PLC 任务周期内调用本方法，耗时操作会拖慢扫描周期。需要异步动作请用独立的后台 FB + Done/Busy 协调。（工程经验补充）
- `M_StateComplete` 是 Acting 状态退出条件，写法常用 latch+计时器或外部 Done 信号；不写它状态机会一直停在 Acting。（工程经验补充）
- 同一个 Unit FB 不要同时 `IMPLEMENTS I_UnitState` 和 `IMPLEMENTS I_UnitStateWaiting`，方法签名重复会有歧义。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_I_UnitState.TcPOU`](../examples/P_Demo_I_UnitState.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：一台带预热/灌装/封口/标签贴附的多工位灌装机，按照 ISA-TR88/PackML V3 标准实现 Idle→Starting→Execute→Completing→Complete 主循环 + Holding/Held + Suspending/Suspended 维护态分支。设备工程师把每个工位的 PLC 程序写成一个 `FB_FillingUnit IMPLEMENTS I_UnitState`，由统一的 `PML_StateMachine` 调度。
- **价值**：使用本接口后，机器逻辑被 19 个独立方法精确划分，新人也能立即看懂"启动序列在 M_Starting 里、急停安全输出在 M_Aborting 里、生产主循环在 M_Execute 里"。状态切换由 PackML 标准状态机保证，工程师不必手写 case 语句和状态迁移条件。
- **替代方案对比**：不用接口而手写 `CASE eState OF ePMLState_Execute: ...; ePMLState_Aborting: ...;` 也能实现，但缺点是：(1) 不同设备的 case 分支结构不一致，跨机型维护困难；(2) 容易遗漏状态分支造成跑飞；(3) 没法编译期检查覆盖完整。INTERFACE 强制全覆盖、按方法独立编辑，是 OMAC PackML V3 标准的官方实现路径。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6298407051.html
- **相关**：`I_UnitStateWaiting`（仅 Waiting 子集）、`I_UnitStateActing`（仅 Acting 子集）、`PML_StateMachine`（消费本接口的中央状态机）、`E_PMLState` / `E_PMLCommand`（状态/命令枚举）
