# MC_Jog

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_DriveMotionControl` |
| Library Version | `1.5.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `Manual motion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8280347019.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_Jog.TcPOU`](../examples/P_Demo_MC_Jog.TcPOU) |

---

## 1. 功能简述

**手动寸动（Jog）功能块（Function Block, FB）**，让轴通过手动按键移动。两个按键信号可直接接到 `JogForward`（正向）和 `JogBackwards`（反向）输入。

适合调试和手动操作场景：按住正向键轴往正方向走、按住反向键往反方向走。两个方向内部互锁，运动期间不接受新的信号沿。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    JogForward   : BOOL;
    JogBackwards : BOOL;
    Velocity     : LREAL;
    Acceleration : LREAL;
    Deceleration : LREAL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `JogForward` | `BOOL` | — | 上升沿触发命令，轴沿**正方向**移动。运动期间不接受更多信号沿（含 `JogBackwards` 输入） |
| `JogBackwards` | `BOOL` | — | 上升沿触发命令，轴沿**负方向**移动。`JogForward` 与 `JogBackwards` 应择一触发，二者内部也互锁 |
| `Velocity` | `LREAL` | — | 最大行进速度（`>0`） |
| `Acceleration` | `LREAL` | — | 加速度（`≥0`） |
| `Deceleration` | `LREAL` | — | 减速度（`≥0`） |

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
    CommandAborted : BOOL;
    Error          : BOOL;
    ErrorID        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 一次运动成功完成时置 `TRUE` |
| `Busy` | `BOOL` | FB 处于激活状态时为 `TRUE`；处于默认（空闲）状态时为 `FALSE`。只有 `Busy = FALSE` 时寸动输入才能再接受一个新边沿 |
| `CommandAborted` | `BOOL` | 过程被外部事件中断（例如被 `MC_Stop` 调用）时置 `TRUE` |
| `Error` | `BOOL` | 发生错误时为 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出错误号（参见 §4） |

> 注：PDF 的图示与描述表另列有 `Active` 输出（"Indicates that the axis is moved via the jog function"，表示轴正通过寸动功能移动）；但 PDF 在本 FB 的 `VAR_OUTPUT` 代码块中**未列出** `Active`，故本文严格按 PDF 的 `VAR_OUTPUT` 代码块搬运，不在接口代码块中列 `Active`。

## 3. 行为说明

**触发语义**：`JogForward` / `JogBackwards` 都是**上升沿**触发。给 `JogForward` 上升沿轴沿正方向移动，给 `JogBackwards` 上升沿轴沿负方向移动。这与"按住走、松开停"的纯电平点动不同——本 FB 是边沿启动一段寸动。

**运动期间锁信号沿**：一旦寸动启动（`Busy = TRUE`），运动期间**不接受任何新的信号沿**，包括另一方向的键。只有运动结束、`Busy` 回到 `FALSE` 后，寸动输入才能再接受下一个边沿。因此快速反复打两个方向键不会让轴来回抖——多余的沿被忽略。

**方向互锁**：`JogForward` 和 `JogBackwards` 内部互锁，应择一触发。同时给两个方向不会让轴"两个命令叠加"，互锁会处理冲突。

**`Active` 表示寸动控制中**：PDF 描述表里的 `Active` 输出表示"轴正通过寸动功能移动"。被 `MC_Stop` 等外部命令打断则 `CommandAborted = TRUE`。

**典型用法**：调试面板上的"正向 / 反向"两个点动按钮，信号转上升沿后接 `JogForward` / `JogBackwards`；`Velocity` 设一个慢速调试速度。注意这里是边沿语义，若想实现"按住持续走"需要在外部把按钮电平在按住期间不断重新制造沿，或结合库的其它运动模式。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC/驱动错误号（不是 HRESULT）。

| 返回值 / 错误码 | 含义 | 处理建议 |
|---|---|---|
| `Done = TRUE` | 一次寸动成功完成 | 轴已停在寸动结束位置 |
| `CommandAborted = TRUE` | 寸动被外部命令打断（如 `MC_Stop`） | 视业务决定后续动作 |
| `Error = TRUE` + `ErrorID ≠ 0` | 寸动出错（`Velocity ≤ 0`、轴未使能、超软限位等） | 检查 `Velocity > 0`、轴是否已 `MC_Power` 使能、目标是否在软限位内 |

PDF 与 InfoSys 在本 FB 章节均未逐条列出具体 `ErrorID` 码值，具体码值需对照 TwinCAT NC 错误码总表（⚠️ PDF + InfoSys 本章节未枚举）。

## 5. 使用注意 / 常见坑

- **是边沿触发不是按住电平**：`JogForward` / `JogBackwards` 上升沿启动寸动。把它当"按住走、松开停"会发现行为不符预期；要持续走需在外部持续制造沿或换用其它运动 FB。
- **运动中锁信号沿**：寸动进行时（`Busy = TRUE`）所有新边沿被忽略，包括反方向键。等 `Busy = FALSE` 才能再触发。
- **两个方向择一**：`JogForward` 和 `JogBackwards` 内部互锁，不要同时给。
- **`Velocity` 必须 `>0`**：填 `0` 不会让轴"原地不动"而是报错。
- **`Active` 不在接口代码块里**：PDF 的 VAR_OUTPUT 代码块未列 `Active`（仅图示/描述表有）。本文按 PDF 代码块搬运。引用 `Active` 前请确认实际库版本是否暴露该输出。
- **寸动前要先使能**：轴未 `MC_Power` 使能时寸动无法运动。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_Jog.TcPOU`](../examples/P_Demo_MC_Jog.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：调试面板上的"正向/反向"点动按钮，慢速手动移动进给轴用于对刀/找正
PROGRAM P_Demo_MC_Jog
VAR
    fbJog           : MC_Jog;
    axisFeed        : AXIS_REF;
    bJogFwdButton   : BOOL := FALSE;       // 在线写 TRUE 模拟按正向点动键
    bJogBwdButton   : BOOL := FALSE;       // 在线写 TRUE 模拟按反向点动键
    lrJogVelocity   : LREAL := 20.0;       // 慢速调试速度 (mm/s)
    bJogDone        : BOOL;
    bJogBusy        : BOOL;
    bJogAborted     : BOOL;
    bJogError       : BOOL;
    nJogErrorID     : UDINT;
END_VAR

// 单次调用：JogForward/JogBackwards 走上升沿；Axis 是 VAR_IN_OUT 用 :=
fbJog(
    JogForward     := bJogFwdButton,
    JogBackwards   := bJogBwdButton,
    Velocity       := lrJogVelocity,
    Acceleration   := 200.0,
    Deceleration   := 200.0,
    Axis           := axisFeed,
    Done           => bJogDone,
    Busy           => bJogBusy,
    CommandAborted => bJogAborted,
    Error          => bJogError,
    ErrorID        => nJogErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：所有需要手动点动轴的场合：设备调试时对刀 / 找正、维护时手动挪轴、HMI 上的"正向 / 反向"点动按钮。是产线调试与维护最常用的手动运动原语。
- **价值**：业务代码不必去拼 NC 的点动命令、不必自己处理方向互锁与运动中锁沿，单个 FB 调用即把"按键→寸动→互锁"封装好；两个方向输入可直接接按钮信号。
- **替代方案对比**：
  - 用 `MC_MoveRelative` 模拟点动：要自己算每次移动距离、自己做方向互锁，繁琐
  - 用 `MC_MoveVelocity` + 手动停：能做"按住走"，但需自己管启停时序与互锁
  - **本 FB**：PLCopen 标准点动入口，方向互锁与运动中锁沿内建，调试 / 手动操作首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf) §6.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8280347019.html
- **相关 FB**：`MC_MoveVelocity`（恒速运动）、`MC_Power`（点动前使能）、`MC_Stop`（打断点动）
