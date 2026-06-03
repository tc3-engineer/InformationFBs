# FB_DBRecordInsert_EX

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108030475.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBRecordInsert_EX.TcPOU`](../examples/P_Demo_FB_DBRecordInsert_EX.TcPOU) |

---

## 1. 功能简述

FB_DBRecordInsert_EX 在数据库中执行用户自定义的 `INSERT` SQL 命令插入单条或多条记录。与已废弃的 `FB_DBRecordInsert`（obsolete §7.1.20.2）相比，本 EX 版本**支持长达 10000 字符的 SQL 命令**——可容纳多列、多值、子查询等复杂 INSERT 语法。SQL 命令以**指针 + 长度**方式传入。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID      : T_AmsNetId;
    hDBID       : UDINT;
    cbCmdSize   : UDINT;
    pCmdAddr    : UDINT;
    bExecute    : BOOL;
    tTimeout    : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetId` | - | 目标 AMS Net ID。本机 = `''`。 |
| `hDBID` | `UDINT` | - | 数据库连接 ID。 |
| `cbCmdSize` | `UDINT` | - | SQL 命令字节长度，用 `SIZEOF(sCmd)`。 |
| `pCmdAddr` | `UDINT` | - | SQL 命令缓冲地址，`ADR(sCmd)`。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次插入。 |
| `tTimeout` | `TIME` | - | ADS 超时，`T#15S` 通常够；批量 INSERT 建议加大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy       : BOOL;
    bError      : BOOL;
    nErrID      : UDINT;
    sSQLState   : ST_DBSQLError;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 请求处理中。 |
| `bError` | `BOOL` | TRUE 表示插入失败。 |
| `nErrID` | `UDINT` | ADS 错误码 + Database Server 内部码。 |
| `sSQLState` | `ST_DBSQLError` | SQL 错误码结构。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿后 Server 在该连接执行调用方提供的 SQL INSERT 命令。

**典型 SQL 模板**：
```sql
INSERT INTO tBatchHeader (BatchID, ProductName, StartTime, Operator)
  VALUES ('B20260603-001', 'M250 Module', GETDATE(), 'Zhang San')

INSERT INTO tProductionLog (Timestamp, Name, Value, BatchID)
  VALUES (GETDATE(), 'production_count', 1234.5, 'B20260603-001')

INSERT INTO tArchive (id, ts, val)
  SELECT NEWID(), Timestamp, Value FROM tLive WHERE Timestamp < '2026-01-01'
```

**与 `FB_DBWrite` 的区别**：
- `FB_DBWrite` 适合"`Timestamp/Name/Value`"标准 3 列结构，自动从 ADS 读变量值；
- 本 FB 适合**任意多列业务表**，PLC 端拼好完整 INSERT 语句即可。
- 本 FB 自由度高、`FB_DBWrite` 简单——按业务需求选。

**SQL 长度上限 10000 字符**：覆盖大多数 INSERT 场景。批量 INSERT 单语句（VALUES(),(),()）也能装下数十条。

**字串值的引号转义**：SQL 内的字串值要用单引号包，字符串本身含的单引号要双写：`'O''Brien'`。PLC 端用 `REPLACE(sName, "'", "''")` 之类处理。

**Datetime 字面量**：MS SQL 用 `'2026-06-03 14:30:00'`；MySQL `'2026-06-03 14:30:00'`；SQL Compact 类似 MS SQL；Oracle 用 `TO_DATE('...', 'YYYY-MM-DD HH24:MI:SS')`。跨 DB 用 `GETDATE()` / `CURRENT_TIMESTAMP` 让 DB 自己填。

**SQL 注入风险**：与 `FB_DBRecordDelete` 同。生产代码中拼接外部输入应做转义或用 `FB_DBStoredProcedures` 参数化。

## 4. 错误码 / 返回值

| 错误号 | sSQLState | 含义 | 排查 |
|---|---|---|---|
| `0x6` | `00000` | Server 未启动 | 启动服务 |
| `0x0` | `42000` | SQL 语法错 | 检查 INSERT 语句 |
| `0x0` | `23000` | 违反约束（UNIQUE / 外键 / NOT NULL） | 检查值是否冲突或必填字段是否给值 |
| `0x0` | `42S02` | 表不存在 | 建表 |
| `0x0` | `42S22` | 列名错 | 核对列名拼写 |
| `0x745` | `00000` | ADS 超时 | 加大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **字串转义**：PLC 拼 SQL 时容易忘记把单引号、反斜杠、% / _（LIKE 特殊字符）转义。最佳实践是用 `FB_DBStoredProcedures` 参数化方式而不是 PLC 端拼 SQL。
- **多语句 SQL 不一定支持**：`INSERT ...; INSERT ...;` 分号分隔的多语句在某些 OLE DB Provider 上禁用。批量插入用 `INSERT ... VALUES(),(),()`。
- **`GETDATE()` 时区**：返回的是 DB 服务器时区，跨地域要注意。统一用 UTC（`GETUTCDATE()`）更安全。（工程经验补充）
- **`cbCmdSize` 用 `SIZEOF`**：STRING(10000) 的 SIZEOF 是 10001（含 NUL）；Server 按 NUL 截断，不会出错。
- **Compact 数据库不支持 `GETDATE()`**：用 `CURRENT_TIMESTAMP`（标准 SQL）跨 DB 更兼容。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBRecordInsert_EX.TcPOU`](../examples/P_Demo_FB_DBRecordInsert_EX.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：每批生产开始时往 `tBatchHeader` 表插入一条批次记录（含 BatchID / 产品型号 / 操作员 / 开始时间）；批次过程中产生的工艺点 Insert 到 `tProductionLog`（含 BatchID 外键）。最终在 MES 端可按批次查询完整生产路径。
- **价值**：相比 `FB_DBWrite` 的简单 3 列表——本 FB 让 PLC 直接写入设计好的业务表，列结构对接 MES / ERP；表结构由 DBA 控制，PLC 只写值。
- **替代方案对比**：
  - **`FB_DBWrite`**：标准 Timestamp/Name/Value 表；业务场景需要事后查再 JOIN BatchID 等关联表。
  - **`FB_DBStoredProcedures`**：参数化更安全，复杂业务流（多表插入 + 事务）推荐。
  - **本 FB**：单语句、PLC 端拼 SQL 的中间方案；OEM 设备 PLC 端能掌控的最直白方式。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.16
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108030475.html
- **相关 FB / FC**：`FB_DBRecordDelete`（DELETE 对偶）、`FB_DBRecordInsert`（已废弃，仅作兼容；新代码用本 EX 版本）、`FB_DBStoredProcedures`（参数化推荐）、`FB_DBWrite`（标准表简化版）
