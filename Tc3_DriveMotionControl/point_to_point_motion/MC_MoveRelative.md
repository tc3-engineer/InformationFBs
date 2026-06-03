# MC_MoveRelative

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_DriveMotionControl` |
| Library Version | `1.5.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `Point to point motion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8280630411.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_MoveRelative.TcPOU`](../examples/P_Demo_MC_MoveRelative.TcPOU) |

---

## 1. 功能简述

PLCopen Motion Control 标准定义的**相对定位功能块（Function Block, FB）**。`Execute` 上升沿启动一次基于当前**设定位置**的相对定位，并在整段行程上监视轴的运动。

到达目标位置后 `Done` 置 `TRUE`；否则被抢占时 `CommandAborted = TRUE`、出错时 `Error = TRUE`。相对定位的起点是"当前 NC 设定位置"，目标 = 起点 + `Distance`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Distance     : LREAL;
    Velocity     : LREAL;
    Acceleration : LREAL;
    Deceleration : LREAL;
    Options      : ST_MoveOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次定位命令 |
| `Distance` | `LREAL` | — | 用于定位的相对距离（相对当前设定位置；可正可负代表方向） |
| `Velocity` | `LREAL` | — | 最大行进速度（`>0`） |
| `Acceleration` | `LREAL` | — | 加速度（`≥0`） |
| `Deceleration` | `LREAL` | — | 减速度（`≥0`） |
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

**触发语义**：`Execute` **上升沿**启动一次相对定位，在整段行程上监视轴运动。上升沿后 `Busy` 置 `TRUE`，到位后 `Done` 置 `TRUE`。输出遵循库通用规则（`Busy` / `Done` / `CommandAborted` / `Error` 互斥）。

**相对距离的起点**：起点是**当前 NC 设定位置**（set position），目标 = 设定位置 + `Distance`。`Distance` 可正可负表示方向。注意起点是"设定位置"而非"实际位置"——存在跟随误差时两者略有差别，相对定位以设定位置为基准。

**状态机三分支**：正常到位 → `Done = TRUE`；被另一条 Move 抢占或被停止 → `CommandAborted = TRUE`；参数越界 / 轴未使能等 → `Error = TRUE`。

**与绝对定位的区别**：相对定位关心"再走多少距离"，绝对定位关心"开到哪个坐标"。连续多次相对定位会**累积**——每次都从上次结束的设定位置再加 `Distance`，因此长期使用会有累计误差漂移。需要"到确定坐标且不漂移"用 `MC_MoveAbsolute`。

**本库不提供 `BufferMode`**：与 `MC_MoveAbsolute` 一样，本库相对定位也没有 `BufferMode` 输入，可选参数走 `Options : ST_MoveOptions`。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC/驱动错误号（不是 HRESULT）。

| 返回值 / 错误码 | 含义 | 处理建议 |
|---|---|---|
| `Done = TRUE` | 到达相对目标位置 | 定位完成 |
| `CommandAborted = TRUE` | 被另一条 Move 抢占或被停止 | 视业务决定后续动作 |
| `Error = TRUE` + `ErrorID ≠ 0` | 定位出错（`Velocity ≤ 0`、轴未使能、超软限位等） | 检查 `Velocity > 0`、轴是否已 `MC_Power` 使能、目标是否在软限位内；必要时 `MC_Reset` |

PDF 与 InfoSys 在本 FB 章节均未逐条列出具体 `ErrorID` 码值，具体码值需对照 TwinCAT NC 错误码总表（⚠️ PDF + InfoSys 本章节未枚举）。

## 5. 使用注意 / 常见坑

- **起点是设定位置不是实际位置**：相对定位以 NC 设定位置为基准。有跟随误差时和实际位置略有差别。
- **连续相对定位会累积漂移**：每次从上次结束位置再加 `Distance`，长期累计误差。要"到确定坐标"用 `MC_MoveAbsolute`。
- **`Execute` 是边沿触发**：上升沿发一次命令；一直拉高不会反复走。
- **`Velocity` 必须 `>0`**：填 0 报错。停轴用 `MC_Halt` / `MC_Stop`。
- **`Distance` 符号代表方向**：正向 / 负向用 `Distance` 的正负表示。
- **本库无 `BufferMode`**：可选参数走 `Options : ST_MoveOptions`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_MoveRelative.TcPOU`](../examples/P_Demo_MC_MoveRelative.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：步进送料每次相对前进 50.0 mm（一个料距），可正可负调向
PROGRAM P_Demo_MC_MoveRelative
VAR
    fbMoveRel       : MC_MoveRelative;
    axisFeeder      : AXIS_REF;
    rtStepReq       : R_TRIG;              // 步进请求转上升沿
    bStepRequest    : BOOL := FALSE;       // 在线写 TRUE 触发一次步进
    lrStepDistance  : LREAL := 50.0;       // 每步相对距离 (mm)，正=前进
    bRelDone        : BOOL;
    bRelBusy        : BOOL;
    bRelAborted     : BOOL;
    bRelError       : BOOL;
    nRelErrorID     : UDINT;
END_VAR

// 步进请求转上升沿；Axis 是 VAR_IN_OUT 用 :=
rtStepReq(CLK := bStepRequest);
fbMoveRel(
    Execute        := rtStepReq.Q,
    Distance       := lrStepDistance,
    Velocity       := 200.0,
    Acceleration   := 2000.0,
    Deceleration   := 2000.0,
    Axis           := axisFeeder,
    Done           => bRelDone,
    Busy           => bRelBusy,
    CommandAborted => bRelAborted,
    Error          => bRelError,
    ErrorID        => nRelErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：步进 / 增量式运动：步进送料每次前进一个料距、点动一个固定增量、相对修正位置。要点是"在当前位置基础上再走一段"，而非"到某个绝对坐标"。
- **价值**：业务代码不必自己读当前位置再算目标坐标，直接给"再走多少"即可；单个 FB 调用完成发命令 + 监视到位 + 上报状态。
- **替代方案对比**：
  - 用 `MC_MoveAbsolute` 模拟：要先读当前设定位置再加 `Distance` 算绝对目标，多一步
  - 自己累加位置发绝对命令：逻辑等价但要自己维护累加变量，易出错
  - **本 FB**：PLCopen 标准相对定位入口；但注意连续使用会累积漂移，定长场景配合周期性 `MC_MoveAbsolute` 校准更稳

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf) §6.3.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8280630411.html
- **相关 FB**：`MC_MoveAbsolute`（绝对坐标、不漂移）、`MC_MoveModulo`（模数轴）、`MC_Halt` / `MC_Stop`（停轴）、`MC_Power`（使能）
