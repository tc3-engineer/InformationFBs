# Tc2_MC2_Drive

> Beckhoff TwinCAT 3 PLC 库 **Tc2_MC2_Drive** 的中文技术文档与可导入演示程序。
> 库版本：`1.14.2`（取自 PDF 头部 Version）。

本库是 `Tc2_MC2` 之上的**驱动器专用层**：在 PLCopen 运动控制（`Tc2_MC2`）之外，提供针对 Beckhoff 伺服硬件（AX5000 / AX8000 / AMP8xxx / MD8xxx / EL72xx / 紧凑型驱动）的底层访问能力——SoE / CoE 参数读写、抱闸控制、位置偏置、通道驻留、驱动器信息读取、固件更新等。所有 FB 通过 `AXIS_REF` 关联到一根 NC 轴。

## 接口约定（库内通用）

- 多数 FB 用 **Beckhoff 异步风格**：`Execute` 边沿触发 → `Busy` 高电平期间跨多周期执行 → 完成时 `Busy` 落回 `FALSE`。
- **大多数 FB 没有 `Done` 输出**（例外：`FB_ReadDriveInfo` 有 `Done`）；判完成靠 `Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`。
- 错误输出因协议而异：
  - SoE FB → `AdsErrId`（ADS 错误）+ `SercosErrId`（Sercos 错误）双码
  - CoE FB → `AdsErrId` + `CANopenErrId` 双码
  - 通用/型号 FB → `ErrorID`（ADS 错误码，`UDINT`）
- `Axis : AXIS_REF` 为 **VAR_IN_OUT**，调用时必须传引用。
- `ErrorID` 是 **ADS 错误码**，不是 NC 错误号；具体数值见 Beckhoff ADS Return Codes 总表（PDF 未逐条列）。

## 条目索引（29）

### Functions（§3）
| 条目 | 类型 | 说明 | 文档 |
|---|---|---|---|
| F_GetVersionTcMc2Drive | FC | 读库版本号（major/minor/revision） | [functions/F_GetVersionTcMc2Drive.md](functions/F_GetVersionTcMc2Drive.md) |

### General Beckhoff（§4.1，硬件无关）
| 条目 | 类型 | 说明 | 文档 |
|---|---|---|---|
| FB_DeletePositionOffset | FB | 删除位置偏置（自动选 SoE/CoE） | [general_beckhoff/FB_DeletePositionOffset.md](general_beckhoff/FB_DeletePositionOffset.md) |
| FB_BrakeControl | FB | 手动抱闸控制（Automatic/Lock/Unlock） | [general_beckhoff/FB_BrakeControl.md](general_beckhoff/FB_BrakeControl.md) |
| FB_SetPositionOffset | FB | 写位置偏置（绝对/相对） | [general_beckhoff/FB_SetPositionOffset.md](general_beckhoff/FB_SetPositionOffset.md) |
| FB_ReadDriveInfo | FB | 读驱动器寻址信息（ST_DriveInfo，**有 Done**） | [general_beckhoff/FB_ReadDriveInfo.md](general_beckhoff/FB_ReadDriveInfo.md) |
| FB_ParkAxis | FB | 通道驻留/释放 | [general_beckhoff/FB_ParkAxis.md](general_beckhoff/FB_ParkAxis.md) |

### General SoE（§4.2，Sercos over EtherCAT）
| 条目 | 类型 | 说明 | 文档 |
|---|---|---|---|
| FB_SoERead | FB | 用 IDN+Element 读 SoE 参数 | [general_soe/FB_SoERead.md](general_soe/FB_SoERead.md) |
| FB_SoEWrite | FB | 用 IDN+Element 写 SoE 参数 | [general_soe/FB_SoEWrite.md](general_soe/FB_SoEWrite.md) |
| FB_SoEReset | FB | 驱动器复位（S-0-0099，非 NC 复位） | [general_soe/FB_SoEReset.md](general_soe/FB_SoEReset.md) |
| FB_SoEWritePassword | FB | 写驱动器密码（S-0-0267）解锁参数 | [general_soe/FB_SoEWritePassword.md](general_soe/FB_SoEWritePassword.md) |
| FB_SoESetDataAccessMode | FB | 切并行/顺序 SoE 访问（**无 Axis**） | [general_soe/FB_SoESetDataAccessMode.md](general_soe/FB_SoESetDataAccessMode.md) |

### General CoE（§4.3，CANopen over EtherCAT）
| 条目 | 类型 | 说明 | 文档 |
|---|---|---|---|
| FB_CoERead | FB | 用 Index+SubIndex 读 CoE 对象 | [general_coe/FB_CoERead.md](general_coe/FB_CoERead.md) |
| FB_CoEWrite | FB | 用 Index+SubIndex 写 CoE 对象 | [general_coe/FB_CoEWrite.md](general_coe/FB_CoEWrite.md) |
| FB_CoEExecuteCommand | FB | 执行 CoE 命令型对象（带轮询，`ErrorId`） | [general_coe/FB_CoEExecuteCommand.md](general_coe/FB_CoEExecuteCommand.md) |

### AX5000 SoE（§4.4，AX5000 专用）
| 条目 | 类型 | 说明 | 文档 |
|---|---|---|---|
| FB_SoEAX5000ReadActMainVoltage | FB | 读 AX5000 电网电压峰值（P-0-0200） | [ax5000_soe/FB_SoEAX5000ReadActMainVoltage.md](ax5000_soe/FB_SoEAX5000ReadActMainVoltage.md) |
| FB_SoEAX5000SetMotorCtrlWord | FB | 设 AX5000 抱闸 ForceLock/ForceUnlock（P-0-0096） | [ax5000_soe/FB_SoEAX5000SetMotorCtrlWord.md](ax5000_soe/FB_SoEAX5000SetMotorCtrlWord.md) |
| FB_SoEAX5000FirmwareUpdate | FB | AX5000 固件检查与自动更新（b/i/s 前缀命名） | [ax5000_soe/FB_SoEAX5000FirmwareUpdate.md](ax5000_soe/FB_SoEAX5000FirmwareUpdate.md) |
| FB_SoEAX5000SetPositionOffset | FB | 写 AX5000 位置偏置 | [ax5000_soe/FB_SoEAX5000SetPositionOffset.md](ax5000_soe/FB_SoEAX5000SetPositionOffset.md) |
| FB_SoEAX5000DeletePositionOffset | FB | 删 AX5000 位置偏置 | [ax5000_soe/FB_SoEAX5000DeletePositionOffset.md](ax5000_soe/FB_SoEAX5000DeletePositionOffset.md) |
| FB_SoEAX5000ParkAxis | FB | AX5000 通道驻留/释放 | [ax5000_soe/FB_SoEAX5000ParkAxis.md](ax5000_soe/FB_SoEAX5000ParkAxis.md) |

### AX8000 CoE（§4.5，AX8000 专用）
| 条目 | 类型 | 说明 | 文档 |
|---|---|---|---|
| FB_CoEAX8000BrakeControl | FB | AX8000 手动抱闸控制 | [ax8000_coe/FB_CoEAX8000BrakeControl.md](ax8000_coe/FB_CoEAX8000BrakeControl.md) |
| FB_CoEAX8000BrakeTest | FB | AX8000 功能性抱闸测试（CST 模式，⚠️ DANGER） | [ax8000_coe/FB_CoEAX8000BrakeTest.md](ax8000_coe/FB_CoEAX8000BrakeTest.md) |
| FB_CoEAX8000SetPositionOffset | FB | 写 AX8000 位置偏置 | [ax8000_coe/FB_CoEAX8000SetPositionOffset.md](ax8000_coe/FB_CoEAX8000SetPositionOffset.md) |
| FB_CoEAX8000DeletePositionOffset | FB | 删 AX8000 位置偏置 | [ax8000_coe/FB_CoEAX8000DeletePositionOffset.md](ax8000_coe/FB_CoEAX8000DeletePositionOffset.md) |
| FB_CoEAX8000ParkAxis | FB | AX8000 通道驻留/释放 | [ax8000_coe/FB_CoEAX8000ParkAxis.md](ax8000_coe/FB_CoEAX8000ParkAxis.md) |

### EL72xx CoE（§4.6，EL72xx 伺服端子专用）
| 条目 | 类型 | 说明 | 文档 |
|---|---|---|---|
| FB_CoEEL72xxBrakeControl | FB | EL72xx 手动抱闸控制（需 OCT + FW≥v16） | [el72xx_coe/FB_CoEEL72xxBrakeControl.md](el72xx_coe/FB_CoEEL72xxBrakeControl.md) |
| FB_CoEEL72xxSetPositionOffset | FB | 写 EL72xx 位置偏置（仅驱动器内存） | [el72xx_coe/FB_CoEEL72xxSetPositionOffset.md](el72xx_coe/FB_CoEEL72xxSetPositionOffset.md) |
| FB_CoEEL72xxDeletePositionOffset | FB | 删 EL72xx 位置偏置 | [el72xx_coe/FB_CoEEL72xxDeletePositionOffset.md](el72xx_coe/FB_CoEEL72xxDeletePositionOffset.md) |

### SoE Parameter Access（§6.1，全局常量）
| 条目 | 类型 | 说明 | 文档 |
|---|---|---|---|
| S_0_IDNs | GVL | SoE IDN 基地址常量（S-0…S-7 / P-0…P-7） | [soe_parameter_access/S_0_IDNs.md](soe_parameter_access/S_0_IDNs.md) |

## 硬件无关 vs 型号专用

很多操作有"硬件无关"和"型号专用"两套 FB，行为等价、可互换：

| 操作 | 硬件无关（自动选通道） | AX5000 | AX8000 | EL72xx |
|---|---|---|---|---|
| 抱闸控制 | `FB_BrakeControl` | `FB_SoEAX5000SetMotorCtrlWord` | `FB_CoEAX8000BrakeControl` | `FB_CoEEL72xxBrakeControl` |
| 写位置偏置 | `FB_SetPositionOffset` | `FB_SoEAX5000SetPositionOffset` | `FB_CoEAX8000SetPositionOffset` | `FB_CoEEL72xxSetPositionOffset` |
| 删位置偏置 | `FB_DeletePositionOffset` | `FB_SoEAX5000DeletePositionOffset` | `FB_CoEAX8000DeletePositionOffset` | `FB_CoEEL72xxDeletePositionOffset` |
| 通道驻留 | `FB_ParkAxis` | `FB_SoEAX5000ParkAxis` | `FB_CoEAX8000ParkAxis` | — |

新项目优先用硬件无关版本，跨型号无需改代码；明确单一型号时型号专用版本亦可。

## 数据来源

- **第一可信源**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf)（Version 1.14.2）
- **第二可信源**：[InfoSys tcplclib_tc2_mc2_drive](https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2305793419.html)

各 FB VAR 区已与 PDF 逐字核对；多数与 InfoSys 交叉验证（`InfoSys-checked: ✅ 2026-05-21`）。少数无独立 InfoSys topic 页的条目（`F_GetVersionTcMc2Drive`、`FB_DeletePositionOffset`、`FB_SoEAX5000DeletePositionOffset`、`FB_CoEAX8000ParkAxis`、`S_0_IDNs`）标 `⚠️ not-on-infosys`，已用 PDF 单源核对。
