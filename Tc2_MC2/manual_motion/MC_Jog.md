# MC_Jog

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2` |
| Library Version | `2.17.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Manual motion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70120459.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_Jog.TcPOU`](../examples/P_Demo_MC_Jog.TcPOU) |

---


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
| `Acceleration` | `LREAL` | — | 加速度，要求 `≥0`；填 `0` 表示采用轴参数中默认加速度；`STANDARD_*` 模式忽略 |
| `Deceleration` | `LREAL` | — | 减速度，要求 `≥0`；填 `0` 表示采用轴参数中默认减速度；`STANDARD_*` 模式忽略 |
| `Jerk` | `LREAL` | — | 加加速度（Jerk），要求 `≥0`；填 `0` 表示采用轴参数中默认 Jerk；`STANDARD_*` 模式忽略 |

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
    CommandAborted : BOOL;
    Error          : BOOL;
    ErrorID        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 一段 Jog 动作完成（寸动一格 / 按钮松开后轴停） |
| `Busy` | `BOOL` | `Execute` 上升沿后立即变 `TRUE`，结束（无论 Done/Aborted/Error）才变 `FALSE`；FB 可接受新命令的前提是 `Busy = FALSE` |
| `CommandAborted` | `BOOL` | 命令未完成就被中止（被另一 Move 抢占 / `MC_Stop` 停掉）时置 `TRUE` |
| `Error` | `BOOL` | 执行期间发生错误置 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出 NC 错误号（不是 HRESULT，参见 §4） |

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

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC 错误号（**不是** HRESULT）。常见类别：

| 错误码段 | 含义 | 处理建议 |
|---|---|---|
| `16#4550` 段（0x4550…） | NC 通道命令错误（参数越界、轴非 Ready、目标超软限位等） | 检查 `Velocity > 0`、轴是否 `MC_Power` 后 `Status.Ready = TRUE`、目标在软限位内 |
| `16#4260`、`16#4261` 等 | 跟随误差超限、紧急停止激活 | `MC_Reset` 清错后再 retry；持续出现需检查机械/伺服参数 |
| 其他 | 完整列表见 Beckhoff `Tc2_MC2` PDF 附录 `Overview of axis error codes` 或 InfoSys 主题 `E_AxisErrorCodes` | ⚠️ PDF 在本 FB 章节未逐条列出具体错误码，请参见 NC 错误码总表 |

**清错**：本 FB 自身不带清错入口；需调用 `MC_Reset(Axis)` 把轴从 Errorstop 拉回 Standstill 才能继续发新命令。


## 5. 使用注意 / 常见坑

- **运动中无视按钮变化**：开始走以后再按反方向无效，必须先把当前方向松开。
- **`STANDARD_*` 模式下 Velocity 不生效**：很多新手在 STANDARD_FAST 下改 `Velocity` 入口不解为何没反应——这两模式用的是 System Manager 配置不是 FB 入口。
- **`INCHING` 模式下按钮按住不影响**：触发即走一段，不会因为按钮一直按继续走。要"按住一直走"应该选 `CONTINOUS`。
- **两按钮同时按 JogForward 优先**：硬件上别指望"同时按表示停"，要停得双都松开。
- **没有上锁机制**：Jog 不锁轴，所以 Jog 中其它代码发 Move 命令可以抢；调试时应禁止业务程序与 Jog 同时启用。（工程经验补充）
- **HMI 设计要把按钮接到电平变量而非脉冲变量**：JogForward 是电平触发（除 inching），如果 HMI 给的是"按一次发 100 ms 脉冲"会出怪异行为。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_Jog.TcPOU`](../examples/P_Demo_MC_Jog.TcPOU)

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

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf) §6.4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70120459.html
- **相关 FB**：`MC_MoveVelocity`、`MC_Halt`、`E_JogMode`（枚举定义）
