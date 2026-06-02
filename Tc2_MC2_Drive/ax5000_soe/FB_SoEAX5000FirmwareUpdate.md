# FB_SoEAX5000FirmwareUpdate

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `AX5000 SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2306313867.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEAX5000FirmwareUpdate.TcPOU`](../examples/P_Demo_FB_SoEAX5000FirmwareUpdate.TcPOU) |

---

## 1. 功能简述

检查并自动更新 **AX5000** 固件的功能块（Function Block, FB）。它能把 AX5000 固件检查并自动改到给定版本（Revision 和 Build），或改到所配置 Revision 的当前 Build。

更新流程（PDF 列出）：① 确定配置的从站型号（如 `AX5103-0000-0010`）→ ② 用预设从站地址确定当前从站（如 `AX5103-0000-0009`）→ ③ 确定当前从站固件（如 `v1.05_b0009`）→ ④ 比对配置与实测从站的通道数、电流、Revision、固件 → ⑤ 确定所需固件文件名并搜索 → ⑥ 执行更新（如需要）→ ⑦ 重新确定从站 → ⑧ 把从站切到预设 EtherCAT 状态。

更新成功以 `eFwUpdateState = eFwU_FwUpdateDone` 结束；若无需更新则 `eFwUpdateState = eFwU_NoFwUpdateRequired`。更新经指定通道（A=0 或 B=1）进行；双通道设备只能用其中一个通道，另一通道会报 `eFwU_UpdateViaOtherChannelActive` 或 `eFwU_UpdateViaOtherChannel`。更新进行中（`eFwU_FwUpdateInProgress`），`iLoadProgress` 给出百分比进度。

⚠️ **NOTICE（来自 PDF）**：更新期间任何中断都可能导致更新失败或不正确，之后端子可能在没有正确固件时无法使用。更新期间规则：PLC 与 TwinCAT 不能停、EtherCAT 连接不能断、AX5000 不能断电。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId           : T_AmsNetID;
    bExecute         : BOOL;    
    sFirmwareVersion : STRING(20);
    sFirmwarePath    : T_MaxString;
    iReqEcState      : UINT := EC_DEVICE_STATE_OP;
    tTimeout         : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetID` | — | 控制器（IPC）的 AMS NetId |
| `bExecute` | `BOOL` | — | 上升沿触发一次固件更新 |
| `sFirmwareVersion` | `STRING(20)` | — | 版本字符串 `vx.yy_bnnnn`，如 `"v1.05_b0009"` 表示 v1.05 Build 0009 |
| `sFirmwarePath` | `T_MaxString` | — | 固件池路径 `drive:\path`，如 `"C:\TwinCAT\Io\TcDriveManager\FirmwarePool"` |
| `iReqEcState` | `UINT` | `EC_DEVICE_STATE_OP` | 更新后要求从站进入的 EtherCAT 状态 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | FB 执行允许的最大时间 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | 唯一标识系统中一根轴的数据结构，含位置、速度、错误状态等循环数据。**必须传引用**（VAR_IN_OUT 语义） |

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
    sSelectedFirmwareFile : STRING(MAX_STRING_LENGTH);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 激活后置位，直到收到反馈才复位 |
| `bError` | `BOOL` | `bBusy` 复位后若命令传输出错则置位 |
| `iAdsErrId` | `UINT` | `bError = TRUE` 时返回最后一条命令的 ADS 错误码 |
| `iSercosErrId` | `UINT` | `bError = TRUE` 时返回最后一条命令的 Sercos 错误码 |
| `iDiagNumber` | `UDINT` | `bError = TRUE` 时返回最后一次固件更新的驱动器错误 |
| `eFwUpdateState` | `E_FwUpdateState` | 返回固件更新状态（`eFwU_FwUpdateDone` 完成 / `eFwU_NoFwUpdateRequired` 无需更新 / `eFwU_FwUpdateInProgress` 进行中 / `eFwU_UpdateViaOtherChannelActive` / `eFwU_UpdateViaOtherChannel` 等） |
| `iLoadProgress` | `INT` | 返回当前固件更新进度（百分比） |
| `sSelectedFirmwareFile` | `STRING(MAX_STRING_LENGTH)` | 显示搜索/选中的固件文件名，如 `"AX5yxx_xxxx_-0010_v1_05_b0009.efw"` |

## 3. 行为说明

**触发**：`bExecute` 上升沿启动一次固件更新流程（含上节 8 步），`bBusy := TRUE`，**整个过程跨非常多个 PLC 周期**（固件更新本身可能数十秒至数分钟），必须每周期循环调用直到 `bBusy` 落回 `FALSE`。

**状态机（核心看 `eFwUpdateState`）**：本 FB 没有 `bDone`，进展全靠 `eFwUpdateState` 与 `iLoadProgress` 体现：
- `eFwU_NoFwUpdateRequired`：当前固件已是目标版本，无需更新（成功结束的一种）
- `eFwU_FwUpdateInProgress`：更新进行中，`iLoadProgress` 给百分比进度
- `eFwU_FwUpdateDone`：更新成功完成
- `eFwU_UpdateViaOtherChannelActive` / `eFwU_UpdateViaOtherChannel`：双通道设备的另一通道正在/应通过另一通道更新

**完成与出错收敛**：成功判据是 `bBusy` 落回 FALSE 且 `bError = FALSE` 且 `eFwUpdateState ∈ {eFwU_FwUpdateDone, eFwU_NoFwUpdateRequired}`。出错则 `bError := TRUE`，`iAdsErrId`/`iSercosErrId`/`iDiagNumber` 三路给出错误信息（`iDiagNumber` 是固件更新特有的驱动器诊断号）。

**双通道约束**：双通道 AX5000 只能从一个通道（A=0/B=1）发起更新，另一通道会报 `eFwU_UpdateViaOtherChannel...`。

**绝对不能中断**：⚠️ 更新期间 PLC/TwinCAT 不能停、EtherCAT 不能断、AX5000 不能断电——中断会损坏固件使端子不可用。因此更新必须在受控停机窗口做，不能在生产中随意触发。

## 4. 错误码 / 返回值

错误通过 `bError = TRUE` 输出，分三路：`iAdsErrId : UINT`（ADS 错误码）、`iSercosErrId : UINT`（Sercos 错误码）、`iDiagNumber : UDINT`（固件更新驱动器诊断号）。

| 输出 | 含义 | 处理建议 |
|---|---|---|
| `iAdsErrId` ≠ 0 | ADS 通道错误：超时、设备不可达 | 检查 EtherCAT OP、`sNetId`、`tTimeout` |
| `iSercosErrId` ≠ 0 | Sercos 服务错误 | 见 AX5000 Sercos 文档 |
| `iDiagNumber` ≠ 0 | 固件更新过程中的驱动器诊断号 | 查 AX5000 诊断号说明；确认固件文件存在于 `sFirmwarePath` 且版本字符串格式正确 |

⚠️ PDF 与 InfoSys 未逐条列出具体错误码 / `iDiagNumber` 数值含义。见 Beckhoff ADS Return Codes 总表与 AX5000 文档。

**清错**：固件更新失败可能导致端子不可用，需按 AX5000 手册的恢复流程处理，不是简单重发 `bExecute` 就能解决。

## 5. 使用注意 / 常见坑

- **更新期间绝不能中断**：PLC/TwinCAT/EtherCAT/供电任何一个中断都可能损坏固件——这是最致命的坑，必须在受控停机窗口操作。
- **没有 `bDone`，看 `eFwUpdateState`**：判完成靠 `eFwU_FwUpdateDone` 或 `eFwU_NoFwUpdateRequired`，进度看 `iLoadProgress`。
- **版本字符串格式严格**：`sFirmwareVersion` 必须是 `vx.yy_bnnnn` 格式（如 `v1.05_b0009`），格式错会找不到固件文件。
- **固件文件须在 `sFirmwarePath` 下**：默认池路径 `C:\TwinCAT\Io\TcDriveManager\FirmwarePool`，文件缺失会失败。
- **双通道设备只能从一个通道更新**：另一通道报 `eFwU_UpdateViaOtherChannel...`。
- **输出/输入用 `b`/`i`/`s` 前缀**：本 FB 命名风格与库内其它 FB 不同（`bBusy`/`bError`/`iAdsErrId` 等），写代码注意 pin 名。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEAX5000FirmwareUpdate.TcPOU`](../examples/P_Demo_FB_SoEAX5000FirmwareUpdate.TcPOU)

```iecst
// 场景：受控停机窗口里把 AX5000 固件更新到指定版本
rtFwTrig(CLK := bStartFwUpdate);
fbFwUpdate(
    sNetId           := '',
    bExecute         := rtFwTrig.Q,
    sFirmwareVersion := 'v1.05_b0009',
    sFirmwarePath    := 'C:\TwinCAT\Io\TcDriveManager\FirmwarePool',
    tTimeout         := DEFAULT_ADS_TIMEOUT,
    Axis             := axisServo,
    bBusy            => bFwBusy,
    bError           => bFwError,
    eFwUpdateState   => eFwState,
    iLoadProgress    => iFwProgress
);
```

## 7. 业务场景与实际价值

- **场景**：批量设备固件统一升级、新机调试时把驱动器刷到工程要求的固件版本、售后远程升级 AX5000 固件。
- **价值**：把"检查固件→比对版本→找文件→刷写→恢复状态"整套流程封装成一个 FB，免去人工进 DriveManager 逐台操作，可纳入自动化升级脚本。
- **替代方案对比**：
  - 在 DriveManager 手动逐台刷固件：人工、慢、易漏
  - **本 FB**：程序化批量固件更新的标准入口（但必须在受控窗口、绝不中断）

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.4.3，枚举 `E_FwUpdateState`
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2306313867.html
- **相关 FB**：`FB_SoERead`（读 AX5000 当前固件版本等参数）
