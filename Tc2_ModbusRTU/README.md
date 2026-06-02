# Tc2_ModbusRTU（TF6255 Modbus RTU）

> Beckhoff TwinCAT 3 Modbus RTU 串行通讯 PLC 库——主站（master）+ 从站（slave）。
> 这是 TF6255 TwinCAT 3 Modbus RTU 的 PLC 库。

## 概览

| 字段 | 值 |
|---|---|
| 库版本 | `1.4.3` |
| 来源 PDF | [TF6255_TC3_Modbus_RTU_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6255_TC3_Modbus_RTU_EN.pdf) |
| InfoSys 根 | https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/ |
| 文档进度 | 12 / 12（8 FB + 3 obsolete FB + 1 GVL；DUT 仅作引用） |

**用途定位**：让 TwinCAT 控制器经 RS232/RS485 串口做 Modbus RTU 通讯——既能当**主站**主动轮询现场的变频器/电表/温控器/第三方 PLC，也能当**从站**把自身数据暴露给上位 PLC/SCADA/网关。与 Modbus **TCP**（TF6250）的区别是走串口而非以太网。

**硬件接口选型**：每种角色（主站/从站）都有 4 个硬件变体——
- `_PcCOM`：PC 板载/扩展 COM 口
- `_KL6x22B`：串行总线端子 KL6031 / KL6041（及 22 字节过程映像的串行 EtherCAT 端子）
- `_KL6x5B`：串行总线端子 KL6001 / KL6011 / KL6021（3 字节过程映像）
- `_Generic`：硬件无关，**唯一支持虚拟 COM 口**，但需额外引入 `Tc2_SerialCom` + TF6340 license，并把 `RxBuffer`/`TxBuffer`（`ComBuffer`）作为 `VAR_IN_OUT` 接到后台串口块

**许可**：`_PcCOM` / `_KL6x22B` / `_KL6x5B` 系列不单独要 TF6255 运行时 license（按 PDF 描述）；`_Generic` 系列依赖 `Tc2_SerialCom` 的通讯块，需 TF6340 TwinCAT 3 Serial Communication license。KL6x 端子的串口参数配置（用 `Tc2_SerialCom` 的 `KL6configuration`）本身不需 license。

## 典型部署模板

### 作主站（主动轮询从站）
1. 选硬件变体（`ModbusRtuMasterV2_PcCOM` / `_KL6x22B` / `_KL6x5B` / `_Generic`）
2. 在 System Manager 把 FB 内置的串口数据结构链接到 COM 口 / 端子（`_Generic` 改为每周期跑 `Tc2_SerialCom` 串口块搬运缓冲）
3. 业务里按动作调用：`fbMaster.ReadRegs(...)`（功能码 3）、`fbMaster.WriteRegs(...)`（功能码 16）等
4. `Execute` 上升沿触发一次，等 `BUSY` 落回判 `Error`/`ErrorId`

### 作从站（被动应答主站）
1. 声明三块 Modbus 数据区：输入区（偏移 `16#0`，功能码 2/4 只读）、输出区（偏移 `16#800`，功能码 1/3/5/6/15/16）、存储区（偏移 `16#4000`，功能码 3/6/16）
2. 选硬件变体（`ModbusRtuSlave_PcCOM` / `_KL6x22B` / `_KL6x5B` / `_Generic`），把三块区的 `ADR`/`SIZEOF` 传入
3. 每个 PLC 周期调用一次（从站无 `Execute`，纯被动）

## Function blocks（8）

### 主站 ModbusRtuMasterV2_*（4）

| 名称 | 硬件接口 | 文档 |
|---|---|---|
| `ModbusRtuMasterV2_PcCOM` | PC COM 口 | [function_blocks/ModbusRtuMasterV2_PcCOM.md](function_blocks/ModbusRtuMasterV2_PcCOM.md) |
| `ModbusRtuMasterV2_KL6x22B` | KL6031 / KL6041（22 字节映像） | [function_blocks/ModbusRtuMasterV2_KL6x22B.md](function_blocks/ModbusRtuMasterV2_KL6x22B.md) |
| `ModbusRtuMasterV2_KL6x5B` | KL6001 / KL6011 / KL6021（3 字节映像） | [function_blocks/ModbusRtuMasterV2_KL6x5B.md](function_blocks/ModbusRtuMasterV2_KL6x5B.md) |
| `ModbusRtuMasterV2_Generic` | 硬件无关 / 虚拟 COM（需 Tc2_SerialCom + TF6340） | [function_blocks/ModbusRtuMasterV2_Generic.md](function_blocks/ModbusRtuMasterV2_Generic.md) |

V2 主站支持功能码 1/2/3/4/5/6/8/15/16/23 及用户自定义报文（`ReadWriteRegs`=23、`UserReadWrite` 为 V2 独有，带 `Aux*` 辅助参数）。

### 从站 ModbusRtuSlave_*（4）

| 名称 | 硬件接口 | 文档 |
|---|---|---|
| `ModbusRtuSlave_PcCOM` | PC COM 口 | [function_blocks/ModbusRtuSlave_PcCOM.md](function_blocks/ModbusRtuSlave_PcCOM.md) |
| `ModbusRtuSlave_KL6x22B` | KL6031 / KL6041（22 字节映像） | [function_blocks/ModbusRtuSlave_KL6x22B.md](function_blocks/ModbusRtuSlave_KL6x22B.md) |
| `ModbusRtuSlave_KL6x5B` | KL6001 / KL6011 / KL6021（3 字节映像） | [function_blocks/ModbusRtuSlave_KL6x5B.md](function_blocks/ModbusRtuSlave_KL6x5B.md) |
| `ModbusRtuSlave_Generic` | 硬件无关 / 虚拟 COM（需 Tc2_SerialCom + TF6340） | [function_blocks/ModbusRtuSlave_Generic.md](function_blocks/ModbusRtuSlave_Generic.md) |

## Obsolete（3，已废弃，仅维护老程序）

PDF §5.1.1 `[obsolete]` 区的旧版主站。它们 `UnitID` 为 `UINT`（V2 的 VAR 声明块为 `BYTE`），且**不含**功能码 23 / 用户自定义报文。新工程请用对应的 V2 版本。

| 名称 | 推荐替代 | 文档 |
|---|---|---|
| `ModbusRtuMaster_PcCOM` | `ModbusRtuMasterV2_PcCOM` | [obsolete/ModbusRtuMaster_PcCOM.md](obsolete/ModbusRtuMaster_PcCOM.md) |
| `ModbusRtuMaster_KL6x5B` | `ModbusRtuMasterV2_KL6x5B` | [obsolete/ModbusRtuMaster_KL6x5B.md](obsolete/ModbusRtuMaster_KL6x5B.md) |
| `ModbusRtuMaster_KL6x22B` | `ModbusRtuMasterV2_KL6x22B` | [obsolete/ModbusRtuMaster_KL6x22B.md](obsolete/ModbusRtuMaster_KL6x22B.md) |

## Global Constants（1）

| 名称 | 类型 | 文档 |
|---|---|---|
| `Global_Version`（`stLibVersion_Tc2_Modbus_RTU`） | `VAR_GLOBAL CONSTANT` / `ST_LibVersion` | [global_constants/Global_Version.md](global_constants/Global_Version.md) |

## Datatypes（2，未单独成文档）

以下数据类型在 PDF §5.2 出现，作为上述 FB 的参数 / 输出类型使用；不为单独条目生成 .md（按 CLAUDE.md 流程 DUT 在父 FB 文档中按需引用，各 FB 的 §4 已完整列出 `MODBUS_ERRORS`）：

| 名称 | 类型 | 用途 |
|---|---|---|
| `MODBUS_UNITID` | ENUM | 站地址集合：`MODBUS_UNITID_BROADCAST`=0、`MODBUS_UNITID_ALLVALID`=256（应答 1..247）、`MODBUS_UNITID_ALLBUTBROADCAST`=257（应答 1..255）、`MODBUS_UNITID_ALL`=258（应答 0..255）。有效单站地址 1..247，248..255 保留。InfoSys topic：[186546827](https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/186546827.html) |
| `MODBUS_ERRORS` | ENUM | 主站/从站 `ErrorId` 输出的错误号枚举。InfoSys topic：[186558219](https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/186558219.html) |

## Modbus 地址映射（从站，PDF §4.2）

从站把三块 PLC 数据区按固定偏移映射到 Modbus 地址空间。**主站组态时 `MBAddr` 必须带上偏移**：

| 数据区 | Modbus 报文地址偏移 | 最大尺寸 | 主站可用功能码 | 设备地址示例（首元素） |
|---|---|---|---|---|
| Inputs（输入区，只读） | `16#0` | 2048 words | 2、4 | 30001（字）/ 10001（位） |
| Outputs（输出区，读写） | `16#800` | 14336 words | 1、3、5、6、15、16 | 40801（字）/ 00801（位） |
| Memory（存储区，读写） | `16#4000` | 16384 words | 3、6、16 | 44001（字） |

输入/输出区可用 `AT %I*` / `AT %Q*` 直接映射控制器物理 I/O，也可声明为与物理无关的纯数据区。

## MODBUS_ERRORS 错误码概览

主站和从站的 `ErrorId : MODBUS_ERRORS` 输出，分三类（PDF §5.2.2）：

| 类别 | 取值 | 代表错误 |
|---|---|---|
| Modbus 标准异常码 | 0..16#B | `ILLEGAL_FUNCTION`=1、`ILLEGAL_DATA_ADDRESS`=2、`ILLEGAL_DATA_VALUE`=3、`SLAVE_DEVICE_FAILURE`=4、`SLAVE_DEVICE_BUSY`=6 |
| 库追加 Modbus 错误 | 16#20..16#25 | `CHARREC_TIMEOUT`=16#20、`ILLEGAL_DATA_SIZE`=16#21（多为 `cbLength` 不足）、`NO_RESPONSE`=16#25（最常见掉线错） |
| 底层 / 高层 PLC 错误 | 102..233 | `SENDTIMEOUT`=103、`INVALIDPOINTER`=120、`CRC`=150（波特率/校验位不匹配或线路干扰）、`INVALIDMEMORYADDRESS`=232 |

## 例程导入

每篇文档配套 `examples/P_Demo_<Name>.TcPOU`：

1. 在 TwinCAT 3 XAE 中右键 PLC 项目下 POUs 文件夹 → **Add → Existing Item…**
2. 选择 `P_Demo_<Name>.TcPOU`
3. References → Add library → `Tc2_ModbusRTU`（`_Generic` 变体另需 `Tc2_SerialCom`）
4. 编译 → 登录 → 运行
5. 按文档 §6 / §7 中的「验证步骤」在线观察输入输出

## 验证基线

- 全部 12 篇文档 `verify_doc.py` 退出 0（PASS）：双源核对 VAR 名/类型/默认值、占位短语扫描、§3 长度、InfoSys topic URL + InfoSys-checked 格式。
- 全部 12 个 `.TcPOU` 例程 `lint_tcpou.py` 退出 0（PASS）。
- 双可信源：PDF（v1.4.3）+ InfoSys（slug `tf6255_tc3_modbus_rtu`），逐条对照。
- ⚠️ 已知文档级不一致：V2 主站系列的 `UnitID` 在 PDF/InfoSys 的 **VAR 声明块**为 `BYTE`，而**参数说明表 Type 列**为 `UINT`；本仓库逐字搬运声明块（`BYTE`），并在各 V2 主站文档 §5/§9 说明。obsolete 主站的 `UnitID` 两处一致为 `UINT`。

## 参考资料

- **PDF**：[TF6255_TC3_Modbus_RTU_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6255_TC3_Modbus_RTU_EN.pdf)
- **InfoSys 根**：https://infosys.beckhoff.com/content/1033/tf6255_tc3_modbus_rtu/
- **产品页**：https://www.beckhoff.com/tf6255
- **相关库**：`Tc2_SerialCom`（Generic 变体的后台串口通讯）、`Tc2_System`（`F_CmpLibVersion` / `ST_LibVersion`）、Modbus TCP 见 TF6250
