# MC_ResetAndStop_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Administrative` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599682443.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_ResetAndStop_BkPlcMc.TcPOU`](../examples/P_Demo_MC_ResetAndStop_BkPlcMc.TcPOU) |

---

## 1. 功能简述

把出错的液压轴置入可操作状态**并**确保停车的复合功能块。`Execute` 上升沿同时触发两件事：① 取消当前正在执行的运动命令；② 用 `Deceleration` / `Jerk` / `RampTime` 给出的减速曲线把轴停下；③ 把轴错误状态清掉。两步都成功才 `Done := TRUE`。`MC_Reset_BkPlcMc` 只清错不停车——本 FB 是"清错并停车"的复合版。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute:        BOOL;
    Deceleration:   LREAL;  //from V3.0.5
    Jerk:           LREAL;  //from V3.0.5
    RampTime:       LREAL;  //from V3.0.5
    BufferMode:     MC_BufferMode_BkPlcMc:=Aborting_BkPlcMc;  //from V3.0.8
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次复位+停车 |
| `Deceleration` | `LREAL` | — | 减速度，单位 mm/s²（自 V3.0.5 起加入）。≤0 时采用轴参数默认 |
| `Jerk` | `LREAL` | — | 加加速度（jerk），单位 mm/s³（自 V3.0.5 起加入）。≤0 时采用默认 |
| `RampTime` | `LREAL` | — | 所需停车时间，单位 s（自 V3.0.5 起加入）。给定后内部据此计算 Deceleration |
| `BufferMode` | `MC_BufferMode_BkPlcMc` | `Aborting_BkPlcMc` | 保留，当前仅允许 `Aborting_BkPlcMc`（自 V3.0.8 起加入） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis:       AXIS_REF_BkPlcMc;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF_BkPlcMc` | 轴接口结构。必须以 `VAR_IN_OUT` 方式传引用 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Busy:       BOOL;
    Done:       BOOL;
    Error:      BOOL;
    ErrorID:    UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | 复位/停车进行中。停车需要时间或驱动器握手时为 `TRUE` |
| `Done` | `BOOL` | 复位+停车都成功；轴已 StandStill 且无错 |
| `Error` | `BOOL` | 复位或停车失败 |
| `ErrorID` | `UDINT` | 失败时给出轴的错误码 |

## 3. 行为说明

**调用模式**：边沿触发。`Execute` 上升沿启动复合动作。

**执行步骤**：
1. 检查轴接口；若发现故障源未消除 → 直接 `Error`、`ErrorID := 轴错误码`
2. 若轴正在运动 → 用 `Deceleration` / `Jerk`（或 `RampTime`）减速到 0
3. 停车过程中若出新错 → `Error`、`ErrorID := 新错码`
4. 两步都成功（轴静止 + 无错）→ `Done := TRUE`

**与 `MC_Reset_BkPlcMc` 的对比**：
- `MC_Reset_BkPlcMc`：只清错。轴在运动中（异常情况）调用，可能运动继续
- `MC_ResetAndStop_BkPlcMc`：清错 + 强制停车。等动作完成才 `Done`

**与 `MC_Stop_BkPlcMc` 的对比**：
- `MC_Stop_BkPlcMc`：停车并锁轴（停下后进 Errorstop）
- `MC_ResetAndStop_BkPlcMc`：停车并清错（停下后进 StandStill）。"安全停车后继续生产"用本 FB

**典型用法**：
- 急停拉起后：先操作员排查现场，按"恢复"按钮触发本 FB，确保液压轴在已知静止位置后再清错
- 工艺异常后恢复：检测到压力异常自动停车 + 清错，操作员介入处理

**典型陷阱**：
- 给 0 的 `Deceleration`：会用轴参数默认值，可能比预期慢（液压轴大惯量减速时间长）
- 没等 `Done` 就发新命令：可能正在 `Busy` 期间被打断，结果未定义
- 用本 FB 代替急停：本 FB 是"软停"，不切液压源；急停应另接硬件回路

## 4. 错误码 / 返回值

| `Done` | `Busy` | `Error` | `ErrorID` | 含义 |
|---|---|---|---|---|
| `TRUE` | `FALSE` | `FALSE` | `0` | 成功（轴已 StandStill 且无错） |
| `FALSE` | `TRUE` | `FALSE` | `0` | 复位 / 停车进行中 |
| `FALSE` | `FALSE` | `TRUE` | = 轴错误码 | 复位 / 停车失败 |

⚠️ 具体 `ErrorID` 数值参见 PDF §5.2 全局常量。

## 5. 使用注意 / 常见坑

- **`Deceleration` / `Jerk` / `RampTime` 三选一**：通常给 `Deceleration` + `Jerk`，`RampTime` 留 0；或只给 `RampTime` 让 FB 自己算 Deceleration。三个都给可能内部以 `RampTime` 为主。
- **停车后是 StandStill 不是 Errorstop**：与 `MC_Stop_BkPlcMc` 区别明显；想"停车后再发新命令"用本 FB。
- **PDF/InfoSys 都没枚举 ErrorID**：失败时给的是轴本身的 `nErrorCode`；要排查具体原因要结合 `MC_ReadAxisError_BkPlcMc`。
- **不是急停替代品**：本 FB 软件实现，遇到 PLC 死循环就失效；真正急停必须硬件回路（24V 断电、液压源断电）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_ResetAndStop_BkPlcMc.TcPOU`](../examples/P_Demo_MC_ResetAndStop_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机急停拉起后的恢复流程。操作员检查模具内无障碍、油压正常、温度正常后，按"安全恢复"按钮触发本 FB。FB 把液压锁模轴用预设 500 mm/s² 的减速度刹住（如果还在动），同时清掉轴错误状态。等 `Done = TRUE` 再允许操作员手动 jog 回零位准备下一周期。
- **价值**：手写需要：① 调 `MC_Stop` 把轴停掉；② 等停下后看 `Errorstop = TRUE`；③ 调 `MC_Reset` 清错；④ 等 `Done`。本 FB 一次调用完成全流程，并由 FB 内部保证两步顺序正确。
- **替代方案对比**：
  - `MC_Stop_BkPlcMc` + `MC_Reset_BkPlcMc`：两步式，需自己处理时序与状态判断
  - `MC_Reset_BkPlcMc` 单独：不停车，轴还在动就清错可能很危险
  - **本 FB**：一站式安全恢复，停车+清错原子化

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.1.11
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599682443.html
- **相关 FB**：`MC_Reset_BkPlcMc`（纯清错）、`MC_Stop_BkPlcMc`（停车并锁轴）、`MC_EmergencyStop_BkPlcMc`（带斜坡急停）
