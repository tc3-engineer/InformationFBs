# MC_Home

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_DriveMotionControl` |
| Library Version | `1.5.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `Homing` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8280289803.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_Home.TcPOU`](../examples/P_Demo_MC_Home.TcPOU) |

---

## 1. 功能简述

PLCopen Motion Control 标准定义的**轴回零（参考运行，Homing）功能块（Function Block, FB）**。`Execute` 上升沿启动一次回零，把轴运行到参考点并把该点位置标定为 `Position` 指定的绝对参考位置。

回零方式由 `Options.ReferenceMode` 决定，整体行为由 `HomingMode` 选择（默认回零、直接设位置、撞挡块回零、强制 / 复位标定等）。相关参数可能需要在驱动参数里设置（伺服端子见对象 DMC Setting (0x8030) / DMC Features (0x8031)）。由于参考位置一般是在运动中设定的，轴不会精确停在该位置——停止位置与之相差一个制动距离，但**标定本身是精确的**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute         : BOOL;
    Position        : LREAL         := DEFAULT_HOME_POSITION;
    HomingMode      : MC_HomingMode;
    Options         : ST_HomingOptions;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次回零命令 |
| `Position` | `LREAL` | `DEFAULT_HOME_POSITION` | 回零后轴被设置到的绝对参考位置。也可用常量 `DEFAULT_HOME_POSITION`，此时采用 TwinCAT System Manager 里设定的"回零参考位置" |
| `HomingMode` | `MC_HomingMode` | — | 决定如何执行标定（类型 `MC_HomingMode`）：`MC_DefaultHoming`（默认回零）；`MC_Direct`（不运动，直接把轴位置设为 `Position`）；`MC_Block`（撞机械挡块回零）；`MC_ForceCalibration`（强制"已标定"状态，不运动、位置不变）；`MC_ResetCalibration`（复位轴的标定状态，不运动、位置不变） |
| `Options` | `ST_HomingOptions` | — | 含附加参数的数据结构：`SearchDirection`（找参考凸轮的方向）、`SearchVelocity`（找凸轮速度）、`SyncDirection`（检到凸轮后找其下降沿的方向）、`SyncVelocity`（找下降沿速度）、`ReferenceMode`（参考模式，当前仅 `ENCODERREFERENCEMODE_CAMATDIGITALINPUT`）、`Acceleration` / `Deceleration`（回零加减速）。参考凸轮信号须接到数字端子输入（`HomingMode = MC_DefaultHoming`） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | 轴数据结构，在系统中唯一标识一根轴；含当前轴状态，包括位置、速度、错误状态等。**必须传引用**（VAR_IN_OUT 语义） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done           : BOOL;
    Busy           : BOOL;
    Active         : BOOL;
    CommandAborted : BOOL;
    Error          : BOOL;
    ErrorID        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 轴已标定且运动完成时置 `TRUE` |
| `Busy` | `BOOL` | `Execute` 启动后置 `TRUE` 并持续到运动命令处理结束；`Busy = FALSE` 时 FB 可接受新命令，同时 `Done` / `CommandAborted` / `Error` 之一置位 |
| `Active` | `BOOL` | **当前未实现**——本应表示命令正在运行；命令被缓冲时要等正在运行的命令结束后才激活 |
| `CommandAborted` | `BOOL` | 命令未能完整执行时置 `TRUE` |
| `Error` | `BOOL` | 发生错误时为 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出错误号（参见 §4） |

## 3. 行为说明

**触发语义**：`Execute` **上升沿**启动一次回零。上升沿后 `Busy` 置 `TRUE`，回零完成后 `Done` 置 `TRUE`、`Busy` 落 `FALSE`。输出遵循库通用规则（`Busy` / `Done` / `CommandAborted` / `Error` 互斥）。被打断则 `CommandAborted = TRUE`。

**`HomingMode` 的五种行为分支**：
- `MC_DefaultHoming`：标准回零。轴按 `Options` 里的方向 / 速度去找参考凸轮，凸轮信号须接数字端子输入；找到后按 `SyncDirection`/`SyncVelocity` 同步到凸轮边沿，最后把位置标定为 `Position`。
- `MC_Direct`：**不运动**，直接把轴位置设为 `Position`（类似坐标重定义）。
- `MC_Block`：撞机械挡块回零（以挡块为参考）。
- `MC_ForceCalibration`：强制把轴置为"已标定"状态，不运动、位置不变。
- `MC_ResetCalibration`：复位轴的标定状态，不运动、位置不变。

**`MC_DefaultHoming` 的多阶段时序**：标准回零有多个阶段（找凸轮 → 检到凸轮 → 同步到凸轮下降沿 → 完成标定）。PDF 以时序图说明了 `MC_DefaultHoming` 各阶段的先后顺序。

**停止位置 vs 标定精度**：参考位置一般在轴运动过程中被设定，因此轴不会精确停在参考位置上——实际停止点与参考位置相差一个制动距离。但要强调：这只影响"停在哪"，**标定本身（坐标与机械的对应关系）是精确的**，不会因制动距离引入标定误差。

**`Active` 当前未实现**：PDF 明确标注 `Active` 输出"Currently not implemented"。判断回零是否完成请用 `Done`，不要依赖 `Active`。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC/驱动错误号（不是 HRESULT）。

| 返回值 / 错误码 | 含义 | 处理建议 |
|---|---|---|
| `Done = TRUE` | 回零成功、轴已标定 | 轴坐标已与机械参考点对齐，可正常运动 |
| `CommandAborted = TRUE` | 回零被打断（如被 `MC_Stop`） | 视业务决定是否重新回零 |
| `Error = TRUE` + `ErrorID ≠ 0` | 回零出错（找不到凸轮、驱动参数未配、轴未使能等） | 检查参考凸轮接线 / 数字输入、驱动 DMC 参数、轴是否已 `MC_Power` 使能 |

PDF 与 InfoSys 在本 FB 章节均未逐条列出具体 `ErrorID` 码值，具体码值需对照 TwinCAT NC 错误码总表（⚠️ PDF + InfoSys 本章节未枚举）。

## 5. 使用注意 / 常见坑

- **`Active` 当前未实现，别用它判完成**：用 `Done`。这是 PDF 明文标注的限制。
- **参考凸轮信号要接数字端子**：`MC_DefaultHoming` 依赖参考凸轮，其信号必须路由到数字端子输入。没接 / 接错会找不到凸轮导致回零超时或报错。
- **`Position` 默认用 `DEFAULT_HOME_POSITION`**：不显式给值时，采用 System Manager 里配的"回零参考位置"。改参考位置要在 System Manager 改，或显式传 `Position`。
- **轴不精确停在参考位置是正常的**：停止点与参考位置差一个制动距离，但标定精确。不要误以为"没停在 0 就是回零不准"。
- **`MC_Direct` 不运动**：它只设位置，等价于坐标重定义；需要物理回零请用 `MC_DefaultHoming` / `MC_Block`。
- **回零前要先使能**：轴未 `MC_Power` 使能时回零无法运动。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_Home.TcPOU`](../examples/P_Demo_MC_Home.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：龙门轴每次开机做标准回零，找参考凸轮后把参考点标定为 0 mm
PROGRAM P_Demo_MC_Home
VAR
    fbHome          : MC_Home;
    axisGantry      : AXIS_REF;
    rtStartHoming   : R_TRIG;              // 回零请求转上升沿
    bStartHoming    : BOOL := FALSE;       // 在线写 TRUE 启动一次回零
    eHomingMode     : MC_HomingMode := MC_DefaultHoming;  // 标准回零
    bHomeDone       : BOOL;
    bHomeBusy       : BOOL;
    bHomeAborted    : BOOL;
    bHomeError      : BOOL;
    nHomeErrorID    : UDINT;
END_VAR

// 回零请求转上升沿；Position 用默认 DEFAULT_HOME_POSITION；Axis 是 VAR_IN_OUT 用 :=
rtStartHoming(CLK := bStartHoming);
fbHome(
    Execute        := rtStartHoming.Q,
    Position       := DEFAULT_HOME_POSITION,
    HomingMode     := eHomingMode,
    Axis           := axisGantry,
    Done           => bHomeDone,
    Busy           => bHomeBusy,
    CommandAborted => bHomeAborted,
    Error          => bHomeError,
    ErrorID        => nHomeErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：所有带绝对坐标系需求的设备开机回零：龙门 / 直线进给轴找参考凸轮、转台找零位、撞挡块回零的简易机构。回零让轴的逻辑坐标与机械参考点对齐，是后续所有绝对定位的前提。
- **价值**：业务代码不必去拼回零的多阶段状态机（找凸轮 → 同步边沿 → 标定），不必自己处理"运动中标定 + 制动距离"的细节，单个 FB 调用即完成；`HomingMode` 一个枚举覆盖默认回零 / 直接设位置 / 撞挡块 / 强制 / 复位标定五种需求。
- **替代方案对比**：
  - 自己写回零状态机（点动找凸轮 + 读输入 + 调 `MC_SetPosition`）：代码量大、边界条件多、易出错
  - 用 `MC_SetPosition` 替代：只能"直接设位置"，无法做"运动找凸轮"的真回零
  - **本 FB**：PLCopen 标准回零入口，多模式覆盖，与 System Manager 的回零参数配置打通

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf) §6.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8280289803.html
- **相关 FB / 类型**：`MC_SetPosition`（直接设位置，无运动）、`MC_Power`（回零前使能）、`MC_HomingMode`（回零模式枚举）、`ST_HomingOptions`（回零参数结构）
