# MC_MoveVelocity

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Point to point motion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70102411.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_MoveVelocity.TcPOU`](../examples/P_Demo_MC_MoveVelocity.TcPOU) |

---


## 1. 功能简述

PLCopen 标准定义的**恒速无限行进 FB**。`Execute` 上升沿启动一段无终点的运动：先按加速度爬升到 `Velocity`，到达后 `InVelocity := TRUE`，**FB 任务即结束**——之后 NC 继续以恒速运行不再监视。要停轴需另外调用 `MC_Stop` / `MC_Halt`。

加速段中被另一个命令抢占 → `CommandAborted := TRUE`；硬件/参数错误 → `Error := TRUE`。注意没有 `Done` 输出，只有 `InVelocity`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Velocity     : LREAL;
    Acceleration : LREAL;
    Deceleration : LREAL;
    Jerk         : LREAL;
    Direction    : MC_Direction := MC_Positive_Direction;
    BufferMode   : MC_BufferMode;
    Options      : ST_MoveOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次定位命令；命令进入运动队列后即开始执行，不需保持高电平 |
| `Velocity` | `LREAL` | — | 目标行进速度，`>0` |
| `Acceleration` | `LREAL` | — | 加速度，要求 `≥0`；填 `0` 表示采用轴参数中默认加速度 |
| `Deceleration` | `LREAL` | — | 减速度，要求 `≥0`；填 `0` 表示采用轴参数中默认减速度 |
| `Jerk` | `LREAL` | — | 加加速度（Jerk），要求 `≥0`；填 `0` 表示采用轴参数中默认 Jerk |
| `Direction` | `MC_Direction` | `MC_Positive_Direction` | 行进方向 |
| `BufferMode` | `MC_BufferMode` | — | 队列模式：当轴正在执行另一命令时本命令的接入方式（`MC_Aborting` / `MC_Buffered` / `MC_BlendingLow` / `MC_BlendingPrevious` / `MC_BlendingNext` / `MC_BlendingHigh`）；耦合从轴只允许 `Aborting` |
| `Options` | `ST_MoveOptions` | — | 额外可选参数结构，绝大部分场景留默认即可 |

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
    InVelocity     : BOOL;
    Busy           : BOOL;
    Active         : BOOL;
    CommandAborted : BOOL;
    Error          : BOOL;
    ErrorID        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `InVelocity` | `BOOL` | 达到目标恒速时置 `TRUE`；之后本 FB 不再监视轴 |
| `Busy` | `BOOL` | `Execute` 上升沿后立即变 `TRUE`，结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE` |
| `Active` | `BOOL` | 表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE` |
| `CommandAborted` | `BOOL` | 命令未完成就被中止（被另一 Move 抢占 / `MC_Stop` 停掉）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |

## 3. 行为说明

**触发**：`Execute` 上升沿启动恒速运动。`InVelocity = TRUE` 之后 FB 完成自身职责，**不再持续监视轴**——这是与 `MC_MoveAbsolute` 等位置类 FB 最大的区别。轴会按 NC 设定一直走，直到收到下一条命令（典型是 `MC_Stop` / `MC_Halt`）。

**状态机分支**：
- 正常：加速段完成 → `InVelocity = TRUE`、`Busy = FALSE`、`Active = FALSE`（FB 退出"忙"态）
- 加速段被抢：另一条命令切入 → `CommandAborted = TRUE`、`InVelocity` 不会被置位
- 出错：参数越界等 → `Error = TRUE`、`ErrorID` 给码

**典型场景**：传送带恒速运行、卷绕收放线速度跟随、风机/泵恒速运转。所有"有起点没终点"的运动都用本 FB。

**易踩坑**：达到恒速后 `Busy = FALSE`，看似 FB "完成了"，但**轴还在动**。新手把"Busy 灭"当成"运动结束"会出事。要停轴必须显式调 `MC_Stop` / `MC_Halt`。

**耦合从轴特例**：与其它 P2P FB 一致，会先自动解耦再执行恒速运动，且只能 `MC_Aborting`。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **没有 Done 输出**：用 `InVelocity` 判断"已达速度"；判断"轴已停"要靠 `Axis.NcToPlc.ActVelo ≈ 0` 或自己跟踪后续 `MC_Stop` 的 `Done`。
- **`Velocity := 0` 报错**：禁用此 FB 停轴的写法，要停用 `MC_Halt`。
- **`Direction` 必填**：默认 `MC_Positive_Direction`，但工业代码建议显式给值避免误读。
- **`InVelocity` 灭 ≠ 停轴**：加速完达到恒速后 `InVelocity = TRUE` 一直保持直到本 FB 被覆盖；轴恒速运行期间 `InVelocity` 不会自动灭。
- **`Busy = FALSE` 时还在跑**：见 §3。要持续监视应跟踪 `Axis.NcToPlc.ActVelo` 而不是本 FB 输出。
- **耦合从轴行为**：从轴上发 `MC_MoveVelocity` 自动解耦，要再耦合需重新 `MC_GearIn`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_MoveVelocity.TcPOU`](../examples/P_Demo_MC_MoveVelocity.TcPOU)

```iecst
// 场景：传送带启动后恒速 1.5 m/s 运行；点 bStartConveyor 启动，点 bStopConveyor 停
PROGRAM P_Demo_MC_MoveVelocity
VAR
    fbConveyorRun     : MC_MoveVelocity;
    fbConveyorHalt    : MC_Halt;
    axisConveyor      : AXIS_REF;
    rtStartTrig       : R_TRIG;
    rtStopTrig        : R_TRIG;
    bStartConveyor    : BOOL;
    bStopConveyor     : BOOL;
    lrLineSpeedMMpS   : LREAL := 1500.0;
    bAtSpeed          : BOOL;
    bRunBusy          : BOOL;
    bHaltDone         : BOOL;
    nRunErrorID       : UDINT;
END_VAR

rtStartTrig(CLK := bStartConveyor);
rtStopTrig(CLK := bStopConveyor);

fbConveyorRun(
    Execute      := rtStartTrig.Q,
    Velocity     := lrLineSpeedMMpS,
    Acceleration := 2000.0,
    Deceleration := 2000.0,
    Jerk         := 20000.0,
    Direction    := MC_Positive_Direction,
    BufferMode   := MC_Aborting,
    Axis         := axisConveyor,
    InVelocity   => bAtSpeed,
    Busy         => bRunBusy,
    ErrorID      => nRunErrorID
);

fbConveyorHalt(
    Execute      := rtStopTrig.Q,
    Deceleration := 2000.0,
    Jerk         := 20000.0,
    BufferMode   := MC_Aborting,
    Axis         := axisConveyor,
    Done         => bHaltDone
);
```

## 7. 业务场景与实际价值

- **场景**：传送带、卷绕收放、贴标机滚筒、印刷机版辊、风扇/泵恒速运转。所有"开起来恒速跑、停由外部触发"的设备都属这一类。
- **价值**：FB 自动处理加速段 S 曲线、达到恒速后即"放手"让 NC 维持；停轴用配套的 `MC_Halt` / `MC_Stop`，分工明确。比写定时器 + 速度环手动控制省 30+ 行代码。
- **替代方案对比**：
  - 直接给 NC 通道速度命令：要拼 `MC_DIRECTVELOCITY` 控制字
  - 用 `MC_MoveAbsolute(Position := very_large_number)`：勉强能跑但行程有限且不符合"无终点"语义
  - **本 FB**：恒速运动的标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.1.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70102411.html
- **相关 FB**：`MC_Halt`、`MC_Stop`（停轴）、`MC_MoveContinuousAbsolute`（带终点的恒速变体）
