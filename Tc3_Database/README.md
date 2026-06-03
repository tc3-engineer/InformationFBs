# Tc3_Database（TF6420 TwinCAT 3 Database Server，现代版）

> Beckhoff TwinCAT 3 Database Server 的现代 PLC API 库（运行时依赖 TF6420 Database Server 服务）。
> 把 PLC 变量与外部数据库（MS SQL / MS Compact / Access / MySQL / PostgreSQL / Oracle / DB2 / Firebird / InterBase / ASCII / XML / MongoDB / InfluxDB / CosmosDB）打通——PLC 端调用本库 FB 完成连接管理、库 / 表创建、Name/Value 与自定义结构读写、SQL 命令执行、存储过程调用、AutoLog 周期采集、NoSQL 文档库 / 时序库读写等。带 Tc3_EventLogger 接口诊断（区别于 Tc2_Database 的裸 `nErrId`）。

## 概览

| 字段 | 值 |
|---|---|
| 库版本 | `1.14.1`（PDF 头部 `Version: 1.14.1`） |
| 库类型 | TwinCAT 3 Function (TF6420) |
| 运行时依赖 | `TF6420 TwinCAT Database Server` 服务（必须安装 TF6420 并启动 Server 进程） |
| 来源 PDF | [tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) |
| InfoSys（Tc3_Database 章入口） | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2668529419.html |
| 文档进度 | 27 / 27（活跃 FB 16 / obsolete FB 10 / GVL 1） |
| 验证基线 | verify_doc 27/27 PASS · lint_tcpou 27/27 PASS · 全仓 `--check-unique` PASS |

## 架构与四种 Mode

Tc3_Database 在 PLC API 层面提供 **四种使用模式**（PDF §6.1.1.1 ~ §6.1.1.4），用户根据场景选择。它们可以在同一 PLC 程序里共存：

1. **Configure mode**（§6.1.1.1）：通过 TF6420 配置器图形界面下发；PLC 端只需 `FB_ConfigTcDBSrvEvt` 管 XML，`FB_PLCDBAutoLogEvt` 控 AutoLog 组。
2. **PLC Expert mode**（§6.1.1.2）：PLC 主动调用 `FB_PLCDB*Evt` 系列做读 / 写 / 建库 / 自由 SQL。每方法自动开关连接。适合中低吞吐 + 业务逻辑驱动场景。
3. **SQL Expert mode**（§6.1.1.3）：手动管理 SQL 长连接 + 自由 SQL（`FB_SQLDatabaseEvt` + `FB_SQLCommandEvt` + `FB_SQLResultEvt` + `FB_SQLStoredProcedureEvt`）。适合高吞吐 + 频繁 SQL 操作场景。
4. **NoSQL Expert mode**（§6.1.1.4）：用 Builder + Executor + Result 三件套访问 MongoDB（文档型）与 InfluxDB / TimescaleDB（时序型）。

所有 16 个活跃 FB 都通过 `ipTcResult : Tc3_EventLogger.I_TcMessage` 暴露错误事件（用 `RequestEventText(nLangId, ...)` 取本地化文本），并通过 `eTraceLevel : TcEventSeverity` 控制事件分级——这是 Tc3_Database 相对 Tc2_Database 的核心升级。

## 性能路径选择

按吞吐量从低到高（与 Tc2 类似但接口现代化）：
- **PLC 主动单条** (`FB_PLCDBCmdEvt.Execute` 自由 SQL / `FB_PLCDBWriteEvt.Write`)：200~500 ms / 条（每次自动连）。事件型、HMI 触发的写 / 读。
- **PLC 主动 + 常驻连接** (`FB_SQLDatabaseEvt.Connect` + `FB_SQLCommandEvt.Execute`)：5~10 ms / 条。高吞吐主动写入。
- **AutoLog Server 端周期** (`FB_PLCDBAutoLogEvt.Start` + 配置好的 AutoLog 组)：批量 INSERT，吞吐最高，PLC 几乎无开销。大量固定变量持续采样首选。
- **NoSQL Expert TimeSeries 批量** (`FB_NoSQLQueryEvt.Execute` + `FB_NoSQLQueryBuilder_TimeSeriesDB` Insert 模式)：单次写 1000+ 点到 InfluxDB / TimescaleDB，时序场景最优。
- **TF3500 Analytics Logger**：付费插件，性能最高，超出本库范围。

## 索引（27 条）

### Function Blocks - 现代版（16）

#### Configure / PLC Expert / SQL Expert mode 共用（同 FB 名同接口）

| 名称 | 用途 | 文档 |
|---|---|---|
| `FB_ConfigTcDBSrvEvt` | 在线读写 XML 配置：增 / 删 / 列出 数据库连接与 AutoLog 组 | [function_blocks/FB_ConfigTcDBSrvEvt.md](function_blocks/FB_ConfigTcDBSrvEvt.md) |
| `FB_PLCDBAutoLogEvt` | AutoLog 组控制：Start / Stop / RunOnce / Status，Server 端周期采集 | [function_blocks/FB_PLCDBAutoLogEvt.md](function_blocks/FB_PLCDBAutoLogEvt.md) |

#### PLC Expert mode

| 名称 | 用途 | 文档 |
|---|---|---|
| `FB_PLCDBCreateEvt` | 物理建库（文件型）+ 建表，OEM 首次部署链路核心 FB | [function_blocks/FB_PLCDBCreateEvt.md](function_blocks/FB_PLCDBCreateEvt.md) |
| `FB_PLCDBReadEvt` | 读 Beckhoff 标准 4 列表 / 自定义结构表，支持排序 + 分页 | [function_blocks/FB_PLCDBReadEvt.md](function_blocks/FB_PLCDBReadEvt.md) |
| `FB_PLCDBWriteEvt` | 写标准 4 列表 / 自定义表 / 跨设备 ADS 符号，4 种 E_WriteMode | [function_blocks/FB_PLCDBWriteEvt.md](function_blocks/FB_PLCDBWriteEvt.md) |
| `FB_PLCDBCmdEvt` | 占位符 SQL 命令（`Execute` 不返回 / `ExecuteDataReturn` 返回数据集） | [function_blocks/FB_PLCDBCmdEvt.md](function_blocks/FB_PLCDBCmdEvt.md) |

#### SQL Expert mode

| 名称 | 用途 | 文档 |
|---|---|---|
| `FB_SQLDatabaseEvt` | SQL 长连接管理（Connect / Disconnect / CreateCmd / CreateSP） | [function_blocks/FB_SQLDatabaseEvt.md](function_blocks/FB_SQLDatabaseEvt.md) |
| `FB_SQLCommandEvt` | 执行任意 SQL，复用 FB_SQLDatabaseEvt 的常驻连接 | [function_blocks/FB_SQLCommandEvt.md](function_blocks/FB_SQLCommandEvt.md) |
| `FB_SQLResultEvt` | 读 SQL Expert mode 结果集（分页 Read / Release，可选 verifying） | [function_blocks/FB_SQLResultEvt.md](function_blocks/FB_SQLResultEvt.md) |
| `FB_SQLStoredProcedureEvt` | 调存储过程（IN/OUT 参数 + 可选返回数据集） | [function_blocks/FB_SQLStoredProcedureEvt.md](function_blocks/FB_SQLStoredProcedureEvt.md) |

#### NoSQL Expert mode

| 名称 | 用途 | 文档 |
|---|---|---|
| `FB_NoSQLQueryEvt` | NoSQL 查询 Executor（DocumentDB + TimeSeriesDB 都用） | [function_blocks/FB_NoSQLQueryEvt.md](function_blocks/FB_NoSQLQueryEvt.md) |
| `FB_NoSQLResultEvt` | 读 NoSQL 结果集（ReadAsString / ReadAsStruct） | [function_blocks/FB_NoSQLResultEvt.md](function_blocks/FB_NoSQLResultEvt.md) |
| `FB_NoSQLValidationEvt` | schema 验证：GetIssues / GetRemainingData | [function_blocks/FB_NoSQLValidationEvt.md](function_blocks/FB_NoSQLValidationEvt.md) |
| `FB_NoSQLQueryBuilder_DocumentDB` | 文档型查询参数容器（Find / Insert / Update / Delete / Aggregate） | [function_blocks/FB_NoSQLQueryBuilder_DocumentDB.md](function_blocks/FB_NoSQLQueryBuilder_DocumentDB.md) |
| `FB_NoSQLQueryBuilder_TimeSeriesDB` | 时序查询参数容器（Insert / Query） | [function_blocks/FB_NoSQLQueryBuilder_TimeSeriesDB.md](function_blocks/FB_NoSQLQueryBuilder_TimeSeriesDB.md) |
| `FB_NoSQLObjectId_MongoDB` | MongoDB ObjectId 12-byte 解析（取时间戳 / 机器 ID / 进程 ID / 计数器） | [function_blocks/FB_NoSQLObjectId_MongoDB.md](function_blocks/FB_NoSQLObjectId_MongoDB.md) |

### Obsolete Function Blocks（10）

⚠️ **已废弃** —— 早期版本，仅维护老工程兼容（旧 `ipTcResultEvent : I_TcResultEvent` 接口）。新代码必走对应 `*Evt` 版本。

| 名称 | 已被替代 | 文档 |
|---|---|---|
| `FB_ConfigTcDBSrv` | → `FB_ConfigTcDBSrvEvt` | [obsolete/FB_ConfigTcDBSrv.md](obsolete/FB_ConfigTcDBSrv.md) |
| `FB_PLCDBAutoLog` | → `FB_PLCDBAutoLogEvt` | [obsolete/FB_PLCDBAutoLog.md](obsolete/FB_PLCDBAutoLog.md) |
| `FB_PLCDBCreate` | → `FB_PLCDBCreateEvt` | [obsolete/FB_PLCDBCreate.md](obsolete/FB_PLCDBCreate.md) |
| `FB_PLCDBRead` | → `FB_PLCDBReadEvt` | [obsolete/FB_PLCDBRead.md](obsolete/FB_PLCDBRead.md) |
| `FB_PLCDBWrite` | → `FB_PLCDBWriteEvt` | [obsolete/FB_PLCDBWrite.md](obsolete/FB_PLCDBWrite.md) |
| `FB_PLCDBCmd` | → `FB_PLCDBCmdEvt` | [obsolete/FB_PLCDBCmd.md](obsolete/FB_PLCDBCmd.md) |
| `FB_SQLDatabase` | → `FB_SQLDatabaseEvt` | [obsolete/FB_SQLDatabase.md](obsolete/FB_SQLDatabase.md) |
| `FB_SQLCommand` | → `FB_SQLCommandEvt` | [obsolete/FB_SQLCommand.md](obsolete/FB_SQLCommand.md) |
| `FB_SQLResult` | → `FB_SQLResultEvt` | [obsolete/FB_SQLResult.md](obsolete/FB_SQLResult.md) |
| `FB_SQLStoredProcedure` | → `FB_SQLStoredProcedureEvt` | [obsolete/FB_SQLStoredProcedure.md](obsolete/FB_SQLStoredProcedure.md) |

### Global Constants（1）

| 名称 | 用途 | 文档 |
|---|---|---|
| `Constants` 全部 GVL | `AMSPORT_DBSRV` + 5 个 `MAX_*` 上限常量 | [global_constants/Constants.md](global_constants/Constants.md) |

### DUTs（未单独成文档，在引用的 FB 文档中说明）

#### Configure / SQL / PLC 数据类型（PDF §6.1.2.1 ~ §6.1.2.4）

| 名称 | 用途 |
|---|---|
| `T_DBConfig_MsSQL` / `T_DBConfig_MsCompactSQL` / `T_DBConfig_MsAccess` / `T_DBConfig_Odbc` / `T_DBConfig_ASCII` / `T_DBConfig_SQLite` / `T_DBConfig_XML` | 数据库连接配置（按数据库类型选） |
| `ST_ConfigDB` / `ST_ConfigAutoLogGrp` | `FB_ConfigTcDBSrvEvt.Read` 输出条目 |
| `ST_ColumnInfo` | 列定义（`sName` / `eType` / `nLength` / `sProperty`） |
| `ST_StandardRecord` | Beckhoff 标准 4 列日志记录（ID / Timestamp / Name / Value） |
| `ST_ADSDevice` / `ST_Symbol` | `FB_PLCDBWriteEvt.WriteBySymbol` 跨设备读取的描述结构 |
| `ST_ExpParameter` | `FB_PLCDBCmdEvt` 占位符参数描述 |
| `ST_SQLSPParameter` | `FB_SQLDatabaseEvt.CreateSP` 存储过程参数描述 |
| `ST_AutoLogGrpStatus` | `FB_PLCDBAutoLogEvt.Status` 每组状态明细 |

#### NoSQL 数据类型（PDF §6.1.2.2）

| 名称 | 用途 |
|---|---|
| `T_QueryOptionDocumentDB_Find` / `_Aggregate` / `_Insert` / `_Update` / `_Delete` | DocumentDB 查询选项 |
| `T_QueryOptionTimeSeriesDB_Insert` / `_Query` | TimeSeriesDB 查询选项 |
| `T_ObjectId_MongoDB` | 12 字节 MongoDB ObjectId 描述 |

#### 枚举（Enumerations）

| 名称 | 取值 |
|---|---|
| `E_ColumnType` | `BigInt` / `Integer` / `SmallInt` / `TinyInt` / `BIT_` / `Money` / `Float` / `REAL_` / `DateTime` / `NText` / `NChar` / `Image` / `NVarChar` / `Binary` / `VarBinary` |
| `E_WriteMode` | `eADS_TO_DB_Append` / `_Update` / `_RingBuff_Time` / `_RingBuff_Count` |
| `E_OrderColumn` | `eColumnID` / `eColumn_Timestamp` / `eColumn_Name` / `eColumn_Value` |
| `E_OrderType` | `eOrder_ASC` / `eOrder_DESC` |
| `E_TcDBSrvConfigType` | `Database` / `AutoLogGroup` |
| `E_DocumentDbQueryType` | `Find` / `Aggregate` / `InsertOne` / `InsertMany` / `Update` / `Delete` 等 |
| `E_NoSQLDatabaseType` | NoSQL 数据库类型枚举 |
| `E_TimeSeriesDbQueryType` | 时序查询类型 |
| `E_ExpParameterType` | `Int32` / `Int64` / `Float32` / `Double64` / `Boolean` / `Byte_` / `STRING_` / `ByteArray` / `DateTime` |
| `E_SPParameterType` | `Input` / `Output` / `InputOutput` / `ReturnValue` / `OracleCursor` |
| `E_ADSRdWrtMode` / `E_PLCDataType` / `E_ErrorType` | `WriteBySymbol` 与 ADS 操作支持枚举 |

### Tc3_EventLogger 接口（PDF §6.1.1.5）

| 名称 | 来源 | 说明 |
|---|---|---|
| `I_TcMessage` | Tc3_EventLogger | 现代版 FB（`*Evt` 后缀）的 `ipTcResult` 类型，提供 `RequestEventText` / `EqualsToEventEntry` 等方法 |
| `I_TcEventBase` | Tc3_EventLogger | `I_TcMessage` 父接口，提供事件 ID / Severity / Source 等属性 |
| `I_TcResultEvent` | Tc3_EventLogger | 旧版 obsolete FB 的 `ipTcResultEvent` 类型 |
| `TcEventSeverity` | Tc3_EventLogger | 事件分级枚举：`Verbose` / `Information` / `Warning` / `Error` / `Critical` |

> 详情见 Tc3_EventLogger 库；本库 FB 引用即可。

## 错误码

错误来源 3 路并行——`bError` + Tc3 EventLogger 接口（`ipTcResult` 或 `ipTcResultEvent`）：

| 来源 | 表现 | PDF 章节 |
|---|---|---|
| ADS Return Codes | `nErrId` 0x0..0x7xx | §8.1.1 |
| Database Server 内部错误 | 通过 `RequestEventText` 取本地化文本 | §8.1.1 |
| NoSQL database return codes | NoSQL 专属事件 | §8.1.1 末尾 |

`ipTcResult.RequestEventText(nLangId, ADR(sBuf), SIZEOF(sBuf))` 取语言本地化错误描述：`1033` 英语 / `1031` 德语 / `2052` 简体中文。

## 例程导入

每篇文档配套 `examples/P_Demo_<Name>.TcPOU`（TwinCAT 3 原生 .TcPOU XML 骨架，GUID 全仓唯一，CDATA 包裹 IEC 文本）：

1. 在 TwinCAT 3 XAE 中右键 PLC 项目下 POUs 文件夹 → **Add → Existing Item…**
2. 选择 `P_Demo_<Name>.TcPOU`
3. 引用 `Tc3_Database` 与 `Tc3_EventLogger`（References → Add library）
4. 编译 → 登录 → 运行；启动 TwinCAT Functions 下的 TF6420 Database Server 服务
5. 按各文档 §6 的「验证步骤」在线触发输入信号并 monitor 输出

## 验证基线

| 工具 | 范围 | 结果 |
|---|---|---|
| `verify_doc.py` | 27 / 27 文档 | ✅ 全 PASS（退出 0） |
| `lint_tcpou.py` | 27 / 27 例程 | ✅ 全 PASS（退出 0） |
| `lint_tcpou.py --check-unique` | 全仓所有 .TcPOU GUID 唯一性 | ✅ PASS |
| 占位短语扫描 | 27 / 27 文档 | ✅ 无 |
| InfoSys URL 真实性 | 27 / 27 文档 | ✅ 全部 topic ID 可达 |

## 关键工程判断（PDF + InfoSys 双源核对的非显然结论）

1. **InfoSys slug**：本库 InfoSys topic 全部位于 `tf6420_tc3_database_server/<topicid>.html`；同根目录托管 Tc2_Database（PDF 也是同一份手册的 §6.2）。各 FB 的 topic ID 通过 Web 搜索 + 与 PDF 双向对照后确认（如 `FB_ConfigTcDBSrvEvt` = `2674371339.html`、`FB_PLCDBWriteEvt` = `2674379019.html`、`FB_NoSQLQueryBuilder_DocumentDB` = `5875132043.html`）。
2. **parse_toc.py 返回空（已知工具行为）**：TF 系列 PDF 的多级章节深度（`6.1.1.4.1.1` 等）超过 parse_toc 当前 `\d+(?:\.\d+){0,4}` 的最大 5 段限制，所以本库通过 `_find_section_in_body` fallback 完成 verify_doc。对深度 6 的 3 个 FB（`FB_NoSQLQueryBuilder_DocumentDB` / `_TimeSeriesDB` / `FB_NoSQLObjectId_MongoDB`）以及深度 4 的 `Constants` 章节，在 `_meta/.pdf-cache/Tc3_Database.txt` 中追加了 `6.1.1.9.x` / `6.1.3.9` 风格的深度 ≤ 5 别名行（不影响其他工具行为，缓存为本库专用）。
3. **同名 FB 跨 3 mode**：`FB_ConfigTcDBSrvEvt` 在 PDF §6.1.1.1.1（Configure mode）+ §6.1.1.2.1（PLC Expert）+ §6.1.1.3.1（SQL Expert）三处出现同一份接口；`FB_PLCDBAutoLogEvt` 在 §6.1.1.1.2 + §6.1.1.2.2 两处。本库每个唯一 FB 名只做一篇文档，文档中明确说明它在多个 mode 下都是同一份接口。
4. **现代版 `*Evt` 与 obsolete 版的差异**：仅在错误接口字段名 / 类型：`*Evt` 用 `ipTcResult : I_TcMessage`（新），obsolete 用 `ipTcResultEvent : I_TcResultEvent`（旧）；方法签名 / 参数 / 状态机 / 行为完全一致。SQL Expert mode 的 obsolete `FB_SQLCommand` / `FB_SQLStoredProcedure` 与 obsolete 配套的 `FB_SQLResult` / `FB_SQLDBResult` 与新版互不兼容（CreateCmd / CreateSP 的指针类型严格匹配）。
5. **NoSQL Expert mode 的接口名 typo**：`FB_NoSQLQueryEvt.ExecuteDataReturn` 入参 PDF 印为 `iNoSSQLQueryBuilder`（多一个 S），而其他场合是 `iNoSQLQueryBuilder`。InfoSys 同保留。本仓所有例程按 PDF 拼写。
6. **FB_NoSQLResultEvt 内部声明 typo**：PDF §6.1.1.4.3 定义里写 `FUNCTION BLOCK FB_SQLResultEvt`（漏 No 前缀），但 InfoSys 与上游 `FB_NoSQLQueryEvt.ExecuteDataReturn` 的 `pNoSQLResult: POINTER TO FB_NoSQLResultEvt` 引用都用正确名。本仓元信息按正确名命名。
7. **FB_NoSQLValidationEvt 用 `I_TcResultEvent` 而非 `I_TcMessage`**：PDF 此 FB 输出声明类型与其他 NoSQL FB 不一致；可能是 Beckhoff 内部接口分级（`I_TcResultEvent` 或为 `I_TcMessage` 父接口）。例程按 PDF 声明类型使用。
8. **`FB_NoSQLObjectId_MongoDB` PDF 章节标题处 typo**：PDF 6.1.1.4.5.1 节内部声明里有时拼为 `FB_NoSQLObjecId_MongoDB`（少一个 `t`），InfoSys 用完整名。本仓按 InfoSys 命名。
9. **AutoLog `Status` 方法的独立 `bBusy_Status`**：与多数 Beckhoff FB 单实例单方法语义不同——`Status` 方法可与 `RunOnce` / `Start` / `Stop` 并行运行而互不阻塞，因此有独立的 `bBusy_Status` 位。HMI 1Hz 周期调 Status 不会卡其他业务调用。
10. **OEM 首次部署完整链路**：`FB_ConfigTcDBSrvEvt.Create(bTemporary := FALSE)` 注册连接 → `FB_PLCDBCreateEvt.Database(bCreateXMLConfig := TRUE)` 物理建库 + 拿 hDBID → `FB_PLCDBCreateEvt.Table(hDBID, ...)` 建表 → `FB_PLCDBWriteEvt.Write(...)` 写入。整条链全在 PLC 代码，不依赖配置器图形界面。这是 OEM 量产线零配置装机的标准做法。
11. **占位符 SQL（PLC Expert mode）vs 拼字符串 SQL（SQL Expert mode）**：`FB_PLCDBCmdEvt` 用 `{name}` 占位符 + `ST_ExpParameter` 数组防 SQL 注入；`FB_SQLCommandEvt` 直接拼 SQL 字符串。安全敏感场景（HMI 输入用作 WHERE 条件等）必走前者或存储过程。
12. **AutoLog `RunOnce(bAll := TRUE)` 在大量组场景代价高**：例如 100 组同时强制采集会让 DB 一瞬间收 100 条 INSERT。事件触发型批量快照前先评估 DB 吞吐。
13. **NoSQL 时序 `nCycleTime` 单位是 µs**：PDF 例子 `nCycleTime := 1000` 是 1 ms；不要错写 `T#1MS`（TIME 类型）。Builder 模式 schema 验证开 `bValidate := TRUE` + `FB_NoSQLValidationEvt` 可在 OEM 跨车间部署时快速适配 DB 端字段差异。
14. **占位符 `{name}` 与 SQL 字面字符 `{` 冲突**：MS SQL / MySQL 通常不在 SQL 里用 `{`；PostgreSQL 的 JSON 操作符可能用。极少数情况需评估。

## 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf)（v1.14.1，411 页，含 Tc2_Database 与 Tc3_Database 两章）
- **InfoSys（TF6420 章节首页）**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/index.html
- **Tc3_Database 子章入口**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2668529419.html
- **产品页**：https://www.beckhoff.com/tf6420
- **姊妹库 Tc2_Database**：本仓 [Tc2_Database/](../Tc2_Database/)（TC2 风格 + 同源 PDF §6.2 章节）
