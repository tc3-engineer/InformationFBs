# Tc3_MC2_AdvancedHoming — 自定义归零（参考运行）库

> Beckhoff TwinCAT 3 运动控制库，基于 **PLCopen Motion Control Part 5 – Homing Procedures** 规范。
> 它把过去“黑盒、不可见”的归零序列拆成一组可拼接的功能块（FB），让用户自己用 step 函数 + 收尾函数
> 组合出任意自定义归零流程：搜参考凸轮、搜硬件限位开关、撞机械止挡、找编码器零脉冲、运行中飞行对零等。
>
> - **Library Version**：1.7.7
> - **要求**：TwinCAT 3.1 Build 4020 或更高
> - **Source PDF**：[TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_MC2_AdvancedHoming_EN.pdf)
> - **Source InfoSys**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_mc2_advancedhoming/

## 关键概念

- **每个 FB 都有 `Axis : AXIS_REF` 作为 VAR_IN_OUT**（必须传引用）；step / 收尾类 FB 还要传第二个 VAR_IN_OUT `Parameter : MC_HomingParameter`。
- **`MC_HomingParameter` 必须贯穿整条序列**：同一个实例在序列里所有 FB 之间逐级传递。step 函数会临时备份并修改 NC / 驱动参数（限速、限矩、关闭跟随误差监控等），收尾 FB 负责把它们还原。
- **三类 FB 的状态机语义不同**：
  - **Step 函数**（`MC_Step*`）在轴状态 `Homing` 中执行，完成后轴**仍停留在 `Homing`**——必须再调一个收尾 FB 才会切回 `Standstill`。
  - **收尾函数**（`MC_FinishHoming` / `MC_HomeDirect` / `MC_AbortHoming`）把轴状态从 `Homing` 切回 `Standstill` 并还原参数。每条序列（除非只用被动 flying 函数）都必须以一个收尾 FB 结束。
  - **被动 / flying 函数**（`MC_StepReferenceFlying*` / `MC_AbortPassiveHoming`）在机器运行中执行，**不进入 `Homing`、不影响 PLCopen 状态机**，可在任意运动状态下调用。
- **`...Detection` 版本不改写轴位置**，而是把检测到事件那一刻的轴位置通过 `RecordedPosition` 返回，由用户决定置零策略。
- 输出统一遵循 PLCopen 收敛分支：`Done` / `CommandAborted` / `Error` + `ErrorID`（中止靠 `CommandAborted`，错误靠 `Error`）。
- 错误码 `ErrorID` 取本库枚举 **`E_HomingErrorCodes`**（`16#4B90`–`16#4B98`，UDINT 基）；底层 NC / 驱动错误也可能经 `ErrorID` 透传。

## 典型序列结构（来自 PDF 第 2.4 节）

“Home-on-block”示例：调 `MC_StepBlock` 顶机械止挡 → 若 `Done = TRUE` 则调 `MC_FinishHoming` 正常收尾（带退离）；
若 `Error` / `CommandAborted` 则调 `MC_AbortHoming` 中止收尾。整条序列共用同一个 `Axis` 与 `MC_HomingParameter`。

## 分类索引（共 16 个）

### Finalizing functions（收尾函数，3 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_FinishHoming` | 正常收尾：还原参数 + 切回 Standstill，可带退离运动 | [finalizing_functions/MC_FinishHoming.md](finalizing_functions/MC_FinishHoming.md) |
| `MC_HomeDirect` | 直接置位收尾：把轴位置设为 `SetPosition` 并收尾 | [finalizing_functions/MC_HomeDirect.md](finalizing_functions/MC_HomeDirect.md) |
| `MC_AbortHoming` | 异常收尾：中止序列、还原参数、切回 Standstill | [finalizing_functions/MC_AbortHoming.md](finalizing_functions/MC_AbortHoming.md) |

### Referencing functions (passive)（被动 / flying 归零，3 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_AbortPassiveHoming` | 取消正在等待的被动 flying 归零 | [referencing_functions_passive/MC_AbortPassiveHoming.md](referencing_functions_passive/MC_AbortPassiveHoming.md) |
| `MC_StepReferenceFlyingRefPulse` | 运行中飞抓编码器零脉冲对零 | [referencing_functions_passive/MC_StepReferenceFlyingRefPulse.md](referencing_functions_passive/MC_StepReferenceFlyingRefPulse.md) |
| `MC_StepReferenceFlyingSwitch` | 运行中飞抓外部开关对零 | [referencing_functions_passive/MC_StepReferenceFlyingSwitch.md](referencing_functions_passive/MC_StepReferenceFlyingSwitch.md) |

### Step functions（主动搜索 step 函数，10 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_StepAbsoluteSwitch` | 搜绝对参考凸轮开关，命中置零 | [step_functions/MC_StepAbsoluteSwitch.md](step_functions/MC_StepAbsoluteSwitch.md) |
| `MC_StepAbsoluteSwitchDetection` | 搜绝对参考凸轮开关，只返回检测位置 | [step_functions/MC_StepAbsoluteSwitchDetection.md](step_functions/MC_StepAbsoluteSwitchDetection.md) |
| `MC_StepBlock` | 撞机械止挡（转矩 + 速度判据），命中置零 | [step_functions/MC_StepBlock.md](step_functions/MC_StepBlock.md) |
| `MC_StepBlockDetection` | 撞机械止挡（转矩判据），只返回检测位置 | [step_functions/MC_StepBlockDetection.md](step_functions/MC_StepBlockDetection.md) |
| `MC_StepBlockLagBased` | 撞机械止挡（跟随误差判据），命中置零 | [step_functions/MC_StepBlockLagBased.md](step_functions/MC_StepBlockLagBased.md) |
| `MC_StepBlockLagBasedDetection` | 撞机械止挡（跟随误差判据），只返回检测位置 | [step_functions/MC_StepBlockLagBasedDetection.md](step_functions/MC_StepBlockLagBasedDetection.md) |
| `MC_StepLimitSwitch` | 搜硬件限位开关，命中置零 | [step_functions/MC_StepLimitSwitch.md](step_functions/MC_StepLimitSwitch.md) |
| `MC_StepLimitSwitchDetection` | 搜硬件限位开关，只返回检测位置 | [step_functions/MC_StepLimitSwitchDetection.md](step_functions/MC_StepLimitSwitchDetection.md) |
| `MC_StepReferencePulse` | 搜编码器零脉冲，命中置零 | [step_functions/MC_StepReferencePulse.md](step_functions/MC_StepReferencePulse.md) |
| `MC_StepReferencePulseDetection` | 搜编码器零脉冲，只返回检测位置 | [step_functions/MC_StepReferencePulseDetection.md](step_functions/MC_StepReferencePulseDetection.md) |

## 数据类型（库内共用，PDF 第 4 章）

- `MC_Home_Direction`（枚举）：`mcPositiveDirection := 1` / `mcNegativeDirection := 3` / `mcSwitchPositive := 5` / `mcSwitchNegative := 7`。
- `MC_Switch_Mode`（枚举）：`mcOn := 1` / `mcOff := 2` / `mcRisingEdge := 3` / `mcFallingEdge := 4` / `mcEdgeSwitchPositive := 5` / `mcEdgeSwitchNegative := 6` / `mcRisingEdgeInverse := 11` / `mcFallingEdgeInverse := 12`。
- `MC_Ref_Signal_Ref`（结构）：`SignalSource` / `TouchProbe` / `Level`。
- `ST_Home_Options` / `ST_Home_Options2` / `ST_Home_Options3` / `ST_Home_Options4`：选项结构，含 `DisableDriveAccess`、`InstantLagReduction`、`EnableLagErrorDetection` 等。
- `MC_HomingParameter`（结构）：`Stored` / `Nc` / `Drive`，贯穿整条序列。
- `E_HomingErrorCodes`（枚举，UDINT 基）：`16#4B90`–`16#4B98`，各 FB 错误码段，详见各文档 §4。

## 已知 PDF 笔误（已在对应文档 §3 标注 ⚠️）

- `MC_StepReferenceFlyingSwitch`（3.2.3）：正文 VAR_INPUT 代码块把 `SwitchMode` 印为 `BOOL`，接口图与说明表为 `MC_Switch_Mode`。文档 §2 逐字照搬代码块（`BOOL`）并在 §3 说明应按 `MC_Switch_Mode` 理解。
- `MC_StepReferencePulse`（3.3.9）/ `MC_StepReferencePulseDetection`（3.3.10）：正文 VAR_INPUT 代码块多印 `SwitchMode : MC_Switch_Mode`，接口图与说明表均无此入口（零脉冲搜索无需 SwitchMode）。
- `MC_StepBlockLagBasedDetection`（3.3.6）：正文 VAR_INPUT 代码块多印 `SetPosition : LREAL`，Detection 版不改写轴位置，该入口无效。

## 验证

全部 16 篇文档 `verify_doc.py` 退出 0（PASS），16 个 `examples/P_Demo_*.TcPOU` `lint_tcpou.py` 退出 0。
PDF + InfoSys 双源交叉核对一致（接口 VAR 名 / 类型 / Description 与 InfoSys topic 页一致）。
