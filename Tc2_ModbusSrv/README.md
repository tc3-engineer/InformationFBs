# Tc2_ModbusSrv（TF6250 Modbus TCP）

> Beckhoff TwinCAT 3 TF6250 Modbus TCP 的 PLC 库。提供让 PLC 充当 **Modbus 主站（client）**
> 主动读写远端 Modbus 设备的功能块（TCP 与 UDP 两套），以及库版本常量。
> 运行时需要 TF6250 Modbus TCP 授权。

## 概览

| 字段 | 值 |
|---|---|
| 库版本 | `1.6.4` |
| 来源 PDF | [TF6250_TC3_Modbus_TCP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6250_TC3_Modbus_TCP_EN.pdf) |
| InfoSys 根 | https://infosys.beckhoff.com/content/1033/tf6250_tc3_modbus_tcp/index.html |
| 文档进度 | 21 / 21（FB 20 + GVL 1） |

**主站 vs 从站（关键区分）**：本库的 `FB_MB*` / `FB_MBUdp*` 功能块让 TwinCAT PLC 作为 **Modbus 主站/客户端**，
主动去读写别的 Modbus 设备（参数 `sIPAddr` 指向目标设备）。如果需求是“让 TwinCAT 自身作为 Modbus **从站/服务端**
被外部 SCADA / 主站访问”，那是另一套机制：通过 TF6250 服务端 + TwinCAT Modbus TCP 配置器（`TcModbusSrv.xml`）
+ PLC 里的 `mb_Input_Coils` / `mb_Output_Coils` / `mb_Input_Registers` / `mb_Output_Registers` 全局数组 + ADS 映射完成，
**不经过本库的任何 FB**（参见 PDF 第 4 章 Configuration、第 5 章 Diagnosis）。本仓库 21 篇覆盖的是主站侧 FB + 库版本常量。

## Modbus 功能码对照

| Modbus 功能 | 功能码 | TCP 功能块 | UDP 功能块 |
|---|---|---|---|
| Read Coils（读线圈） | 1 | `FB_MBReadCoils` | `FB_MBUdpReadCoils` |
| Read Discrete Inputs（读离散输入） | 2 | `FB_MBReadInputs` | `FB_MBUdpReadInputs` |
| Read Holding Registers（读保持寄存器） | 3 | `FB_MBReadRegs` | `FB_MBUdpReadRegs` |
| Read Input Registers（读输入寄存器） | 4 | `FB_MBReadInputRegs` | `FB_MBUdpReadInputRegs` |
| Write Single Coil（写单线圈） | 5 | `FB_MBWriteSingleCoil` | `FB_MBUdpWriteSingleCoil` |
| Write Single Register（写单寄存器） | 6 | `FB_MBWriteSingleReg` | `FB_MBUdpWriteSingleReg` |
| Write Multiple Coils（写多线圈） | 15 | `FB_MBWriteCoils` | `FB_MBUdpWriteCoils` |
| Write Multiple Registers（写多寄存器） | 16 | `FB_MBWriteRegs` | `FB_MBUdpWriteRegs` |
| Read/Write Multiple Registers（读写多寄存器） | 23 | `FB_MBReadWriteRegs` | `FB_MBUdpReadWriteRegs` |
| Diagnostics（诊断） | 8 | `FB_MBDiagnose` | `FB_MBUdpDiagnose` |

## Function Blocks — TCP（10）

| 名称 | Modbus 功能码 | 用途 | 文档 |
|---|---|---|---|
| `FB_MBReadCoils` | 1 | 读线圈 | [function_blocks/FB_MBReadCoils.md](function_blocks/FB_MBReadCoils.md) |
| `FB_MBReadInputs` | 2 | 读离散输入 | [function_blocks/FB_MBReadInputs.md](function_blocks/FB_MBReadInputs.md) |
| `FB_MBReadRegs` | 3 | 读保持寄存器 | [function_blocks/FB_MBReadRegs.md](function_blocks/FB_MBReadRegs.md) |
| `FB_MBReadInputRegs` | 4 | 读输入寄存器 | [function_blocks/FB_MBReadInputRegs.md](function_blocks/FB_MBReadInputRegs.md) |
| `FB_MBWriteSingleCoil` | 5 | 写单个线圈 | [function_blocks/FB_MBWriteSingleCoil.md](function_blocks/FB_MBWriteSingleCoil.md) |
| `FB_MBWriteSingleReg` | 6 | 写单个寄存器 | [function_blocks/FB_MBWriteSingleReg.md](function_blocks/FB_MBWriteSingleReg.md) |
| `FB_MBWriteCoils` | 15 | 写多线圈 | [function_blocks/FB_MBWriteCoils.md](function_blocks/FB_MBWriteCoils.md) |
| `FB_MBWriteRegs` | 16 | 写多寄存器 | [function_blocks/FB_MBWriteRegs.md](function_blocks/FB_MBWriteRegs.md) |
| `FB_MBReadWriteRegs` | 23 | 同事务先读后写寄存器 | [function_blocks/FB_MBReadWriteRegs.md](function_blocks/FB_MBReadWriteRegs.md) |
| `FB_MBDiagnose` | 8 | 设备诊断（function 8） | [function_blocks/FB_MBDiagnose.md](function_blocks/FB_MBDiagnose.md) |

## Function Blocks — UDP（10）

> UDP 版与同名 TCP 版接口完全一致，区别仅在传输层：UDP 无连接、首包更快，但不保证可靠交付。
> 适合同网段、低延迟、可容忍偶发丢包的场景。

| 名称 | Modbus 功能码 | 用途 | 文档 |
|---|---|---|---|
| `FB_MBUdpReadCoils` | 1 | 读线圈 | [function_blocks/FB_MBUdpReadCoils.md](function_blocks/FB_MBUdpReadCoils.md) |
| `FB_MBUdpReadInputs` | 2 | 读离散输入 | [function_blocks/FB_MBUdpReadInputs.md](function_blocks/FB_MBUdpReadInputs.md) |
| `FB_MBUdpReadRegs` | 3 | 读保持寄存器 | [function_blocks/FB_MBUdpReadRegs.md](function_blocks/FB_MBUdpReadRegs.md) |
| `FB_MBUdpReadInputRegs` | 4 | 读输入寄存器 | [function_blocks/FB_MBUdpReadInputRegs.md](function_blocks/FB_MBUdpReadInputRegs.md) |
| `FB_MBUdpWriteSingleCoil` | 5 | 写单个线圈 | [function_blocks/FB_MBUdpWriteSingleCoil.md](function_blocks/FB_MBUdpWriteSingleCoil.md) |
| `FB_MBUdpWriteSingleReg` | 6 | 写单个寄存器 | [function_blocks/FB_MBUdpWriteSingleReg.md](function_blocks/FB_MBUdpWriteSingleReg.md) |
| `FB_MBUdpWriteCoils` | 15 | 写多线圈 | [function_blocks/FB_MBUdpWriteCoils.md](function_blocks/FB_MBUdpWriteCoils.md) |
| `FB_MBUdpWriteRegs` | 16 | 写多寄存器 | [function_blocks/FB_MBUdpWriteRegs.md](function_blocks/FB_MBUdpWriteRegs.md) |
| `FB_MBUdpReadWriteRegs` | 23 | 同事务先读后写寄存器 | [function_blocks/FB_MBUdpReadWriteRegs.md](function_blocks/FB_MBUdpReadWriteRegs.md) |
| `FB_MBUdpDiagnose` | 8 | 设备诊断（function 8） | [function_blocks/FB_MBUdpDiagnose.md](function_blocks/FB_MBUdpDiagnose.md) |

## Global Constants（1）

| 名称 | 用途 | 文档 |
|---|---|---|
| `stLibVersion_Tc2_ModbusSrv` | 库版本结构（运行时版本检查用） | [global_constants/stLibVersion_Tc2_ModbusSrv.md](global_constants/stLibVersion_Tc2_ModbusSrv.md) |

## 通用调用约定

所有数据传输 FB 共享一套约定：

- `sIPAddr` 填**目标设备** IP；`nTCPPort` 用常量 `MODBUS_TCP_PORT`（=502）；`nUnitID` 直连填 `16#FF`。
- `bExecute` **上升沿**触发一次（不是电平），周期采集需自行产生脉冲。
- 读用 `pDestAddr` + `cbLength` 指定落点缓冲区；写用 `pSrcAddr` + `cbLength` 指定源缓冲区；用 `ADR()` / `SIZEOF()` 赋值。
- 输出 `bBUSY`（执行中）/ `bError` / `nErrId`（ADS/Modbus 错误码）三件套；读类还有 `cbRead`。
- `tTimeout` 无默认值，必须显式赋（如 `T#5S`）。

## 错误码概览

`nErrId`（`UDINT`）按取值分三段（PDF §8.1）：

| 范围（hex） | 来源 | 例 |
|---|---|---|
| `0x0000`–`0x7800` | TwinCAT 系统 / ADS 错误 | `6` 端口未找到、`7` 机器未找到、`1861` ADS 超时 |
| `0x8000`–`0x80FF` | 内部 TwinCAT Modbus TCP 错误 | `8001` 功能未实现、`8002` 地址/长度无效、`8003` 参数无效、`8004` 服务器错误 |
| `0x80070000`–`0x8007FFFF` | Win32 / Winsock | 真值 = `nErrId - 0x80070000` |

## 例程导入

每篇文档配套 `examples/P_Demo_<Name>.TcPOU`：

1. 在 TwinCAT 3 XAE 中右键 PLC 项目下 POUs 文件夹 → **Add → Existing Item…**
2. 选择 `P_Demo_<Name>.TcPOU`
3. 引用 `Tc2_ModbusSrv`，确保 TF6250 已授权运行
4. 把例程里的 `sTargetIp` 改成现场设备 IP，编译 → 登录 → 运行
5. 按文档 §6 / §7 的“验证步骤”在线脉冲 `bTrigger` 观察输出

## 参考资料

- **PDF**：[TF6250_TC3_Modbus_TCP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6250_TC3_Modbus_TCP_EN.pdf)
- **InfoSys 根**：https://infosys.beckhoff.com/content/1033/tf6250_tc3_modbus_tcp/index.html
