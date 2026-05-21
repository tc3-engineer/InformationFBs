# MC_Stop

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Point to point motion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70108555.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_Stop.xml`](../examples/P_Demo_MC_Stop.xml) |

---


## 1. 功能简述

PLCopen 标准定义的**硬停车 + 锁轴 FB**。按指定减速度把轴停下来，**同时把轴锁定**——锁定期间任何运动命令都被拒绝，必须调 `MC_Reset` 才能解锁。

用于"出事了，不许再动"的故障/紧急停车场景；正常工艺停用 `MC_Halt`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Deceleration : LREAL;
    Jerk         : LREAL;
    Options      : ST_MoveOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 命令在 `Execute` 高电平期间持续生效：上升沿启动停车，**直到 `Execute = FALSE` 后等待几个周期 NC 才解除"停车命令保持"，但锁状态仍在直到 `MC_Reset`** |
| `Deceleration` | `LREAL` | — | 减速度；`≤ 0` 时采用轴参数默认减速度 |
| `Jerk` | `LREAL` | — | 加加速度（Jerk），要求 `≥0`；填 `0` 表示采用轴参数中默认 Jerk |
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
| `Done` | `BOOL` | 轴已减速到 0 时置 `TRUE`（锁定状态仍在） |
| `Busy` | `BOOL` | `Execute` 上升沿后立即 `TRUE`，**`Execute` 撤销后还会维持几个周期**（NC 释放命令所需）才变 `FALSE` |
| `Active` | `BOOL` | 表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE` |
| `CommandAborted` | `BOOL` | 命令未完成就被中止（被另一 Move 抢占 / `MC_Stop` 停掉）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |

## 3. 行为说明

**触发**：`Execute` 上升沿启动减速 + 上锁。减速到 0 后 `Done := TRUE`，但**轴仍被锁**。

**解锁流程**（PDF 明文要求）：
1. 减速完成（看到 `Done = TRUE`）
2. 撤销 `Execute`（`Execute := FALSE`）
3. **继续调用本 FB 几个周期**直到 `Busy = FALSE`（NC 释放命令）
4. 调用 `MC_Reset(Axis)` 解锁

**锁定语义**：锁定期间发任何 Move 命令都会出错（`Error = TRUE`、`ErrorID` 给"轴被锁"码）。这正是与 `MC_Halt` 的本质差异。

**何时用 `MC_Stop` 而非 `MC_Halt`**：
- 故障检测到异常需要锁住设备避免操作员误启动
- 紧急停止信号（注意：硬件 E-Stop 走 Safety PLC，本 FB 只用于软件触发的"业务紧急停")
- 上位机要求"停下来等指令"

**耦合从轴特例**：从轴发 `MC_Stop` 自动解耦再停 + 锁。

**`MC_Stop` 没有 `BufferMode`**：因为它是抢占式，永远以 Aborting 语义切入，不能被排队。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **正常停轴别用 `MC_Stop`**：会导致每次都要 `MC_Reset`，多余操作步骤拖慢节拍。
- **`Execute` 撤销后还要继续调用**：常见错误是 `MC_Stop` 触发后立刻把 `Execute := FALSE` 且不再 cyclic 调用，导致 NC 状态卡住下一次重启失败。**FB 必须周期调用直到 `Busy = FALSE`**。
- **`Done` 出现不代表解锁**：解锁要 `MC_Reset`。把 `Done = TRUE` 当解锁信号会出现下一条命令报错。
- **耦合从轴上发会解耦**：要让"耦合系统一起停 + 锁"应作用于主轴，从轴会自动跟。
- **MC_Stop 没有 BufferMode**：因为它本质是 Aborting；用户不能让它"排队"。
- **硬件 E-Stop 必须走 Safety PLC**：本 FB 不能替代功能安全停车；功能安全要 Safety over EtherCAT。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_Stop.xml`](../examples/P_Demo_MC_Stop.xml)

```iecst
// 场景：检测到工件卡死，立刻停轴并锁住等操作员手动 Reset 后才能再开
PROGRAM P_Demo_MC_Stop
VAR
    fbEmergencyStop    : MC_Stop;
    fbResetAxis        : MC_Reset;
    axisLoader         : AXIS_REF;
    rtFaultDetected    : R_TRIG;
    rtOperatorReset    : R_TRIG;
    bFaultDetected     : BOOL;
    bOperatorAck       : BOOL;
    bStopDone          : BOOL;
    bStopBusy          : BOOL;
    bResetDone         : BOOL;
    nStopErrorID       : UDINT;
    nResetErrorID      : UDINT;
END_VAR

rtFaultDetected(CLK := bFaultDetected);
rtOperatorReset(CLK := bOperatorAck);

// MC_Stop 的 Execute 是电平触发；只要 bStopBusy 还在就持续触发
fbEmergencyStop(
    Execute      := bFaultDetected,
    Deceleration := 10000.0,
    Jerk         := 100000.0,
    Axis         := axisLoader,
    Done         => bStopDone,
    Busy         => bStopBusy,
    ErrorID      => nStopErrorID
);

// 操作员按 Reset 后调 MC_Reset 解锁
fbResetAxis(
    Execute  := rtOperatorReset.Q,
    Axis     := axisLoader,
    Done     => bResetDone,
    ErrorID  => nResetErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：上料卡死、刀具断裂、工件超温、跟踪误差超限、力矩超限 — 所有"出事了，不许再动"的业务紧急停。
- **价值**：停车 + 上锁一体完成；避免操作员或上位机在故障未确认时误重启设备。
- **替代方案对比**：
  - `MC_Halt` + 业务代码自己加锁标志：能做但要自己维护"锁状态"全局变量，并在每条 Move 前判断
  - 清 `MC_Power.Enable`：触发非受控停车（drive coast），机械冲击大
  - 硬件 E-Stop：是功能安全场景，与本 FB 互补不互换
  - **本 FB**：业务级紧急停 + 锁的标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.1.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70108555.html
- **相关 FB**：`MC_Halt`（不锁的正常停）、`MC_Reset`（解锁）、`MC_Power`（轴使能）
