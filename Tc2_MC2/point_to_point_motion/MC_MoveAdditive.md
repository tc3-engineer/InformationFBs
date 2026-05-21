# MC_MoveAdditive

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Point to point motion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70097803.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_MoveAdditive.xml`](../examples/P_Demo_MC_MoveAdditive.xml) |

---


## 1. 功能简述

PLCopen 标准定义的**叠加相对定位 FB**。起点是**上一条运动命令的目标位置**（不是当前设定位置），与 `MC_MoveRelative` 形成对比。若没有"上一目标位置"可参考（如刚上电）或轴正在连续运动，则退化为以当前设定位置为起点。

典型用途：连续动作中插入"目标位再补偿一段"的修正运动——比如视觉系统给出一个"再走 2.3 mm 才精准对准"的偏移。**不支持高/低速专用轴（high/low speed axes）**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Distance     : LREAL;
    Velocity     : LREAL;
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
| `Distance` | `LREAL` | — | 相对叠加距离；终点 = 上一命令的目标位置 + `Distance` |
| `Velocity` | `LREAL` | — | 最大行进速度，要求 `>0`；轴在加减速段两端按 `Acceleration` / `Deceleration` 限速 |
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
| `Done` | `BOOL` | 目标到达 / 命令完成时置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后立即变 `TRUE`，结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE` |
| `Active` | `BOOL` | 表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE` |
| `CommandAborted` | `BOOL` | 命令未完成就被中止（被另一 Move 抢占 / `MC_Stop` 停掉）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |

## 3. 行为说明

**触发**：`Execute` 上升沿；起点取"上一条 Move 命令的目标位置"。例如先 `MC_MoveAbsolute(Position := 100)` 命令发出后立刻接 `MC_MoveAdditive(Distance := 5)`，**不管第一条命令是否到达 100**，第二条的目标会被锁定为 105。这是与 `MC_MoveRelative` 最关键的区别。

**没有上一目标位置时**（首次运动 / 上次是 Velocity move / 上次被 Reset）：退化为以"当前 NC 设定位置"为起点，与 `MC_MoveRelative` 行为一致。

**状态机**：PLCopen 标准三分支 Done / CommandAborted / Error，与 `MC_MoveAbsolute` 一致。

**关键差异**：
- `MC_MoveRelative` 起点 = 当前 SetPos（即时快照）
- `MC_MoveAdditive` 起点 = 上次命令的目标位置（逻辑量）
- 若上一命令半途被打断，`MC_MoveAdditive` 仍以"原本要去的位置"为锚

**典型用法**：高速贴片机里"先粗定位 → 视觉相机识别 → 微调"。粗定位用 `MC_MoveAbsolute(Position := 100)` 发出后**马上**用 `MC_MoveAdditive(Distance := visionOffsetMM)` 排队（BufferMode = Buffered），轴执行完粗定位**自动**接着走视觉偏移，省一次"等 Done 再触发"的时序。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **概念易混淆**：`MC_MoveRelative` vs `MC_MoveAdditive` 在轴静止时**行为相同**，所以测试覆盖不全很容易在生产中出现"轴在动时叠加，结果跑过头"的事故。
- **不支持高/低速专用轴**：硬件类型为 High/Low Speed Axis 时本 FB 报错，需改用 `MC_MoveRelative`。
- **首次调用退化为 Relative**：开机后第一次调用本 FB 与 `MC_MoveRelative` 等价；不要据此就把两个 FB 混用。
- **`BufferMode = Buffered` 是常态**：本 FB 的设计意图就是"叠加在前一条之后"，单实例用 `Aborting` 反而抢掉前一条达不到叠加效果。
- **被打断后再触发起点未变**：第一次绝对到 100，途中 `MC_Stop` 停在 30，下一次 `MC_Additive(Distance := 5)` **目标仍然是 105**（因为"上一命令目标"是 100，不是停下来的 30）。
- **`MC_Reset` 会清空"上一目标位置"记忆**：Reset 后首次 `MC_MoveAdditive` 退化为 Relative 行为。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_MoveAdditive.xml`](../examples/P_Demo_MC_MoveAdditive.xml)

```iecst
// 场景：贴片机粗定位到 PCB 坐标 (100 mm) 后用视觉补偿叠加 2.3 mm
PROGRAM P_Demo_MC_MoveAdditive
VAR
    fbVisionAdjust       : MC_MoveAdditive;
    axisHeadX            : AXIS_REF;
    rtAdjustTrigger      : R_TRIG;
    bApplyVisionOffset   : BOOL;
    lrVisionCorrectionMM : LREAL := 2.3;
    bAdjustDone          : BOOL;
    bAdjustError         : BOOL;
    nErrorID             : UDINT;
END_VAR

rtAdjustTrigger(CLK := bApplyVisionOffset);
fbVisionAdjust(
    Execute      := rtAdjustTrigger.Q,
    Distance     := lrVisionCorrectionMM,
    Velocity     := 50.0,
    Acceleration := 500.0,
    Deceleration := 500.0,
    Jerk         := 5000.0,
    BufferMode   := MC_Buffered,
    Axis         := axisHeadX,
    Done         => bAdjustDone,
    Error        => bAdjustError,
    ErrorID      => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：视觉补偿、激光测距修正、张力调整后追加位移、套色印刷"主版定位 + 各色版微调"。共同特征：**前一命令的目标作为基准**，再叠加一个不确定时才知道的小修正量。
- **价值**：把"粗定位 + 微调"两段拼成无缝连续运动，避免在两段之间停下来重新加速；同时业务代码无需自己缓存"上一目标位置"。
- **替代方案对比**：
  - 业务自己缓存 lastTargetPos 然后用 `MC_MoveAbsolute(Position := lastTargetPos + correction)`：可行但要小心 `MC_Reset` 后清缓存
  - 用 `MC_MoveRelative`：起点是 SetPos 而非 lastTarget，被打断时行为不一致
  - **本 FB**：语义直接对齐"叠加修正"业务，BufferMode = Buffered 时与前一命令拼接最自然

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70097803.html
- **相关 FB**：`MC_MoveAbsolute`、`MC_MoveRelative`、`MC_MoveModulo`
