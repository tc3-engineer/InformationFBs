# MC_StepReferenceFlyingRefPulse

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_MC2_AdvancedHoming` |
| Library Version | `1.7.7` |
| Type | `FUNCTION_BLOCK` |
| Category | `Referencing functions (passive)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_mc2_advancedhoming/427754251.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_StepReferenceFlyingRefPulse.TcPOU`](../examples/P_Demo_MC_StepReferenceFlyingRefPulse.TcPOU) |

---

## 1. 功能简述

**被动（flying）编码器零脉冲归零**功能块。它在机器正常运行（运动进行中）时执行，对编码器的零脉冲（zero pulse / reference pulse）做参考：抓到零脉冲那一刻把轴位置设为 `SetPosition`。本 FB 自身**不启动也不修改任何运动**，只是后台监听参考信号，因此不进入 `Homing` 状态、不影响 PLCopen 状态机。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute         : BOOL;
    ReferenceSignal : MC_Ref_Signal_Ref;
    SetPosition     : LREAL;
    TimeLimit       : TIME;
    DistanceLimit   : LREAL;
    BufferMode      : MC_BufferMode;
    Options         : ST_Home_Options;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Execute` | `BOOL` | 上升沿触发一次命令执行；触发后进入处理状态，无需保持高电平 |
| `ReferenceSignal` | `MC_Ref_Signal_Ref` | `MC_Ref_Signal_Ref` 结构：定义参考信号源（锁存单元 `TouchProbe`、信号源 `SignalSource`、当前电平 `Level`），见 §8 |
| `SetPosition` | `LREAL` | 搜索成功后把轴的当前位置设为该值（绝对零点） |
| `TimeLimit` | `TIME` | 搜索耗时超过此时间则中止搜索过程 |
| `DistanceLimit` | `LREAL` | 相对起始位置移动超过此距离则中止搜索过程 |
| `BufferMode` | `MC_BufferMode` | 未实现（`Not implemented`），按 PDF 说明本入口当前无效 |
| `Options` | `ST_Home_Options` | `ST_Home_Options` 结构：当前未使用（`Currently not used`） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | `AXIS_REF` 轴数据结构，唯一标识系统中的一根轴，含位置、速度、错误状态等循环数据。**必须传引用**（VAR_IN_OUT 语义） |

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

`Execute` 上升沿启动后台监听。按 PDF 第 3.2.2 节，本 FB 在运动进行中对编码器零脉冲做参考，**它本身不产生任何运动**——运动由其它 Move FB 提供，本 FB 只通过 `ReferenceSignal` 配置的锁存单元（touch probe）等待零脉冲事件。零脉冲到达瞬间，NC 把轴当前位置锁存并设为 `SetPosition`，`Done = TRUE`。若超过 `TimeLimit` 时间、或相对启动点移动超过 `DistanceLimit` 距离仍没抓到零脉冲，则搜索中止，`CommandAborted` 置位。`Busy` 在 `Execute` 上升沿后置 `TRUE`，`Active` 表示监听中。由于不进入 `Homing` 状态、不改运动状态，本 FB 可像管理类 FB 一样在任意运动状态下调用，适合“边走边对零”。

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

- 本 FB 不发运动；必须由别的 Move FB 让轴动起来经过零脉冲，否则永远抓不到信号、最终 `TimeLimit` 超时中止 ⚠️。
- `SetPosition` 是抓到零脉冲那一点的绝对坐标，不是当前位置偏移。
- `ReferenceSignal.TouchProbe` 必须选对应零脉冲的锁存单元，选错会一直抓不到。
- `TimeLimit` / `DistanceLimit` 要留足，使运动确实能在限制内跨过至少一个零脉冲。
- 放弃等待时用 `MC_AbortPassiveHoming` 取消，以释放锁存单元。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_StepReferenceFlyingRefPulse.TcPOU`](../examples/P_Demo_MC_StepReferenceFlyingRefPulse.TcPOU)

详见上述 XML 文件，内含场景 / 价值 / 验证步骤注释，可右键 PLC 项目下 POUs 文件夹 → Add → Existing Item 导入后编译运行。

## 7. 业务场景与实际价值

- **场景**：连续运转的辊轴 / 转台，不停机的情况下利用每转一次的编码器零脉冲在线重新对零，消除累积漂移。
- **价值**：归零与生产运动并行，不必停机走专门的归零序列；零脉冲精度远高于普通接近开关。
- **替代方案对比**：`MC_StepReferencePulse`（主动版，自己发运动找零脉冲、要进 Homing 状态、停机）；`MC_StepReferenceFlyingSwitch`（飞行版但用外部开关而非零脉冲）。本 FB 用于运行中飞抓零脉冲。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf) 第 3.2.2 节（Version 1.7.7）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_mc2_advancedhoming/427754251.html
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
