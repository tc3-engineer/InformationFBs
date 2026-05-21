# MC_GearInDyn

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Axis coupling` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70124939.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_GearInDyn.xml`](../examples/P_Demo_MC_GearInDyn.xml) |

---


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
| `Busy` | `BOOL` | `Execute` 上升沿后立即变 `TRUE`，结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE` |
| `Active` | `BOOL` | 表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE` |
| `CommandAborted` | `BOOL` | 命令未完成就被中止（被另一 Move 抢占 / `MC_Stop` 停掉）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |

## 3. 行为说明

**电平触发耦合**：与 `MC_GearIn` 边沿触发不同，本 FB 是电平：`Enable = TRUE` 期间耦合持续；改 `GearRatio` 立即生效。

**`Enable → FALSE` 不解耦**：PDF 明确：`Enable` 变 FALSE 后命令结束，**齿比冻结在最后值**但从轴**仍处于耦合状态**。要真正解耦必须调 `MC_GearOut`。这是与 `MC_GearIn` 边沿触发型最大的差异。

**`MC_GearOut` 与 `Enable` 互动**：若在 `Enable = TRUE` 期间调用 `MC_GearOut`，从轴**短暂解耦后立刻重新耦合**——因为本 FB 仍在持续要求耦合状态。要真正解耦必须**先 `Enable := FALSE` 再 `MC_GearOut`**。

**`Acceleration` 的作用机制**：大幅变齿比时（例如从 1.0 切到 5.0）从轴需要加速跟上，本入口限制此加速段的加速度上限。**最大加速度只在主轴最大速度时达到**；主轴速度低时从轴实际加速度会按比例缩小。

**典型用法**：根据卷径变化实时调整收线辊齿比保持线速度恒定、张力反馈环每周期微调齿比。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **`Enable := FALSE` 不等于解耦**：见 §3。新手最常踩的坑是把 Enable 拉低期望"解耦从轴"——实际从轴仍按上一次齿比跟主轴走。
- **`MC_GearOut` 在 `Enable = TRUE` 时无效**：短暂解耦立刻重耦。要解耦顺序必须是 `Enable := FALSE` → `MC_GearOut(Slave)` → 可选 `MC_Halt(Slave)`。
- **`Deceleration / Jerk / BufferMode` 未实现**：填了没用，别误以为变齿比时减速段会受这些约束。
- **齿比大跃迁会出冲击**：从 1 一步切到 10，受 `Acceleration` 限制后从轴会有一段斜坡跟上，但工艺上仍可能有突变冲击。建议在 PLC 侧用低通滤波平滑 `GearRatio` 输入。（工程经验补充）
- **耦合期间从轴上发 Move 自动解耦**：与 `MC_GearIn` 相同行为。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_GearInDyn.xml`](../examples/P_Demo_MC_GearInDyn.xml)

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

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.5.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70124939.html
- **相关 FB**：`MC_GearIn`（固定齿比）、`MC_GearOut`（解耦）、`MC_GearInMultiMaster`（多主跟随）
