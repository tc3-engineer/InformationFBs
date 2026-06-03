# MC_Halt_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion - Single axis` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599698699.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_Halt_BkPlcMc.TcPOU`](../examples/P_Demo_MC_Halt_BkPlcMc.TcPOU) |

---

## 1. 功能简述

PLCopen 风格**软停车**功能块。`Execute` 上升沿启动一次"取消当前运动并按 `Deceleration` / `Jerk` / `RampTime` 减速到停"的动作。停车过程可以被其它运动 FB 打断（→ `CommandAborted`）。与 `MC_Stop_BkPlcMc` 的唯一区别是 Stop 不可被打断（不允许停车期间重启）。本 FB 行为说明在 PDF 中写明"与 MC_Stop_BkPlcMc 完全相同，仅打断语义不同"。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute:        BOOL;
    Deceleration:   LREAL;  //from V3.0.5
    Jerk:           LREAL;  //from V3.0.5
    RampTime:       LREAL;  //from V3.0.5
    BufferMode:     MC_BufferMode_BkPlcMc:=Aborting_BkPlcMc;    //from V3.0.8
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿启动一次软停车 |
| `Deceleration` | `LREAL` | — | 减速度，单位 mm/s²（自 V3.0.5 起加入）。≤0 用 `RampTime` 或 `MaxDec` |
| `Jerk` | `LREAL` | — | jerk，单位 mm/s³（自 V3.0.5 起加入）。仅在选用 jerk-limited 生成器时生效 |
| `RampTime` | `LREAL` | — | 停车时间，单位 s（自 V3.0.5 起加入）。给定时按参考速度算出 Deceleration |
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
| `Done` | `BOOL` | 软停车成功（轴已静止） |
| `Error` | `BOOL` | 启动检查或停车算法错 |
| `ErrorID` | `UDINT` | 错误码 |
| `Active` | `BOOL` | 命令活动中（当前与 Busy 相同） |
| `CommandAborted` | `BOOL` | 被另一 FB 打断（Halt 的特性——允许停车期间重启） |

## 3. 行为说明

**与 MC_Stop 的关系**：PDF 行为段落直接写"行为与 `MC_Stop_BkPlcMc()` 完全相同，唯一区别是命令处理可以被其他 FB 打断"。即所有启动检查、停车曲线、`Deceleration` / `RampTime` / `Jerk` 优先级、终态判定都一致；只是 Halt 期间可以中途接新命令（接新命令 → `CommandAborted`）。

**典型工艺用法**：正常工艺停车用 Halt。例如"该工序段结束停一下，下个工序段开始就走"——停车期间允许立即接 Move 命令（如急切换到下一道工序）。Stop 适合需要"必须真的停透"再做下一步的场景。

**参数生效优先级**（PDF §4.2.18 详细描述，本 FB 同）：
- 若 `Deceleration > 0`：用之
- 否则若 `RampTime > 0`：按参考速度算出 Deceleration
- 否则用轴参数 `MaxDec`、`MaxJerk`

**停车后状态**：轴回到 StandStill 状态（不锁轴，可立即接新命令）；与 Stop 锁轴行为相反。

**典型用法**：
- 一次工艺段结束的"软停"，期间可接下个动作
- 操作员手动模式下的暂停按钮（允许"暂停 → 立即接 jog"）
- 工艺切换间的过渡停车

**典型陷阱**：
- 期望"停一段时间不被打断"：用 MC_Stop_BkPlcMc 而不是 Halt
- `Deceleration = RampTime = 0`：用 MaxDec/MaxJerk 默认，可能比预期慢
- 停车期间立即发新命令：`CommandAborted := TRUE`，业务侧要注意区分"主动打断"和"出错"

## 4. 错误码 / 返回值

| `ErrorID` 常量 | 含义 | 处理建议 |
|---|---|---|
| `dwTcHydErrCdNotReady` | 轴在错误状态或正在停车中 | `MC_Reset_BkPlcMc` 清错 |
| `dwTcHydErrCdNotReady` | 轴正被耦合控制 | 先 `MC_GearOut_BkPlcMc` 解耦 |
| (算法错码) | 运动算法报错 | 查 PDF §5.2 全局常量 |

## 5. 使用注意 / 常见坑

- **可被打断**：与 Stop 的唯一区别。期间发新 Move → CommandAborted。
- **三参数优先级**：`Deceleration` > `RampTime` > 轴参数 MaxDec。
- **`Jerk` 仅 jerk-limited 生成器才生效**：液压库当前主要用线性生成器，给 Jerk 通常无效。
- **停车后是 StandStill 不是 Errorstop**：与 Stop 不同；这正是 "Halt 适合工艺停车"的根因。
- **轴静止时调用**：立即 `Done := TRUE`（无运动可停）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_Halt_BkPlcMc.TcPOU`](../examples/P_Demo_MC_Halt_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机液压锁模完成后到下一周期的合模之间需要工艺停车（保压/冷却）。用 Halt 而不是 Stop，因为如果操作员中途按"急换模"或"手动复位"，业务侧需要立即接新命令——Halt 允许这种打断。
- **价值**：与 Stop 相比，Halt 不锁轴（停后是 StandStill），不需要 Reset 就能接新命令；与"撤 Execute"相比，Halt 是真的停车（带减速曲线），不是简单切换控制。
- **替代方案对比**：
  - `MC_Stop_BkPlcMc`：必须真的停透才能下命令；强制性更高
  - 撤 `Execute`：不停车，运动继续
  - **本 FB**：工艺暂停首选

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.2.11
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599698699.html
- **相关 FB**：`MC_Stop_BkPlcMc`（不可打断版）、`MC_RampedStop_BkPlcMc`（纯时间斜坡）、`MC_EmergencyStop_BkPlcMc`（急停带斜坡）、`MC_ImediateStop_BkPlcMc`（零斜坡瞬停）
