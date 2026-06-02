# MC_MoveAbsolute

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_DriveMotionControl` |
| Library Version | `1.5.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `Point to point motion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8280601227.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_MoveAbsolute.TcPOU`](../examples/P_Demo_MC_MoveAbsolute.TcPOU) |

---

## 1. 功能简述

PLCopen Motion Control 标准定义的**绝对定位功能块（Function Block, FB）**。`Execute` 上升沿启动一次到绝对目标位置的定位，并在整段行程上监视轴的运动。到达目标位置后 `Done` 置 `TRUE`；被抢占则 `CommandAborted = TRUE`，出错则 `Error = TRUE`。

主要用于直线轴系统。对模数轴而言，`Position` 不被当作模数位置，而是连续绝对坐标系下的绝对位置——若要做模数定位请改用 `MC_MoveModulo`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Position     : LREAL;
    Velocity     : LREAL;
    Acceleration : LREAL;
    Deceleration : LREAL;
    Options      : ST_MoveOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次定位命令 |
| `Position` | `LREAL` | — | 用于定位的绝对目标位置 |
| `Velocity` | `LREAL` | — | 最大行进速度（`>0`） |
| `Acceleration` | `LREAL` | — | 加速度（`>0`） |
| `Deceleration` | `LREAL` | — | 减速度（`>0`） |
| `Options` | `ST_MoveOptions` | — | 数据结构（`ST_MoveOptions`），含附加的、很少用的参数。通常该输入可不用 |

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
| `Done` | `BOOL` | 目标位置到达时置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 启动后置 `TRUE` 并持续到运动命令处理结束；`Busy = FALSE` 时 FB 可接受新命令，同时 `Done` / `CommandAborted` / `Error` 之一置位 |
| `Active` | `BOOL` | 表示命令正在执行。命令被缓冲时，要等正在运行的命令完成后才变激活 |
| `CommandAborted` | `BOOL` | 命令未能完整执行时置 `TRUE`：轴被停止或当前命令被另一条 Move 命令替换 |
| `Error` | `BOOL` | 发生错误时为 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出错误号（参见 §4） |

## 3. 行为说明

**触发语义**：`Execute` **上升沿**启动一次绝对定位。命令进入执行后即在整段行程上监视轴运动直至到位。上升沿后 `Busy` 置 `TRUE`，到位后 `Done` 置 `TRUE`。`Execute` 撤销不会停轴——要停轴用 `MC_Halt` / `MC_Stop`。

**状态机三分支**（遵循库通用规则，`Busy` / `Done` / `CommandAborted` / `Error` 互斥）：
- **正常到位**：`Done = TRUE`、`CommandAborted = FALSE`、`Error = FALSE`
- **被抢占**：被另一条 Move 切入或被停止 → `CommandAborted = TRUE`、`Done = FALSE`
- **出错**：参数越界 / 轴未使能 / 超软限位等 → `Error = TRUE` 并给 `ErrorID`

**绝对位置语义**：`Position` 是工件坐标系下的绝对目标位置，不是"再走多少距离"（那是 `MC_MoveRelative`）。多次绝对定位到同一坐标不会累积误差。

**模数轴特例**：本 FB 对模数轴**不**按模数解释 `Position`——它把 `Position` 当作连续绝对坐标系下的绝对位置（例如 720° 就是 720°，不会折回到 0°）。要按模数定位（带方向、最短路径等）请用 `MC_MoveModulo`。

**本库不提供 `BufferMode`**：与某些运动库不同，本库的 Move FB 没有 `BufferMode` 输入，而是用 `Options : ST_MoveOptions` 承载少量可选参数。命令的接续 / 抢占按库的默认规则处理。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC/驱动错误号（不是 HRESULT）。

| 返回值 / 错误码 | 含义 | 处理建议 |
|---|---|---|
| `Done = TRUE` | 到达绝对目标位置 | 定位完成 |
| `CommandAborted = TRUE` | 被另一条 Move 抢占或被停止 | 视业务决定后续动作 |
| `Error = TRUE` + `ErrorID ≠ 0` | 定位出错（`Velocity ≤ 0`、轴未使能、超软限位等） | 检查 `Velocity` / `Acceleration` / `Deceleration` 均 `>0`、轴是否已 `MC_Power` 使能、目标是否在软限位内；必要时 `MC_Reset` |

PDF 与 InfoSys 在本 FB 章节均未逐条列出具体 `ErrorID` 码值，具体码值需对照 TwinCAT NC 错误码总表（⚠️ PDF + InfoSys 本章节未枚举）。

## 5. 使用注意 / 常见坑

- **`Execute` 是边沿触发**：上升沿发一次命令。把 `Execute` 一直拉高期望"持续保持目标位置"是误解——只第一次有效，改 `Position` 不会自动跟随。
- **`Velocity` / `Acceleration` / `Deceleration` 都要 `>0`**：本库 MC_MoveAbsolute 明确要求三者 `>0`（注意：不同于某些库允许加减速为 0 表示用默认值）。填 0 会报错。
- **模数轴慎用**：`Position = 720°` 不会"多转两圈"，会被当作绝对 720°。模数定位用 `MC_MoveModulo`。
- **`Execute` 撤销不停轴**：停轴要用 `MC_Halt` / `MC_Stop`，不是把 `Execute` 置 `FALSE`。
- **本库无 `BufferMode`**：不要按其它库的习惯找 `BufferMode` 输入；本库用 `Options : ST_MoveOptions`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_MoveAbsolute.TcPOU`](../examples/P_Demo_MC_MoveAbsolute.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：进给轴把工件从取料位移动到加工绝对坐标 250.0 mm
PROGRAM P_Demo_MC_MoveAbsolute
VAR
    fbMoveAbs       : MC_MoveAbsolute;
    axisFeed        : AXIS_REF;
    rtStartMove     : R_TRIG;              // 启动信号转上升沿
    bStartMove      : BOOL := FALSE;       // 在线写 TRUE 触发一次绝对定位
    lrTargetPos     : LREAL := 250.0;      // 加工绝对坐标 (mm)
    lrMoveVelo      : LREAL := 300.0;      // 行进速度 (mm/s)，必须 >0
    bMoveDone       : BOOL;
    bMoveBusy       : BOOL;
    bMoveAborted    : BOOL;
    bMoveError      : BOOL;
    nMoveErrorID    : UDINT;
END_VAR

// 启动信号转上升沿；Acceleration/Deceleration 必须 >0；Axis 是 VAR_IN_OUT 用 :=
rtStartMove(CLK := bStartMove);
fbMoveAbs(
    Execute        := rtStartMove.Q,
    Position       := lrTargetPos,
    Velocity       := lrMoveVelo,
    Acceleration   := 3000.0,
    Deceleration   := 3000.0,
    Axis           := axisFeed,
    Done           => bMoveDone,
    Busy           => bMoveBusy,
    CommandAborted => bMoveAborted,
    Error          => bMoveError,
    ErrorID        => nMoveErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：所有"把轴开到一个确定坐标"的场合：进给轴定位到加工位、托盘定位、定长收放卷的目标位、简易取放的固定工位。要点是"目标坐标在工件坐标系下已知"。
- **价值**：业务代码不必去拼 NC 通道命令、不必自己监视整段行程，单个 FB 调用即把"发命令 + 监视到位 + 上报状态"封装好；绝对坐标语义下多次定位不累积误差。
- **替代方案对比**：
  - 直接写 NC 通道命令：要熟悉 NCTOPLC/PLCTONC 接口字段，升级有适配风险
  - 用 `MC_MoveRelative`：要业务自己累加位置，连续相对定位会累积漂移
  - **本 FB**：直接给绝对坐标，最直觉、误差不累积，PLCopen 标准

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf) §6.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8280601227.html
- **相关 FB**：`MC_MoveRelative`（相对距离）、`MC_MoveModulo`（模数轴专用）、`MC_MoveVelocity`（恒速）、`MC_Halt` / `MC_Stop`（停轴）、`MC_Power`（使能）
