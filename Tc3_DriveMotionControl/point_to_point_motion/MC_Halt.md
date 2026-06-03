# MC_Halt

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_DriveMotionControl` |
| Library Version | `1.5.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `Point to point motion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8280917515.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_Halt.TcPOU`](../examples/P_Demo_MC_Halt.TcPOU) |

---

## 1. 功能简述

PLCopen Motion Control 标准定义的**软停车功能块（Function Block, FB）**。`Execute` 上升沿触发，按给定减速度把轴沿减速斜坡停下。

与 `MC_Stop` 的本质区别：`MC_Halt` 停车后**不锁轴**——轴停下后可以被另一条命令重新启动，无需复位。因此 `MC_Halt` 是**正常工艺停车**的首选；`MC_Stop` 用于需要锁轴的特殊 / 故障停车。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Deceleration : LREAL;
    Options      : ST_MoveOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次停车命令 |
| `Deceleration` | `LREAL` | — | 减速度。值 `≤ 0` 时采用上一条 Move 命令的减速度。出于安全，`MC_Halt` / `MC_Stop` 不能用比当前激活运动更弱的动力学执行——必要时参数化会被自动调整 |
| `Options` | `ST_MoveOptions` | — | 数据结构（`ST_MoveOptions`），含附加的、很少需要的参数。通常该输入可不用 |

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
| `Done` | `BOOL` | 轴已停下且静止时置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 启动后置 `TRUE` 并持续到命令处理结束；`Busy = FALSE` 时 FB 可接受新命令，同时 `Done` / `CommandAborted` / `Error` 之一置位 |
| `Active` | `BOOL` | 表示命令正在执行。命令被缓冲时，要等正在运行的命令完成后才变激活 |
| `CommandAborted` | `BOOL` | 命令未能完整执行时置 `TRUE`。正在运行的停车命令后面可能跟了一条 Move 命令把它抢占 |
| `Error` | `BOOL` | 发生错误时为 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出错误号（参见 §4） |

## 3. 行为说明

**触发语义**：`Execute` **上升沿**启动减速停车。上升沿后 `Busy` 置 `TRUE`，轴减速到静止后 `Done` 置 `TRUE`、`Busy` 落 `FALSE`。输出遵循库通用规则（`Busy` / `Done` / `CommandAborted` / `Error` 互斥）。

**不锁轴是核心特性**：停车完成（`Done = TRUE`）后轴只是停下，**没有被锁**——后续可以直接发 Move 命令重新启动，不需要 `MC_Reset`。这正是与 `MC_Stop` 的本质差异：`MC_Stop` 停车后锁轴，必须 `MC_Reset` 解锁才能再动。

**减速度的安全约束**：`Deceleration ≤ 0` 时采用上一条 Move 命令的减速度。出于安全，停车的减速度不允许比当前正在执行的运动命令更"软"（更慢的减速会导致停车距离过长甚至冲出）。如果给的减速度偏弱，系统会自动调整参数化以保证不弱于当前运动。

**可被 Move 抢占**：`MC_Halt` 停车过程中若发来新的 Move 命令，停车会被抢占，`CommandAborted = TRUE`。这是"不锁轴"的直接体现——轴随时可被重新调度。

**何时用 `MC_Halt` 而非 `MC_Stop`**：正常工艺停车、节拍中的暂停、流程切换前的停车，都用 `MC_Halt`（不锁、可立即重启）。需要"停下来并锁住、防止误启动"的故障 / 安全场景才用 `MC_Stop`。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC/驱动错误号（不是 HRESULT）。

| 返回值 / 错误码 | 含义 | 处理建议 |
|---|---|---|
| `Done = TRUE` | 轴已停下且静止（未锁轴） | 可直接发新的 Move 命令重启 |
| `CommandAborted = TRUE` | 停车被新的 Move 命令抢占 | 正常现象，轴已被重新调度 |
| `Error = TRUE` + `ErrorID ≠ 0` | 停车出错（轴未使能、参数非法等） | 检查轴状态；必要时 `MC_Reset` 清错 |

PDF 与 InfoSys 在本 FB 章节均未逐条列出具体 `ErrorID` 码值，具体码值需对照 TwinCAT NC 错误码总表（⚠️ PDF + InfoSys 本章节未枚举）。

## 5. 使用注意 / 常见坑

- **`MC_Halt` 不锁轴**：停下后可直接重启，无需 `MC_Reset`。需要锁轴防误启动用 `MC_Stop`。
- **减速度不能比当前运动更弱**：出于安全，停车减速度会被自动调整到不弱于当前运动命令。给一个很小的减速度想"缓停"可能被系统改写。
- **`Deceleration ≤ 0` 用上一条 Move 的减速度**：不显式给减速度时沿用上次 Move 的值。
- **停车中可被 Move 抢占**：这是不锁轴的特性。若你期望"停了就别动"，`MC_Halt` 不保证——要锁请用 `MC_Stop`。
- **正常停车别用 `MC_Stop`**：用 `MC_Stop` 每次都要 `MC_Reset`，多余操作拖慢节拍。常规停车用 `MC_Halt`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_Halt.TcPOU`](../examples/P_Demo_MC_Halt.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：传送带匀速运行中，工艺节拍要求暂停一下，用 MC_Halt 缓停（停后不锁，可立即重启）
PROGRAM P_Demo_MC_Halt
VAR
    fbHalt          : MC_Halt;
    axisConveyor    : AXIS_REF;
    rtPauseReq      : R_TRIG;              // 暂停请求转上升沿
    bPauseRequest   : BOOL := FALSE;       // 在线写 TRUE 触发一次缓停
    lrHaltDecel     : LREAL := 500.0;      // 停车减速度 (mm/s^2)
    bHaltDone       : BOOL;
    bHaltBusy       : BOOL;
    bHaltAborted    : BOOL;
    bHaltError      : BOOL;
    nHaltErrorID    : UDINT;
END_VAR

// 暂停请求转上升沿；Axis 是 VAR_IN_OUT 用 :=
rtPauseReq(CLK := bPauseRequest);
fbHalt(
    Execute        := rtPauseReq.Q,
    Deceleration   := lrHaltDecel,
    Axis           := axisConveyor,
    Done           => bHaltDone,
    Busy           => bHaltBusy,
    CommandAborted => bHaltAborted,
    Error          => bHaltError,
    ErrorID        => nHaltErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：所有需要"正常停一下、之后还要继续"的工艺停车：传送带节拍暂停、流程步骤切换前停轴、HMI 上的"暂停"按钮。不涉及故障锁定，停后要能立即重启。
- **价值**：业务代码不必去拼 NC 停车命令、不必自己维护"停车减速度不弱于当前运动"的安全约束，单个 FB 调用即完成受控减速停车；停后不锁，下一条 Move 直接重启。
- **替代方案对比**：
  - 用 `MC_Stop`：会锁轴，每次重启都要 `MC_Reset`，正常停车不该用
  - 落 `MC_Power.Enable`：非受控停车（自由滑行），机械冲击大
  - 发一个 `Velocity = 0` 的 Move：本库 Move 要求 `Velocity > 0`，不能这么停
  - **本 FB**：PLCopen 标准的"软停不锁"入口，正常工艺停车首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf) §6.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8280917515.html
- **相关 FB**：`MC_Stop`（停车并锁轴，需 `MC_Reset` 解锁）、各 `MC_Move*`（停后可重启的运动命令）、`MC_Reset`（清错）
