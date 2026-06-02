# FB_SoEAX5000FirmwareUpdate

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_NcDrive` |
| Library Version | `1.2.9` |
| Type | `FUNCTION_BLOCK` |
| Category | `AX5000 SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ncdrive/2305442443.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEAX5000FirmwareUpdate.TcPOU`](../examples/P_Demo_FB_SoEAX5000FirmwareUpdate.TcPOU) |

---

## 1. 功能简述

检查并在需要时自动更新 AX5000 驱动器**固件（Firmware）**的功能块（Function Block, FB）。`bExecute` 上升沿触发后，FB 会自动完成：识别配置的从站型号、读取在线从站当前固件、比对通道数/电流/版本/Build、查找匹配的固件文件、必要时执行更新、更新后把从站切回指定的 EtherCAT 状态。

更新成功以 `eFwUpdateState = eFwU_FwUpdateDone` 结束；若本就不需要更新则返回 `eFwU_NoFwUpdateRequired`。更新过程中 `iLoadProgress` 以百分比给出进度。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId           : T_AmsNetId;
    bExecute         : BOOL;
    sFirmwareVersion : STRING(20);
    sFirmwarePath    : T_MaxString;
    iReqEcState      : UINT := EC_DEVICE_STATE_OP;
    tTimeout         : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | 控制器（IPC）的 AMS-NetID |
| `bExecute` | `BOOL` | — | 上升沿激活一次固件更新流程 |
| `sFirmwareVersion` | `STRING(20)` | — | 期望固件版本，形如 `vx.yy_bnnnn`（例 `"v1.05_b0009"` = 版本 v1.05 Build 0009）；可用通配指定"某版本最新 Build / 某主版本最新 / 最新版本"，空串 `" "` 表示最新版本最新 Build |
| `sFirmwarePath` | `T_MaxString` | — | 固件池路径（固件文件所在目录），例 `C:\TwinCAT\Io\TcDriveManager\FirmwarePool` |
| `iReqEcState` | `UINT` | `EC_DEVICE_STATE_OP` | 更新后期望的 EtherCAT 状态（仅在实际执行了更新时生效）；状态常量定义在 PLC Lib Tc2_EtherCAT 全局常量中 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 这里指定的是单个内部 ADS 实例的超时（大型 EtherCAT 网络的整体更新可能耗时更长） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : NCTOPLC_AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `NCTOPLC_AXIS_REF` | NC 轴数据结构（映射在 `%I*` 输入过程映像）；本 FB 据此定位目标 AX5000 及其通道（A=0 / B=1） |

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
| `bBusy` | `BOOL` | 命令激活后置 `TRUE`，直到收到反馈才复位 |
| `bError` | `BOOL` | 在 `bBusy` 复位之后，若命令传输发生错误则置 `TRUE` |
| `iAdsErrId` | `UINT` | `bError = TRUE` 时返回上一条命令的 ADS 错误码 |
| `iSercosErrId` | `UINT` | `bError = TRUE` 时返回上一条命令的 Sercos 错误码 |
| `iDiagNumber` | `UDINT` | `bError = TRUE` 时返回上一次固件更新的驱动器错误号（drive error） |
| `eFwUpdateState` | `E_FwUpdateState` | 返回固件更新的状态（见 §3 / §4 状态枚举） |
| `iLoadProgress` | `INT` | 返回实际固件更新进度，百分比 |
| `sSelectedFirmwareFile` | `STRING(MAX_STRING_LENGTH)` | 显示正在查找/选用的固件文件名（例 `"AX5yxx_xxxx_-0010_v1_05_b0009.efw"`） |

## 3. 行为说明

**完整流程**：`bExecute` 上升沿后，`bBusy` 置 `TRUE`，FB 依次执行：(1) 确定配置的从站型号（如 AX5103-0000-0010）；(2) 用预定义从站地址确定当前在线从站（如 AX5103-0000-0009）；(3) 读当前从站固件（如 v1.05_b0009）；(4) 比对配置与在线从站的通道数、电流、版本、固件；(5) 推算需要的固件文件名并在 `sFirmwarePath` 池中查找；(6) 若需要则执行更新；(7) 重新确定在线从站；(8) 把从站切到 `iReqEcState` 指定的 EtherCAT 状态。

**状态机（`eFwUpdateState`）**：更新进行中为 `eFwU_FwUpdateInProgress`，此时 `iLoadProgress` 给出百分比进度；成功结束为 `eFwU_FwUpdateDone`；本就不需更新为 `eFwU_NoFwUpdateRequired`。双通道设备只能用一个通道执行更新，另一通道会报告 `eFwU_UpdateViaOtherChannelActive` 或 `eFwU_UpdateViaOtherChannel`。

**版本字符串语义**：`sFirmwareVersion` 支持精确指定与通配，例如 `"v1.05_b0009"` 指定具体 Build，`"v1.05_b00??"` 取该版本最新 Build，`"v1.??_b00??"` 取该主版本最新，`"v?.??_b00??"` 或 `" "` 取最新版本的最新 Build；客户专用 Build 用不同的中间两位区分。

**更新中断的风险（NOTICE）**：更新期间发生中断可能导致更新未执行或执行不完整，之后端子可能在没有正确固件的情况下无法使用。更新期间的规则是：PLC 与 TwinCAT 不得停止；EtherCAT 连接不得中断；AX5000 不得断电。

## 4. 错误码 / 返回值

本 FB 无函数返回值。错误通过 `bError = TRUE` 配合错误码输出表达，状态通过 `eFwUpdateState : E_FwUpdateState` 反映：

| 输出 | 类型 | 含义 |
|---|---|---|
| `iAdsErrId` | `UINT` | ADS 传输层错误码 |
| `iSercosErrId` | `UINT` | Sercos / SoE 协议层错误码 |
| `iDiagNumber` | `UDINT` | 上一次固件更新的驱动器错误号（drive error） |
| `eFwUpdateState` | `E_FwUpdateState` | 更新状态枚举，PDF 列出的取值含义见下 |

`E_FwUpdateState` 在 PDF 行为描述中出现的取值：

| 枚举值 | 含义 |
|---|---|
| `eFwU_FwUpdateInProgress` | 更新进行中（此时 `iLoadProgress` 有效） |
| `eFwU_FwUpdateDone` | 更新成功完成 |
| `eFwU_NoFwUpdateRequired` | 无需更新 |
| `eFwU_UpdateViaOtherChannelActive` | 双通道设备：更新正通过另一通道进行 |
| `eFwU_UpdateViaOtherChannel` | 双通道设备：更新通过另一通道完成 |

⚠️ PDF 未给出 `E_FwUpdateState` 的完整枚举清单与每个 `iDiagNumber` / ADS / Sercos 错误码的逐条数值含义；以上为 PDF 正文明确提到的取值。完整枚举与错误码以 AX5000 固件/驱动手册为准。

## 5. 使用注意 / 常见坑

- **更新期间绝不能断电/断网/停 TwinCAT**：否则可能刷成砖（NOTICE 明确警告），更新过程务必有不间断供电与稳定网络。
- **`tTimeout` 只是单个内部 ADS 实例的超时**：大型网络整体更新更久，别因为这个值小就以为整个更新该这么快。
- **双通道设备只能用一个通道更新**：另一通道会报 `eFwU_UpdateViaOtherChannel*`，这是正常提示不是错误。
- **版本通配要看懂**：`??` 是通配位，`b` 后中间两位区分 Release / 客户专用 Build，写错会选到非预期固件。
- **`iReqEcState` 仅在真执行更新时生效**：若 `eFwU_NoFwUpdateRequired`，不会强制切状态。
- **`Axis` 是 VAR_IN_OUT 必须传引用**：传入映射在 `%I*` 上的 `NCTOPLC_AXIS_REF` 实例。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEAX5000FirmwareUpdate.TcPOU`](../examples/P_Demo_FB_SoEAX5000FirmwareUpdate.TcPOU)

```iecst
// 场景：产线批量上线前统一把 AX5000 固件刷到指定版本，避免不同站固件不一致引发的偶发问题
PROGRAM P_Demo_FB_SoEAX5000FirmwareUpdate
VAR
    fbFwUpdate        : FB_SoEAX5000FirmwareUpdate;
    NcToPlcAxis AT %I*: NCTOPLC_AXIS_REF;
    bStartUpdate      : BOOL;                  // HMI 触发固件检查/更新
    rtStart           : R_TRIG;
    sTargetVersion    : STRING(20) := 'v1.05_b0009';
    sFwPool           : T_MaxString := 'C:\TwinCAT\Io\TcDriveManager\FirmwarePool';
    eState            : E_FwUpdateState;       // 监视更新状态机
    iProgress         : INT;                   // 监视更新进度百分比
    sSelectedFile     : STRING(MAX_STRING_LENGTH);
    bBusy             : BOOL;
    bError            : BOOL;
    iAdsErr           : UINT;
    iSercosErr        : UINT;
    iDiag             : UDINT;
END_VAR

rtStart(CLK := bStartUpdate);
fbFwUpdate(
    Axis             := NcToPlcAxis,
    sNetId           := '',
    bExecute         := rtStart.Q,
    sFirmwareVersion := sTargetVersion,
    sFirmwarePath    := sFwPool,
    iReqEcState      := EC_DEVICE_STATE_OP,
    tTimeout         := T#15S,
    bBusy                 => bBusy,
    bError                => bError,
    iAdsErrId             => iAdsErr,
    iSercosErrId          => iSercosErr,
    iDiagNumber           => iDiag,
    eFwUpdateState        => eState,
    iLoadProgress         => iProgress,
    sSelectedFirmwareFile => sSelectedFile
);
IF NOT bBusy THEN
    bStartUpdate := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：产线批量上线统一固件、售后远程升级驱动器、解决因固件版本不一致引发的偶发故障。
- **价值**：不用本 FB 时需手动用 TcDriveManager 逐台点更新，无法用 PLC 程序批量自动化；本 FB 把"识别→比对→选文件→更新→切状态"整套流程封装成一个 `bExecute` 边沿并带进度/状态反馈，可做无人值守批量升级。
- **替代方案对比**：
  - 手动 TcDriveManager：交互式，不适合批量/无人化
  - **本 FB**：可编程的 AX5000 固件自动更新，配合 `ARRAY OF FB_SoEAX5000FirmwareUpdate` 可并行刷多台

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf) §3.3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ncdrive/2305442443.html
- **相关 FB**：`FB_SoEReset`（更新后清错复位）、Tc2_EtherCAT 的 `EC_DEVICE_STATE_*` 常量
