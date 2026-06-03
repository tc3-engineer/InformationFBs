# FB_SQLResultEvt

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/4830142475.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SQLResultEvt.TcPOU`](../examples/P_Demo_FB_SQLResultEvt.TcPOU) |

---

## 1. 功能简述

SQL Expert mode 下读取 Server 端缓存的 SQL 结果集的功能块（PDF §6.1.1.3.4）。配合 `FB_SQLCommandEvt.ExecuteDataReturn` 或 `FB_SQLStoredProcedureEvt.ExecuteDataReturn` 使用——这些方法把 SELECT / 存储过程返回的数据集缓存在 TwinCAT Database Server 内存中，由本 FB 的 `Read` 方法分页读到 PLC 结构体数组。`Release` 方法释放该缓存。Server 端缓存机制让大结果集可以分多次读，避免一次性 ADS 传输几十 MB 数据。

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
| `bBusy` | `BOOL` | 方法运行中。 |
| `bError` | `BOOL` | 错误置 TRUE。 |
| `ipTcResult` | `Tc3_EventLogger.I_TcMessage` | Tc3 EventLogger 消息接口。 |

### VAR_IN_OUT

无。

### Properties

| 属性 | 类型 | 说明 |
|---|---|---|
| `eTraceLevel` | `TcEventSeverity` | 事件分级阈值。 |

### Method: `Read`

```iecst
METHOD Read : BOOL
VAR_INPUT
    nStartIndex: UDINT := 0;
    nRecordCount: UDINT := 1;
    pData: POINTER TO BYTE;
    cbData: UDINT;
    bWithVerifying: BOOL := FALSE;
    bDataRelease: BOOL := TRUE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nStartIndex` | `UDINT` | `0` | 起始行 0 基索引。 |
| `nRecordCount` | `UDINT` | `1` | 要读的行数；不能超过 `pData^` 容量。 |
| `pData` | `POINTER TO BYTE` | - | 接收行的结构体数组地址；字段顺序须与 SELECT 列顺序对应。 |
| `cbData` | `UDINT` | - | 接收数组 SIZEOF。 |
| `bWithVerifying` | `BOOL` | `FALSE` | TRUE = Server 把返回的列类型 / 大小与 `pData^` 结构对比，必要时自适应调整（防类型不匹配时静默写错值）；FALSE = 直接按声明顺序填，更快但更脆。 |
| `bDataRelease` | `BOOL` | `TRUE` | TRUE = 读完后自动释放 Server 端缓存（一次性读完场景常用）；FALSE = 保留缓存以便分多次 Read（分页场景）。 |

### Method: `Release`

```iecst
METHOD Release : BOOL
```

无入参——显式释放 Server 端缓存。分页读完后必须调，否则 Server 内存累积。

## 3. 行为说明

**典型用法链路**：
1. `FB_SQLDatabaseEvt.Connect` 建连接，`CreateCmd` 绑给 `FB_SQLCommandEvt fbCmd`。
2. `fbCmd.ExecuteDataReturn(ADR(sSelectSql), ..., ADR(fbResult))` 把 SELECT 结果缓存到 Server 端，与 `fbResult` 实例绑定。
3. `fbResult.Read(nStartIndex := 0, nRecordCount := 10, ADR(aRows), SIZEOF(aRows), bDataRelease := FALSE)` 读前 10 行，保留缓存。
4. 需要更多数据时 `fbResult.Read(nStartIndex := 10, nRecordCount := 10, ...)` 继续读。
5. 读完后 `fbResult.Release()` 释放缓存。

**`bDataRelease` 自动 vs 显式 Release**：一次性读完场景 `bDataRelease := TRUE` 让 Server 自动清理；分页场景 `bDataRelease := FALSE` + 最后手动 `Release()`。如果分页时每次都 TRUE → Server 提前清缓存，第二次 Read 会失败。

**`bWithVerifying` 的作用**：Server 端缓存的列类型 / 大小可能与 PLC `pData^` 结构有差异（例如 SELECT 列是 `NVARCHAR(100)` 而 `pData^` 字段是 `STRING(50)`）。`bWithVerifying := TRUE` 让 Server 做类型适配（截断 / 填充 / 类型转换）；FALSE 则按字节直接拷贝，类型不匹配时数据错位。生产建议 TRUE（性能损失 < 10%，但避免错值），调试 / 已知严格匹配场景可 FALSE。

**`pData^` 结构与 SELECT 列对应**：列顺序按 SELECT 语句的列名顺序排；`SELECT ID, Timestamp, Name, Value FROM ...` 对应 `STRUCT nID : LINT; dtTimestamp : DATE_AND_TIME; sName : STRING(80); nValue : LREAL; END_STRUCT`。多了 padding 或字段顺序乱 → 数据错位。

**结果集大小未知时**：先 `Read(nStartIndex := 0, nRecordCount := 1, bDataRelease := FALSE)` 读 1 行；通过 `bError`、`bBusy` 判断是否还有数据（Server 错码会指示）。或在 SQL 里加 `COUNT(*)` 单独取行数（额外一次 Execute）。

**Tc3_EventLogger 错误**：`bError` 时 `ipTcResult.RequestEventText` 取详细文本，常见 `'Index out of range'`（nStartIndex 超出）、`'Cache empty'`（缓存被释放后再读）、`'Type mismatch'`（关 verifying 时类型对不上）。

## 4. 错误码 / 返回值

方法返回 `BOOL`（TRUE = 方法体结束）。`bError` + `ipTcResult` 报实际结果。典型：

| 现象 | 含义 | 处理 |
|---|---|---|
| Read 错，事件含 `Index out of range` | nStartIndex + nRecordCount > 实际行数 | 减小或先取行数 |
| Read 错，事件含 `Cache empty` | 之前 bDataRelease=TRUE 或显式 Release 后再读 | 重发 SELECT |
| Read 错，事件含 `Type mismatch` | 列类型与 `pData^` 字段不符（bWithVerifying = FALSE） | 改 TRUE 或修结构 |
| Release 错 | 缓存已释放 / 不存在 | 一般 ignore |

完整 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **必须先 `ExecuteDataReturn` 绑定缓存**：否则 Read 找不到缓存。
- **`pData^` 容量必须 ≥ `nRecordCount * SIZEOF(record)`**：否则 `cbData` 校验失败。
- **分页时 `bDataRelease := FALSE`**：所有中间 Read 用 FALSE，最后一次或显式 Release。否则 Server 提前清缓存。
- **`bWithVerifying := FALSE` 时类型严格匹配**：DateTime / String 长度对齐要小心；推荐 TRUE 保稳。
- **缓存生命周期长**：如果 `Release` 漏调，Server 端内存会累积；长时间运行后内存压力大。建议每次 ExecuteDataReturn + Read 都成对调 Release。（工程经验补充）
- **不能跨 `FB_SQLCommandEvt` 实例共享缓存**：每个 `FB_SQLResultEvt` 实例绑一次结果。
- **`Read` 不更新缓存中的「已读位置」**：可以重复读同一段；用 `nStartIndex` 控制位置而不是依赖 Server 端游标。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SQLResultEvt.TcPOU`](../examples/P_Demo_FB_SQLResultEvt.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 触发拉「最近 1000 条工艺采样」做趋势图。PLC 用 `FB_SQLCommandEvt.ExecuteDataReturn` 发 `SELECT TOP 1000 ... ORDER BY ID DESC` 让结果缓存到 Server；然后用本 FB 分 10 次 Read 各取 100 行（避免单次 ADS 传输几十 KB），HMI 边收边画曲线，最后 `Release()` 释放缓存。
- **价值**：大结果集分页避免单次 ADS 缓冲溢出；Server 端缓存让 PLC 端可按需读、按需停；EventLogger 错误诊断；分页是处理「百万行级历史数据」的唯一可行方案。
- **替代方案对比**：
  - **`FB_DBRecordArraySelect`（Tc2）**：等价但一次性返回全部数据 + nErrId 报错，大结果集不可行。
  - **`FB_PLCDBCmdEvt.ExecuteDataReturn`**：PLC Expert mode 等价，自动连接管理但需要预拼 SQL。
  - **本 FB**：SQL Expert mode 的结果集分页读取首选；obsolete `FB_SQLResult` 仅老项目兼容。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.1.3.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/4830142475.html
- **相关 FB / FC / DUT**：`FB_SQLCommandEvt`（ExecuteDataReturn 把缓存绑过来）、`FB_SQLStoredProcedureEvt`（同上）、`ST_StandardRecord`（典型行结构）、obsolete `FB_SQLResult`
