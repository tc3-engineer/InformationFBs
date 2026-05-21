# MC_Halt

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Point to point motion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70107019.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_Halt.xml`](../examples/P_Demo_MC_Halt.xml) |

---


## 1. 功能简述

PLCopen 标准定义的**软停车 FB**。按指定减速度斜坡把轴停下来，但**不锁轴**——停下来后业务可立即用其它命令再让轴动起来。

与 `MC_Stop` 的关键区别：`MC_Stop` 停轴 + 上锁，必须 `MC_Reset` 才能解锁；`MC_Halt` 停轴 + 不锁，是"正常工艺停"的首选。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Deceleration : LREAL;
    Jerk         : LREAL;
    BufferMode   : MC_BufferMode;
    Options      : ST_MoveOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次定位命令；命令进入运动队列后即开始执行，不需保持高电平 |
| `Deceleration` | `LREAL` | — | 减速度；`≤ 0` 时采用轴参数默认减速度 |
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
| `Done` | `BOOL` | 轴已减速到 0 时置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后立即变 `TRUE`，结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE` |
| `Active` | `BOOL` | 表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE` |
| `CommandAborted` | `BOOL` | 减速中被其它运动命令抢占时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |

## 3. 行为说明

**触发**：`Execute` 上升沿启动减速；轴按指定减速度斜坡降速到 0，`Done` 置 `TRUE`。

**与 `MC_Stop` 关键区别**：
- `MC_Halt`：停后**不锁轴**，业务可立刻发新 Move 命令让轴再动
- `MC_Stop`：停后**锁轴**，必须 `MC_Reset` 才能解锁；适合"出事了不许再动"的紧急停车

**减速段被抢占**：减速过程中若另一条 Move 命令切入（`MC_Aborting`），本 FB 输出 `CommandAborted := TRUE`，轴跟着新命令走。这是"工艺允许中途反悔"的体现。

**`Deceleration ≤ 0` 的行为**：采用轴参数中默认减速度（不是"瞬时停"也不是"无减速"）。

**耦合从轴特例**：从轴上发 `MC_Halt` 会先自动解耦再减速；只能 `MC_Aborting`。

**典型用法**：正常工艺循环结束 / 节拍间停顿 / 操作员按"暂停"按钮 — 这些场景全用 `MC_Halt`。**只有紧急停车 / 检测到故障要锁轴才用 `MC_Stop`**。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **正常停轴用 `MC_Halt` 不是 `MC_Stop`**：搞错了导致每次正常循环结束都要 Reset 才能开新循环，很别扭。
- **`Done` 短暂置位**：`Done := TRUE` 只维持一个周期左右（直到 `Execute` 撤销或新命令进来）；不能当成"轴静止"长期判定，要持续判断停止应读 `Axis.NcToPlc.ActVelo`。
- **`Execute` 撤销不影响停车**：本 FB 一旦启动减速，撤 `Execute` 不会让轴重新加速，但减速继续完成。
- **减速度太小会出问题**：极小的减速度 + 极高初速度可能导致超软限位，NC 会报错。建议留 20% 安全余量。
- **耦合从轴上调用会解耦**：常被忽略。要"让从轴跟主轴一起停"应停主轴（`MC_Halt(MasterAxis)`）而不是发 `MC_Halt(SlaveAxis)`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_Halt.xml`](../examples/P_Demo_MC_Halt.xml)

```iecst
// 场景：传送带在工艺结束时正常停车，停后允许下一节拍再启动
PROGRAM P_Demo_MC_Halt
VAR
    fbCycleHalt       : MC_Halt;
    axisProcess       : AXIS_REF;
    rtCycleEnd        : R_TRIG;
    bEndOfCycle       : BOOL;
    bHaltDone         : BOOL;
    bHaltBusy         : BOOL;
    bAborted          : BOOL;
    nErrorID          : UDINT;
END_VAR

rtCycleEnd(CLK := bEndOfCycle);
fbCycleHalt(
    Execute      := rtCycleEnd.Q,
    Deceleration := 2000.0,
    Jerk         := 20000.0,
    BufferMode   := MC_Aborting,
    Axis         := axisProcess,
    Done         => bHaltDone,
    Busy         => bHaltBusy,
    CommandAborted => bAborted,
    ErrorID      => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：所有"工艺停"——节拍循环之间、操作员暂停、上料完成停轴等位、品种切换前归位停车。共同特征：**停下来还要再开起来**。
- **价值**：减速曲线 + Done 上报由 FB 处理；业务代码不用写"先发 0 速度命令再等 ActVelo 归零"那套手撸逻辑。停后不锁轴的设计避免了每次都要 Reset 的麻烦。
- **替代方案对比**：
  - `MC_Stop`：会锁轴，正常工艺停用了体验差
  - 发 `MC_MoveVelocity(Velocity := 0)`：报错（Velocity 必须 >0）
  - 直接清 `MC_Power.Enable`：会触发"非受控停车"（drive coast 或 quick stop），不是 PLCopen 标准停车
  - **本 FB**：PLCopen 标准 + 不锁轴，正常工艺停首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.1.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70107019.html
- **相关 FB**：`MC_Stop`（紧急/故障锁停）、`MC_MoveVelocity`（启动恒速）、`MC_Reset`（解锁）
