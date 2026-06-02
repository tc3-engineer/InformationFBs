# MC_PhasingRelative

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Phasing` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/2250456587.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_PhasingRelative.TcPOU`](../examples/P_Demo_MC_PhasingRelative.TcPOU) |

---


## 1. 功能简述

PLCopen 标准定义的**相对相位调整 FB**。在已耦合的主从两轴之间**叠加**一个相位增量（`PhaseShift`）—— FB 在从轴上执行一段叠加运动让主从相位差**再增加 `PhaseShift`**。

与 `MC_PhasingAbsolute` 的区别：本 FB 是"再加多少"，绝对版是"设到多少"。输出 `CoveredPhaseShift` 反馈系统实际叠加的相位增量。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute            : BOOL;
    ContinuousUpdate   : BOOL;
    PhaseShift         : LREAL;
    Velocity           : LREAL;
    Acceleration       : LREAL;
    Deceleration       : LREAL;
    Jerk               : LREAL;
    BufferMode         : MC_BufferMode;
    Options            : ST_PhasingOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次定位命令；命令进入运动队列后即开始执行，不需保持高电平 |
| `ContinuousUpdate` | `BOOL` | — | 上升沿时若为 `TRUE`：命令执行期间改参数会尽快生效 |
| `PhaseShift` | `LREAL` | — | 要**再叠加**的相位增量（可正可负） |
| `Velocity` | `LREAL` | — | 相位调整叠加运动可达最大速度 |
| `Acceleration` | `LREAL` | — | 最大加速度 |
| `Deceleration` | `LREAL` | — | 最大减速度 |
| `Jerk` | `LREAL` | — | 最大 Jerk（同时作用加减速段） |
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
| `Master` | `AXIS_REF` | 主轴引用 |
| `Slave` | `AXIS_REF` | 从轴引用 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done              : BOOL;
    Busy              : BOOL;
    Active            : BOOL;
    CommandAborted    : BOOL;
    Error             : BOOL;
    ErrorId           : UDINT;
    CoveredPhaseShift : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 相位增量已叠加完成时置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后立即变 `TRUE`，结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE` |
| `Active` | `BOOL` | 表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE` |
| `CommandAborted` | `BOOL` | 命令未完成就被中止（被另一 Move 抢占 / `MC_Stop` 停掉）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorId` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |
| `CoveredPhaseShift` | `LREAL` | 系统实际叠加的相位增量（可能因夹紧与请求略异） |

## 3. 行为说明

**触发**：`Execute` 上升沿启动相位增量叠加；当前相位差再加上 `PhaseShift`。例如当前差 5°，本 FB `PhaseShift := 3` 启动 → 完成后差 8°。

**与绝对版区别**：本 FB 叠加增量，绝对版设置目标。相对版适合"每次套准检测算出微小偏差后再调一点"。

**`ContinuousUpdate` 行为**：与绝对版一致——上升沿采样，TRUE 时参数动态可改。

**多次叠加**：每次相对调整都在前一次结果上累加；要"回到初始相位"需反向 `PhaseShift := -coverage_so_far`。

**`MC_GearInDyn` 不支持**：与绝对版一致。

**`CoveredPhaseShift` 反馈**：系统实际叠加的量；正常等于 `PhaseShift`，但如有夹紧 / 错误中止会与请求值不一致。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **每次叠加都累积**：多次调用本 FB 相位差不断累加；要还原必须反向调用。
- **耦合必须已建立**：本 FB 不建立耦合。
- **不支持 `MC_GearInDyn`**：同绝对版。
- **`BufferMode` 仅 Aborting**：填别的报错。
- **`Velocity ≥ 0.01`**：太小报错。
- **`Jerk` 同时作用加减速段**：与绝对版一致。
- **被 `MC_HaltPhasing` 中止后 `CoveredPhaseShift` 反映已走的部分**：例如要叠 10°，走到 6° 被 Halt → `CoveredPhaseShift ≈ 6`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_PhasingRelative.TcPOU`](../examples/P_Demo_MC_PhasingRelative.TcPOU)

```iecst
// 场景：套准检测每次反馈一个小偏差（如 +0.2°）→ 用相对相位调整连续修正
PROGRAM P_Demo_MC_PhasingRelative
VAR
    fbAddPhase        : MC_PhasingRelative;
    axisMainRoller    : AXIS_REF;
    axisColorPlate    : AXIS_REF;
    rtCorrectTrig     : R_TRIG;
    bRunCorrection    : BOOL;
    lrPhaseErrorDeg   : LREAL := 0.2;
    bCorrectionDone   : BOOL;
    lrCoveredPhase    : LREAL;
    nErrorID          : UDINT;
END_VAR

rtCorrectTrig(CLK := bRunCorrection);
fbAddPhase(
    Execute           := rtCorrectTrig.Q,
    ContinuousUpdate  := FALSE,
    PhaseShift        := lrPhaseErrorDeg,
    Velocity          := 5.0,
    Acceleration      := 50.0,
    Deceleration      := 50.0,
    Jerk              := 500.0,
    BufferMode        := MC_Aborting,
    Master            := axisMainRoller,
    Slave             := axisColorPlate,
    Done              => bCorrectionDone,
    CoveredPhaseShift => lrCoveredPhase,
    ErrorId           => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：套准闭环逐步修正（每个反馈周期叠加一小段偏差）、张力调整后的相位微调、跟随过程中加入小相位补偿。共同特征：**每次调一小段，多次累积**。
- **价值**：业务侧不用维护"当前总相位"，FB 自动叠加；适合做相位的闭环 PID 输出。
- **替代方案对比**：
  - 用 `MC_PhasingAbsolute(PhaseShift := currentTotal + correction)`：要业务侧维护 currentTotal，容易丢失
  - 用 `MC_MoveSuperImposed` 算距离：要业务把"相位差 (°) 换算成距离 (mm)"
  - **本 FB**：相对相位累加的首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.6.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/2250456587.html
- **相关 FB**：`MC_PhasingAbsolute`、`MC_HaltPhasing`、`MC_MoveSuperImposed`
