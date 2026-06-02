# MC_MoveRelative

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Point to point motion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70096267.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_MoveRelative.TcPOU`](../examples/P_Demo_MC_MoveRelative.TcPOU) |

---


## 1. 功能简述

PLCopen 标准定义的**相对定位运动 FB**。从轴**当前设定位置**起，按 `Distance` 走一段相对距离（有正负号），整段轨迹由 NC 监视。到达后 `Done := TRUE`；中途被抢占 `CommandAborted := TRUE`；出错 `Error := TRUE` 并通过 `ErrorID` 给 NC 错误号。

与 `MC_MoveAbsolute` 的区别：本 FB 给的是"再走多远"，不是"到哪个坐标"；和 `MC_MoveAdditive` 区别：本 FB 起点是"当前设定位置"，`MC_MoveAdditive` 起点是"上次命令的目标位置"。

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
| `Distance` | `LREAL` | — | 相对行进距离，可正可负；起点是 NC 当前设定位置 |
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

**触发**：`Execute` 上升沿启动一次相对定位；起点取"当前 NC 设定位置（SetPos）"，终点 = SetPos + `Distance`。`Execute` 撤销不停轴，要停用 `MC_Stop` / `MC_Halt`。

**状态机**（PLCopen 标准三分支）：

- **正常完成**：轴到位 → `Done = TRUE`、`Busy = Active = CommandAborted = Error = FALSE`
- **被抢占**：另一 Move/Stop 切入 → `CommandAborted = TRUE`、`Done = FALSE`
- **出错**：参数越界/轴未使能/软限位/跟随误差等 → `Error = TRUE`、`ErrorID` 给码

`Done` 的具体判据与 `MC_MoveAbsolute` 一致——取决于轴参数"目标位置监视"配置（启用时等 `InPositionArea = TRUE` 才置位；不启用时设定值生成完即刻置位）。

**累计漂移风险**：连续多次"相对走 100 mm"看似简单，但每次起点是"上次 NC 设定位置"。若中途出现 `CommandAborted` 让轴没走完，下次相对运动的起点是被中断时的设定位（不是原目标位），累计就会偏。需要"绝对一致"的场景应改用 `MC_MoveAbsolute`。

**耦合从轴特例**：与 `MC_MoveAbsolute` 一致，会先自动解耦再执行，且只能用 `MC_Aborting`。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **`Execute` 是边沿触发**：连续两次"走 50 mm"必须 `Execute` 之间至少有一个周期回 FALSE，否则只触发一次。
- **`Distance` 可负**：负数表示反向。但伺服未做反向间隙补偿时反复正反相对运动会积累实际偏差。
- **多次相对运动累计误差**：见 §3。要"走 10 步每步 10 mm 共 100 mm"建议用 `MC_MoveAbsolute(Position := 100)` 而非循环 10 次 `MC_MoveRelative(Distance := 10)`。
- **被打断后再触发起点变了**：第一次相对 100 mm，走 30 mm 时 `MC_Stop` 干预，再触发相对 100 mm 时**起点是 30 mm 处**而非原 0 mm 起点。
- **耦合状态下只能 `Aborting`**：从轴接到 `MC_MoveRelative` 会先解耦，要再耦合需重新调用 `MC_GearIn` / `MC_CamIn`。
- **`Velocity = 0` 报错**：用 `MC_Halt` / `MC_Stop` 停轴，别用 `Velocity := 0` 触发本 FB。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_MoveRelative.TcPOU`](../examples/P_Demo_MC_MoveRelative.TcPOU)

```iecst
// 场景：步进送料机每个生产节拍把材料相对推进 50 mm；上位 PLC 触发一次 = 一格送料
PROGRAM P_Demo_MC_MoveRelative
VAR
    fbStepFeed         : MC_MoveRelative;
    axisFeeder         : AXIS_REF;
    rtStepTrigger      : R_TRIG;
    bIndexStep         : BOOL;
    lrStepLengthMM     : LREAL := 50.0;
    bStepDone          : BOOL;
    bStepBusy          : BOOL;
    nErrorID           : UDINT;
END_VAR

rtStepTrigger(CLK := bIndexStep);
fbStepFeed(
    Execute      := rtStepTrigger.Q,
    Distance     := lrStepLengthMM,
    Velocity     := 300.0,
    Acceleration := 3000.0,
    Deceleration := 3000.0,
    Jerk         := 30000.0,
    BufferMode   := MC_Aborting,
    Axis         := axisFeeder,
    Done         => bStepDone,
    Busy         => bStepBusy,
    ErrorID      => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：步进送料、卷绕收放周期性长度、机器人 JOG 模式按定长寸动、印刷套色每色版按定长换色。共同特征是"每次触发 = 再前进固定距离"。
- **价值**：业务代码无需自己计算"上次到了哪，这次目标 = 上次 + 距离"，FB 自动以 NC 当前设定位置为起点。误差不在 FB 而在累计的多次调用，业务可选用 `MC_MoveAbsolute` 兜底校准。
- **替代方案对比**：
  - 用 `MC_MoveAbsolute(Position := lastSetPos + Distance)`：要业务自己维护 lastSetPos，容易出错
  - 用 `MC_MoveAdditive`：基于"上次目标位置"而非"当前设定位置"，被打断时行为不同
  - **本 FB**：起点定义清晰（NC SetPos），最贴合"再走多远"语义

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70096267.html
- **相关 FB**：`MC_MoveAbsolute`、`MC_MoveAdditive`、`MC_MoveModulo`、`MC_Stop`、`MC_Halt`
