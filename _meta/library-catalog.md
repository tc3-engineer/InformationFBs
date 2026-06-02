# Beckhoff TwinCAT 3 PLC 库总目录

> URL 规则：`https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_<NAME>_EN.pdf`
> InfoSys：`https://infosys.beckhoff.com/content/1033/tcplclib_<lowercase_name>/`

## 状态字段

- ⏳ pending — 已知但未启动
- 🔍 discovered — `/discover` 已完成，等 `/doc-shard`
- 🚧 in_progress — 部分 doc-shard 已生成
- ✅ done — 全部条目 verified
- ❌ unavailable — 标准 PDF URL 404（详见 [`preflight-2026-05-10.md`](preflight-2026-05-10.md) 与 [`blocked.md`](blocked.md)）

## Pre-flight 摘要（2026-05-10，含 URL 别名）

40/41 库 PDF 可达：22 走标准 URL 模式，18 走 `URL_ALIASES`（TF 系列产品手册）。仅 Tc2_KNXLib ❌（TF8030 KNX 公开站无 PDF）。详见 [`preflight-2026-05-10.md`](preflight-2026-05-10.md)。

> ⚠️ TF 文档结构与 PLC Library 不同，doc-shard 前需先抽样确认 `parse_toc.py` 适用。

---

## Tier 1 · 基础（必备）

| 库 | InfoSys 版本 | 估算 FB+FC | 状态 | 备注 |
|---|---|---|---|---|
| Tc2_Standard | 1.3.4 | 32 | ✅ done (32/32) | IEC 61131-3 标准 POU + 库版本常量 |
| Tc2_System | 1.17.3 | 79 | ✅ done (79/79) | ADS、文件、任务、时间、字符串、EventLogger 接入 |
| Tc2_Utilities | 2.18.2 | 344 | ✅ done (344/344) | 通用工具（97 FB + 1 OO parent + 245 FC + 1 GVL） |
| Tc2_Math | 1.3.3 | 9 | ✅ done (9/9) | 取整 / 模运算（无矩阵/统计/滤波；那些在 Tc3_Controller） |
| Tc3_EventLogger | 1.6.2 | 74 | ✅ done (74/74) | 事件/报警分发（7 OO parent + 66 method + 1 standalone FB） |

## Tier 2 · 运动控制

| 库 | InfoSys 版本 | 估算 FB+FC | 状态 | 备注 |
|---|---|---|---|---|
| Tc2_MC2 | 2.17.0 | 22 (single-axis subset) | ✅ done (22/22) | PLCopen 单轴运动；多轴 / Cam / FlyingSaw 见 Tc2_MC2_Drive 及 Tc3_McCoordinatedMotion |
| Tc2_MC2_Drive | 1.14.2 | 29 | ✅ done (29/29) | SoE 驱动器接入 |
| Tc2_NC | — | 0 (stub) | ⚠️ no-plc-api | 仅 AXIS_REF / PTP 数据结构，无独立 PLC FB；NC 控制 FB 已在 Tc2_MC2 / Tc2_NcDrive / Tc2_NCI 中（详见 blocked.md） |
| Tc2_NcDrive | 现行 | 6 | ✅ done (6/6) | NC 驱动器 wrapper |
| Tc2_Drive | 现行 | 12 | ✅ done (12/12) | SoE 驱动器底层 |

## Tier 3 · 通信

| 库 | InfoSys 版本 | 估算 FB+FC | 状态 | 备注 |
|---|---|---|---|---|
| Tc2_EtherCAT | 现行 | ~80 | ⏳ pending | EtherCAT 主从配置 |
| Tc2_TcpIp | 1.5.2 | 24 | ✅ done (24/24) | TF6310 TCP/UDP/TLS socket（19 FB + 4 FC + 1 GVL；9 DUT 仅引用） |
| Tc2_SerialCom | 1.8.1 | 24 | ✅ done (24/24) | 串口通信 FB（收发/配置/后台通信/3964R+RK512）+ FC（ASC/CHR/错误转换）+ 版本 GVL；TF6340 |
| Tc2_ModbusSrv | 1.6.4 | 21 | ✅ done (21/21) | Modbus TCP/UDP 主站读写 FB（10 TCP + 10 UDP + 版本 GVL；TF6250；从站服务端走配置器+ADS 非本库 FB） |
| Tc2_ModbusRTU | 1.4.3 | 12 | ✅ done (12/12) | Modbus RTU 主站/从站 FB（V2 主站×4 + 从站×4 硬件变体 + 3 obsolete + 版本 GVL；TF6255） |
| Tc2_EthernetIP | — | 0 (stub) | ⚠️ no-plc-api | TF6280 EtherNet/IP Adapter 是配置型产品：PDF 0 个 FB_、无 PLC API 章节；适配器在 XAE 中配置，无独立 PLC 库 FB（同 Tc2_NC，详见 blocked.md） |
| Tc2_IoFunctions | 现行 | 68 | ✅ done (68/68) | KL/EL 端子配置（含 ASI、AX2000、Lightbus、UPS、CANopen、DPV1、SERCOS 等） |
| Tc2_ProfinetDiag | 1.0.2 | 27 | ✅ done (27/27) | PROFINET 控制器/设备诊断 + I&M + 端口诊断 FB（1 个 FB_PN_SCAN_UpTo255 较新未上 InfoSys） |

## Tier 4 · 数据与诊断

| 库 | InfoSys 版本 | 估算 FB+FC | 状态 | 备注 |
|---|---|---|---|---|
| Tc3_JsonXml | 1.14.2 | ~50 | ⏳ pending | JSON/XML SAX+DOM |
| Tc2_DataExchange | 1.2.2 | 3 | ✅ done (3/3) | 跨 PLC watchdog 数据交换 |
| Tc3_Database | 现行 | ~30 | ⏳ pending | 数据库访问（走 TF6420 别名） |
| Tc2_Database | 现行 | ~30 | ⏳ pending | 旧版数据库（走 TS6420 TwinCAT 2 路径别名） |
| Tc2_Filter | 1.8.0 | 15 | ✅ done (15/15) | 数字滤波 FB（PT1/PT2/Notch/LeadLag/Median/Gaussian 等；TF3680；无 GVL/FC，用 EventLogger 报错） |
| Tc2_SUPS | 1.5.2 | 7 | ✅ done (7/7) | 1-second UPS 控制（多硬件平台） |

## Tier 5 · 领域专用（按需选）

| 库 | 估算 FB+FC | 状态 | 适用场景 |
|---|---|---|---|
| Tc3_OPCUA / Tc3_IotBase | ~50 | ⏳ pending | 对外 IT 集成 |
| Tc3_PackML_V2 / V3 | ~30 | ⏳ pending | 包装机械 OMAC |
| Tc2_MC2_Camming | 6 | ✅ done (6/6) | 凸轮（走 TF5050 别名） |
| Tc2_MC2_FlyingSaw | 4 | ✅ done (4/4) | 飞剪（走 TF5055 别名） |
| Tc3_DriveMotionControl | 14 ✅ done (13 FB + 1 GVL, v1.5.5) | ✅ done | 简化伺服（MC_* 单轴运动，无 BufferMode，走 ST_*Options） |
| Tc2_NCI | ~30 | ⏳ pending | 插补 / CNC（走 TF5100 别名） |
| Tc3_MC2_AdvancedHoming | 1.7.7 | 16 | ✅ done (16/16) | 自定义回零（PLCopen Part 5；收尾 3 + 被动 flying 3 + step 10） |
| Tc3_Vision | ~80 | ⏳ pending | 机器视觉 TF7xxx（走 TF7000-TF7810 别名） |
| Tc2_Hydraulic | ~40 | ⏳ pending | 液压闭环（走 TF5810 别名） |
| Tc2_BACnet | ~30 | ⏳ pending | 楼宇自动化（走 TF8020 别名） |
| Tc2_DALI | ~30 | ⏳ pending | 照明总线 |
| Tc2_DMX | 34 ✅ done (34 FB, v1.8.1) | ✅ done | 舞台灯光 DMX512/RDM（主站/发现/RDM 参数/状态/EL6851；含 1 outdated FB） |
| Tc2_KNXLib | ~30 | ❌ unavailable | KNX/EIB（PDF 404） |
| Tc2_EIB | ~20 | ⏳ pending | EIB（旧 KNX） |
| Tc2_EnOcean | ~20 | ⏳ pending | 无线传感 |
| Tc3_BA2 | ~200 | ⏳ pending | Building Automation 2.0（走 Tc3_BA2_Common 别名） |
| Tc2_HVAC | ~50 | ⏳ pending | 暖通（走 TF8000 别名） |
| Tc2_Lighting | ~30 | ⏳ pending | 照明控制（走 TF8050 别名） |
| Tc2_Coupler | 7 | ✅ done (7/7) | 老式 BK 耦合器（含 1 个 obsolete FC） |

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
