# MC_MoveAbsolute

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Point to point motion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70094731.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_MoveAbsolute.xml`](../examples/P_Demo_MC_MoveAbsolute.xml) |

---

## 1. 功能简述

PLCopen Motion Control Part 1 标准定义的**绝对定位运动功能块（Function Block, FB）**。Beckhoff 在 TwinCAT 3 NC PTP 之上提供这层 IEC 61131-3 兼容封装，让运动控制代码可在不同支持 PLCopen 的运动平台间移植。

`Execute` 上升沿触发，沿整段轨迹监视轴的运动，把轴驱动到 `Position` 指定的**绝对目标位置**。到达后 `Done` 置 `TRUE`；中途被另一条运动命令抢占则 `CommandAborted := TRUE`；硬件/参数错误则 `Error := TRUE` 并通过 `ErrorID` 输出 NC 错误码。

该 FB 主要用于直线轴。对模数轴（Modulo）而言 `Position` 被解释为**无限绝对坐标系下的绝对位置**，不会按 360° 折回；如需模数定位请用 `MC_MoveModulo`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Position     : LREAL;
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
| `Position` | `LREAL` | — | 绝对目标位置，单位由轴参数中"用户单位"决定（mm / ° / pulse 等） |
| `Velocity` | `LREAL` | — | 最大行进速度，要求 `>0`；轴在加减速段两端会按 `Acceleration` / `Deceleration` 限速 |
| `Acceleration` | `LREAL` | — | 加速度，要求 `≥0`；填 `0` 表示采用轴参数中默认加速度 |
| `Deceleration` | `LREAL` | — | 减速度，要求 `≥0`；填 `0` 表示采用轴参数中默认减速度 |
| `Jerk` | `LREAL` | — | 加加速度（Jerk），要求 `≥0`；填 `0` 表示采用轴参数中默认 Jerk |
| `BufferMode` | `MC_BufferMode` | — | 队列模式：当轴正在执行另一命令时本命令的接入方式（Aborting / Buffered / BlendingLow / BlendingPrevious / BlendingNext / BlendingHigh）；耦合从轴只允许 `Aborting` |
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
| `Done` | `BOOL` | 目标位置到达时置 `TRUE`（具体判据见 §3） |
| `Busy` | `BOOL` | `Execute` 上升沿后立即变 `TRUE`，运动结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE` |
| `Active` | `BOOL` | 表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE` |
| `CommandAborted` | `BOOL` | 命令未完成就被中止（被另一 Move 抢占 / 轴被 `MC_Stop` 停掉）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（参见 §4） |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次绝对定位；命令一旦进入 NC 队列即不可改参数 —— 想改新目标必须再触发一次（且 `BufferMode` 决定是覆盖还是排队）。`Execute` 撤销不会停轴，要停用 `MC_Stop` 或 `MC_Halt`。

**状态机**：FB 输出按 PLCopen 标准的三分支收敛：

- **正常完成**：轴到位 → `Active = FALSE`、`Busy = FALSE`、`Done = TRUE`、`CommandAborted = FALSE`、`Error = FALSE`
- **被抢占**：另一 Move/Stop 命令切入 → `Active = FALSE`、`Busy = FALSE`、`CommandAborted = TRUE`、`Done = FALSE`
- **出错**：参数越界 / 轴未使能 / 软限位 / 跟随误差超限等 → `Busy = FALSE`、`Error = TRUE`、`ErrorID` 给码

**Done 的具体判据**（取决于轴参数中"位置监视"配置）：

1. 启用了"Target Position Monitoring"（标配）：NC 设定值生成完毕（`HasJob = FALSE`）**之后**`InPositionArea = TRUE` → `Done := TRUE`
2. 启用了"Position Range Monitoring"（未开 Target Position Monitoring 时）：同样需要 NC 设定值生成完毕且 `InPositionArea = TRUE`
3. 两种监视都未启用：NC 设定值一生成完即立刻 `Done := TRUE`，**不等实际位置到位**

**BufferMode 语义**：单实例 FB 用 `Aborting` 即可；要做"位置 A → 位置 B 连续过渡"必须用**第二个**实例并设 `Buffered` 或 `BlendingXxx`，同一 FB 实例在 `Busy` 期间改参数无效。

**耦合从轴特例**：若轴当前是某主轴的从轴且轴参数允许"Allow motion commands"，本命令会先**自动解耦**再执行定位；这种情况下只能用 `Aborting`，且从轴动力学被限制在最大动力学之内。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。

## 5. 使用注意 / 常见坑

- **`Execute` 是边沿触发不是电平触发**。常见错误是把 `Execute := TRUE` 一直拉高期望"持续保持目标位置"——实际只第一次触发有效，之后改 `Position` 不会自动跟随。需要"参数跟随更新"应改用支持 `ContinuousUpdate` 的 FB（本 FB 不支持）。
- **`Velocity` 必须 `> 0`**。填 `0` 不会让轴"原地待命"而是直接报错。停轴用 `MC_Halt` / `MC_Stop`。
- **`Acceleration = 0` 不是"无加速"** 而是"用轴参数默认值"。要"瞬时跳到目标速度"在物理上做不到，NC 也不允许。
- **同一 FB 实例不能在多任务共享**。`AXIS_REF` 在循环数据接口里有内部状态，并发调用会出竞态。一个轴用一个 FB 实例，跨任务用 `MC_Power` 之外的命令需小心同步。
- **`BufferMode` 选错导致命令堆栈错乱**：单实例只能 `Aborting`，串接两个 Move 必须用**两个不同实例**才能 `Buffered`，否则后一次触发把前一次抢掉，看到的现象是"Done 没出来，CommandAborted 反而出来了"。
- **位置监视未启用时 Done 来得早**：如果两种 Position Monitoring 都关掉了，`Done` 在 NC 设定值轨迹生成完时就置 TRUE，**实际伺服可能还在追位置**。把"Done 出现"当成"机械已到位"会出现夹紧机构在轴还在动时闭合的事故。（工程经验补充）
- **模数轴慎用**：对模数轴 `Position = 720°` 不会"再转两圈"，会被解释为绝对的 720°；要转两圈用 `MC_MoveModulo` 配 `Direction := MC_Positive_Direction`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_MoveAbsolute.xml`](../examples/P_Demo_MC_MoveAbsolute.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 场景：贴片机 Y 轴把吸嘴从料带取料位 (0 mm) 移动到 PCB 上某个绝对贴装坐标
//       (150.250 mm)。完成后释放 vacuum，下一周期再回取料位。
PROGRAM P_Demo_MC_MoveAbsolute
VAR
    fbMoveToPlace         : MC_MoveAbsolute;
    axisYHead             : AXIS_REF;                  // PLCopen VAR_IN_OUT，必须传
    rtMoveTrigger         : R_TRIG;                    // 边沿触发器
    bStartPlaceMove       : BOOL := FALSE;             // 在线置 TRUE 触发一次
    lrPlacementPositionMM : LREAL := 150.25;           // PCB 上的贴装绝对位
    lrTraverseVelocity    : LREAL := 500.0;            // 500 mm/s
    bMoveDone             : BOOL;
    bMoveBusy             : BOOL;
    bMoveAborted          : BOOL;
    bMoveError            : BOOL;
    nMoveErrorID          : UDINT;
END_VAR

// 单次完整调用：所有 VAR_INPUT 显式赋值，Axis 用 := 不是 :=>
rtMoveTrigger(CLK := bStartPlaceMove);
fbMoveToPlace(
    Execute      := rtMoveTrigger.Q,
    Position     := lrPlacementPositionMM,
    Velocity     := lrTraverseVelocity,
    Acceleration := 5000.0,
    Deceleration := 5000.0,
    Jerk         := 50000.0,
    BufferMode   := MC_Aborting,
    Axis         := axisYHead,
    Done         => bMoveDone,
    Busy         => bMoveBusy,
    CommandAborted => bMoveAborted,
    Error        => bMoveError,
    ErrorID      => nMoveErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：所有需要"把轴开到一个确定坐标"的工业自动化场合：贴片机贴装头、CNC 刀具换刀位、机器人单关节关节定位、卷料定长收放、电池模组 PACK 线托盘定位。要点是"目标坐标在工件坐标系下已知"，不是"再走多少距离"。
- **价值**：业务代码不需要自己写 NC 通道命令（`MC_Direct` 写 NC 控制字 `nCommand = 1` / 拼 `fPosition` / 等 `fError = 0`）这一套底层时序，单次 FB 调用即把"发命令 + 监视轨迹 + 上报状态"全部封装好。配合 PLCopen 标准状态机，可直接套用 IEC 61131-3 教科书上的"Done/Busy/Error"三态判断写控制逻辑。
- **替代方案对比**：
  - 直接写 NC 通道命令：需对 NCTOPLC/PLCTONC 接口 30+ 字段熟悉，且每次升级 Beckhoff NC 接口都有适配风险
  - 用 `MC_MoveRelative`（相对定位）：要求业务自己累加位置；连续多次相对定位累计误差会漂移
  - 用 `MC_MoveAdditive`：基于"上一次目标"叠加，定位结果取决于上一条命令完成情况，与"绝对到某坐标"语义不同
  - **本 FB**：直接给绝对坐标，最直觉、误差不累积、符合 PLCopen 标准

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70094731.html
- **PLCopen Spec**：Function blocks for motion control Part 1 — Single axis（MC_MoveAbsolute 章节）
- **相关 FB**：`MC_MoveRelative`（相对距离）、`MC_MoveAdditive`（叠加上一目标）、`MC_MoveModulo`（模数轴专用）、`MC_Stop` / `MC_Halt`（停轴）、`MC_Reset`（清错）、`MC_Power`（轴使能）
