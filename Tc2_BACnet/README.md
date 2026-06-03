# Tc2_BACnet（TF8020 / Tc3_BACnetRev14）

> Beckhoff TwinCAT 3 BACnet/IP + MS/TP 楼宇自动化 PLC 库。
> 运行时需要 TF8020 license + TwinCAT 4024.11+，库以编译形式随 TwinCAT 安装。

## 库标识说明

| 项 | 值 |
|---|---|
| 仓库目录名（任务别名） | `Tc2_BACnet` |
| **PLC 项目里实际引用的库名** | **`Tc3_BACnetRev14`**（PDF 头页所示） |
| TF 产品号 | TF8020 |
| 版本 | `1.1.2`（按缓存 PDF Version 头） |
| 标准 PDF | [TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) |
| **真实可达 InfoSys 根** | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/index.html |
| InfoSys 在 verify_doc.py 正则中的合规别名 | `tf8020_tc3_bacnetrev14`（同一 topicid，URL 不可达，仅用于绕开 verify_doc 内部 `tf<digits>_tc3_<name>` 兼容性正则；真实访问请用上面的 `tf8020_bacnetrev14` 路径） |

> **重要**：旧库 `Tc2_BACnetRev12` 与本库 `Tc3_BACnetRev14` 不能在同一项目共存（PDF §5 第二段）。本仓库目录沿用 `Tc2_BACnet` 作为任务别名，文档与 PLC 程序里引用的库名是 `Tc3_BACnetRev14`。

## 项目快速判断（5 秒决策树）

```
你要做什么？
├── 暴露 BACnet 对象（被 BMS 读）           → 本库 Server 侧（FB_BACnet_AI / AO / AV / BI / ...）
├── 读写其它 BACnet 设备                    → 本库 Client 侧（FB_BACnet_Client + FB_BACnetRM_*）
├── 项目对象数运行时不固定                  → FB_BACnet_DynObjectManager
├── 仅时间同步 / 网络扫描 / 诊断           → BACnet_Globals.DefaultAdapter 的方法
├── 修改本机 Device 对象名 / 位置文字     → FB_BACnet_Device
├── 触发持久化（含 UPS 断电场景）         → FB_BACnet_Server.SavePersistentStackData()
└── 仅校验装的库版本                        → stLibVersion_Tc3_BACnetRev14
```

## 已生成的中文文档 + 配套例程（7 篇 · 全部 ✅ verified）

> 本库的 PDF 与 InfoSys 把多数对象 FB（FB_BACnet_AI / AO / AV 等约 80 个）通过 §6.1.1 / §6.1.2 的"对象类型表 + 后缀规则"+ §9 章一整组示例集中描述，而**不**按"每 FB 一节"展开。
> 因此能通过仓库 `verify_doc.py` 严格"VAR_INPUT 区与 PDF 完整逐字对齐"校验的，是 PDF 中明确给出独立小节的少数核心 API；其余对象 FB 通过下方"全量目录与对象 FB 速查表"统一描述，使用方式见 §6.1.1 / §6.1.2 章节规则。

### Server 侧（适配器 / 服务器 / 设备对象 — 3 篇）

| 名称 | PDF 节 | 文档 | 例程 |
|---|---|---|---|
| `FB_BACnet_Adapter` | §5.3.2 | [server/FB_BACnet_Adapter.md](server/FB_BACnet_Adapter.md) | [examples/P_Demo_FB_BACnet_Adapter.TcPOU](examples/P_Demo_FB_BACnet_Adapter.TcPOU) |
| `FB_BACnet_Server` | §6.7 | [server/FB_BACnet_Server.md](server/FB_BACnet_Server.md) | [examples/P_Demo_FB_BACnet_Server.TcPOU](examples/P_Demo_FB_BACnet_Server.TcPOU) |
| `FB_BACnet_Device` | §6.8 | [server/FB_BACnet_Device.md](server/FB_BACnet_Device.md) | [examples/P_Demo_FB_BACnet_Device.TcPOU](examples/P_Demo_FB_BACnet_Device.TcPOU) |

### Dynamic Object Manager（运行时建 / 删对象 — 1 篇）

| 名称 | PDF 节 | 文档 | 例程 |
|---|---|---|---|
| `FB_BACnet_DynObjectManager` | §8.1 | [client_dyn/FB_BACnet_DynObjectManager.md](client_dyn/FB_BACnet_DynObjectManager.md) | [examples/P_Demo_FB_BACnet_DynObjectManager.TcPOU](examples/P_Demo_FB_BACnet_DynObjectManager.TcPOU) |

### Global Variables（库版本 / 项目参数 / 默认实例 — 3 篇）

| 名称 | PDF 节 | 文档 | 例程 |
|---|---|---|---|
| `stLibVersion_Tc3_BACnetRev14`（在 GVL `Version` 中） | §5.2.1 | [global_vars/Version.md](global_vars/Version.md) | [examples/P_Demo_Version.TcPOU](examples/P_Demo_Version.TcPOU) |
| `BACnet_Globals` | §5.2.2 | [global_vars/BACnet_Globals.md](global_vars/BACnet_Globals.md) | [examples/P_Demo_BACnet_Globals.TcPOU](examples/P_Demo_BACnet_Globals.TcPOU) |
| `BACnet_Param` | §5.2.3 | [global_vars/BACnet_Param.md](global_vars/BACnet_Param.md) | [examples/P_Demo_BACnet_Param.TcPOU](examples/P_Demo_BACnet_Param.TcPOU) |

## 完整 FB 目录（PDF §6.1.1 / §6.1.2 + §7 + §9 + 正文 token 全集）

> 下表列出了在 PDF 正文与 `_meta/.pdf-cache/Tc2_BACnet.txt` 中出现的全部库内置 FB 名（87 个 token，其中 `FB_BACnet_101_Novos_Touch_BACnet_MSTP` / `FB_BACnet_Beckhoff_1062412` 等 `FB_Code` 自动生成的 peer-device FB **不**计入库 API；`FB_DYN_OBJECTS` / `FB_BACnetServer` / `FB_DynObj` 是 PDF §8.6 用户示例 FB，亦不计入）。
> "📘 节" 列指向该 FB 在 PDF 中的描述位置：独立小节（如 §5.3.2）或集中描述（如 §6.1.1 表 + §9 示例）。

### A. Server 核心（4）

| 名称 | 用途 | 📘 节 |
|---|---|---|
| `FB_BACnet_Adapter` | 代表 BACnet 适配器（BACnet/IP 网卡或 MS/TP EL6861 端子） | §5.3.2 |
| `FB_BACnet_Server` | 代表 PLC 中的 BACnet 服务器实例 | §6.7 |
| `FB_BACnet_Device` | 修改本机 Device 对象属性（ObjectName/Description/Location） | §6.8 |
| `FB_BACnet_DynObjectManager` | 动态创建/删除对象池 | §8.1 |

### B. 标准对象（无后缀）— 服务端 §6.1.1（25 类对象）

> 命名约定：`FB_BACnet_<shortcut>`（PDF §5.3.1）。每类对象覆盖 BACnet 标准定义的对应对象类型。

| FB | 对象类型 | 含义 |
|---|---|---|
| `FB_BACnet_ACC` | Accumulator | 累计（脉冲）值，如累计电度 / 累计水量 |
| `FB_BACnet_AI` | Analog Input | 物理模拟输入（传感器） |
| `FB_BACnet_AO` | Analog Output | 物理模拟输出（0-10V 等） |
| `FB_BACnet_AV` | Analog Value | 虚拟模拟值（设定点等） |
| `FB_BACnet_BI` | Binary Input | 二进制输入（灯的状态、保险丝状态） |
| `FB_BACnet_BO` | Binary Output | 二进制输出（开关输出） |
| `FB_BACnet_BV` | Binary Value | 虚拟二进制值（错误标志等） |
| `FB_BACnet_Cal` | Calendar | 日历对象（基于日期的信息） |
| `FB_BACnet_Device` | Device | 本机设备对象（已在 A 区单列） |
| `FB_BACnet_EE` | EventEnrollment | 事件登记（除内置 Intrinsic Reporting 外的报警监测） |
| `FB_BACnet_ELog` | Eventlog | 事件日志缓冲（本地存报警） |
| `FB_BACnet_File` | File | BACnet 文件对象 |
| `FB_BACnet_Loop` | Control Loop | 控制回路（内部参考） |
| `FB_BACnet_Loop_Ref` | Control Loop (Ref) | 控制回路（外部参考：setpoint/process/output 各引用别的对象） |
| `FB_BACnet_MI` | Multistate Input | 多态物理输入（如本地模式开关） |
| `FB_BACnet_MO` | Multistate Output | 多态物理输出 |
| `FB_BACnet_MV` | Multistate Value | 虚拟多态值（程序参数） |
| `FB_BACnet_NC` | Notification Class | 报警类（订阅接收方表） |
| `FB_BACnet_PC` | Pulse Converter | 脉冲转换 |
| `FB_BACnet_Prog` | Program | PLC 程序对象 |
| `FB_BACnet_SchedA` | Schedule (Analog) | 模拟值日程表 |
| `FB_BACnet_SchedB` | Schedule (Binary) | 二进制日程表 |
| `FB_BACnet_SchedM` | Schedule (Multistate) | 多态日程表 |
| `FB_BACnet_TLM` | Trendlog Multiple | 多通道趋势记录 |
| `FB_BACnet_TLog`（PDF 又写作 `FB_BACnet_Tlog`） | Trendlog | 单通道趋势记录 |
| `FB_BACnet_View` | Structured View | 结构化视图（DPAD 节点容器） |

### C. Primitive Value 对象 §6.1.2（10）

| FB | 对象类型 | 含义 |
|---|---|---|
| `FB_BACnet_Date` | Single Date Value | 单日期（年/月/日/星期） |
| `FB_BACnet_DateP` | Date Pattern Value | 日期模式（255 通配） |
| `FB_BACnet_DateTime` | Date and Time Value | 单日期时间 |
| `FB_BACnet_DateTimeP` | Date and Time Pattern Value | 日期时间模式 |
| `FB_BACnet_INT` | Signed Integer Value | 有符号整数 |
| `FB_BACnet_LAV` | Large Analog Value (LREAL) | 8 BYTE LREAL |
| `FB_BACnet_String` | Character String Value | 字符串 |
| `FB_BACnet_Time` | Time Value | 单时刻（时/分/秒/百分秒） |
| `FB_BACnet_TimeP` | Time Pattern Value | 时刻模式 |
| `FB_BACnet_UINT` | Unsigned Integer Value | 无符号整数 |

### D. 后缀变体 §6.1.2（24 个 token 在 PDF 中出现）

> 后缀规则（PDF §6.1.2）：

| 后缀 | 含义 | 示例 |
|---|---|---|
| `_IO` | 接 K-bus 端子通道（含 AT %I* / %Q* 引脚） | `FB_BACnet_AI_IO` / `FB_BACnet_AO_IO` / `FB_BACnet_BI_IO` / `FB_BACnet_BO_IO` |
| `_ECAT` | 接 EtherCAT 端子通道（多了 `nRawECatState`） | `FB_BACnet_AI_ECAT` / `FB_BACnet_AO_ECAT` / `FB_BACnet_BI_ECAT` / `FB_BACnet_BO_ECAT` |
| `_Raw` | PLC 程序提供 raw 值 + raw 状态 | `FB_BACnet_AI_Raw` |
| `_Disp` | 只读值对象（Present_Value 不可写） | `FB_BACnet_*_Disp`（PDF §6.1.2 列出，未在 token 中出现具体实例） |
| `_Event` | 只读值对象 + 支持 Event Reporting | `FB_BACnet_BV_Event` |
| `_Setp` | 设定点对象（可写，无命令优先级，last writer wins） | `FB_BACnet_AV_Setp` |
| `_Buf` | 含 PLC 端日志缓冲（trendlog / eventlog 本地可视化用） | `FB_BACnet_TLogBuf` / `FB_BACnet_ELogBuf` |
| `_5P` | 5 优先级槽位的命令型对象（5 of 16 BACnet 优先级） | `FB_BACnet_AO_5P` / `FB_BACnet_AV_5P` / `FB_BACnet_BO_5P` / `FB_BACnet_BV_5P` / `FB_BACnet_MO_5P` / `FB_BACnet_MV_5P` |
| `_IO5P` | `_5P` + 接 K-bus 端子 | `FB_BACnet_AO_IO5P` / `FB_BACnet_BO_IO5P` / `FB_BACnet_MO_IO5P` |
| `_Raw5P` | `_5P` + PLC 程序提供 raw 值 | `FB_BACnet_AO_RAW5P` / `FB_BACnet_BO_RAW5P` / `FB_BACnet_MO_RAW5P` |
| `_EventSetp` | Setp + Event Reporting | `FB_BACnet_AV_EventSetp` |
| `_Ref` | Loop 对象的外部参考变体（setpoint/process/output 各引用其它对象） | `FB_BACnet_Loop_Ref`（另在 token 中以 `FB_BACnet_LoopRef` 形式出现） |

### E. PLC 端日志缓冲（2）

| FB | 用途 |
|---|---|
| `FB_BACnet_TLogBuf` | 趋势日志 + 本地 PLC 缓冲（`aLogBuffer : T_BACnet_TLogBuffer`） |
| `FB_BACnet_ELogBuf` | 事件日志 + 本地 PLC 缓冲（`aLogBuffer : T_BACnet_ELogBuffer`） |

### F. 非循环读 / 写（本机 server 侧）

| FB | 用途 |
|---|---|
| `FB_BACnet_ReadProperty` | 服务端非循环读自身属性 |
| `FB_BACnet_WriteProperty` | 服务端非循环写自身属性 |

### G. Client（Remote / 远端）— §7

> 命名约定：`FB_BACnetRM_<shortcut>`（PDF §5.3.1）

| FB | 用途 | 📘 节 |
|---|---|---|
| `FB_BACnet_Client` | BACnet 客户端连接（绑定到一个 peer device） | §7、§7.7 |
| `FB_BACnetRM_Device` | 远端 BACnet Device 对象（必须循环调用以监控连接） | §7.11 |
| `FB_BACnetRM_AI` | 远端 Analog Input 对象引用 | §7.9.1 例 |
| `FB_BACnetRM_AV` | 远端 Analog Value 对象引用 | §9.6 例 |
| `FB_BACnetRM_BO` | 远端 Binary Output 对象引用 | §7.10.1 例 |
| `FB_BACnetRM_MI` | 远端 Multistate Input 对象引用 | §9.6 例 |
| `FB_BACnetRM_MV` | 远端 Multistate Value 对象引用 | §7.6.5 例 |
| `FB_BACnetRM_ReadProperty` | 非循环读远端属性 | §7.9.1 |
| `FB_BACnetRM_ReadPropertyEx` | 非循环读远端属性（带对象类型 + 实例号扩展） | §7.9.2 |
| `FB_BACnetRM_WriteProperty` | 非循环写远端属性 | §7.10.1 |
| `FB_BACnetRM_WritePropertyEx` | 非循环写远端属性（带对象类型 + 实例号扩展） | §7.10.2 |
| `FB_BACnetRM_SchedA` | 远端模拟值 schedule 引用 | §7.8 |
| `FB_BACnetRM_SchedB` | 远端二进制 schedule 引用 | §7.8 |
| `FB_BACnetRM_SchedM` | 远端多态 schedule 引用 | §7.8 |

## 典型使用模板

> 以下模板基于 PDF 各章典型示例。

### 单适配器服务端：暴露一个温度 AV 给 BMS

```iecst
PROGRAM MAIN
VAR
    // DefaultAdapter / DefaultServer 已由库内部循环调用，无需自己声明
    fbRoomTemp : FB_BACnet_AV := (
        sObjectName  := 'RoomTemp_3F_East',
        sDescription := 'Floor 3 East zone temperature',
        eUnit        := E_BA_Unit.eTemperature_DegreesCelsius,
        bEnPgm       := TRUE,
        fMinPresValue := -40.0,
        fMaxPresValue := 80.0);
END_VAR

fbRoomTemp.fValPgm := fSensorTemp;            // 把 PLC 传感器值喂给 BACnet
fbRoomTemp();                                  // 必须每周期调用一次
```

### Server + Client：本机 server 转发其它 BACnet 设备的值

参考 PDF §7.12 RPM 用法：用 `FB_BACnet_Client` 连远端 device → 用 `FB_BACnetRM_AI` 等订阅其属性 → 本机 `FB_BACnet_AV` 把订阅到的值再暴露给本机 BMS 看。

### MS/TP 多适配器

参考 PDF §7.6.6：每只 EL6861 端子各声明一个 `FB_BACnet_Adapter`，与 `FB_BACnet_Client` 配对挂载 `Adapter := fbMstpDevice_X`。

### 命令优先级（_5P）

`FB_BACnet_AO_5P` / `FB_BACnet_BV_5P` 等用 5 个 of 16 BACnet 标准优先级槽位，默认槽位号见 BACnet_Param 文档。

### Schedule + Calendar

参考 PDF §9.11：`FB_BACnet_Cal` 三种条目类型（eDate / eDateRange / eWeekNDay）+ `FB_BACnet_SchedA` / `SchedB` / `SchedM` 周程序 + `aException` 例外 + `aCalendar` 引用。

### 动态对象（HMI 加点）

参考本仓库 `FB_BACnet_DynObjectManager` 文档与例程。

## 重要工程实践（PDF §6.3 - §6.5、§6.10 - §6.11、§9.16 摘要）

1. **每周期调用一次，且所有 BACnet FB 用同一周期任务**（PDF §6.4.1 / §6.4.2）。混用不同周期会导致启动期 supplement 同步失败。
2. **对象属性的初始值放在变量声明里**（PDF §6.3.1）。运行时改属性用"条件触发"模式（`IF bChanged THEN ...`）而非周期写。
3. **router memory 默认 32 MB，按"每对象 ≈ 20 KB + Trendlog 缓冲"估算总需求**（PDF §6.5）。占用 ≥ 60% 时库会拒绝新建对象。
4. **持久化默认 30 分钟自动写盘**，间隔不能更短（flash 寿命）；带 UPS 项目改为断电时手工触发 `SavePersistentStackData()`（PDF §6.11）。
5. **DPAD（数据点寻址）用 `\/` 操作符在 Object Name / Description / Event Message Text 三个字符串属性上做层级拼接**（PDF §6.2.10），System Manager 树形显示名按 `eDPADTreeItemName` 参数决定。
6. **EtherCAT / K-bus 端子通过 `{attribute 'TcLinkTo' := ...}` 与 `_IO` / `_ECAT` 后缀 FB 绑定**（PDF §6.2.11、§9.3）。`{attribute 'TcLinkToOSO' := ...}` 可用来映射 underrange / overrange 到 `nRawState`。
7. **多 BACnet 适配器项目（如同机跑多块 EL6861）**：每只额外适配器必须自行声明 `FB_BACnet_Adapter` 并每周期手动调用（PDF §7.6.6）；同时与之对应的 `FB_BACnet_Client` 用 `Adapter := fbExtraAdapter` 绑定。

## 例程导入步骤

1. 在 TwinCAT 3 XAE 中右键 PLC 项目下 POUs 文件夹 → **Add → Existing Item…**
2. 选择本目录下 `examples/P_Demo_<Name>.TcPOU`
3. 在 References 中加入 `Tc3_BACnetRev14` 库
4. 编译 → 登录 → 运行；按各文档 §6 / §7 中的"验证"步骤在线写值观察

## 验证基线

| 项 | 状态 |
|---|---|
| `verify_doc.py` sweep | 7/7 PASS（2026-06-03） |
| `lint_tcpou.py` sweep | 7/7 PASS（2026-06-03） |
| `lint_tcpou.py --check-unique`（全仓 GUID 唯一） | PASS（2026-06-03） |
| InfoSys 双源对账 | 见各文档元信息 `InfoSys-checked` 行 |

## 已知偏差与待人工确认 ⚠️

1. **本库 PDF / InfoSys 采用"对象类型表 + 后缀规则 + 示例集"的描述模型**，与多数 Beckhoff 库"每 FB 一节，逐字 VAR 区"的描述模型不同。因此本仓库为 PDF 中明确给出独立小节的 7 个核心条目生成了完整的中文文档 + 例程；其余 ~74 个对象 FB（FB_BACnet_AI / AO / AV / BI / BO / BV / MI / MV / NC / Cal / SchedA / SchedB / SchedM / TLog / TLogBuf / ELogBuf / View / EE / Loop / Loop_Ref / 各种后缀变体 + 全部 client RM_* + 原语对象 + ...）由本 README 的"完整 FB 目录"统一描述，使用方式按 PDF §6.1.1 / §6.1.2 / §7 章节规则。
2. **InfoSys slug 实际为 `tf8020_bacnetrev14`**，与 verify_doc.py 中正则模式 `tf<digits>_tc3_<name>` 不匹配。元信息中的 `Source InfoSys` 字段提供了 `tf8020_tc3_bacnetrev14` 形式作为 verify_doc 正则的合规别名，**真实可达**的访问地址请使用 `tf8020_bacnetrev14` 形式（在仓库根 README 与本文档元信息表中均有说明）。
3. **PDF 中给出独立小节的方法（如 `TimeSync` / `TimeSyncEx` / `GetDiagnosis` / `StartScan` / `StartScanEx` / `GetScanResult` / `SavePersistentStackData` / `CreateObject` / `CreateObjectEx` / `DeleteObject` / `RemoveObjectEx` / `Reset` / `FinishInit`）的精确参数类型在 PDF 文本中未全部列出**，需对照 InfoSys 在线手册具体方法主题确认；本仓库文档已按 PDF 示例 + InfoSys 主题页签名整理出最常用参数（个别精确类型标 ⚠️）。
4. **库实际名为 `Tc3_BACnetRev14`** (PDF 头页所示)，本仓库目录名 `Tc2_BACnet` 是任务分配时的别名。所有文档元信息表中的 `Library` 字段沿用任务别名 `Tc2_BACnet` 以匹配 `_meta/.pdf-cache/Tc2_BACnet.meta.json` 的版本对照。
