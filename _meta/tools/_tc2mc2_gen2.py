#!/usr/bin/env python3
"""Generator for Tc2_MC2 docs + examples — batch 2 (remaining 18).

Imports helpers from _tc2mc2_gen and adds emit functions for:
  point_to_point_motion: MC_MoveModulo, MC_MoveVelocity, MC_MoveContinuousAbsolute,
                          MC_MoveContinuousRelative, MC_Halt, MC_Stop
  superposition:          MC_MoveSuperImposed, MC_AbortSuperposition
  homing:                 MC_Home
  manual_motion:          MC_Jog
  axis_coupling:          MC_GearIn, MC_GearInDyn, MC_GearOut, MC_GearInMultiMaster
  phasing:                MC_HaltPhasing, MC_PhasingAbsolute, MC_PhasingRelative
  torque_control:         MC_TorqueControl
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
# MC_MoveModulo (6.1.4) — adds Direction input
# ---------------------------------------------------------------------------

def gen_move_modulo():
    name = "MC_MoveModulo"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70099339.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Point to point motion", info, name)}

## 1. 功能简述

PLCopen 标准定义的**模数轴定位 FB**。专为旋转/无限循环轴设计，参数 `Position` 被解释为**模数坐标系**下的目标位置（例如 0~360°，由轴参数中"模数因子"决定）。

通过 `Direction` 输入选择三种走法：正向（`MC_Positive_Direction`）、反向（`MC_Negative_Direction`）、最短路径（`MC_ShortestWay`）。轴静止时若 `Position ≥ 360°` 会**多转几圈**再到位；轴运动中触发时圈数由系统自动算成最短路径。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Position     : LREAL;
    Velocity     : LREAL;
    Acceleration : LREAL;
    Deceleration : LREAL;
    Jerk         : LREAL;
    Direction    : MC_Direction;
    BufferMode   : MC_BufferMode;
    Options      : ST_MoveOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | {DESC_EXECUTE} |
| `Position` | `LREAL` | — | 模数目标位置；从静止启动时 `>360°` 表示再多转圈数；不允许负值 |
| `Velocity` | `LREAL` | — | {DESC_VELOCITY} |
| `Acceleration` | `LREAL` | — | {DESC_ACC} |
| `Deceleration` | `LREAL` | — | {DESC_DEC} |
| `Jerk` | `LREAL` | — | {DESC_JERK} |
| `Direction` | `MC_Direction` | — | 行进方向：`MC_Positive_Direction` / `MC_Negative_Direction` / `MC_ShortestWay`；运动中触发不允许换向 |
| `BufferMode` | `MC_BufferMode` | — | {DESC_BUFFER} |
| `Options` | `ST_MoveOptions` | — | {DESC_OPTIONS} |

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
| `Done` | `BOOL` | {DESC_DONE} |
| `Busy` | `BOOL` | {DESC_BUSY} |
| `Active` | `BOOL` | {DESC_ACTIVE} |
| `CommandAborted` | `BOOL` | {DESC_ABORTED} |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorID` | `UDINT` | {DESC_ERRORID} |

## 3. 行为说明

**触发**：`Execute` 上升沿启动模数定位。模数因子（如 360°）来自轴参数 → 模数设置。

**静止启动**：`Position` 可以 ≥ 360°；例如轴在 0°，`Position := 720`、`Direction := MC_Positive_Direction` 会让轴正向转 2 圈到 0°。`BufferMode := MC_Buffered` 时同样适用。

**运动中启动**：圈数由系统按"最短路径"自动算，**用户无法指定额外圈数**。需要评估 `Error`，因为某些情况下"定向停车（oriented stop）"无法完成：例如不久前发了 standard stop，或软限位在路径上。这类情况下轴被安全停下但**最终位置不一定是目标位置**。

**特殊情形**：轴正好停在设定的目标处（如 90°）再发"到 90°"，**不会有任何运动**；若发"正方向走 450°"则只转一圈到 90°。`MC_Reset` 后当前实际位置被采纳为设定位置，可能略偏 90°——这时再发同样命令行为会突变（要么微动到 90°，要么转一整圈）。

**与 `MC_MoveAbsolute` 抉择**：完整模数旋转（精确转 N 圈）建议算出绝对目标位置后用 `MC_MoveAbsolute`，行为更可预测。

**模数/绝对定位与 System Manager 设置无关**：每根轴都可用绝对/模数两种定位，取决于业务调用哪个 FB；当前绝对位置 `SetPos` 可从 `NCTOPLC_AXIS_REF` 循环数据读出。

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **`Position` 不许负**：模数语义里不存在负角度；要反向请用 `Direction := MC_Negative_Direction`。
- **运动中改向不允许**：轴正在沿正方向走，触发新命令 `Direction := MC_Negative_Direction` 会报错。
- **`MC_ShortestWay` 实际方向不确定**：若起点和终点角度差恰好 180°，"最短"可能取正可能取负，依赖浮点；机械有方向偏好的应固定 `Positive` 或 `Negative`。
- **轴位置恰好等于目标位置 = 不动**：自动化场景里"每周期触发一次走到 X 度"在 X 与当前位完全相同时变成 NOP，常导致"看 Busy 一直没起来"的诡异现象。（工程经验补充）
- **`MC_Reset` 重新采纳实际位置后行为突变**：见 §3 末段；生产工艺对位置精度敏感时应在 Reset 后先做一次 `MC_Home` 或绝对定位再走模数。
- **要精确"转 N 圈"建议用 `MC_MoveAbsolute`**：算出 currentPos + 360°×N 给绝对定位，避免运动中触发被系统改成最短路径。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

```iecst
// 场景：分度盘工位旋转 — 每个生产节拍把工件旋转到下一工位（90°），始终取最短路径
PROGRAM P_Demo_MC_MoveModulo
VAR
    fbIndexRotate     : MC_MoveModulo;
    axisIndexTable    : AXIS_REF;
    rtNextStation     : R_TRIG;
    bAdvanceStation   : BOOL;
    lrNextStationDeg  : LREAL := 90.0;
    bRotateDone       : BOOL;
    nErrorID          : UDINT;
END_VAR

rtNextStation(CLK := bAdvanceStation);
fbIndexRotate(
    Execute      := rtNextStation.Q,
    Position     := lrNextStationDeg,
    Velocity     := 180.0,
    Acceleration := 360.0,
    Deceleration := 360.0,
    Jerk         := 3600.0,
    Direction    := MC_Positive_Direction,
    BufferMode   := MC_Aborting,
    Axis         := axisIndexTable,
    Done         => bRotateDone,
    ErrorID      => nErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：分度盘工位切换、转盘式装配机、车铣复合的 C 轴定向、旋转刀库换刀、激光打标转台。共同点：**模数旋转**（如 0~360°），且工艺有"下一工位"语义而非"再走多少度"。
- **价值**：业务给"目标角度"+"方向"两个量，FB 自动处理 360° 折回 / 多圈 / 最短路径；不会出现 `MC_MoveRelative` 那种"走 360° 等于回原点 = 0 度"的迷惑结果。
- **替代方案对比**：
  - 用 `MC_MoveAbsolute` 算"现位 + 角度差"：要业务自己处理 ±360° 跨界，容易出 bug
  - 用 `MC_MoveRelative`：连续多次相对累计漂移
  - **本 FB**：模数语义直接，是分度类设备的首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.1.4
- **InfoSys topic**：{info}
- **相关 FB**：`MC_MoveAbsolute`、`MC_MoveRelative`、`MC_MoveVelocity`
"""
    body = "\n".join([
        vderived("fbIndexRotate", "MC_MoveModulo"),
        vderived("axisIndexTable", "AXIS_REF"),
        vderived("rtNextStation", "R_TRIG"),
        vbool("bAdvanceStation", "FALSE", "在线 TRUE 一次 = 转到下一工位"),
        vlreal("lrNextStationDeg", "90.0", "下一工位的模数目标角度"),
        vbool("bRotateDone"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：4 工位分度盘 — 每按一次"下一工位"按钮，转台正向转 90° 到下一工位。
// 价值：模数 FB 处理角度 wrap，业务不用算"现位 + 90 是否过 360"。
// 验证：登录后 bAdvanceStation := TRUE 一次 → 角度 0→90；再触发 90→180；
//       连续 4 次回到 0；将 lrNextStationDeg 改为 720 看到转 2 圈再到位。
// =============================================================================

rtNextStation(CLK := bAdvanceStation);

fbIndexRotate(
    Execute      := rtNextStation.Q,
    Position     := lrNextStationDeg,
    Velocity     := 180.0,
    Acceleration := 360.0,
    Deceleration := 360.0,
    Jerk         := 3600.0,
    Direction    := MC_Positive_Direction,
    BufferMode   := MC_Aborting,
    Axis         := axisIndexTable,
    Done         =&gt; bRotateDone,
    ErrorID      =&gt; nErrorID
);
"""
    emit("point_to_point_motion", name, doc, xml_skel(name, body, st))


# ---------------------------------------------------------------------------
# MC_MoveVelocity (6.1.6)
# ---------------------------------------------------------------------------

def gen_move_velocity():
    name = "MC_MoveVelocity"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70102411.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Point to point motion", info, name)}

## 1. 功能简述

PLCopen 标准定义的**恒速无限行进 FB**。`Execute` 上升沿启动一段无终点的运动：先按加速度爬升到 `Velocity`，到达后 `InVelocity := TRUE`，**FB 任务即结束**——之后 NC 继续以恒速运行不再监视。要停轴需另外调用 `MC_Stop` / `MC_Halt`。

加速段中被另一个命令抢占 → `CommandAborted := TRUE`；硬件/参数错误 → `Error := TRUE`。注意没有 `Done` 输出，只有 `InVelocity`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Velocity     : LREAL;
    Acceleration : LREAL;
    Deceleration : LREAL;
    Jerk         : LREAL;
    Direction    : MC_Direction := MC_Positive_Direction;
    BufferMode   : MC_BufferMode;
    Options      : ST_MoveOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | {DESC_EXECUTE} |
| `Velocity` | `LREAL` | — | 目标行进速度，`>0` |
| `Acceleration` | `LREAL` | — | {DESC_ACC} |
| `Deceleration` | `LREAL` | — | {DESC_DEC} |
| `Jerk` | `LREAL` | — | {DESC_JERK} |
| `Direction` | `MC_Direction` | `MC_Positive_Direction` | 行进方向 |
| `BufferMode` | `MC_BufferMode` | — | {DESC_BUFFER} |
| `Options` | `ST_MoveOptions` | — | {DESC_OPTIONS} |

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
    InVelocity     : BOOL;
    Busy           : BOOL;
    Active         : BOOL;
    CommandAborted : BOOL;
    Error          : BOOL;
    ErrorID        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `InVelocity` | `BOOL` | 达到目标恒速时置 `TRUE`；之后本 FB 不再监视轴 |
| `Busy` | `BOOL` | {DESC_BUSY} |
| `Active` | `BOOL` | {DESC_ACTIVE} |
| `CommandAborted` | `BOOL` | {DESC_ABORTED} |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorID` | `UDINT` | {DESC_ERRORID} |

## 3. 行为说明

**触发**：`Execute` 上升沿启动恒速运动。`InVelocity = TRUE` 之后 FB 完成自身职责，**不再持续监视轴**——这是与 `MC_MoveAbsolute` 等位置类 FB 最大的区别。轴会按 NC 设定一直走，直到收到下一条命令（典型是 `MC_Stop` / `MC_Halt`）。

**状态机分支**：
- 正常：加速段完成 → `InVelocity = TRUE`、`Busy = FALSE`、`Active = FALSE`（FB 退出"忙"态）
- 加速段被抢：另一条命令切入 → `CommandAborted = TRUE`、`InVelocity` 不会被置位
- 出错：参数越界等 → `Error = TRUE`、`ErrorID` 给码

**典型场景**：传送带恒速运行、卷绕收放线速度跟随、风机/泵恒速运转。所有"有起点没终点"的运动都用本 FB。

**易踩坑**：达到恒速后 `Busy = FALSE`，看似 FB "完成了"，但**轴还在动**。新手把"Busy 灭"当成"运动结束"会出事。要停轴必须显式调 `MC_Stop` / `MC_Halt`。

**耦合从轴特例**：与其它 P2P FB 一致，会先自动解耦再执行恒速运动，且只能 `MC_Aborting`。

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **没有 Done 输出**：用 `InVelocity` 判断"已达速度"；判断"轴已停"要靠 `Axis.NcToPlc.ActVelo ≈ 0` 或自己跟踪后续 `MC_Stop` 的 `Done`。
- **`Velocity := 0` 报错**：禁用此 FB 停轴的写法，要停用 `MC_Halt`。
- **`Direction` 必填**：默认 `MC_Positive_Direction`，但工业代码建议显式给值避免误读。
- **`InVelocity` 灭 ≠ 停轴**：加速完达到恒速后 `InVelocity = TRUE` 一直保持直到本 FB 被覆盖；轴恒速运行期间 `InVelocity` 不会自动灭。
- **`Busy = FALSE` 时还在跑**：见 §3。要持续监视应跟踪 `Axis.NcToPlc.ActVelo` 而不是本 FB 输出。
- **耦合从轴行为**：从轴上发 `MC_MoveVelocity` 自动解耦，要再耦合需重新 `MC_GearIn`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

```iecst
// 场景：传送带启动后恒速 1.5 m/s 运行；点 bStartConveyor 启动，点 bStopConveyor 停
PROGRAM P_Demo_MC_MoveVelocity
VAR
    fbConveyorRun     : MC_MoveVelocity;
    fbConveyorHalt    : MC_Halt;
    axisConveyor      : AXIS_REF;
    rtStartTrig       : R_TRIG;
    rtStopTrig        : R_TRIG;
    bStartConveyor    : BOOL;
    bStopConveyor     : BOOL;
    lrLineSpeedMMpS   : LREAL := 1500.0;
    bAtSpeed          : BOOL;
    bRunBusy          : BOOL;
    bHaltDone         : BOOL;
    nRunErrorID       : UDINT;
END_VAR

rtStartTrig(CLK := bStartConveyor);
rtStopTrig(CLK := bStopConveyor);

fbConveyorRun(
    Execute      := rtStartTrig.Q,
    Velocity     := lrLineSpeedMMpS,
    Acceleration := 2000.0,
    Deceleration := 2000.0,
    Jerk         := 20000.0,
    Direction    := MC_Positive_Direction,
    BufferMode   := MC_Aborting,
    Axis         := axisConveyor,
    InVelocity   => bAtSpeed,
    Busy         => bRunBusy,
    ErrorID      => nRunErrorID
);

fbConveyorHalt(
    Execute      := rtStopTrig.Q,
    Deceleration := 2000.0,
    Jerk         := 20000.0,
    BufferMode   := MC_Aborting,
    Axis         := axisConveyor,
    Done         => bHaltDone
);
```

## 7. 业务场景与实际价值

- **场景**：传送带、卷绕收放、贴标机滚筒、印刷机版辊、风扇/泵恒速运转。所有"开起来恒速跑、停由外部触发"的设备都属这一类。
- **价值**：FB 自动处理加速段 S 曲线、达到恒速后即"放手"让 NC 维持；停轴用配套的 `MC_Halt` / `MC_Stop`，分工明确。比写定时器 + 速度环手动控制省 30+ 行代码。
- **替代方案对比**：
  - 直接给 NC 通道速度命令：要拼 `MC_DIRECTVELOCITY` 控制字
  - 用 `MC_MoveAbsolute(Position := very_large_number)`：勉强能跑但行程有限且不符合"无终点"语义
  - **本 FB**：恒速运动的标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.1.6
- **InfoSys topic**：{info}
- **相关 FB**：`MC_Halt`、`MC_Stop`（停轴）、`MC_MoveContinuousAbsolute`（带终点的恒速变体）
"""
    body = "\n".join([
        vderived("fbConveyorRun", "MC_MoveVelocity"),
        vderived("fbConveyorHalt", "MC_Halt"),
        vderived("axisConveyor", "AXIS_REF"),
        vderived("rtStartTrig", "R_TRIG"),
        vderived("rtStopTrig", "R_TRIG"),
        vbool("bStartConveyor", "FALSE", "在线 TRUE 启动传送带"),
        vbool("bStopConveyor", "FALSE", "在线 TRUE 平稳停止传送带"),
        vlreal("lrLineSpeedMMpS", "1500.0", "传送带线速度 mm/s"),
        vbool("bAtSpeed"),
        vbool("bRunBusy"),
        vbool("bHaltDone"),
        vudint("nRunErrorID"),
    ])
    st = """// =============================================================================
// 场景：包装线主传送带 — 启动后恒速 1.5 m/s 运行直到 PLC 发停车指令。
//       MoveVelocity 负责加速到目标速度，Halt 负责停车，分工明确。
// 价值：达到恒速后 FB 自动"放手"，NC 维持速度无需 PLC 持续干预。
// 验证：bStartConveyor := TRUE → 看 axisConveyor.NcToPlc.ActVelo 爬升到 1500，
//       bAtSpeed 置 TRUE。bStopConveyor := TRUE → 减速到 0，bHaltDone 短暂 TRUE。
// =============================================================================

rtStartTrig(CLK := bStartConveyor);
rtStopTrig(CLK := bStopConveyor);

fbConveyorRun(
    Execute      := rtStartTrig.Q,
    Velocity     := lrLineSpeedMMpS,
    Acceleration := 2000.0,
    Deceleration := 2000.0,
    Jerk         := 20000.0,
    Direction    := MC_Positive_Direction,
    BufferMode   := MC_Aborting,
    Axis         := axisConveyor,
    InVelocity   =&gt; bAtSpeed,
    Busy         =&gt; bRunBusy,
    ErrorID      =&gt; nRunErrorID
);

fbConveyorHalt(
    Execute      := rtStopTrig.Q,
    Deceleration := 2000.0,
    Jerk         := 20000.0,
    BufferMode   := MC_Aborting,
    Axis         := axisConveyor,
    Done         =&gt; bHaltDone
);
"""
    emit("point_to_point_motion", name, doc, xml_skel(name, body, st))


# ---------------------------------------------------------------------------
# MC_MoveContinuousAbsolute (6.1.7) — Position + EndVelocity
# ---------------------------------------------------------------------------

def gen_move_continuous_absolute():
    name = "MC_MoveContinuousAbsolute"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70103947.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Point to point motion", info, name)}

## 1. 功能简述

PLCopen 标准定义的**带终末速度的绝对定位 FB**。轴沿整段轨迹监视，到达 `Position` 时**不停车，而是保持 `EndVelocity` 继续走**——`InEndVelocity := TRUE` 标志到达目标位置且已达到终末速度。

目标位置到达后 FB 任务结束，轴不再被本 FB 监视；后续要做什么完全由业务下一条命令决定（典型搭配是 `MC_Halt` 或另一条 `MC_MoveAbsolute`）。**不支持高/低速专用轴**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Position     : LREAL;
    Velocity     : LREAL;
    EndVelocity  : LREAL;
    Acceleration : LREAL;
    Deceleration : LREAL;
    Jerk         : LREAL;
    BufferMode   : MC_BufferMode;
    Options      : ST_MoveOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | {DESC_EXECUTE} |
| `Position` | `LREAL` | — | 绝对目标位置 |
| `Velocity` | `LREAL` | — | 行程中最大行进速度，`>0` |
| `EndVelocity` | `LREAL` | — | 到达 `Position` 时维持的终末速度 |
| `Acceleration` | `LREAL` | — | {DESC_ACC} |
| `Deceleration` | `LREAL` | — | {DESC_DEC} |
| `Jerk` | `LREAL` | — | {DESC_JERK} |
| `BufferMode` | `MC_BufferMode` | — | {DESC_BUFFER} |
| `Options` | `ST_MoveOptions` | — | {DESC_OPTIONS} |

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
    InEndVelocity  : BOOL;
    Busy           : BOOL;
    Active         : BOOL;
    CommandAborted : BOOL;
    Error          : BOOL;
    ErrorID        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `InEndVelocity` | `BOOL` | 到达 `Position` 且已达 `EndVelocity` 时置 `TRUE`；之后 FB 不再监视 |
| `Busy` | `BOOL` | {DESC_BUSY} |
| `Active` | `BOOL` | {DESC_ACTIVE} |
| `CommandAborted` | `BOOL` | {DESC_ABORTED} |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorID` | `UDINT` | {DESC_ERRORID} |

## 3. 行为说明

**触发**：`Execute` 上升沿；轴按 `Velocity` 加速行进，临近 `Position` 时让出剩余距离用于减速，到达 `Position` 时速度恰为 `EndVelocity`。

**状态机**：与 `MC_MoveVelocity` 类似——`InEndVelocity` 一旦置位 FB 即"放手"，与 `MC_MoveAbsolute` 持续监视到位的语义不同。

**为何要"过点不停"**：典型应用是**连续工艺段**：例如激光切割完一段直线后**不要在拐点完全停下来**（会出过烧痕），而要保持 `EndVelocity` 衔接下一段弧线。Beckhoff 在 PDF 中明确给出 `MC_MoveContinuousAbsolute` 是为这类"过点连续运动"设计的——配合下一条 `MC_MoveContinuousRelative` 或 `MC_MoveAbsolute` 用 `BufferMode = Buffered` 串接。

**轴不被监视**：`InEndVelocity = TRUE` 后**只能保证**该瞬间速度等于 `EndVelocity`、位置等于 `Position`。之后如果业务没发新命令，NC 仍会按 `EndVelocity` 继续走，**这是预期行为**。

**不支持高/低速轴**。`EndVelocity = 0` 退化为普通 `MC_MoveAbsolute` 行为，但建议直接用后者更清晰。

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **`EndVelocity > 0` 时轴不会停**：`InEndVelocity = TRUE` 后轴继续走，必须有下一条命令兜底，**否则轴一路冲到软限位报错**。
- **`EndVelocity > Velocity` 会报错**：终末速度不能超过行程速度。
- **拐点匀速过渡需要 `Buffered`**：单实例用 `Aborting` 起不到过点效果；两段过点连续运动需要**两个不同实例**配 `BufferMode := MC_Buffered`。
- **不支持高/低速轴**：硬件类型为 high/low speed axis 报错。
- **小心 `BufferMode = Blending*`**：blending 模式会让两段轨迹"融合"，行为比 Buffered 复杂，没有把握就先用 Buffered。
- **业务必须有"兜底停车"机制**：写代码时记得在状态机 Error 分支或紧急停止信号触发时调 `MC_Halt`，否则轴永远不停。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

```iecst
// 场景：激光切割机 — 直线段以高速 1000 mm/s 切到 100 mm，过点不停继续 200 mm/s 进入圆弧段
PROGRAM P_Demo_MC_MoveContinuousAbsolute
VAR
    fbStraightCut    : MC_MoveContinuousAbsolute;
    fbHaltSafety     : MC_Halt;
    axisLaserHead    : AXIS_REF;
    rtCutTrig        : R_TRIG;
    rtSafetyHalt     : R_TRIG;
    bStartStraight   : BOOL;
    bEmergencyStop   : BOOL;
    bInArc           : BOOL;
    bSafetyHaltDone  : BOOL;
    nErrorID         : UDINT;
END_VAR

rtCutTrig(CLK := bStartStraight);
rtSafetyHalt(CLK := bEmergencyStop);

fbStraightCut(
    Execute       := rtCutTrig.Q,
    Position      := 100.0,
    Velocity      := 1000.0,
    EndVelocity   := 200.0,
    Acceleration  := 5000.0,
    Deceleration  := 5000.0,
    Jerk          := 50000.0,
    BufferMode    := MC_Buffered,
    Axis          := axisLaserHead,
    InEndVelocity => bInArc,
    ErrorID       => nErrorID
);

// 兜底停车：紧急停止信号触发把轴减速到 0
fbHaltSafety(
    Execute      := rtSafetyHalt.Q,
    Deceleration := 10000.0,
    Jerk         := 100000.0,
    Axis         := axisLaserHead,
    Done         => bSafetyHaltDone
);
```

## 7. 业务场景与实际价值

- **场景**：激光/水刀切割轨迹过点不停、雕刻机段间过渡、印刷机色版定位段间衔接。共同点：**点 A 到点 B 的过渡不能停顿**，要保持工艺速度。
- **价值**：业务无需自己算"在终点前多少 mm 开始减速"，FB 直接接受目标位 + 终末速度两个工艺量，加减速曲线由 NC 自动算。
- **替代方案对比**：
  - 用 `MC_MoveAbsolute` 然后再 `MC_MoveVelocity`：两段之间必然停顿（前者 `Done` 出现时速度已是 0）
  - 用 `MC_MoveContinuousRelative`：基于相对距离，本 FB 基于绝对位置
  - **本 FB**：连续轨迹工艺的首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.1.7
- **InfoSys topic**：{info}
- **相关 FB**：`MC_MoveContinuousRelative`、`MC_MoveAbsolute`、`MC_Halt`
"""
    body = "\n".join([
        vderived("fbStraightCut", "MC_MoveContinuousAbsolute"),
        vderived("fbHaltSafety", "MC_Halt"),
        vderived("axisLaserHead", "AXIS_REF"),
        vderived("rtCutTrig", "R_TRIG"),
        vderived("rtSafetyHalt", "R_TRIG"),
        vbool("bStartStraight", "FALSE"),
        vbool("bEmergencyStop", "FALSE"),
        vbool("bInArc"),
        vbool("bSafetyHaltDone"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：激光切割机 — 直线段切到 100 mm 时不要停（停了会出过烧痕），保持
//       200 mm/s 进入下一段圆弧。EndVelocity = 200 是关键。
// 价值：业务给绝对终点 + 终末速度两个量，FB 自动算减速曲线让到位时速度恰好。
// 验证：bStartStraight := TRUE → 看 ActPos 加速到 1000 mm/s 走到 100 mm，
//       到位时 ActVelo ≈ 200，bInArc 置 TRUE。bEmergencyStop := TRUE → 兜底停车。
// =============================================================================

rtCutTrig(CLK := bStartStraight);
rtSafetyHalt(CLK := bEmergencyStop);

fbStraightCut(
    Execute       := rtCutTrig.Q,
    Position      := 100.0,
    Velocity      := 1000.0,
    EndVelocity   := 200.0,
    Acceleration  := 5000.0,
    Deceleration  := 5000.0,
    Jerk          := 50000.0,
    BufferMode    := MC_Buffered,
    Axis          := axisLaserHead,
    InEndVelocity =&gt; bInArc,
    ErrorID       =&gt; nErrorID
);

fbHaltSafety(
    Execute      := rtSafetyHalt.Q,
    Deceleration := 10000.0,
    Jerk         := 100000.0,
    Axis         := axisLaserHead,
    Done         =&gt; bSafetyHaltDone
);
"""
    emit("point_to_point_motion", name, doc, xml_skel(name, body, st))


# ---------------------------------------------------------------------------
# MC_MoveContinuousRelative (6.1.8) — Distance + EndVelocity
# ---------------------------------------------------------------------------

def gen_move_continuous_relative():
    name = "MC_MoveContinuousRelative"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70105483.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Point to point motion", info, name)}

## 1. 功能简述

PLCopen 标准定义的**带终末速度的相对定位 FB**。从当前 NC 设定位置起按 `Distance` 走一段相对距离，到达终点时**不停车**，而是保持 `EndVelocity` 继续走。`InEndVelocity := TRUE` 标志到达目标位置且已达终末速度。

与 `MC_MoveContinuousAbsolute` 的区别：本 FB 给"再走多远"，绝对版给"到哪个坐标"。**不支持高/低速专用轴**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute      : BOOL;
    Distance     : LREAL;
    Velocity     : LREAL;
    EndVelocity  : LREAL;
    Acceleration : LREAL;
    Deceleration : LREAL;
    Jerk         : LREAL;
    BufferMode   : MC_BufferMode;
    Options      : ST_MoveOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | {DESC_EXECUTE} |
| `Distance` | `LREAL` | — | 相对行进距离（可负） |
| `Velocity` | `LREAL` | — | 行程中最大速度 |
| `EndVelocity` | `LREAL` | — | 到达终点时维持的终末速度 |
| `Acceleration` | `LREAL` | — | {DESC_ACC} |
| `Deceleration` | `LREAL` | — | {DESC_DEC} |
| `Jerk` | `LREAL` | — | {DESC_JERK} |
| `BufferMode` | `MC_BufferMode` | — | {DESC_BUFFER} |
| `Options` | `ST_MoveOptions` | — | {DESC_OPTIONS} |

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
    InEndVelocity  : BOOL;
    Busy           : BOOL;
    Active         : BOOL;
    CommandAborted : BOOL;
    Error          : BOOL;
    ErrorID        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `InEndVelocity` | `BOOL` | 到达终点且速度=`EndVelocity` 时置 `TRUE` |
| `Busy` | `BOOL` | {DESC_BUSY} |
| `Active` | `BOOL` | {DESC_ACTIVE} |
| `CommandAborted` | `BOOL` | {DESC_ABORTED} |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorID` | `UDINT` | {DESC_ERRORID} |

## 3. 行为说明

**触发**：`Execute` 上升沿；起点 = NC 当前设定位置，终点 = 起点 + `Distance`，到达时速度 = `EndVelocity`。

**FB 终止行为**：`InEndVelocity = TRUE` 后 FB 任务结束，**轴继续以 `EndVelocity` 行进**；业务必须后续接管。

**典型工艺**：用于连续路径中每段以相对距离描述的场景。例如打标机沿 X 方向先打 50 mm 长的横线（结束保持 100 mm/s）→ 再发一段 `MC_MoveContinuousRelative(Distance := 50, EndVelocity := 0)` 让它平滑收尾。两段之间用 `BufferMode := MC_Buffered` 串接实现无停顿过渡。

**与 `MC_MoveRelative` 区别**：后者到位即"完成 Done"且默认希望停车；本 FB 到位时速度恰好等于 `EndVelocity`，**不一定为 0**。

**不支持高/低速专用轴**。

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **`EndVelocity > Velocity` 报错**：终末速度物理上不能超过行程速度。
- **`EndVelocity > 0` 后轴不停**：业务必须有后续命令。常见 bug 是单独用本 FB 试图走一段相对距离然后期待轴自己停 —— 实际不会，需要再发 `MC_Halt`。
- **被打断后相对距离起点变**：与 `MC_MoveRelative` 一样，被 `MC_Stop` 干预后再触发本 FB 起点是被打断时的设定位。
- **不支持高/低速专用轴**：硬件类型不符报错。
- **被 `MC_MoveContinuousAbsolute` 抢占后位置漂移**：相对运动与绝对运动混用时务必清楚每条命令的"基准点"。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

```iecst
// 场景：贴标机标头沿 X 走 200 mm 完成一张标签贴附，过点不停 100 mm/s 进入下一段
PROGRAM P_Demo_MC_MoveContinuousRelative
VAR
    fbLabelStroke   : MC_MoveContinuousRelative;
    fbStopAtEnd     : MC_Halt;
    axisLabelHead   : AXIS_REF;
    rtStrokeTrig    : R_TRIG;
    rtStopTrig      : R_TRIG;
    bStartStroke    : BOOL;
    bFinishCycle    : BOOL;
    lrLabelLengthMM : LREAL := 200.0;
    lrTransitVelo   : LREAL := 100.0;
    bAtEnd          : BOOL;
    bStopDone       : BOOL;
    nErrorID        : UDINT;
END_VAR

rtStrokeTrig(CLK := bStartStroke);
rtStopTrig(CLK := bFinishCycle);

fbLabelStroke(
    Execute       := rtStrokeTrig.Q,
    Distance      := lrLabelLengthMM,
    Velocity      := 800.0,
    EndVelocity   := lrTransitVelo,
    Acceleration  := 4000.0,
    Deceleration  := 4000.0,
    Jerk          := 40000.0,
    BufferMode    := MC_Buffered,
    Axis          := axisLabelHead,
    InEndVelocity => bAtEnd,
    ErrorID       => nErrorID
);

fbStopAtEnd(
    Execute      := rtStopTrig.Q,
    Deceleration := 4000.0,
    Jerk         := 40000.0,
    Axis         := axisLabelHead,
    Done         => bStopDone
);
```

## 7. 业务场景与实际价值

- **场景**：贴标段连续过渡、印刷机版滚定长走一格 + 维持线速度衔接下一格、激光打标的横划/竖划段间无停顿衔接。
- **价值**：相对距离 + 终末速度组合直接描述工艺，PLC 不用算减速点位置。
- **替代方案对比**：
  - 用 `MC_MoveRelative` 然后再 `MC_MoveVelocity`：两段之间必停
  - 用 `MC_MoveContinuousAbsolute`：要业务自己算绝对终点位置
  - **本 FB**：相对距离描述的连续轨迹工艺首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.1.8
- **InfoSys topic**：{info}
- **相关 FB**：`MC_MoveContinuousAbsolute`、`MC_MoveRelative`、`MC_Halt`
"""
    body = "\n".join([
        vderived("fbLabelStroke", "MC_MoveContinuousRelative"),
        vderived("fbStopAtEnd", "MC_Halt"),
        vderived("axisLabelHead", "AXIS_REF"),
        vderived("rtStrokeTrig", "R_TRIG"),
        vderived("rtStopTrig", "R_TRIG"),
        vbool("bStartStroke", "FALSE"),
        vbool("bFinishCycle", "FALSE"),
        vlreal("lrLabelLengthMM", "200.0"),
        vlreal("lrTransitVelo", "100.0"),
        vbool("bAtEnd"),
        vbool("bStopDone"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：贴标机标头沿 X 走 200 mm（一张标签长度），到位时不停保持 100 mm/s
//       衔接下一段（例如下一个标签或回程段）。
// 价值：相对距离 + 终末速度直接描述工艺，PLC 不用算减速点位置。
// 验证：bStartStroke := TRUE → ActPos 增加 200 mm 后 ActVelo 维持 100 mm/s，
//       bAtEnd 置 TRUE。bFinishCycle := TRUE → 兜底停车。
// =============================================================================

rtStrokeTrig(CLK := bStartStroke);
rtStopTrig(CLK := bFinishCycle);

fbLabelStroke(
    Execute       := rtStrokeTrig.Q,
    Distance      := lrLabelLengthMM,
    Velocity      := 800.0,
    EndVelocity   := lrTransitVelo,
    Acceleration  := 4000.0,
    Deceleration  := 4000.0,
    Jerk          := 40000.0,
    BufferMode    := MC_Buffered,
    Axis          := axisLabelHead,
    InEndVelocity =&gt; bAtEnd,
    ErrorID       =&gt; nErrorID
);

fbStopAtEnd(
    Execute      := rtStopTrig.Q,
    Deceleration := 4000.0,
    Jerk         := 40000.0,
    Axis         := axisLabelHead,
    Done         =&gt; bStopDone
);
"""
    emit("point_to_point_motion", name, doc, xml_skel(name, body, st))


# ---------------------------------------------------------------------------
# MC_Halt (6.1.9)
# ---------------------------------------------------------------------------

def gen_halt():
    name = "MC_Halt"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70107019.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Point to point motion", info, name)}

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
| `Execute` | `BOOL` | — | {DESC_EXECUTE} |
| `Deceleration` | `LREAL` | — | 减速度；`≤ 0` 时采用轴参数默认减速度 |
| `Jerk` | `LREAL` | — | {DESC_JERK} |
| `BufferMode` | `MC_BufferMode` | — | {DESC_BUFFER} |
| `Options` | `ST_MoveOptions` | — | {DESC_OPTIONS} |

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
| `Done` | `BOOL` | 轴已减速到 0 时置 `TRUE` |
| `Busy` | `BOOL` | {DESC_BUSY} |
| `Active` | `BOOL` | {DESC_ACTIVE} |
| `CommandAborted` | `BOOL` | 减速中被其它运动命令抢占时置 `TRUE` |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorID` | `UDINT` | {DESC_ERRORID} |

## 3. 行为说明

**触发**：`Execute` 上升沿启动减速；轴按指定减速度斜坡降速到 0，`Done` 置 `TRUE`。

**与 `MC_Stop` 关键区别**：
- `MC_Halt`：停后**不锁轴**，业务可立刻发新 Move 命令让轴再动
- `MC_Stop`：停后**锁轴**，必须 `MC_Reset` 才能解锁；适合"出事了不许再动"的紧急停车

**减速段被抢占**：减速过程中若另一条 Move 命令切入（`MC_Aborting`），本 FB 输出 `CommandAborted := TRUE`，轴跟着新命令走。这是"工艺允许中途反悔"的体现。

**`Deceleration ≤ 0` 的行为**：采用轴参数中默认减速度（不是"瞬时停"也不是"无减速"）。

**耦合从轴特例**：从轴上发 `MC_Halt` 会先自动解耦再减速；只能 `MC_Aborting`。

**典型用法**：正常工艺循环结束 / 节拍间停顿 / 操作员按"暂停"按钮 — 这些场景全用 `MC_Halt`。**只有紧急停车 / 检测到故障要锁轴才用 `MC_Stop`**。

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **正常停轴用 `MC_Halt` 不是 `MC_Stop`**：搞错了导致每次正常循环结束都要 Reset 才能开新循环，很别扭。
- **`Done` 短暂置位**：`Done := TRUE` 只维持一个周期左右（直到 `Execute` 撤销或新命令进来）；不能当成"轴静止"长期判定，要持续判断停止应读 `Axis.NcToPlc.ActVelo`。
- **`Execute` 撤销不影响停车**：本 FB 一旦启动减速，撤 `Execute` 不会让轴重新加速，但减速继续完成。
- **减速度太小会出问题**：极小的减速度 + 极高初速度可能导致超软限位，NC 会报错。建议留 20% 安全余量。
- **耦合从轴上调用会解耦**：常被忽略。要"让从轴跟主轴一起停"应停主轴（`MC_Halt(MasterAxis)`）而不是发 `MC_Halt(SlaveAxis)`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

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

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.1.9
- **InfoSys topic**：{info}
- **相关 FB**：`MC_Stop`（紧急/故障锁停）、`MC_MoveVelocity`（启动恒速）、`MC_Reset`（解锁）
"""
    body = "\n".join([
        vderived("fbCycleHalt", "MC_Halt"),
        vderived("axisProcess", "AXIS_REF"),
        vderived("rtCycleEnd", "R_TRIG"),
        vbool("bEndOfCycle", "FALSE"),
        vbool("bHaltDone"),
        vbool("bHaltBusy"),
        vbool("bAborted"),
        vudint("nErrorID"),
    ])
    st = """// =============================================================================
// 场景：包装线传送带每完成一袋产品就发"节拍结束"信号让传送带平稳停下，下一
//       节拍信号到了再启动。这是"正常工艺停"——用 MC_Halt 不用 MC_Stop。
// 价值：停后不锁轴，下一节拍 MC_MoveVelocity 可直接启动，不需先 Reset。
// 验证：先 MC_MoveVelocity 让传送带跑起来（demo 假设已跑）；bEndOfCycle := TRUE →
//       看 ActVelo 在 ~ 0.75 s 内减到 0，bHaltDone 短暂置 TRUE。然后立刻
//       MC_MoveVelocity 应能再启动（如果先发 MC_Stop 就启动不了，需 Reset）。
// =============================================================================

rtCycleEnd(CLK := bEndOfCycle);

fbCycleHalt(
    Execute        := rtCycleEnd.Q,
    Deceleration   := 2000.0,
    Jerk           := 20000.0,
    BufferMode     := MC_Aborting,
    Axis           := axisProcess,
    Done           =&gt; bHaltDone,
    Busy           =&gt; bHaltBusy,
    CommandAborted =&gt; bAborted,
    ErrorID        =&gt; nErrorID
);
"""
    emit("point_to_point_motion", name, doc, xml_skel(name, body, st))


# ---------------------------------------------------------------------------
# MC_Stop (6.1.10) — no BufferMode
# ---------------------------------------------------------------------------

def gen_stop():
    name = "MC_Stop"
    info = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70108555.html"
    doc = f"""# {name}

{metablock("FUNCTION_BLOCK", "Point to point motion", info, name)}

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
| `Jerk` | `LREAL` | — | {DESC_JERK} |
| `Options` | `ST_MoveOptions` | — | {DESC_OPTIONS} |

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
| `Done` | `BOOL` | 轴已减速到 0 时置 `TRUE`（锁定状态仍在） |
| `Busy` | `BOOL` | `Execute` 上升沿后立即 `TRUE`，**`Execute` 撤销后还会维持几个周期**（NC 释放命令所需）才变 `FALSE` |
| `Active` | `BOOL` | {DESC_ACTIVE} |
| `CommandAborted` | `BOOL` | {DESC_ABORTED} |
| `Error` | `BOOL` | {DESC_ERROR} |
| `ErrorID` | `UDINT` | {DESC_ERRORID} |

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

{ERRORID_SECTION}

## 5. 使用注意 / 常见坑

- **正常停轴别用 `MC_Stop`**：会导致每次都要 `MC_Reset`，多余操作步骤拖慢节拍。
- **`Execute` 撤销后还要继续调用**：常见错误是 `MC_Stop` 触发后立刻把 `Execute := FALSE` 且不再 cyclic 调用，导致 NC 状态卡住下一次重启失败。**FB 必须周期调用直到 `Busy = FALSE`**。
- **`Done` 出现不代表解锁**：解锁要 `MC_Reset`。把 `Done = TRUE` 当解锁信号会出现下一条命令报错。
- **耦合从轴上发会解耦**：要让"耦合系统一起停 + 锁"应作用于主轴，从轴会自动跟。
- **MC_Stop 没有 BufferMode**：因为它本质是 Aborting；用户不能让它"排队"。
- **硬件 E-Stop 必须走 Safety PLC**：本 FB 不能替代功能安全停车；功能安全要 Safety over EtherCAT。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_{name}.xml`](../examples/P_Demo_{name}.xml)

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

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf]({PDF_URL}) §6.1.10
- **InfoSys topic**：{info}
- **相关 FB**：`MC_Halt`（不锁的正常停）、`MC_Reset`（解锁）、`MC_Power`（轴使能）
"""
    body = "\n".join([
        vderived("fbEmergencyStop", "MC_Stop"),
        vderived("fbResetAxis", "MC_Reset"),
        vderived("axisLoader", "AXIS_REF"),
        vderived("rtFaultDetected", "R_TRIG"),
        vderived("rtOperatorReset", "R_TRIG"),
        vbool("bFaultDetected", "FALSE", "在线 TRUE 模拟故障检测"),
        vbool("bOperatorAck", "FALSE", "在线 TRUE 模拟操作员按 Reset"),
        vbool("bStopDone"),
        vbool("bStopBusy"),
        vbool("bResetDone"),
        vudint("nStopErrorID"),
        vudint("nResetErrorID"),
    ])
    st = """// =============================================================================
// 场景：上料轴检测到工件卡死（外部传感器报警）→ 立刻紧急停 + 锁轴，
//       等操作员现场确认排障 + 按 Reset 才允许继续。
// 价值：停 + 锁一体完成，避免上位机或操作员在故障未确认时误重启。
// 验证：1) 让 axisLoader 运行（例如先在另一个 PRG 里发 MC_MoveVelocity）
//       2) bFaultDetected := TRUE → bStopBusy 立 TRUE，ActVelo 快速降到 0
//       3) bStopDone 短暂 TRUE，但此时再发 Move 会报错（轴被锁）
//       4) bFaultDetected := FALSE 让 Stop 释放，bStopBusy 几周期后 FALSE
//       5) bOperatorAck := TRUE → MC_Reset 解锁，bResetDone 短暂 TRUE
//       6) 之后再发 Move 才能正常执行
// =============================================================================

rtFaultDetected(CLK := bFaultDetected);
rtOperatorReset(CLK := bOperatorAck);

// MC_Stop 的 Execute 持续保持 TRUE 直到 Done 出现 + 业务确认要"释放"才置 FALSE
// 但锁状态会一直保持到 MC_Reset
fbEmergencyStop(
    Execute      := bFaultDetected,
    Deceleration := 10000.0,
    Jerk         := 100000.0,
    Axis         := axisLoader,
    Done         =&gt; bStopDone,
    Busy         =&gt; bStopBusy,
    ErrorID      =&gt; nStopErrorID
);

// 操作员 Reset 后解锁
fbResetAxis(
    Execute := rtOperatorReset.Q,
    Axis    := axisLoader,
    Done    =&gt; bResetDone,
    ErrorID =&gt; nResetErrorID
);
"""
    emit("point_to_point_motion", name, doc, xml_skel(name, body, st))


if __name__ == "__main__":
    gen_move_modulo()
    gen_move_velocity()
    gen_move_continuous_absolute()
    gen_move_continuous_relative()
    gen_halt()
    gen_stop()
    print("batch 2 done")
