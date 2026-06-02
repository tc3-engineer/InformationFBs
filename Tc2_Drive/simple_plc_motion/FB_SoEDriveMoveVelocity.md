# FB_SoEDriveMoveVelocity

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Drive` |
| Library Version | `1.4.8` |
| Type | `FUNCTION_BLOCK` |
| Category | `SimplePlcMotion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/10731923211.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEDriveMoveVelocity.TcPOU`](../examples/P_Demo_FB_SoEDriveMoveVelocity.TcPOU) |

---

## 1. 功能简述

为 SoE（Sercos over EtherCAT）驱动器生成简单三段式速度曲线的功能块。本 FB 生成一条无 jerk（加加速度）限制的三段速度型材（加速 / 匀速 / 减速），直接喂给 SoE 驱动器作为速度设定值。可在某个可参数化的速度阈值上下使用不同的加 / 减速度，目标速度可在运行中实时修改。

使用前 SoE 驱动器必须已通过 `FB_SoEDriveEnable` 使能（到达运行使能态）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEnable            : BOOL;
    fVelocity          : LREAL;
    fAcceleration1     : LREAL;
    fAccelaration2     : LREAL;
    fDeceleration1     : LREAL;
    fDeceleration2     : LREAL;
    bNegativeDirection : BOOL;
    stOptions          : ST_DriveMoveVelocityOptions;
END_VAR
```

> 注：第 4 个输入在 PDF 的 VAR 区里拼作 `fAccelaration2`（少一个字母 e，原文如此），其说明行写作 "Acceleration 2"。本表保留 PDF VAR 区的字面拼写。

| 名称 | 类型 | 说明 |
|---|---|---|
| `bEnable` | `BOOL` | 激活设定值生成（电平型：`TRUE` 开始按曲线输出速度，`FALSE` 停止生成） |
| `fVelocity` | `LREAL` | 目标速度。`fVelocity` 可在运行中修改 |
| `fAcceleration1` | `LREAL` | 加速度 1，用于参数化速度阈值 `stOptions.fVelocityThreshold` **以下** |
| `fAccelaration2` | `LREAL` | 加速度 2，用于速度阈值 `stOptions.fVelocityThreshold` **以上**（PDF VAR 区字面拼写 `fAccelaration2`） |
| `fDeceleration1` | `LREAL` | 减速度 1，用于速度阈值 `stOptions.fVelocityThreshold` 以下 |
| `fDeceleration2` | `LREAL` | 减速度 2，用于速度阈值 `stOptions.fVelocityThreshold` 以上 |
| `bNegativeDirection` | `BOOL` | `bNegativeDirection` 反转运行方向 |
| `stOptions` | `ST_DriveMoveVelocityOptions` | 附加参数的数据结构（含速度阈值 `fVelocityThreshold` 等） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bInVelocity     : BOOL;
    bBusy           : BOOL;
    bError          : BOOL;
    iErrorID        : UDINT;
    fActualVelocity : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bInVelocity` | `BOOL` | 目标速度已达到 |
| `bBusy` | `BOOL` | 只要 FB 处于活动状态、正在计算设定值型材，`bBusy` 即为 `TRUE` |
| `bError` | `BOOL` | 发生错误时 `bError` 变为 `TRUE` |
| `iErrorID` | `UDINT` | 错误号 |
| `fActualVelocity` | `LREAL` | 驱动器当前实际达到的速度 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stSoEDriveIoInterface : ST_SoeDriveIoInterface;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stSoEDriveIoInterface` | `ST_SoeDriveIoInterface` | SoE 驱动器的过程映像（与 `FB_SoEDriveEnable` 用同一个实例链接）。本 FB 通过它把生成的速度设定值写给驱动器、读回实际速度 |

> 注：PDF §4.5.4 的 VAR_OUTPUT 后那张说明表里，该 VAR_IN_OUT 行误抄成了 `stCoEDriveIoInterface` / `ST_CoeDriveIoInterface`（CoE 字样），与 VAR_IN_OUT 声明区给出的 `stSoEDriveIoInterface : ST_SoeDriveIoInterface` 不一致。本文以**声明区**为准（SoE 版用 SoE 接口结构），表中 CoE 字样判定为 PDF 文档复制错误。

## 3. 行为说明

本 FB 是电平驱动（`bEnable`）的速度型材生成器，每个 PLC 周期调用以推进速度曲线：

1. **启动**：`bEnable = TRUE`（且驱动器已由 `FB_SoEDriveEnable` 使能）时，FB 按当前速度与目标 `fVelocity` 的差，用相应加 / 减速度生成三段曲线（加速→匀速→减速），把速度设定值写入 `stSoEDriveIoInterface`，`bBusy := TRUE`。
2. **达速**：实际速度到达目标速度时 `bInVelocity := TRUE`；`fActualVelocity` 持续给出当前实际速度。
3. **运行中改速**：`fVelocity` 可随时改，FB 用对应加 / 减速度平滑过渡到新目标。
4. **方向**：`bNegativeDirection = TRUE` 反向运行。
5. **停止**：`bEnable = FALSE` 停止设定值生成。
6. **错误分支**：出错时 `bError := TRUE`，`iErrorID` 给出错误号。

**双段加减速语义**：以 `stOptions.fVelocityThreshold` 为界，阈值**以下**用 `fAcceleration1` / `fDeceleration1`，阈值**以上**用 `fAccelaration2` / `fDeceleration2`。低速段与高速段可用不同加减速特性。

**无 jerk 限制**：本 FB 生成的是梯形 / 三段速度曲线，没有加加速度限制，速度拐点处加速度是阶跃的；需要 S 曲线平滑应另选带 jerk 限制的方案。

**前置条件**：驱动器必须先经 `FB_SoEDriveEnable` 到运行使能态，且两个 FB 用同一个 `stSoEDriveIoInterface` 实例（VAR_IN_OUT 必传）。

## 4. 错误码 / 返回值

| 输出 | 含义 | 处理建议 |
|---|---|---|
| `bInVelocity = TRUE` | 已达目标速度 | 速度环稳定 |
| `bBusy = TRUE` | 正在计算 / 输出速度型材 | 正常运行中 |
| `bError = TRUE` | 发生错误 | 读 `iErrorID` 定位 |
| `iErrorID`（UDINT） | 错误号 | 具体码表 PDF/InfoSys 未列（⚠️ 待人工对照库错误号 / 驱动器 Sercos 诊断） |

PDF 与 InfoSys 均未给 `iErrorID` 的具体取值表（⚠️ 待人工确认）。

## 5. 使用注意 / 常见坑

- **必须先用 `FB_SoEDriveEnable` 使能**：驱动器未到运行使能态时本 FB 喂的速度进不去。两个 FB 串联使用，且用同一个 `stSoEDriveIoInterface` 实例。（PDF）
- **VAR 区拼写是 `fAccelaration2`（少个 e）**：库接口字面拼写，赋值时引脚名必须照写 `fAccelaration2 := ...`，写成 `fAcceleration2` 会编译报"未知参数"。（PDF VAR 区原文）
- **PDF 说明表把 VAR_IN_OUT 误标为 CoE 结构**：实际声明区是 `ST_SoeDriveIoInterface`，以声明区为准。（PDF 文档错误）
- **`stOptions.fVelocityThreshold` 决定用哪组加减速**：阈值以下用 1，以上用 2。不分段就把 1、2 设相同值。
- **无 jerk 限制**：梯形速度曲线，拐点加速度突变；对机械冲击敏感场合需另选 S 曲线方案。（工程经验补充）
- **电平型 `bEnable` + 每周期调用并传 `stSoEDriveIoInterface`**：曲线靠周期计算推进，漏调会卡。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEDriveMoveVelocity.TcPOU`](../examples/P_Demo_FB_SoEDriveMoveVelocity.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_SoEDriveMoveVelocity
VAR
    fbDriveEnable   : FB_SoEDriveEnable;           // 先使能
    fbMoveVelocity  : FB_SoEDriveMoveVelocity;     // 再喂速度
    stSoEDriveIo    : ST_SoEDriveIoInterface;      // 两个 FB 共用同一过程映像实例
    stVelOptions    : ST_DriveMoveVelocityOptions; // 含速度阈值等附加参数
    bEnableDrive    : BOOL := FALSE;               // 在线置 TRUE 使能驱动器
    bRunConveyor    : BOOL := FALSE;               // 在线置 TRUE 开始跑速度曲线
    fTargetVel      : LREAL := 1000.0;             // 目标速度（驱动器速度单位）
    bDriveReady     : BOOL;                        // 使能完成
    bDriveFault     : BOOL;
    bAtSpeed        : BOOL;                        // 已达目标速度
    bMoveBusy       : BOOL;
    bMoveError      : BOOL;
    iMoveErrId      : UDINT;
    fActVel         : LREAL;                       // 在线 monitor 实际速度
END_VAR

// 第一步：使能 SoE 驱动器（VAR_IN_OUT 必传；SoE 版无 bReset）
fbDriveEnable(
    bEnable := bEnableDrive,
    stSoeDriveIoInterface := stSoEDriveIo,
    bStatus     => bDriveReady,
    bDriveError => bDriveFault
);

// 第二步：使能成功后才喂速度；引脚名 fAccelaration2 按库字面拼写（少个 e）
fbMoveVelocity(
    bEnable            := bRunConveyor AND bDriveReady,
    fVelocity          := fTargetVel,
    fAcceleration1     := 500.0,
    fAccelaration2     := 800.0,
    fDeceleration1     := 500.0,
    fDeceleration2     := 800.0,
    bNegativeDirection := FALSE,
    stOptions          := stVelOptions,
    stSoEDriveIoInterface := stSoEDriveIo,
    bInVelocity     => bAtSpeed,
    bBusy           => bMoveBusy,
    bError          => bMoveError,
    iErrorID        => iMoveErrId,
    fActualVelocity => fActVel
);
```

## 7. 业务场景与实际价值

- **场景**：SoE 伺服（如 AX5000）驱动输送带 / 风机 / 卷绕轴做纯调速运行，需要带加减速的平滑起停且能运行中改速度，但不需要位置插补 / 同步，不想配 NC。
- **价值**：把"三段速度曲线生成 + 双段加减速 + 实时改速 + 写 SoE 设定值"封装成一个 FB，配 `FB_SoEDriveEnable` 即可纯 PLC 实现带加减速的调速。
- **替代方案对比**：
  - NC 轴 + `MC_MoveVelocity`：功能全、带 jerk 限制，但要配 NC 任务和轴对象
  - 自己写斜坡发生器 + 写 Sercos 目标速度 IDN：要手算加减速分段、处理改速过渡
  - **本 FB**：现成三段曲线 + 双段加减速 + 运行中改速，适合无需插补的简单调速

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf) §4.5.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/10731923211.html
- **相关**：`FB_SoEDriveEnable`（前置使能，配套）、`FB_CoEDriveMoveVelocity`（CoE 版同类）、`ST_DriveMoveVelocityOptions` / `ST_SoeDriveIoInterface`（参数 / 过程映像结构）

## 9. 待确认项

- ⚠️ PDF VAR 区第 4 个输入拼作 `fAccelaration2`（与说明行 "Acceleration 2" 不一致），本文按 VAR 区字面保留；实际库符号以工程编译为准。
- ⚠️ PDF §4.5.4 说明表把 VAR_IN_OUT 误标为 `stCoEDriveIoInterface` / `ST_CoeDriveIoInterface`，与声明区 `ST_SoeDriveIoInterface` 矛盾；本文以声明区为准。
- ⚠️ `iErrorID` 取值表与 `ST_DriveMoveVelocityOptions` 字段定义 PDF/InfoSys 未逐条列出。
