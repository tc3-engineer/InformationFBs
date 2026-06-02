# Tc3_DriveMotionControl — 基于伺服端子的简化运动控制库

> Beckhoff TwinCAT 3 标准库，为基于 Beckhoff 伺服端子（如 EL72xx / EL70xx 系列）技术的**简单机器应用**提供运动控制功能块。
> 基于 **PLCopen Motion Control 功能块规范 V2.0**，提供 IEC 61131-3 兼容的轴使能、复位、定位、回零、寸动、测头采样等原语。
>
> - **Library Version**：1.5.5
> - **Source PDF**：[TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf)
> - **Source InfoSys**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/index.html

## 关键概念

- 所有 MC_* 功能块的轴接口都是 `Axis : AXIS_REF` 作为 **VAR_IN_OUT**（必须传引用，不能传值）；测头类（`MC_TouchProbe` / `MC_AbortTrigger`）还把 `TriggerInput : TRIGGER_REF` 作为 VAR_IN_OUT 传入
- 运动 / 复位 / 定位 / 回零 / 测头类用 **`Execute` 上升沿**触发；`MC_Power` 用 **`Enable` 电平**触发（持续给使能）；`MC_Jog` 用 `JogForward` / `JogBackwards` 上升沿触发
- 输出遵循 PLCopen 通用规则：`Busy` / `Done` / `CommandAborted` / `Error` 互斥（同时只有一个为 `TRUE`）；`MC_MoveVelocity` 的成功信号是 `InVelocity` 而非 `Done`
- **`MC_Stop` 是通用规则的特例**：减速到 0 后 `Done = TRUE`，但 `Busy` / `Active` 仍保持 `TRUE`（轴被锁），只有 `Execute` 置 `FALSE` 后才解锁；解锁还需 `MC_Reset`
- **本库不提供 `BufferMode`**：与 Tc2_MC2 等库不同，本库 Move 类 FB 没有 `BufferMode` 输入，少量可选参数走 `Options : ST_MoveOptions` / `ST_HomingOptions` / `ST_SetPositionOptions`
- 错误码 `ErrorID`（`MC_TouchProbe` 输出写作 `ErrorId`，小写 d）是 **TwinCAT NC/驱动错误号**，不是 HRESULT；PDF / InfoSys 在各 FB 章节未逐条枚举具体码值
- 相关驱动参数（测头 / 回零）可能需在驱动对象 DMC Setting (0x8030) / DMC Features (0x8031) 中设置

## 分类索引

### Axis functions（轴功能，3 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_Power` | 轴软件使能（电平触发，`Status` 表示就绪） | [axis_functions/MC_Power.md](axis_functions/MC_Power.md) |
| `MC_Reset` | 轴复位（从故障拉回可运行，常连带复位驱动器） | [axis_functions/MC_Reset.md](axis_functions/MC_Reset.md) |
| `MC_SetPosition` | 设置 / 重定义轴位置（绝对 / 相对，不产生运动） | [axis_functions/MC_SetPosition.md](axis_functions/MC_SetPosition.md) |

### Touch probe（测头采样，2 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_TouchProbe` | 硬件锁存测头采样（触发瞬间高精度记录轴位置） | [touch_probe/MC_TouchProbe.md](touch_probe/MC_TouchProbe.md) |
| `MC_AbortTrigger` | 取消测头采样周期（释放硬件锁存，需同一 `TriggerInput`） | [touch_probe/MC_AbortTrigger.md](touch_probe/MC_AbortTrigger.md) |

### Homing（回零，1 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_Home` | 轴参考运行（回零）；含 DefaultHoming / Direct / Block / ForceCalibration / ResetCalibration 多模式 | [homing/MC_Home.md](homing/MC_Home.md) |

### Manual motion（手动运动，1 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_Jog` | 手动寸动（`JogForward` / `JogBackwards` 边沿触发，方向互锁） | [manual_motion/MC_Jog.md](manual_motion/MC_Jog.md) |

### Point to point motion（点对点定位，6 个）

| FB | 用途 | 文档 |
|---|---|---|
| `MC_MoveAbsolute` | 绝对位置定位（直线轴；模数轴按连续绝对坐标） | [point_to_point_motion/MC_MoveAbsolute.md](point_to_point_motion/MC_MoveAbsolute.md) |
| `MC_MoveRelative` | 相对距离定位（起点 = NC 当前设定位置） | [point_to_point_motion/MC_MoveRelative.md](point_to_point_motion/MC_MoveRelative.md) |
| `MC_MoveModulo` | 模数轴定位（正 / 负 / 最短路径；基于 `ModuloFactor`） | [point_to_point_motion/MC_MoveModulo.md](point_to_point_motion/MC_MoveModulo.md) |
| `MC_MoveVelocity` | 恒速无终点运动（成功信号 `InVelocity`；达速后不再监视） | [point_to_point_motion/MC_MoveVelocity.md](point_to_point_motion/MC_MoveVelocity.md) |
| `MC_Halt` | 软停车 + 不锁轴（正常工艺停首选） | [point_to_point_motion/MC_Halt.md](point_to_point_motion/MC_Halt.md) |
| `MC_Stop` | 硬停车 + 锁轴（故障 / 紧急停；需 `MC_Reset` 解锁） | [point_to_point_motion/MC_Stop.md](point_to_point_motion/MC_Stop.md) |

### Library version（库版本元数据，1 个）

| 标识符 | 用途 | 文档 |
|---|---|---|
| `stLibVersion_Tc3_DriveMotionControl` | `VAR_GLOBAL CONSTANT`：当前库版本信息（配 `F_CmpLibVersion` 做开机版本校验） | [library_version/stLibVersion_Tc3_DriveMotionControl.md](library_version/stLibVersion_Tc3_DriveMotionControl.md) |

## 例程

全部 14 篇文档都配套一个 [`examples/P_Demo_<Name>.TcPOU`](examples/) — TwinCAT 3 原生 .TcPOU 格式，右键 PLC 项目下 POUs 文件夹 → Add → Existing Item 即可导入。每个例程头部带 **场景 / 价值 / 验证步骤** 三件套中文注释，变量名贴近工业语义（`axisFeed` / `bMotorStartReq` 风格），注释比例 ≥ 1/3。

所有 MC_* 例程中 `Axis : AXIS_REF` 都作为 **VAR_IN_OUT** 用 `:=` 传引用；`Execute` 型 FB 的触发均经 `R_TRIG` 走上升沿（演示正确的边沿语义）。

## 与其它库的搭配

- **`Tc2_System`**：版本比对（`F_CmpLibVersion`）、版本信息结构（`ST_LibVersion`）
- **`Tc2_MC2`** / **`Tc3_McCoordinatedMotion`**：本库面向"基于伺服端子的简单单轴应用"；更复杂的 NC PTP 运动、凸轮、坐标系运动用 Tc2_MC2 / 协调运动库
- **`Tc_Standard`** / **`Tc2_Standard`**：基础 PLC 类型与边沿检测（`R_TRIG`）

## 验证基线

全部 14 篇通过：

- `_meta/tools/verify_doc.py` — VAR 区逐字一致（含 `Position := DEFAULT_HOME_POSITION`、`Direction := MC_Positive_Direction` 等默认值字面）、占位短语 / 中文长度 / InfoSys topic URL 检查全 PASS（14/14）
- `_meta/tools/lint_tcpou.py` — 例程 XML 结构合法（14/14）
- InfoSys 主题 URL 已逐条校验（`InfoSys-checked: ✅ 2026-06-02`），与 PDF VAR 区双源对照一致

## 已知限制 / ⚠️

- 错误码段（`ErrorID`）PDF 未在每个 FB 章节逐条枚举具体码值；本仓库不脑补具体码，仅说明 `ErrorID` 为 TwinCAT NC/驱动错误号并指向 NC 错误码总表。
- `MC_TouchProbe` 的错误输出 PDF 写作 `ErrorId`（小写 d），与其它 FB 的 `ErrorID`（大写 D）不一致；本仓库严格按 PDF 大小写搬运。
- `MC_Jog` 的 `Active` 输出、`MC_MoveVelocity` 的 `ContinuousUpdate` 输入出现在 PDF 图示 / 描述表中，但**未列入对应 FB 的 VAR 代码块**；本仓库严格按 PDF 的 VAR 代码块搬运接口，相关输出 / 输入在文档 §2 / §3 中以注记说明。
- `MC_Home` 的 `Active` 输出 PDF 明确标注"当前未实现（Currently not implemented）"——判断回零完成请用 `Done`。
- 章节 6.3.4 "Modulo positioning" 为模数定位的说明性小节（非独立 POU），其内容已并入 `MC_MoveModulo` 文档；章节 7.x 为数据类型 / 枚举 / 结构（AXIS_REF、MC_HomingMode、TRIGGER_REF 等），按本仓库约定不单独成篇（被引用的 DUT 不独立建文档）。
