# I_UnitStateWaiting

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `INTERFACE` |
| Category | `Packaging Machine State / Interfaces` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6298422923.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_I_UnitStateWaiting.TcPOU`](../examples/P_Demo_I_UnitStateWaiting.TcPOU) |

---

## 1. 功能简述

`I_UnitStateWaiting` 是 PackML 状态模型的**等待态（Waiting）子接口**，只声明 PackML V3 中的 7 个稳态（Steady State）回调：`M_Aborted` / `M_Complete` / `M_Held` / `M_Idle` / `M_Stopped` / `M_Suspended` / `M_Undefined`。

设计目的：让单元 FB 只关心"机器停在某态时该维持什么输出/做什么周期性检查"，不必实现完整 `I_UnitState` 的 19 个方法。等待态方法仅用于状态维持，不能在内部做状态切换；状态切换由外部命令驱动。

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
| `M_Aborted` | 急停后稳态：维持安全输出（夹爪松开、加热关闭、阀门归位），等待操作员清警 |
| `M_Complete` | 一次生产完成后稳态：保持成品在出口、显示完成提示、等待 Reset |
| `M_Held` | 主动暂停稳态：保持中间产品在工位、加热保温、等待 Unhold |
| `M_Idle` | 待命稳态：所有动作复位、传感器周期扫描就绪、等待 Start |
| `M_Stopped` | 操作员停机后稳态：保留状态信息、关辅助设备、等待 Reset |
| `M_Suspended` | 外部条件挂起稳态（上游堵料 / 下游饱和）：保持当前工件、轮询恢复条件 |
| `M_Undefined` | 未初始化或非法状态兜底：写默认输出、记日志 |

## 3. 行为说明

`I_UnitStateWaiting` 用于场景：单元 FB 不关心过渡动作、只关心稳态维持。例如：一个上料模块只在 Idle 稳态做"传感器扫描判断料盘是否满"、在 Held 稳态做"保温丝 PID 控制"、在 Stopped 稳态写"待机记录"——其他过渡态由父模块或专用的 Acting 模块处理。

**周期调用语义**：所有 Waiting 方法在状态机停留在对应稳态时每个 PLC 周期被调一次。方法体应当**幂等**——不能假设是首次进入还是第二个周期，建议用边沿检测包裹一次性动作。

**与 PML_StateMachine 的协作**：`PML_StateMachine` 内部根据 `eMode + eCommand + 子单元反馈` 决定稳态切换。Waiting 方法没有返回值或返回值不影响状态切换。状态切换仅由命令（`E_PMLCommand`）和子单元状态汇总（`ST_PMLSubUnitInfoRef`）触发。

**典型场景**：与 `I_UnitStateActing` 配合使用——把"做事的活"和"等的活"分到不同的 FB，前者实现 Acting 接口、后者实现 Waiting 接口。这样新设备只需重写关心的那一块。

**典型陷阱**：在 Waiting 方法里启动一个长时间运动（不是稳态行为）会破坏 PackML 状态语义——应该把长动作放到对应的 Acting 方法里（例如启动序列写在 `M_Starting` 而非 `M_Idle`）。

## 4. 错误码 / 返回值

INTERFACE 类型本身不返回值。各方法 PackML V3 建议声明为 `METHOD <name>` 无返回值。

PDF + InfoSys 均未列错误码（INTERFACE 无运行时错误码概念）。

## 5. 使用注意 / 常见坑

- Waiting 方法不应包含状态切换条件判断——状态切换由命令和子单元反馈在 `PML_StateMachine` 内部决定。（工程经验补充）
- 维持类输出（保温、保压、安全输出）适合写在 Waiting 方法；一次性动作（启动序列、清料）写在 Acting 方法。（工程经验补充）
- 同一个 Unit FB 可以同时 `IMPLEMENTS I_UnitStateWaiting, I_UnitStateActing`——本接口 + Acting 接口的方法签名不冲突。（工程经验补充）
- `M_Undefined` 是兜底回调，建议至少写一行 LOG 输出帮助排查异常上电时序。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_I_UnitStateWaiting.TcPOU`](../examples/P_Demo_I_UnitStateWaiting.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：一台多模块灌装机，主灌装模块（`FB_FillingActor`）专心做 Acting 过渡逻辑、辅助保温模块（`FB_TempKeeper`）专心做 Waiting 稳态控温。后者声明 `IMPLEMENTS I_UnitStateWaiting`，把 PID 控温写入 `M_Held` 和 `M_Idle`、把停机断电写入 `M_Stopped`、把急停安全断电写入 `M_Aborted`。
- **价值**：模块化清晰——保温逻辑 7 个方法、灌装逻辑 12 个方法、互不耦合。如果工艺更换需要改控温策略，只动 `FB_TempKeeper` 就行，灌装代码不受影响。
- **替代方案对比**：直接实现 `I_UnitState` 强制 19 个方法骨架——文件冗长、容易把维持逻辑写到 Acting 里造成状态语义混乱。用本子接口在编译期就把"只能做维持"的约束固化下来。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6298422923.html
- **相关**：`I_UnitState`（完整 19 方法）、`I_UnitStateActing`（动作态 12 方法，与本接口互补）、`PML_StateMachine`、`E_PMLState`
