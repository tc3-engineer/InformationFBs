# MC_GearInVelo

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_FlyingSaw` |
| Library Version | `1.6.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Flying saw` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5055_TC3_NC_Flying_Saw_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5055_tc3_nc_flying_saw/9007200258735627.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_GearInVelo.xml`](../examples/P_Demo_MC_GearInVelo.xml) |

---

## 1. 功能简述

飞锯（Flying Saw）库的**速度同步耦合**功能块（Function Block, FB）。建立从轴（Slave）到主轴（Master）的线性齿轮耦合，把从轴**同步到主轴的速度**——若主轴已经在运动，从轴会按指定齿比加速到与主轴匹配的速度并跟随。齿比以分子/分母（`RatioNumerator` / `RatioDenominator`）形式给出。

与标准 `MC_GearIn`（要求从轴静止才能耦合）不同，本 FB 可以**在主轴运动中接入**，专为飞锯/横切场景设计：从轴先做一段同步加速，进入同步后保持与主轴速度成固定比例。

解耦用 `MC_GearOut`；运动中解耦时从轴保持当前速度，需用 `MC_Stop` 或 `MC_Halt` 停下。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute          : BOOL;
    RatioNumerator   : LREAL;
    RatioDenominator : UINT;
    SyncMode         : ST_SyncMode;
    Velocity         : LREAL;
    Acceleration     : LREAL;
    Deceleration     : LREAL;
    Jerk             : LREAL;
    BufferMode       : MC_BufferMode;
    Options          : ST_GearInVeloOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次耦合命令 |
| `RatioNumerator` | `LREAL` | — | 齿比分子；若 `RatioDenominator = 1`，可直接把齿比写成浮点值（如 0.25）。可为负（反向跟随） |
| `RatioDenominator` | `UINT` | — | 齿比分母；1:4 写法为分子 1、分母 4 |
| `SyncMode` | `ST_SyncMode` | — | 同步过程的边界条件结构（位掩码），逐位指定是否检查最小/最大位置、速度、加速度等限值 |
| `Velocity` | `LREAL` | — | 同步阶段从轴最大速度；不指定时用 System Manager 中的轴默认速度。仅当 `SyncMode` 中开启对应检查位时才校验 |
| `Acceleration` | `LREAL` | — | 同步阶段从轴最大加速度；不指定时用轴默认值。仅当 `SyncMode` 开启对应检查位时才校验 |
| `Deceleration` | `LREAL` | — | 同步阶段从轴最大减速度；不指定时用轴默认值。仅当 `SyncMode` 开启对应检查位时才校验 |
| `Jerk` | `LREAL` | — | 同步阶段从轴最大 Jerk；不指定时用轴默认值。仅当 `SyncMode` 开启对应检查位时才校验 |
| `BufferMode` | `MC_BufferMode` | — | **当前版本未实现** |
| `Options` | `ST_GearInVeloOptions` | — | 含两个位置限值（`PositionLimitMin` / `PositionLimitMax`）；需在 `SyncMode` 中置 `GearInSync_CheckMask_OptionalMinPos` / `OptionalMaxPos` 才生效 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Master : AXIS_REF;
    Slave  : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Master` | `AXIS_REF` | 主轴数据结构 |
| `Slave` | `AXIS_REF` | 从轴数据结构；耦合后其运动由主轴速度按齿比决定 |

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

**速度同步语义**：本 FB 做的是**速度耦合**——目标是让从轴速度达到 `主轴速度 × 齿比`，而不关心相位/位置对齐。`Execute` 上升沿后 `Busy` 与 `StartSync` 反映同步开始，从轴按 `Velocity`/`Acceleration`/`Deceleration`/`Jerk`（或轴默认动态值）做一段加速过渡；当速度达到比例关系后 `InSync` 置 `TRUE`，此后从轴持续以固定速比跟随主轴。

**与位置同步（`MC_GearInPos`）的区别**：`MC_GearInVelo` 只保证**速度**成比例，不保证在某个主轴位置上从轴恰好到达某个位置；`MC_GearInPos` 则要求在指定的主/从同步点上**位置与速度同时精确对齐**（见该 FB 文档）。横切来料时若只需匹配线速度用本 FB；若需在特定切点对齐位置则用 `MC_GearInPos`。

**主轴可运动中接入**：与标准 `MC_GearIn` 不同，本 FB 允许主轴已经在动时接入，从轴自动追上主轴速度，这正是"飞锯/飞剪"跟随启动的能力。

**同步窗口（边界条件检查）**：`SyncMode` 是逐位掩码，可开启对最小/最大位置、最大速度/加速度/减速度/Jerk、过冲/欠冲等的检查；只有被开启的检查位对应的 `Velocity`/`Acceleration` 等限值才会被校验，未开启时这些输入仅作动态规划参考。开启位置检查时还需配合 `Options`（`ST_GearInVeloOptions`）里的 `PositionLimitMin/Max`。

**解耦时机**：耦合后从轴持续跟随，不需要每周期发命令。解耦用 `MC_GearOut`；**运动中解耦从轴不会自动停**，它保持当前速度继续走，必须用 `MC_Stop` / `MC_Halt` 主动停从轴，否则会冲过行程极限。

**时间基同步模式**：`ST_SyncMode` 的 `GearInSyncMode` 可选 `GEARINSYNCMODE_TIMEBASED`（时间相关的运动规划，保证遵守所有从轴动态限值），该模式当前**仅 `MC_GearInVelo` 支持**（`MC_GearInPos` 不支持）。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC / 飞锯错误号。

| 输出 | 类型 | 含义 |
|---|---|---|
| `Error` | `BOOL` | 发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | 错误号；同步边界条件检查不通过、主轴状态不满足、参数非法等都会反映在此 |

⚠️ PDF 在本 FB 章节未逐条列出 `ErrorID` 数值含义。完整错误码见 TF5055 飞锯手册的 Error Codes 主题（InfoSys: tf5055_tc3_nc_flying_saw Error Codes）；启用 `SyncMode` 的 `GearInSync_OpMask_DetailedErrorCodes` 位可获得更细的检查失败错误码。

## 5. 使用注意 / 常见坑

- **速比配错**：分子/分母搞反或符号写反会导致从轴跑反方向或速度不匹配；负分子表示反向跟随，确认机械方向再用。
- **同步区间不足**：若来料/主轴运动区间太短，从轴来不及加速到同步速度就过了切点，`InSync` 永远到不了；要保证有足够的同步加速窗口。
- **解耦不停从轴**：运动中 `MC_GearOut` 后从轴保持速度继续走，必须紧接 `MC_Stop`/`MC_Halt`，否则撞极限。这是飞锯最典型事故。
- **`Velocity` 等限值默认不校验**：只有在 `SyncMode` 里开了对应检查位才生效，别以为填了 `Velocity` 就一定限速。
- **`BufferMode` 未实现**：填了无效，当前 `Active = Busy`。
- **`Master` / `Slave` 都是 VAR_IN_OUT 必须传引用**：两根 `AXIS_REF` 都要传。
- **时间基模式只支持本 FB**：`GEARINSYNCMODE_TIMEBASED` 用在 `MC_GearInPos` 上无效。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_GearInVelo.xml`](../examples/P_Demo_MC_GearInVelo.xml)

```iecst
// 场景：包装线连续走料主输送带 + 横封刀从轴，刀需先与来料线速度同步再下刀，避免拉伸/堆料
PROGRAM P_Demo_MC_GearInVelo
VAR
    fbGearInVelo    : MC_GearInVelo;
    axisMaterialFeed: AXIS_REF;          // 主轴：来料输送带
    axisCrossSaw    : AXIS_REF;          // 从轴：横切/横封刀
    syncMode        : ST_SyncMode;
    bCoupleReq      : BOOL;              // 启动速度同步
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
// 1:1 速比，使用轴默认动态值；SyncMode 全 0（不额外校验限值），speed-only 跟随
fbGearInVelo(
    Execute          := rtCouple.Q,
    RatioNumerator   := 1.0,
    RatioDenominator := 1,
    SyncMode         := syncMode,
    Master           := axisMaterialFeed,
    Slave            := axisCrossSaw,
    StartSync        => bStartSync,
    InSync           => bInSync,
    Busy             => bBusy,
    Active           => bActive,
    CommandAborted   => bAborted,
    Error            => bErr,
    ErrorID          => nErrID
);
IF NOT bBusy THEN
    bCoupleReq := FALSE;    // 命令进队后复位触发，准备下次
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：连续走料的横切/横封（包装袋切断、印刷连线裁切）、飞剪跟随主线速度、回转刀辊与来料线速度匹配。共同点是**从轴只需匹配主轴线速度**，不强求在某位置精确对齐。
- **价值**：不用本 FB 时要自己读主轴速度、做加速规划再周期性给从轴发速度命令，相位与时序难控；本 FB 把"运动中接入 + 加速同步 + 固定速比跟随"封装成一次 `Execute`，并支持时间基规划保证动态限值。
- **替代方案对比**：
  - `MC_GearInPos`：需要在指定切点精确对齐位置时用（位置同步），比速度同步严格
  - 标准 `MC_GearIn`（Tc2_MC2）：只能从轴静止时耦合，无法运动中接入，不适合飞锯
  - **本 FB**：飞锯速度同步的首选

## 8. 参考资料

- **PDF**：[TF5055_TC3_NC_Flying_Saw_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5055_TC3_NC_Flying_Saw_EN.pdf) §5.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5055_tc3_nc_flying_saw/9007200258735627.html
- **相关 FB / DUT**：`MC_GearInPos`（位置同步飞锯）、`MC_GearOut`（解耦）、`MC_Stop` / `MC_Halt`（解耦后停从轴）、`ST_SyncMode`（同步边界条件）、`ST_GearInVeloOptions`（位置限值）
