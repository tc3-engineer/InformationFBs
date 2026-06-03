# Tc2_Hydraulic — TF5810 液压闭环定位库

> Beckhoff TwinCAT 3 PLC 库（TF5810 License），提供液压伺服 / 比例阀 / 步进液压系统的 PLCopen Motion Control 风格定位与闭环控制功能块。基于内部专有的液压算法层（pStAxRtData / pStAxParams 结构），上层对接 PLCopen FB 接口。
>
> - **Library Version**：1.8.3
> - **Source PDF**：[TF5810_TC3_Hydraulic_Positioning_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf)
> - **Source InfoSys**：https://infosys.beckhoff.com/content/1033/tf5810_tc3_hydraulic_positioning/
> - **手册总篇幅**：389 页（大部分讲液压系统配置 + 闭环参数 + commissioning）

## 关键概念

- 所有 MC_*_BkPlcMc FB 的轴接口都是 `Axis : AXIS_REF_BkPlcMc` 作为 **VAR_IN_OUT**（必须传引用）
- 主从耦合类（`GearIn` / `GearInPos` / `CamIn`）同时传 `Master` 与 `Slave` 两根 AXIS_REF
- 输出统一遵循 PLCopen 三态收敛：`Done` / `CommandAborted` / `Error` + `ErrorID`（部分 FB 没有 Done 而是 InVelocity / InGear / InSync 等场景化字段）
- `BufferMode` 在当前版本（1.8.3）几乎所有 FB 中都是**保留字段**，只允许 `Aborting_BkPlcMc`
- `Execute` 通常是**边沿触发**；停车类（`MC_EmergencyStop` / `MC_ImediateStop`）是**电平触发**（持续维持电压抑制）
- `MC_Power_BkPlcMc` 是必经前置：不开 Power 任何运动 FB 都会报错
- 错误码 `ErrorID` 是液压库的全局常量 `dwTcHydErrCd*` 系列（不是 HRESULT 也不是 NC 错误号）
- 实际压力 / 力 反馈链：`MC_AxRtReadPressureXxx_BkPlcMc` / `MC_AxRtReadForceXxx_BkPlcMc` 必须每周期调用且在压力闭环 FB 之前

## 分类索引

### Administrative（管理类，11 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_Power_BkPlcMc` | 控制外部执行器使能（必经前置） | [administrative/MC_Power_BkPlcMc.md](administrative/MC_Power_BkPlcMc.md) |
| `MC_ReadActualPosition_BkPlcMc` | 读实际位置（mm） | [administrative/MC_ReadActualPosition_BkPlcMc.md](administrative/MC_ReadActualPosition_BkPlcMc.md) |
| `MC_ReadActualTorque_BkPlcMc` | 读实际力 / 压力 | [administrative/MC_ReadActualTorque_BkPlcMc.md](administrative/MC_ReadActualTorque_BkPlcMc.md) |
| `MC_ReadActualVelocity_BkPlcMc` | 读实际速度（mm/s） | [administrative/MC_ReadActualVelocity_BkPlcMc.md](administrative/MC_ReadActualVelocity_BkPlcMc.md) |
| `MC_ReadAxisError_BkPlcMc` | 读轴错误码 | [administrative/MC_ReadAxisError_BkPlcMc.md](administrative/MC_ReadAxisError_BkPlcMc.md) |
| `MC_ReadStatus_BkPlcMc` | 读 PLCopen 状态机（11 个 BOOL 输出） | [administrative/MC_ReadStatus_BkPlcMc.md](administrative/MC_ReadStatus_BkPlcMc.md) |
| `MC_Reset_BkPlcMc` | 清错（Errorstop → StandStill） | [administrative/MC_Reset_BkPlcMc.md](administrative/MC_Reset_BkPlcMc.md) |
| `MC_ResetAndStop_BkPlcMc` | 清错并强制停车 | [administrative/MC_ResetAndStop_BkPlcMc.md](administrative/MC_ResetAndStop_BkPlcMc.md) |
| `MC_SetOverride_BkPlcMc` | 设速度倍率（0-100%） | [administrative/MC_SetOverride_BkPlcMc.md](administrative/MC_SetOverride_BkPlcMc.md) |
| `MC_SetPosition_BkPlcMc` | 软归零（修改坐标定义，不动轴） | [administrative/MC_SetPosition_BkPlcMc.md](administrative/MC_SetPosition_BkPlcMc.md) |
| `MC_SetReferenceFlag_BkPlcMc` | 设参考标志（非 PLCopen 扩展） | [administrative/MC_SetReferenceFlag_BkPlcMc.md](administrative/MC_SetReferenceFlag_BkPlcMc.md) |

### Motion - Single axis（单轴运动，9 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_MoveAbsolute_BkPlcMc` | 绝对位置定位 | [motion_single_axis/MC_MoveAbsolute_BkPlcMc.md](motion_single_axis/MC_MoveAbsolute_BkPlcMc.md) |
| `MC_MoveRelative_BkPlcMc` | 相对距离定位（含符号方向） | [motion_single_axis/MC_MoveRelative_BkPlcMc.md](motion_single_axis/MC_MoveRelative_BkPlcMc.md) |
| `MC_MoveVelocity_BkPlcMc` | 恒速无目标运动（直到撞软限位） | [motion_single_axis/MC_MoveVelocity_BkPlcMc.md](motion_single_axis/MC_MoveVelocity_BkPlcMc.md) |
| `MC_MoveJoySticked_BkPlcMc` | 摇杆式电平驱动调速（非 PLCopen） | [motion_single_axis/MC_MoveJoySticked_BkPlcMc.md](motion_single_axis/MC_MoveJoySticked_BkPlcMc.md) |
| `MC_Halt_BkPlcMc` | 软停车（可被打断；停后回 StandStill） | [motion_single_axis/MC_Halt_BkPlcMc.md](motion_single_axis/MC_Halt_BkPlcMc.md) |
| `MC_Stop_BkPlcMc` | 强制停车（不可打断；停后是 Errorstop） | [motion_single_axis/MC_Stop_BkPlcMc.md](motion_single_axis/MC_Stop_BkPlcMc.md) |
| `MC_RampedStop_BkPlcMc` | 纯时间斜坡停车（不保证终止位置） | [motion_single_axis/MC_RampedStop_BkPlcMc.md](motion_single_axis/MC_RampedStop_BkPlcMc.md) |
| `MC_EmergencyStop_BkPlcMc` | 软急停 + 电压抑制（电平触发） | [motion_single_axis/MC_EmergencyStop_BkPlcMc.md](motion_single_axis/MC_EmergencyStop_BkPlcMc.md) |
| `MC_ImediateStop_BkPlcMc` | 瞬时无斜坡停（⚠️ 巨大冲击风险） | [motion_single_axis/MC_ImediateStop_BkPlcMc.md](motion_single_axis/MC_ImediateStop_BkPlcMc.md) |

### Motion - Multiple axis（多轴耦合，5 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_GearIn_BkPlcMc` | 线性电子齿轮耦合（仅静止启动） | [motion_multiple_axis/MC_GearIn_BkPlcMc.md](motion_multiple_axis/MC_GearIn_BkPlcMc.md) |
| `MC_GearInPos_BkPlcMc` | 飞行同步齿轮耦合（主轴运动中也能启动） | [motion_multiple_axis/MC_GearInPos_BkPlcMc.md](motion_multiple_axis/MC_GearInPos_BkPlcMc.md) |
| `MC_GearOut_BkPlcMc` | 齿轮解耦（⚠️ 解耦不停轴，必须接 MC_Halt） | [motion_multiple_axis/MC_GearOut_BkPlcMc.md](motion_multiple_axis/MC_GearOut_BkPlcMc.md) |
| `MC_CamIn_BkPlcMc` | 凸轮表非线性耦合 | [motion_multiple_axis/MC_CamIn_BkPlcMc.md](motion_multiple_axis/MC_CamIn_BkPlcMc.md) |
| `MC_CamOut_BkPlcMc` | 凸轮解耦（⚠️ 同 GearOut 不停轴） | [motion_multiple_axis/MC_CamOut_BkPlcMc.md](motion_multiple_axis/MC_CamOut_BkPlcMc.md) |

### Homing（归零，1 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_Home_BkPlcMc` | 多模式归零（AbsSwitch / RefPulse / Direct / Block） | [homing/MC_Home_BkPlcMc.md](homing/MC_Home_BkPlcMc.md) |

### Controllers（控制器，3 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_AxCtrlPressure_BkPlcMc` | 压力闭环 PI 控制器（保压段必备） | [controllers/MC_AxCtrlPressure_BkPlcMc.md](controllers/MC_AxCtrlPressure_BkPlcMc.md) |
| `MC_AxCtrlSlowDownOnPressure_BkPlcMc` | 压力限制减速（运动中超压自动减速） | [controllers/MC_AxCtrlSlowDownOnPressure_BkPlcMc.md](controllers/MC_AxCtrlSlowDownOnPressure_BkPlcMc.md) |
| `MC_AxCtrlAutoZero_BkPlcMc` | 零遮盖阀自动零位补偿（在线学习） | [controllers/MC_AxCtrlAutoZero_BkPlcMc.md](controllers/MC_AxCtrlAutoZero_BkPlcMc.md) |

### Pressure / Force sensing（压力 / 力 反馈采集，4 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_AxRtReadPressureSingle_BkPlcMc` | 单路压力 ADC → bar（压力闭环数据源） | [pressure_force_sensing/MC_AxRtReadPressureSingle_BkPlcMc.md](pressure_force_sensing/MC_AxRtReadPressureSingle_BkPlcMc.md) |
| `MC_AxRtReadPressureDiff_BkPlcMc` | 双路差动压力 → 差压 bar | [pressure_force_sensing/MC_AxRtReadPressureDiff_BkPlcMc.md](pressure_force_sensing/MC_AxRtReadPressureDiff_BkPlcMc.md) |
| `MC_AxRtReadForceSingle_BkPlcMc` | 单路力（含摩擦补偿） → N | [pressure_force_sensing/MC_AxRtReadForceSingle_BkPlcMc.md](pressure_force_sensing/MC_AxRtReadForceSingle_BkPlcMc.md) |
| `MC_AxRtReadForceDiff_BkPlcMc` | 双路差动力 → 净力 N（差动缸必备） | [pressure_force_sensing/MC_AxRtReadForceDiff_BkPlcMc.md](pressure_force_sensing/MC_AxRtReadForceDiff_BkPlcMc.md) |

## 例程

所有 33 篇 FB 文档都配套一个 [`examples/P_Demo_<Name>.TcPOU`](examples/) — TwinCAT 3 原生 .TcPOU 格式。

**导入步骤**：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选 .TcPOU 文件 → OK

每个例程都按本仓库行动纲领 D 节要求带**场景 / 价值 / 验证步骤**三件套中文注释，变量名贴近液压工业语义（`axHydClampingHead` / `axHydInjPiston` / `axHydDiffCyl` 等），注释比例 ≥ 1/3。

## 本库的特殊命名 / 文档错误

液压库 PDF（1.8.3 版）存在多处文档错误，本仓库严格按 PDF 字面搬运而非"修正"，原因是 IEC 编译器看的是 PDF 给出的字段名，"修正"反而会编译错：

| 错误位置 | PDF 字面 | 真实/应是 | 仓库处理 |
|---|---|---|---|
| `MC_ImediateStop_BkPlcMc` 名 | `Imediate`（缺 m） | `Immediate` | 严格按 PDF 用 `Imediate` |
| `MC_ReadStatus_BkPlcMc` 输出字段 | `ContinousMotion`（缺 u） | `ContinuousMotion` | 严格按 PDF 用 `ContinousMotion` |
| `MC_Power_BkPlcMc` 输出字段 | 代码块 `Status`、描述表 `State` | 应一致 | 用代码块的 `Status` |
| `MC_AxCtrlAutoZero_BkPlcMc` 接口图 | 头部错写 `MC_AxUtiOffsetLatch_BkPlcMc` | 章节标题正确 | 用章节标题名 |
| `MC_CamOut_BkPlcMc` VAR_INPUT | `END_VAR` 被截断为 `ND_VAR` | `END_VAR` | 在文档中描述字段但跳过 PDF 误版代码块 |
| `MC_AxRtReadForceSingle_BkPlcMc` VAR_INPUT | 抄了 Diff 版的 B 路字段 | 单路应只有 A 路 | 严格按 PDF 搬运，B 路给 0 |
| `MC_AxRtReadPressureSingle_BkPlcMc` `ScaleOffset` 单位 | `[N/ADC_INC]` | `[bar]` | 文档标 ⚠️ 但搬运 |
| `MC_AxCtrlSlowDownOnPressure_BkPlcMc` `FirstAuxParamIdx` 默认值 | `INT:=0.0` | `INT:=0` | 严格按 PDF 字面 |
| `MC_AxCtrlPressure_BkPlcMc` `InWindup` 类型 | 代码块 `UDINT`，描述说 "TRUE" | BOOL 语义 | 用 UDINT，非 0 当 TRUE |

完整待确认项见各文档 §9 节。

## 文档质量

所有 33 篇通过：

- `_meta/tools/verify_doc.py` — VAR 区一致、占位短语 / 中文长度 / InfoSys URL 检查全 PASS
- `_meta/tools/lint_tcpou.py` — 例程 XML 结构合法
- `_meta/tools/lint_tcpou.py --check-unique` — 全仓 TcPOU GUID 唯一性 PASS
- 引脚名审计 — 例程里每个 `pin := value` / `pin => var` 的 LEFT 名称与对应 FB 文档的 VAR_INPUT/OUTPUT/IN_OUT 完全一致

InfoSys 主题 URL 已逐条校验（`InfoSys-checked: ✅ 2026-06-03`）。

## 与其它库的搭配

- **`Tc2_Standard`**：基础 PLC 类型与边沿检测（`R_TRIG`）—— 边沿触发的 Move FB 必用
- **`Tc2_System`**：错误码比对、版本信息结构
- **`Tc2_MC2`**：PLCopen Part 1 标准电气伺服库（与本库不能混用，电液混合系统的各轴各自属于一个库）
- **`Tc3_DriveMotionControl`**：TwinCAT 3 风格的电气运动库

## 本库覆盖范围说明

液压库 PDF 共 ~100 个 FB（含很多 internal use only / not recommended 的运行时辅助 FB）。本仓库覆盖了**用户最常调用的 33 个核心 FB**，包括：

- 全部 11 个 Administrative FB
- 全部 9 个 Motion Single Axis FB
- 全部 5 个 Multi Axis 耦合 FB
- 全部 4 个 Pressure / Force 反馈采集 FB
- 3 个核心 Controller FB（Pressure / SlowDownOnPressure / AutoZero）
- 1 个 Homing FB

未覆盖的 FB 大多是 internal use only 的运行时 / 配置 / 日志 / Ads 通讯辅助 FB（`MC_AxRtFinish*` / `MC_AxRtGenerator*` / `MC_AxRtEncoder*` / `MC_AxStandardBody*` / `MC_AxAdsCommServer*` / `MC_AxParamLoad*` 等），通常由 `MC_AxStandardBody_BkPlcMc` 模板调用，不需要业务代码直接接触。
