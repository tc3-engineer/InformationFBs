# MC_Stop

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_DriveMotionControl` |
| Library Version | `1.5.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `Point to point motion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8280956299.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_Stop.TcPOU`](../examples/P_Demo_MC_Stop.TcPOU) |

---

## 1. 功能简述

PLCopen Motion Control 标准定义的**硬停车 + 锁轴功能块（Function Block, FB）**。按给定减速度把轴沿减速斜坡停下，**同时把轴锁定**，阻止其它运动命令。因此适合在特殊情形下停车——这些情形要防止轴再发生任何运动。

轴在停下后只有把 `Execute` 置 `FALSE` 才能重新启动；`Execute` 下降沿后还需几个周期来释放轴，这段时间 `Busy` 保持 `TRUE`，必须持续调用本 FB 直到 `Busy` 变 `FALSE`。轴的锁定由 `MC_Reset` 解除。正常运动停车更宜用不锁的 `MC_Halt`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Deceleration : LREAL;
    Options      : ST_MoveOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发命令。停车期间轴被锁定；轴停下后只有把 `Execute` 置 `FALSE` 才能重新启动 |
| `Deceleration` | `LREAL` | — | 减速度。值为 `0` 时采用上一条 Move 命令的减速度。出于安全，`MC_Stop` / `MC_Halt` 不能用比当前激活运动更弱的动力学执行——必要时参数化会被自动调整 |
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
| `Done` | `BOOL` | 轴已停下且静止时置 `TRUE`（注意：此时轴仍被锁定） |
| `Busy` | `BOOL` | `Execute` 启动后置 `TRUE` 并持续到命令处理结束；`Busy = FALSE` 时 FB 可接受新命令。**只要轴仍被锁，`Busy` 保持 `TRUE`；只有 `Execute` 置 `FALSE` 后轴才解锁、`Busy` 才变 `FALSE`** |
| `Active` | `BOOL` | 表示本 FB 控制着轴。只要轴仍被锁就保持 `TRUE`；只有 `Execute` 置 `FALSE` 后轴解锁、`Active` 才变 `FALSE` |
| `CommandAborted` | `BOOL` | 命令未能完整执行时置 `TRUE` |
| `Error` | `BOOL` | 发生错误时为 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出错误号（参见 §4） |

## 3. 行为说明

**触发与锁定语义**：`Execute` **上升沿**启动减速 + 上锁。这是库通用规则里的**特例**——一般 FB 的 `Busy` / `Done` 互斥，但 `MC_Stop` 在轴停下后 `Done` 置 `TRUE` 的同时 `Busy` / `Active` **仍保持 `TRUE`**（因为轴被锁着）。这三个输出只有在 `Execute` 置 `FALSE` 后才复位。

**完整解锁流程**（PDF 明文要求，必须按序执行）：
1. 触发停车（`Execute` 上升沿），轴减速到静止，`Done = TRUE`（此时轴仍锁、`Busy` 仍 `TRUE`）
2. 把 `Execute` 置 `FALSE`
3. `Execute` 下降沿后还需**几个周期**释放轴，期间 `Busy` 保持 `TRUE`——**必须持续调用本 FB** 直到 `Busy` 变 `FALSE`
4. 调用 `MC_Reset(Axis)` 解除锁定

**锁定的作用**：锁定期间轴拒绝其它运动命令。这正是与 `MC_Halt` 的本质差异——`MC_Halt` 停后不锁、可立即重启；`MC_Stop` 停后锁住、必须经上述流程 + `MC_Reset` 才能再动。用于"出事了，不许再动"的故障 / 安全停车，防止误启动。

**减速度安全约束**：`Deceleration = 0` 时用上一条 Move 的减速度；且停车减速度不允许比当前运动更弱，必要时自动调整。

**常见误用**：停车触发后立刻把 `Execute := FALSE` 且不再周期调用，会导致 NC 状态卡住、下次重启失败。FB 必须持续调用直到 `Busy = FALSE`。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC/驱动错误号（不是 HRESULT）。

| 返回值 / 错误码 | 含义 | 处理建议 |
|---|---|---|
| `Done = TRUE` | 轴已停下且静止（仍锁定） | 按解锁流程：撤 `Execute` → 等 `Busy = FALSE` → `MC_Reset` |
| `Error = TRUE` + `ErrorID ≠ 0` | 停车出错 | 检查轴状态；必要时 `MC_Reset` |

锁定期间对轴发其它运动命令会令那条命令出错（轴被锁）。PDF 与 InfoSys 在本 FB 章节均未逐条列出具体 `ErrorID` 码值，具体码值需对照 TwinCAT NC 错误码总表（⚠️ PDF + InfoSys 本章节未枚举）。

## 5. 使用注意 / 常见坑

- **`Done` 出现不代表解锁**：减速到 0 后 `Done = TRUE`，但轴仍锁，`Busy` / `Active` 仍 `TRUE`。解锁要走"撤 `Execute` → 等 `Busy = FALSE` → `MC_Reset`"。
- **`Execute` 撤销后还要继续调用**：下降沿后需几个周期释放轴，期间必须持续调用本 FB 直到 `Busy = FALSE`。立刻停调会卡住 NC 状态、下次重启失败。
- **正常停车别用 `MC_Stop`**：会导致每次都要 `MC_Reset`，多余步骤拖慢节拍。常规停车用 `MC_Halt`。
- **`Deceleration = 0` 用上一条 Move 的减速度**：且不能比当前运动更弱（自动调整）。
- **硬件 E-Stop 必须走 Safety PLC**：本 FB 是软件触发的"业务紧急停"，不能替代功能安全停车（STO / Safety over EtherCAT）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_Stop.TcPOU`](../examples/P_Demo_MC_Stop.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：检测到工件卡死，立刻停轴并锁住，等操作员排障后 MC_Reset 才能再开
PROGRAM P_Demo_MC_Stop
VAR
    fbStop          : MC_Stop;
    fbResetAxis     : MC_Reset;
    axisLoader      : AXIS_REF;
    rtOperatorReset : R_TRIG;              // 复位按钮转上升沿
    bFaultDetected  : BOOL := FALSE;       // 在线写 TRUE 模拟检测到卡死(电平保持)
    bOperatorAck    : BOOL := FALSE;       // 在线写 TRUE 模拟操作员按复位
    bStopDone       : BOOL;
    bStopBusy       : BOOL;
    bStopAborted    : BOOL;
    bStopError      : BOOL;
    nStopErrorID    : UDINT;
    bResetDone      : BOOL;
    nResetErrorID   : UDINT;
END_VAR

// MC_Stop：Execute 高电平期间锁轴；故障期间持续给 Execute，停稳后撤销才解锁
// Axis 是 VAR_IN_OUT 用 :=；FB 必须周期调用直到 Busy=FALSE
fbStop(
    Execute        := bFaultDetected,
    Deceleration   := 5000.0,
    Axis           := axisLoader,
    Done           => bStopDone,
    Busy           => bStopBusy,
    CommandAborted => bStopAborted,
    Error          => bStopError,
    ErrorID        => nStopErrorID
);

// 操作员撤销故障(bFaultDetected:=FALSE)、等 bStopBusy=FALSE 后按复位解锁
rtOperatorReset(CLK := bOperatorAck);
fbResetAxis(
    Execute := rtOperatorReset.Q,
    Axis    := axisLoader,
    Done    => bResetDone,
    ErrorID => nResetErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：上料卡死、刀具断裂、工件超温、跟随误差超限等"出事了，不许再动"的业务紧急停。停车后锁住设备，防止操作员或上位机在故障未确认时误重启。
- **价值**：停车 + 上锁一体完成；业务代码不必自己维护"锁状态"全局变量并在每条 Move 前判断，本 FB 直接拒绝锁定期间的运动命令。
- **替代方案对比**：
  - `MC_Halt` + 自己加锁标志：能做，但要自己维护锁状态并在每条 Move 前判断
  - 落 `MC_Power.Enable`：非受控停车（自由滑行），机械冲击大，且不等于"锁"
  - 硬件 E-Stop：功能安全场景，与本 FB 互补不互换
  - **本 FB**：业务级紧急停 + 锁的标准做法，配 `MC_Reset` 解锁

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf) §6.3.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8280956299.html
- **相关 FB**：`MC_Halt`（不锁的正常停车）、`MC_Reset`（解锁）、`MC_Power`（使能）
