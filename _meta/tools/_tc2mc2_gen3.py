#!/usr/bin/env python3
"""Generator for Tc2_MC2 — batch 3 (remaining 12):

  superposition:    MC_MoveSuperImposed, MC_AbortSuperposition
  homing:           MC_Home
  manual_motion:    MC_Jog
  axis_coupling:    MC_GearIn, MC_GearInDyn, MC_GearOut, MC_GearInMultiMaster
  phasing:          MC_HaltPhasing, MC_PhasingAbsolute, MC_PhasingRelative
  torque_control:   MC_TorqueControl
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _tc2mc2_gen import (
    emit, metablock, xml_skel, vbool, vlreal, vudint, vuint, vderived,
    PDF_URL, ERRORID_SECTION,
    DESC_EXECUTE, DESC_VELOCITY, DESC_ACC, DESC_DEC, DESC_JERK,
    DESC_BUFFER, DESC_OPTIONS, DESC_AXIS,
    DESC_DONE, DESC_BUSY, DESC_ACTIVE, DESC_ABORTED, DESC_ERROR, DESC_ERRORID,
)


# ---------------------------------------------------------------------------
# 6.2.1 MC_MoveSuperImposed
# ---------------------------------------------------------------------------

def gen_move_superimposed():
    name = "MC_MoveSuperImposed"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70111499.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Superposition", info, name)}

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
| `Execute` | `BOOL` | — | {DESC_EXECUTE} |
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
| `Axis` | `AXIS_REF` | {DESC_AXIS} |

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
| `Busy` | `BOOL` | {DESC_BUSY} |
| `Active` | `BOOL` | {DESC_ACTIVE} |
| `CommandAborted` | `BOOL` | {DESC_ABORTED} |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorID` | `UDINT` | {DESC_ERRORID} |
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

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **主运动不能停**：主运动停叠加也跟着失效（默认 Options）；要"主停叠加仍执行"需 `Options.AbortOnMainStop := FALSE`。
- **`Jerk` 不生效**：填了也没用；运动平顺度由 NC 内部决定。
- **`VelocityDiff` 上限取决于叠加方向**：正方向加叠加时受最大速度限制，负方向受当前速度限制；超出会被夹紧并报警。
- **作用于主轴会传到从轴**：耦合下从轴会跟着跳变，工艺上往往不期望这样；要"只让主轴叠加，从轴不跟"需先解耦或用别的方案。
- **`Length` 太小报警**：若叠加距离按 `VelocityDiff` 算需要更长路径，系统会输出 `Warning` 并使用实际可达的距离 / 速度。
- **叠加完成只代表本 FB 任务结束**：主运动还在跑；判断"整体到位"要看主运动的 Move FB 的 `Done`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

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

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.2.1
- **InfoSys topic**：{info}
- **相关 FB**：`MC_AbortSuperposition`（提前中止叠加）、`MC_PhasingAbsolute`（主从相位调整，叠加的特化）
"""
    body = "\n".join([
        vderived("fbColorRegistration", "MC_MoveSuperImposed"),
        vderived("axisPrintRoller", "AXIS_REF"),
        vderived("rtApplyShift", "R_TRIG"),
        vbool("bApplyColorShift", "FALSE"),
        vlreal("lrShiftMM", "2.0"),
        vbool("bShiftDone"),
        vbool("bShiftWarn"),
        vlreal("lrActualShift"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：印刷机色版主轴正在恒速跑（前序 MC_MoveVelocity 发起，demo 中假设已启动），
//       套色检测发现本色版需领先主色版 2 mm 才能对齐，调用本 FB 在主运动之上
//       叠加 2 mm 相对位移 — 主运动不停，叠加完成后两轴位置差保留。
// 价值：业务不用停掉主运动重新发新命令；叠加期间主速度变化 FB 自动适应。
// 验证：先用 MC_MoveVelocity 让 axisPrintRoller 跑起来（demo 假设）；
//       bApplyColorShift := TRUE → 看 ActPos 在 ~ 0.1 s 内额外多走 2 mm；
//       bShiftDone 短暂置 TRUE；lrActualShift 应等于 2.0。
// =============================================================================

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
    Done            =&gt; bShiftDone,
    Warning         =&gt; bShiftWarn,
    ActualDistance  =&gt; lrActualShift,
    ErrorID         =&gt; nErrorID
);
"""
    emit("superposition", name, doc, xml_skel(name, body, st))


# ---------------------------------------------------------------------------
# 6.2.3 MC_AbortSuperposition (minimal VAR set)
# ---------------------------------------------------------------------------

def gen_abort_superposition():
    name = "MC_AbortSuperposition"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70114571.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Superposition", info, name)}

## 1. 功能简述

PLCopen 标准定义的**叠加运动中止 FB**。提前结束由 `MC_MoveSuperImposed` 启动的叠加运动，**但不停止主运动**。叠加运动被中止后，已叠加的部分保留（位置差保留），剩余未完成的叠加被抛弃。

如果需要"主运动 + 叠加运动全停"应直接用 `MC_Stop` / `MC_Halt`，无需先调 `MC_AbortSuperposition`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发：立刻终止当前叠加运动，主运动继续 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | {DESC_AXIS} |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done    : BOOL;
    Busy    : BOOL;
    Error   : BOOL;
    ErrorID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 叠加运动已成功中止时置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后立即 `TRUE`，FB 完成后 `FALSE` |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorID` | `UDINT` | {DESC_ERRORID} |

## 3. 行为说明

**触发**：`Execute` 上升沿。立刻终止该轴上正在执行的 `MC_MoveSuperImposed` 叠加运动；主运动 FB 继续监视主运动，不受影响。

**已叠加位移保留**：例如叠加运动准备走 10 mm，已走完 6 mm 时被本 FB 中止，**6 mm 的位置差被保留**，未走的 4 mm 不再补。

**没有 `CommandAborted`、`Active` 等输出**：因为本 FB 自身是个"中止动作"，瞬时完成，没有"可被打断"的概念。

**典型用法**：业务在叠加运动启动后发现条件变了（例如套准检测发现叠加方向算错了），想立即终止叠加但不影响生产线主运动。

**已无叠加运动时调用**：若轴上当前并无叠加运动，本 FB 报错 `Error := TRUE`、`ErrorID` 给"无叠加可中止"码。

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **`MC_AbortSuperposition` 只中止叠加，不停主轴**：要全停应用 `MC_Stop` / `MC_Halt`。
- **没有叠加运行时调用会报错**：先确认 `MC_MoveSuperImposed` 实例的 `Busy = TRUE` 再触发本 FB。
- **不能"撤销"已叠加的位移**：本 FB 只是停止后续未完成的叠加段，已经叠加进去的位置差**永久保留**。要把"叠加的位置差减回去"得反向再发一次 `MC_MoveSuperImposed`。
- **不要把它当"叠加运动的 Reset"**：与 `MC_Reset` 无关，本 FB 不清错。
- **耦合从轴上的叠加**：从轴叠加被中止后从轴回到"按耦合公式跟主轴走"的状态。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

```iecst
// 场景：套色检测系统在叠加运动启动后发现方向算错，立刻终止叠加避免错色印更多
PROGRAM P_Demo_MC_AbortSuperposition
VAR
    fbAbortShift       : MC_AbortSuperposition;
    axisPrintRoller    : AXIS_REF;
    rtAbortTrig        : R_TRIG;
    bRequestAbort      : BOOL;
    bAbortDone         : BOOL;
    bAbortBusy         : BOOL;
    bAbortError        : BOOL;
    nErrorID           : UDINT;
END_VAR

rtAbortTrig(CLK := bRequestAbort);
fbAbortShift(
    Execute  := rtAbortTrig.Q,
    Axis     := axisPrintRoller,
    Done     => bAbortDone,
    Busy     => bAbortBusy,
    Error    => bAbortError,
    ErrorID  => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：叠加运动启动后业务发现参数错了 / 检测信号变了 / 操作员按急停辅助键。需要"叠加段提前结束，但生产线主运动不能停"。
- **价值**：用一个 FB 精准中止叠加，不波及主运动。比"停掉所有运动再重新发主运动命令"的开销低几个数量级。
- **替代方案对比**：
  - 用 `MC_Stop`：把主运动也停了，生产线必停
  - 让叠加自己跑完：等待时间不可控，可能继续印更多废品
  - **本 FB**：精准中止叠加 + 主运动续行

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.2.3
- **InfoSys topic**：{info}
- **相关 FB**：`MC_MoveSuperImposed`（启动叠加）、`MC_Stop`、`MC_Halt`
"""
    body = "\n".join([
        vderived("fbAbortShift", "MC_AbortSuperposition"),
        vderived("axisPrintRoller", "AXIS_REF"),
        vderived("rtAbortTrig", "R_TRIG"),
        vbool("bRequestAbort", "FALSE"),
        vbool("bAbortDone"),
        vbool("bAbortBusy"),
        vbool("bAbortError"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：套色检测在叠加运动启动后发现方向算错（应叠加 -2 而非 +2）, 必须立刻
//       中止叠加避免印更多错色废品 — 但生产线主运动不能停。
// 价值：精准中止叠加，不波及主运动；比 MC_Stop 整体停产代价低几个数量级。
// 验证：先让 MC_MoveSuperImposed 叠加运动跑起来（前序 demo 假设已启动）；
//       bRequestAbort := TRUE → 看 ActPos 增长立刻停止（叠加段不再增长），
//       但主运动 ActVelo 维持原值；bAbortDone 短暂 TRUE。
// =============================================================================

rtAbortTrig(CLK := bRequestAbort);

fbAbortShift(
    Execute := rtAbortTrig.Q,
    Axis    := axisPrintRoller,
    Done    =&gt; bAbortDone,
    Busy    =&gt; bAbortBusy,
    Error   =&gt; bAbortError,
    ErrorID =&gt; nErrorID
);
"""
    emit("superposition", name, doc, xml_skel(name, body, st))


# ---------------------------------------------------------------------------
# 6.3.1 MC_Home — Position default DEFAULT_HOME_POSITION
# ---------------------------------------------------------------------------

def gen_home():
    name = "MC_Home"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70117515.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Homing", info, name)}

## 1. 功能简述

PLCopen 标准定义的**轴归零（参考运行）FB**。把轴从"未校准"状态变为"已校准"——通过参考运行序列（搜索原点开关 / 编码器 Z 信号 / 用户直接设位置等）确立轴的绝对零点。

参考模式由 System Manager 中编码器参数"Reference Mode"决定，本 FB 只是**触发**这个过程，具体序列取决于编码器硬件。`HomingMode` 输入可在多种模式间切换：默认归零、直接置位、强制标记已校准、复位校准状态等。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute         : BOOL;
    Position        : LREAL         := DEFAULT_HOME_POSITION;
    HomingMode      : MC_HomingMode;
    BufferMode      : MC_BufferMode;
    Options         : ST_HomingOptions;
    bCalibrationCam : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | {DESC_EXECUTE} |
| `Position` | `LREAL` | `DEFAULT_HOME_POSITION` | 归零完成后轴的绝对位置；取常量 `DEFAULT_HOME_POSITION` 表示采用 System Manager 里配的"参考位置" |
| `HomingMode` | `MC_HomingMode` | — | 归零模式：`MC_DefaultHoming`（默认序列）/ `MC_Direct`（直接置位不运动）/ `MC_ForceCalibration`（强制标记已校准不动）/ `MC_ResetCalibration`（清除已校准标志） |
| `BufferMode` | `MC_BufferMode` | — | {DESC_BUFFER} |
| `Options` | `ST_HomingOptions` | — | 归零序列选项（保留扩展） |
| `bCalibrationCam` | `BOOL` | — | 校准凸轮（原点开关）信号，由用户接入；归零序列在凸轮信号上升/下降沿做触发 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | {DESC_AXIS} |

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
| `Done` | `BOOL` | 归零完成置 `TRUE` |
| `Busy` | `BOOL` | {DESC_BUSY} |
| `Active` | `BOOL` | {DESC_ACTIVE} |
| `CommandAborted` | `BOOL` | {DESC_ABORTED} |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorID` | `UDINT` | {DESC_ERRORID} |

## 3. 行为说明

**触发**：`Execute` 上升沿启动归零序列。具体序列依赖编码器配置：

- **增量编码器 + 原点开关**：轴先按 System Manager 中"Reference Velocity (Sync)" 反方向找凸轮 → 找到后反向用"Reference Velocity (Cal)" 慢速过凸轮 → 在凸轮信号边沿（或下一个编码器 Z 信号）锁定零点 → 设位置为 `Position`
- **绝对编码器**：通常直接读编码器绝对值并设为 `Position`
- **MC_Direct**：不动轴，直接把当前位置设为 `Position`（适合手动校准后告诉 NC "我现在在哪"）
- **MC_ForceCalibration**：不动轴，强制把"轴已校准"标志置 TRUE（适合诊断 / 跳过参考运行）
- **MC_ResetCalibration**：不动轴，把"轴已校准"标志清 FALSE（用于强制下次必须归零）

**`bCalibrationCam` 信号接入**：通常把外部原点接近开关（NPN/PNP）的 PLC 输入直接连到本入口；NC 在归零序列中读这个位。

**与轴使能的关系**：归零通常要求轴 `MC_Power` 后处于 Standstill 状态；未使能轴无法运动归零（`MC_Direct` 等不动的模式除外）。

**归零完成后 `Axis.Status.HomingDone = TRUE`**（NC 内部状态）。

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **`Position` 留默认 = 用 System Manager 配置**：常量 `DEFAULT_HOME_POSITION` 由 Beckhoff 定义；不要传字面值 0 替代，因为很多轴的零点是非零绝对值（比如龙门机床的工件坐标原点）。
- **`HomingMode` 选错代价大**：`MC_ResetCalibration` 会让轴失去校准状态，再发任何位置类 Move 都报错；误用了要再 `MC_Home(HomingMode := MC_DefaultHoming)` 重新归。
- **`MC_Direct` 适合手动模式校准**：操作员手动把轴拖到已知位置后调 `MC_Direct(Position := knownPos)` 告诉 NC，省去再走一遍参考运行。
- **`bCalibrationCam` 信号必须与编码器"Reference Mode"匹配**：选错下降沿/上升沿模式会归零失败甚至撞极限。
- **归零进行中其它 Move 命令被锁**：和 `MC_Stop` 锁轴行为类似，归零期间发 Move 会被拒。
- **绝对编码器一般不需要每次开机归零**：但 TwinCAT 仍需要"知道编码器值映射到哪个绝对坐标"，开机第一次仍要 `MC_Direct` 或参数配置告诉 NC。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

```iecst
// 场景：CNC 机床开机自动归零 X 轴 — 走到原点开关然后定零，定零位置取 System Manager 配置
PROGRAM P_Demo_MC_Home
VAR
    fbAxisHoming      : MC_Home;
    axisX             : AXIS_REF;
    rtHomeTrig        : R_TRIG;
    bRequestHoming    : BOOL;
    bHomeCamSignal    : BOOL;
    bHomingDone       : BOOL;
    bHomingActive     : BOOL;
    nErrorID          : UDINT;
END_VAR

rtHomeTrig(CLK := bRequestHoming);
fbAxisHoming(
    Execute         := rtHomeTrig.Q,
    Position        := DEFAULT_HOME_POSITION,
    HomingMode      := MC_DefaultHoming,
    BufferMode      := MC_Aborting,
    bCalibrationCam := bHomeCamSignal,
    Axis            := axisX,
    Done            => bHomingDone,
    Active          => bHomingActive,
    ErrorID         => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：开机首次启动设备前的轴归零、操作员替换工件 / 重定基准的工序、绝对编码器丢失零点后的恢复、设备故障复位后的强制重新校准。
- **价值**：把"找原点开关 → 锁编码器 Z → 设零位"三段标准化序列封装为一个 FB；切换编码器硬件代码不变。
- **替代方案对比**：
  - 直接写 NC 通道命令（`MC_HOME`）：要拼 NC 控制字 + 监视状态字，10+ 行代码
  - 操作员手动 jog + `MC_Direct`：能做但依赖操作员准度
  - **本 FB**：自动化归零的标准做法；`HomingMode` 切换覆盖所有变体

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.3.1
- **InfoSys topic**：{info}
- **相关 FB**：`MC_Power`（先使能再归零）、`MC_Reset`（清错后才能归零）、`MC_Stop`、`MC_HomingMode`（枚举定义）
"""
    body = "\n".join([
        vderived("fbAxisHoming", "MC_Home"),
        vderived("axisX", "AXIS_REF"),
        vderived("rtHomeTrig", "R_TRIG"),
        vbool("bRequestHoming", "FALSE", "在线 TRUE 触发归零"),
        vbool("bHomeCamSignal", "FALSE", "在线模拟原点开关信号；实机接 PLC 输入"),
        vbool("bHomingDone"),
        vbool("bHomingActive"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：CNC 机床开机自动归零 X 轴 — 走到原点接近开关 + 锁编码器 Z 后把当前
//       位置设为 System Manager 中配置的"参考位置"（用 DEFAULT_HOME_POSITION
//       常量自动取系统配置而非脑补 0）。
// 价值：把"找原点 → 锁 Z → 设零位"三段标准化序列封装；切换编码器硬件不改代码。
// 验证：先确保 axisX 已用 MC_Power 使能；bRequestHoming := TRUE →
//       bHomingActive 立即 TRUE；轴自动跑到原点开关附近；bHomeCamSignal
//       上升沿后轴锁 Z；bHomingDone 短暂 TRUE，之后 axisX.Status.HomingDone = TRUE。
// =============================================================================

rtHomeTrig(CLK := bRequestHoming);

fbAxisHoming(
    Execute         := rtHomeTrig.Q,
    Position        := DEFAULT_HOME_POSITION,
    HomingMode      := MC_DefaultHoming,
    BufferMode      := MC_Aborting,
    bCalibrationCam := bHomeCamSignal,
    Axis            := axisX,
    Done            =&gt; bHomingDone,
    Active          =&gt; bHomingActive,
    ErrorID         =&gt; nErrorID
);
"""
    emit("homing", name, doc, xml_skel(name, body, st))


# ---------------------------------------------------------------------------
# 6.4.1 MC_Jog
# ---------------------------------------------------------------------------

def gen_jog():
    name = "MC_Jog"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70120459.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Manual motion", info, name)}

## 1. 功能简述

PLCopen 标准定义的**手动寸动（Jog）FB**。直接把操作员按钮（前进 / 后退）信号接到 `JogForward` / `JogBackwards`，FB 按 `Mode` 选定的模式驱动轴：按住按钮持续走、按一次走固定距离、按一次走整数倍模数等。

`Mode` 决定了 `Position`、`Velocity`、`Acceleration`、`Deceleration`、`Jerk` 是否生效——标准慢/快模式用 System Manager 中"manual functions"的预设速度，连续模式 / 寸动模式才用 FB 入口参数。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    JogForward   : BOOL;
    JogBackwards : BOOL;
    Mode         : E_JogMode;
    Position     : LREAL;
    Velocity     : LREAL;
    Acceleration : LREAL;
    Deceleration : LREAL;
    Jerk         : LREAL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `JogForward` | `BOOL` | — | 上升沿触发正方向运动；电平 TRUE 期间轴持续走（除 `MC_JOGMODE_INCHING*`）；运动中再触发任何沿不响应；`JogForward` 与 `JogBackwards` 同时高时 `JogForward` 优先 |
| `JogBackwards` | `BOOL` | — | 上升沿触发反方向运动；与 `JogForward` 互锁 |
| `Mode` | `E_JogMode` | — | 寸动模式：`MC_JOGMODE_STANDARD_SLOW` / `_STANDARD_FAST` / `_CONTINOUS` / `_INCHING` / `_INCHING_MODULO`（具体行为见 §3） |
| `Position` | `LREAL` | — | `MC_JOGMODE_INCHING` / `_INCHING_MODULO` 模式下的单步距离 |
| `Velocity` | `LREAL` | — | 最大行进速度 `>0`；`STANDARD_*` 模式忽略此值（用 System Manager 预设） |
| `Acceleration` | `LREAL` | — | {DESC_ACC}；`STANDARD_*` 模式忽略 |
| `Deceleration` | `LREAL` | — | {DESC_DEC}；`STANDARD_*` 模式忽略 |
| `Jerk` | `LREAL` | — | {DESC_JERK}；`STANDARD_*` 模式忽略 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | {DESC_AXIS} |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done           : BOOL;
    Busy           : BOOL;
    CommandAborted : BOOL;
    Error          : BOOL;
    ErrorID        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 一段 Jog 动作完成（寸动一格 / 按钮松开后轴停） |
| `Busy` | `BOOL` | {DESC_BUSY} |
| `CommandAborted` | `BOOL` | {DESC_ABORTED} |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorID` | `UDINT` | {DESC_ERRORID} |

## 3. 行为说明

**五种 `Mode` 行为详解**：

| Mode 取值 | 触发 | 速度/加速来源 | 走多远 |
|---|---|---|---|
| `MC_JOGMODE_STANDARD_SLOW` | 电平：按钮 TRUE 走，FALSE 停 | System Manager "low velocity for manual" + 标准加速 | 按住多久走多远 |
| `MC_JOGMODE_STANDARD_FAST` | 电平 | System Manager "high velocity for manual" + 标准加速 | 按住多久走多远 |
| `MC_JOGMODE_CONTINOUS` | 电平 | FB 入口 `Velocity` / `Acceleration` / `Deceleration` / `Jerk` | 按住多久走多远 |
| `MC_JOGMODE_INCHING` | 上升沿 | FB 入口 | 走 `Position` 然后自动停，无视按钮是否还按住 |
| `MC_JOGMODE_INCHING_MODULO` | 上升沿 | FB 入口 | 走到 `Position` 的整数倍位置（"对齐到格子") |

**两按钮互锁**：`JogForward` 与 `JogBackwards` 内部互斥；同时 TRUE 时 `JogForward` 优先。运动中切按钮无效，必须先松一次再按。

**典型用法**：HMI 上"快/慢前进"按钮、机床调试面板上的方向键、机械手手动模式下的关节寸动。`MC_JOGMODE_INCHING` 适合"按一次走 0.1 mm"这种精细调整。

**Done 出现时机**：寸动模式下走完一段 Position 即 Done；电平模式下松开按钮、轴减速到 0 时 Done。

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **运动中无视按钮变化**：开始走以后再按反方向无效，必须先把当前方向松开。
- **`STANDARD_*` 模式下 Velocity 不生效**：很多新手在 STANDARD_FAST 下改 `Velocity` 入口不解为何没反应——这两模式用的是 System Manager 配置不是 FB 入口。
- **`INCHING` 模式下按钮按住不影响**：触发即走一段，不会因为按钮一直按继续走。要"按住一直走"应该选 `CONTINOUS`。
- **两按钮同时按 JogForward 优先**：硬件上别指望"同时按表示停"，要停得双都松开。
- **没有上锁机制**：Jog 不锁轴，所以 Jog 中其它代码发 Move 命令可以抢；调试时应禁止业务程序与 Jog 同时启用。（工程经验补充）
- **HMI 设计要把按钮接到电平变量而非脉冲变量**：JogForward 是电平触发（除 inching），如果 HMI 给的是"按一次发 100 ms 脉冲"会出怪异行为。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

```iecst
// 场景：HMI 手动模式面板 — 操作员按住"X+"快速正向走，按住"X-"快速反向走
PROGRAM P_Demo_MC_Jog
VAR
    fbJogX           : MC_Jog;
    axisX            : AXIS_REF;
    bHmiJogForward   : BOOL;
    bHmiJogBackward  : BOOL;
    bJogDone         : BOOL;
    bJogBusy         : BOOL;
    nErrorID         : UDINT;
END_VAR

fbJogX(
    JogForward   := bHmiJogForward,
    JogBackwards := bHmiJogBackward,
    Mode         := MC_JOGMODE_STANDARD_FAST,
    Position     := 0.0,
    Velocity     := 100.0,
    Acceleration := 1000.0,
    Deceleration := 1000.0,
    Jerk         := 10000.0,
    Axis         := axisX,
    Done         => bJogDone,
    Busy         => bJogBusy,
    ErrorID      => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：调试 / 维修人员手动调位、HMI 手动模式按钮、机械手关节寸动、机床导轨清洁后定位、料盒手动归位。共同点：**操作员按钮直接驱动轴**。
- **价值**：业务无需自己写"按钮按下 → 调 MoveVelocity → 按钮抬起 → 调 Halt"的状态机；FB 直接接电平信号，加上 5 种模式覆盖工业上几乎所有手动场景。
- **替代方案对比**：
  - 自己写 `MC_MoveVelocity` + `MC_Halt`：能做但要管理按钮上升沿 / 下降沿、互锁、停止时序等
  - 用 `MC_MoveAbsolute` 给一个超远目标：违背"按钮电平"语义，松开按钮停车依赖额外 Halt
  - **本 FB**：手动寸动标准做法，与 PLCopen 规范一致

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.4.1
- **InfoSys topic**：{info}
- **相关 FB**：`MC_MoveVelocity`、`MC_Halt`、`E_JogMode`（枚举定义）
"""
    body = "\n".join([
        vderived("fbJogX", "MC_Jog"),
        vderived("axisX", "AXIS_REF"),
        vbool("bHmiJogForward", "FALSE", "HMI 正方向按钮电平"),
        vbool("bHmiJogBackward", "FALSE", "HMI 反方向按钮电平"),
        vbool("bJogDone"),
        vbool("bJogBusy"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：HMI 手动面板 — 操作员按住"X+"快速正向走，按住"X-"快速反向走。
//       用 MC_JOGMODE_STANDARD_FAST 表示"用 System Manager 中的高速预设"，
//       FB 入口 Velocity 不生效（这点新手容易迷惑）。
// 价值：业务不用自己写 MoveVelocity + Halt 的按钮状态机，FB 直接收电平。
// 验证：先 MC_Power 使能 axisX；bHmiJogForward := TRUE 持续 1 秒 → ActPos
//       增加约 100 mm（按 SysMgr 高速预设），松开后自动减速到 0；
//       bHmiJogBackward 反方向同理。
// =============================================================================

fbJogX(
    JogForward   := bHmiJogForward,
    JogBackwards := bHmiJogBackward,
    Mode         := MC_JOGMODE_STANDARD_FAST,
    Position     := 0.0,
    Velocity     := 100.0,
    Acceleration := 1000.0,
    Deceleration := 1000.0,
    Jerk         := 10000.0,
    Axis         := axisX,
    Done         =&gt; bJogDone,
    Busy         =&gt; bJogBusy,
    ErrorID      =&gt; nErrorID
);
"""
    emit("manual_motion", name, doc, xml_skel(name, body, st))


# ---------------------------------------------------------------------------
# 6.5.1 MC_GearIn — Master/Slave VAR_IN_OUT, RatioNumerator LREAL, RatioDenominator UINT
# ---------------------------------------------------------------------------

def gen_gear_in():
    name = "MC_GearIn"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70123403.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Axis coupling", info, name)}

## 1. 功能简述

PLCopen 标准定义的**线性电子齿轮耦合 FB**。把从轴（Slave）按固定齿比 `RatioNumerator / RatioDenominator` 绑定到主轴（Master），从轴位置 = 主轴位置 × 齿比。耦合建立后从轴**自动跟随**主轴运动，无需 PLC 周期性发命令。

**只能在从轴静止时建立耦合**——`MC_GearIn` 无法同步到正在运动的主轴。要做"飞剪 / 跟随启动"用 `MC_GearInVelo` 或 `MC_GearInPos`（不在本库标准 22 个内）。

齿比解耦用 `MC_GearOut`；要动态调齿比用 `MC_GearInDyn`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute          : BOOL;
    RatioNumerator   : LREAL;
    RatioDenominator : UINT;
    Acceleration     : LREAL;
    Deceleration     : LREAL;
    Jerk             : LREAL;
    BufferMode       : MC_BufferMode;
    Options          : ST_GearInOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | {DESC_EXECUTE} |
| `RatioNumerator` | `LREAL` | — | 齿比分子（浮点）；若 `RatioDenominator = 1` 则齿比 = 此分子 |
| `RatioDenominator` | `UINT` | — | 齿比分母 |
| `Acceleration` | `LREAL` | — | 加速度 `≥0`，**当前版本未实现**，填什么都不生效 |
| `Deceleration` | `LREAL` | — | 减速度 `≥0`，**当前版本未实现** |
| `Jerk` | `LREAL` | — | Jerk `≥0`，**当前版本未实现** |
| `BufferMode` | `MC_BufferMode` | — | **当前版本未实现** |
| `Options` | `ST_GearInOptions` | — | 耦合选项（保留扩展） |

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
| `Slave` | `AXIS_REF` | 从轴 AXIS_REF；耦合建立后从轴的运动**由主轴决定** |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    InGear         : BOOL;
    Busy           : BOOL;
    Active         : BOOL;
    CommandAborted : BOOL;
    Error          : BOOL;
    ErrorID        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `InGear` | `BOOL` | 耦合已建立时置 `TRUE`；从轴开始跟随主轴 |
| `Busy` | `BOOL` | {DESC_BUSY} |
| `Active` | `BOOL` | {DESC_ACTIVE} |
| `CommandAborted` | `BOOL` | {DESC_ABORTED} |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorID` | `UDINT` | {DESC_ERRORID} |

## 3. 行为说明

**触发**：`Execute` 上升沿在从轴静止时建立耦合，`InGear := TRUE`。之后只要主轴动，从轴**自动按齿比跟随**，PLC 不用写任何运动命令。

**齿比表达**：分数形式 `RatioNumerator / RatioDenominator` 适合工程上"输入齿数/输出齿数"这种整数比；浮点用法 `Denominator = 1` 时 `RatioNumerator` 直接当浮点比。例：`RatioNumerator = 1.5, RatioDenominator = 1` 表示从轴速度是主轴的 1.5 倍。

**反向耦合**：`RatioNumerator` 为负 = 反向跟随。

**从轴静止要求**：耦合时从轴 `Status.NotMoving = TRUE`，否则报错。若从轴在动，先 `MC_Halt(Slave)` 停下再耦合。

**解耦**：用 `MC_GearOut`；解耦时从轴**不会自动停**，会保持当前速度无限走（除非外部用 `MC_Halt` / `MC_Stop` 停它）。这一点常被忽略，引发"解耦后轴撞极限"事故。

**主轴运动期间发 Move 给从轴**：从轴上发 `MC_MoveAbsolute` 等会先**自动解耦**再执行；耦合状态被破坏。

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **`Acceleration / Deceleration / Jerk / BufferMode` 全部未实现**：填了没用，别误以为耦合"会按这个加速度跟上去"。耦合建立时从轴是瞬时跟随。
- **解耦后从轴不会自动停**：见 §3 解耦段。要"解耦即停"必须在 `MC_GearOut` 后立即接 `MC_Halt(Slave)`。
- **必须从轴静止才能耦合**：动着要先停。
- **耦合期间给从轴发 Move 自动解耦**：常见坑，例如调试时手贱给从轴发 `MC_Jog` 一下就把耦合关系破坏。
- **齿比改不了**：要改需先 `MC_GearOut` 再重新 `MC_GearIn`，或者用 `MC_GearInDyn`。
- **AXIS_REF 必须传引用**：`Master` 和 `Slave` 都是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

```iecst
// 场景：包装线主滚筒 + 推送轴电子齿轮 1:2（推送走 2 倍速度），保持袋长一致
PROGRAM P_Demo_MC_GearIn
VAR
    fbCouplePusher    : MC_GearIn;
    axisMainRoller    : AXIS_REF;
    axisPusher        : AXIS_REF;
    rtCoupleTrig      : R_TRIG;
    bRequestCouple    : BOOL;
    bIsCoupled        : BOOL;
    bCoupleBusy       : BOOL;
    nErrorID          : UDINT;
END_VAR

rtCoupleTrig(CLK := bRequestCouple);
fbCouplePusher(
    Execute          := rtCoupleTrig.Q,
    RatioNumerator   := 2.0,
    RatioDenominator := 1,
    Acceleration     := 0.0,
    Deceleration     := 0.0,
    Jerk             := 0.0,
    Master           := axisMainRoller,
    Slave            := axisPusher,
    InGear           => bIsCoupled,
    Busy             => bCoupleBusy,
    ErrorID          => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：包装机推送轴跟随主传送带、印刷机色版滚筒严格同步主滚筒、卷绕机收线辊跟随主线辊、机械式齿轮箱的电子化替代。共同点：**两轴硬同步**，比例固定。
- **价值**：建立耦合后从轴自动跟，PLC 不用周期性发位置/速度命令；机械齿轮箱可直接拆掉变成电子齿轮，结构简化 + 比例可动态切换。
- **替代方案对比**：
  - 用 `MC_GearInDyn`：齿比动态可调，但 Acceleration 才生效；本 FB 是固定齿比的简化版
  - 用 `MC_CamIn`（不在本库 22 个内）：凸轮表非线性同步，比电子齿轮灵活
  - 自己读主轴位置 × 齿比 → `MC_MoveAbsolute(Slave)`：每周期发命令，CPU 开销大且有相位滞后
  - **本 FB**：固定线性比例耦合的首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.5.1
- **InfoSys topic**：{info}
- **相关 FB**：`MC_GearOut`（解耦）、`MC_GearInDyn`（动态齿比）、`MC_GearInMultiMaster`（多主跟随）、`MC_Halt(Slave)`（解耦后停从轴）
"""
    body = "\n".join([
        vderived("fbCouplePusher", "MC_GearIn"),
        vderived("axisMainRoller", "AXIS_REF"),
        vderived("axisPusher", "AXIS_REF"),
        vderived("rtCoupleTrig", "R_TRIG"),
        vbool("bRequestCouple", "FALSE"),
        vbool("bIsCoupled"),
        vbool("bCoupleBusy"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：包装机主滚筒带动料袋前行，推送轴必须以主滚筒 2 倍速度同步把袋子推
//       出 — 用电子齿轮 RatioNumerator/Denominator = 2/1 严格绑定，保证袋
//       长一致不受主速度变化影响。
// 价值：建立耦合后 PLC 不用周期性发推送命令，主滚筒动从轴自动跟。
// 验证：先用 MC_Halt 把 axisPusher 停住（耦合要求从轴静止）；
//       bRequestCouple := TRUE → bIsCoupled 立 TRUE；
//       此时改 axisMainRoller 的速度（外部 MC_MoveVelocity），axisPusher.NcToPlc.ActVelo
//       应自动 = 主轴速度 × 2。
//       注意：解耦时（用 MC_GearOut）从轴不会自动停，需另用 MC_Halt(axisPusher) 接着停。
// =============================================================================

rtCoupleTrig(CLK := bRequestCouple);

fbCouplePusher(
    Execute          := rtCoupleTrig.Q,
    RatioNumerator   := 2.0,
    RatioDenominator := 1,
    Acceleration     := 0.0,
    Deceleration     := 0.0,
    Jerk             := 0.0,
    Master           := axisMainRoller,
    Slave            := axisPusher,
    InGear           =&gt; bIsCoupled,
    Busy             =&gt; bCoupleBusy,
    ErrorID          =&gt; nErrorID
);
"""
    emit("axis_coupling", name, doc, xml_skel(name, body, st))


if __name__ == "__main__":
    gen_move_superimposed()
    gen_abort_superposition()
    gen_home()
    gen_jog()
    gen_gear_in()
    print("batch 3a done")
