# Tc2_IoFunctions

Beckhoff TwinCAT 3 **Tc2_IoFunctions** 库的中文技术文档与可导入演示例程。
本库提供通用 I/O 子系统访问、现场总线诊断、bus terminal 配置、SINAMICS Profibus / Profinet DPV1 通讯、SERCOS motion 总线、Beckhoff RAID 监控、Beckhoff UPS 监控、TcTouchLock 多触摸屏聚焦等一系列功能块。

| 字段 | 值 |
|---|---|
| Library | Tc2_IoFunctions |
| Library Version | `1.5.3` |
| PDF | [TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) |
| InfoSys 入口 | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/index.html |
| 文档总数 | **68 个 FB/FC + 1 GVL = 68 篇**（PDF TOC 列 70 项，其中 2 项为 "Overview" 导航条目无独立 API） |
| 例程总数 | **68 个 P_Demo_*.xml** |
| Verify 状态 | 全部 PASS（2026-05-21） |
| Lint 状态 | 全部 PASS（2026-05-21） |

## 分类导航

### General IO FBs（13 个）

通用 I/O 子系统访问：根据名字 / ID / 站号互查 box / device 信息，复位 IO 设备。

| FB | 用途 |
|---|---|
| [IOF_DeviceReset](general_io/IOF_DeviceReset.md) | 在线复位 I/O 设备（等价 System Manager → Reset Device） |
| [IOF_GetBoxAddrByName](general_io/IOF_GetBoxAddrByName.md) | 由 box 名字 + DeviceId 查现场总线地址 |
| [IOF_GetBoxAddrByNameEx](general_io/IOF_GetBoxAddrByNameEx.md) | 由 box 名字 + 设备名字 查现场总线地址（推荐） |
| [IOF_GetBoxCount](general_io/IOF_GetBoxCount.md) | 读现场总线下挂在线 box 总数 |
| [IOF_GetBoxNameByAddr](general_io/IOF_GetBoxNameByAddr.md) | 由站号反查 box 名字（用于报警可读化） |
| [IOF_GetBoxNetId](general_io/IOF_GetBoxNetId.md) | 由站号查 box 的 AMS Net ID（如有） |
| [IOF_GetDeviceCount](general_io/IOF_GetDeviceCount.md) | 读激活 I/O 设备总数 |
| [IOF_GetDeviceIDByName](general_io/IOF_GetDeviceIDByName.md) | 由设备名字查 DeviceId |
| [IOF_GetDeviceIDs](general_io/IOF_GetDeviceIDs.md) | 一次性读所有 I/O 设备 ID 列表 |
| [IOF_GetDeviceInfoByName](general_io/IOF_GetDeviceInfoByName.md) | 由设备名字一次性查 DeviceId + AMS Net ID |
| [IOF_GetDeviceName](general_io/IOF_GetDeviceName.md) | 由 DeviceId 反查设备名字 |
| [IOF_GetDeviceNetId](general_io/IOF_GetDeviceNetId.md) | 由 DeviceId 查设备的 AMS Net ID（如有） |
| [IOF_GetDeviceType](general_io/IOF_GetDeviceType.md) | 由 DeviceId 查 I/O 设备类型枚举（Profibus / EtherCAT / Lightbus / ...） |

### ASI master terminal（8 个）

KL6201 / EL6201 ASI 主端子的 slave 管理 + 过程数据访问。
`FB_ASI_ParameterControl` 是必须循环调用的后台调度器。

| FB | 用途 |
|---|---|
| [FB_ASI_Addressing](asi_master_terminal/FB_ASI_Addressing.md) | 给 ASI slave 编址 |
| [FB_ASI_SlaveDiag](asi_master_terminal/FB_ASI_SlaveDiag.md) | slave 计数器诊断 + LES / LAS 位图 |
| [FB_ASI_ReadParameter](asi_master_terminal/FB_ASI_ReadParameter.md) | 读 slave 4-bit 参数 |
| [FB_ASI_WriteParameter](asi_master_terminal/FB_ASI_WriteParameter.md) | 写 slave 4-bit 参数 |
| [FB_ASI_Processdata_digital](asi_master_terminal/FB_ASI_Processdata_digital.md) | 数字过程数据读 / 写 |
| [FB_ASI_ParameterControl](asi_master_terminal/FB_ASI_ParameterControl.md) | **后台调度器（必须循环调用）** |
| [FB_ReadInput_analog](asi_master_terminal/FB_ReadInput_analog.md) | ASI 模拟输入读取 |
| [FB_WriteOutput_analog](asi_master_terminal/FB_WriteOutput_analog.md) | ASI 模拟输出写入 |

### AX200x Profibus（5 个）

Kollmorgen AX2000 老 Profibus 伺服驱动器接口（维护老线）。

| FB | 用途 |
|---|---|
| [FB_AX2000_Parameter](ax200x_profibus/FB_AX2000_Parameter.md) | PKW 读 / 写 AX2000 驱动器参数 |
| [FB_AX2000_AXACT](ax200x_profibus/FB_AX2000_AXACT.md) | motion 命令（start / stop / motion-task） |
| [FB_AX2000_JogMode](ax200x_profibus/FB_AX2000_JogMode.md) | 点动模式 |
| [FB_AX2000_Reference](ax200x_profibus/FB_AX2000_Reference.md) | 设参考点 / homing |
| [FB_AX200X_Profibus](ax200x_profibus/FB_AX200X_Profibus.md) | 综合 FB（不含 PKW） |

### Beckhoff Lightbus（3 个）

早期 Beckhoff 光纤总线（C1220 / FC200x）；**TwinCAT 3 已不支持**，仅供老工程兼容性参考。

| FB | 用途 |
|---|---|
| [IOF_LB_BreakLocationTest](beckhoff_lightbus/IOF_LB_BreakLocationTest.md) | 断纤位置定位 |
| [IOF_LB_ParityCheck](beckhoff_lightbus/IOF_LB_ParityCheck.md) | 读奇偶错计数器（不复位） |
| [IOF_LB_ParityCheckWithReset](beckhoff_lightbus/IOF_LB_ParityCheckWithReset.md) | 读奇偶错计数器 + 复位 |

### Beckhoff UPS（1 个）

UPS 状态读取（电平触发，约每 4.5 秒读一次）。

| FB | 用途 |
|---|---|
| [FB_GetUPSStatus](beckhoff_ups/FB_GetUPSStatus.md) | 读 UPS 状态（电池电量 / AC vs 电池 / 倒计时） |

### Bus Terminal configuration（5 个）

KL 端子的运行时配置 FB（写端子寄存器）。每通道独立 FB 实例。

| FB | 端子 |
|---|---|
| [FB_KL1501Config](bus_terminal_configuration/FB_KL1501Config.md) | KL1501 计数器端子 |
| [FB_KL27x1Config](bus_terminal_configuration/FB_KL27x1Config.md) | KL2751 / KL2761 调光端子 |
| [FB_KL320xConfig](bus_terminal_configuration/FB_KL320xConfig.md) | KL3201 / 3202 / 3204 电阻输入端子 |
| [FB_KL3208Config](bus_terminal_configuration/FB_KL3208Config.md) | KL3208-0010 8 通道电阻输入端子 |
| [FB_KL3228Config](bus_terminal_configuration/FB_KL3228Config.md) | KL3228 8 通道电阻输入端子 |

### CANopen（1 个）

| FB | 用途 |
|---|---|
| [IOF_CAN_Layer2Command](canopen/IOF_CAN_Layer2Command.md) | layer-2 原始 CAN 帧发送（TwinCAT 3 不支持） |

### NOV/DP-RAM（4 个）

FCxxxx-0002 卡 NOV-RAM 直接访问（老接口；现代 retain 不需要）。

| FB | 用途 |
|---|---|
| [FB_NovRamReadWrite](nov_dpram/FB_NovRamReadWrite.md) | NOV-RAM 偏移 0 读 / 写 |
| [FB_NovRamReadWriteEx](nov_dpram/FB_NovRamReadWriteEx.md) | NOV-RAM 任意偏移 + 字节对齐 |
| [FB_GetDPRAMInfo](nov_dpram/FB_GetDPRAMInfo.md) | 查 NOV-RAM 地址 + 大小 |
| [FB_GetDPRAMInfoEx](nov_dpram/FB_GetDPRAMInfoEx.md) | 查 NOV-RAM 完整元信息（含访问类型） |

### Profibus DPV1 (Sinamics)（6 个）

SINAMICS Profidrive 通过 Profibus DPV1 读 / 写参数。完整流程：`F_Create*ReqPkg` → `FB_Dpv1*` → `F_Split*ResPkg`。

| FB/FC | 用途 |
|---|---|
| [F_CreateDpv1ReadReqPkg](profibus_dpv1_sinamics/F_CreateDpv1ReadReqPkg.md) | 生成读请求帧 |
| [F_CreateDpv1WriteReqPkg](profibus_dpv1_sinamics/F_CreateDpv1WriteReqPkg.md) | 生成写请求帧 |
| [F_SplitDpv1ReadResPkg](profibus_dpv1_sinamics/F_SplitDpv1ReadResPkg.md) | 解析读响应帧 |
| [F_SplitDpv1WriteResPkg](profibus_dpv1_sinamics/F_SplitDpv1WriteResPkg.md) | 解析写响应帧 |
| [FB_Dpv1Read](profibus_dpv1_sinamics/FB_Dpv1Read.md) | 发读请求 + 等响应（异步） |
| [FB_Dpv1Write](profibus_dpv1_sinamics/FB_Dpv1Write.md) | 发写请求 + 等响应（异步） |

### Profinet DPV1 (Sinamics)（6 个）

与 Profibus DPV1 对称，面向 EL6632 Profinet 主站。

| FB/FC | 用途 |
|---|---|
| [F_CreateDpv1ReadReqPkgPNET](profinet_dpv1_sinamics/F_CreateDpv1ReadReqPkgPNET.md) | 生成读请求帧 |
| [F_CreateDpv1WriteReqPkgPNET](profinet_dpv1_sinamics/F_CreateDpv1WriteReqPkgPNET.md) | 生成写请求帧 |
| [F_SplitDpv1ReadResPkgPNET](profinet_dpv1_sinamics/F_SplitDpv1ReadResPkgPNET.md) | 解析读响应帧 |
| [F_SplitDpv1WriteResPkgPNET](profinet_dpv1_sinamics/F_SplitDpv1WriteResPkgPNET.md) | 解析写响应帧 |
| [FB_Dpv1ReadPNET](profinet_dpv1_sinamics/FB_Dpv1ReadPNET.md) | 发读请求 + 等响应 |
| [FB_Dpv1WritePNET](profinet_dpv1_sinamics/FB_Dpv1WritePNET.md) | 发写请求 + 等响应 |

### RAID Controller（3 个）

Beckhoff 工业服务器 RAID 阵列状态监控。**所有 FB 不能循环调用**（PDF NOTICE 警告）。

| FB | 用途 |
|---|---|
| [FB_RAIDFindCntlr](raid_controller/FB_RAIDFindCntlr.md) | 枚举 RAID 控制器 |
| [FB_RAIDGetInfo](raid_controller/FB_RAIDGetInfo.md) | 查控制器的 RAID 集数 + 每组最大盘数 |
| [FB_RAIDGetStatus](raid_controller/FB_RAIDGetStatus.md) | 查 RAID 阵列健康状态（每秒最多一次） |

### SERCOS（9 个）

早期 SERCOS motion 总线（SERCANS / FC750x）。

| FB | 用途 |
|---|---|
| [IOF_SER_GetPhase](sercos/IOF_SER_GetPhase.md) | 读当前 SERCOS 通讯 phase（0..4） |
| [IOF_SER_SetPhase](sercos/IOF_SER_SetPhase.md) | 设置 SERCOS 通讯 phase |
| [IOF_SER_SaveFlash](sercos/IOF_SER_SaveFlash.md) | 保存系统参数到主站 EEPROM |
| [IOF_SER_ResetErr](sercos/IOF_SER_ResetErr.md) | 全清错（主站 + 所有 drive） |
| [IOF_SER_IDN_Read](sercos/IOF_SER_IDN_Read.md) | 读 drive 的 S / P 参数（按 IDN） |
| [IOF_SER_IDN_Write](sercos/IOF_SER_IDN_Write.md) | 写 drive 的 S / P 参数 |
| [IOF_SER_DRIVE_Backup](sercos/IOF_SER_DRIVE_Backup.md) | drive 参数备份 / 恢复 |
| [IOF_SER_DRIVE_BackupEx](sercos/IOF_SER_DRIVE_BackupEx.md) | drive 参数备份 / 恢复（支持自定义清单 + 忽略错误） |
| [IOF_SER_DRIVE_Reset](sercos/IOF_SER_DRIVE_Reset.md) | 单 drive 复位 |

### TcTouchLock（1 个）

多触摸屏聚焦控制。

| FB | 用途 |
|---|---|
| [FB_TcTouchLock_AcquireFocus](tctouchlock/FB_TcTouchLock_AcquireFocus.md) | 请求 / 释放某个屏的输入 focus |

### Obsolete（2 个）

⚠️ **已废弃**。新工程改用 `stLibVersion_Tc2_IoFunctions` 全局常量。

| FC | 用途 |
|---|---|
| [F_GetVersionTcIoFunctions](obsolete/F_GetVersionTcIoFunctions.md) | 读库版本号字段（废弃） |
| [F_GetVersionRAIDController](obsolete/F_GetVersionRAIDController.md) | 读库版本号字段（废弃） |

### Library version（1 个）

| GVL | 用途 |
|---|---|
| [stLibVersion_Tc2_IoFunctions](library_version/stLibVersion_Tc2_IoFunctions.md) | 库版本全局常量（`ST_LibVersion`） |

## 例程目录

所有 68 篇文档配套的 PLCopenXML 演示程序在 [`examples/`](examples/) 下，文件名 `P_Demo_<Name>.xml`。

导入方式：
1. 右键 TwinCAT 3 PLC 项目 → **Import PLCopenXML**
2. 选 `examples/P_Demo_<Name>.xml`
3. 编译 → 登录 → 按文档 §7 与例程头部"验证"注释执行测试

## 文档遵循的硬规则

详见仓库根目录的 [`CLAUDE.md`](../CLAUDE.md)，要点：
- 中文叙述、IEC 关键字保留英文
- 不出现「详见 PDF」「见上方」等占位短语
- 每篇含 PDF + InfoSys 双源 URL
- 例程含「场景 / 价值 / 验证步骤」三件套
- 例程注释 ≥ 1/3 代码行，解释 WHY 不复述 WHAT
- 不引入 TwinCAT 私有特性，例程是纯 PLCopenXML 可跨工程导入

## 已知偏差与待人工确认 ⚠️

1. **PDF VAR 区拼写错误（已在对应文档中点明）**：
   - `FB_ASI_SlaveDiag`：`bCyleMode` 应为 `bCycleMode`；`bCounterReset` 在描述列出现但 VAR_INPUT 区没有
   - `IOF_SER_SetPhase`：VAR 区 `PHASE : BOOL` 应为 `PHASE : BYTE`
   - `IOF_SER_IDN_Write`：描述列 `dwDestAddr` 应为 `dwSrcAddr`
   - `IOF_CAN_Layer2Command`：VAR_INPUT 区漏列 `LEN` 与 `SRCADDR`
   - `FB_TcTouchLock_AcquireFocus`：`bError:` 末尾多冒号
   - `FB_Dpv1Read/Write/ReadPNET/WritePNET`：`iRequestRef` 在 PDF 中标在 "Inputs/outputs" 章节，实际是 VAR_OUTPUT
2. **`F_GetVersionTcIoFunctions` / `F_GetVersionRAIDController`** 在 InfoSys 没有专属页面，本文档的 `Source InfoSys` 字段指向 Library version 页作为替代说明，并把 `InfoSys-checked` 标为 `⚠️ not-on-infosys`。
3. **`IOF_SER_DRIVE_BackupEx`** 的 `arrList`（用户自定义清单数组）字段在 PDF VAR 区未完整列出；使用前请对照 PDF 正文 + drive 手册。
4. **CANopen / Lightbus** 类 FB：PDF 明确 TwinCAT 3 不支持对应硬件（HILSCHER CIF3xx / Beckhoff C1220）。本系列文档仅作"代码兼容性参考"。
