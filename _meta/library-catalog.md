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
| Tc2_EtherCAT | 109 ✅ done (v1.9.5) | ✅ done | EtherCAT 主从配置 + 诊断 + 状态机 + ADS/CoE/FoE/SoE/转换/Distributed Clocks (63 FB + 46 FC，含 21 obsolete) |
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
| Tc3_JsonXml | 1.14.2 | 337 | ✅ done (337/337) | JSON/XML SAX+DOM(8 FB + 327 method + 2 INTERFACE)。仓内单库最大体量。 |
| Tc2_DataExchange | 1.2.2 | 3 | ✅ done (3/3) | 跨 PLC watchdog 数据交换 |
| Tc3_Database | 27 ✅ done (v1.14.1) | ✅ done | TF6420 现代数据库访问（16 主 FB + 10 obsolete + 1 GVL）。覆盖 Configure/PLC-Expert/SQL-Expert/NoSQL 四种 mode + Mongo/DocDB/TimeSeries 适配。 |
| Tc2_Database | 26 ✅ done (v1.2) | ✅ done | 旧版数据库 TS6420（19 FB + 5 obsolete + 1 FC + 1 GVL）。InfoSys 走 TF6420 TC3 兼容路径。 |
| Tc2_Filter | 1.8.0 | 15 | ✅ done (15/15) | 数字滤波 FB（PT1/PT2/Notch/LeadLag/Median/Gaussian 等；TF3680；无 GVL/FC，用 EventLogger 报错） |
| Tc2_SUPS | 1.5.2 | 7 | ✅ done (7/7) | 1-second UPS 控制（多硬件平台） |

## Tier 5 · 领域专用（按需选）

| 库 | 估算 FB+FC | 状态 | 适用场景 |
|---|---|---|---|
| Tc3_OPCUA / Tc3_IotBase | ~50 | ⏳ pending | 对外 IT 集成 |
| Tc3_PackML_V2 | 25 ✅ done (v1.2.4) | ✅ done | OMAC PackML 包装机械（3 接口 + 5 FB + 9 PML_AdminAlarm 方法 + 8 转换 FC） |
| Tc3_PackML_V3 | 32 ✅ done (v1.0.0, 2025-08-25) | ✅ done | OMAC PackML V3 升级版（2 接口 + 5 FB + 17 PMLAdminAlarm 方法 + 8 转换 FC）。FB_PML* 命名前缀；Alarm 方法 9→17 扩展；StopReason 容器从数组改单值。28/32 ⚠️ not-on-infosys（库新发布,InfoSys 公网索引尚未完整）。 |
| Tc2_MC2_Camming | 6 | ✅ done (6/6) | 凸轮（走 TF5050 别名） |
| Tc2_MC2_FlyingSaw | 4 | ✅ done (4/4) | 飞剪（走 TF5055 别名） |
| Tc3_DriveMotionControl | 14 ✅ done (13 FB + 1 GVL, v1.5.5) | ✅ done | 简化伺服（MC_* 单轴运动，无 BufferMode，走 ST_*Options） |
| Tc2_NCI | 101 ✅ done (v2.15.1) | ✅ done | 插补 / CNC TF5100（76 FB + 25 FC,分 configuration / nci_pous / blocksearch / retrace / parts_program_generator / compatibility / obsolete） |
| Tc3_MC2_AdvancedHoming | 1.7.7 | 16 | ✅ done (16/16) | 自定义回零（PLCopen Part 5；收尾 3 + 被动 flying 3 + step 10） |
| Tc3_Vision | ~80 | ⏳ pending | 机器视觉 TF7xxx（走 TF7000-TF7810 别名） |
| Tc2_Hydraulic | 33 ✅ done user-facing (v1.8.3) | ✅ done | 液压闭环 TF5810；33 个用户面 FB(管理/单轴运动/多轴/归零/控制器/压力力反馈)。PDF 另含 ~67 个 _BkPlcMc internal-use FB（StandardBody/Generator/AdsCommServer 等模板内部调用），按 PDF 自身"internal use only/not recommended"标注未单独成篇 |
| Tc2_BACnet | 53 ✅ done (v1.1.2 / Tc3_BACnetRev14) | ✅ done | TF8020；7 基础架构 FB/GVL（Wave-2）+ 24 对象 FB 类（objects/）+ 6 Primitive Value 类 + 14 Client/RM FB + 2 服务端 RP/WP（Wave-3）。对象类型每篇覆盖该类型全部后缀变体（_IO/_ECAT/_Raw/_5P 等）。41 篇 `chapter-overview-only` + 5 篇 `infer-from-naming-convention`（PDF 不按"每 FB 一节"展开,verify_doc 走合规旁路）。 |
| Tc2_DALI | ~30 | ⏳ pending | 照明总线 |
| Tc2_DMX | 34 ✅ done (34 FB, v1.8.1) | ✅ done | 舞台灯光 DMX512/RDM（主站/发现/RDM 参数/状态/EL6851；含 1 outdated FB） |
| Tc2_KNXLib | ~30 | ❌ unavailable | KNX/EIB（PDF 404） |
| Tc2_EIB | 48 ✅ done (v1.16.1) | ✅ done | EIB（旧 KNX）— KL6301 耦合器接入 + 15 个 receive FB + 29 个 send FB + 2 个地址转换 FC |
| Tc2_EnOcean | 20 ✅ done (v1.7.1) | ✅ done | 无线传感（KL6021-0023 / KL6581 终端 + receive/send/teach-in + 字节转换 FC） |
| Tc3_BA2_Common | 80 ✅ done (v1.0.2) | ✅ done | Building Automation 2.0 公用底座（9 FB + 68 FC + 3 GVL）。控制器/IO/触发/斜坡滤波/迟滞/持久化/比较/内存/枚举/时间/调度/趋势/日志 等 19 类 |
| Tc2_HVAC | 135 ✅ done (v1.3.0) | ✅ done | TF8000 暖通空调(131 FB + 2 FC + 2 GVL,15 类:actuators/controllers/sensors/sequence/scheduler/room_*/...)。全 135 篇 chapter-overview-only(PDF VAR 块无 END_VAR 终止符;字段已逐字搬运)。 |
| Tc2_Lighting | — | 0 (stub) | ⚠️ application-package | TF8050 是预配置 Lighting Solution **应用包**(BA_LS + BA_LS_Dali_Communication 两个 PROGRAM POU + 参数表),非 PLC 库 FB API 范式。实际 DALI 总线 FB 由 Tc2_DALI 提供。详见 blocked.md。 |
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
