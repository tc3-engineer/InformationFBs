# MC_MoveVelocity

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_DriveMotionControl` |
| Library Version | `1.5.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `Point to point motion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8280997387.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_MoveVelocity.TcPOU`](../examples/P_Demo_MC_MoveVelocity.TcPOU) |

---

## 1. 功能简述

PLCopen Motion Control 标准定义的**恒速运动功能块（Function Block, FB）**。`Execute` 上升沿启动一次以指定速度和方向的**无终点行进**；运动可通过 Stop 命令停止。

达到恒定速度后 `InVelocity` 置 `TRUE`；一旦达到恒速，本功能块的任务即完成，**不再监视运动**。若在加速阶段命令被中止，则置 `CommandAborted`，出错则置 `Error`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Velocity     : LREAL;
    Acceleration : LREAL;
    Deceleration : LREAL;
    Direction    : MC_Direction := MC_Positive_Direction;
    Options      : ST_MoveOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次命令 |
| `Velocity` | `LREAL` | — | 最大行进速度（`>0`） |
| `Acceleration` | `LREAL` | — | 加速度（`≥0`） |
| `Deceleration` | `LREAL` | — | 减速度（`≥0`） |
| `Direction` | `MC_Direction` | `MC_Positive_Direction` | 正方向或负方向（类型 `MC_Direction`） |
| `Options` | `ST_MoveOptions` | — | 数据结构（`ST_MoveOptions`），含附加的、很少用的参数。通常该输入可不用 |

> 注：PDF 的图示与描述表另列有 `ContinuousUpdate` 输入（`BOOL`，含义："若 `ContinuousUpdate = TRUE`，在命令处理期间通过 `Execute` 上升沿可按 `Velocity` / `Acceleration` / `Deceleration` 输入改变动力学并尽快生效"）；但 PDF 在本 FB 的 `VAR_INPUT` 代码块中**未列出** `ContinuousUpdate`，故本文严格按 PDF 的 `VAR_INPUT` 代码块搬运，不在接口代码块中列 `ContinuousUpdate`。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | 轴数据结构，在系统中唯一标识一根轴；含当前轴状态，包括位置、速度、错误状态等。**必须传引用**（VAR_IN_OUT 语义） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    InVelocity     : BOOL; (* B *)
    Busy           : BOOL; (* E *)
    Active         : BOOL; (* E *)
    CommandAborted : BOOL; (* E *)
    Error          : BOOL; (* B *)
    ErrorID        : UDINT; (* E *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `InVelocity` | `BOOL` | 轴加速后达到请求的目标速度时，`InVelocity` 变为 `TRUE` |
| `Busy` | `BOOL` | `Execute` 启动后置 `TRUE` 并持续到 FB 激活结束；`Busy = FALSE` 时 FB 可接受新命令，同时 `CommandAborted` 或 `Error` 之一置位 |
| `Active` | `BOOL` | 表示命令正在执行 |
| `CommandAborted` | `BOOL` | 命令未能完整执行时置 `TRUE`：轴被停止或当前命令被另一条 Move 命令替换 |
| `Error` | `BOOL` | 发生错误时为 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出错误号（参见 §4） |

## 3. 行为说明

**触发语义**：`Execute` **上升沿**启动一次恒速行进。这是**无终点**运动——没有目标位置，轴一直按 `Direction` 方向以 `Velocity` 跑，直到被 Stop（`MC_Halt` / `MC_Stop`）或别的命令停下。

**`InVelocity` 而非 `Done`**：本 FB 没有 `Done` 输出，对应的"成功"信号是 `InVelocity`——轴加速到目标速度后 `InVelocity = TRUE`。**关键点**：一旦达到恒速，FB 任务即视为完成，**之后不再监视运动**。这意味着 `InVelocity = TRUE` 后，FB 不会持续盯着速度是否被外部扰动；它的职责到"把轴加速到目标速度"为止。

**加速阶段被中止**：若在尚未达到恒速的加速阶段命令被打断，则 `CommandAborted = TRUE`（被抢占）或 `Error = TRUE`（出错）。达到恒速后由于 FB 不再监视，抢占主要体现为新命令直接接管。

**`Direction` 默认正方向**：`Direction` 默认 `MC_Positive_Direction`，可选正 / 负方向。

**`ContinuousUpdate`（描述表所列）**：PDF 描述表说明若 `ContinuousUpdate = TRUE`，可在命令处理期间用 `Execute` 上升沿按新的 `Velocity` / `Acceleration` / `Deceleration` 改变动力学并尽快生效——用于运行中动态调速。但该输入未出现在 PDF 的 VAR_INPUT 代码块中（见 §2 注），引用前请确认实际库版本。

**停止方式**：恒速运动靠 `MC_Halt`（不锁）或 `MC_Stop`（锁轴）停止；`Execute` 撤销不停轴。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC/驱动错误号（不是 HRESULT）。

| 返回值 / 错误码 | 含义 | 处理建议 |
|---|---|---|
| `InVelocity = TRUE` | 已达到目标速度（之后 FB 不再监视运动） | 恒速行进中；停轴用 `MC_Halt` / `MC_Stop` |
| `CommandAborted = TRUE` | 加速阶段被抢占或被停止 | 视业务决定后续动作 |
| `Error = TRUE` + `ErrorID ≠ 0` | 运动出错（`Velocity ≤ 0`、轴未使能等） | 检查 `Velocity > 0`、轴是否已 `MC_Power` 使能；必要时 `MC_Reset` |

PDF 与 InfoSys 在本 FB 章节均未逐条列出具体 `ErrorID` 码值，具体码值需对照 TwinCAT NC 错误码总表（⚠️ PDF + InfoSys 本章节未枚举）。

## 5. 使用注意 / 常见坑

- **没有 `Done`，看 `InVelocity`**：成功信号是 `InVelocity`（达到目标速度），不是 `Done`。
- **达速后不再监视运动**：`InVelocity = TRUE` 后 FB 不持续盯速度。需要持续闭环监视速度要靠业务逻辑或外部监控，别假设 FB 会一直纠偏。
- **无终点运动靠 Stop 停**：本 FB 不会自己停。停轴用 `MC_Halt` / `MC_Stop`；`Execute` 撤销不停轴。
- **`Velocity` 必须 `>0`**：填 0 报错。要停轴用 Stop 命令不是给 0 速度。
- **`Direction` 默认正方向**：不显式给则按 `MC_Positive_Direction`。
- **运行中调速看 `ContinuousUpdate`**：PDF 描述表提到该机制，但它不在 VAR_INPUT 代码块里；用前确认库版本是否暴露。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_MoveVelocity.TcPOU`](../examples/P_Demo_MC_MoveVelocity.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：传送带启动后以 150 mm/s 恒速正向运行，直到用 MC_Halt 停下
PROGRAM P_Demo_MC_MoveVelocity
VAR
    fbMoveVelo      : MC_MoveVelocity;
    axisConveyor    : AXIS_REF;
    rtStartRun      : R_TRIG;              // 启动信号转上升沿
    bStartRun       : BOOL := FALSE;       // 在线写 TRUE 启动恒速运行
    lrRunVelocity   : LREAL := 150.0;      // 恒速目标速度 (mm/s)，必须 >0
    eRunDirection   : MC_Direction := MC_Positive_Direction;  // 正方向
    bInVelocity     : BOOL;                // 达到目标速度标志（非 Done）
    bVeloBusy       : BOOL;
    bVeloAborted    : BOOL;
    bVeloError      : BOOL;
    nVeloErrorID    : UDINT;
END_VAR

// 启动信号转上升沿；Direction 默认正向；Axis 是 VAR_IN_OUT 用 :=
rtStartRun(CLK := bStartRun);
fbMoveVelo(
    Execute        := rtStartRun.Q,
    Velocity       := lrRunVelocity,
    Acceleration   := 1000.0,
    Deceleration   := 1000.0,
    Direction      := eRunDirection,
    Axis           := axisConveyor,
    InVelocity     => bInVelocity,
    Busy           => bVeloBusy,
    CommandAborted => bVeloAborted,
    Error          => bVeloError,
    ErrorID        => nVeloErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：所有"匀速无终点运行"的场合：传送带 / 输送线、卷绕收放、连续给料、磨削进给。要点是"按某速度一直跑"，没有固定目标位置，靠工艺信号或停止命令终止。
- **价值**：业务代码不必去拼 NC 的速度模式命令、不必自己做加速到目标速度的判断，单个 FB 调用即把"按速度方向跑 + 达速上报"封装好；`InVelocity` 直接给出"已达目标速度"。
- **替代方案对比**：
  - 用 `MC_MoveAbsolute` 给一个很远的目标：能近似恒速段，但终点处会减速，不是真"无终点"
  - 直接写 NC 速度命令：要熟悉接口字段，且达速判断要自己做
  - **本 FB**：PLCopen 标准恒速运动入口，传送 / 卷绕类设备首选；配 `MC_Halt` / `MC_Stop` 停车

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf) §6.3.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8280997387.html
- **相关 FB / 类型**：`MC_Halt` / `MC_Stop`（停恒速运动）、`MC_Direction`（方向枚举）、`MC_MoveAbsolute`（有终点定位）、`MC_Power`（使能）
