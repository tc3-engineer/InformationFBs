# MC_EmergencyStop_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion - Single axis` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599694603.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_EmergencyStop_BkPlcMc.TcPOU`](../examples/P_Demo_MC_EmergencyStop_BkPlcMc.TcPOU) |

---

## 1. 功能简述

液压库**软件急停**功能块（PLCopen 标准之外的扩展）。`Execute` 上升沿启动一次"取消当前运动并按 `RampTime` 时间斜坡减速到 0"的急停动作。**急停特性**：在控制值降到 0 之后，只要 `Execute` 仍为 `TRUE`，所有控制 / 调节电压输出**保持抑制**——即液压阀输出强制为 0，避免任何残余输出导致漂移。内部用 `MC_Stop_BkPlcMc` 做减速。**注意：本 FB 是软件急停，不能替代硬件急停回路。**

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute:        BOOL;
    RampTime:       LREAL;  //from V3.0.5
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 电平驱动急停。上升沿启动；持续高维持电压抑制；下降沿撤销 |
| `RampTime` | `LREAL` | — | 停车时间，单位 s（自 V3.0.5 起加入）。≤0 用轴参数 `fEmergencyRamp` |

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
    Done:           BOOL;
    Error:          BOOL;
    ErrorID:        UDINT;
    Active:         BOOL;
    CommandAborted: BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | 命令处理中 |
| `Done` | `BOOL` | 急停成功（速度已 = 0） |
| `Error` | `BOOL` | 启动检查或停车算法错 |
| `ErrorID` | `UDINT` | 错误码 |
| `Active` | `BOOL` | 命令活动中 |
| `CommandAborted` | `BOOL` | 被另一 FB 打断 |

## 3. 行为说明

**调用模式**：**电平触发**（与 Halt/Stop 的边沿触发不同）。`Execute` 上升沿启动减速；维持高电平期间持续抑制控制电压输出；下降沿撤销抑制（轴可被其它 FB 重新控制）。

**启动检查**：
1. **轴必须有运动可停**：轴已静止 → 立即 `Done := TRUE`
2. **轴在错误/停车中**：→ `Error`、`ErrorID := dwTcHydErrCdNotReady`
3. **轴被耦合控制**：→ `Error`、`ErrorID := dwTcHydErrCdNotReady`

**停车算法**：`RampTime` 按参考速度算出减速度；用 jerk-limited 生成器时同时用 `MaxJerk`。`RampTime ≤ 0` 时用轴参数 `fEmergencyRamp`（这是为急停专门准备的默认值）。

**控制电压抑制**：PDF 关键描述："Once the control value output is reduced to 0, all control or regulating voltage outputs are suppressed, as long as Execute is set to TRUE." 即减速到 0 后，**只要 `Execute` 仍为 TRUE**，FB 持续把所有阀控电压输出固定为 0。这避免了"减速完成后阀回到设定值导致轴又开始漂"。

**内部实现**：内部实例化一个 `MC_Stop_BkPlcMc` 做减速过程；本 FB 在 Stop 之外额外加电压抑制。

**典型用法**：
- 上位机触发的软急停（与硬件急停回路冗余）
- 安全门打开信号触发的工艺停车（不需要硬件继电器但需要电压抑制）
- 测试 / 调试时的紧急保护

**典型陷阱**：
- **当硬件急停用**：本 FB 是软件实现，遇 PLC 死循环或扫描周期延迟就失效；安全等级要求高的应用必须用硬件急停回路（24V 断电 / 液压源断电）
- 撤 `Execute` 后立即接 Move：`Execute := FALSE` 撤销电压抑制后轴可被控制，但前面急停过程没 Reset，可能仍在 Errorstop（内部 Stop 的副作用）
- `RampTime = 0`：用 `fEmergencyRamp` 默认（通常很短，注意冲击）

## 4. 错误码 / 返回值

| `ErrorID` 常量 | 含义 | 处理建议 |
|---|---|---|
| `dwTcHydErrCdNotReady` | 轴在错误状态 / 已在停车 / 被耦合 | Reset 或 GearOut |
| (算法错码) | 内部 Stop 报错 | 查 PDF §5.2 |

## 5. 使用注意 / 常见坑

- **不是硬件急停替代品**：本 FB 软件实现，安全等级有限；高安全等级场景必须配合 SIL 认证的硬件急停回路。
- **`Execute` 是电平触发**：与 Halt/Stop 边沿触发不同；持续高才维持电压抑制。
- **撤 `Execute` 不自动清错**：仍需 `MC_Reset_BkPlcMc` 才能再发新命令（取决于内部 Stop 把轴置入了什么状态）。
- **`fEmergencyRamp` 是急停专用参数**：在轴参数里设比正常 `MaxDec` 更激进的减速度。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_EmergencyStop_BkPlcMc.TcPOU`](../examples/P_Demo_MC_EmergencyStop_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机安全门打开传感器信号（PNP 高有效）触发的工艺停车。要求："门一开就立即停车 + 期间所有阀输出强制 0；门关上后才允许重新动作"。本 FB 满足这种"持续抑制"语义。
- **价值**：相比 Stop + 自己抑制阀输出，本 FB 内置电压抑制；相比硬件继电器急停，软件实现更灵活（可由 PLC 条件触发，不依赖固定接线）。
- **替代方案对比**：
  - 硬件急停继电器：安全等级最高但灵活性低
  - `MC_Stop_BkPlcMc`：停车后阀输出回到设定值可能漂动
  - **本 FB**：软件急停 + 电压抑制，作为硬件急停的冗余补充

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.2.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599694603.html
- **相关 FB**：`MC_Stop_BkPlcMc`（普通停车，无电压抑制）、`MC_ImediateStop_BkPlcMc`（零斜坡瞬停 + 电压抑制）、`MC_RampedStop_BkPlcMc`（纯时间斜坡）
