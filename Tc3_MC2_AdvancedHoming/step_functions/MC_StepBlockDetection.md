# MC_StepBlockDetection

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_MC2_AdvancedHoming` |
| Library Version | `1.7.7` |
| Type | `FUNCTION_BLOCK` |
| Category | `Step functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_mc2_advancedhoming/427763851.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_StepBlockDetection.TcPOU`](../examples/P_Demo_MC_StepBlockDetection.TcPOU) |

---

## 1. 功能简述

**主动归零 step 函数：撞机械止挡（转矩+速度判据，Detection 版）**。搜索逻辑与 `MC_StepBlock` 相同（限矩顶止挡，转矩进容差带 + 速度持续低于限值双判据），但本 Detection 版**不改写轴位置**，而是把检测到止挡那一刻的轴位置通过 `RecordedPosition` 返回给用户。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute                : BOOL;
    Direction              : MC_Home_Direction;
    Velocity               : LREAL;
    Acceleration           : LREAL;
    Deceleration           : LREAL;
    Jerk                   : LREAL;
    DetectionVelocityLimit : LREAL;
    DetectionVelocityTime  : TIME;
    TimeLimit              : TIME;
    DistanceLimit          : LREAL;
    TorqueLimit            : LREAL;
    TorqueTolerance        : LREAL;
    BufferMode             : MC_BufferMode;
    Options                : ST_Home_Options3;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Execute` | `BOOL` | 上升沿触发一次命令执行；触发后进入处理状态，无需保持高电平 |
| `Direction` | `MC_Home_Direction` | 枚举（见 §8 数据类型）：定义搜索过程的起始运动方向（`mcPositiveDirection` / `mcNegativeDirection` / `mcSwitchPositive` / `mcSwitchNegative`） |
| `Velocity` | `LREAL` | 最大运行速度（必须 > 0） |
| `Acceleration` | `LREAL` | 加速度（≥ 0）；取 0 时采用轴配置里的标准加速度 |
| `Deceleration` | `LREAL` | 减速度（≥ 0）；取 0 时采用轴配置里的标准减速度 |
| `Jerk` | `LREAL` | 加加速度 / 急动度（≥ 0）；取 0 时采用轴配置里的标准急动度 |
| `DetectionVelocityLimit` | `LREAL` | 限制速度：实际速度必须在 `DetectionVelocityTime` 时间内持续低于此值，才判定为已顶到机械止挡 |
| `DetectionVelocityTime` | `TIME` | 判定速度跌落（顶到止挡）所需的持续时间 |
| `TimeLimit` | `TIME` | 搜索耗时超过此时间则中止搜索过程 |
| `DistanceLimit` | `LREAL` | 相对起始位置移动超过此距离则中止搜索过程 |
| `TorqueLimit` | `LREAL` | 把电机转矩限制到该值，避免撞击时损坏机械 |
| `TorqueTolerance` | `LREAL` | 相对 `TorqueLimit` 的容差；实际转矩进入该容差带才判定为顶到止挡 |
| `BufferMode` | `MC_BufferMode` | 未实现（`Not implemented`），按 PDF 说明本入口当前无效 |
| `Options` | `ST_Home_Options3` | `ST_Home_Options3` 结构：含 `DisableDriveAccess : BOOL`（同 Options2）与 `InstantLagReduction : BOOL`（顶到机械止挡后突停会产生跟随误差，置 `TRUE` 让其瞬时消除，对“软”止挡尤其有用） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis      : AXIS_REF;
    Parameter : MC_HomingParameter;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | `AXIS_REF` 轴数据结构，唯一标识系统中的一根轴，含位置、速度、错误状态等循环数据。**必须传引用**（VAR_IN_OUT 语义） |
| `Parameter` | `MC_HomingParameter` | `MC_HomingParameter` 数据结构，必须在整条归零序列的所有 FB 之间逐级传递（参数先备份、被各 FB 修改、序列结束时还原）。**必须传引用** |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done             : BOOL;
    Busy             : BOOL;
    Active           : BOOL;
    CommandAborted   : BOOL;
    Error            : BOOL;
    ErrorID          : UDINT;
    RecordedPosition : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 命令成功完成时置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后立即置 `TRUE`，命令处理期间保持 `TRUE`；变回 `FALSE` 时 FB 可接新命令，同时 `Done` / `CommandAborted` / `Error` 之一被置位 |
| `Active` | `BOOL` | 表示命令当前正在执行 |
| `CommandAborted` | `BOOL` | 命令未能完整执行（被中止）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间一旦发生错误即置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出错误号（见 §4，本库 `E_HomingErrorCodes` 段） |
| `RecordedPosition` | `LREAL` | 记录到事件（开关/脉冲/堵转）时刻的轴位置；Detection 版本不改写轴位置，而是用本输出返回检测到的位置 |

## 3. 行为说明

`Execute` 上升沿启动搜索。本 FB 驱动轴朝 `Direction` 方向运动去顶一个机械固定止挡（撞块），为避免损坏机械，运动以 `TorqueLimit` 限矩进行。成功条件由两部分组成：实际转矩进入 `TorqueTolerance` 容差带并贴近 `TorqueLimit`，且实际速度在 `DetectionVelocityTime` 内持续低于 `DetectionVelocityLimit`。区别在于按 PDF 第 3.3.4 节，本 Detection 版**不改写轴位置**，而是把检测到止挡那一刻的轴位置写入输出 `RecordedPosition` 返回（因此没有 `SetPosition` 入口）。满足上述两个条件即判定已顶到止挡。`Velocity` / `Acceleration` / `Deceleration` / `Jerk` 定义搜索运动动力学；超过 `TimeLimit` 或相对起点移动超 `DistanceLimit` 则 `CommandAborted` 置位。`Options`（`ST_Home_Options3`）的 `InstantLagReduction` 用于顶到“软”止挡突停后瞬时消除跟随误差。本 FB 在 `Homing` 状态执行、结束后保持 `Homing`，需配 `MC_FinishHoming` / `MC_AbortHoming` 收尾；`Parameter`（`MC_HomingParameter`）在序列各 FB 间逐级传递。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 取本库枚举 `E_HomingErrorCodes`（UDINT 基，PDF 第 4.1.1 节）中的值；超时 / 距离超限等中止情况则通过 `CommandAborted = TRUE` 反映而非 `Error`。`E_HomingErrorCodes` 取值：

| 错误码 | 符号名 | 含义 |
|---|---|---|
| `16#4B90` | `MC_HOMINGERROR_DRIVETYPE` | 驱动型号不受支持（支持 AX5xxx-xxxx-02xx FW≥2.05、EL7201-0000/-0001/-0010/-0011、AX8xxx 等） |
| `16#4B91` | `MC_HOMINGERROR_DIRECTION` | 参数化的方向对该 FB 不允许 |
| `16#4B92` | `MC_HOMINGERROR_SWITCHMODE` | 参数化的模式（`SwitchMode`）对该 FB 不允许 |
| `16#4B93` | `MC_HOMINGERROR_MODE` | 模式错误（PDF 未给进一步描述，⚠️ 待人工确认具体含义） |
| `16#4B94` | `MC_HOMINGERROR_TORQUEPARAMETER` | 参数化的转矩预设不允许 |
| `16#4B95` | `MC_HOMINGERROR_LAGPARAMETER` | 参数化的跟随误差不允许（< 0） |
| `16#4B96` | `MC_HOMINGERROR_DISTANCELIMIT` | 参数化的最大距离不允许（< 0） |
| `16#4B97` | `MC_HOMINGERROR_PARAMETER_ALREADYSTORED` | 已备份过参数却又以 READ 模式调用参数控制 FB |
| `16#4B98` | `MC_HOMINGERROR_PARAMETER_NOTSTORED` | 未备份参数却以 RESTORE 模式调用参数控制 FB |

除上述本库专有码外，底层 NC / 驱动错误仍可能经 `ErrorID` 透传（NC 轴错误号，非 HRESULT）；本 FB 自身不带清错入口，轴进入 Errorstop 后需先 `MC_Reset(Axis)`（Tc2_MC2）才能继续。

## 5. 使用注意 / 常见坑

- 顶撞块归零靠主动撞机械止挡完成，`TorqueLimit` 必须设得足够低以免撞坏机械，但又要高于正常搜索摩擦阻力 ⚠️。
- `Direction` 选错会朝远离止挡的方向运动，可能撞上另一侧硬限位 ⚠️。
- `DetectionVelocityTime` 太短可能在加减速波动中误判堵转；太长会延迟检测。
- “软”止挡突停产生的跟随误差较大，按需置 `Options.InstantLagReduction := TRUE` 让其瞬时消除。
- 结束后轴停在 `Homing` 且压在止挡上，收尾 FB 通常带退离 `Distance` 把轴从止挡松开（用 `MC_FinishHoming`）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_StepBlockDetection.TcPOU`](../examples/P_Demo_MC_StepBlockDetection.TcPOU)

详见上述 XML 文件，内含场景 / 价值 / 验证步骤注释，可右键 PLC 项目下 POUs 文件夹 → Add → Existing Item 导入后编译运行。

## 7. 业务场景与实际价值

- **场景**：需要先测出机械止挡相对当前坐标的实际位置（检查机械磨损 / 装配偏差），再由上层决定置零策略。
- **价值**：把“顶止挡测量”与“置零”解耦，测量值经 `RecordedPosition` 返回供上层判断。
- **替代方案对比**：`MC_StepBlock`（顶到即置零，一步到位）；`MC_StepBlockLagBasedDetection`（同为 Detection 但用跟随误差判据）。本 FB 用转矩判据并只返回位置。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf) 第 3.3.4 节（Version 1.7.7）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_mc2_advancedhoming/427763851.html
- **数据类型（本库共用）**：

本库共用的数据类型（来自 PDF 第 4 章）：

- `MC_Home_Direction`（枚举，UDINT 基）：`mcPositiveDirection := 1`（起始朝逻辑正方向）、`mcNegativeDirection := 3`（起始朝逻辑负方向）、`mcSwitchPositive := 5`、`mcSwitchNegative := 7`（后两者起始方向取决于传感器当前开关状态）。到达行程限位或开关状态变化时方向可反转。
- `MC_Switch_Mode`（枚举，UDINT 基）：`mcOn := 1`、`mcOff := 2`、`mcRisingEdge := 3`、`mcFallingEdge := 4`、`mcEdgeSwitchPositive := 5`、`mcEdgeSwitchNegative := 6`、`mcRisingEdgeInverse := 11`、`mcFallingEdgeInverse := 12`。定义搜索的结束条件。
- `MC_Ref_Signal_Ref`（结构）：`SignalSource : E_SignalSource := SignalSource_Default`（信号源，多数情况下在驱动里固定配置，取默认值）、`TouchProbe : E_TouchProbe := PlcEvent`（编码器硬件锁存单元）、`Level : BOOL`（传感器当前电平，由用户传入）。
- `ST_Home_Options`（结构）：当前为空 / 未使用。
- `ST_Home_Options2`（结构）：`DisableDriveAccess : BOOL`。
- `ST_Home_Options3`（结构）：`DisableDriveAccess : BOOL`、`InstantLagReduction : BOOL`。
- `ST_Home_Options4`（结构）：`DisableDriveAccess : BOOL`、`EnableLagErrorDetection : BOOL`。
- `MC_HomingParameter`（结构）：`Stored : BOOL`、`Nc : MC_HomingParameterNcGeneral`、`Drive : MC_HomingParameterDriveGeneral`。整条自定义归零序列必须把同一个该结构实例在所有 FB 间逐级传递（先备份、被修改、结束时还原）。
- **相关 FB**：`MC_FinishHoming` / `MC_AbortHoming`（序列收尾）、`MC_Power` / `MC_Reset`（Tc2_MC2，使能与清错）、Tc2_MC2 的 `MC_Home`（固定序列归零，与本库自定义序列互补）
