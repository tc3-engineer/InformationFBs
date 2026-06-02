# MC_SetPosition

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_DriveMotionControl` |
| Library Version | `1.5.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `Axis functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8278986251.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_SetPosition.TcPOU`](../examples/P_Demo_MC_SetPosition.TcPOU) |

---

## 1. 功能简述

PLCopen Motion Control 标准定义的**设置轴位置功能块（Function Block, FB）**。`Execute` 上升沿触发一次，把轴当前位置设为一个可参数化的值（坐标重定义），**轴本身不发生物理运动**。

支持两种模式：**绝对模式**把实际位置直接设为 `Position` 给定的绝对值；**相对模式**把实际位置在原值基础上偏移 `Position`。两种模式下默认都会**保留已有的跟随误差**；若要顺带清除跟随误差，置 `Options.ClearPositionLag`。相对模式还可用于在运动过程中改变轴位置坐标。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute  : BOOL;
    Position : LREAL;
    Mode     : BOOL; (* RELATIVE=True, ABSOLUTE=False (Default) *)
    Options  : ST_SetPositionOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次命令 |
| `Position` | `LREAL` | — | 要把轴位置设成的值：绝对模式下实际位置被设为此值；相对模式下实际位置在原值上偏移此值 |
| `Mode` | `BOOL` | — | `FALSE` = 绝对模式（把轴位置设为绝对值，为默认）；`TRUE` = 相对模式（在当前位置上偏移 `Position`）。相对模式可用于运动过程中改变轴位置 |
| `Options` | `ST_SetPositionOptions` | — | 附加可选参数结构。PDF 标注"当前未使用（Not used at present）"。其中 `ClearPositionLag` 用于清除跟随误差 |

> 注：PDF VAR 区把 `Mode` 的默认行为以注释 `(* RELATIVE=True, ABSOLUTE=False (Default) *)` 形式给出，类型本身无 `:=` 字面默认值。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | 轴数据结构，在系统中唯一标识一根轴；含当前轴状态，包括位置、速度、错误状态等。**必须传引用**（VAR_IN_OUT 语义） |

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
| `Done` | `BOOL` | 位置设置成功时置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 启动命令后置 `TRUE` 并持续到命令处理结束；`Busy = FALSE` 时 FB 可接受新命令，同时 `Done` 或 `Error` 之一置位 |
| `Error` | `BOOL` | 发生错误时为 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出错误号（参见 §4） |

## 3. 行为说明

**触发语义**：`Execute` **上升沿**触发一次设置。上升沿后 `Busy` 置 `TRUE`，设置完成后 `Done` 置 `TRUE`、`Busy` 落 `FALSE`；输出遵循库通用规则（`Busy` / `Done` / `Error` 互斥）。`Execute` 空闲时落 `FALSE` 会复位 `Done` / `Error`。

**绝对模式（`Mode = FALSE`，默认）**：把轴的实际位置直接**重定义**为 `Position` 值。常用于归零后把某机械参考点定义为坐标原点，或把当前位置标定为某已知绝对坐标。注意这只改坐标读数，轴不动。

**相对模式（`Mode = TRUE`）**：把实际位置在原值上**偏移** `Position`。一个关键特性是相对模式**可以在运动过程中执行**——即轴在动的时候平移其坐标系而不打断运动，用于运动中的坐标校正。

**跟随误差的处理**：两种模式下，轴的设定位置都被设置成**保留现有跟随误差**（lag error）的形式，即设置位置后跟随误差不被人为抹掉。若希望同时把跟随误差清零，置 `Options.ClearPositionLag`。

**不产生运动**：本 FB 是"改坐标读数"而非"移动到某坐标"。要让轴物理移动到某绝对位置请用 `MC_MoveAbsolute`。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC/驱动错误号（不是 HRESULT）。

| 返回值 / 错误码 | 含义 | 处理建议 |
|---|---|---|
| `Done = TRUE` | 位置设置成功 | 坐标读数已更新到目标值 |
| `Error = TRUE` + `ErrorID ≠ 0` | 设置失败（轴状态不允许、参数非法等） | 检查轴是否处于可设置状态；必要时 `MC_Reset` 清错后重试 |

PDF 与 InfoSys 在本 FB 章节均未逐条列出具体 `ErrorID` 码值，具体码值需对照 TwinCAT NC 错误码总表（⚠️ PDF + InfoSys 本章节未枚举）。

## 5. 使用注意 / 常见坑

- **`MC_SetPosition` 不让轴动**：它只改坐标读数。把它当成"移动到某坐标"是典型误解；要物理移动用 `MC_MoveAbsolute`。
- **`Mode` 的默认是绝对**：`Mode = FALSE`（绝对）。注释里写明 `ABSOLUTE=False (Default)`；不显式赋值时按绝对处理。
- **相对模式可在运动中用**：这是它区别于"先停轴再设位置"的价值点——运动中平移坐标系不打断运动。绝对模式则一般在静止时用。
- **默认保留跟随误差**：设置后跟随误差不被抹掉；要清零须显式置 `Options.ClearPositionLag`。误以为设位置会顺带清跟随误差会导致后续判断偏差。
- **`Options` 当前主要为预留**：PDF 标注"Not used at present"，除 `ClearPositionLag` 外一般留默认。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_SetPosition.TcPOU`](../examples/P_Demo_MC_SetPosition.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：卷料轴每换一卷料，把当前料头位置重定义为坐标 0，后续按绝对长度切料
PROGRAM P_Demo_MC_SetPosition
VAR
    fbSetPos        : MC_SetPosition;
    axisWebFeed     : AXIS_REF;
    rtNewRoll       : R_TRIG;              // 换卷信号转上升沿
    bNewRollLoaded  : BOOL := FALSE;       // 在线写 TRUE 表示新卷已装、料头已对位
    lrZeroPosition  : LREAL := 0.0;        // 把料头位置重定义为 0 mm
    bSetDone        : BOOL;
    bSetBusy        : BOOL;
    bSetError       : BOOL;
    nSetErrorID     : UDINT;
END_VAR

// 换卷后把当前位置设为绝对 0（Mode := FALSE 绝对模式）；Axis 是 VAR_IN_OUT 用 :=
rtNewRoll(CLK := bNewRollLoaded);
fbSetPos(
    Execute  := rtNewRoll.Q,
    Position := lrZeroPosition,
    Mode     := FALSE,
    Axis     := axisWebFeed,
    Done     => bSetDone,
    Busy     => bSetBusy,
    Error    => bSetError,
    ErrorID  => nSetErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：卷料 / 收放卷设备换卷后把料头重定义为坐标原点；机械归零后把参考点标定为已知绝对坐标；运动中需要平移坐标系做在线校正（相对模式）。共同点是"重定义坐标读数"而非"移动到某处"。
- **价值**：业务代码不必去拼 NC 轴的 SetActPos 命令、不必自己处理跟随误差保留逻辑，单个 FB 调用即完成坐标重定义；相对模式还允许运动中校正，省去"停轴 → 设位置 → 重启"的繁琐流程。
- **替代方案对比**：
  - 直接写 NC SetActPos 命令：要熟悉 NC 接口命令字，且跟随误差处理要自己管
  - 用 `MC_Home` 的 `MC_Direct` 模式：也能直接设位置，但语义偏向"归零标定"；纯坐标重定义用 `MC_SetPosition` 更直接
  - **本 FB**：PLCopen 标准的坐标重定义入口，绝对 / 相对两模式覆盖标定与在线校正两类需求

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf) §5.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8278986251.html
- **相关 FB**：`MC_Home`（归零，含直接设位置模式）、`MC_MoveAbsolute`（物理移动到绝对位置）、`MC_Reset`（清错）
