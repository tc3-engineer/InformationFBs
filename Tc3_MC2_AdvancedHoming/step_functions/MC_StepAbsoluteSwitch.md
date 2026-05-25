# MC_StepAbsoluteSwitch

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_MC2_AdvancedHoming` |
| Library Version | `1.7.7` |
| Type | `FUNCTION_BLOCK` |
| Category | `Step functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_mc2_advancedhoming/427758475.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_StepAbsoluteSwitch.xml`](../examples/P_Demo_MC_StepAbsoluteSwitch.xml) |

---

## 1. 功能简述

**主动归零 step 函数：搜索绝对参考开关（reference cam）**。它驱动轴运动去寻找一个绝对安装的外部物理开关（参考凸轮）。一般绝对开关有两个“关”区和一个“开”区；若开关不可越过则只有一个“关”区和一个“开”区。搜到开关满足 `SwitchMode` 条件后把轴位置设为 `SetPosition`。本 FB 在 `Homing` 状态执行，完成后轴仍停留在 `Homing` 状态，需配 finalizing FB 收尾。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute             : BOOL;
    Direction           : MC_Home_Direction;
    SwitchMode          : MC_Switch_Mode;
    ReferenceSignal     : MC_Ref_Signal_Ref;
    Velocity            : LREAL;
    Acceleration        : LREAL;
    Deceleration        : LREAL;
    Jerk                : LREAL;
    SetPosition         : LREAL;
    TimeLimit           : TIME;
    DistanceLimit       : LREAL;
    TorqueLimit         : LREAL;
    PositiveLimitSwitch : BOOL;
    NegativeLimitSwitch : BOOL;
    BufferMode          : MC_BufferMode;
    Options             : ST_Home_Options4;
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
| `PositiveLimitSwitch` | `BOOL` | 逻辑正方向硬件限位开关信号（在允许行程范围内时 `PositiveLimitSwitch = FALSE`） |
| `NegativeLimitSwitch` | `BOOL` | 逻辑负方向硬件限位开关信号（在允许行程范围内时 `NegativeLimitSwitch = FALSE`） |
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

`Execute` 上升沿启动搜索。按 PDF 第 3.3.1 节，本 FB 主动驱动轴去找绝对参考开关：起始方向由 `Direction`（`MC_Home_Direction`）决定，轴按 `Velocity` / `Acceleration` / `Deceleration` / `Jerk` 运动；遇到行程极限传感器（`PositiveLimitSwitch` / `NegativeLimitSwitch`）或满足 `mcSwitch*` 方向条件时可反向。`SwitchMode`（`MC_Switch_Mode`）定义结束条件，`ReferenceSignal` 给出参考凸轮信号源；满足结束条件时把轴位置设为 `SetPosition`，`Done = TRUE`。搜索运动以 `TorqueLimit` 限矩、step 函数默认关闭跟随误差监控（可经 `Options.EnableLagErrorDetection` 打开）。超过 `TimeLimit` 或相对起点移动超过 `DistanceLimit` 则 `CommandAborted` 置位。本 FB 把轴置于 / 保持在 `Homing` 状态，序列结束后仍停在 `Homing`，必须再调 `MC_FinishHoming`（成功）或 `MC_AbortHoming`（失败）才能切回 `Standstill`。`Parameter`（`MC_HomingParameter`）在整条序列各 FB 间逐级传递。

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

- `Direction` 起始方向选错会先撞向远离开关的一侧，可能直接顶上硬限位 ⚠️ —— 必须按机械布置选对方向。
- 必须正确接入 `PositiveLimitSwitch` / `NegativeLimitSwitch`，否则反向逻辑失效，轴可能越过开关撞硬限位 ⚠️。
- `TorqueLimit` 设太低会在正常搜索运动中误判堵转 / 走不动；设太高失去撞击保护意义。
- 参考凸轮开关有抖动时要在 `ReferenceSignal` / 接线侧滤波，避免锁到抖动沿。
- 结束后轴停在 `Homing`，忘记调收尾 FB 会导致临时参数不还原、状态卡在 `Homing` ⚠️。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_StepAbsoluteSwitch.xml`](../examples/P_Demo_MC_StepAbsoluteSwitch.xml)

详见上述 XML 文件，内含场景 / 价值 / 验证步骤注释，可右键 PLC 项目 → Import PLCopenXML 导入后编译运行。

## 7. 业务场景与实际价值

- **场景**：龙门 / 直线轴用一个安装在行程中段的参考凸轮开关归零，两端有硬件限位保护。
- **价值**：把“向参考凸轮运动 + 到限位反向 + 满足条件定零”整套搜索逻辑封装为一段可拼接的 step；配合 finalizing FB 可组成完全自定义的归零序列。
- **替代方案对比**：`MC_StepAbsoluteSwitchDetection`（同样找开关但只返回检测位置、不改写轴位置）；`MC_StepLimitSwitch`（找硬件限位开关而非中段参考凸轮）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf) 第 3.3.1 节（Version 1.7.7）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_mc2_advancedhoming/427758475.html
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
