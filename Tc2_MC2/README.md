# Tc2_MC2 — PLCopen 单轴运动控制库

> Beckhoff TwinCAT 3 标准库，提供符合 **PLCopen Motion Control Part 1** 标准的单轴运动 FB。
> 本库在 TC NC PTP 底层之上提供 IEC 61131-3 兼容封装，让运动控制代码可在不同支持 PLCopen 的运动平台间移植。
>
> - **Library Version**：2.17.0
> - **Source PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_EN.pdf)
> - **Source InfoSys**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/

## 关键概念

- 所有 MC_* FB 的轴接口都是 `Axis : AXIS_REF` 作为 **VAR_IN_OUT**（必须传引用，不能传值）
- 主从耦合类（GearIn / Phasing 等）同时传 `Master` 与 `Slave` 两根 AXIS_REF
- 输出统一遵循 PLCopen 三分支收敛：`Done` / `CommandAborted` / `Error` + `ErrorID`（部分老 FB 为 `ErrorId`）
- `BufferMode` 决定命令在轴忙时如何接入（Aborting / Buffered / Blending）
- `Execute` 通常是**边沿触发**；个别 FB（`MC_Stop` / `MC_GearInDyn` / `MC_GearInMultiMaster` / `MC_TorqueControl(ContinuousUpdate)`）有特殊电平 / 持续语义，详见对应 FB 文档
- 错误码 `ErrorID` 是 **TwinCAT NC 错误号**，不是 HRESULT；具体码表见 PDF 附录 / InfoSys `E_AxisErrorCodes`

## 分类索引

### Point to point motion（点对点定位，9 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_MoveAbsolute` | 绝对位置定位 | [point_to_point_motion/MC_MoveAbsolute.md](point_to_point_motion/MC_MoveAbsolute.md) |
| `MC_MoveRelative` | 相对距离定位（起点 = NC 当前设定位置） | [point_to_point_motion/MC_MoveRelative.md](point_to_point_motion/MC_MoveRelative.md) |
| `MC_MoveAdditive` | 叠加定位（起点 = 上一命令目标位置） | [point_to_point_motion/MC_MoveAdditive.md](point_to_point_motion/MC_MoveAdditive.md) |
| `MC_MoveModulo` | 模数轴定位（带方向选择，最短路径 / 正向 / 反向） | [point_to_point_motion/MC_MoveModulo.md](point_to_point_motion/MC_MoveModulo.md) |
| `MC_MoveVelocity` | 恒速无终点运动（适合传送带 / 卷绕） | [point_to_point_motion/MC_MoveVelocity.md](point_to_point_motion/MC_MoveVelocity.md) |
| `MC_MoveContinuousAbsolute` | 绝对定位 + 终末速度（过点不停） | [point_to_point_motion/MC_MoveContinuousAbsolute.md](point_to_point_motion/MC_MoveContinuousAbsolute.md) |
| `MC_MoveContinuousRelative` | 相对定位 + 终末速度（过点不停） | [point_to_point_motion/MC_MoveContinuousRelative.md](point_to_point_motion/MC_MoveContinuousRelative.md) |
| `MC_Halt` | 软停车 + 不锁轴（正常工艺停首选） | [point_to_point_motion/MC_Halt.md](point_to_point_motion/MC_Halt.md) |
| `MC_Stop` | 硬停车 + 锁轴（紧急 / 故障停车） | [point_to_point_motion/MC_Stop.md](point_to_point_motion/MC_Stop.md) |

### Superposition（叠加运动，2 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_MoveSuperImposed` | 在主运动之上叠加一段相对运动 | [superposition/MC_MoveSuperImposed.md](superposition/MC_MoveSuperImposed.md) |
| `MC_AbortSuperposition` | 中止叠加运动（不停主运动） | [superposition/MC_AbortSuperposition.md](superposition/MC_AbortSuperposition.md) |

### Homing（归零，1 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_Home` | 轴参考运行（归零）；含 DefaultHoming / Direct / ForceCalibration / ResetCalibration 多模式 | [homing/MC_Home.md](homing/MC_Home.md) |

### Manual motion（手动运动，1 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_Jog` | 手动寸动（5 种模式：standard slow/fast、continous、inching、inching modulo） | [manual_motion/MC_Jog.md](manual_motion/MC_Jog.md) |

### Axis coupling（轴耦合，4 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_GearIn` | 线性电子齿轮（固定齿比，分子分母形式） | [axis_coupling/MC_GearIn.md](axis_coupling/MC_GearIn.md) |
| `MC_GearInDyn` | 线性电子齿轮（齿比动态可调） | [axis_coupling/MC_GearInDyn.md](axis_coupling/MC_GearInDyn.md) |
| `MC_GearOut` | 解耦（⚠️ 解耦不停轴，必须接 MC_Halt） | [axis_coupling/MC_GearOut.md](axis_coupling/MC_GearOut.md) |
| `MC_GearInMultiMaster` | 多主电子齿轮（最多 4 主），从轴 = Σ(MasterN × GearRatioN) | [axis_coupling/MC_GearInMultiMaster.md](axis_coupling/MC_GearInMultiMaster.md) |

### Phasing（相位调整，3 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_PhasingAbsolute` | 设定主从轴绝对相位差（"差到 5°"） | [phasing/MC_PhasingAbsolute.md](phasing/MC_PhasingAbsolute.md) |
| `MC_PhasingRelative` | 叠加相位增量（"再差 0.2°"） | [phasing/MC_PhasingRelative.md](phasing/MC_PhasingRelative.md) |
| `MC_HaltPhasing` | 平稳停止相位调整运动（Jerk-limited） | [phasing/MC_HaltPhasing.md](phasing/MC_HaltPhasing.md) |

### Torque Control（力矩控制，1 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_TorqueControl` | 把轴切到 CST（Cyclic Synchronous Torque）模式做恒力矩控制（⚠️ 使用后必须显式切回 CSV/CSP） | [torque_control/MC_TorqueControl.md](torque_control/MC_TorqueControl.md) |

### Library version（库版本元数据，1 个）

| 标识符 | 用途 | 文档 |
|---|---|---|
| `stLibVersion_Tc2_MC2` | `VAR_GLOBAL CONSTANT`：当前 Tc2_MC2 库版本信息（配 `F_CmpLibVersion` 做开机版本校验） | [library_version/stLibVersion_Tc2_MC2.md](library_version/stLibVersion_Tc2_MC2.md) |

## 例程

所有 22 个文档都配套一个 [`examples/P_Demo_<Name>.TcPOU`](examples/) — TwinCAT 3 原生 .TcPOU 格式，右键 PLC 项目下 POUs 文件夹 → Add → Existing Item 即可导入。每个例程都按本仓库 2026-05-11 行动纲领的 D 节要求，头部带 **场景 / 价值 / 验证步骤** 三件套中文注释，变量名贴近工业语义，注释比例 ≥ 1/3。

## 与其它库的搭配

- **`Tc2_System`**：错误码比对（`F_CmpLibVersion`）、版本信息结构（`ST_LibVersion`）
- **`Tc2_MC2_Drive`** / **`Tc3_McCoordinatedMotion`**：本库不涵盖的扩展运动（飞剪、凸轮、坐标系运动）
- **`Tc_Standard`**：基础 PLC 类型与边沿检测（`R_TRIG`）

## 文档质量

所有 22 篇通过：

- `_meta/tools/verify_doc.py` — VAR 区一致、占位短语 / 中文长度 / InfoSys URL 检查全 PASS
- `_meta/tools/lint_tcpou.py` — 例程 XML 结构合法
- 引脚名审计（Pin-name audit）— 例程里每个 `pin := value` 的 LEFT 名称与对应 FB 文档的 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT 完全一致

InfoSys 主题 URL 已逐条校验（`InfoSys-checked: ✅ 2026-05-21`）。

## 已知限制 / ⚠️

- 错误码段（`ErrorID`）PDF 未在每个 FB 章节逐条枚举具体码值；本仓库不脑补具体码，仅指向 PDF 附录 / InfoSys `E_AxisErrorCodes` 总表。
- `MC_Phasing*` 系列 PDF 写作 `ErrorId`（小写 d），与其它 FB 的 `ErrorID` 不一致；本仓库严格按 PDF 大小写搬运。
- 部分 FB 的 `Acceleration` / `Deceleration` / `Jerk` / `BufferMode` 输入 PDF 标明"当前版本未实现"——本仓库照实标注。
