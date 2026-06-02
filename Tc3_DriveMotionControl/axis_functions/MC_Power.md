# MC_Power

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_DriveMotionControl` |
| Library Version | `1.5.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `Axis functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8278916363.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_MC_Power.TcPOU`](../examples/P_Demo_MC_Power.TcPOU) |

---

## 1. 功能简述

PLCopen Motion Control 标准定义的**轴软件使能功能块（Function Block, FB）**，是 `Tc3_DriveMotionControl` 库（基于 Beckhoff 伺服端子技术的简化运动控制库）里所有运动命令的前置开关。

只要 `Enable` 保持高电平，本 FB 就持续向 NC 轴发软件使能；`Status` 输出表示"轴已就绪、可以接收运动命令"。除软件使能外，驱动器通常还需要一路**硬件使能信号**——这路信号不受 `MC_Power` 控制，必须由 PLC 另行驱动。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Enable          : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Enable` | `BOOL` | — | 轴的通用软件使能。电平触发：高电平期间持续给轴使能，置 `FALSE` 即撤销软件使能 |

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
    Status  : BOOL;
    Busy    : BOOL;
    Active  : BOOL;
    Error   : BOOL;
    ErrorID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Status` | `BOOL` | 轴已就绪可运行时为 `TRUE`。这是判断"能否发运动命令"的标志位 |
| `Busy` | `BOOL` | 只要本 FB 以 `Enable = TRUE` 被调用即为 `TRUE` |
| `Active` | `BOOL` | 表示命令正在执行 |
| `Error` | `BOOL` | 发生错误时为 `TRUE` |
| `ErrorID` | `UDINT` | `Error = TRUE` 时给出错误号（参见 §4） |

## 3. 行为说明

**触发语义**：`MC_Power` 是**电平触发**（`Enable` 型输入），不是边沿触发。`Enable = TRUE` 期间持续给轴软件使能，`Busy` 随之为 `TRUE`；置 `Enable = FALSE` 立即撤销软件使能。这与库内其它 `Execute` 边沿触发的运动 FB 截然不同——后者上升沿发一次命令即结束。

**就绪判据**：软件使能下发后，轴还要满足驱动器侧条件（硬件使能、无残留错误、伺服环锁定）才会就绪，`Status` 此时才置 `TRUE`。因此"`Enable := TRUE` 之后立刻发 Move"是错误时序——必须先轮询到 `Status = TRUE` 再发运动命令，否则运动 FB 会因轴未就绪而报错。

**软件使能 vs 硬件使能**：本 FB 只管软件使能这一路。多数驱动器还需要一路独立的硬件使能（数字量输出 / STO 解除等），该路信号由 PLC 业务代码单独控制，`MC_Power` 不触碰。两路使能都满足，伺服才真正上电锁轴。

**调用方式**：本 FB 须周期调用（放在循环任务里每周期调）。停机时把 `Enable` 置 `FALSE` 即落软件使能；注意单纯落软件使能是**非受控停车**（轴自由滑行），正常停车应先用 `MC_Halt` 把轴停住再落使能。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 TwinCAT NC/驱动错误号（不是 HRESULT）。

| 返回值 / 错误码 | 含义 | 处理建议 |
|---|---|---|
| `Error = FALSE` | 无错误 | 正常；等待 `Status = TRUE` 后再发运动命令 |
| `Error = TRUE` + `ErrorID ≠ 0` | 使能过程出错（驱动未响应、硬件使能缺失、轴残留故障等） | 检查硬件使能信号是否给出、驱动器是否上电；用 `MC_Reset` 清轴残留故障后重试 |

PDF 与 InfoSys 在本 FB 章节均未逐条列出具体 `ErrorID` 码值，仅说明"`Error` 置位时本参数给出错误号"。具体码值需对照 TwinCAT NC 错误码总表（⚠️ PDF + InfoSys 本章节未枚举）。

## 5. 使用注意 / 常见坑

- **`Enable` 是电平不是边沿**：把它当 `Execute` 一样"打一下脉冲"会导致使能立刻被撤销。必须在循环里持续给 `Enable := TRUE`。
- **别把 `Enable = TRUE` 当成"轴已就绪"**：使能下发≠就绪。运动命令的前提是 `Status = TRUE`，不是 `Enable = TRUE`。常见现象是"刚使能就发 Move，结果 Move 报错轴未 Ready"。
- **硬件使能要自己给**：`MC_Power` 不控制硬件使能 / STO。只给软件使能、不给硬件使能，伺服不会真正上电。（工程经验补充）
- **落使能 = 非受控停车**：运行中直接 `Enable := FALSE` 会让轴自由滑行（drive coast），高速时机械冲击大。正常停车流程是先 `MC_Halt` 停住、`Done` 后再落使能。（工程经验补充）
- **本 FB 须周期调用**：和所有 PLCopen FB 一样，放在循环任务里每周期调用一次；漏调会导致状态不更新。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MC_Power.TcPOU`](../examples/P_Demo_MC_Power.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 场景：CX 控制器带一个伺服端子驱动的进给轴，上电后先给软件使能并等待就绪
PROGRAM P_Demo_MC_Power
VAR
    fbPowerAxis     : MC_Power;
    axisFeed        : AXIS_REF;            // 进给轴；必须先在 System Manager 配好
    bDriveSwEnable  : BOOL := FALSE;       // 在线写 TRUE 给软件使能
    bAxisReady      : BOOL;                // Status 输出：轴是否就绪
    bPowerBusy      : BOOL;
    bPowerError     : BOOL;
    nPowerErrorID   : UDINT;
END_VAR

// 电平触发：Enable 持续高电平才保持软件使能；Axis 是 VAR_IN_OUT 用 :=
fbPowerAxis(
    Enable  := bDriveSwEnable,
    Axis    := axisFeed,
    Status  => bAxisReady,
    Busy    => bPowerBusy,
    Error   => bPowerError,
    ErrorID => nPowerErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：所有用 Beckhoff 伺服端子（如 EL72xx / EL70xx 系列）做简单单轴运动的设备，开机第一步都要给轴软件使能。进给轴、卷绕轴、单关节定位等任意运动场合的"总开关"。
- **价值**：业务代码不必去拼 NC 轴控制字里的使能位、不必处理使能下发后的状态握手，单个 FB 调用即把"软件使能 + 就绪状态上报"封装好；`Status` 直接给出可否发运动命令的判断。
- **替代方案对比**：
  - 直接写 NC 轴接口控制字：要手动设置 `nControl` 使能位并轮询 `nState`，对接口字段熟悉度要求高，升级有适配风险
  - 不用使能 FB 直接发 Move：轴未使能时 Move 必报错，无意义
  - **本 FB**：PLCopen 标准做法，与库内其它运动 FB 配套，时序清晰

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_DriveMotionControl_EN.pdf) §5.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_drivemotioncontrol/8278916363.html
- **相关 FB**：`MC_Reset`（清轴错误）、`MC_Halt` / `MC_Stop`（停轴）、各 `MC_Move*`（使能就绪后才能发的运动命令）
