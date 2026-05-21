#!/usr/bin/env python3
"""Generator for Tc2_MC2 — batch 4 (final 7):

  axis_coupling: MC_GearInDyn, MC_GearOut, MC_GearInMultiMaster
  phasing:       MC_HaltPhasing, MC_PhasingAbsolute, MC_PhasingRelative
  torque:        MC_TorqueControl
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
# 6.5.2 MC_GearInDyn — Enable + dynamic GearRatio
# ---------------------------------------------------------------------------

def gen_gear_in_dyn():
    name = "MC_GearInDyn"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70124939.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Axis coupling", info, name)}

## 1. 功能简述

PLCopen 标准定义的**动态齿比电子齿轮 FB**。与 `MC_GearIn` 区别：齿比 `GearRatio` 可在每个 PLC 周期动态变化——只要 `Enable = TRUE` 就持续生效。`Acceleration` 入口在齿比大幅变化时起限速作用。

典型用法：根据张力 / 速度 / 工艺参数实时调齿比，实现"软电子齿轮"——比 `MC_GearIn` 灵活但仅 `Acceleration` 入口实现，其它如 `Deceleration`、`Jerk`、`BufferMode` 在当前 PDF 版本未实现。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Enable       : BOOL;
    GearRatio    : LREAL;
    Acceleration : LREAL;
    Deceleration : LREAL;
    Jerk         : LREAL;
    BufferMode   : MC_BufferMode;
    Options      : ST_GearInDynOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Enable` | `BOOL` | — | 电平触发：`TRUE` 时建立耦合并持续保持；`TRUE → FALSE` 时**结束命令但不解耦**（齿比冻结在最后值，从轴仍跟主轴） |
| `GearRatio` | `LREAL` | — | 齿比（浮点）；`Enable = TRUE` 时可每周期改 |
| `Acceleration` | `LREAL` | — | 加速度 `≥0`；在大幅变齿比时限制从轴加速度。最大加速度只在主轴最大速度时达到 |
| `Deceleration` | `LREAL` | — | 减速度 `≥0`，**当前版本未实现** |
| `Jerk` | `LREAL` | — | Jerk `≥0`，**当前版本未实现** |
| `BufferMode` | `MC_BufferMode` | — | **当前版本未实现** |
| `Options` | `ST_GearInDynOptions` | — | 耦合选项（保留扩展） |

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
| `Slave` | `AXIS_REF` | 从轴 AXIS_REF |

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
| `InGear` | `BOOL` | 耦合建立时置 `TRUE` |
| `Busy` | `BOOL` | {DESC_BUSY} |
| `Active` | `BOOL` | {DESC_ACTIVE} |
| `CommandAborted` | `BOOL` | {DESC_ABORTED} |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorID` | `UDINT` | {DESC_ERRORID} |

## 3. 行为说明

**电平触发耦合**：与 `MC_GearIn` 边沿触发不同，本 FB 是电平：`Enable = TRUE` 期间耦合持续；改 `GearRatio` 立即生效。

**`Enable → FALSE` 不解耦**：PDF 明确：`Enable` 变 FALSE 后命令结束，**齿比冻结在最后值**但从轴**仍处于耦合状态**。要真正解耦必须调 `MC_GearOut`。这是与 `MC_GearIn` 边沿触发型最大的差异。

**`MC_GearOut` 与 `Enable` 互动**：若在 `Enable = TRUE` 期间调用 `MC_GearOut`，从轴**短暂解耦后立刻重新耦合**——因为本 FB 仍在持续要求耦合状态。要真正解耦必须**先 `Enable := FALSE` 再 `MC_GearOut`**。

**`Acceleration` 的作用机制**：大幅变齿比时（例如从 1.0 切到 5.0）从轴需要加速跟上，本入口限制此加速段的加速度上限。**最大加速度只在主轴最大速度时达到**；主轴速度低时从轴实际加速度会按比例缩小。

**典型用法**：根据卷径变化实时调整收线辊齿比保持线速度恒定、张力反馈环每周期微调齿比。

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **`Enable := FALSE` 不等于解耦**：见 §3。新手最常踩的坑是把 Enable 拉低期望"解耦从轴"——实际从轴仍按上一次齿比跟主轴走。
- **`MC_GearOut` 在 `Enable = TRUE` 时无效**：短暂解耦立刻重耦。要解耦顺序必须是 `Enable := FALSE` → `MC_GearOut(Slave)` → 可选 `MC_Halt(Slave)`。
- **`Deceleration / Jerk / BufferMode` 未实现**：填了没用，别误以为变齿比时减速段会受这些约束。
- **齿比大跃迁会出冲击**：从 1 一步切到 10，受 `Acceleration` 限制后从轴会有一段斜坡跟上，但工艺上仍可能有突变冲击。建议在 PLC 侧用低通滤波平滑 `GearRatio` 输入。（工程经验补充）
- **耦合期间从轴上发 Move 自动解耦**：与 `MC_GearIn` 相同行为。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

```iecst
// 场景：卷料机收线辊根据卷径变化实时调齿比 — 卷越大主轴 1 圈 = 从轴少几度
PROGRAM P_Demo_MC_GearInDyn
VAR
    fbDynamicGear      : MC_GearInDyn;
    axisLineRoll       : AXIS_REF;
    axisTakeUp         : AXIS_REF;
    bEnableCoupling    : BOOL;
    lrCurrentGearRatio : LREAL := 1.0;
    bIsCoupled         : BOOL;
    bCoupleBusy        : BOOL;
    nErrorID           : UDINT;
END_VAR

// 业务每周期根据卷径算新齿比并写到 lrCurrentGearRatio
// 这里假设外部代码维护，本 FB 只负责把齿比应用到耦合
fbDynamicGear(
    Enable       := bEnableCoupling,
    GearRatio    := lrCurrentGearRatio,
    Acceleration := 1000.0,
    Deceleration := 0.0,
    Jerk         := 0.0,
    Master       := axisLineRoll,
    Slave        := axisTakeUp,
    InGear       => bIsCoupled,
    Busy         => bCoupleBusy,
    ErrorID      => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：卷绕收放线（卷径变化自动调齿比保线速度）、张力闭环控制（张力反馈实时微调齿比）、变频调速对齐主从、PCB 钻床主轴-进给轴动态比例。
- **价值**：齿比是 PLC 变量可任意 PID/算法控制；机械变速箱无法做到的"软实时变比"用本 FB 直接实现。
- **替代方案对比**：
  - `MC_GearIn`：齿比固定，改齿比要 GearOut + GearIn 两步切换且从轴瞬时解耦再耦合，工艺中断
  - 自己读主轴位置 × 齿比 → `MC_MoveAbsolute(Slave)`：CPU 开销大、有相位滞后
  - **本 FB**：动态齿比的标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.5.2
- **InfoSys topic**：{info}
- **相关 FB**：`MC_GearIn`（固定齿比）、`MC_GearOut`（解耦）、`MC_GearInMultiMaster`（多主跟随）
"""
    body = "\n".join([
        vderived("fbDynamicGear", "MC_GearInDyn"),
        vderived("axisLineRoll", "AXIS_REF"),
        vderived("axisTakeUp", "AXIS_REF"),
        vbool("bEnableCoupling", "FALSE", "在线 TRUE 启用动态齿轮耦合"),
        vlreal("lrCurrentGearRatio", "1.0", "动态齿比；业务代码每周期可改"),
        vbool("bIsCoupled"),
        vbool("bCoupleBusy"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：卷绕收线机 — 主轴是出料辊（线速度恒定），从轴是收线轴。随着卷径变
//       大，要保持线速度恒定就要不停降低齿比。业务侧代码（外部）根据卷径
//       传感器每周期更新 lrCurrentGearRatio，本 FB 把这个齿比应用到耦合。
// 价值：齿比是 PLC 变量，可被 PID / 卷径算法实时控制；机械齿轮箱做不到。
// 验证：bEnableCoupling := TRUE → bIsCoupled 立 TRUE；
//       在线写 lrCurrentGearRatio = 0.5 → 看 axisTakeUp.NcToPlc.ActVelo 立刻变为
//       axisLineRoll.ActVelo × 0.5；继续在线写 0.3、0.2 验证连续可变。
//       注意：bEnableCoupling := FALSE 不会解耦（齿比冻结），要彻底解耦
//       需调用 MC_GearOut(axisTakeUp)。
// =============================================================================

fbDynamicGear(
    Enable       := bEnableCoupling,
    GearRatio    := lrCurrentGearRatio,
    Acceleration := 1000.0,
    Deceleration := 0.0,
    Jerk         := 0.0,
    Master       := axisLineRoll,
    Slave        := axisTakeUp,
    InGear       =&gt; bIsCoupled,
    Busy         =&gt; bCoupleBusy,
    ErrorID      =&gt; nErrorID
);
"""
    emit("axis_coupling", name, doc, xml_skel(name, body, st))


# ---------------------------------------------------------------------------
# 6.5.3 MC_GearOut — minimal: Execute + Options + Slave
# ---------------------------------------------------------------------------

def gen_gear_out():
    name = "MC_GearOut"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70126475.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Axis coupling", info, name)}

## 1. 功能简述

PLCopen 标准定义的**电子齿轮解耦 FB**。把由 `MC_GearIn` / `MC_GearInDyn` / `MC_GearInMultiMaster` / `MC_CamIn` 建立的主从耦合**解开**。

⚠️ **解耦不停轴**：从轴解耦后**仍保持当前速度无限走**，与主轴无关。PDF 明确以 `DANGER` / `WARNING` 标识此风险。必须显式接 `MC_Halt` / `MC_Stop` 才能停从轴。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute : BOOL;
    Options : ST_GearOutOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | {DESC_EXECUTE} |
| `Options` | `ST_GearOutOptions` | — | 解耦选项（保留扩展） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Slave : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Slave` | `AXIS_REF` | 要解耦的从轴；解耦后该轴从耦合状态变成"已解耦但仍在走"状态 |

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
| `Done` | `BOOL` | 解耦完成置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后立即 `TRUE`，FB 完成后 `FALSE` |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorID` | `UDINT` | {DESC_ERRORID} |

## 3. 行为说明

**触发**：`Execute` 上升沿启动解耦。瞬时完成，`Done` 短暂置 TRUE。

**Setpoint generator type 影响**：PDF 明确指出，若轴设定值发生器类型为 "7 phases (optimized)"（TwinCAT 2.11 起的默认），从轴解耦后进入**无加速度状态**并以解耦瞬间的恒速继续走，行为等同于 `MC_MoveVelocity` 启动后的"放手"状态。TwinCAT 2.10 用户可自选发生器类型，但 2.11+ 已固定。

**`MC_GearInDyn` 持续耦合时**：若 `MC_GearInDyn` 的 `Enable` 仍为 TRUE 状态下调用本 FB，从轴**短暂解耦后立即重新耦合**（因为 `MC_GearInDyn` 持续要求耦合）。要彻底解耦顺序：`Enable := FALSE` → `MC_GearOut(Slave)`。

**与 `MC_GearInMultiMaster` 互动相同**：见上一条。

**典型用法**：
1. 工艺段结束需要从轴单独继续走或停下时，先 `MC_GearOut` 再 `MC_Halt`
2. 模式切换：从"耦合跟随"切换到"独立定位"

⚠️ **解耦后必须管住从轴**：永远不要单独发 `MC_GearOut` 不接停车命令。

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- ⚠️ **解耦后从轴不停**：是本 FB 最大的"坑"。必须显式 `MC_Halt(Slave)` 或 `MC_Stop(Slave)`。
- **`MC_GearInDyn` 持续 Enable = TRUE 时解不掉**：见 §3。顺序必须先关 Enable 再 GearOut。
- **解耦速度等于解耦瞬间从轴速度**：不是主轴速度 × 齿比，而是从轴实际速度（受加速度限制可能略小于理论值）。
- **没耦合状态调用会出错**：`MC_GearOut` 期望轴当前在耦合中，否则 `Error := TRUE`。
- **解耦后再耦合需重新调 `MC_GearIn`**：解耦不是"暂停"，是终止耦合关系。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

```iecst
// 场景：工艺段结束 — 从轴脱开主轴跟随，然后立刻平稳停车避免冲极限
PROGRAM P_Demo_MC_GearOut
VAR
    fbDecouple        : MC_GearOut;
    fbHaltSlave       : MC_Halt;
    axisSlave         : AXIS_REF;
    rtDecoupleTrig    : R_TRIG;
    bRequestDecouple  : BOOL;
    bDecoupleDone     : BOOL;
    bSlaveStopDone    : BOOL;
    nErrorID          : UDINT;
END_VAR

rtDecoupleTrig(CLK := bRequestDecouple);
fbDecouple(
    Execute := rtDecoupleTrig.Q,
    Slave   := axisSlave,
    Done    => bDecoupleDone,
    ErrorID => nErrorID
);

// 解耦完成立刻发停车命令 — 否则从轴会无限走
fbHaltSlave(
    Execute      := bDecoupleDone,
    Deceleration := 2000.0,
    Jerk         := 20000.0,
    Axis         := axisSlave,
    Done         => bSlaveStopDone
);
```

## 7. 业务场景与实际价值

- **场景**：耦合工艺段完成后切换到独立运动、故障检测要求"脱开主轴单独停"、多工艺模式切换。
- **价值**：把"解耦"动作标准化为单次 FB 调用；不必直接操作 NC 通道控制字。
- **替代方案对比**：
  - 自己写 NC 命令解耦：要拼 `MC_DECOUPLE` 控制字，10+ 行
  - 用 `MC_Stop(Slave)`：停轴但**不解耦**，主轴动从轴仍试图跟，会跟错位
  - **本 FB + `MC_Halt`**：解耦 + 停车的标准两步法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.5.3
- **InfoSys topic**：{info}
- **相关 FB**：`MC_GearIn`、`MC_GearInDyn`、`MC_GearInMultiMaster`、`MC_Halt`、`MC_Stop`
"""
    body = "\n".join([
        vderived("fbDecouple", "MC_GearOut"),
        vderived("fbHaltSlave", "MC_Halt"),
        vderived("axisSlave", "AXIS_REF"),
        vderived("rtDecoupleTrig", "R_TRIG"),
        vbool("bRequestDecouple", "FALSE"),
        vbool("bDecoupleDone"),
        vbool("bSlaveStopDone"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：电子齿轮耦合工艺段完成 — 先解耦从轴让它脱离主轴跟随，然后立刻
//       发 MC_Halt 把从轴平稳停下来。直接发 MC_GearOut 不接停车从轴会
//       无限走（PDF DANGER 提醒）。
// 价值：标准的"解耦 + 停车"两步法；避免冲软限位 / 撞机械限位事故。
// 验证：先建立耦合（外部 MC_GearIn 已经调过，demo 假设 axisSlave 在跟主轴跑）；
//       bRequestDecouple := TRUE → bDecoupleDone 一闪 TRUE；
//       同周期触发 fbHaltSlave 减速；ActVelo 渐降到 0；
//       bSlaveStopDone 短暂 TRUE。
// =============================================================================

rtDecoupleTrig(CLK := bRequestDecouple);

fbDecouple(
    Execute := rtDecoupleTrig.Q,
    Slave   := axisSlave,
    Done    =&gt; bDecoupleDone,
    ErrorID =&gt; nErrorID
);

// 解耦完成立刻接停车 — 这是 PDF 反复强调的"务必做"步骤
fbHaltSlave(
    Execute      := bDecoupleDone,
    Deceleration := 2000.0,
    Jerk         := 20000.0,
    Axis         := axisSlave,
    Done         =&gt; bSlaveStopDone
);
"""
    emit("axis_coupling", name, doc, xml_skel(name, body, st))


# ---------------------------------------------------------------------------
# 6.5.4 MC_GearInMultiMaster — Master1..Master4 (Reference To AXIS_REF), GearRatio1..4
# ---------------------------------------------------------------------------

def gen_gear_in_multimaster():
    name = "MC_GearInMultiMaster"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70128011.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Axis coupling", info, name)}

## 1. 功能简述

PLCopen 标准扩展的**多主电子齿轮耦合 FB**。最多 4 根主轴同时驱动一根从轴：从轴运动 = Σ(MasterN × GearRatioN)。齿比每周期可改，`Acceleration` 在大幅变齿比时限速。

用于 1+ 主轴对 1 从轴的复杂同步：例如双轴叠加（X1 + X2 → 工件 X 位）或张力补偿叠加。少于 4 主时未用的 Master 参数传空数据结构（轴 ID = 0）即可。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Master1      : Reference To AXIS_REF;
    Master2      : Reference To AXIS_REF;
    Master3      : Reference To AXIS_REF;
    Master4      : Reference To AXIS_REF;
    Enable       : BOOL;
    GearRatio1   : LREAL;
    GearRatio2   : LREAL;
    GearRatio3   : LREAL;
    GearRatio4   : LREAL;
    Acceleration : LREAL;
    Deceleration : LREAL;
    Jerk         : LREAL;
    BufferMode   : MC_BufferMode;
    Options      : ST_GearInMultiMasterOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Master1` | `Reference To AXIS_REF` | — | 主轴 1 引用 |
| `Master2` | `Reference To AXIS_REF` | — | 主轴 2 引用；不用时传空结构（轴 ID = 0） |
| `Master3` | `Reference To AXIS_REF` | — | 主轴 3 引用；不用时传空结构 |
| `Master4` | `Reference To AXIS_REF` | — | 主轴 4 引用；不用时传空结构 |
| `Enable` | `BOOL` | — | 电平触发；行为同 `MC_GearInDyn`：`TRUE` 期间持续耦合，`FALSE` 时命令结束**但不解耦**（齿比冻结） |
| `GearRatio1` | `LREAL` | — | Master1 的齿比（浮点）；`Enable = TRUE` 时可周期改 |
| `GearRatio2` | `LREAL` | — | Master2 齿比 |
| `GearRatio3` | `LREAL` | — | Master3 齿比 |
| `GearRatio4` | `LREAL` | — | Master4 齿比 |
| `Acceleration` | `LREAL` | — | 加速度，限制齿比大幅变化时的从轴加速度 |
| `Deceleration` | `LREAL` | — | 减速度 |
| `Jerk` | `LREAL` | — | Jerk |
| `BufferMode` | `MC_BufferMode` | — | 当前版本未实现 |
| `Options` | `ST_GearInMultiMasterOptions` | — | 选项（可启用 AdvancedSlaveDynamics 等） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Slave : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Slave` | `AXIS_REF` | 从轴；其运动 = Σ(MasterN.ActVelo × GearRatioN) |

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
| `InGear` | `BOOL` | 耦合建立时置 `TRUE` |
| `Busy` | `BOOL` | {DESC_BUSY} |
| `Active` | `BOOL` | {DESC_ACTIVE} |
| `CommandAborted` | `BOOL` | {DESC_ABORTED} |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorID` | `UDINT` | {DESC_ERRORID} |

## 3. 行为说明

**叠加合成**：从轴速度 / 位置 = Σ(MasterN × GearRatioN)，N = 1..4 中未被禁用的项（轴 ID ≠ 0 才参与）。

**齿比动态可调**：`Enable = TRUE` 期间可任意 GearRatioN 每周期改，FB 自动更新。

**`MC_GearOut` 与 `Enable = TRUE` 互动**：若 `MC_GearOut` 在 `Enable` 仍 TRUE 时执行，从轴短暂解耦后立刻重新耦合。要彻底解耦：先 `Enable := FALSE` 再 `MC_GearOut`。

**`Enable := FALSE` 不解耦**：与 `MC_GearInDyn` 一致——命令结束但耦合保留，齿比冻结在最后值，从轴仍跟主轴们走。

**少于 4 主**：未用的 Master 参数传"空 AXIS_REF"结构（即 NC ID 为 0）。本 FB 自动忽略 ID = 0 的主轴。

**典型工艺**：龙门双驱（左右两个 X 轴叠加成"工件 X 位置"）、张力补偿（主线辊 + 张力反馈轴叠加成实际收线速度）。

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **`Reference To AXIS_REF` 是引用语义**：传 ADR 取地址传给 FB；不能直接传 AXIS_REF 实体。例：`Master1 := ADR(axisMain1)`。
- **未用的 Master 不能传 NULL**：要传一个 AXIS_REF 实例（其轴 ID = 0 即可）；NULL pointer 会导致 PLC 异常。
- **`Enable := FALSE` 不解耦**：与 `MC_GearInDyn` 同坑。
- **齿比绝对值过大时受 `Acceleration` 限制**：从轴可能跟不上主轴瞬时变化，工艺上要预留余量。
- **不要混用同一从轴的多个耦合 FB 实例**：从轴上同时跑两个 `MC_GearInMultiMaster` 会冲突。
- **应用 `Options.AdvancedSlaveDynamics = TRUE` 可获更好动态**：但仅适用于 `MC_PhasingAbsolute/Relative` 与本 FB 配合的场景。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

```iecst
// 场景：龙门双驱机床 — 左右两个 X 轴严格同步驱动横梁，叠加后驱动一根"工件 X 虚轴"
PROGRAM P_Demo_MC_GearInMultiMaster
VAR
    fbMultiGear        : MC_GearInMultiMaster;
    axisXLeft          : AXIS_REF;
    axisXRight         : AXIS_REF;
    axisXUnused3       : AXIS_REF;
    axisXUnused4       : AXIS_REF;
    axisWorkpieceX     : AXIS_REF;
    bEnableSync        : BOOL;
    bIsCoupled         : BOOL;
    nErrorID           : UDINT;
END_VAR

fbMultiGear(
    Master1      := ADR(axisXLeft),
    Master2      := ADR(axisXRight),
    Master3      := ADR(axisXUnused3),
    Master4      := ADR(axisXUnused4),
    Enable       := bEnableSync,
    GearRatio1   := 0.5,
    GearRatio2   := 0.5,
    GearRatio3   := 0.0,
    GearRatio4   := 0.0,
    Acceleration := 1000.0,
    Deceleration := 0.0,
    Jerk         := 0.0,
    Slave        := axisWorkpieceX,
    InGear       => bIsCoupled,
    ErrorID      => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：龙门双驱（两侧 X 同步成"工件 X"）、张力补偿叠加（主辊 + 补偿辊）、多源同步馈纸、3D 打印机 H-Bot 拓扑（两电机合成一轴运动）。
- **价值**：用一个 FB 完成多主合成；不用业务侧 PID 加和。比手写"slave_target = m1 × k1 + m2 × k2"省一大圈代码。
- **替代方案对比**：
  - 自己每周期算 `slave_target := Σ Mi × ki` → `MC_MoveAbsolute`：CPU 大开销 + 相位滞后
  - 两个 `MC_GearIn` 叠加：不可能——一个从轴只能有一个耦合源
  - **本 FB**：多主合成的唯一标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.5.4
- **InfoSys topic**：{info}
- **相关 FB**：`MC_GearIn`、`MC_GearInDyn`、`MC_GearOut`、`MC_PhasingAbsolute`（叠加相位移）
"""
    body = "\n".join([
        vderived("fbMultiGear", "MC_GearInMultiMaster"),
        vderived("axisXLeft", "AXIS_REF"),
        vderived("axisXRight", "AXIS_REF"),
        vderived("axisXUnused3", "AXIS_REF"),
        vderived("axisXUnused4", "AXIS_REF"),
        vderived("axisWorkpieceX", "AXIS_REF"),
        vbool("bEnableSync", "FALSE"),
        vbool("bIsCoupled"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：龙门双驱机床 — 左右两根 X 伺服共同驱动横梁，要严格同步。把它们各
//       0.5 齿比叠加到一根"工件 X 虚轴"上，业务只读虚轴位置即可。Master3/4
//       未用，传空 AXIS_REF（ID = 0），齿比也置 0。
// 价值：用单 FB 完成多主合成，业务不需要每周期 slave_target = sum(mi*ki)。
// 验证：bEnableSync := TRUE → bIsCoupled 立 TRUE；
//       让 axisXLeft 和 axisXRight 同速跑（外部 MoveVelocity 都设 100 mm/s），
//       axisWorkpieceX.NcToPlc.ActVelo 应 = 100*0.5 + 100*0.5 = 100；
//       让两根速度差 50 → 虚轴速度 = 50*0.5 + 100*0.5 = 75。
// =============================================================================

fbMultiGear(
    Master1      := ADR(axisXLeft),
    Master2      := ADR(axisXRight),
    Master3      := ADR(axisXUnused3),
    Master4      := ADR(axisXUnused4),
    Enable       := bEnableSync,
    GearRatio1   := 0.5,
    GearRatio2   := 0.5,
    GearRatio3   := 0.0,
    GearRatio4   := 0.0,
    Acceleration := 1000.0,
    Deceleration := 0.0,
    Jerk         := 0.0,
    Slave        := axisWorkpieceX,
    InGear       =&gt; bIsCoupled,
    ErrorID      =&gt; nErrorID
);
"""
    emit("axis_coupling", name, doc, xml_skel(name, body, st))


# ---------------------------------------------------------------------------
# 6.6.1 MC_HaltPhasing — Execute / Deceleration / Jerk / BufferMode / Options
# Master + Slave VAR_IN_OUT
# Note: output is ErrorId (lowercase d) per PDF
# ---------------------------------------------------------------------------

def gen_halt_phasing():
    name = "MC_HaltPhasing"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/2217662859.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Phasing", info, name)}

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
| `Execute` | `BOOL` | — | {DESC_EXECUTE} |
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
| `Busy` | `BOOL` | {DESC_BUSY} |
| `Active` | `BOOL` | {DESC_ACTIVE} |
| `CommandAborted` | `BOOL` | {DESC_ABORTED} |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorId` | `UDINT` | {DESC_ERRORID} |

## 3. 行为说明

**触发**：`Execute` 上升沿启动减速；相位调整的"叠加速度"按 `Deceleration` + `Jerk` 平滑降为 0，此后从轴继续跟主轴但不再有相位调整位移。

**与 `MC_AbortSuperposition` 关系**：相位调整本质是一种特殊的叠加运动，但 `MC_HaltPhasing` 提供**可控减速曲线**，而 `MC_AbortSuperposition` 是瞬时中止。要平滑停"相位调整"用本 FB；要立刻中止用 `MC_AbortSuperposition`。

**`BufferMode` 仅支持 `Aborting`**：相位停车是抢占式动作，不能排队。

**已建立的相位差保留**：与 `MC_AbortSuperposition` 一样，已经走过的相位差**永久保留**，本 FB 只是停止后续相位调整。

**从轴耦合状态不变**：本 FB 只针对相位调整运动；从轴的 GearIn / CamIn 耦合关系不被本 FB 解开。

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **只停相位调整，不停从轴**：从轴在耦合下继续跟主轴跑；要停从轴需后续接 `MC_GearOut` + `MC_Halt`。
- **`BufferMode` 只能 `Aborting`**：填别的报错。
- **已建立的相位差保留**：要把相位还原需反向再调一次 `MC_PhasingRelative(PhaseShift := -shift)`。
- **`Options` 未实现**：填了没用。
- **没有相位调整运行时调用 `Error := TRUE`**：先确认相位 FB 在 Busy 状态再触发本 FB。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

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
    ErrorID      => nErrorID
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

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.6.1
- **InfoSys topic**：{info}
- **相关 FB**：`MC_PhasingAbsolute`、`MC_PhasingRelative`、`MC_AbortSuperposition`
"""
    body = "\n".join([
        vderived("fbStopPhasing", "MC_HaltPhasing"),
        vderived("axisMaster", "AXIS_REF"),
        vderived("axisColorPlate", "AXIS_REF"),
        vderived("rtStopTrig", "R_TRIG"),
        vbool("bRequestStop", "FALSE"),
        vbool("bStopDone"),
        vbool("bStopBusy"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：套色印刷启动相位调整后业务发现参数算错，需要让色版从轴的"相位调整
//       速度"按 Jerk-limited 曲线平稳归零，避免色版瞬时抖动印废品。
// 价值：相对 MC_AbortSuperposition 的瞬时中止，本 FB 给可控减速曲线工艺平顺；
//       从轴耦合关系保留，主运动继续推进。
// 验证：先用 MC_PhasingRelative 启动相位调整（外部 demo 假设已启动）；
//       bRequestStop := TRUE → bStopBusy 立 TRUE；从轴叠加速度按 1000 mm/s²
//       减速降到 0，bStopDone 短暂 TRUE；从轴仍按之前齿比跟主轴走。
// =============================================================================

rtStopTrig(CLK := bRequestStop);

fbStopPhasing(
    Execute      := rtStopTrig.Q,
    Deceleration := 1000.0,
    Jerk         := 10000.0,
    BufferMode   := MC_Aborting,
    Master       := axisMaster,
    Slave        := axisColorPlate,
    Done         =&gt; bStopDone,
    Busy         =&gt; bStopBusy,
    ErrorID      =&gt; nErrorID
);
"""
    emit("phasing", name, doc, xml_skel(name, body, st))


# ---------------------------------------------------------------------------
# 6.6.2 MC_PhasingAbsolute
# ---------------------------------------------------------------------------

def gen_phasing_absolute():
    name = "MC_PhasingAbsolute"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/2217664779.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Phasing", info, name)}

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
| `Execute` | `BOOL` | — | {DESC_EXECUTE} |
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
| `Busy` | `BOOL` | {DESC_BUSY} |
| `Active` | `BOOL` | {DESC_ACTIVE} |
| `CommandAborted` | `BOOL` | {DESC_ABORTED} |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorId` | `UDINT` | {DESC_ERRORID} |
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

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **耦合必须已建立**：本 FB 不建立耦合，只调整已有耦合的相位差。先调 `MC_GearIn` / `MC_CamIn_V2` 再调本 FB。
- **不支持 `MC_GearInDyn`**：PDF 明确；若用 GearInDyn 的耦合要做相位调整请用 `MC_GearInMultiMaster(AdvancedSlaveDynamics=TRUE)` 替代。
- **`Velocity < 0.01` 报错**：极小值要小心。
- **`BufferMode` 只能 Aborting**。
- **`Options` 未实现**。
- **改相位时主轴动着 vs 静着**：主轴动时设定相位差是动态目标（"差始终保持 5°"）；主轴静止时设定的相位差是一次性 offset。
- **`Jerk` 同时作用加减速段**：标准 PLCopen FB 加减速段 Jerk 可不同，本 FB 强制一致。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

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
    ErrorID            => nErrorID
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

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.6.2
- **InfoSys topic**：{info}
- **相关 FB**：`MC_PhasingRelative`、`MC_HaltPhasing`、`MC_MoveSuperImposed`
"""
    body = "\n".join([
        vderived("fbSetPhase", "MC_PhasingAbsolute"),
        vderived("axisMainRoller", "AXIS_REF"),
        vderived("axisColorPlate", "AXIS_REF"),
        vderived("rtSetTrig", "R_TRIG"),
        vbool("bApplyPhase", "FALSE"),
        vlreal("lrTargetPhaseDeg", "5.0"),
        vbool("bPhaseDone"),
        vlreal("lrActualPhase"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：印刷机色版需相对主辊设定 5° 的绝对相位差以套色对齐。前序已经用
//       MC_GearIn 把色版从轴耦合到主辊（demo 假设耦合已建立），本 FB 在耦
//       合基础上调整绝对相位。
// 价值：相位差作参数直接给，FB 自动规划 Jerk-limited 调整曲线；ContinuousUpdate
//       = TRUE 允许调整过程中再改目标。
// 验证：bApplyPhase := TRUE → bPhaseDone 在 ~ 0.5 s 后置 TRUE；
//       lrActualPhase 应 ≈ 5.0；
//       此时让 axisMainRoller 速度变化，axisColorPlate 应始终保持 5° 领先（不掉相）。
// =============================================================================

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
    Done               =&gt; bPhaseDone,
    AbsolutePhaseShift =&gt; lrActualPhase,
    ErrorID            =&gt; nErrorID
);
"""
    emit("phasing", name, doc, xml_skel(name, body, st))


# ---------------------------------------------------------------------------
# 6.6.3 MC_PhasingRelative — similar to PhasingAbsolute, outputs CoveredPhaseShift
# ---------------------------------------------------------------------------

def gen_phasing_relative():
    name = "MC_PhasingRelative"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/2250456587.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Phasing", info, name)}

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
| `Execute` | `BOOL` | — | {DESC_EXECUTE} |
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
| `Busy` | `BOOL` | {DESC_BUSY} |
| `Active` | `BOOL` | {DESC_ACTIVE} |
| `CommandAborted` | `BOOL` | {DESC_ABORTED} |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorId` | `UDINT` | {DESC_ERRORID} |
| `CoveredPhaseShift` | `LREAL` | 系统实际叠加的相位增量（可能因夹紧与请求略异） |

## 3. 行为说明

**触发**：`Execute` 上升沿启动相位增量叠加；当前相位差再加上 `PhaseShift`。例如当前差 5°，本 FB `PhaseShift := 3` 启动 → 完成后差 8°。

**与绝对版区别**：本 FB 叠加增量，绝对版设置目标。相对版适合"每次套准检测算出微小偏差后再调一点"。

**`ContinuousUpdate` 行为**：与绝对版一致——上升沿采样，TRUE 时参数动态可改。

**多次叠加**：每次相对调整都在前一次结果上累加；要"回到初始相位"需反向 `PhaseShift := -coverage_so_far`。

**`MC_GearInDyn` 不支持**：与绝对版一致。

**`CoveredPhaseShift` 反馈**：系统实际叠加的量；正常等于 `PhaseShift`，但如有夹紧 / 错误中止会与请求值不一致。

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **每次叠加都累积**：多次调用本 FB 相位差不断累加；要还原必须反向调用。
- **耦合必须已建立**：本 FB 不建立耦合。
- **不支持 `MC_GearInDyn`**：同绝对版。
- **`BufferMode` 仅 Aborting**：填别的报错。
- **`Velocity ≥ 0.01`**：太小报错。
- **`Jerk` 同时作用加减速段**：与绝对版一致。
- **被 `MC_HaltPhasing` 中止后 `CoveredPhaseShift` 反映已走的部分**：例如要叠 10°，走到 6° 被 Halt → `CoveredPhaseShift ≈ 6`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

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
    ErrorID           => nErrorID
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

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.6.3
- **InfoSys topic**：{info}
- **相关 FB**：`MC_PhasingAbsolute`、`MC_HaltPhasing`、`MC_MoveSuperImposed`
"""
    body = "\n".join([
        vderived("fbAddPhase", "MC_PhasingRelative"),
        vderived("axisMainRoller", "AXIS_REF"),
        vderived("axisColorPlate", "AXIS_REF"),
        vderived("rtCorrectTrig", "R_TRIG"),
        vbool("bRunCorrection", "FALSE"),
        vlreal("lrPhaseErrorDeg", "0.2"),
        vbool("bCorrectionDone"),
        vlreal("lrCoveredPhase"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：套准闭环 — 视觉相机每秒反馈一个小相位偏差（如 +0.2°），用相对相位
//       调整 FB 把这个增量叠加到色版从轴上。多次调用累积修正。
// 价值：业务不用维护"当前总相位偏差"全局变量，FB 自动累加；适合做相位的
//       闭环 PID 直接输出。
// 验证：先确认主从耦合已建立（外部 MC_GearIn 已运行）；
//       bRunCorrection := TRUE 一次 → bCorrectionDone 在 ~ 0.1 s 后 TRUE，
//       lrCoveredPhase ≈ 0.2。多次触发可看到相位差累积（视觉系统反馈应回零）。
// =============================================================================

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
    Done              =&gt; bCorrectionDone,
    CoveredPhaseShift =&gt; lrCoveredPhase,
    ErrorID           =&gt; nErrorID
);
"""
    emit("phasing", name, doc, xml_skel(name, body, st))


# ---------------------------------------------------------------------------
# 6.7.1 MC_TorqueControl
# ---------------------------------------------------------------------------

def gen_torque_control():
    name = "MC_TorqueControl"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/7617393803.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Torque Control", info, name)}

## 1. 功能简述

PLCopen 标准定义的**力矩控制 FB**。把 NC 下的轴切换到 **CST（Cyclic Synchronous Torque）模式**并给定力矩设定值。这种模式下 NC 不再以位置 / 速度环为主，而是把驱动器直接置于"恒力矩输出"状态——典型应用是张力控制、压紧机构、扭矩限制工艺。

`VelocityLimitHigh` 和 `VelocityLimitLow` 通过 NC 循环接口（`Axis->Drive->Outputs->nDataOut5/nDataOut6`）传给驱动器，由驱动器在力矩模式下限制速度上下限避免飞车。

**⚠️ 危险**：使用本 FB 后轴可能仍处于 CST 模式；再次使能时（特别是垂直轴）可能突然下坠或冲撞。PDF 中以 DANGER 警示——使用后必须显式切换回 CSV/CSP 模式。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute            : BOOL;
    ContinuousUpdate   : BOOL;
    Relative           : BOOL;
    Torque             : LREAL;
    TorqueRamp         : LREAL;
    VelocityLimitHigh  : LREAL;
    VelocityLimitLow   : LREAL;
    BufferMode         : MC_BufferMode;
    Options            : ST_TorqueControlOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | {DESC_EXECUTE} |
| `ContinuousUpdate` | `BOOL` | — | 上升沿时若 TRUE：命令执行期间改 `Torque` / `TorqueRamp` 等参数会尽快生效，适合做力矩闭环 |
| `Relative` | `BOOL` | — | `FALSE` = `Torque` 是绝对力矩设定值；`TRUE` = 在当前力矩上叠加 |
| `Torque` | `LREAL` | — | 力矩设定值（单位取决于驱动器配置，典型为 Nm 或额定力矩百分比） |
| `TorqueRamp` | `LREAL` | — | 力矩斜坡，限制力矩瞬时跳变避免机械冲击 |
| `VelocityLimitHigh` | `LREAL` | — | CST 模式下的速度上限（正方向） |
| `VelocityLimitLow` | `LREAL` | — | CST 模式下的速度下限（负方向，typically 负值） |
| `BufferMode` | `MC_BufferMode` | — | {DESC_BUFFER} |
| `Options` | `ST_TorqueControlOptions` | — | 扩展选项 |

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
    InTorque           : BOOL;
    Busy               : BOOL;
    Active             : BOOL;
    CommandAborted     : BOOL;
    Error              : BOOL;
    ErrorID            : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `InTorque` | `BOOL` | 力矩设定值已达到时置 `TRUE`（速度限制下） |
| `Busy` | `BOOL` | {DESC_BUSY} |
| `Active` | `BOOL` | {DESC_ACTIVE} |
| `CommandAborted` | `BOOL` | {DESC_ABORTED} |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorID` | `UDINT` | {DESC_ERRORID} |

## 3. 行为说明

**触发**：`Execute` 上升沿启动。NC 把驱动器切换到 **CST（Cyclic Synchronous Torque）模式**，并按 `TorqueRamp` 斜率把力矩设定值从 0 拉到 `Torque`。`VelocityLimitHigh / Low` 限制速度避免飞车。

**支持的 Beckhoff 硬件**：
- AX5xxx：FW v2.14 b0001 起
- AX8xxx / AMP8xxx / MD8xxx：FW v1.05 b0001 起
- Compact drive（伺服，含 ELM72xx 和 AMI8xxx）：FW v01 起

**驱动器需支持运动模式动态切换**：CSP/CSV ↔ CST 切换；不是所有伺服都支持，使用前查驱动器手册。

**死区时间补偿**：要无冲击切换模式必须**激活 NC 轴的死区时间补偿**（dead time compensation），否则切换瞬间会有抖动。

**关闭力矩控制**：撤 `Execute` 不会自动切回 CSP/CSV，必须显式：
1. 用 `MC_ReadDriveOperationMode` 检查当前模式
2. 若不在位置相关模式（CSV/CSP）则用 `MC_WriteDriveOperationMode` 直接切回，或用 `MC_Halt` / `MC_Stop`（TwinCAT 3.1.4024.40+）间接切回
3. 再次检查模式确保切回成功；否则中止并报错

⚠️ **垂直轴 / 起吊轴特别警告**：CST 模式下使能瞬间力矩可能不足以维持重量 → 轴下坠。**必须经过风险评估后才允许使用**。

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **⚠️ 模式切换不会自动还原**：撤 `Execute` 后轴可能仍在 CST，再使能可能突然动。**必须显式切回 CSV/CSP**。
- **垂直轴使用前先评估风险**：CST 模式下重力可能让轴下坠，机械结构必须能承受或加入抱闸。
- **驱动器固件版本要够**：见上面硬件支持表；旧固件不支持 CST 模式切换。
- **死区时间补偿必开**：否则模式切换瞬间抖动剧烈。
- **`VelocityLimitLow` 通常为负值**：限制负方向速度；写正值会让限制无效。
- **力矩单位看驱动器**：有的伺服用 Nm，有的用额定力矩百分比；调试时先用小值验证。
- **`ContinuousUpdate := TRUE` 适合力矩闭环**：例如张力 PID 输出连续改 `Torque`；`FALSE` 适合一次性设定后不变。
- **`BufferMode` 行为**：与其它 MC FB 一致，但 PDF 没特别提，建议先用 `MC_Aborting`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

```iecst
// 场景：卷绕机张力控制 — 收线轴以恒定 35 Nm 力矩拉紧线材，速度限在 ±500 rpm
PROGRAM P_Demo_MC_TorqueControl
VAR
    fbTensionCtrl    : MC_TorqueControl;
    axisTensionRoll  : AXIS_REF;
    bEnableTension   : BOOL;
    lrTorqueSetNm    : LREAL := 35.0;
    bAtTorque        : BOOL;
    bCtrlBusy        : BOOL;
    bCtrlError       : BOOL;
    nErrorID         : UDINT;
END_VAR

fbTensionCtrl(
    Execute           := bEnableTension,
    ContinuousUpdate  := TRUE,
    Relative          := FALSE,
    Torque            := lrTorqueSetNm,
    TorqueRamp        := 10.0,
    VelocityLimitHigh := 400.0,
    VelocityLimitLow  := -500.0,
    BufferMode        := MC_Aborting,
    Axis              := axisTensionRoll,
    InTorque          => bAtTorque,
    Busy              => bCtrlBusy,
    Error             => bCtrlError,
    ErrorID           => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：卷绕机收线/放线张力控制、压紧机构（夹具按恒力夹紧工件）、扭矩限制工艺（拧螺丝到指定扭矩）、惯量补偿。共同特征：**力矩是控制目标，速度只是约束**。
- **价值**：把 NC + 驱动器固件级的模式切换 + 力矩闭环 + 速度限制封装为一个 FB；不用业务侧自己写 SDO 写驱动器对象字典。
- **替代方案对比**：
  - 直接 SDO 切换驱动器 modes_of_operation：要熟悉 CiA402 状态机，且 PLC 周期内可能出 timing 问题
  - 用 `MC_WriteDriveOperationMode` + 自己写力矩设定值：分两步比本 FB 麻烦
  - **本 FB**：力矩控制的标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.7.1
- **InfoSys topic**：{info}
- **相关 FB**：`MC_ReadDriveOperationMode`、`MC_WriteDriveOperationMode`、`MC_Halt` / `MC_Stop`（用于切回 CSV/CSP）、`ST_TorqueControlOptions`
"""
    body = "\n".join([
        vderived("fbTensionCtrl", "MC_TorqueControl"),
        vderived("axisTensionRoll", "AXIS_REF"),
        vbool("bEnableTension", "FALSE", "在线 TRUE 启用张力控制；FALSE 后必须切回 CSV/CSP 模式"),
        vlreal("lrTorqueSetNm", "35.0", "力矩设定值 (Nm 或额定百分比，取决于驱动器)"),
        vbool("bAtTorque"),
        vbool("bCtrlBusy"),
        vbool("bCtrlError"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：卷绕机收线轴张力控制 — 用 35 Nm 恒力矩拉紧线材让线张力恒定，速度
//       限制在 -500..+400 rpm 避免飞车。当线径变化导致负载变时 NC 自动调整
//       速度以维持力矩。
// 价值：把 NC + 驱动器固件级的 CST 模式切换 + 力矩斜坡 + 速度限制封装为一
//       个 FB；业务不用自己写 SDO 切驱动器对象字典。
// 验证：先 MC_Power 使能 axisTensionRoll；bEnableTension := TRUE → bAtTorque
//       在力矩斜坡完成后 TRUE。在线观察 axisTensionRoll.NcToPlc.ActTorque ≈ 35。
//       ⚠️ 使用后必须显式调 MC_WriteDriveOperationMode 切回 CSV/CSP，否则下次
//       使能轴可能突然动（垂直轴会下坠）。
// =============================================================================

fbTensionCtrl(
    Execute           := bEnableTension,
    ContinuousUpdate  := TRUE,
    Relative          := FALSE,
    Torque            := lrTorqueSetNm,
    TorqueRamp        := 10.0,
    VelocityLimitHigh := 400.0,
    VelocityLimitLow  := -500.0,
    BufferMode        := MC_Aborting,
    Axis              := axisTensionRoll,
    InTorque          =&gt; bAtTorque,
    Busy              =&gt; bCtrlBusy,
    Error             =&gt; bCtrlError,
    ErrorID           =&gt; nErrorID
);
"""
    emit("torque_control", name, doc, xml_skel(name, body, st))


if __name__ == "__main__":
    gen_gear_in_dyn()
    gen_gear_out()
    gen_gear_in_multimaster()
    gen_halt_phasing()
    gen_phasing_absolute()
    gen_phasing_relative()
    gen_torque_control()
    print("batch 4 done — all 22 emitted")
