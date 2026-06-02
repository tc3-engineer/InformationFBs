# MC_AbortHoming

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_MC2_AdvancedHoming` |
| Library Version | `1.7.7` |
| Type | `FUNCTION_BLOCK` |
| Category | `Finalizing functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_mc2_advancedhoming/427719051.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_AbortHoming.TcPOU`](../examples/P_Demo_MC_AbortHoming.TcPOU) |

---

## 1. 功能简述

归零序列的**异常收尾功能块**。当一条自定义归零序列中的 step 函数报错或被中止时，调用本 FB 来中止整条序列：它把序列中被临时修改的 NC / 驱动参数还原为原值，并把轴状态从 `Homing` 切回 `Standstill`。与 `MC_FinishHoming` 成对使用——前者用于成功分支，本 FB 用于失败分支。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute : BOOL;
    Options : ST_Home_Options2;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Execute` | `BOOL` | 上升沿触发一次命令执行；触发后进入处理状态，无需保持高电平 |
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
    CommandAborted : BOOL;
    Error          : BOOL;
    ErrorID        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 命令成功完成时置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后立即置 `TRUE`，命令处理期间保持 `TRUE`；变回 `FALSE` 时 FB 可接新命令，同时 `Done` / `CommandAborted` / `Error` 之一被置位 |
| `CommandAborted` | `BOOL` | 命令未能完整执行（被中止）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间一旦发生错误即置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出错误号（见 §4，本库 `E_HomingErrorCodes` 段） |

## 3. 行为说明

`Execute` 上升沿启动中止收尾。本 FB 属 finalizing 类：按 PDF 第 3.1.3 节，它终止当前归零序列，把被各 step 函数临时修改的 NC / 驱动参数依据 `Parameter`（`MC_HomingParameter`）还原回备份值，并把轴状态由 `Homing` 切回 `Standstill`。它不执行搜索也不下发定位运动，只做“安全收尾 + 参数还原”。`Busy` 在 `Execute` 上升沿后置 `TRUE`，收尾完成后 `Done = TRUE`；若收尾本身被抢占则 `CommandAborted = TRUE`，出错 `Error = TRUE` 给出 `ErrorID`。典型用法：在序列状态机里监视 step 函数的 `Error` / `CommandAborted`，一旦置位就转去调用本 FB，确保哪怕归零失败也不把临时参数残留在 NC / 驱动里（否则后续运动会异常）。

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

- 即使归零没成功，也**必须**调用本 FB（或 `MC_FinishHoming`）收尾，否则临时改过的参数残留，后续运动可能报跟随误差或限速异常 ⚠️。
- `Parameter` 必须是贯穿整条序列的同一个 `MC_HomingParameter` 实例，否则无法还原。
- （工程经验补充）本 FB 不停止正在进行的运动；如果 step 还在动，应先用 `MC_Stop` 停轴再 `MC_AbortHoming`（工程经验补充）。
- 收尾后轴回到 `Standstill` 但仍未校准，需重新发起归零序列。
- `Options.DisableDriveAccess` 必须与序列中 step 函数所用设置一致，否则驱动参数还原可能不完整。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_AbortHoming.TcPOU`](../examples/P_Demo_MC_AbortHoming.TcPOU)

详见上述 XML 文件，内含场景 / 价值 / 验证步骤注释，可右键 PLC 项目下 POUs 文件夹 → Add → Existing Item 导入后编译运行。

## 7. 业务场景与实际价值

- **场景**：归零序列中 `MC_StepBlock` 顶撞块超时报错，需要安全中止并把被改的转矩限制等参数还原。
- **价值**：保证“归零失败也能干净收场”，避免临时参数（限速、限矩、关掉的跟随监控）残留导致设备后续异常。
- **替代方案对比**：`MC_FinishHoming`（成功分支收尾，可带退离运动）。本 FB 专用于失败 / 中止分支，二者通常在同一状态机里按 step 函数结果二选一调用。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf) 第 3.1.3 节（Version 1.7.7）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_mc2_advancedhoming/427719051.html
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
