# MC_MoveContinuousRelative

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Point to point motion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70105483.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_MoveContinuousRelative.TcPOU`](../examples/P_Demo_MC_MoveContinuousRelative.TcPOU) |

---


## 1. 功能简述

PLCopen 标准定义的**带终末速度的相对定位 FB**。从当前 NC 设定位置起按 `Distance` 走一段相对距离，到达终点时**不停车**，而是保持 `EndVelocity` 继续走。`InEndVelocity := TRUE` 标志到达目标位置且已达终末速度。

与 `MC_MoveContinuousAbsolute` 的区别：本 FB 给"再走多远"，绝对版给"到哪个坐标"。**不支持高/低速专用轴**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Distance     : LREAL;
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
| `Distance` | `LREAL` | — | 相对行进距离（可负） |
| `Velocity` | `LREAL` | — | 行程中最大速度 |
| `EndVelocity` | `LREAL` | — | 到达终点时维持的终末速度 |
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
| `InEndVelocity` | `BOOL` | 到达终点且速度=`EndVelocity` 时置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后立即变 `TRUE`，结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE` |
| `Active` | `BOOL` | 表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE` |
| `CommandAborted` | `BOOL` | 命令未完成就被中止（被另一 Move 抢占 / `MC_Stop` 停掉）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |

## 3. 行为说明

**触发**：`Execute` 上升沿；起点 = NC 当前设定位置，终点 = 起点 + `Distance`，到达时速度 = `EndVelocity`。

**FB 终止行为**：`InEndVelocity = TRUE` 后 FB 任务结束，**轴继续以 `EndVelocity` 行进**；业务必须后续接管。

**典型工艺**：用于连续路径中每段以相对距离描述的场景。例如打标机沿 X 方向先打 50 mm 长的横线（结束保持 100 mm/s）→ 再发一段 `MC_MoveContinuousRelative(Distance := 50, EndVelocity := 0)` 让它平滑收尾。两段之间用 `BufferMode := MC_Buffered` 串接实现无停顿过渡。

**与 `MC_MoveRelative` 区别**：后者到位即"完成 Done"且默认希望停车；本 FB 到位时速度恰好等于 `EndVelocity`，**不一定为 0**。

**不支持高/低速专用轴**。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **`EndVelocity > Velocity` 报错**：终末速度物理上不能超过行程速度。
- **`EndVelocity > 0` 后轴不停**：业务必须有后续命令。常见 bug 是单独用本 FB 试图走一段相对距离然后期待轴自己停 —— 实际不会，需要再发 `MC_Halt`。
- **被打断后相对距离起点变**：与 `MC_MoveRelative` 一样，被 `MC_Stop` 干预后再触发本 FB 起点是被打断时的设定位。
- **不支持高/低速专用轴**：硬件类型不符报错。
- **被 `MC_MoveContinuousAbsolute` 抢占后位置漂移**：相对运动与绝对运动混用时务必清楚每条命令的"基准点"。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_MoveContinuousRelative.TcPOU`](../examples/P_Demo_MC_MoveContinuousRelative.TcPOU)

```iecst
// 场景：贴标机标头沿 X 走 200 mm 完成一张标签贴附，过点不停 100 mm/s 进入下一段
PROGRAM P_Demo_MC_MoveContinuousRelative
VAR
    fbLabelStroke   : MC_MoveContinuousRelative;
    fbStopAtEnd     : MC_Halt;
    axisLabelHead   : AXIS_REF;
    rtStrokeTrig    : R_TRIG;
    rtStopTrig      : R_TRIG;
    bStartStroke    : BOOL;
    bFinishCycle    : BOOL;
    lrLabelLengthMM : LREAL := 200.0;
    lrTransitVelo   : LREAL := 100.0;
    bAtEnd          : BOOL;
    bStopDone       : BOOL;
    nErrorID        : UDINT;
END_VAR

rtStrokeTrig(CLK := bStartStroke);
rtStopTrig(CLK := bFinishCycle);

fbLabelStroke(
    Execute       := rtStrokeTrig.Q,
    Distance      := lrLabelLengthMM,
    Velocity      := 800.0,
    EndVelocity   := lrTransitVelo,
    Acceleration  := 4000.0,
    Deceleration  := 4000.0,
    Jerk          := 40000.0,
    BufferMode    := MC_Buffered,
    Axis          := axisLabelHead,
    InEndVelocity => bAtEnd,
    ErrorID       => nErrorID
);

fbStopAtEnd(
    Execute      := rtStopTrig.Q,
    Deceleration := 4000.0,
    Jerk         := 40000.0,
    Axis         := axisLabelHead,
    Done         => bStopDone
);
```

## 7. 业务场景与实际价值

- **场景**：贴标段连续过渡、印刷机版滚定长走一格 + 维持线速度衔接下一格、激光打标的横划/竖划段间无停顿衔接。
- **价值**：相对距离 + 终末速度组合直接描述工艺，PLC 不用算减速点位置。
- **替代方案对比**：
  - 用 `MC_MoveRelative` 然后再 `MC_MoveVelocity`：两段之间必停
  - 用 `MC_MoveContinuousAbsolute`：要业务自己算绝对终点位置
  - **本 FB**：相对距离描述的连续轨迹工艺首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.1.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70105483.html
- **相关 FB**：`MC_MoveContinuousAbsolute`、`MC_MoveRelative`、`MC_Halt`
