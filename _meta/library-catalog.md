# Beckhoff TwinCAT 3 PLC 库总目录

> URL 规则：`https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_<NAME>_EN.pdf`
> InfoSys：`https://infosys.beckhoff.com/content/1033/tcplclib_<lowercase_name>/`

## 状态字段

- ⏳ pending — 已知但未启动
- 🔍 discovered — `/discover` 已完成，等 `/doc-shard`
- 🚧 in_progress — 部分 doc-shard 已生成
- ✅ done — 全部条目 verified
- ❌ unavailable — 标准 PDF URL 404（详见 [`preflight-2026-05-10.md`](preflight-2026-05-10.md) 与 [`blocked.md`](blocked.md)）

## Pre-flight 摘要（2026-05-10）

22/41 库标准 PDF URL 可达；19 库 ❌ unavailable。详见 [`preflight-2026-05-10.md`](preflight-2026-05-10.md)。

---

## Tier 1 · 基础（必备）

| 库 | InfoSys 版本 | 估算 FB+FC | 状态 | 备注 |
|---|---|---|---|---|
| Tc2_Standard | 1.3.4 | 31 | ✅ done (31/31) | IEC 61131-3 标准 POU |
| Tc2_System | 1.17.1 | ~150 | ⏳ pending | ADS、文件、任务、时间、字符串、EventLogger 接入 |
| Tc2_Utilities | 现行 | ~50 | ⏳ pending | 通用工具（CRC、转换、调度等） |
| Tc2_Math | 现行 | ~30 | ⏳ pending | 矩阵、统计、滤波数学 |
| Tc3_EventLogger | 1.6.2 | ~20 | ⏳ pending | 事件/报警分发 |

## Tier 2 · 运动控制

| 库 | InfoSys 版本 | 估算 FB+FC | 状态 | 备注 |
|---|---|---|---|---|
| Tc2_MC2 | 2.17.0 | ~80 | ⏳ pending | PLCopen 单/多轴 |
| Tc2_MC2_Drive | 1.14.2 | ~30 | ⏳ pending | SoE 驱动器接入 |
| Tc2_NC | 现行 | ~30 | ❌ unavailable | NC PTP 底层（PDF 404，见 blocked.md） |
| Tc2_NcDrive | 现行 | ~30 | ⏳ pending | NC 驱动器 wrapper |
| Tc2_Drive | 现行 | ~30 | ⏳ pending | SoE 驱动器底层 |

## Tier 3 · 通信

| 库 | InfoSys 版本 | 估算 FB+FC | 状态 | 备注 |
|---|---|---|---|---|
| Tc2_EtherCAT | 现行 | ~80 | ⏳ pending | EtherCAT 主从配置 |
| Tc2_TcpIp | 现行 | ~30 | ❌ unavailable | Socket TCP/UDP（PDF 404） |
| Tc2_SerialCom | 现行 | ~20 | ❌ unavailable | 串口通信（PDF 404） |
| Tc2_ModbusSrv | 现行 | ~20 | ❌ unavailable | Modbus 服务端（PDF 404） |
| Tc2_ModbusRTU | 现行 | ~20 | ❌ unavailable | Modbus RTU 主站（PDF 404） |
| Tc2_EthernetIP | 现行 | ~30 | ❌ unavailable | EtherNet/IP（PDF 404） |
| Tc2_IoFunctions | 现行 | ~30 | ⏳ pending | KL/EL 端子配置 |
| Tc2_ProfinetDiag | 现行 | ~20 | ⏳ pending | PROFINET 诊断 |

## Tier 4 · 数据与诊断

| 库 | InfoSys 版本 | 估算 FB+FC | 状态 | 备注 |
|---|---|---|---|---|
| Tc3_JsonXml | 1.14.2 | ~50 | ⏳ pending | JSON/XML SAX+DOM |
| Tc2_DataExchange | 现行 | ~20 | ⏳ pending | 跨 PLC 数据交换 |
| Tc3_Database | 现行 | ~30 | ❌ unavailable | 数据库访问（PDF 404） |
| Tc2_Database | 现行 | ~30 | ❌ unavailable | 旧版数据库（PDF 404） |
| Tc2_Filter | 现行 | ~15 | ❌ unavailable | 信号滤波（PDF 404） |
| Tc2_SUPS | 1.5.2 | ~10 | ⏳ pending | 1 秒 UPS 控制 |

## Tier 5 · 领域专用（按需选）

| 库 | 估算 FB+FC | 状态 | 适用场景 |
|---|---|---|---|
| Tc3_OPCUA / Tc3_IotBase | ~50 | ⏳ pending | 对外 IT 集成 |
| Tc3_PackML_V2 / V3 | ~30 | ⏳ pending | 包装机械 OMAC |
| Tc2_MC2_Camming | ~20 | ❌ unavailable | 凸轮（PDF 404） |
| Tc2_MC2_FlyingSaw | ~10 | ❌ unavailable | 飞剪（PDF 404） |
| Tc3_DriveMotionControl | ~20 | ⏳ pending | 简化伺服 |
| Tc2_NCI | ~30 | ❌ unavailable | 插补 / CNC（PDF 404） |
| Tc3_MC2_AdvancedHoming | ~15 | ⏳ pending | 自定义回零 |
| Tc3_Vision | ~80 | ❌ unavailable | 机器视觉 TF7xxx（PDF 404） |
| Tc2_Hydraulic | ~40 | ❌ unavailable | 液压闭环（PDF 404） |
| Tc2_BACnet | ~30 | ❌ unavailable | 楼宇自动化（PDF 404） |
| Tc2_DALI | ~30 | ⏳ pending | 照明总线 |
| Tc2_DMX | ~10 | ⏳ pending | 舞台灯光 |
| Tc2_KNXLib | ~30 | ❌ unavailable | KNX/EIB（PDF 404） |
| Tc2_EIB | ~20 | ⏳ pending | EIB（旧 KNX） |
| Tc2_EnOcean | ~20 | ⏳ pending | 无线传感 |
| Tc3_BA2 | ~200 | ❌ unavailable | Building Automation 2.0（PDF 404） |
| Tc2_HVAC | ~50 | ❌ unavailable | 暖通（PDF 404） |
| Tc2_Lighting | ~30 | ❌ unavailable | 照明控制（PDF 404） |
| Tc2_Coupler | ~10 | ⏳ pending | 老式 BK 耦合器 |

---

## 类别 → 子目录映射（discover 时使用）

| Category（PDF 章节标题原文） | 子目录名 |
|---|---|
| Bistable | `bistable` |
| Counter | `counter` |
| Timer | `timer` |
| Timer (LTIME) | `timer_ltime` |
| Trigger | `trigger` |
| String functions | `string` |
| String functions (WSTRING) | `wstring` |
| ADS function blocks | `ads` |
| Expanded ADS function blocks | `ads_expanded` |
| Function blocks for data access | `data_access` |
| Functions for files | `file` |
| EventLogger | `event_logger` |
| TwinCAT 3 EventLogger | `event_logger` |
| Single axis | `single_axis` |
| Multi-axis | `multi_axis` |
| ... | (新增映射由 /discover 自动追加) |
