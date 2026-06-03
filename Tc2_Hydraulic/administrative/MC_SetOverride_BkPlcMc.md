# MC_SetOverride_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Administrative` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599683467.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_SetOverride_BkPlcMc.TcPOU`](../examples/P_Demo_MC_SetOverride_BkPlcMc.TcPOU) |

---

## 1. 功能简述

设置液压轴**速度倍率**（override）的功能块。`Enable = TRUE` 时把 `VelFactor`（取值 0.0–1.0）写入 `Axis.pStAxParams^.fOverride`；所有当前及后续运动命令的实际速度都按 `指令速度 × override` 计算。`Enable` 下降沿清所有输出。**注意**：本 FB 只在 `iTcMc_ProfileCtrlBased` 配置文件下生效；用其他 profile type 时无效。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Enable:     BOOL;
    VelFactor:  LREAL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Enable` | `BOOL` | — | `TRUE` 激活倍率设置；下降沿清所有输出 |
| `VelFactor` | `LREAL` | — | 速度倍率，单位无量纲。FB 内部限幅到 `[0.0, 1.0]`；写入 `pStAxParams^.fOverride` |

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
    Enabled:    BOOL;
    Busy:       BOOL;
    Error:      BOOL;
    ErrorID:    UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Enabled` | `BOOL` | 倍率设置已激活；FB 处于正常工作状态 |
| `Busy` | `BOOL` | 命令处理中。本 FB 不需任何时间，`Busy` 通常为 `FALSE`，仅为兼容性保留 |
| `Error` | `BOOL` | 出错指示 |
| `ErrorID` | `UDINT` | 编码错误号 |

## 3. 行为说明

**调用模式**：每周期调用，电平触发。

**操作流程**：
1. `Enable = TRUE`：FB 把 `VelFactor` 限幅到 `[0.0, 1.0]` 区间后写入 `Axis.pStAxParams^.fOverride`；`Enabled := TRUE`
2. `Enable = FALSE`：清所有输出；`fOverride` 保持上次写入值（FB 不主动复位为 1.0）

**倍率应用**：所有运动 FB（`MC_MoveAbsolute_BkPlcMc` / `MoveRelative` / `MoveVelocity` 等）的实际行进速度 = `Velocity × fOverride`。这种应用是由 `iTcMc_ProfileCtrlBased` 配置文件内部完成的；其他 profile 不读 `fOverride`。

**加减速限制**：倍率变化引起的速度变化受最大允许加速度 / 减速度约束。例如从 100% 突变到 50%，轴不会瞬间减速，而是按最大减速度平滑过渡。

**最小有效值（`fCreepSpeed` 屏障）**：为保证"目标接近"行为可重现，倍率只能把速度降到 `pStAxParams.fCreepSpeed`，**不能把轴停下**。即使 `VelFactor := 0.0`，轴也会以爬行速度（creep speed）继续运动到达目标。要真正停轴用 `MC_Stop_BkPlcMc` 或 `MC_Halt_BkPlcMc`。

**典型用法**：
- HMI 上的"速度调节"旋钮（0–100%）
- 试运行 / 试模阶段限速 50% 验证轨迹无误后再调到 100% 生产
- 工件粗加工和精加工切换速度档位

**典型陷阱**：
- 期望 `VelFactor := 0` 停轴：实际仍以 `fCreepSpeed` 移动；停车必须用 Stop/Halt
- 只对 `iTcMc_ProfileCtrlBased` 有效：其他 profile（如时间基的生成器）不读 fOverride，本 FB 调了等于没调
- 倍率改变后期望立即生效：实际有加减速延迟，HMI 上看是平滑过渡而非瞬变

## 4. 错误码 / 返回值

PDF 与 InfoSys 在本 FB 章节都未列具体 `ErrorID` 数值；常见情况只是 `Enabled` / `Error` 的状态指示。⚠️ 待人工确认完整错误码表。

## 5. 使用注意 / 常见坑

- **只对 `iTcMc_ProfileCtrlBased` profile 有效**：必须先在轴参数里设置该 profile 类型；否则本 FB 调用看似成功但不影响速度。
- **不能停轴**：`VelFactor = 0` 仍按 `fCreepSpeed` 走；停车用专门的 Stop / Halt FB。
- **加减速限幅是为安全**：倍率突变时 FB 自动按最大加减速过渡，可能延迟数百 ms 才到目标倍率。
- **`Enable := FALSE` 不复位倍率**：FB 撤 `Enable` 后 `fOverride` 保持上次值；要回到 100% 需要 `VelFactor := 1.0; Enable := TRUE`。
- **`Busy` 通常 FALSE**：判 FB 工作状态用 `Enabled`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_SetOverride_BkPlcMc.TcPOU`](../examples/P_Demo_MC_SetOverride_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机 HMI 上"速度倍率"旋钮（0–100%）。新模具试模时操作员先设 50% 倍率，运行几个周期确认动作轨迹无误后调到 100% 进入生产。某些客户在小批量试产时常驻在 80% 倍率以延长设备寿命。
- **价值**：手写需要：① 把 HMI 旋钮值换算到 [0,1]；② 直接写 `pStAxParams^.fOverride`；③ 自己处理边界限幅。本 FB 提供标准接口，限幅与加减速过渡都内置。
- **替代方案对比**：
  - 直接写 `pStAxParams^.fOverride`：性能略好但需自己限幅，且与 PLCopen 标准接口语义不符
  - 重新定义每个运动 FB 的 Velocity：要改业务代码每一处运动命令，违反"按倍率全局调速"语义
  - **本 FB**：标准接口，全局生效，HMI 直接对接

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.1.12
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599683467.html
- **相关 FB**：`MC_Stop_BkPlcMc` / `MC_Halt_BkPlcMc`（真正停车）、各 `MC_Move*_BkPlcMc`（实际速度按 override 缩放）

## 9. 待确认项 (⚠️)

- PDF 与 InfoSys 在本 FB 章节均未列具体 `ErrorID` 数值；待人工补充错误码表。
