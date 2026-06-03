# MC_ReadStatus_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Administrative` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599680395.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_ReadStatus_BkPlcMc.TcPOU`](../examples/P_Demo_MC_ReadStatus_BkPlcMc.TcPOU) |

---

## 1. 功能简述

按 PLCopen 状态机定义解码液压轴当前状态的功能块。每周期把轴的内部 `nStateDWord` 翻译成 11 个独立 BOOL 输出：`Errorstop` / `Disabled` / `Stopping` / `StandStill` / `DiscreteMotion` / `ContinousMotion` / `SynchronizedMotion` / `Homing` / `ConstantVelocity` / `Accelerating` / `Decelerating`。同一时刻轴只可能处于"主状态机"的某一个状态（互斥），但 `Accelerating` / `Decelerating` / `ConstantVelocity` 是"速度子状态"可与主状态并存。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Enable:              BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Enable` | `BOOL` | — | `TRUE` 触发状态刷新；持续高即持续刷新 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis:               AXIS_REF_BkPlcMc;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF_BkPlcMc` | 轴接口结构。必须以 `VAR_IN_OUT` 方式传引用 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Busy:               BOOL;
    Valid:              BOOL;
    Error:              BOOL;
    ErrorID:            UDINT;
    Errorstop:          BOOL;
    Disabled:           BOOL;
    Stopping:           BOOL;
    StandStill:         BOOL;
    DiscreteMotion:     BOOL;
    ContinousMotion:    BOOL;
    SynchronizedMotion: BOOL;
    Homing:             BOOL;
    ConstantVelocity:   BOOL;
    Accelerating:       BOOL;
    Decelerating:       BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | 命令处理中。本 FB 不需任何时间，`Busy` 永远为 `FALSE` |
| `Valid` | `BOOL` | 状态解码成功 |
| `Error` | `BOOL` | 本 FB 自身错误指示（不是轴错误） |
| `ErrorID` | `UDINT` | 本 FB 自身错误码 |
| `Errorstop` | `BOOL` | 轴处于错误停止状态。只能通过 `MC_Reset_BkPlcMc` 或 `MC_ResetAndStop_BkPlcMc` 清除 |
| `Disabled` | `BOOL` | 轴未由 `MC_Power_BkPlcMc` 使能 |
| `Stopping` | `BOOL` | 正在被 `MC_Stop_BkPlcMc` 或 `MC_ResetAndStop_BkPlcMc` 减速停车；轴静止后该位清 |
| `StandStill` | `BOOL` | 轴既无错误也无运动（"待命"状态） |
| `DiscreteMotion` | `BOOL` | 轴正在执行带明确目标的自主运动（非耦合，如 MoveAbsolute / MoveRelative） |
| `ContinousMotion` | `BOOL` | 轴正在执行恒速无目标的自主运动（如 MoveVelocity）。⚠️ PDF 原拼写漏 `u`，本仓库严格按 PDF 搬运 |
| `SynchronizedMotion` | `BOOL` | 轴正在被齿轮耦合控制（GearIn / CamIn） |
| `Homing` | `BOOL` | 轴正在执行归零（`MC_Home_BkPlcMc`） |
| `ConstantVelocity` | `BOOL` | 轴正在以恒定速度运动 |
| `Accelerating` | `BOOL` | 轴正在向指定速度趋近。⚠️注意：若运动中的轴接到反方向的速度指令，从原方向看是"减速"但从新方向看仍是"加速"——本字段反映"向新指令速度趋近"的方向 |
| `Decelerating` | `BOOL` | 轴正在降速以达到指定速度 |

## 3. 行为说明

**调用模式**：每周期调用，电平触发。

**PLCopen 状态机互斥关系**：以下 8 个主状态在任意时刻**互斥**，同时只有一个为 `TRUE`：
- `Disabled` / `StandStill` / `Errorstop` / `Stopping` / `DiscreteMotion` / `ContinousMotion` / `SynchronizedMotion` / `Homing`

而以下 3 个速度子状态与主状态**并存**（描述当前速度趋势）：
- `Accelerating` / `ConstantVelocity` / `Decelerating`

例如：执行 `MC_MoveAbsolute_BkPlcMc` 期间，`DiscreteMotion = TRUE`，同时根据速度曲线 `Accelerating` → `ConstantVelocity` → `Decelerating` 依次为 `TRUE`。

**状态转换示例**：
- 上电后 / 撤 `MC_Power_BkPlcMc.Enable`：`Disabled = TRUE`
- `MC_Power_BkPlcMc.Enable := TRUE` + 无错：`StandStill = TRUE`
- 发任何运动命令：`StandStill → DiscreteMotion / ContinousMotion / SynchronizedMotion / Homing`
- 运动中遇错：→ `Errorstop`
- `MC_Stop_BkPlcMc` 命令：→ `Stopping`（减速中）→ 停下后 → `Errorstop`（因为 MC_Stop 会锁轴）
- `MC_Reset_BkPlcMc`：`Errorstop` → `StandStill`

**典型用法**：业务代码用 `StandStill` 判断"可以发新命令"；用 `Errorstop` 触发报警；用 `DiscreteMotion` 显示"运动中"动画；速度子状态用于显示加速度阶段（HMI 画曲线）。

**典型陷阱**：
- 没看到任何状态为 `TRUE`：先确认 `Enable := TRUE` 且 `Valid = TRUE`
- 用 `StandStill` 判"运动完成"：`StandStill` 在初始未发命令时也是 `TRUE`，要判"运动完成"应看具体运动 FB 的 `Done` 字段
- `Stopping` 时新发命令：会被忽略或排队；应等 `Stopping → Errorstop` 然后 `MC_Reset_BkPlcMc` → `StandStill`

## 4. 错误码 / 返回值

本 FB 自身不会产生错误（`Error` 永远 `FALSE`，`ErrorID` 永远 0）。要读轴本身的错误码用 `MC_ReadAxisError_BkPlcMc`。

## 5. 使用注意 / 常见坑

- **`ContinousMotion` PDF 拼写漏 `u`**：API 字段名严格是 `ContinousMotion`（不是 `ContinuousMotion`），编译会过；不要"修正"为标准英文拼写，否则编译错。
- **主状态互斥 / 速度子状态并存**：判"是否在运动"应看 `DiscreteMotion OR ContinousMotion OR SynchronizedMotion OR Homing`；判"加速段还是匀速段"看 `Accelerating` / `ConstantVelocity` / `Decelerating`。
- **`Stopping` 完成后是 `Errorstop` 不是 `StandStill`**：`MC_Stop_BkPlcMc` 设计上会把轴锁到 Errorstop 状态，必须 `MC_Reset_BkPlcMc` 才能再发新命令。如果只想"软停"不锁轴用 `MC_Halt_BkPlcMc`。
- **`Busy` 永远 FALSE**：判读取完成看 `Valid`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_ReadStatus_BkPlcMc.TcPOU`](../examples/P_Demo_MC_ReadStatus_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机液压轴 HMI 主控面板。需要同时显示轴状态指示灯（待命 / 运动中 / 急停 / 归零）、速度趋势（加 / 匀 / 减）、错误状态。
- **价值**：手写需要解析 `pStAxRtData^.nStateDWord` 的各个 bit（不同 mask 对应不同状态），还要处理 PLCopen 标准要求的互斥关系；本 FB 一次调用直接拿到 11 个独立 BOOL，与 PLCopen 标准状态机完全对应。
- **替代方案对比**：
  - 解析 `nStateDWord` bit：要熟记 `dwTcHydNsDw*` mask 含义
  - 用各 Read* FB 单独读：复杂业务需要状态机判断时仍要凑齐这些 bit
  - **本 FB**：一站式状态解码，与 PLCopen 标准对齐

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.1.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599680395.html
- **相关 FB**：`MC_ReadAxisError_BkPlcMc`（读错误码数值）、`MC_Reset_BkPlcMc`（Errorstop → StandStill）、`MC_Power_BkPlcMc`（控制 Disabled 状态）

## 9. 待确认项 (⚠️)

- PDF 输出字段拼写为 `ContinousMotion`（漏 `u`）；本仓库严格按 PDF 字面搬运，不"修正"为 `ContinuousMotion`。
