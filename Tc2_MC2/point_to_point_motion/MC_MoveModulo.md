# MC_MoveModulo

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Point to point motion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70099339.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_MoveModulo.xml`](../examples/P_Demo_MC_MoveModulo.xml) |

---


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
| `Execute` | `BOOL` | — | 上升沿触发一次定位命令；命令进入运动队列后即开始执行，不需保持高电平 |
| `Position` | `LREAL` | — | 模数目标位置；从静止启动时 `>360°` 表示再多转圈数；不允许负值 |
| `Velocity` | `LREAL` | — | 最大行进速度，要求 `>0`；轴在加减速段两端按 `Acceleration` / `Deceleration` 限速 |
| `Acceleration` | `LREAL` | — | 加速度，要求 `≥0`；填 `0` 表示采用轴参数中默认加速度 |
| `Deceleration` | `LREAL` | — | 减速度，要求 `≥0`；填 `0` 表示采用轴参数中默认减速度 |
| `Jerk` | `LREAL` | — | 加加速度（Jerk），要求 `≥0`；填 `0` 表示采用轴参数中默认 Jerk |
| `Direction` | `MC_Direction` | — | 行进方向：`MC_Positive_Direction` / `MC_Negative_Direction` / `MC_ShortestWay`；运动中触发不允许换向 |
| `BufferMode` | `MC_BufferMode` | — | 队列模式：当轴正在执行另一命令时本命令的接入方式（`MC_Aborting` / `MC_Buffered` / `MC_BlendingLow` / `MC_BlendingPrevious` / `MC_BlendingNext` / `MC_BlendingHigh`）；耦合从轴只允许 `Aborting` |
| `Options` | `ST_MoveOptions` | — | 额外可选参数结构，绝大部分场景留默认即可 |

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
| `Done` | `BOOL` | 目标到达 / 命令完成时置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 上升沿后立即变 `TRUE`，结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE` |
| `Active` | `BOOL` | 表示**当前正在执行**本 FB 的命令；若被 `BufferMode` 缓冲则要等前一命令完成才变 `TRUE` |
| `CommandAborted` | `BOOL` | 命令未完成就被中止（被另一 Move 抢占 / `MC_Stop` 停掉）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |

## 3. 行为说明

**触发**：`Execute` 上升沿启动模数定位。模数因子（如 360°）来自轴参数 → 模数设置。

**静止启动**：`Position` 可以 ≥ 360°；例如轴在 0°，`Position := 720`、`Direction := MC_Positive_Direction` 会让轴正向转 2 圈到 0°。`BufferMode := MC_Buffered` 时同样适用。

**运动中启动**：圈数由系统按"最短路径"自动算，**用户无法指定额外圈数**。需要评估 `Error`，因为某些情况下"定向停车（oriented stop）"无法完成：例如不久前发了 standard stop，或软限位在路径上。这类情况下轴被安全停下但**最终位置不一定是目标位置**。

**特殊情形**：轴正好停在设定的目标处（如 90°）再发"到 90°"，**不会有任何运动**；若发"正方向走 450°"则只转一圈到 90°。`MC_Reset` 后当前实际位置被采纳为设定位置，可能略偏 90°——这时再发同样命令行为会突变（要么微动到 90°，要么转一整圈）。

**与 `MC_MoveAbsolute` 抉择**：完整模数旋转（精确转 N 圈）建议算出绝对目标位置后用 `MC_MoveAbsolute`，行为更可预测。

**模数/绝对定位与 System Manager 设置无关**：每根轴都可用绝对/模数两种定位，取决于业务调用哪个 FB；当前绝对位置 `SetPos` 可从 `NCTOPLC_AXIS_REF` 循环数据读出。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **`Position` 不许负**：模数语义里不存在负角度；要反向请用 `Direction := MC_Negative_Direction`。
- **运动中改向不允许**：轴正在沿正方向走，触发新命令 `Direction := MC_Negative_Direction` 会报错。
- **`MC_ShortestWay` 实际方向不确定**：若起点和终点角度差恰好 180°，"最短"可能取正可能取负，依赖浮点；机械有方向偏好的应固定 `Positive` 或 `Negative`。
- **轴位置恰好等于目标位置 = 不动**：自动化场景里"每周期触发一次走到 X 度"在 X 与当前位完全相同时变成 NOP，常导致"看 Busy 一直没起来"的诡异现象。（工程经验补充）
- **`MC_Reset` 重新采纳实际位置后行为突变**：见 §3 末段；生产工艺对位置精度敏感时应在 Reset 后先做一次 `MC_Home` 或绝对定位再走模数。
- **要精确"转 N 圈"建议用 `MC_MoveAbsolute`**：算出 currentPos + 360°×N 给绝对定位，避免运动中触发被系统改成最短路径。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_MoveModulo.xml`](../examples/P_Demo_MC_MoveModulo.xml)

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

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.1.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70099339.html
- **相关 FB**：`MC_MoveAbsolute`、`MC_MoveRelative`、`MC_MoveVelocity`
