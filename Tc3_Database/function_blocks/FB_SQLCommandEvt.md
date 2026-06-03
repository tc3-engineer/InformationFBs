# FB_SQLCommandEvt

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2674384779.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SQLCommandEvt.TcPOU`](../examples/P_Demo_FB_SQLCommandEvt.TcPOU) |

---

## 1. 功能简述

SQL Expert mode 下执行任意 SQL 命令的功能块（PDF §6.1.1.3.3）。使用前必须先用 `FB_SQLDatabaseEvt.CreateCmd` 把数据库连接绑定到本 FB 的实例。提供 `Execute`（不返回数据集）和 `ExecuteDataReturn`（返回数据集，需配 `FB_SQLResultEvt` 接收）两个方法。与 PLC Expert mode 的 `FB_PLCDBCmdEvt` 不同——本 FB 复用 `FB_SQLDatabaseEvt` 已开的常驻连接，单次 SQL 调用无重连开销，高吞吐 SQL 工作流首选；缺点是 SQL 命令不支持参数占位符（`{name}` 替换），需要调用方拼好完整 SQL 字符串。

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
| `sNetID` | `T_AmsNetID` | `''` | Database Server AMS Net ID（一般与 FB_SQLDatabaseEvt 同）。 |
| `tTimeout` | `TIME` | `T#5S` | ADS 超时。 |

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
    pSQLCmd: POINTER TO BYTE;
    cbSQLCmd: UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pSQLCmd` | `POINTER TO BYTE` | SQL 命令字符串地址（如 `ADR(sCmd)`，`sCmd : STRING(1000)`）。 |
| `cbSQLCmd` | `UDINT` | SQL 字符串字节大小（`SIZEOF`）。 |

### Method: `ExecuteDataReturn`（返回数据集）

```iecst
METHOD ExecuteDataReturn : BOOL
VAR_INPUT
    pSQLCmd: POINTER TO BYTE;
    cbSQLCmd: UDINT;
    pSQLDBResult: POINTER TO FB_SQLResult;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pSQLCmd` | `POINTER TO BYTE` | SQL 命令地址（一般 SELECT）。 |
| `cbSQLCmd` | `UDINT` | SQL 字节大小。 |
| `pSQLDBResult` | `POINTER TO FB_SQLResult` | 调用方提供的 `FB_SQLResultEvt`（或 obsolete `FB_SQLResult`）实例地址；返回行将缓存到 Server 内由该实例读取。 |

## 3. 行为说明

**初始化前提**：必须先调 `FB_SQLDatabaseEvt.CreateCmd(ADR(fbThis))` 把已打开的连接句柄绑到本 FB 实例上，否则 Execute 会失败。绑定后本 FB 实例与原 `FB_SQLDatabaseEvt` 实例共享同一连接，不能跨实例混用。

**`Execute` vs `ExecuteDataReturn`**：`Execute` 用于 INSERT / UPDATE / DELETE / DDL（CREATE TABLE / DROP / ALTER）—— 这些不返回结果集；`ExecuteDataReturn` 用于 SELECT，结果集由 Server 端缓存，需调 `FB_SQLResultEvt.Read` 读取。

**SQL 字符串处理**：本 FB 不支持占位符替换，调用方必须自己拼完整 SQL（含值字面、引号转义等）。处理字符串的 ANSI / Unicode 转义、DateTime 格式、NULL 表示要按目标 DB 方言处理。对于结构化插入 / 防注入需求，用 `FB_PLCDBCmdEvt`（PLC Expert mode）的占位符模式更安全。

**连接复用 vs 重连**：与 `FB_PLCDBCmdEvt` 的「每次自动开关连接」不同，本 FB 用上游 `FB_SQLDatabaseEvt` 的常驻连接，单次 Execute 只有协议层延迟（5-10 ms）；前者每次 200-500 ms 建连开销。同一 `FB_SQLCommandEvt` 实例可反复 Execute 不同 SQL，无需重新 CreateCmd。

**`pSQLDBResult` 必须事先就绪**：传入的 `FB_SQLResultEvt` 实例必须已声明且作用域持续到结果读完。Server 端把结果缓存与该实例绑定，调用方后续通过 `fbResult.Read(...)` 取数据；不再用时 `fbResult.Release()` 释放缓存。

**Tc3_EventLogger 错误**：`bError` 时 `ipTcResult.RequestEventText` 取详细文本，常见 `'Connection not initialized'`（忘记 CreateCmd）、`'Syntax error'`、`'Connection lost'`。

## 4. 错误码 / 返回值

方法返回 `BOOL`（TRUE = 方法体结束）。`bError` + `ipTcResult` 报实际结果。典型：

| 现象 | 含义 | 处理 |
|---|---|---|
| Execute 错，事件含 `not initialized` | 忘记先 `FB_SQLDatabaseEvt.CreateCmd` | 加初始化步骤 |
| 事件含 `Syntax error` | SQL 语法错 | 在 SQL 客户端先跑通 |
| 事件含 `Connection lost` | DB 端断开 | 重 Connect + CreateCmd |
| 事件含 `Permission denied` | 用户无权执行 | DBA 给权限 |

完整 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **必须先 `CreateCmd` 才能 Execute**：否则方法瞬间报「未初始化」。生产代码应在启动序列里检查 CreateCmd 成功才放行业务。
- **`pSQLCmd` 指向 STRING 变量**：`sCmd : STRING(1000)` 然后 `ADR(sCmd)` + `SIZEOF(sCmd)`。STRING 长度上限决定 SQL 最大长度，复杂 SQL 用 `STRING(4000)` 或更大。
- **SQL 字符串单引号转义**：MS SQL / MySQL 用 `''` 转义（两个单引号），PostgreSQL 同；Oracle 同。IEC 字符串里也是 `$'`。手工拼字符串易出错——含用户输入的 SQL 一定要走存储过程或 `FB_PLCDBCmdEvt` 占位符。
- **`ExecuteDataReturn` 后必须 `FB_SQLResultEvt.Release` 释放缓存**：否则 Server 端 RAM 累积；长时间运行后崩溃。（工程经验补充）
- **连接断后所有 `FB_SQLCommandEvt` 实例失效**：必须 `FB_SQLDatabaseEvt.Disconnect → Connect → CreateCmd` 重建链路；不能只 reconnect。
- **多线程 / 多任务并发**：同一 `FB_SQLCommandEvt` 实例不能被多个任务同时 Execute——本 FB 是单线程语义。多任务用各自实例（共享连接需评估 Server 端并发能力）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SQLCommandEvt.TcPOU`](../examples/P_Demo_FB_SQLCommandEvt.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：MES 系统要求 PLC 每秒向 MS SQL 写 100 条工艺采样 + 周期 SELECT 拉配方表。先用 `FB_SQLDatabaseEvt.Connect` 建一次常驻连接，`CreateCmd` 绑给本 FB 实例 `fbCmd`；业务循环里 `fbCmd.Execute(ADR(sInsertSql), SIZEOF(sInsertSql))` 写入采样（单次 5-10 ms）；HMI 触发时 `fbCmd.ExecuteDataReturn(ADR(sSelectSql), ..., ADR(fbResult))` 取结果。
- **价值**：高吞吐采集场景比 `FB_PLCDBCmdEvt` 快 10-50 倍；SELECT 结果集 Server 端缓存避免一次大量 ADS 数据；EventLogger 错误诊断。
- **替代方案对比**：
  - **`FB_PLCDBCmdEvt`**：自动连接、有占位符支持；低频写或安全敏感场景更好。本 FB 高频写更优。
  - **`FB_DBRecordInsert_EX`（Tc2）**：等价但 nErrId 报错。
  - **本 FB**：TC3 SQL Expert mode 高吞吐自由 SQL 首选；obsolete `FB_SQLCommand` 仅老项目兼容。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.1.3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/2674384779.html
- **相关 FB / FC / DUT**：`FB_SQLDatabaseEvt`（必须先 CreateCmd 绑连接）、`FB_SQLResultEvt`（接收 SELECT 结果）、`FB_PLCDBCmdEvt`（PLC Expert mode 等价）、obsolete `FB_SQLCommand`
