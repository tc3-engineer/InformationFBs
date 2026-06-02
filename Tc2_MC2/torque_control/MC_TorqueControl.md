# MC_TorqueControl

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Torque Control` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/7617393803.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_TorqueControl.TcPOU`](../examples/P_Demo_MC_TorqueControl.TcPOU) |

---


## 1. 功能简述

PLCopen 标准定义的**力矩控制 FB**。把 NC 下的轴切换到 **CST（Cyclic Synchronous Torque）模式**并给定力矩设定值。这种模式下 NC 不再以位置 / 速度环为主，而是把驱动器直接置于"恒力矩输出"状态——典型应用是张力控制、压紧机构、扭矩限制工艺。

`VelocityLimitHigh` 和 `VelocityLimitLow` 通过 NC 循环接口（`Axis->Drive->Outputs->nDataOut5/nDataOut6`）传给驱动器，由驱动器在力矩模式下限制速度上下限避免飞车。

**⚠️ 危险**：使用本 FB 后轴可能仍处于 CST 模式；再次使能时（特别是垂直轴）可能突然下坠或冲撞。PDF 中以 DANGER 警示——使用后必须显式切换回 CSV/CSP 模式。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute            : BOOL;
    ContinuousUpdate   : BOOL;
    Relative           : BOOL;
    Torque             : LREAL;
    TorqueRamp         : LREAL;
    VelocityLimitHigh  : LREAL;
    VelocityLimitLow   : LREAL;
    BufferMode         : MC_BufferMode;
    Options            : ST_TorqueControlOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次定位命令；命令进入运动队列后即开始执行，不需保持高电平 |
| `ContinuousUpdate` | `BOOL` | — | 上升沿时若 TRUE：命令执行期间改 `Torque` / `TorqueRamp` 等参数会尽快生效，适合做力矩闭环 |
| `Relative` | `BOOL` | — | `FALSE` = `Torque` 是绝对力矩设定值；`TRUE` = 在当前力矩上叠加 |
| `Torque` | `LREAL` | — | 力矩设定值（单位取决于驱动器配置，典型为 Nm 或额定力矩百分比） |
| `TorqueRamp` | `LREAL` | — | 力矩斜坡，限制力矩瞬时跳变避免机械冲击 |
| `VelocityLimitHigh` | `LREAL` | — | CST 模式下的速度上限（正方向） |
| `VelocityLimitLow` | `LREAL` | — | CST 模式下的速度下限（负方向，typically 负值） |
| `BufferMode` | `MC_BufferMode` | — | 队列模式：当轴正在执行另一命令时本命令的接入方式（`MC_Aborting` / `MC_Buffered` / `MC_BlendingLow` / `MC_BlendingPrevious` / `MC_BlendingNext` / `MC_BlendingHigh`）；耦合从轴只允许 `Aborting` |
| `Options` | `ST_TorqueControlOptions` | — | 扩展选项 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | 轴数据结构，唯一标识系统中一根轴；含位置、速度、错误状态等全部循环数据。**必须传引用**（VAR_IN_OUT 语义） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    InTorque           : BOOL;
    Busy               : BOOL;
    Active             : BOOL;
    CommandAborted     : BOOL;
    Error              : BOOL;
    ErrorID            : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `InTorque` | `BOOL` | 力矩设定值已达到时置 `TRUE`（速度限制下） |
| `Busy` | `BOOL` | `Execute` 上升沿后立即变 `TRUE`，结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE` |
| `Active` | `BOOL` | 表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE` |
| `CommandAborted` | `BOOL` | 命令未完成就被中止（被另一 Move 抢占 / `MC_Stop` 停掉）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |

## 3. 行为说明

**触发**：`Execute` 上升沿启动。NC 把驱动器切换到 **CST（Cyclic Synchronous Torque）模式**，并按 `TorqueRamp` 斜率把力矩设定值从 0 拉到 `Torque`。`VelocityLimitHigh / Low` 限制速度避免飞车。

**支持的 Beckhoff 硬件**：
- AX5xxx：FW v2.14 b0001 起
- AX8xxx / AMP8xxx / MD8xxx：FW v1.05 b0001 起
- Compact drive（伺服，含 ELM72xx 和 AMI8xxx）：FW v01 起

**驱动器需支持运动模式动态切换**：CSP/CSV ↔ CST 切换；不是所有伺服都支持，使用前查驱动器手册。

**死区时间补偿**：要无冲击切换模式必须**激活 NC 轴的死区时间补偿**（dead time compensation），否则切换瞬间会有抖动。

**关闭力矩控制**：撤 `Execute` 不会自动切回 CSP/CSV，必须显式：
1. 用 `MC_ReadDriveOperationMode` 检查当前模式
2. 若不在位置相关模式（CSV/CSP）则用 `MC_WriteDriveOperationMode` 直接切回，或用 `MC_Halt` / `MC_Stop`（TwinCAT 3.1.4024.40+）间接切回
3. 再次检查模式确保切回成功；否则中止并报错

⚠️ **垂直轴 / 起吊轴特别警告**：CST 模式下使能瞬间力矩可能不足以维持重量 → 轴下坠。**必须经过风险评估后才允许使用**。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **⚠️ 模式切换不会自动还原**：撤 `Execute` 后轴可能仍在 CST，再使能可能突然动。**必须显式切回 CSV/CSP**。
- **垂直轴使用前先评估风险**：CST 模式下重力可能让轴下坠，机械结构必须能承受或加入抱闸。
- **驱动器固件版本要够**：见上面硬件支持表；旧固件不支持 CST 模式切换。
- **死区时间补偿必开**：否则模式切换瞬间抖动剧烈。
- **`VelocityLimitLow` 通常为负值**：限制负方向速度；写正值会让限制无效。
- **力矩单位看驱动器**：有的伺服用 Nm，有的用额定力矩百分比；调试时先用小值验证。
- **`ContinuousUpdate := TRUE` 适合力矩闭环**：例如张力 PID 输出连续改 `Torque`；`FALSE` 适合一次性设定后不变。
- **`BufferMode` 行为**：与其它 MC FB 一致，但 PDF 没特别提，建议先用 `MC_Aborting`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_TorqueControl.TcPOU`](../examples/P_Demo_MC_TorqueControl.TcPOU)

```iecst
// 场景：卷绕机张力控制 — 收线轴以恒定 35 Nm 力矩拉紧线材，速度限在 ±500 rpm
PROGRAM P_Demo_MC_TorqueControl
VAR
    fbTensionCtrl    : MC_TorqueControl;
    axisTensionRoll  : AXIS_REF;
    bEnableTension   : BOOL;
    lrTorqueSetNm    : LREAL := 35.0;
    bAtTorque        : BOOL;
    bCtrlBusy        : BOOL;
    bCtrlError       : BOOL;
    nErrorID         : UDINT;
END_VAR

fbTensionCtrl(
    Execute           := bEnableTension,
    ContinuousUpdate  := TRUE,
    Relative          := FALSE,
    Torque            := lrTorqueSetNm,
    TorqueRamp        := 10.0,
    VelocityLimitHigh := 400.0,
    VelocityLimitLow  := -500.0,
    BufferMode        := MC_Aborting,
    Axis              := axisTensionRoll,
    InTorque          => bAtTorque,
    Busy              => bCtrlBusy,
    Error             => bCtrlError,
    ErrorID           => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：卷绕机收线/放线张力控制、压紧机构（夹具按恒力夹紧工件）、扭矩限制工艺（拧螺丝到指定扭矩）、惯量补偿。共同特征：**力矩是控制目标，速度只是约束**。
- **价值**：把 NC + 驱动器固件级的模式切换 + 力矩闭环 + 速度限制封装为一个 FB；不用业务侧自己写 SDO 写驱动器对象字典。
- **替代方案对比**：
  - 直接 SDO 切换驱动器 modes_of_operation：要熟悉 CiA402 状态机，且 PLC 周期内可能出 timing 问题
  - 用 `MC_WriteDriveOperationMode` + 自己写力矩设定值：分两步比本 FB 麻烦
  - **本 FB**：力矩控制的标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.7.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/7617393803.html
- **相关 FB**：`MC_ReadDriveOperationMode`、`MC_WriteDriveOperationMode`、`MC_Halt` / `MC_Stop`（用于切回 CSV/CSP）、`ST_TorqueControlOptions`
