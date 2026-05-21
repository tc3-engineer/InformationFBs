# MC_GearIn

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Axis coupling` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70123403.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_GearIn.xml`](../examples/P_Demo_MC_GearIn.xml) |

---


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
| `Execute` | `BOOL` | — | 上升沿触发一次定位命令；命令进入运动队列后即开始执行，不需保持高电平 |
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
| `Busy` | `BOOL` | `Execute` 上升沿后立即变 `TRUE`，结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE` |
| `Active` | `BOOL` | 表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE` |
| `CommandAborted` | `BOOL` | 命令未完成就被中止（被另一 Move 抢占 / `MC_Stop` 停掉）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |

## 3. 行为说明

**触发**：`Execute` 上升沿在从轴静止时建立耦合，`InGear := TRUE`。之后只要主轴动，从轴**自动按齿比跟随**，PLC 不用写任何运动命令。

**齿比表达**：分数形式 `RatioNumerator / RatioDenominator` 适合工程上"输入齿数/输出齿数"这种整数比；浮点用法 `Denominator = 1` 时 `RatioNumerator` 直接当浮点比。例：`RatioNumerator = 1.5, RatioDenominator = 1` 表示从轴速度是主轴的 1.5 倍。

**反向耦合**：`RatioNumerator` 为负 = 反向跟随。

**从轴静止要求**：耦合时从轴 `Status.NotMoving = TRUE`，否则报错。若从轴在动，先 `MC_Halt(Slave)` 停下再耦合。

**解耦**：用 `MC_GearOut`；解耦时从轴**不会自动停**，会保持当前速度无限走（除非外部用 `MC_Halt` / `MC_Stop` 停它）。这一点常被忽略，引发"解耦后轴撞极限"事故。

**主轴运动期间发 Move 给从轴**：从轴上发 `MC_MoveAbsolute` 等会先**自动解耦**再执行；耦合状态被破坏。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **`Acceleration / Deceleration / Jerk / BufferMode` 全部未实现**：填了没用，别误以为耦合"会按这个加速度跟上去"。耦合建立时从轴是瞬时跟随。
- **解耦后从轴不会自动停**：见 §3 解耦段。要"解耦即停"必须在 `MC_GearOut` 后立即接 `MC_Halt(Slave)`。
- **必须从轴静止才能耦合**：动着要先停。
- **耦合期间给从轴发 Move 自动解耦**：常见坑，例如调试时手贱给从轴发 `MC_Jog` 一下就把耦合关系破坏。
- **齿比改不了**：要改需先 `MC_GearOut` 再重新 `MC_GearIn`，或者用 `MC_GearInDyn`。
- **AXIS_REF 必须传引用**：`Master` 和 `Slave` 都是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_GearIn.xml`](../examples/P_Demo_MC_GearIn.xml)

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

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.5.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70123403.html
- **相关 FB**：`MC_GearOut`（解耦）、`MC_GearInDyn`（动态齿比）、`MC_GearInMultiMaster`（多主跟随）、`MC_Halt(Slave)`（解耦后停从轴）
