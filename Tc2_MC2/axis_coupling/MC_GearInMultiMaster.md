# MC_GearInMultiMaster

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Axis coupling` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70128011.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_GearInMultiMaster.TcPOU`](../examples/P_Demo_MC_GearInMultiMaster.TcPOU) |

---


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
| `Busy` | `BOOL` | `Execute` 上升沿后立即变 `TRUE`，结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE` |
| `Active` | `BOOL` | 表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE` |
| `CommandAborted` | `BOOL` | 命令未完成就被中止（被另一 Move 抢占 / `MC_Stop` 停掉）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |

## 3. 行为说明

**叠加合成**：从轴速度 / 位置 = Σ(MasterN × GearRatioN)，N = 1..4 中未被禁用的项（轴 ID ≠ 0 才参与）。

**齿比动态可调**：`Enable = TRUE` 期间可任意 GearRatioN 每周期改，FB 自动更新。

**`MC_GearOut` 与 `Enable = TRUE` 互动**：若 `MC_GearOut` 在 `Enable` 仍 TRUE 时执行，从轴短暂解耦后立刻重新耦合。要彻底解耦：先 `Enable := FALSE` 再 `MC_GearOut`。

**`Enable := FALSE` 不解耦**：与 `MC_GearInDyn` 一致——命令结束但耦合保留，齿比冻结在最后值，从轴仍跟主轴们走。

**少于 4 主**：未用的 Master 参数传"空 AXIS_REF"结构（即 NC ID 为 0）。本 FB 自动忽略 ID = 0 的主轴。

**典型工艺**：龙门双驱（左右两个 X 轴叠加成"工件 X 位置"）、张力补偿（主线辊 + 张力反馈轴叠加成实际收线速度）。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **`Reference To AXIS_REF` 是引用语义**：传 ADR 取地址传给 FB；不能直接传 AXIS_REF 实体。例：`Master1 := ADR(axisMain1)`。
- **未用的 Master 不能传 NULL**：要传一个 AXIS_REF 实例（其轴 ID = 0 即可）；NULL pointer 会导致 PLC 异常。
- **`Enable := FALSE` 不解耦**：与 `MC_GearInDyn` 同坑。
- **齿比绝对值过大时受 `Acceleration` 限制**：从轴可能跟不上主轴瞬时变化，工艺上要预留余量。
- **不要混用同一从轴的多个耦合 FB 实例**：从轴上同时跑两个 `MC_GearInMultiMaster` 会冲突。
- **应用 `Options.AdvancedSlaveDynamics = TRUE` 可获更好动态**：但仅适用于 `MC_PhasingAbsolute/Relative` 与本 FB 配合的场景。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_GearInMultiMaster.TcPOU`](../examples/P_Demo_MC_GearInMultiMaster.TcPOU)

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

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.5.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70128011.html
- **相关 FB**：`MC_GearIn`、`MC_GearInDyn`、`MC_GearOut`、`MC_PhasingAbsolute`（叠加相位移）
