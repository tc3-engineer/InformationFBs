# FB_SoEDriveEnable

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
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEDriveEnable.xml`](../examples/P_Demo_FB_SoEDriveEnable.xml) |

---

## 1. 功能简述

使能 SoE（Sercos over EtherCAT）驱动器的功能块。本 FB 走 Sercos 驱动器状态机，把一台 SoE 驱动器从禁用态拉到"运行使能"态，使其随后能被 `FB_SoEDriveMoveVelocity` 喂入速度设定值。

本 FB 直接操作链接到 `stSoeDriveIoInterface` 的过程映像（Sercos 控制字 / 状态字等），属于"简单 PLC 运动控制"（SimplePlcMotion）方案：不依赖 NC 任务，由 PLC 直接驱动 SoE 伺服（如 AX5000）做调速。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEnable : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bEnable` | `BOOL` | 激活 SoE 驱动器（电平型：`TRUE` 推动状态机走向运行使能，`FALSE` 去使能） |

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
    stSoeDriveIoInterface : ST_SoEDriveIoInterface;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stSoeDriveIoInterface` | `ST_SoEDriveIoInterface` | 必须链接 SoE 驱动器过程映像的数据结构（含 Sercos 控制字 / 状态字 / 设定值 / 实际值等）。本 FB 通过它读写驱动器的 Sercos 控制字与状态字 |

## 3. 行为说明

本 FB 是电平驱动（非边沿）的状态机推进型功能块，每个 PLC 周期调用以推进 Sercos 驱动器状态机：

1. **使能推进**：`bEnable = TRUE` 时，FB 读 `stSoeDriveIoInterface` 中的 Sercos 状态字（drive status word），按 Sercos 状态机依次走：从禁用 / 待命态逐步到运行使能（对应 Sercos 的相 / 使能逻辑，概念上等同 Switch on disabled → Ready → Operation enabled 这条链），逐步写控制字驱动状态迁移。到达运行使能后 `bStatus := TRUE`。
2. **去使能**：`bEnable = FALSE` 时，FB 把状态机退回待命态，`bStatus` 回到 `FALSE`。
3. **错误指示**：驱动器进入错误态时 `bDriveError := TRUE`，此时 `bStatus = FALSE`，需先清错（驱动器侧复位，如配合 `FB_SoEReset_ByDriveRef`）才能重新使能。

**过程映像驱动**：与 `_ByDriveRef` 系列发 ADS 命令不同，本 FB 每周期直接读写 `stSoeDriveIoInterface` 链接的 Sercos 过程数据（控制字 / 状态字），实时性好、无服务通道延迟。

**与 CoE 版的区别**：`FB_CoEDriveEnable` 带 `bReset` 输入（CiA 402 控制字 Bit 7 复位），而本 SoE 版**没有 `bReset` 输入**——SoE 驱动器的故障复位走另外的机制（如 `FB_SoEReset_ByDriveRef` 复位 `S-0-0099`）。

**调用范式**：必须每周期调用并传入 `stSoeDriveIoInterface`（VAR_IN_OUT 必传）；典型是先调本 FB 使能，待 `bStatus = TRUE` 后再调 `FB_SoEDriveMoveVelocity` 喂速度。

## 4. 错误码 / 返回值

本 FB 通过 `bStatus` / `bDriveError` 两个布尔输出反映状态，不提供数值错误码。

| 输出组合 | 含义 | 处理建议 |
|---|---|---|
| `bStatus = TRUE`，`bDriveError = FALSE` | 已运行使能，可喂设定值 | 调 `FB_SoEDriveMoveVelocity` |
| `bStatus = FALSE`，`bDriveError = FALSE` | 使能过程中 / 未使能 | 保持 `bEnable = TRUE` 等状态机走完 |
| `bDriveError = TRUE` | 驱动器错误态 | 用 `FB_SoEReset_ByDriveRef` 等复位驱动器后重新使能；故障原因看驱动器 Sercos 诊断 |

PDF 与 InfoSys 均未给本 FB 的数值错误码（状态由 `bDriveError` 表达，详细故障号需查驱动器 Sercos 诊断 IDN，⚠️ 待人工对照具体驱动手册）。

## 5. 使用注意 / 常见坑

- **`stSoeDriveIoInterface` 必须正确链接过程映像**：这是 VAR_IN_OUT，本 FB 靠它读写 Sercos 控制 / 状态字。在 System Manager 把 SoE 驱动器过程数据链接到该结构对应字段，漏链 / 链错则 `bStatus` 永远上不来。（PDF）
- **本 FB 没有 `bReset`**：和 CoE 版不同。SoE 驱动器故障要用别的方式复位（如 `FB_SoEReset_ByDriveRef` 复位 `S-0-0099`），别指望本 FB 清错。（PDF 接口对比）
- **电平型 `bEnable`**：持续保持才维持使能，置 `FALSE` 立即去使能。
- **先使能再运动**：`bStatus = TRUE` 之前不要调 `FB_SoEDriveMoveVelocity`，否则设定值进不去。（PDF：MoveVelocity 要求先经本 FB 使能）
- **必须每周期调用**：状态机靠周期调用推进，漏调会卡中间状态。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEDriveEnable.xml`](../examples/P_Demo_FB_SoEDriveEnable.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_SoEDriveEnable
VAR
    fbDriveEnable   : FB_SoEDriveEnable;
    stSoEDriveIo    : ST_SoEDriveIoInterface;      // 在 System Manager 链接 SoE 驱动器过程数据
    bEnableDrive    : BOOL := FALSE;               // 在线置 TRUE 推动使能状态机（电平型）
    bDriveReady     : BOOL;                        // 在线 monitor：到达运行使能为 TRUE
    bDriveFault     : BOOL;                        // 驱动器错误态
END_VAR

// 单次调用形式：VAR_IN_OUT stSoeDriveIoInterface 必传；每周期调用推进状态机
// 注意：本 SoE 版没有 bReset 输入，故障复位需另用 FB_SoEReset_ByDriveRef
fbDriveEnable(
    bEnable := bEnableDrive,
    stSoeDriveIoInterface := stSoEDriveIo,
    bStatus     => bDriveReady,
    bDriveError => bDriveFault
);
```

## 7. 业务场景与实际价值

- **场景**：用 SoE 伺服（如 AX5000）做简单速度控制，不想引入完整 NC 配置，希望直接由 PLC 程序使能并喂速度（输送带、风机、卷绕等纯调速场合）。
- **价值**：把 Sercos 驱动器使能状态机的逐步控制字操作封装成一个 `bEnable` 布尔，业务侧不必手写 Sercos 状态字解析和控制字时序。
- **替代方案对比**：
  - NC 轴 + `MC_Power`：功能全但要配 NC 任务、轴对象，配置重
  - 自己解析 Sercos drive status word / 写 control word：要手写完整状态机
  - **本 FB**：一个 `bEnable` 搞定使能，配 `FB_SoEDriveMoveVelocity` 即可纯 PLC 调速，适合无需插补的简单运动

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf) §4.5.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/10731920907.html
- **相关**：`FB_SoEDriveMoveVelocity`（配套，使能后喂速度）、`FB_CoEDriveEnable`（CoE 版同类，带 `bReset`）、`FB_SoEReset_ByDriveRef`（SoE 故障复位）、`ST_SoEDriveIoInterface`（过程映像结构）

## 9. 待确认项

- ⚠️ `ST_SoEDriveIoInterface` 结构各字段定义见库数据类型章节（PDF），本文未逐字段罗列。
- ⚠️ 驱动器具体故障号需读 Sercos 诊断 IDN（如 S-0-0095 / C1D），PDF/InfoSys 未列。
