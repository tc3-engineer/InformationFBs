# MC_StepReferencePulseDetection

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_MC2_AdvancedHoming` |
| Library Version | `1.7.7` |
| Type | `FUNCTION_BLOCK` |
| Category | `Step functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_mc2_advancedhoming/427785867.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_StepReferencePulseDetection.TcPOU`](../examples/P_Demo_MC_StepReferencePulseDetection.TcPOU) |

---

## 1. 功能简述

**主动归零 step 函数：搜索编码器零脉冲并仅返回检测位置（Detection 版）**。搜索逻辑与 `MC_StepReferencePulse` 相同（驱动轴找编码器零脉冲），但本 Detection 版**不改写轴位置**，而是把命中零脉冲那一刻的轴位置通过 `RecordedPosition` 返回给用户。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute         : BOOL;
    Direction       : MC_Home_Direction;
    SwitchMode      : MC_Switch_Mode;
    ReferenceSignal : MC_Ref_Signal_Ref;
    Velocity        : LREAL;
    Acceleration    : LREAL;
    Deceleration    : LREAL;
    Jerk            : LREAL;
    TimeLimit       : TIME;
    DistanceLimit   : LREAL;
    TorqueLimit     : LREAL;
    BufferMode      : MC_BufferMode;
    Options         : ST_Home_Options4;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Execute` | `BOOL` | 上升沿触发一次命令执行；触发后进入处理状态，无需保持高电平 |
| `Direction` | `MC_Home_Direction` | 枚举（见 §8 数据类型）：定义搜索过程的起始运动方向（`mcPositiveDirection` / `mcNegativeDirection` / `mcSwitchPositive` / `mcSwitchNegative`） |
| `SwitchMode` | `MC_Switch_Mode` | `MC_Switch_Mode` 枚举（见 §8）：定义搜索过程的结束条件（`mcOn` / `mcOff` / `mcRisingEdge` / `mcFallingEdge` / `mcEdgeSwitchPositive` / `mcEdgeSwitchNegative` / `mcRisingEdgeInverse` / `mcFallingEdgeInverse`） |
| `ReferenceSignal` | `MC_Ref_Signal_Ref` | `MC_Ref_Signal_Ref` 结构：定义参考信号源（锁存单元 `TouchProbe`、信号源 `SignalSource`、当前电平 `Level`），见 §8 |
| `Velocity` | `LREAL` | 最大运行速度（必须 > 0） |
| `Acceleration` | `LREAL` | 加速度（≥ 0）；取 0 时采用轴配置里的标准加速度 |
| `Deceleration` | `LREAL` | 减速度（≥ 0）；取 0 时采用轴配置里的标准减速度 |
| `Jerk` | `LREAL` | 加加速度 / 急动度（≥ 0）；取 0 时采用轴配置里的标准急动度 |
| `TimeLimit` | `TIME` | 搜索耗时超过此时间则中止搜索过程 |
| `DistanceLimit` | `LREAL` | 相对起始位置移动超过此距离则中止搜索过程 |
| `TorqueLimit` | `LREAL` | 把电机转矩限制到该值，避免撞击时损坏机械 |
| `BufferMode` | `MC_BufferMode` | 未实现（`Not implemented`），按 PDF 说明本入口当前无效 |
| `Options` | `ST_Home_Options4` | `ST_Home_Options4` 结构：含 `DisableDriveAccess : BOOL`（同 Options2）与 `EnableLagErrorDetection : BOOL`（step 函数默认关闭跟随误差监控以保证平顺，置 `TRUE` 可在搜索期间保持跟随误差监控） |

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

`Execute` 上升沿启动搜索。搜索过程与 `MC_StepReferencePulse` 一致：按 `Direction` 起始方向、`Velocity` / `Acceleration` / `Deceleration` / `Jerk` 动力学驱动轴找编码器零脉冲，`ReferenceSignal` 通过 `TouchProbe` 锁存单元等待零脉冲，`TorqueLimit` 限矩。区别在于按 PDF 第 3.3.10 节，本 Detection 版**不改写轴位置**，而是把命中零脉冲那一刻的轴位置写入输出 `RecordedPosition` 返回（因此没有 `SetPosition` 入口）。`Done = TRUE` 表示检测成功并已给出 `RecordedPosition`；超过 `TimeLimit` / `DistanceLimit` 则 `CommandAborted` 置位。本 FB 在 `Homing` 状态执行、结束后保持 `Homing`，需配收尾 FB；`Parameter` 在序列各 FB 间逐级传递。⚠️ 提示：PDF 第 3.3.10 节正文的 `VAR_INPUT` 代码块多印了一个 `SwitchMode : MC_Switch_Mode`（本文档 §2 逐字照搬保留），但同节的接口图与参数说明表均无此入口；零脉冲检测的结束条件是“命中零脉冲”，并不需要 `SwitchMode`，该入口系 PDF 代码块多余项，工程中可忽略。

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

- 本 FB**不改写轴位置**，只给出 `RecordedPosition`；若忘了用它去置零，轴仍未真正校准 ⚠️。
- 零脉冲并非所有编码器都有，用前确认编码器输出零脉冲且已正确链接 ⚠️。
- 通常先粗定位再用本 FB 在小范围检测零脉冲，避免一次跨多个零脉冲。
- `ReferenceSignal.TouchProbe` 必须选对应零脉冲的锁存单元。
- 结束后轴停在 `Homing`，仍需收尾 FB。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_StepReferencePulseDetection.TcPOU`](../examples/P_Demo_MC_StepReferencePulseDetection.TcPOU)

详见上述 XML 文件，内含场景 / 价值 / 验证步骤注释，可右键 PLC 项目下 POUs 文件夹 → Add → Existing Item 导入后编译运行。

## 7. 业务场景与实际价值

- **场景**：需要先测出编码器零脉冲相对当前坐标的精确位置（编码器安装相位标定 / 多轴零脉冲对齐），再决定置零策略。
- **价值**：以编码器级精度测出零脉冲位置并返回，把高精度测量与置零解耦。
- **替代方案对比**：`MC_StepReferencePulse`（命中即置零）；`MC_StepReferenceFlyingRefPulse`（飞行版）。需要拿零脉冲测量值做相位标定 / 对齐时用本 Detection 版。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf) 第 3.3.10 节（Version 1.7.7）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_mc2_advancedhoming/427785867.html
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
