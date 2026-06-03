# MC_CamIn_BkPlcMc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Hydraulic` |
| Library Version | `1.8.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Motion - Multiple axis` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599690507.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_CamIn_BkPlcMc.TcPOU`](../examples/P_Demo_MC_CamIn_BkPlcMc.TcPOU) |

---

## 1. 功能简述

PLCopen 风格**凸轮表耦合**功能块。`Execute` 上升沿启动两轴之间的凸轮表耦合：从轴的位置由"主轴位置 → 凸轮表查表 → 从轴位置"映射决定。凸轮表必须先用 `MC_CamTableSelect_BkPlcMc` 初始化并把 `MC_CAM_ID_BkPlcMc` 传过来。支持 `MasterOffset` / `SlaveOffset` / `MasterScaling` / `SlaveScaling` 4 个变换参数；`StartMode` 决定从轴启动时如何与凸轮表对齐（Absolute / Relative / RampIn 等）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute:        BOOL;
    MasterOffset:   LREAL:=0.0;
    SlaveOffset:    LREAL:=0.0;
    MasterScaling:  LREAL:=0.0;
    SlaveScaling:   LREAL:=0.0;
    StartMode:      MC_StartMode_BkPlcMc:=MC_StartMode_Absolute;
    CamTableId:     MC_CAM_ID_BkPlcMc;
    BufferMode:     MC_BufferMode_BkPlcMc:=Aborting_BkPlcMc;    //from V3.0.8
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿启动凸轮耦合 |
| `MasterOffset` | `LREAL` | `0.0` | 主轴位置在查表前的偏移（实际查表用 `master_pos + MasterOffset`），单位 mm |
| `SlaveOffset` | `LREAL` | `0.0` | 从轴位置在查表后的偏移（最终从轴位置 = 查表值 + `SlaveOffset`），单位 mm |
| `MasterScaling` | `LREAL` | `0.0` | 主轴位置缩放（注：PDF 描述与 MasterOffset 一致，可能是文档错误） |
| `SlaveScaling` | `LREAL` | `0.0` | 从轴位置缩放（同上） |
| `StartMode` | `MC_StartMode_BkPlcMc` | `MC_StartMode_Absolute` | 启动模式：Absolute / Relative / RampIn 等 |
| `CamTableId` | `MC_CAM_ID_BkPlcMc` | — | 凸轮表 ID。必须先由 `MC_CamTableSelect_BkPlcMc` 初始化（`bValidated := TRUE`） |
| `BufferMode` | `MC_BufferMode_BkPlcMc` | `Aborting_BkPlcMc` | 保留（自 V3.0.8 起加入） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Master:         AXIS_REF_BkPlcMc;
    Slave:          AXIS_REF_BkPlcMc;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Master` | `AXIS_REF_BkPlcMc` | 主轴接口结构 |
| `Slave` | `AXIS_REF_BkPlcMc` | 从轴接口结构 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Busy:           BOOL;
    InSync:         BOOL;
    CommandAborted: BOOL;
    Error:          BOOL;
    ErrorID:        UDINT;
    EndOfProfile:   BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | 命令处理中 |
| `InSync` | `BOOL` | 首次同步成功（latched） |
| `CommandAborted` | `BOOL` | 耦合被打断 |
| `Error` | `BOOL` | 启动检查或运行中错 |
| `ErrorID` | `UDINT` | 错误码 |
| `EndOfProfile` | `BOOL` | 主轴到达凸轮表定义的范围末端 |

## 3. 行为说明

**调用模式**：边沿触发。

**启动检查**：
1. `CamTableId.bValidated = FALSE`（未先调 `MC_CamTableSelect_BkPlcMc`）→ `Error`、`ErrorID := dwTcHydErrCdTblNoInit`
2. 主或从不在 idle 状态 → `Error`、`ErrorID := dwTcHydErrCdNotStartable`
3. `StartMode = MC_StartMode_RampIn` → `Error`（暂不支持）

**凸轮表查表**：每周期算 `slave_pos = CamTable[master_pos + MasterOffset] + SlaveOffset`（Scaling 类似但缩放）。从轴速度由位置导数决定，与主轴速度成比例（比例由凸轮表斜率决定）。

**`EndOfProfile` 语义**：凸轮表是有限范围的（例如主轴 0-360°）；主轴位置走出范围时该位置 TRUE。可用于触发"循环回起点"或"结束动作"。

**典型用法**：
- 注塑机锁模 + 注射的协同动作：锁模到一定位置后注射头按非线性曲线推进
- 飞剪 / 旋切非线性切割轨迹
- 模具开模 + 顶杆同步动作

**典型陷阱**：
- 没先调 `MC_CamTableSelect_BkPlcMc`：`bValidated = FALSE`，凸轮表无效
- `StartMode_RampIn` 不支持：会报错
- 主从在动就启动：报 NotStartable
- 凸轮表斜率过大导致从轴超速：未必有警告，要业务侧自己校准

## 4. 错误码 / 返回值

| `ErrorID` 常量 | 含义 | 处理建议 |
|---|---|---|
| `dwTcHydErrCdTblNoInit` | 凸轮表未初始化 | 先调 `MC_CamTableSelect_BkPlcMc` |
| `dwTcHydErrCdNotStartable` | 主或从不在 idle | 先停 |
| (其它) | 算法报错 | 查 PDF §5.2 |

## 5. 使用注意 / 常见坑

- **凸轮表先初始化**：缺这一步直接报 NoInit。
- **`MasterScaling` / `SlaveScaling` PDF 描述含糊**：可能是 PDF 文档错误，描述与 Offset 看上去一致。实际工程上一般给 1.0 不变；不确定时按 InfoSys 实测验证。⚠️
- **`EndOfProfile` 是脉冲不是 latched**：到达边界瞬间 TRUE 一个周期；要循环使用要业务侧记下来。
- **解耦用 `MC_CamOut_BkPlcMc`**：与 GearOut 类似，解耦不停轴。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_CamIn_BkPlcMc.TcPOU`](../examples/P_Demo_MC_CamIn_BkPlcMc.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见对应 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机锁模与注射的协同动作。锁模合到一定位置后，注射头按非线性曲线（不是匀速也不是线性）推进，凸轮表预先编程好"锁模位置 0-350 mm 对应注射头 0-50 mm" 的非线性映射。本 FB 把锁模轴定为主、注射轴定为从，启动后注射头按表自动跟随。
- **价值**：复杂运动轨迹无需 PLC 周期性计算，离线编程凸轮表后实时跟随；适合数学难以描述的工艺曲线。
- **替代方案对比**：
  - `MC_GearIn_BkPlcMc`：线性恒齿比，非线性映射做不到
  - 自己周期性算 slave_pos：实时性差
  - **本 FB**：非线性映射标准接口

## 8. 参考资料

- **PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf) §4.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/1599690507.html
- **相关 FB**：`MC_CamTableSelect_BkPlcMc`（必需的凸轮表初始化）、`MC_CamOut_BkPlcMc`（解耦）、`MC_GearIn_BkPlcMc`（线性耦合）

## 9. 待确认项 (⚠️)

- PDF 的 `MasterScaling` / `SlaveScaling` 描述与 `MasterOffset` / `SlaveOffset` 描述文字几乎相同，疑似文档错误；实际语义应是缩放因子（乘法），但 PDF 未明确。
