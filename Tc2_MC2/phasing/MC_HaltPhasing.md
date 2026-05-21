# MC_HaltPhasing

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Phasing` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/2217662859.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_HaltPhasing.xml`](../examples/P_Demo_MC_HaltPhasing.xml) |

---


## 1. 功能简述

PLCopen 标准定义的**相位调整中止 FB**。把 `MC_PhasingAbsolute` 或 `MC_PhasingRelative` 启动的"从轴相对主轴相位调整运动"按指定减速度可控停下来。停车曲线始终 Jerk-limited（按 `Jerk` 输入指定的恒定 Jerk）。

只用于停止相位调整运动，**不停止从轴的耦合跟随**——从轴解耦时机由后续命令决定。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Deceleration : LREAL;
    Jerk         : LREAL;
    BufferMode   : MC_BufferMode;
    Options      : ST_PhasingOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次定位命令；命令进入运动队列后即开始执行，不需保持高电平 |
| `Deceleration` | `LREAL` | — | 最大减速度 |
| `Jerk` | `LREAL` | — | 最大 Jerk |
| `BufferMode` | `MC_BufferMode` | — | **仅支持 `MC_Aborting`** |
| `Options` | `ST_PhasingOptions` | — | **未实现** |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Master : AXIS_REF;
    Slave  : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Master` | `AXIS_REF` | 主轴 AXIS_REF |
| `Slave` | `AXIS_REF` | 从轴 AXIS_REF；正在调整相位的那根 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done           :    BOOL;
    Busy           :    BOOL;
    Active         :    BOOL;
    CommandAborted :    BOOL;
    Error          :    BOOL;
    ErrorId        :    UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 相位调整运动已减速到 0 时置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后立即变 `TRUE`，结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE` |
| `Active` | `BOOL` | 表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE` |
| `CommandAborted` | `BOOL` | 命令未完成就被中止（被另一 Move 抢占 / `MC_Stop` 停掉）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorId` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |

## 3. 行为说明

**触发**：`Execute` 上升沿启动减速；相位调整的"叠加速度"按 `Deceleration` + `Jerk` 平滑降为 0，此后从轴继续跟主轴但不再有相位调整位移。

**与 `MC_AbortSuperposition` 关系**：相位调整本质是一种特殊的叠加运动，但 `MC_HaltPhasing` 提供**可控减速曲线**，而 `MC_AbortSuperposition` 是瞬时中止。要平滑停"相位调整"用本 FB；要立刻中止用 `MC_AbortSuperposition`。

**`BufferMode` 仅支持 `Aborting`**：相位停车是抢占式动作，不能排队。

**已建立的相位差保留**：与 `MC_AbortSuperposition` 一样，已经走过的相位差**永久保留**，本 FB 只是停止后续相位调整。

**从轴耦合状态不变**：本 FB 只针对相位调整运动；从轴的 GearIn / CamIn 耦合关系不被本 FB 解开。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **只停相位调整，不停从轴**：从轴在耦合下继续跟主轴跑；要停从轴需后续接 `MC_GearOut` + `MC_Halt`。
- **`BufferMode` 只能 `Aborting`**：填别的报错。
- **已建立的相位差保留**：要把相位还原需反向再调一次 `MC_PhasingRelative(PhaseShift := -shift)`。
- **`Options` 未实现**：填了没用。
- **没有相位调整运行时调用 `Error := TRUE`**：先确认相位 FB 在 Busy 状态再触发本 FB。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_HaltPhasing.xml`](../examples/P_Demo_MC_HaltPhasing.xml)

```iecst
// 场景：套色印刷相位调整发现参数错了，平滑停止相位调整不要让色版突然抖一下
PROGRAM P_Demo_MC_HaltPhasing
VAR
    fbStopPhasing    : MC_HaltPhasing;
    axisMaster       : AXIS_REF;
    axisColorPlate   : AXIS_REF;
    rtStopTrig       : R_TRIG;
    bRequestStop     : BOOL;
    bStopDone        : BOOL;
    bStopBusy        : BOOL;
    nErrorID         : UDINT;
END_VAR

rtStopTrig(CLK := bRequestStop);
fbStopPhasing(
    Execute      := rtStopTrig.Q,
    Deceleration := 1000.0,
    Jerk         := 10000.0,
    BufferMode   := MC_Aborting,
    Master       := axisMaster,
    Slave        := axisColorPlate,
    Done         => bStopDone,
    Busy         => bStopBusy,
    ErrorId      => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：相位调整运动启动后业务发现参数错了 / 套准检测信号变了，需要平滑停止相位调整以避免色版突然抖动印出废品。
- **价值**：相对于 `MC_AbortSuperposition` 的瞬时中止，本 FB 给出 Jerk-limited 减速曲线，工艺平顺；从轴耦合关系保留，工艺继续推进。
- **替代方案对比**：
  - `MC_AbortSuperposition`：瞬时中止，可能引入冲击
  - `MC_Stop(Slave)`：停从轴 + 锁，工艺中断
  - **本 FB**：相位调整的可控停车

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.6.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/2217662859.html
- **相关 FB**：`MC_PhasingAbsolute`、`MC_PhasingRelative`、`MC_AbortSuperposition`
