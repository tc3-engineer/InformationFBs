# MC_MoveSuperImposed

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Superposition` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70111499.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_MoveSuperImposed.xml`](../examples/P_Demo_MC_MoveSuperImposed.xml) |

---


## 1. 功能简述

PLCopen 标准定义的**叠加运动 FB**。在轴正在运行的主运动之上**叠加**一段相对运动（不打断主运动），叠加段完成后 `Done := TRUE`，主运动继续由其原本的 Move FB 监视。

典型用途：两轴同步运行时让其中一根**临时领先 / 落后**一段距离（如套准印刷的色版微调）；或飞剪过程中追加一段位移。本 FB 既可作用于单轴，也可作用于主轴或从轴。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute         : BOOL;
    Mode            : E_SuperpositionMode;
    Distance        : LREAL;
    VelocityDiff    : LREAL;
    Acceleration    : LREAL;
    Deceleration    : LREAL;
    Jerk            : LREAL;
    VelocityProcess : LREAL;
    Length          : LREAL;
    Options         : ST_SuperpositionOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次定位命令；命令进入运动队列后即开始执行，不需保持高电平 |
| `Mode` | `E_SuperpositionMode` | — | 叠加运动类型（见 `E_SuperpositionMode` 枚举） |
| `Distance` | `LREAL` | — | 要"追赶"的相对距离；正值 = 提速追赶，负值 = 制动后退 |
| `VelocityDiff` | `LREAL` | — | 相对当前主速度的最大速度差，`>0`；正向叠加时上限 = 最大速度 - 主速度，负向叠加时上限 = 主速度 |
| `Acceleration` | `LREAL` | — | 加速度 ≥0；填 0 取轴默认 |
| `Deceleration` | `LREAL` | — | 减速度 ≥0；填 0 取轴默认 |
| `Jerk` | `LREAL` | — | **未实现**，传任意值都不生效 |
| `VelocityProcess` | `LREAL` | — | 叠加期间的平均主速度 `>0`；用于动态规划叠加曲线 |
| `Length` | `LREAL` | — | 叠加可用的路径长度（按主轴位移计），用于在固定段内完成 |
| `Options` | `ST_SuperpositionOptions` | — | 可选项：例如主运动停止时叠加是否中止还是继续 |

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
    Done               : BOOL;
    Busy               : BOOL;
    Active             : BOOL;
    CommandAborted     : BOOL;
    Error              : BOOL;
    ErrorID            : UDINT;
    Warning            : BOOL;
    WarningID          : UDINT;
    ActualVelocityDiff : LREAL;
    ActualDistance     : LREAL;
    ActualLength       : LREAL;
    ActualAcceleration : LREAL;
    ActualDeceleration : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 叠加运动完成时置 `TRUE`；主运动可能仍在进行 |
| `Busy` | `BOOL` | `Execute` 上升沿后立即变 `TRUE`，结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE` |
| `Active` | `BOOL` | 表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE` |
| `CommandAborted` | `BOOL` | 命令未完成就被中止（被另一 Move 抢占 / `MC_Stop` 停掉）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |
| `Warning` | `BOOL` | 出现非致命警告（如参数被自动夹紧到上限） |
| `WarningID` | `UDINT` | 警告码 |
| `ActualVelocityDiff` | `LREAL` | 系统实际采用的速度差（可能因夹紧与请求值不一致） |
| `ActualDistance` | `LREAL` | 系统实际采用的距离 |
| `ActualLength` | `LREAL` | 系统实际采用的长度 |
| `ActualAcceleration` | `LREAL` | 系统实际采用的加速度 |
| `ActualDeceleration` | `LREAL` | 系统实际采用的减速度 |

## 3. 行为说明

**触发**：`Execute` 上升沿启动叠加。主运动**不被打断**——它由原来的 Move FB 继续监视；本 FB 只负责"在主运动之上加一段位移"。

**几何意义**：两轴同速并行，对其一发 `MC_MoveSuperImposed(Distance := +D)` 会让该轴**比对方多走 D**，叠加结束后两轴位置差 = D 永久保留。

**作用于主从耦合的特殊性**：
- 作用于从轴：叠加只发生在从轴
- 作用于主轴：从轴**会跟随**主轴的叠加运动（因为耦合关系仍在）

**与主运动的速度联动**：叠加运动的速度与主运动当前速度挂钩——主运动加速 / 减速时叠加运动也跟着变；主运动停了，叠加运动**会停或继续**取决于 `Options` 配置。

**`Length` 的意义**：要求"在主轴走过这么远之内完成叠加"。若给定 `Length` 不足以容纳 `Distance` × `VelocityDiff` 的叠加曲线，系统自动夹紧或报警。

**实际值 vs 请求值**：如果 `VelocityDiff` 超过物理上限会被夹紧，从 `ActualVelocityDiff` 等可读到系统采纳的实际值。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **主运动不能停**：主运动停叠加也跟着失效（默认 Options）；要"主停叠加仍执行"需 `Options.AbortOnMainStop := FALSE`。
- **`Jerk` 不生效**：填了也没用；运动平顺度由 NC 内部决定。
- **`VelocityDiff` 上限取决于叠加方向**：正方向加叠加时受最大速度限制，负方向受当前速度限制；超出会被夹紧并报警。
- **作用于主轴会传到从轴**：耦合下从轴会跟着跳变，工艺上往往不期望这样；要"只让主轴叠加，从轴不跟"需先解耦或用别的方案。
- **`Length` 太小报警**：若叠加距离按 `VelocityDiff` 算需要更长路径，系统会输出 `Warning` 并使用实际可达的距离 / 速度。
- **叠加完成只代表本 FB 任务结束**：主运动还在跑；判断"整体到位"要看主运动的 Move FB 的 `Done`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_MoveSuperImposed.xml`](../examples/P_Demo_MC_MoveSuperImposed.xml)

```iecst
// 场景：印刷机色版主轴恒速跑（外部已发 MC_MoveVelocity），现在需要让色版临时领先 2 mm 完成套色补偿
PROGRAM P_Demo_MC_MoveSuperImposed
VAR
    fbColorRegistration : MC_MoveSuperImposed;
    axisPrintRoller     : AXIS_REF;
    rtApplyShift        : R_TRIG;
    bApplyColorShift    : BOOL;
    lrShiftMM           : LREAL := 2.0;
    bShiftDone          : BOOL;
    bShiftWarn          : BOOL;
    lrActualShift       : LREAL;
    nErrorID            : UDINT;
END_VAR

rtApplyShift(CLK := bApplyColorShift);
fbColorRegistration(
    Execute         := rtApplyShift.Q,
    Mode            := SUPERPOSITIONMODE_VELOREDUCTIONCONTINUOUS,
    Distance        := lrShiftMM,
    VelocityDiff    := 20.0,
    Acceleration    := 200.0,
    Deceleration    := 200.0,
    Jerk            := 2000.0,
    VelocityProcess := 100.0,
    Length          := 500.0,
    Axis            := axisPrintRoller,
    Done            => bShiftDone,
    Warning         => bShiftWarn,
    ActualDistance  => lrActualShift,
    ErrorID         => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：套色印刷的色版微调、双轴同步生产线的相位补偿、卷绕收放的张力修正引入的小位移、飞剪在剪切瞬间叠加位移以"对准刀口"。
- **价值**：业务无需停掉主运动重新发新命令；叠加在主运动之上完成，工艺连贯性最好。系统自动管理"主速度变化时叠加速度也跟着变"。
- **替代方案对比**：
  - 用 `MC_MoveAdditive(BufferMode := Buffered)`：要等当前命令结束才能叠加，无法在主运动持续期间临时插
  - 自己算出新目标位置发 `MC_MoveAbsolute(Aborting)`：会打断主运动，工艺不连续
  - **本 FB**：叠加运动的标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70111499.html
- **相关 FB**：`MC_AbortSuperposition`（提前中止叠加）、`MC_PhasingAbsolute`（主从相位调整，叠加的特化）
