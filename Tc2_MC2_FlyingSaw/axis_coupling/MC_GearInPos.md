# MC_GearInPos

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_FlyingSaw` |
| Library Version | `1.6.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Flying saw` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5055_TC3_NC_Flying_Saw_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5055_tc3_nc_flying_saw/1004044683.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_GearInPos.TcPOU`](../examples/P_Demo_MC_GearInPos.TcPOU) |

---

## 1. 功能简述

飞锯（Flying Saw）库的**位置同步耦合**功能块（Function Block, FB）。把从轴（Slave）精确同步到主轴（Master）——不仅速度成齿比，而且在指定的主轴同步位置 `MasterSyncPosition` 与从轴同步位置 `SlaveSyncPosition` 上，从轴恰好达到同步速度且位置精确对齐。这正是横切/飞剪要求"在某个料长位置精确下刀"的能力。

主轴**必须已经在运动**，否则无法完成同步。齿比同样以分子/分母（`RatioNumerator` / `RatioDenominator`）形式给出。解耦用 `MC_GearOut`；运动中解耦从轴保持当前速度，需用 `MC_Stop` / `MC_Halt` 停下。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute             : BOOL;
    RatioNumerator      : LREAL;
    RatioDenominator    : UINT;
    MasterSyncPosition  : LREAL;
    SlaveSyncPosition   : LREAL;
    SyncMode            : ST_SyncMode;
    MasterStartDistance : LREAL;
    Velocity            : LREAL;
    Acceleration        : LREAL;
    Deceleration        : LREAL;
    Jerk                : LREAL;
    BufferMode          : MC_BufferMode;
    Options             : ST_GearInPosOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次耦合命令 |
| `RatioNumerator` | `LREAL` | — | 齿比分子；若 `RatioDenominator = 1` 可直接写浮点比（如 0.25）。可为负（反向） |
| `RatioDenominator` | `UINT` | — | 齿比分母；1:4 写法为分子 1、分母 4 |
| `MasterSyncPosition` | `LREAL` | — | 主轴的同步位置（在此主轴位置上完成同步） |
| `SlaveSyncPosition` | `LREAL` | — | 从轴的同步位置（在主轴到达同步位置时从轴应处的位置） |
| `SyncMode` | `ST_SyncMode` | — | 同步过程边界条件结构（位掩码），逐位指定是否检查位置/速度/加速度等限值 |
| `MasterStartDistance` | `LREAL` | — | **当前版本未实现** |
| `Velocity` | `LREAL` | — | 同步阶段从轴最大速度；不指定用轴默认值。仅当 `SyncMode` 开启对应检查位时才校验 |
| `Acceleration` | `LREAL` | — | 同步阶段从轴最大加速度；不指定用轴默认值。仅当 `SyncMode` 开启对应检查位时才校验 |
| `Deceleration` | `LREAL` | — | 同步阶段从轴最大减速度；不指定用轴默认值。仅当 `SyncMode` 开启对应检查位时才校验 |
| `Jerk` | `LREAL` | — | 同步阶段从轴最大 Jerk；不指定用轴默认值。仅当 `SyncMode` 开启对应检查位时才校验 |
| `BufferMode` | `MC_BufferMode` | — | **当前版本未实现** |
| `Options` | `ST_GearInPosOptions` | — | 含两个位置限值（`PositionLimitMin` / `PositionLimitMax`）；需在 `SyncMode` 中置 `GearInSync_CheckMask_OptionalMinPos` / `OptionalMaxPos` 才生效 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Master : AXIS_REF;
    Slave  : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Master` | `AXIS_REF` | 主轴数据结构（必须已在运动） |
| `Slave` | `AXIS_REF` | 从轴数据结构；同步后在同步点上位置与速度都与主轴精确对齐 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    StartSync      : BOOL;
    InSync         : BOOL;
    Busy           : BOOL;
    Active         : BOOL;
    CommandAborted : BOOL;
    Error          : BOOL;
    ErrorID        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `StartSync` | `BOOL` | 与主轴的同步**开始**时置 `TRUE` |
| `InSync` | `BOOL` | 耦合成功完成、从轴已与主轴同步时置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 触发后置 `TRUE`，命令处理期间保持；变 `FALSE` 即 FB 可接新命令，同时 `InSync` / `CommandAborted` / `Error` 之一被置位 |
| `Active` | `BOOL` | 表示命令正在执行（当前版本 `Active = Busy`，见 `BufferMode`） |
| `CommandAborted` | `BOOL` | 命令未能完整执行时置 `TRUE`（耦合过程中被其他命令打断/解耦） |
| `Error` | `BOOL` | 发生错误时置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出错误号 |

## 3. 行为说明

**位置同步语义**：本 FB 是**位置耦合**——目标是在主轴到达 `MasterSyncPosition` 的同一时刻，从轴恰好到达 `SlaveSyncPosition` 且速度已达 `主轴速度 × 齿比`。换言之同步点上**位置与速度同时精确对齐**。`Execute` 上升沿后，NC 为从轴规划一段过渡轮廓（cam-table），使其在指定同步点平滑切入比例跟随；同步开始时 `StartSync` 为 `TRUE`，完成时 `InSync` 为 `TRUE`。

**与速度同步（`MC_GearInVelo`）的区别**：`MC_GearInVelo` 只保证速度成比例，不约束在哪个主轴位置上从轴到达什么位置；`MC_GearInPos` 额外强制**位置对齐**。横切来料时若需要"主轴走到第 N 个料长位置时刀刃正好对准切缝并同速"，必须用本 FB；只要线速度匹配则用 `MC_GearInVelo` 更简单。

**主轴必须在运动**：与 `MC_GearInVelo` 一样允许运动中接入，但本 FB 明确要求主轴已经在动，否则无法规划同步轮廓、同步失败。

**同步窗口（边界条件检查）**：`SyncMode` 逐位掩码可开启对最小/最大位置、最大速度/加速度/减速度/Jerk、过冲/欠冲等检查；只有被开启的检查位对应的限值才会校验。开启位置检查时配合 `Options`（`ST_GearInPosOptions`）的 `PositionLimitMin/Max`。同步点之间的距离必须足够从轴完成过渡轮廓，否则同步窗口不足会同步失败或超动态限值。

**未实现项**：`MasterStartDistance` 与 `BufferMode` 当前版本未实现；时间基同步模式 `GEARINSYNCMODE_TIMEBASED` 当前**仅 `MC_GearInVelo` 支持**，对本 FB 无效，本 FB 使用位置相关（`GEARINSYNCMODE_POSITIONBASED`）规划。

**解耦时机**：耦合后从轴持续按比例跟随，不需周期发命令。解耦用 `MC_GearOut`；**运动中解耦从轴不会自动停**，保持当前速度继续走，必须用 `MC_Stop` / `MC_Halt` 主动停从轴。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC / 飞锯错误号。

| 输出 | 类型 | 含义 |
|---|---|---|
| `Error` | `BOOL` | 发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | 错误号；主轴未运动、同步窗口不足、边界检查不通过、参数非法等都会反映在此 |

⚠️ PDF 在本 FB 章节未逐条列出 `ErrorID` 数值含义。完整错误码见 TF5055 飞锯手册的 Error Codes 主题；启用 `SyncMode` 的 `GearInSync_OpMask_DetailedErrorCodes` 位可获得更细的检查失败错误码。

## 5. 使用注意 / 常见坑

- **主从速比 + 同步点要自洽**：`MasterSyncPosition` / `SlaveSyncPosition` 与齿比必须物理一致，配错会导致同步点对不上或同步失败。
- **同步区间不足**：同步点离接入点太近，从轴来不及规划完整过渡轮廓，`InSync` 到不了或超动态限值报错；要留足同步窗口。
- **解耦不停从轴**：运动中 `MC_GearOut` 后从轴保持速度继续走，必须接 `MC_Stop`/`MC_Halt`，否则撞极限。飞锯最典型事故。
- **主轴未运动直接耦合会失败**：本 FB 要求主轴已在动。
- **`MasterStartDistance` / `BufferMode` 未实现**：填了无效。
- **时间基模式无效**：`GEARINSYNCMODE_TIMEBASED` 仅 `MC_GearInVelo` 支持，本 FB 用位置基规划。
- **`Master` / `Slave` 都是 VAR_IN_OUT 必须传引用**：两根 `AXIS_REF` 都要传。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_GearInPos.TcPOU`](../examples/P_Demo_MC_GearInPos.TcPOU)

```iecst
// 场景：印刷连线横切，主轴(走料)走到每个印张切缝位置时刀辊须位置+速度精确对齐再切，保证切口落在印记上
PROGRAM P_Demo_MC_GearInPos
VAR
    fbGearInPos     : MC_GearInPos;
    axisWebFeed     : AXIS_REF;          // 主轴：走料/印张
    axisRotarySaw   : AXIS_REF;          // 从轴：旋转切刀
    syncMode        : ST_SyncMode;
    bCoupleReq      : BOOL;
    rtCouple        : R_TRIG;
    bStartSync      : BOOL;
    bInSync         : BOOL;
    bBusy           : BOOL;
    bActive         : BOOL;
    bAborted        : BOOL;
    bErr            : BOOL;
    nErrID          : UDINT;
END_VAR

rtCouple(CLK := bCoupleReq);
// 主轴走到 100.0 时从轴应到达 0.0 并达同步速度；1:1 速比
fbGearInPos(
    Execute            := rtCouple.Q,
    RatioNumerator     := 1.0,
    RatioDenominator   := 1,
    MasterSyncPosition := 100.0,
    SlaveSyncPosition  := 0.0,
    SyncMode           := syncMode,
    Master             := axisWebFeed,
    Slave              := axisRotarySaw,
    StartSync          => bStartSync,
    InSync             => bInSync,
    Busy               => bBusy,
    Active             => bActive,
    CommandAborted     => bAborted,
    Error              => bErr,
    ErrorID            => nErrID
);
IF NOT bBusy THEN
    bCoupleReq := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：印刷连线套准横切（切口必须落在印记位置）、定长飞剪（按料长精确下刀）、贴标/封口须在固定相位对齐的同步。共同点是**从轴必须在主轴某位置精确对齐位置与速度**。
- **价值**：不用本 FB 时要自己算同步点轮廓、做相位补偿与速度匹配，极易切歪/丢位；本 FB 把"在指定主/从同步点精确对齐"封装成一次 `Execute`，由 NC 规划过渡轮廓。
- **替代方案对比**：
  - `MC_GearInVelo`：只匹配速度、不约束位置，切口位置会漂，不能做套准切
  - `MC_CamIn`（Tc2_MC2_Camming）：用凸轮表做任意非线性同步轮廓，比线性飞锯更灵活但配置复杂
  - **本 FB**：线性飞锯位置同步的首选

## 8. 参考资料

- **PDF**：[TF5055_TC3_NC_Flying_Saw_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5055_TC3_NC_Flying_Saw_EN.pdf) §5.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5055_tc3_nc_flying_saw/1004044683.html
- **相关 FB / DUT**：`MC_GearInVelo`（速度同步飞锯）、`MC_GearOut`（解耦）、`MC_Stop` / `MC_Halt`（解耦后停从轴）、`ST_SyncMode`（同步边界条件）、`ST_GearInPosOptions`（位置限值）、`MC_ReadFlyingSawCharacteristics`（读同步特征值）
