# FB_SoEAX5000FirmwareUpdate_ByDriveRef

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Drive` |
| Library Version | `1.4.8` |
| Type | `FUNCTION_BLOCK` |
| Category | `AX5000 SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/2307575435.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEAX5000FirmwareUpdate_ByDriveRef.TcPOU`](../examples/P_Demo_FB_SoEAX5000FirmwareUpdate_ByDriveRef.TcPOU) |

---

## 1. 功能简述

检查并自动更新 AX5000 固件（Firmware）的功能块。本 FB 能把指定通道的 AX5000 固件检查并自动升级到指定版本（Revision + Build），或升级到当前配置 Revision 的最新 Build。

更新流程内部自动完成：确定配置中的从站型号（如 AX5103-0000-0010）、确定实际从站（如 AX5103-0000-0009）、读出当前从站固件（如 v1.05_b0009）、对照配置与实际从站的通道数 / 电流 / Revision / 固件、确定所需固件文件名并搜索文件、执行固件更新（如有必要）、再次确定实际从站、把从站切到预定义的 EtherCAT 状态。更新成功以 `eFwUpdateState = eFwU_FwUpdateDone` 结束；若无需更新则以 `eFwUpdateState = eFwU_NoFwUpdateRequired` 标示。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
   stDriveRef       : ST_DriveRef;
   bExecute         : BOOL;
   tTimeout         : TIME := DEFAULT_ADS_TIMEOUT;
   sFirmwareVersion : STRING(20);  (* version string vx_yy_bnnnn, e.g. "v1.05_b0009" for v1.05 Build 0009*)
   sFirmwarePath    : T_MaxString; (* drive:\path, e.g. "C:\TwinCAT\Io\TcDriveManager\FirmwarePool" *)
   sNetIdIPC        : T_AmsNetId;
   iReqEcState      : UINT := EC_DEVICE_STATE_OP;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stDriveRef` | `ST_DriveRef` | — | 驱动器引用结构。固件经由 `stDriveRef` 指定的通道（A = 0 / B = 1）更新。双通道设备只能用其中一个通道触发，另一通道会报 `eFwU_UpdateViaOtherChannelActive` / `eFwU_UpdateViaOtherChannel` |
| `bExecute` | `BOOL` | — | 上升沿激活本 FB 执行一次固件检查 / 更新；调用期间保持，完成后手动复位 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 命令执行允许的最长时间。固件更新耗时长，例程里用更大值（如 `T#15s`） |
| `sFirmwareVersion` | `STRING(20)` | — | 目标固件版本，形如 `vx.yy_bnnnn`，如 `"v1.05_b0009"` 表示 v1.05 Build 0009。支持通配：`"v1.05_b00??"` = 指定版本最新 build，`"v1.??_b00??"` = 指定主版本最新，`" "`（空）= 最新版本最新 build。Build 段前两位区分发布/客户/调试构建（00=Release，10/89=客户专属，90=Debug） |
| `sFirmwarePath` | `T_MaxString` | — | 固件池路径，固件文件所在目录，如 `C:\TwinCAT\Io\TcDriveManager\FirmwarePool` |
| `sNetIdIPC` | `T_AmsNetId` | — | 控制器（IPC）的 AMS NetID（本机用空串 `''`） |
| `iReqEcState` | `UINT` | `EC_DEVICE_STATE_OP` | 更新后期望的 EtherCAT 状态（仅在确实执行了更新时生效）。各状态在 PLC Lib `Tc2_EtherCAT` 中定义为全局常量 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
   bBusy                 : BOOL;
   bError                : BOOL;
   iAdsErrId             : UINT;
   iSercosErrId          : UINT;
   iDiagNumber           : UDINT;
   eFwUpdateState        : E_FwUpdateState;
   iLoadProgress         : INT;
   sSelectedFirmwareFile : STRING(MAX_STRING_LENGTH); (* found firmware file, e.g. "AX5yxx_xxxx_0010_v1_05_b0009.efw" *)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 被激活时置位，直到收到反馈才复位 |
| `bError` | `BOOL` | 在 `bBusy` 复位之后，若出错则置位 |
| `iAdsErrId` | `UINT` | `bError` 置位时返回上一条命令的 ADS 错误码 |
| `iSercosErrId` | `UINT` | `bError` 置位时返回上一条命令的 Sercos 错误码 |
| `iDiagNumber` | `UDINT` | `bError` 置位时返回上一次固件更新的驱动器（放大器）错误码 |
| `eFwUpdateState` | `E_FwUpdateState` | 返回固件更新的状态（见枚举 `E_FwUpdateState`），如 `eFwU_FwUpdateInProgress` / `eFwU_FwUpdateDone` / `eFwU_NoFwUpdateRequired` |
| `iLoadProgress` | `INT` | 当前固件更新的进度百分比（`eFwUpdateState = eFwU_FwUpdateInProgress` 时有意义） |
| `sSelectedFirmwareFile` | `STRING(MAX_STRING_LENGTH)` | 搜索到的固件文件名，如 `"AX5yxx_xxxx_0010_v1_05_b0009.efw"` |

### VAR_IN_OUT

无。

## 3. 行为说明

本 FB 是 `bExecute` 上升沿驱动的长流程异步功能块，通过 `eFwUpdateState` 暴露多阶段状态：

1. **触发**：`bExecute` 上升沿启动整个固件检查 / 更新流程，置 `bBusy := TRUE`。
2. **检查阶段**：FB 自动读配置型号、实际型号、当前固件，对照通道数 / 电流 / Revision / 固件是否匹配，按 `sFirmwareVersion` 推算目标固件文件名，在 `sFirmwarePath` 里搜索文件（结果回填 `sSelectedFirmwareFile`）。
3. **更新阶段**：若需要更新，进入 `eFwUpdateState = eFwU_FwUpdateInProgress`，`iLoadProgress` 给出 0–100 的进度百分比。
4. **完成分支**：更新成功 → `eFwU_FwUpdateDone`；本来就是目标版本无需更新 → `eFwU_NoFwUpdateRequired`；出错 → `bError := TRUE`，`iDiagNumber` 给出放大器错误码。
5. **双通道分支**：若另一通道正在做更新，本通道返回 `eFwU_UpdateViaOtherChannelActive` / `eFwU_UpdateViaOtherChannel`（双通道设备一次只能从一个通道更新）。

**通配符语义**：`sFirmwareVersion` 用 `?` 通配 build/version，让 FB 自动选最新匹配；空串选全局最新。Build 段编码区分发布 / 客户专属 / 调试构建，误填会选到不期望的构建类型。

**版本号字符串中的 `_b` 段示例**：`"v1.05_b0009"` 是精确指定；`"v1.05_b00??"` 是该版本下最新发布 build。

**调用范式**：`bExecute` 上升沿后必须持续每周期调用本 FB 以推进流程并刷新 `eFwUpdateState` / `iLoadProgress`；`bBusy` 落下后补一次 `bExecute := FALSE` 收尾。

> **⚠️ NOTICE（PDF 警告）：更新中断会导致更新失败**。更新被打断可能导致更新未执行或执行错误，之后驱动器在没有正确固件的情况下可能不再可用。更新期间的规则：① PLC 和 TwinCAT 不能停止；② EtherCAT 连接不能中断；③ AX5000 不能断电。

## 4. 错误码 / 返回值

| 输出 | 含义 | 处理建议 |
|---|---|---|
| `eFwUpdateState = eFwU_FwUpdateDone` | 更新成功完成 | 流程结束 |
| `eFwUpdateState = eFwU_NoFwUpdateRequired` | 已是目标版本，无需更新 | 流程结束 |
| `eFwUpdateState = eFwU_FwUpdateInProgress` | 更新进行中 | 读 `iLoadProgress` 看进度，期间严禁中断 |
| `eFwUpdateState = eFwU_UpdateViaOtherChannelActive` / `eFwU_UpdateViaOtherChannel` | 更新需 / 正经由另一通道进行 | 改用另一通道触发 |
| `bError = TRUE` | 更新出错 | 读 `iDiagNumber`（放大器错误）、`iAdsErrId` / `iSercosErrId` |

`E_FwUpdateState` 的完整枚举值在库的数据类型章节（PDF §「Data types」E_FwUpdateState）定义。`iDiagNumber`（放大器错误）、`iAdsErrId`、`iSercosErrId` 的具体码表 PDF/InfoSys 未逐条列出（⚠️ 待人工对照 AX5000 诊断手册）。

## 5. 使用注意 / 常见坑

- **更新期间绝对不能中断**（PDF NOTICE）：不能停 PLC / TwinCAT、不能断 EtherCAT、不能给 AX5000 断电。中断可能让驱动器固件损坏到不可用。生产中应锁定该时段、提示操作员勿断电。
- **`tTimeout` 要给大**：固件更新比普通 SoE 命令耗时长得多，用 `DEFAULT_ADS_TIMEOUT`（约 5 秒）会超时。PDF 示例用 `T#15s`，实际按固件大小留足。（PDF 示例）
- **双通道设备一次只能从一个通道更新**：另一通道会返回 `eFwU_UpdateViaOtherChannel*`，不要两个通道同时触发。
- **`sFirmwarePath` 要指向有效固件池**：默认 `C:\TwinCAT\Io\TcDriveManager\FirmwarePool`，文件不在该目录会找不到（看 `sSelectedFirmwareFile` 是否被填上确认匹配到文件）。
- **`sFirmwareVersion` 通配要小心 build 类型段**：Release（00）/客户（10、89）/Debug（90）构建混在一起时，通配可能选到非预期类型。要精确版本就写全 `vx.yy_bnnnn`。
- **`iReqEcState` 用 Tc2_EtherCAT 常量**：如 `EC_DEVICE_STATE_OP`，需引用 `Tc2_EtherCAT` 库。
- **`stDriveRef` 必须先初始化好**：例程用 `bInit` 守卫。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEAX5000FirmwareUpdate_ByDriveRef.TcPOU`](../examples/P_Demo_FB_SoEAX5000FirmwareUpdate_ByDriveRef.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_SoEAX5000FirmwareUpdate_ByDriveRef
VAR
    fbFwUpdate      : FB_SoEAX5000FirmwareUpdate_ByDriveRef;
    rtrigUpdate     : R_TRIG;
    stPlcDriveRef   AT %I* : ST_PlcDriveRef;
    stDriveRef      : ST_DriveRef;
    bInit           : BOOL := TRUE;
    bUpdateReq      : BOOL := FALSE;               // 在线置 TRUE 触发一次固件检查/更新
    sTargetFwVer    : STRING(20) := 'v1.05_b0009'; // 目标固件版本
    sFwPath         : T_MaxString := 'C:\TwinCAT\Io\TcDriveManager\FirmwarePool';
    sIpcNetId       : T_AmsNetId := '';            // 本机控制器
    bUpdBusy        : BOOL;
    bUpdError       : BOOL;
    iAdsErr         : UINT;
    iSercosErr      : UINT;
    iDiagNo         : UDINT;
    eFwState        : E_FwUpdateState;             // 在线 monitor 更新状态
    iProgress       : INT;                         // 更新进度百分比
    sFwFile         : STRING(MAX_STRING_LENGTH);   // 匹配到的固件文件名
END_VAR

// 初始化驱动器引用（nDriveNo 决定从哪个通道触发更新）
IF bInit THEN
    stDriveRef.sNetId     := F_CreateAmsNetId(stPlcDriveRef.aNetId);
    stDriveRef.nSlaveAddr := stPlcDriveRef.nSlaveAddr;
    stDriveRef.nDriveNo   := stPlcDriveRef.nDriveNo;
    stDriveRef.nDriveType := stPlcDriveRef.nDriveType;
    IF (stDriveRef.sNetId <> '') AND (stDriveRef.nSlaveAddr <> 0) THEN
        bInit := FALSE;
    END_IF;
END_IF;

rtrigUpdate(CLK := bUpdateReq);

// 单次调用形式：所有 VAR_INPUT 显式赋值；tTimeout 给足 15 秒（固件更新耗时长）
fbFwUpdate(
    stDriveRef       := stDriveRef,
    bExecute         := rtrigUpdate.Q AND NOT bInit,
    tTimeout         := T#15S,
    sFirmwareVersion := sTargetFwVer,
    sFirmwarePath    := sFwPath,
    sNetIdIPC        := sIpcNetId,
    iReqEcState      := EC_DEVICE_STATE_OP,
    bBusy                 => bUpdBusy,
    bError                => bUpdError,
    iAdsErrId             => iAdsErr,
    iSercosErrId          => iSercosErr,
    iDiagNumber           => iDiagNo,
    eFwUpdateState        => eFwState,
    iLoadProgress         => iProgress,
    sSelectedFirmwareFile => sFwFile
);

IF NOT bUpdBusy AND NOT bInit THEN
    bUpdateReq := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：批量设备出厂前 / 现场升级时，需要把一批 AX5000 的固件统一刷到指定版本，做成 PLC 自动流程（开机检查版本，不对就自动升级），避免逐台用 Drive Manager 手动刷。
- **价值**：把"读型号 + 比对版本 + 找固件文件 + 刷写 + 切 EtherCAT 状态"这一整套多步流程封装成一个上升沿调用，并通过 `eFwUpdateState` + `iLoadProgress` 暴露进度，业务侧可在 HMI 显示升级进度条。
- **替代方案对比**：
  - 用 TwinCAT Drive Manager 手动刷：逐台人工，批量场景效率低
  - 自己用 ADS 写固件文件流：极复杂，要处理文件搜索、版本比对、刷写协议
  - **本 FB**：一次调用走完整流程，自带版本通配、进度反馈、双通道保护，适合自动化产线 / 现场批量升级

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf) §4.2.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/2307575435.html
- **相关**：`E_FwUpdateState`（状态枚举，同库数据类型）；`Tc2_EtherCAT` 库的 `EC_DEVICE_STATE_OP` 等 EtherCAT 状态常量；同 AX5000 SoE 类的其它 FB

## 9. 待确认项

- ⚠️ `E_FwUpdateState` 完整枚举值表见库数据类型章节，本文未逐条罗列。
- ⚠️ `iDiagNumber`（放大器错误）/ `iAdsErrId` / `iSercosErrId` 具体码表 PDF/InfoSys 未列，需对照 AX5000 诊断手册。
