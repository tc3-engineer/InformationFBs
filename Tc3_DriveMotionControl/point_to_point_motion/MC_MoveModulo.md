# MC_MoveModulo

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_DriveMotionControl` |
| Library Version | `1.5.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `Point to point motion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8280683915.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_MoveModulo.TcPOU`](../examples/P_Demo_MC_MoveModulo.TcPOU) |

---

## 1. 功能简述

PLCopen Motion Control 标准定义的**模数定位功能块（Function Block, FB）**，用于执行参照轴**模数位置**的定位。模数旋转的基准是 `AXIS_REF` 结构里可调的"模数因子"参数（`Axis.Parameter.ModuloFactor`，例如 360°）。

根据 `Direction` 输入分三种起始方式：**正方向定位**、**负方向定位**、**最短路径定位**。轴从静止启动时，可指定 ≥ 360° 的位置以执行额外的整圈旋转。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Position     : LREAL;
    Velocity     : LREAL;
    Acceleration : LREAL;
    Deceleration : LREAL;
    Direction    : MC_Direction;
    Options      : ST_MoveOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次定位命令 |
| `Position` | `LREAL` | — | 用于定位的模数目标位置。若轴从静止启动，大于 360° 的位置会产生额外整圈。**不允许负位置** |
| `Velocity` | `LREAL` | — | 最大行进速度（`>0`） |
| `Acceleration` | `LREAL` | — | 加速度（`≥0`） |
| `Deceleration` | `LREAL` | — | 减速度（`≥0`） |
| `Direction` | `MC_Direction` | — | 正方向或负方向（类型 `MC_Direction`）。若轴在运动中启动，方向不可反转 |
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

**触发语义**：`Execute` **上升沿**启动一次模数定位，在整段行程上监视轴运动。输出遵循库通用规则（`Busy` / `Done` / `CommandAborted` / `Error` 互斥）。

**三种方向起始**（由 `Direction` 决定）：
- **正方向定位**：沿模数坐标正方向走到目标
- **负方向定位**：沿模数坐标负方向走到目标
- **最短路径定位**：自动选正 / 负中更短的一边

**模数因子是基准**：模数旋转基于 `Axis.Parameter.ModuloFactor`（例如 360°）。目标位置 `Position` 是模数坐标系下的位置，**不允许为负**。

**从静止启动可做额外整圈**：若轴从静止启动，可指定 ≥ 360° 的位置以执行额外整圈。例如请求正方向 450°，轴会转一圈再到 90°。

**特殊情形（PDF 重点提示）**：请求"一圈或多圈完整模数旋转"时要特别注意行为。若轴恰好在精确设定位置 90° 且要定位到 90°，则**不执行运动**；若请求正方向 450°，轴执行一圈。**轴复位（reset）之后行为可能不同**——复位会把当前实际位置当作设定位置，导致轴不再精确处于 90°，而是略低或略高，于是要么变成到 90° 的最小定位、要么变成一整圈。对于完整模数旋转，**更稳妥的做法**往往是基于当前绝对位置计算目标位置，再用 `MC_MoveAbsolute` 定位。

**运动中不可反向**：若轴在运动中再次启动本 FB，方向不可反转。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC/驱动错误号（不是 HRESULT）。

| 返回值 / 错误码 | 含义 | 处理建议 |
|---|---|---|
| `Done = TRUE` | 到达模数目标位置 | 定位完成 |
| `CommandAborted = TRUE` | 被另一条 Move 抢占或被停止 | 视业务决定后续动作 |
| `Error = TRUE` + `ErrorID ≠ 0` | 定位出错（`Position` 为负、`Velocity ≤ 0`、运动中反向、轴未使能等） | 确认 `Position ≥ 0`、`Velocity > 0`、未在运动中反向、轴已使能；必要时 `MC_Reset` |

PDF 与 InfoSys 在本 FB 章节均未逐条列出具体 `ErrorID` 码值，具体码值需对照 TwinCAT NC 错误码总表（⚠️ PDF + InfoSys 本章节未枚举）。

## 5. 使用注意 / 常见坑

- **`Position` 不允许负值**：模数目标位置必须 `≥ 0`。负值会报错。要反方向走用 `Direction` 控制，不是给负位置。
- **完整整圈行为对复位敏感**：复位后实际位置被当作设定位置，可能让"到 90°"变成"转一圈"或反之。要确定性整圈，PDF 建议基于当前绝对位置算目标再用 `MC_MoveAbsolute`。
- **运动中不可反向**：运动途中再触发本 FB，方向不能反转，否则报错。
- **最短路径要靠 `Direction`**：三种方向语义靠 `MC_Direction` 枚举选择；选错会走反方向或非最短路径。
- **模数因子要先配好**：模数基准是 `Axis.Parameter.ModuloFactor`，须在轴参数里正确设置（如转台 360°）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_MoveModulo.TcPOU`](../examples/P_Demo_MC_MoveModulo.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：分度转台正方向转到 90° 工位（模数轴，模数因子 360°）
PROGRAM P_Demo_MC_MoveModulo
VAR
    fbMoveMod       : MC_MoveModulo;
    axisTurntable   : AXIS_REF;
    rtIndexReq      : R_TRIG;              // 分度请求转上升沿
    bIndexRequest   : BOOL := FALSE;       // 在线写 TRUE 触发一次分度
    lrStationAngle  : LREAL := 90.0;       // 目标工位角度 (°)，模数位置必须 ≥0
    eMoveDir        : MC_Direction := MC_Positive_Direction;  // 正方向
    bModDone        : BOOL;
    bModBusy        : BOOL;
    bModAborted     : BOOL;
    bModError       : BOOL;
    nModErrorID     : UDINT;
END_VAR

// 分度请求转上升沿；Direction 选正方向；Axis 是 VAR_IN_OUT 用 :=
rtIndexReq(CLK := bIndexRequest);
fbMoveMod(
    Execute        := rtIndexReq.Q,
    Position       := lrStationAngle,
    Velocity       := 180.0,
    Acceleration   := 1000.0,
    Deceleration   := 1000.0,
    Direction      := eMoveDir,
    Axis           := axisTurntable,
    Done           => bModDone,
    Busy           => bModBusy,
    CommandAborted => bModAborted,
    Error          => bModError,
    ErrorID        => nModErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：旋转 / 分度类机构：分度转台到固定工位、旋转刀库选刀、回转工作台、连续旋转的相位定位。共同点是坐标按模数（如 360°）折回，关心的是"转到某个角度"而非"绝对累计角度"。
- **价值**：业务代码不必自己处理"角度折回 360°"的环绕计算、不必自己判正反向与最短路径，单个 FB 调用即完成模数定位；`Direction` 一个枚举覆盖正 / 负 / 最短路径。
- **替代方案对比**：
  - 用 `MC_MoveAbsolute` 自己算环绕：要手动把目标角折算成连续绝对坐标，边界条件多；但对"确定性整圈"PDF 反而推荐这种方式
  - 自己用相对运动累加：方向 / 最短路径都要自己算，易错
  - **本 FB**：PLCopen 标准模数定位入口，正 / 负 / 最短路径内建；注意整圈对复位敏感的特殊情形

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf) §6.3.3（另见 §6.3.4 Modulo positioning）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8280683915.html
- **相关 FB / 类型**：`MC_MoveAbsolute`（连续绝对坐标，确定性整圈推荐）、`MC_Direction`（方向枚举）、`MC_Halt` / `MC_Stop`（停轴）
