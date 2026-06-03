# MC_MoveVelocity_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion - Single axis` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599704843.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_MoveVelocity_BkPlcMc.TcPOU`](../examples/P_Demo_MC_MoveVelocity_BkPlcMc.TcPOU) |

---

## 1. 功能简述

PLCopen 风格**恒速运动**功能块（液压库实现）。`Execute` 上升沿启动一次"沿 `Direction` 方向以 `Velocity` 恒速运行至软限位"的运动；速度第一次达到 `Velocity` 时 `InVelocity := TRUE`。无明确目标位置（直到撞软限位或被另一 FB 停下）。本 FB 唯一独有的输出是 `InVelocity`（与 Done 不同——Done 表示"到目标完毕"，InVelocity 表示"速度已达到"）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute:        BOOL;
    Velocity:       LREAL;
    Acceleration:   LREAL;
    Deceleration:   LREAL;
    Direction:      MC_Direction_BkPlcMc;
    BufferMode:     MC_BufferMode_BkPlcMc:=Aborting_BkPlcMc;    //from V3.0.8
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次恒速运动 |
| `Velocity` | `LREAL` | — | 目标恒速值，单位 mm/s。要求 > 1% 参考速度 |
| `Acceleration` | `LREAL` | — | 加速度，单位 mm/s² |
| `Deceleration` | `LREAL` | — | 减速度，单位 mm/s² |
| `Direction` | `MC_Direction_BkPlcMc` | — | 方向枚举（`MC_Positive_Direction_BkPlcMc` / `MC_Negative_Direction_BkPlcMc` 等） |
| `BufferMode` | `MC_BufferMode_BkPlcMc` | `Aborting_BkPlcMc` | 保留（自 V3.0.8 起加入） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis:           AXIS_REF_BkPlcMc;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF_BkPlcMc` | 轴接口结构。必须以 `VAR_IN_OUT` 方式传引用 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Busy:           BOOL;
    InVelocity:     BOOL;
    CommandAborted: BOOL;
    Error:          BOOL;
    ErrorID:        UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | 命令处理中（恒速运动期间一直 TRUE） |
| `InVelocity` | `BOOL` | 轴速度**第一次**达到 `Velocity` 时置 `TRUE` 并保持；不像 Done 那样表示"完成" |
| `CommandAborted` | `BOOL` | 被另一运动 FB 打断 |
| `Error` | `BOOL` | 启动检查或运动算法报错 |
| `ErrorID` | `UDINT` | 错误码 |

## 3. 行为说明

**调用模式**：边沿触发。`Execute` 上升沿启动；下降沿清输出但不停轴（恒速会继续直到撞软限位）。

**启动检查**：
1. 算法可启动性 → 不可启动 `dwTcHydErrCdNotStartable`
2. 轴在错误/停车中 → `dwTcHydErrCdNotReady`
3. `Velocity` < 1% 参考速度 → `dwTcHydErrCdSetVelo`
4. 算法已持错码 → `Error` + 算法错码

**目标位置选择**：根据 `Direction` 和软限位参数选定**软限位位置**作为目标位置（即"一直走到边界"）。这样运动算法仍按"绝对定位到软限位"运行，但用户感觉是"恒速走"。

**运动监视**：进入 `McState_Continousmotion`；FB 监视速度。第一次到达 `Velocity` → `InVelocity := TRUE` 并保持；被打断 → `CommandAborted`；算法错 → `Error`。**没有 Done 字段**——恒速运动没有"完成"的概念。

**典型用法**：
- 比例阀手动测试模式：让阀按 200 mm/s 持续运动检查液压响应
- 卸荷动作：以低速持续退到卸荷位再触发 Stop
- 进料 / 收料运动：传送带式连续推料

**典型陷阱**：
- 期望 `Done`：本 FB 没有 Done，要"运动结束"信号要主动调 Stop/Halt 然后看那个 FB 的 Done
- `InVelocity` 不是"完成"：是"已加速到目标速度"。撤 Execute 也不影响 InVelocity
- 撞软限位：FB 不主动停车，运动一直到限位触发后报错；要在到达某点停下必须主动发 Stop
- 多次触发同一 FB 实例：第二次会被算法判 NotStartable

## 4. 错误码 / 返回值

| `ErrorID` 常量 | 含义 | 处理建议 |
|---|---|---|
| `dwTcHydErrCdNotStartable` | 算法不可启动 | 等轴静止 |
| `dwTcHydErrCdNotReady` | 轴在错误/停车中 | `MC_Reset_BkPlcMc` 清错 |
| `dwTcHydErrCdSetVelo` | `Velocity` 太小 | 增大 |
| (算法错码) | 运动中算法报错 | 查 PDF §5.2 |

## 5. 使用注意 / 常见坑

- **没有 Done 字段**：用 `InVelocity` 看"是否到目标速度"；用 `MC_Stop_BkPlcMc` 主动停后看那个 FB 的 Done。
- **运动不自动停**：会一直走到软限位才报错；要在某点停必须主动调 Stop 或 Halt。
- **`Direction` 是必填**：不像 Absolute/Relative 的方向由位置/距离决定。
- **`InVelocity` 是"latched"语义**：第一次到达后保持 TRUE 即使后续速度因负载波动短暂偏离也不清。
- **跨任务调用**：与其它运动 FB 同样需要避免竞态；一根轴一个运动实例。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_MoveVelocity_BkPlcMc.TcPOU`](../examples/P_Demo_MC_MoveVelocity_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：液压注塑机塞料螺杆。退料工序需要螺杆以恒速反向旋转把料筒中的塑料颗粒拉到螺杆前端；预定时长（如 8 秒）后停下进入预塑段。本 FB 启动"反向恒速旋转"，业务侧定时器到点后调 `MC_Stop_BkPlcMc` 停车。
- **价值**：手写需要在算法层切到 ExtGen 模式自己写速度环；本 FB 标准接口，启动一次即恒速。
- **替代方案对比**：
  - `MC_MoveJoySticked_BkPlcMc`：摇杆式连续控制速度可变；本 FB 是恒速
  - 自己写算法层 ExtGen：灵活但侵入性强
  - **本 FB**：标准恒速接口

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.2.16
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599704843.html
- **相关 FB**：`MC_MoveJoySticked_BkPlcMc`（连续可变速度）、`MC_Stop_BkPlcMc`（主动停车）、`MC_Halt_BkPlcMc`（软停车）
