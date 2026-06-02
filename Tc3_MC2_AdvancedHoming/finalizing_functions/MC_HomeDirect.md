# MC_HomeDirect

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_MC2_AdvancedHoming` |
| Library Version | `1.7.7` |
| Type | `FUNCTION_BLOCK` |
| Category | `Finalizing functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_mc2_advancedhoming/427750411.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_HomeDirect.TcPOU`](../examples/P_Demo_MC_HomeDirect.TcPOU) |

---

## 1. 功能简述

归零序列的**收尾功能块**，作用是“直接置位”收尾：成功结束序列的同时把轴当前位置直接设为 `SetPosition` 给定的值，并还原被临时修改的参数、把轴状态从 `Homing` 切回 `Standstill`。与 `MC_FinishHoming` 的区别是本 FB 在收尾时把位置定到一个用户指定的绝对值，常用于静态归零（操作员把轴停在已知位置后直接告诉 NC“我现在在这”）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute     : BOOL;
    SetPosition : LREAL;
    BufferMode  : MC_BufferMode;
    Options     : ST_Home_Options2;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Execute` | `BOOL` | 上升沿触发一次命令执行；触发后进入处理状态，无需保持高电平 |
| `SetPosition` | `LREAL` | 搜索成功后把轴的当前位置设为该值（绝对零点） |
| `BufferMode` | `MC_BufferMode` | 未实现（`Not implemented`），按 PDF 说明本入口当前无效 |
| `Options` | `ST_Home_Options2` | `ST_Home_Options2` 结构：仅含 `DisableDriveAccess : BOOL`。Beckhoff 伺服设 `FALSE`，第三方伺服通常设 `TRUE`；设 `TRUE` 时由用户自行负责修改与恢复驱动参数 |

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

`Execute` 上升沿触发收尾。本 FB 属 finalizing 类：按 PDF 第 3.1.2 节，它把轴当前位置直接复位为 `SetPosition`，确保被序列临时修改的 NC / 驱动参数还原为原值，随后轴离开 `Homing` 状态回到 `Standstill`。它本身不执行搜索运动，只做“定位置 + 还参数 + 切状态”。`Busy` 在 `Execute` 上升沿后置 `TRUE`，`Active` 表示命令正在执行；成功后 `Done = TRUE`，被抢占 / 停止时 `CommandAborted = TRUE`，出错 `Error = TRUE` 给出 `ErrorID`。典型用法：用 `MC_StepReferencePulse` 等 step 函数搜到参考点后，用本 FB 把那一点定义为某个绝对坐标值并收尾；或纯静态场景下不走 step，直接以本 FB 把当前停车点设为已知坐标。

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

- `SetPosition` 是绝对值，不是偏移量；它会覆盖轴当前位置读数，写错会让后续所有绝对定位偏移 ⚠️。
- 本 FB 不产生运动，因此不存在撞限位风险，但定位置前要确认轴确实停在 `SetPosition` 对应的物理点。
- `Parameter` 必须是贯穿整条序列的同一个 `MC_HomingParameter` 实例，否则参数还原不正确。
- `BufferMode` 当前未实现。
- 纯静态归零（无 step 搜索）也要保证 `Parameter.Stored` 状态正确，否则可能报 `MC_HOMINGERROR_PARAMETER_NOTSTORED`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_HomeDirect.TcPOU`](../examples/P_Demo_MC_HomeDirect.TcPOU)

详见上述 XML 文件，内含场景 / 价值 / 验证步骤注释，可右键 PLC 项目下 POUs 文件夹 → Add → Existing Item 导入后编译运行。

## 7. 业务场景与实际价值

- **场景**：编码器零脉冲搜索成功后，把那一点定义为机床坐标 0；或操作员手动把轴拖到已知工件原点后用本 FB 直接置位收尾。
- **价值**：把“设位置 + 还原参数 + 切回 Standstill”封装为一个 FB，比手动写 NC 通道置位命令省事且不漏还原参数。
- **替代方案对比**：`MC_FinishHoming`（保留搜到的位置、不强制改写为指定值，可带退离运动）；Tc2_MC2 的 `MC_Home(HomingMode := MC_Direct)`（固定序列里的直接置位）。本 FB 用于自定义序列里的“指定绝对值”收尾。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf) 第 3.1.2 节（Version 1.7.7）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_mc2_advancedhoming/427750411.html
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
