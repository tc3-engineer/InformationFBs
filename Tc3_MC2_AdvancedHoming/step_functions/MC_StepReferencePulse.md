# MC_StepReferencePulse

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_MC2_AdvancedHoming` |
| Library Version | `1.7.7` |
| Type | `FUNCTION_BLOCK` |
| Category | `Step functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_mc2_advancedhoming/427784331.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_StepReferencePulse.TcPOU`](../examples/P_Demo_MC_StepReferencePulse.TcPOU) |

---

## 1. 功能简述

**主动归零 step 函数：搜索编码器零脉冲（reference pulse）**。它驱动轴朝 `Direction` 方向运动去寻找编码器的零脉冲（每转一次、并非所有编码器都有）。零脉冲信号精度远高于普通传感器，是高精度归零的常用参考。命中零脉冲后把轴位置设为 `SetPosition`。本 FB 在 `Homing` 状态执行，结束后保持 `Homing`，需配收尾 FB。

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
    SetPosition     : LREAL;
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
| `SetPosition` | `LREAL` | 搜索成功后把轴的当前位置设为该值（绝对零点） |
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
    Done           : BOOL;
    Busy           : BOOL;
    Active         : BOOL;
    CommandAborted : BOOL;
    Error          : BOOL;
    ErrorID        : UDINT;
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

## 3. 行为说明

`Execute` 上升沿启动搜索。按 PDF 第 3.3.9 节，本 FB 主动驱动轴去找编码器零脉冲：起始方向由 `Direction`（`MC_Home_Direction`）决定，轴按 `Velocity` / `Acceleration` / `Deceleration` / `Jerk` 运动，`TorqueLimit` 限矩，`ReferenceSignal`（`MC_Ref_Signal_Ref`）通过 `TouchProbe` 锁存单元等待零脉冲。零脉冲是每转一次的高精度信号，命中那一刻把轴位置设为 `SetPosition`，`Done = TRUE`。step 函数默认关闭跟随误差监控（可经 `Options.EnableLagErrorDetection` 打开）。超过 `TimeLimit` 或相对起点移动超 `DistanceLimit` 则 `CommandAborted` 置位。本 FB 在 `Homing` 状态执行、结束后保持 `Homing`，需配 `MC_FinishHoming` / `MC_AbortHoming` 收尾；`Parameter` 在序列各 FB 间逐级传递。⚠️ 提示：PDF 第 3.3.9 节正文的 `VAR_INPUT` 代码块多印了一个 `SwitchMode : MC_Switch_Mode`（本文档 §2 逐字照搬保留），但同节的接口图与参数说明表均无此入口；零脉冲搜索的结束条件是“命中零脉冲”，并不需要 `SwitchMode`，该入口系 PDF 代码块多余项，工程中可忽略。

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

- 零脉冲并非所有编码器都有；用本 FB 前要确认编码器确实输出零脉冲且已在驱动 / NC 中正确链接 ⚠️。
- 通常先用开关 / 限位 step 粗定位到零脉冲附近，再用本 FB 在小范围内精确锁零脉冲，否则一次搜索可能跨多个零脉冲。
- `Direction` 选错会朝远离目标的方向找，可能超 `DistanceLimit` 中止。
- `ReferenceSignal.TouchProbe` 必须选对应零脉冲的锁存单元。
- 结束后轴停在 `Homing`，需收尾 FB。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_StepReferencePulse.TcPOU`](../examples/P_Demo_MC_StepReferencePulse.TcPOU)

详见上述 XML 文件，内含场景 / 价值 / 验证步骤注释，可右键 PLC 项目下 POUs 文件夹 → Add → Existing Item 导入后编译运行。

## 7. 业务场景与实际价值

- **场景**：高精度机床 / 直线电机轴，先粗找开关再用编码器零脉冲精确定零，把重复定位精度提到编码器分辨率级别。
- **价值**：零脉冲精度远高于普通接近开关，是高精度归零的关键一步；封装为可拼接 step 便于组成两段式归零序列。
- **替代方案对比**：`MC_StepReferenceFlyingRefPulse`（飞行版，运行中后台抓零脉冲、不自己发运动）；`MC_StepReferencePulseDetection`（同找零脉冲但只返回检测位置不置零）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf) 第 3.3.9 节（Version 1.7.7）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_mc2_advancedhoming/427784331.html
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
