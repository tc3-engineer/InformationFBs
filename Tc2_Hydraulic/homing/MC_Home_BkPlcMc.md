# MC_Home_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Homing` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599699723.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_Home_BkPlcMc.TcPOU`](../examples/P_Demo_MC_Home_BkPlcMc.TcPOU) |

---

## 1. 功能简述

PLCopen 风格**归零**功能块。`Execute` 上升沿启动一次按 `HomingMode` 指定方法的归零动作。归零成功后轴的"实际位置"被设为 `Position`（参考位置），并把参考标志置 TRUE。支持多种归零模式：`MC_DefaultHomingMode_BkPlcMc`（按轴参数 `nEnc_HomingType` 派生）、`MC_AbsSwitch_BkPlcMc`（找参考凸轮）、`MC_RefPulse_BkPlcMc`（找编码器零脉冲）、`MC_Direct_BkPlcMc`（直接置位，无物理动作）、`MC_Block_BkPlcMc`（撞死点）等。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute:        BOOL;
    Position:       LREAL;
    HomingMode:     MC_HomingMode_BkPlcMc;
    CalibrationCam: BOOL;
    BufferMode:     MC_BufferMode_BkPlcMc:=Aborting_BkPlcMc;    //from V3.0.8
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿启动归零 |
| `Position` | `LREAL` | — | 参考位置，单位 mm。归零成功后轴实际位置被设为此值 |
| `HomingMode` | `MC_HomingMode_BkPlcMc` | — | 归零方法。常用 `MC_DefaultHomingMode_BkPlcMc`（按轴参数 `nEnc_HomingType` 决定） |
| `CalibrationCam` | `BOOL` | — | 参考凸轮直接输入（可用 PLC 端检测的 BOOL 直接接到这里，不必走 `dwTcHydDcDwRefIndex` 通道） |
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
    CommandAborted: BOOL;
    Error:          BOOL;
    ErrorID:        UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | 归零进行中 |
| `Done` | `BOOL` | 归零成功；轴位置已置为 `Position` |
| `CommandAborted` | `BOOL` | 被另一 FB 打断 |
| `Error` | `BOOL` | 启动检查或归零中出错 |
| `ErrorID` | `UDINT` | 错误码 |

## 3. 行为说明

**调用模式**：边沿触发。`Execute` 上升沿启动；下降沿清输出但已启动的归零不打断。

**启动检查**：
1. **轴必须静止且无错**：否则 → `Error`、`ErrorID := dwTcHydErrCdNotStartable` 或传入的错码
2. **轴在错误/停车中**：→ `Error`、`ErrorID := dwTcHydErrCdNotReady`
3. **轴参数速度太小**（参考速度的 1% 以下）：→ `Error`、`ErrorID := dwTcHydErrCdSetVelo`

**`HomingMode` 各模式语义**：

- **`MC_DefaultHomingMode_BkPlcMc`**：由 `pStAxParams.nEnc_HomingType` 决定。映射表（PDF 给出）：
  | `nEnc_HomingType` | `HomingMode_BkPlcMc` |
  |---|---|
  | `iTcMc_HomingOnBlock` | `MC_Block_BkPlcMc` |
  | `iTcMc_HomingOnIndex` | `MC_AbsSwitch_BkPlcMc` |
  | `iTcMc_HomingOnSync` | `MC_RefPulse_BkPlcMc` |
  | `iTcMc_HomingOnExec` | `MC_Direct_BkPlcMc` |

- **`MC_AbsSwitch_BkPlcMc`（参考凸轮）**：轴按 `fEnc_RefIndexVelo` 沿 `bEnc_RefIndexPositive` 方向运动；遇到 `CalibrationCam = TRUE` 或 `nDeCtrlDWord` bit 5 (`dwTcHydDcDwRefIndex`) 为 1 时停下；然后按 `fEnc_RefSyncVelo` 沿 `bEnc_RefSyncPositive` 方向退出凸轮区；脱离瞬间把轴位置设为 `Position`

- **`MC_RefPulse_BkPlcMc`（编码器零脉冲）**：先按 `fEnc_RefIndexVelo` 找凸轮（与 AbsSwitch 同），然后按 `fEnc_RefSyncVelo` 慢速找编码器的零脉冲；找到瞬间置位

- **`MC_Direct_BkPlcMc`（直接置位）**：不动轴，直接把当前位置设为 `Position`（类似 `MC_SetPosition_BkPlcMc`）

- **`MC_Block_BkPlcMc`（撞死点）**：轴往一个方向开到底（无法继续移动），把死点位置定义为 `Position`

- **`MC_LimitSwitch_BkPlcMc`**：当前不支持

**仿真编码器特例**：若编码器类型为 `iTcMc_EncoderSim`，无论 `HomingMode` 与轴参数 `nEnc_HomingType` 是什么，都强制走 `MC_Direct_BkPlcMc`（仿真无物理凸轮）。

**`fEnc_DefaultHomePosition` 用法**：若应用不想每次指定 `Position`，可用 `pStAxParams.fEnc_DefaultHomePosition` 保存默认值（与机器数据一起持久化），业务代码每次传同一值即可。复杂场景用 `pStAxParams.fCustomerData[]` 数组。

**典型用法**：开机后强制归零；维护后重新校准坐标系；定期对位偏差矫正。

**典型陷阱**：
- 轴未上电（`MC_Power_BkPlcMc` 没开）就调本 FB：报 NotReady
- `HomingMode` 与硬件不匹配（用 `MC_AbsSwitch_BkPlcMc` 但没接凸轮信号）：归零失败或永远找不到
- 归零过程中撤 `Execute`：归零继续，结束信号 Done/Error/Aborted 给一个周期
- 使用绝对编码器还跑归零：浪费时间；改用 `MC_SetReferenceFlag_BkPlcMc` 标已参考

## 4. 错误码 / 返回值

| `ErrorID` 常量 | 含义 | 处理建议 |
|---|---|---|
| `dwTcHydErrCdNotStartable` | 轴不静止或有错 | 先静止 + Reset |
| `dwTcHydErrCdNotReady` | 轴在错误/停车中 | Reset |
| `dwTcHydErrCdSetVelo` | 轴参数速度 < 1% refVelo | 检查 `fEnc_RefIndexVelo` / `fEnc_RefSyncVelo` |
| (算法错码) | 归零中算法报错 | 查 PDF §5.2 |

## 5. 使用注意 / 常见坑

- **归零方向 / 速度都在轴参数里**：`pStAxParams.fEnc_RefIndexVelo` / `bEnc_RefIndexPositive` / `fEnc_RefSyncVelo` / `bEnc_RefSyncPositive` 控制各阶段；本 FB 输入不调速度。
- **`CalibrationCam` 可走 PLC 软触发**：若凸轮信号没接 IO 终端但走 EtherCAT 输入，用本字段直接把 BOOL 传进来更灵活。
- **绝对编码器场景慎用**：开机后用 `MC_SetReferenceFlag_BkPlcMc` 更快。
- **归零完成后通常要保存**：调 `MC_AxParamSave_BkPlcMc` 持久化新参考位置。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_Home_BkPlcMc.TcPOU`](../examples/P_Demo_MC_Home_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机开机后必须先归零锁模轴。轴沿正方向以 10 mm/s 慢速去找参考凸轮（机械限位上接近开关），找到后退出凸轮区把那点定义为 0 mm；之后业务代码才能用绝对定位（合模到 350 mm）。
- **价值**：手写需要：① 启动 MoveVelocity；② 监视凸轮信号；③ 触发后 Stop；④ 启动反向慢速 MoveVelocity；⑤ 监视凸轮信号脱离；⑥ Stop；⑦ 调 SetPosition 把位置写为 Position。本 FB 一行调用全部封装。
- **替代方案对比**：
  - 手写 MoveVelocity + 凸轮检测 + SetPosition：业务侧 50+ 行代码，且要处理各种异常
  - `MC_SetPosition_BkPlcMc`：纯软归零，不去找物理参考点（适合绝对编码器）
  - **本 FB**：物理归零的标准接口，多模式支持

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.2.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599699723.html
- **相关 FB**：`MC_HomingMode_BkPlcMc`（模式枚举）、`MC_SetPosition_BkPlcMc`（软归零）、`MC_SetReferenceFlag_BkPlcMc`（标参考）、`MC_AxParamSave_BkPlcMc`（保存）
