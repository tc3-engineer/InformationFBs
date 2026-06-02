# MC_MoveContinuousAbsolute

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Point to point motion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70103947.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_MoveContinuousAbsolute.TcPOU`](../examples/P_Demo_MC_MoveContinuousAbsolute.TcPOU) |

---


## 1. 功能简述

PLCopen 标准定义的**带终末速度的绝对定位 FB**。轴沿整段轨迹监视，到达 `Position` 时**不停车，而是保持 `EndVelocity` 继续走**——`InEndVelocity := TRUE` 标志到达目标位置且已达到终末速度。

目标位置到达后 FB 任务结束，轴不再被本 FB 监视；后续要做什么完全由业务下一条命令决定（典型搭配是 `MC_Halt` 或另一条 `MC_MoveAbsolute`）。**不支持高/低速专用轴**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Position     : LREAL;
    Velocity     : LREAL;
    EndVelocity  : LREAL;
    Acceleration : LREAL;
    Deceleration : LREAL;
    Jerk         : LREAL;
    BufferMode   : MC_BufferMode;
    Options      : ST_MoveOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次定位命令；命令进入运动队列后即开始执行，不需保持高电平 |
| `Position` | `LREAL` | — | 绝对目标位置 |
| `Velocity` | `LREAL` | — | 行程中最大行进速度，`>0` |
| `EndVelocity` | `LREAL` | — | 到达 `Position` 时维持的终末速度 |
| `Acceleration` | `LREAL` | — | 加速度，要求 `≥0`；填 `0` 表示采用轴参数中默认加速度 |
| `Deceleration` | `LREAL` | — | 减速度，要求 `≥0`；填 `0` 表示采用轴参数中默认减速度 |
| `Jerk` | `LREAL` | — | 加加速度（Jerk），要求 `≥0`；填 `0` 表示采用轴参数中默认 Jerk |
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
    InEndVelocity  : BOOL;
    Busy           : BOOL;
    Active         : BOOL;
    CommandAborted : BOOL;
    Error          : BOOL;
    ErrorID        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `InEndVelocity` | `BOOL` | 到达 `Position` 且已达 `EndVelocity` 时置 `TRUE`；之后 FB 不再监视 |
| `Busy` | `BOOL` | `Execute` 上升沿后立即变 `TRUE`，结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE` |
| `Active` | `BOOL` | 表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE` |
| `CommandAborted` | `BOOL` | 命令未完成就被中止（被另一 Move 抢占 / `MC_Stop` 停掉）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |

## 3. 行为说明

**触发**：`Execute` 上升沿；轴按 `Velocity` 加速行进，临近 `Position` 时让出剩余距离用于减速，到达 `Position` 时速度恰为 `EndVelocity`。

**状态机**：与 `MC_MoveVelocity` 类似——`InEndVelocity` 一旦置位 FB 即"放手"，与 `MC_MoveAbsolute` 持续监视到位的语义不同。

**为何要"过点不停"**：典型应用是**连续工艺段**：例如激光切割完一段直线后**不要在拐点完全停下来**（会出过烧痕），而要保持 `EndVelocity` 衔接下一段弧线。Beckhoff 在 PDF 中明确给出 `MC_MoveContinuousAbsolute` 是为这类"过点连续运动"设计的——配合下一条 `MC_MoveContinuousRelative` 或 `MC_MoveAbsolute` 用 `BufferMode = Buffered` 串接。

**轴不被监视**：`InEndVelocity = TRUE` 后**只能保证**该瞬间速度等于 `EndVelocity`、位置等于 `Position`。之后如果业务没发新命令，NC 仍会按 `EndVelocity` 继续走，**这是预期行为**。

**不支持高/低速轴**。`EndVelocity = 0` 退化为普通 `MC_MoveAbsolute` 行为，但建议直接用后者更清晰。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **`EndVelocity > 0` 时轴不会停**：`InEndVelocity = TRUE` 后轴继续走，必须有下一条命令兜底，**否则轴一路冲到软限位报错**。
- **`EndVelocity > Velocity` 会报错**：终末速度不能超过行程速度。
- **拐点匀速过渡需要 `Buffered`**：单实例用 `Aborting` 起不到过点效果；两段过点连续运动需要**两个不同实例**配 `BufferMode := MC_Buffered`。
- **不支持高/低速轴**：硬件类型为 high/low speed axis 报错。
- **小心 `BufferMode = Blending*`**：blending 模式会让两段轨迹"融合"，行为比 Buffered 复杂，没有把握就先用 Buffered。
- **业务必须有"兜底停车"机制**：写代码时记得在状态机 Error 分支或紧急停止信号触发时调 `MC_Halt`，否则轴永远不停。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_MoveContinuousAbsolute.TcPOU`](../examples/P_Demo_MC_MoveContinuousAbsolute.TcPOU)

```iecst
// 场景：激光切割机 — 直线段以高速 1000 mm/s 切到 100 mm，过点不停继续 200 mm/s 进入圆弧段
PROGRAM P_Demo_MC_MoveContinuousAbsolute
VAR
    fbStraightCut    : MC_MoveContinuousAbsolute;
    fbHaltSafety     : MC_Halt;
    axisLaserHead    : AXIS_REF;
    rtCutTrig        : R_TRIG;
    rtSafetyHalt     : R_TRIG;
    bStartStraight   : BOOL;
    bEmergencyStop   : BOOL;
    bInArc           : BOOL;
    bSafetyHaltDone  : BOOL;
    nErrorID         : UDINT;
END_VAR

rtCutTrig(CLK := bStartStraight);
rtSafetyHalt(CLK := bEmergencyStop);

fbStraightCut(
    Execute       := rtCutTrig.Q,
    Position      := 100.0,
    Velocity      := 1000.0,
    EndVelocity   := 200.0,
    Acceleration  := 5000.0,
    Deceleration  := 5000.0,
    Jerk          := 50000.0,
    BufferMode    := MC_Buffered,
    Axis          := axisLaserHead,
    InEndVelocity => bInArc,
    ErrorID       => nErrorID
);

// 兜底停车：紧急停止信号触发把轴减速到 0
fbHaltSafety(
    Execute      := rtSafetyHalt.Q,
    Deceleration := 10000.0,
    Jerk         := 100000.0,
    Axis         := axisLaserHead,
    Done         => bSafetyHaltDone
);
```

## 7. 业务场景与实际价值

- **场景**：激光/水刀切割轨迹过点不停、雕刻机段间过渡、印刷机色版定位段间衔接。共同点：**点 A 到点 B 的过渡不能停顿**，要保持工艺速度。
- **价值**：业务无需自己算"在终点前多少 mm 开始减速"，FB 直接接受目标位 + 终末速度两个工艺量，加减速曲线由 NC 自动算。
- **替代方案对比**：
  - 用 `MC_MoveAbsolute` 然后再 `MC_MoveVelocity`：两段之间必然停顿（前者 `Done` 出现时速度已是 0）
  - 用 `MC_MoveContinuousRelative`：基于相对距离，本 FB 基于绝对位置
  - **本 FB**：连续轨迹工艺的首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.1.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70103947.html
- **相关 FB**：`MC_MoveContinuousRelative`、`MC_MoveAbsolute`、`MC_Halt`
