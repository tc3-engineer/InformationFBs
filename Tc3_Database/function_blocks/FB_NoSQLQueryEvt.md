# FB_NoSQLQueryEvt

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/5875133963.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_NoSQLQueryEvt.TcPOU`](../examples/P_Demo_FB_NoSQLQueryEvt.TcPOU) |

---

## 1. 功能简述

NoSQL Expert Mode 下执行 NoSQL 查询的 Executor 功能块（PDF §6.1.1.4.2）。配合 `FB_NoSQLQueryBuilder_DocumentDB` 或 `FB_NoSQLQueryBuilder_TimeSeriesDB` 使用——Builder 描述查询参数，本 FB 负责发送 ADS 到 Database Server。两个方法：`Execute` 发送查询不接收返回数据集（Insert / Update / Delete 用）；`ExecuteDataReturn` 发送 + 把结果集缓存到调用方提供的 `FB_NoSQLResultEvt` 实例（Find / Aggregate / 时序 Query 用）。NoSQL 与 SQL 模式架构上不同——SQL 是 Database → Command → Result 链；NoSQL 是 Builder → Executor → Result 链。

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
| `sNetID` | `T_AmsNetID` | `''` | Database Server AMS Net ID。 |
| `tTimeout` | `TIME` | `T#5S` | ADS 超时；大批量写入或复杂聚合可加大。 |

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
| `bBusy` | `BOOL` | 任一方法运行中。 |
| `bError` | `BOOL` | 错误置 TRUE。 |
| `ipTcResult` | `Tc3_EventLogger.I_TcMessage` | Tc3 EventLogger 消息接口。 |

### VAR_IN_OUT

无。

### Properties

| 属性 | 类型 | 说明 |
|---|---|---|
| `eTraceLevel` | `TcEventSeverity` | 事件分级阈值。 |

### Method: `Execute`（不返回数据）

```iecst
METHOD Execute : BOOL
VAR_INPUT
    hDBID: UDINT;
    iNoSQLQueryBuilder: I_NoSQLQueryBuilder;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hDBID` | `UDINT` | 已注册的 NoSQL 数据库连接 ID。 |
| `iNoSQLQueryBuilder` | `I_NoSQLQueryBuilder` | 已配好参数的 Builder 实例（DocumentDB 或 TimeSeriesDB 都实现该接口）。 |

### Method: `ExecuteDataReturn`（返回数据集）

```iecst
METHOD ExecuteDataReturn : BOOL
VAR_INPUT
    hDBID : UDINT;
    iNoSSQLQueryBuilder: I_NoSQLQueryBuilder;
    pNoSQLResult: POINTER TO FB_NoSQLResultEvt;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hDBID` | `UDINT` | 数据库连接 ID。 |
| `iNoSSQLQueryBuilder` | `I_NoSQLQueryBuilder` | Builder 实例（注意 PDF 印刷里多了个 `S`：`iNoSSQLQueryBuilder`，调用代码必须照此拼写）。 |
| `pNoSQLResult` | `POINTER TO FB_NoSQLResultEvt` | 接收结果集的 `FB_NoSQLResultEvt` 实例地址。Server 端缓存结果与该实例绑定。 |

### 关联属性（在 PDF 中 `ExecuteDataReturn` 的「Return value」段单独提到）

| 字段 | 类型 | 说明 |
|---|---|---|
| `nDataCount` | `UDINT` | `[optional]` Number of records returned——`ExecuteDataReturn` 完成后表示返回行数。PDF §6.1.1.4.2.2 把它列在 Return value 段，实际是属性形式访问。 |

## 3. 行为说明

**NoSQL Expert mode 架构**：
1. **Builder**（`FB_NoSQLQueryBuilder_DocumentDB` 或 `_TimeSeriesDB`）描述查询参数。
2. **Executor**（本 FB）拿 Builder 实例 + hDBID，通过 ADS 把查询发送给 Database Server。
3. **Result**（`FB_NoSQLResultEvt`）接收 Server 缓存的结果集，按需 Read。

**`I_NoSQLQueryBuilder` 多态**：两种 Builder（DocumentDB / TimeSeriesDB）都实现 `I_NoSQLQueryBuilder` 接口（PDF 6.1.1.4.1 段背景说明），所以本 Executor 通过接口参数能同时接受两类 Builder——单一 Executor 实例可在不同周期切换调用 DocumentDB 与 TimeSeriesDB Builder。

**`Execute` vs `ExecuteDataReturn` 用法选择**：
- `Execute`：仅做事不要结果——InsertOne / InsertMany / Update / Delete / 时序批量 Insert。
- `ExecuteDataReturn`：要拿数据回来——Find / Aggregate / 时序 Query。需提前准备 `FB_NoSQLResultEvt` 实例。

**`pNoSQLResult` 必须事先就绪**：传入 Result 实例必须已声明且作用域持续到结果读完。Server 缓存与该实例绑定。

**PDF 拼写 typo `iNoSSQLQueryBuilder`**：`ExecuteDataReturn` 的入参名为 `iNoSSQLQueryBuilder`（多一个 S），与 `Execute` 的 `iNoSQLQueryBuilder` 不一致。**调用代码必须按 PDF 拼写**否则编译报错（IEC 编译器严格匹配方法签名）。PDF 第 6.1.1.4.2.2 节明确印为这样——可能是 Beckhoff 源码 typo，InfoSys 同保留。

**`nDataCount` 属性**：PDF 把它放在「Return value」段下但 Return value 段同时给出 `ExecuteDataReturn : BOOL`——所以 `nDataCount` 实际是 FB 的一个属性，`ExecuteDataReturn` 完成后访问 `fbExecutor.nDataCount` 取行数。`Execute`（不返回数据）则该属性无意义。

**典型流程**（DocumentDB Insert）：
```iecst
fbBuilder.eQueryType := E_DocumentDbQueryType.InsertOne;
fbBuilder.sCollectionName := 'recipes';
fbBuilder.pQueryOptions := ADR(stInsertOpt);
fbBuilder.cbQueryOptions := SIZEOF(stInsertOpt);
stInsertOpt.pDocuments := ADR(sJsonDoc);
stInsertOpt.cbDocuments := SIZEOF(sJsonDoc);
IF fbExecutor.Execute(hDBID := 1, iNoSQLQueryBuilder := fbBuilder) THEN
    IF fbExecutor.bError THEN ... END_IF
END_IF
```

**典型流程**（DocumentDB Find + Result）：
```iecst
fbBuilder.eQueryType := E_DocumentDbQueryType.Find;
// ... 配 stFindOpt ...
IF fbExecutor.ExecuteDataReturn(hDBID := 1, iNoSSQLQueryBuilder := fbBuilder, pNoSQLResult := ADR(fbResult)) THEN
    IF fbExecutor.bError THEN
        ...
    ELSE
        // fbResult.nDataCount 是返回行数；用 ReadAsString / ReadAsStruct 取
    END_IF
END_IF
```

## 4. 错误码 / 返回值

方法返回 `BOOL`（TRUE = 方法体结束）。`bError` + `ipTcResult` 表征实际结果。典型：

| 现象 | 含义 | 处理 |
|---|---|---|
| 事件含 `Collection not found` | DocumentDB 集合不存在 / `sCollectionName` 拼错 | mongoshell 验证 |
| 事件含 `Measurement not found` | TimeSeriesDB measurement 不存在 | 一般 InfluxDB 自动建；权限问题 |
| 事件含 `Query type mismatch` | Builder 字段配错（eQueryType 与 pQueryOptions^ 不匹配） | 比对 PDF §6.1.2.2 |
| 事件含 `Connection failed` | DB 不可达 | 检查连接 |
| 事件含 `Schema mismatch` (TS) | sDataType 与 PLC 结构不符 | 检查类型定义 |

完整 PDF §8.1.1 + NoSQL database return codes (PDF Appendix)。

## 5. 使用注意 / 常见坑

- **PDF 印刷 typo `iNoSSQLQueryBuilder`**：`ExecuteDataReturn` 入参必须照拼。如果将来 Beckhoff 修正，InfoSys 更新后旧 PLC 代码需要调整。（工程经验补充）
- **Builder 必须先配字段才能传入**：传入未初始化的 Builder → Server 解析错。
- **同一 Executor 实例可反复用**：不需要每次 Execute 都 new 实例。
- **同时多个 Executor 实例可并行**：每个独立的 ADS 调用，互不阻塞——大批量写入 + 后台查询可并行做。
- **`pNoSQLResult` 实例作用域**：必须从 `ExecuteDataReturn` 调用到读完结果都有效；不能用临时栈实例。
- **MongoDB / InfluxDB / TimescaleDB 都要先在 TF6420 配置器注册**：本 FB 不创建连接。
- **`tTimeout` 太小**：聚合查询、大批量写入容易超时；建议 `T#30S` 起步。
- **Builder 复用**：同一 Builder 实例可被多个 Executor 调用（线程安全要看 Server 端实现，一般是单实例单线程操作 Builder 字段）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_NoSQLQueryEvt.TcPOU`](../examples/P_Demo_FB_NoSQLQueryEvt.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：能源管理系统 PLC 端把 5 分钟一次的电能消耗数据写入 InfluxDB（时序）+ 每天一次的工艺配方写入 MongoDB（文档）。同一个 `FB_NoSQLQueryEvt` 实例既调用时序 Builder 也调用文档 Builder——通过 `I_NoSQLQueryBuilder` 接口多态。
- **价值**：单一 Executor 统一处理两类 NoSQL；批量写入 + 异步发送；EventLogger 错误诊断；连接管理透明（hDBID 即可）。
- **替代方案对比**：
  - **SQL Expert mode**：仅支持关系型，不支持 NoSQL。
  - **PLC Expert mode 的 `FB_PLCDBCmdEvt`**：用占位符 SQL，可不能处理 MongoDB JSON 或 InfluxDB 线协议。
  - **本 FB**：TC3 NoSQL Expert mode 唯一 Executor；新项目 NoSQL 集成首选。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.1.4.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/5875133963.html
- **相关 FB / FC / DUT**：`FB_NoSQLQueryBuilder_DocumentDB` / `_TimeSeriesDB`（Builder）、`FB_NoSQLResultEvt`（接收结果）、`I_NoSQLQueryBuilder`（共有接口）、`E_DocumentDbQueryType` / `E_TimeSeriesDbQueryType`、`T_QueryOptionDocumentDB_*` / `T_QueryOptionTimeSeriesDB_*`
