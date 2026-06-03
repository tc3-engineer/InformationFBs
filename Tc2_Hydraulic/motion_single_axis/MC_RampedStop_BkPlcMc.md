# MC_RampedStop_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion - Single axis` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/9073620363.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_RampedStop_BkPlcMc.TcPOU`](../examples/P_Demo_MC_RampedStop_BkPlcMc.TcPOU) |

---

## 1. 功能简述

**纯时间斜坡停车**功能块。与 `MC_Stop_BkPlcMc` 不同，本 FB 不按"到达某个目标位置"停，而是按 `RampTime` 用纯时间斜坡把速度线性减到 0。**无明确终止位置**——轴可能因为时间斜坡冲过软限位（PDF 明确给出 CAUTION）。适合"不在乎停在哪里，只要按指定时间内停下"的场景，例如卸荷动作或紧急工艺切断。

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
| `Execute` | `BOOL` | — | 上升沿启动一次时间斜坡停车 |
| `RampTime` | `LREAL` | — | 所需停车时间，单位 s（自 V3.0.5 起加入）。按参考速度算出减速度 |

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
| `Done` | `BOOL` | 时间斜坡停车成功 |
| `Error` | `BOOL` | 启动检查或停车算法错 |
| `ErrorID` | `UDINT` | 错误码 |
| `Active` | `BOOL` | 命令活动中 |
| `CommandAborted` | `BOOL` | 被另一 FB 打断 |

## 3. 行为说明

**调用模式**：边沿触发。`Execute` 上升沿启动。

**启动检查**：
1. **轴必须有运动可停**：轴已静止 → 立即 `Done := TRUE`
2. **轴在错误/停车中**：→ `Error`、`ErrorID := dwTcHydErrCdNotReady`
3. **轴被耦合控制**：→ `Error`、`ErrorID := dwTcHydErrCdNotReady`

**停车算法**：`RampTime` 按参考速度（`fRefVelo`）算出减速度；以该减速度用纯时间斜坡把当前速度减到 0。

**⚠️ 无终止位置保证**：PDF 明确 CAUTION 段："No defined end position is driven to and the axis can overrun a software limit switch."（无明确终止位置；轴可能越过软限位）。这是与 `MC_Stop_BkPlcMc` 的本质区别——Stop 计算"按当前速度和减速参数能到达的下一个最近位置"作为新目标，本 FB 只按时间走。

**典型用法**：
- 液压卸荷：泵停 → 阀完全打开 → 持续 `RampTime` 时间内压力释放
- 紧急工艺切断：不在乎位置只在乎"停下来"
- 测试 / 调试时间段

**典型陷阱**：
- 期望"停在某位置"：本 FB 不保证；用 Stop/Halt
- `RampTime` 太短：减速度过大可能损伤液压元件
- 越过软限位无报警：与 Stop 不同，软限位被冲过 FB 自身不报，需配合 `MC_ReadAxisError_BkPlcMc` 观察

## 4. 错误码 / 返回值

| `ErrorID` 常量 | 含义 | 处理建议 |
|---|---|---|
| `dwTcHydErrCdNotReady` | 轴在错误状态 / 已在停车 / 被耦合 | Reset 或 GearOut |
| (算法错码) | 运动算法报错 | 查 PDF §5.2 |

## 5. 使用注意 / 常见坑

- **不保证位置**：明确文档警告会冲过软限位。
- **`RampTime` 是按参考速度算的**：实际轴速度若小于参考速度，实际停车时间按比例缩短。
- **不可与高精度停位场景混用**：精确停位用 Stop/Halt 配合 Deceleration 参数。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_RampedStop_BkPlcMc.TcPOU`](../examples/P_Demo_MC_RampedStop_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：液压站日常停机卸荷流程。班末或维护前需要把液压系统的压力慢慢卸到 0（避免液压管路冲击）。本 FB 在 3 秒内把执行器速度线性减到 0，配合泵停 + 卸荷阀打开，让残余压力安全释放。
- **价值**：相比 Stop/Halt 需要计算停止位置，本 FB 只按时间斜坡走，业务侧不需要操心"停哪"。
- **替代方案对比**：
  - `MC_Stop_BkPlcMc` / `MC_Halt_BkPlcMc`：保证位置但减速曲线不一定线性
  - `MC_EmergencyStop_BkPlcMc`：急停 + 控制电压抑制，行为更激进
  - **本 FB**：纯时间斜坡，适合"按时停下不在乎位置"

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.2.17
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/9073620363.html
- **相关 FB**：`MC_Stop_BkPlcMc`（保证位置版）、`MC_EmergencyStop_BkPlcMc`、`MC_Halt_BkPlcMc`
