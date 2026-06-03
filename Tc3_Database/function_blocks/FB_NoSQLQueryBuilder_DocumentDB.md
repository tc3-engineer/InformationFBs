# FB_NoSQLQueryBuilder_DocumentDB

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1031/tf6420_tc3_database_server/5875132043.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_NoSQLQueryBuilder_DocumentDB.TcPOU`](../examples/P_Demo_FB_NoSQLQueryBuilder_DocumentDB.TcPOU) |

---

## 1. 功能简述

NoSQL Expert Mode 下定义文档型数据库（MongoDB / CosmosDB / DocumentDB）查询的功能块（PDF §6.1.1.4.1.1）。**不直接发送查询**——只是「查询参数容器」：把 `eQueryType`（Find / Aggregate / InsertOne / InsertMany / Update / Delete 等）、`sCollectionName`（集合名）、`pQueryOptions`（指向 `T_QueryOptionDocumentDB_*` 选项结构体的地址）填好后，作为参数传给 `FB_NoSQLQueryEvt.Execute(hDBID, ADR(thisBuilder))`，由后者实际发送 ADS 命令到 Server。提供一个 `Build` 方法，但 PDF 明确「It is not necessary to call the Build method」——`FB_NoSQLQueryEvt` 内部会在发送前自动调。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    eQueryType : E_DocumentDbQueryType;
    sCollectionName : T_MAXSTRING;
    pQueryOptions: POINTER TO BYTE;
    cbQueryOptions : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `eQueryType` | `E_DocumentDbQueryType` | - | 查询类型枚举：`Find` / `Aggregate` / `InsertOne` / `InsertMany` / `Update` / `Delete` 等（PDF §6.1.2.2.2）。决定 Server 端解释 `pQueryOptions^` 的方式。 |
| `sCollectionName` | `T_MAXSTRING` | - | 目标集合（document collection）名，如 `'sensors'` / `'recipes'`。空字符串时 Server 报错。 |
| `pQueryOptions` | `POINTER TO BYTE` | - | 查询选项结构体地址。结构体类型按 `eQueryType` 选：`T_QueryOptionDocumentDB_Find` / `_Aggregate` / `_Insert` / `_Update` / `_Delete`（PDF §6.1.2.2.4.1.x）。 |
| `cbQueryOptions` | `UDINT` | - | 选项结构体 SIZEOF。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
END_VAR
```

（无 VAR_OUTPUT 字段——本 FB 是参数容器，不直接输出。错误状态由 `FB_NoSQLQueryEvt` 报告。）

### VAR_IN_OUT

无。

### Method: `Build`（可选，PDF 明确 `[optional]`）

```iecst
METHOD Build
```

无入参 / 无返回值。PDF：「This method is called automatically in case of a FB_NoSQLQueryEvt (either with Execute or ExecuteDataReturn) before the query is sent. It creates a TwinCAT 3 Database Server-specific query from the specified parameters of the QueryBuilder.」一般不需调用方手动调。

## 3. 行为说明

**NoSQL Expert Mode 设计**：与 SQL Expert mode（FB_SQLDatabaseEvt + FB_SQLCommandEvt）不同，NoSQL 不用「连接 + 命令」模式，而是用「QueryBuilder + QueryExecutor」模式。Builder 实例只负责描述查询参数（按数据库类型选），Executor (`FB_NoSQLQueryEvt`) 负责发送 ADS、管理连接、接收结果。一个 Builder 实例可对应多种查询类型（改 eQueryType 即可），同一个 Builder 可被 Executor 反复调用。

**`E_DocumentDbQueryType` 取值**（PDF §6.1.2.2.2）：
- `Find`：按过滤条件查文档（最常用，对应 MongoDB `db.collection.find()`）
- `Aggregate`：聚合管道查询（对应 `aggregate()`）
- `InsertOne` / `InsertMany`：插入文档
- `Update` / `UpdateMany`：更新文档
- `Delete` / `DeleteMany`：删除文档

每种查询类型对应不同的 `T_QueryOptionDocumentDB_*` 选项结构。例如 `Find` 用 `T_QueryOptionDocumentDB_Find`（字段：pFilter / cbFilter / pSort / cbSort / pProjection / cbProjection 等，PDF §6.1.2.2.4.1.1）；`InsertOne` 用 `T_QueryOptionDocumentDB_Insert`（pDocuments / cbDocuments）。

**为什么用 BYTE 指针**：Builder 不需要知道选项结构的具体类型——Server 端按 `eQueryType` 解释 `pQueryOptions^` 的字节。这样同一个 Builder 类型能覆盖 MongoDB 所有查询模式而不需要派生 5-10 个子 FB。代价：调用方填错 `eQueryType` 与 `pQueryOptions^` 不匹配时 Server 才报错（编译期无类型检查）。

**调用流程**：
1. 声明 Builder + Executor + 对应选项结构。
2. 业务逻辑里设 Builder 三个字段（type / collection / options ptr+size）+ 填选项结构。
3. 调 `fbExec.Execute(hDBID, ADR(fbBuilder))` 或 `ExecuteDataReturn(...)`。

**与 `FB_NoSQLQueryBuilder_TimeSeriesDB` 的区别**：本 FB 用于 DocumentDB（MongoDB 类，JSON 文档存储）；时序库（InfluxDB / TimescaleDB / PostgreSQL TimescaleDB）用 `FB_NoSQLQueryBuilder_TimeSeriesDB`。两者接口完全不同（时序库不用 collection 概念而用 measurement / table 名）。

**`Build` 方法不需手动调**：PDF 强调「It is not necessary to call the Build method」。`FB_NoSQLQueryEvt.Execute` 内部会先调 `Build` 把字段编码成 Server 协议。手动调 `Build` 在 PDF 没给出明确用例——可能用于预先验证参数完整性。

## 4. 错误码 / 返回值

本 FB **不直接报错**——它没 `bError` / `ipTcResult` 输出。错误由调用者 `FB_NoSQLQueryEvt` 在 `Execute` 或 `ExecuteDataReturn` 后报告。Build 方法无返回值（PDF 仅写 `METHOD Build`，无 `: <type>` 说明）。

典型上游报错：

| 现象 | 含义 | 处理 |
|---|---|---|
| Executor `bError`，事件含 `Collection not found` | `sCollectionName` 拼写错 / 集合不存在 | 检查 MongoDB 集合 |
| 事件含 `Type mismatch` | `eQueryType` 与 `pQueryOptions^` 选项结构不匹配 | 比对 PDF §6.1.2.2.2 与 §6.1.2.2.4.1 |
| 事件含 `Filter syntax` | Find 的 pFilter 内 JSON 语法错 | 在 mongoshell 先跑通 |

## 5. 使用注意 / 常见坑

- **`pQueryOptions^` 必须指向 `T_QueryOptionDocumentDB_*` 中正确类型**：`eQueryType := Find` → `pQueryOptions := ADR(stFindOpt : T_QueryOptionDocumentDB_Find)`。混用会被 Server 按错类型解析，得到错值或错误。
- **`pQueryOptions^` 必须持续有效**：Server 异步消费；不能用临时栈结构。
- **`Build` 方法只需 Executor 自动调**：手动调几乎无意义；除非要 dry-run 验证参数。
- **多次 Execute 同 Builder**：可改字段后再 Execute；但确保 `pQueryOptions^` 指向的选项结构内容也被更新。
- **不支持参数化 SQL 占位符**：MongoDB 不用 SQL，参数化通过 JSON 结构传——pFilter 是 JSON 字符串，里头的值需自己拼。
- **Builder 实例本身不连数据库**：所有连接管理由 Executor 通过 `hDBID` 做。Builder 只是「参数容器」。
- **MongoDB connection 必须先在 XML 注册**：通过 TF6420 配置器选「MongoDB」类型 + 填 connection string；本 FB 不创建连接。
- **`sCollectionName` 大小写敏感**：MongoDB 集合名严格区分大小写。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_NoSQLQueryBuilder_DocumentDB.TcPOU`](../examples/P_Demo_FB_NoSQLQueryBuilder_DocumentDB.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：注塑机把每个产品的工艺曲线（含 300 个时刻点、嵌套数组）作为 1 个 JSON 文档存到 MongoDB 集合 `production_curves`。传统 SQL 表存这种非定长嵌套数据要么序列化成 BLOB（PLC 端解码困难）要么拆多表（查询慢）。用 MongoDB：1 文档 1 产品，PLC 用 Builder 设 `eQueryType := InsertOne` + `T_QueryOptionDocumentDB_Insert.pDocuments := ADR(sJsonDoc)`，Executor 一次 ADS 即写入。查询时设 `Find` + `pFilter := '{"productId":"P12345"}'` 拉指定产品的曲线。
- **价值**：嵌套 / 非定长数据结构的存储与检索无需 PLC 端复杂序列化；MongoDB 横向扩展能力让历史数据保留期不受单表性能限制；EventLogger 错误诊断（通过 Executor）。
- **替代方案对比**：
  - **SQL 表 + BLOB 列**：PLC 端要做序列化反序列化，查询只能取整 BLOB。
  - **`FB_NoSQLQueryBuilder_TimeSeriesDB`**：固定时序场景（InfluxDB / TimescaleDB）的 Builder；本 FB 适合文档型（MongoDB）。
  - **直连 MongoDB（第三方 PLC 客户端）**：依赖外部组件、许可成本；TF6420 一站式解决。
  - **本 FB**：TF6420 NoSQL Expert mode 文档库 Builder 唯一选项。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.1.4.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1031/tf6420_tc3_database_server/5875132043.html
- **相关 FB / FC / DUT**：`FB_NoSQLQueryEvt`（Executor，发送查询）、`E_DocumentDbQueryType`（§6.1.2.2.2）、`T_QueryOptionDocumentDB_Find` / `_Aggregate` / `_Insert` / `_Update` / `_Delete`（§6.1.2.2.4.1.x）、`FB_NoSQLQueryBuilder_TimeSeriesDB`（同类时序库版本）、`I_NoSQLQueryBuilder`（共有接口）
