# FB_PLCDBCreateEvt

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2674375179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PLCDBCreateEvt.TcPOU`](../examples/P_Demo_FB_PLCDBCreateEvt.TcPOU) |

---

## 1. 功能简述

从 PLC 端物理创建数据库文件与数据表的功能块（PDF §6.1.1.2.3，PLC Expert mode）。提供两个方法：`Database` 在 Database Server 主机上创建一个新的数据库文件（仅文件型数据库——SQL Compact `.sdf` / MS Access `.mdb` / XML / 文件级 MS SQL；不支持 ODBC 远程数据库）；`Table` 在已注册的数据库里建表，列定义通过 `ST_ColumnInfo` 数组传入。这是 OEM 设备「首次部署自动建库建表」流水线的关键一步：跑 `Database` → 拿到新 `hDBID` → 跑 `Table` 建标准表 → 后续 `FB_PLCDBWriteEvt` 即可写入。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID: T_AmsNetID := '';
    tTimeout: TIME := T#5S;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | `''` | Database Server 所在控制器 AMS Net ID。 |
| `tTimeout` | `TIME` | `T#5S` | ADS 超时。建库可能涉及磁盘 I/O，必要时加大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy: BOOL;
    bError: BOOL;
    ipTcResult: Tc3_EventLogger.I_TcMessage;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 方法运行中保持 TRUE。 |
| `bError` | `BOOL` | 方法出错置 TRUE。 |
| `ipTcResult` | `Tc3_EventLogger.I_TcMessage` | Tc3 EventLogger 消息接口；按需取本地化错误文本。 |

### VAR_IN_OUT

无。

### Method: `Database`

```iecst
METHOD Database : BOOL
VAR_INPUT
    pDatabaseConfig: POINTER TO BYTE;
    cbDatabaseConfig: UDINT;
    bCreateXMLConfig: BOOL;
    pDBID: POINTER TO UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pDatabaseConfig` | `POINTER TO BYTE` | 指向具体数据库类型的配置结构（`T_DBConfig_MsCompactSQL` / `T_DBConfig_MsAccess` / `T_DBConfig_MsSQL` / `T_DBConfig_XML` 等，详 §6.1.2.1.8）。 |
| `cbDatabaseConfig` | `UDINT` | 该结构 `SIZEOF`。 |
| `bCreateXMLConfig` | `BOOL` | TRUE = 同时把刚建的数据库注册到 XML 配置（拿回 `hDBID`，后续可直接 Connect 用）；FALSE = 只在磁盘上建文件，不入 XML。 |
| `pDBID` | `POINTER TO UDINT` | 当 `bCreateXMLConfig = TRUE` 时，新生成的 `hDBID` 写到此地址。 |

### Method: `Table`

```iecst
METHOD Table : BOOL
VAR_INPUT
    hDBID : UDINT;
    sTableName : T_MaxString;
    pTableCfg : POINTER TO ARRAY[0..MAX_DBCOLUMNS] OF ST_ColumnInfo;
    cbTableCfg : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hDBID` | `UDINT` | 目标数据库 ID（前一步 `Database` 返回的或事先注册的）。 |
| `sTableName` | `T_MaxString` | 要创建的表名。 |
| `pTableCfg` | `POINTER TO ARRAY[0..MAX_DBCOLUMNS] OF ST_ColumnInfo` | 列定义数组地址；每元素是一列（名 + 类型 + 长度 + property 字符串）。 |
| `cbTableCfg` | `UDINT` | 列定义数组 `SIZEOF`。 |

`ST_ColumnInfo` 字段：`sName : STRING(50)`、`eType : E_ColumnType`、`nLength : UDINT`、`sProperty : STRING(255)`（如 `'IDENTITY(1,1)'` 用于主键自增）。

### Properties

| 属性 | 类型 | 访问 | 说明 |
|---|---|---|---|
| `eTraceLevel` | `TcEventSeverity` | Get / Set | 事件分级阈值。 |

### 关联常量

`MAX_DBCOLUMNS = 255`（PDF §6.1.3.1）——列定义数组上限。

## 3. 行为说明

**`Database` 适用范围**：只能创建「文件型」数据库或 MS SQL Server 上的新数据库实例：SQL Compact (`.sdf`)、MS Access (`.mdb`)、MS SQL Server 上的 CREATE DATABASE、ASCII (`.csv`)、XML。**不能创建** ODBC 远程数据库（MySQL / PostgreSQL / Oracle / DB2 / Firebird）——这类必须由 DBA 在 DB 服务器侧用 `CREATE DATABASE` 预先建好，PLC 只能通过 `FB_ConfigTcDBSrvEvt` 注册连接。

**`bCreateXMLConfig` 的含义**：TRUE 时本 FB 不仅建物理文件还顺便注册到 Server XML，等于一步走完「建库 + 配置」。FALSE 时只在磁盘上落文件，后续需要另外调 `FB_ConfigTcDBSrvEvt.Create` 注册才能用——OEM 自动初始化场景几乎总是 TRUE，节省一次调用。

**`Table` 的列定义**：`ST_ColumnInfo[i]` 的 `eType` 用 `E_ColumnType.<Name>`（PDF §6.1.2.3.1 / Tc2 同名枚举 §6.2.2.x）。`nLength` 对变长类型（NVarChar / Binary / NText）是字节数上限；对定长（BigInt / Float / DateTime）是该类型字节数（写一致便于 Server 校对，不会用作截断）。`sProperty` 是 SQL 列约束直传，如 `'IDENTITY(1,1)'`（MS SQL 主键自增）、`'NOT NULL DEFAULT 0'`、`'PRIMARY KEY'`。该字段直接拼到 CREATE TABLE 语句，不做转义——SQL 注入风险存在但调用方常是受信代码所以一般不防。

**OEM 首次部署典型链路**：(1) `FB_PLCDBCreateEvt.Database(T_DBConfig_MsCompactSQL{sServer := 'C:\Recipes.sdf'}, bCreateXMLConfig := TRUE, ADR(hNewDb))`；(2) 拿到 `hNewDb` 后 `FB_PLCDBCreateEvt.Table(hNewDb, 'tbl_Recipes', ADR(aColInfo), SIZEOF(aColInfo))`；(3) `FB_PLCDBWriteEvt.Write(hNewDb, 'tbl_Recipes', ...)` 即可写入。整条链全在 PLC，不依赖配置器图形界面。

**幂等性**：`Database` 调第二次同一文件会返回错误（文件已存在），不会覆盖；`Table` 第二次同一表名同样错。OEM 自动部署逻辑需先调 `FB_GetDBXMLConfig` 或 `FB_GetStateTcDatabase`（Tc2 版）查询是否已有，再决定建或跳过。

**Tc3_EventLogger 集成**：和其他 `*Evt` FB 一样，`bError = TRUE` 配合 `ipTcResult.RequestEventText` 取详细错误文本。`eTraceLevel` 控事件分级。

## 4. 错误码 / 返回值

每方法返回 `BOOL`（TRUE = 方法体完成）。`bError` + `ipTcResult` 表征实际结果。典型错误：

| 现象 | 含义 | 处理 |
|---|---|---|
| 文件已存在（Database） | 同名 `.sdf` / `.mdb` 已在 | 改用别的名字、或先删旧文件 |
| 路径无权限 | Server 进程无写权限 | 用管理员模式给 `C:\TwinCAT\Functions\TF6420-Database-Server\` 写权限 |
| 表已存在（Table） | 同名表已建 | 改名或先 DROP（用 `FB_PLCDBCmdEvt`） |
| 列类型不被 DB 支持 | 例如 SQL Compact 不全支持 `NText` | 改用 `NVarChar(N)` |
| `hDBID` 不存在 | 未注册的连接 | 先 `Database(bCreateXMLConfig := TRUE)` 或 `FB_ConfigTcDBSrvEvt.Create` |

完整 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **`bCreateXMLConfig := FALSE` 后必须另调 Config**：否则物理文件建好但 Server 不知道它存在，无法 Connect。生产链路用 TRUE 一步到位。
- **`pDatabaseConfig` 必须用对应 `T_DBConfig_*` 而不是裸数组**：例如建 SQL Compact 用 `T_DBConfig_MsCompactSQL`，结构内字段（`sServer` 是文件路径 + 名）含义与 MS SQL 的 `sServer`（IP）完全不同。
- **`sTableName` 与 `sProperty` 都直接拼 SQL**：不要从外部不可信来源（如 OPC 客户端写入）拼接表名，存在注入风险。OEM 内部代码直拼通常 OK。
- **`nLength` 对 NVarChar 是字符数还是字节数**：PDF 没明确，实际 Server 把 NVarChar(50) 当 50 个 Unicode 字符（100 字节）。如果存中文务必加大长度，避免被截断报错。（工程经验补充）
- **同一 PLC 多个 `FB_PLCDBCreateEvt` 实例并行**：可行，但每实例独立的 `bBusy` 状态机；同时 Create 同一 `hDBID` 下两张同名表 Server 不会保护，谁后到谁报「表已存在」。
- **`Database` 仅文件型数据库**：详见行为说明的「适用范围」段。
- **运行后 PLC 重启**：物理文件留在磁盘上不丢，但 `bCreateXMLConfig := FALSE` 创建的（未入 XML）会让 Server 不知道它存在，PLC 重启后看不到该连接，需重跑注册。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PLCDBCreateEvt.TcPOU`](../examples/P_Demo_FB_PLCDBCreateEvt.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机 OEM 量产线，每台机器装机时需要在本地 D 盘自动建一个 SQL Compact 配方数据库 `D:\Recipes.sdf`，含 `tbl_Recipes(nID, sName, rTemperature, rPressure, nCycleCount)`。技师只把机器接电、配 IP，PLC 启动序列里自动跑：(1) `Database()` 创建 .sdf 文件并注册；(2) `Table()` 建表；(3) 业务程序后续读写。
- **价值**：装机零配置——技师无需在每台机器上打开 Database Server 配置器手动建库建表；OEM 维护团队改列定义后只升级 PLC 程序，下次装机自动应用新表结构；首次部署链路全在 PLC，可视化追踪。
- **替代方案对比**：
  - **手工用 SSMS / SQL Compact Toolbox 建库**：装机时间长，对车间技师不友好。
  - **配置器导入预生成 XML**：依赖 Engineering，技师没 XAE。
  - **`FB_DBCreate` + `FB_DBTableCreate`（Tc2_Database）**：TC2 版本等价；TC3 新项目优先用本 FB（带 EventLogger）。
  - **本 FB**：TC3 库的官方建库建表 API；带事件诊断；与 `FB_PLCDBWriteEvt` / `FB_PLCDBReadEvt` 等无缝衔接。
  - **obsolete 版 `FB_PLCDBCreate`**：旧版接口同（裸 nErrId 报错），新项目应迁移到本 FB。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.1.2.3（PLC Expert mode）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2674375179.html
- **相关 FB / FC / DUT**：`T_DBConfig_MsCompactSQL` / `T_DBConfig_MsAccess` / `T_DBConfig_MsSQL` / `T_DBConfig_XML` / `T_DBConfig_ASCII`（§6.1.2.1.8）、`ST_ColumnInfo` / `E_ColumnType`（§6.1.2.3 / §6.1.2.4.10）、`MAX_DBCOLUMNS`、`FB_ConfigTcDBSrvEvt`（配合的配置 API）、`FB_PLCDBWriteEvt`（写入下一步）、obsolete `FB_PLCDBCreate`
