# MC_PhasingAbsolute

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Phasing` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/2217664779.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_PhasingAbsolute.TcPOU`](../examples/P_Demo_MC_PhasingAbsolute.TcPOU) |

---


## 1. 功能简述

PLCopen 标准定义的**绝对相位调整 FB**。在已耦合的主从两轴之间设定一个绝对相位差（`PhaseShift`）—— FB 自动在从轴上执行一段叠加运动，让"从轴位置 − 主轴位置 × 齿比"等于设定的 `PhaseShift`。

完成后输出 `AbsolutePhaseShift` 反馈系统实际设定的相位差。`ContinuousUpdate := TRUE` 时允许在命令执行期间改 `PhaseShift` 等参数并尽快生效。

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
| `ContinuousUpdate` | `BOOL` | — | 上升沿时若为 `TRUE`：命令执行期间改 `PhaseShift` / `Velocity` / `Acceleration` / `Deceleration` / `Jerk` 会尽快生效 |
| `PhaseShift` | `LREAL` | — | 主从轴间要设定的相位差 |
| `Velocity` | `LREAL` | — | 相位调整叠加运动可达最大速度，`≥0.01` |
| `Acceleration` | `LREAL` | — | 最大加速度 |
| `Deceleration` | `LREAL` | — | 最大减速度 |
| `Jerk` | `LREAL` | — | 最大 Jerk（同时作用于加速段和减速段） |
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
| `Slave` | `AXIS_REF` | 从轴引用；将通过叠加运动达到目标相位 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done               : BOOL;
    Busy               : BOOL;
    Active             : BOOL;
    CommandAborted     : BOOL;
    Error              : BOOL;
    ErrorId            : UDINT;
    AbsolutePhaseShift : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 绝对相位差已设定到位时置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后立即变 `TRUE`，结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE` |
| `Active` | `BOOL` | 表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE` |
| `CommandAborted` | `BOOL` | 命令未完成就被中止（被另一 Move 抢占 / `MC_Stop` 停掉）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorId` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |
| `AbsolutePhaseShift` | `LREAL` | 系统实际设定的绝对相位差（可能因夹紧与请求略异） |

## 3. 行为说明

**触发**：`Execute` 上升沿启动相位调整；从轴上执行一段叠加运动让 `(Slave − Master × Ratio) = PhaseShift`。

**`ContinuousUpdate` 用法**：上升沿采样此输入：
- `TRUE` 时本命令"动态可改参数"，业务侧改 `PhaseShift` 等输入 FB 会尽快重新规划
- `FALSE` 时命令进队列后参数锁定，改也无效

**`Velocity ≥ 0.01` 约束**：必须 ≥ 0.01；过小会报错。

**Jerk-limited**：相位调整始终按 Jerk-limited 曲线执行；`Jerk` 同时是加速段和减速段的限制。

**兼容性**：可与 `MC_GearIn` 简单耦合配合，也可与 `MC_GearInMultiMaster(Options.AdvancedSlaveDynamics = TRUE)` 或 `MC_CamIn_V2` 的动态耦合配合。**不支持 `MC_GearInDyn`**。

**与 `MC_PhasingRelative` 区别**：本 FB 设定**绝对相位差**（"无论现在差多少，要差 5°"）；`MC_PhasingRelative` 设定**相对增量**（"再加 5° 相位"）。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **耦合必须已建立**：本 FB 不建立耦合，只调整已有耦合的相位差。先调 `MC_GearIn` / `MC_CamIn_V2` 再调本 FB。
- **不支持 `MC_GearInDyn`**：PDF 明确；若用 GearInDyn 的耦合要做相位调整请用 `MC_GearInMultiMaster(AdvancedSlaveDynamics=TRUE)` 替代。
- **`Velocity < 0.01` 报错**：极小值要小心。
- **`BufferMode` 只能 Aborting**。
- **`Options` 未实现**。
- **改相位时主轴动着 vs 静着**：主轴动时设定相位差是动态目标（"差始终保持 5°"）；主轴静止时设定的相位差是一次性 offset。
- **`Jerk` 同时作用加减速段**：标准 PLCopen FB 加减速段 Jerk 可不同，本 FB 强制一致。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_PhasingAbsolute.TcPOU`](../examples/P_Demo_MC_PhasingAbsolute.TcPOU)

```iecst
// 场景：印刷机色版相对主辊设置 5° 绝对相位差用于套色对齐
PROGRAM P_Demo_MC_PhasingAbsolute
VAR
    fbSetPhase        : MC_PhasingAbsolute;
    axisMainRoller    : AXIS_REF;
    axisColorPlate    : AXIS_REF;
    rtSetTrig         : R_TRIG;
    bApplyPhase       : BOOL;
    lrTargetPhaseDeg  : LREAL := 5.0;
    bPhaseDone        : BOOL;
    lrActualPhase     : LREAL;
    nErrorID          : UDINT;
END_VAR

rtSetTrig(CLK := bApplyPhase);
fbSetPhase(
    Execute            := rtSetTrig.Q,
    ContinuousUpdate   := TRUE,
    PhaseShift         := lrTargetPhaseDeg,
    Velocity           := 10.0,
    Acceleration       := 100.0,
    Deceleration       := 100.0,
    Jerk               := 1000.0,
    BufferMode         := MC_Aborting,
    Master             := axisMainRoller,
    Slave              := axisColorPlate,
    Done               => bPhaseDone,
    AbsolutePhaseShift => lrActualPhase,
    ErrorId            => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：多色印刷机色版套准（每色版相对主版固定相位）、罐装机灌注嘴对齐瓶口、分切机刀位与料速对齐。共同点：**主从同步基础上叠加一个固定相位差**。
- **价值**：相位差作为参数直接给定，FB 自动规划 Jerk-limited 调整曲线；业务无需算"叠加多远才能换算成 5° 相位差"。
- **替代方案对比**：
  - 用 `MC_MoveSuperImposed`：要业务算 Distance = PhaseShift × Ratio
  - 自己加 PID 闭环算相位差：不可控速度过渡
  - **本 FB**：绝对相位调整的首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.6.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/2217664779.html
- **相关 FB**：`MC_PhasingRelative`、`MC_HaltPhasing`、`MC_MoveSuperImposed`
