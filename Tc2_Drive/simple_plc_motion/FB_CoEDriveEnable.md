# FB_CoEDriveEnable

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Drive` |
| Library Version | `1.4.8` |
| Type | `FUNCTION_BLOCK` |
| Category | `SimplePlcMotion` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/10731920907.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CoEDriveEnable.TcPOU`](../examples/P_Demo_FB_CoEDriveEnable.TcPOU) |

---

## 1. 功能简述

使能 CoE（CANopen over EtherCAT）驱动器的功能块。本 FB 走 CiA 402 驱动器状态机，把一台 CoE 驱动器从禁用态拉到"运行使能"态，使其随后能够被 `FB_CoEDriveMoveVelocity` 喂入速度设定值。

本 FB 不通过 ADS 服务通道，而是直接操作链接到 `stCoeDriveIoInterface` 的过程映像（控制字 / 状态字等），属于"简单 PLC 运动控制"（SimplePlcMotion）方案：不依赖 NC 任务，由 PLC 直接驱动 CoE 伺服。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEnable : BOOL;
    bReset  : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bEnable` | `BOOL` | 激活 CoE 驱动器（电平型：`TRUE` 推动状态机走向运行使能，`FALSE` 去使能） |
| `bReset` | `BOOL` | 故障时执行一次驱动器复位，在驱动器控制字中置 "Bit 7"（CiA 402 的 Fault Reset 位） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bStatus     : BOOL;
    bDriveError : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bStatus` | `BOOL` | `bStatus = TRUE` 表示驱动器已就绪、可运行并跟随设定值（运行使能态） |
| `bDriveError` | `BOOL` | 驱动器处于错误状态 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stCoeDriveIoInterface : ST_CoeDriveIoInterface;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stCoeDriveIoInterface` | `ST_CoeDriveIoInterface` | 必须链接 CoE 驱动器过程映像的数据结构（含控制字 / 状态字 / 设定值 / 实际值等）。本 FB 通过它读写驱动器的 CiA 402 控制字与状态字 |

## 3. 行为说明

本 FB 是电平驱动（非边沿）的状态机推进型功能块，每个 PLC 周期调用以推进 CiA 402 驱动器状态机：

1. **使能推进**：`bEnable = TRUE` 时，FB 读 `stCoeDriveIoInterface` 中的状态字，按 CiA 402 状态机依次走：Switch on disabled（接通禁止）→ Ready to switch on（准备接通）→ Switched on（已接通）→ Operation enabled（运行使能），通过逐步写控制字驱动状态迁移。到达 Operation enabled 后 `bStatus := TRUE`。
2. **去使能**：`bEnable = FALSE` 时，FB 把状态机退回禁用 / 待命态，`bStatus` 回到 `FALSE`。
3. **复位分支**：`bReset = TRUE` 时在控制字置 Bit 7（Fault Reset），把驱动器从 Fault 态清回可使能态；故障期间 `bDriveError = TRUE`。
4. **错误指示**：驱动器进入 Fault 态时 `bDriveError := TRUE`，此时 `bStatus = FALSE`，需要 `bReset` 复位后才能重新使能。

**过程映像驱动**：与 SoE `_ByDriveRef` 系列不同，本 FB 不发 ADS 命令，而是每周期直接读写 `stCoeDriveIoInterface` 链接的 PDO（控制字 0x6040 / 状态字 0x6041 等），实时性好、无服务通道延迟。

**调用范式**：必须每周期调用并传入 `stCoeDriveIoInterface`（VAR_IN_OUT 必传），状态机才能持续推进；典型是先调本 FB 使能，待 `bStatus = TRUE` 后再调 `FB_CoEDriveMoveVelocity` 喂速度。

## 4. 错误码 / 返回值

本 FB 通过 `bStatus` / `bDriveError` 两个布尔输出反映状态，不提供数值错误码。

| 输出组合 | 含义 | 处理建议 |
|---|---|---|
| `bStatus = TRUE`，`bDriveError = FALSE` | 已运行使能，可喂设定值 | 调 `FB_CoEDriveMoveVelocity` |
| `bStatus = FALSE`，`bDriveError = FALSE` | 使能过程中 / 未使能 | 保持 `bEnable = TRUE` 等待状态机走完 |
| `bDriveError = TRUE` | 驱动器 Fault 态 | 给 `bReset` 复位后重新使能；具体故障原因看驱动器自身诊断（CoE 0x603F error code 等） |

PDF 与 InfoSys 均未给本 FB 的数值错误码（状态由 `bDriveError` 表达，详细故障号需读驱动器对象字典，⚠️ 待人工对照具体 CoE 驱动手册）。

## 5. 使用注意 / 常见坑

- **`stCoeDriveIoInterface` 必须正确链接过程映像**：这是 VAR_IN_OUT，本 FB 靠它读写控制字 / 状态字。在 System Manager 里把 CoE 驱动器的 PDO 链接到该结构对应字段，链接错 / 漏链 FB 无法工作，`bStatus` 永远上不来。（PDF）
- **电平型 `bEnable`，不是脉冲**：`bEnable` 要持续保持 `TRUE` 才维持使能，置 `FALSE` 立即去使能。和 `bExecute` 上升沿型 FB 语义不同。
- **`bReset` 是复位 Fault**：只在 `bDriveError = TRUE` 时有意义。建议把 `bReset` 接成"由 HMI 复位按钮的上升沿产生一个脉冲"，避免长期置位。（工程经验补充）
- **先使能再运动**：`bStatus = TRUE` 之前不要调 `FB_CoEDriveMoveVelocity`，否则设定值进不去（驱动器还没到 Operation enabled）。（PDF：MoveVelocity 要求驱动器先经本 FB 使能）
- **必须每周期调用**：状态机靠周期调用推进，漏调会卡在中间状态。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CoEDriveEnable.TcPOU`](../examples/P_Demo_FB_CoEDriveEnable.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_CoEDriveEnable
VAR
    fbDriveEnable   : FB_CoEDriveEnable;
    stCoEDriveIo    : ST_CoeDriveIoInterface;      // 在 System Manager 链接 CoE 驱动器 PDO
    rtrigReset      : R_TRIG;
    bEnableDrive    : BOOL := FALSE;               // 在线置 TRUE 推动使能状态机
    bResetReq       : BOOL := FALSE;               // 故障时在线置 TRUE 复位一次
    bDriveReady     : BOOL;                        // 在线 monitor：到达运行使能为 TRUE
    bDriveFault     : BOOL;                        // 驱动器 Fault 态
END_VAR

// bReset 取上升沿，避免长期置位
rtrigReset(CLK := bResetReq);

// 单次调用形式：VAR_IN_OUT stCoeDriveIoInterface 必传；每周期调用推进状态机
fbDriveEnable(
    bEnable := bEnableDrive,
    bReset  := rtrigReset.Q,
    stCoeDriveIoInterface := stCoEDriveIo,
    bStatus     => bDriveReady,
    bDriveError => bDriveFault
);

// 复位脉冲用完即清
IF NOT bDriveFault THEN
    bResetReq := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：用 CoE 伺服（如 EL7 系列伺服端子 / CoE 驱动器）做简单速度控制，不想引入完整 NC 配置，希望直接由 PLC 程序使能并喂速度（输送带、风机、卷绕等单纯调速场合）。
- **价值**：把 CiA 402 驱动器状态机（Switch on disabled → … → Operation enabled）的逐步控制字操作封装成一个 `bEnable` 布尔，业务侧不必手写状态字解析和控制字时序。
- **替代方案对比**：
  - 用 NC 轴 + `MC_Power`：功能全但要配 NC 任务、轴对象，配置重
  - 自己解析状态字 0x6041 / 写控制字 0x6040 走 CiA 402：要手写完整状态机，几十行且易错
  - **本 FB**：一个 `bEnable` 搞定使能，配 `FB_CoEDriveMoveVelocity` 即可纯 PLC 调速，适合无需插补的简单运动

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf) §4.5.1
- **InfoSys topic**：该 FB 在 `tcplclib_tc2_drive`（1033）英文树未检索到独立 topic 页；元信息 `Source InfoSys` 暂指向同库同类已收录的 `FB_SoEDriveEnable`（https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/10731920907.html ）作为最接近的官方参考。本 FB 接口以 PDF §4.5.1 为准。标 ⚠️ not-on-infosys
- **相关**：`FB_CoEDriveMoveVelocity`（配套，使能后喂速度）、`FB_SoEDriveEnable`（SoE 版同类）、`ST_CoeDriveIoInterface`（过程映像结构）

## 9. 待确认项

- ⚠️ 本 FB 在 InfoSys 英文树未收录独立 topic，无法做 PDF–InfoSys 逐字 diff，接口以 PDF §4.5.1 为准。
- ⚠️ `ST_CoeDriveIoInterface` 结构各字段定义见库数据类型章节（PDF），本文未逐字段罗列。
- ⚠️ 驱动器具体故障号需读 CoE 驱动器对象字典（如 0x603F），PDF/InfoSys 未列。
