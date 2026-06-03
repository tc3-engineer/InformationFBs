# MC_Stop_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion - Single axis` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599705867.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_Stop_BkPlcMc.TcPOU`](../examples/P_Demo_MC_Stop_BkPlcMc.TcPOU) |

---

## 1. 功能简述

PLCopen 风格**强制停车**功能块。`Execute` 上升沿启动一次"取消当前运动并按 `Deceleration` / `Jerk` / `RampTime` 减速到停"的动作。与 `MC_Halt_BkPlcMc` 的核心区别：停车过程**不可被其它 FB 打断**——即使在 Stop 进行期间发新 Move 命令，新命令会被算法拒绝（Stop 优先）。停车完成后轴进入 Errorstop 状态（需要 `MC_Reset_BkPlcMc` 才能再接受新命令）。

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
| `Execute` | `BOOL` | — | 上升沿启动一次强制停车 |
| `Deceleration` | `LREAL` | — | 减速度，单位 mm/s²（自 V3.0.5 起加入） |
| `Jerk` | `LREAL` | — | jerk，单位 mm/s³（自 V3.0.5 起加入） |
| `RampTime` | `LREAL` | — | 停车时间，单位 s（自 V3.0.5 起加入）。`Deceleration` 给定时优先 |
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
| `Done` | `BOOL` | 强制停车成功（轴已静止） |
| `Error` | `BOOL` | 启动检查或停车算法错 |
| `ErrorID` | `UDINT` | 错误码 |
| `Active` | `BOOL` | 命令活动中（当前与 Busy 相同） |
| `CommandAborted` | `BOOL` | 字段存在但本 FB 不可被打断；通常不会置 TRUE |

## 3. 行为说明

**调用模式**：边沿触发。`Execute` 上升沿启动；下降沿清输出但不打断已启动的停车。

**启动检查**：
1. **轴必须有运动可停**：轴已静止 → 立即 `Done := TRUE`（不出错，幂等）
2. **轴在错误/停车中**：→ `Error`、`ErrorID := dwTcHydErrCdNotReady`
3. **轴被耦合控制**：→ `Error`、`ErrorID := dwTcHydErrCdNotReady`（先解耦再 Stop）

**减速参数优先级**：
- 若 `Deceleration` 显著大于 0：用之
- 否则若 `RampTime` 显著大于 0：按参考速度算出 Deceleration
- 都不给 → 用轴参数 `MaxDec`（jerk-limited 生成器再考虑 `MaxJerk`）

**目标位置计算**：FB 取"按当前设定速度和减速参数能到达的下一个最近位置"作为新目标位置；到达后轴进入正常静止状态。

**`RampTime` 详细语义**：`RampTime` 指"从参考速度减速到 0 所需时间"。若轴当前速度小于参考速度，实际减速时间按比例缩短。若用 creep 模式生成器，creep 时间会加到刹车时间上。

**与 `MC_Halt_BkPlcMc` 对比**：
- Stop：**不可被打断**。期间发新 Move 会被拒绝；停后轴在 Errorstop，必须 `MC_Reset_BkPlcMc` 才能接新命令
- Halt：**可被打断**。期间可立即接新命令；停后轴在 StandStill

**典型用法**：
- 急停按钮触发的安全停车（必须真停透）
- 工艺异常发现后的强制停车
- 测试 / 调试时强制停下不允许误操作

**典型陷阱**：
- 用 Stop 做日常工艺停车：每次都需要 Reset 才能继续；用 Halt 更合适
- 期望"停了立即接 Move"：行不通，必须 Reset；要这种语义用 Halt 或 ResetAndStop
- `Deceleration = 0` 和 `RampTime = 0` 都不给：用轴默认参数可能太慢/太快

## 4. 错误码 / 返回值

| `ErrorID` 常量 | 含义 | 处理建议 |
|---|---|---|
| `dwTcHydErrCdNotReady` | 轴在错误状态 / 已在停车 / 被耦合 | 视情况：先 Reset 或先 GearOut |
| (算法错码) | 运动算法报错 | 查 PDF §5.2 |

## 5. 使用注意 / 常见坑

- **停后是 Errorstop 不是 StandStill**：必须 `MC_Reset_BkPlcMc` 才能再接受新命令；这是设计选择"强制停透"
- **不可打断**：停车期间发新 Move 算法会拒绝，新 FB 报错
- **耦合轴需先解耦**：耦合状态下直接 Stop 报 NotReady；要先 `MC_GearOut_BkPlcMc`
- **静止时调用幂等**：立即 Done = TRUE，不出错
- **`Active` 字段当前与 `Busy` 相同**：PDF 明确写"output Active is currently identical to the output Busy"

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_Stop_BkPlcMc.TcPOU`](../examples/P_Demo_MC_Stop_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机出现"模具夹具异常"传感器报警，必须立即强制停车防止模具损坏。Stop 比 Halt 更适合此场景，因为必须保证停下来后操作员不会误触发新动作；停后轴在 Errorstop，操作员必须明确按"恢复"才能继续。
- **价值**：相比硬件继电器断电急停，本 FB 软停车带受控减速曲线，避免冲击；相比 Halt，强制性更高不会被误操作打断。
- **替代方案对比**：
  - `MC_Halt_BkPlcMc`：可打断，工艺停车用
  - `MC_EmergencyStop_BkPlcMc`：急停带斜坡 + 控制电压抑制
  - `MC_ImediateStop_BkPlcMc`：瞬时无斜坡（撞击风险）
  - **本 FB**：受控强制停车，安全停车场景标配

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.2.18
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599705867.html
- **相关 FB**：`MC_Halt_BkPlcMc`（可打断版）、`MC_EmergencyStop_BkPlcMc`、`MC_ImediateStop_BkPlcMc`（瞬停）、`MC_Reset_BkPlcMc`（停后清错）
