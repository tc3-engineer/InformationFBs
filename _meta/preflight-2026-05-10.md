# Pre-flight 报告 · 2026-05-10（含 URL 别名）

> 由 `python3 _meta/tools/fetch_pdf.py --head-only` 生成。对 `library-catalog.md`
> 中所有 41 个库做 Range GET 探测。`fetch_pdf.py` 内置 `URL_ALIASES` 对应
> TwinCAT Functions（TF）系列产品的非标准 URL 命名。

- **总数**：41
- **可达（200/206）**：40
- **不可达（404）**：1（Tc2_KNXLib）

## ✅ 可达（40）

### 走标准 URL 模式 `TwinCAT_3_PLC_Lib_<NAME>_EN.pdf`（22）

Tc2_Standard、Tc2_System、Tc2_Utilities、Tc2_Math、Tc3_EventLogger、
Tc2_MC2、Tc2_MC2_Drive、Tc2_NcDrive、Tc2_Drive、Tc2_EtherCAT、
Tc2_IoFunctions、Tc2_ProfinetDiag、Tc3_JsonXml、Tc2_DataExchange、Tc2_SUPS、
Tc3_DriveMotionControl、Tc3_MC2_AdvancedHoming、Tc2_DALI、Tc2_DMX、
Tc2_EIB、Tc2_EnOcean、Tc2_Coupler

### 走 URL 别名（TF 系列产品手册，18）

| 库 | 实际 PDF |
|---|---|
| Tc2_NC | `TF50x0_TC3_NC_PTP_EN.pdf` |
| Tc2_TcpIp | `TF6310_TC3_TCP_IP_EN.pdf` |
| Tc2_SerialCom | `TF6340_TC3_Serial_Communication_EN.pdf` |
| Tc2_ModbusSrv | `TF6250_TC3_Modbus_TCP_EN.pdf` |
| Tc2_ModbusRTU | `TF6255_TC3_Modbus_RTU_EN.pdf` |
| Tc2_EthernetIP | `TF6280_EtherNet_IP_Adapter_EN.pdf` |
| Tc3_Database | `tf6420_tc3_database_server_en.pdf` |
| Tc2_Database | `twincat2/TS6420_tcdbserver_en.pdf`（TwinCAT 2 路径） |
| Tc2_Filter | `TF3680_TC3_Filter_EN.pdf` |
| Tc2_MC2_Camming | `TF5050_TC3_NC_Camming_EN.pdf` |
| Tc2_MC2_FlyingSaw | `TF5055_TC3_NC_Flying_Saw_EN.pdf` |
| Tc2_NCI | `TF5100_TC3_NC_I_EN.pdf` |
| Tc3_Vision | `TF7000-TF7810_TC3_Vision_EN.pdf` |
| Tc2_Hydraulic | `TF5810_TC3_Hydraulic_Positioning_EN.pdf` |
| Tc2_BACnet | `TF8020_TC3_BACnet_EN.pdf` |
| Tc3_BA2 | `TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf`（注：实际 lib 名 `Tc3_BA2_Common`） |
| Tc2_HVAC | `TF8000_TC3_HVAC_EN.pdf` |
| Tc2_Lighting | `TF8050_LS_EN.pdf` |

> ⚠️ **TF 系列文档结构与 PLC Library 文档不同**：TF 文档是产品手册（含许可、安装、配置），FB API 在 "PLC API" 章节下嵌套。
> `parse_toc.py` 当前的启发式（顶级章节"Function blocks"/"Functions"）在 TF 文档上**可能解析不到条目**——/discover 跑这些库时需要先验证 TOC 结构再继续。

## ❌ 不可达（1）

| 库 | 原因 |
|---|---|
| Tc2_KNXLib | 公开下载站无对应 PDF（试过 `TF8030_TC3_KNX_EN.pdf`、`TF8030_TC3_KNX_TPUART_EN.pdf` 等均 404）。InfoSys 在线手册存在但 SPA 抓不到。需要用户提供 PDF。 |

## 后续

- catalog 中标 ❌ 的 18 个库可改回 ⏳ pending（PDF 已可达），但需在 doc-shard 前抽样验证 TOC 解析
- Tc2_KNXLib 保持 ❌ unavailable
