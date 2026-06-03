# FB_DBStoredProceduresRecordArray

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108035083.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBStoredProceduresRecordArray.TcPOU`](../examples/P_Demo_FB_DBStoredProceduresRecordArray.TcPOU) |

---

## 1. 功能简述

FB_DBStoredProceduresRecordArray 执行返回**多行结果集**的存储过程：参数列表机制与 `FB_DBStoredProcedures` 相同，但额外把 SELECT 返回的多条记录写到调用方提供的结构体数组。是"参数化 + 多行返回"的组合——比 `FB_DBRecordArraySelect`（拼 SQL 查询）更安全（无 SQL 注入）+ 比 `FB_DBStoredProcedureRecordReturn`（已 obsolete，单行返回）支持多行。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID      : T_AmsNetID        :='';
    hDBID       : UDINT             :=1;
    sProcedureName  : T_MaxString   :='';
    cbParameterList : UDINT;
    pParameterList  : POINTER TO ARRAY[0..MAX_STORED_PROCEDURES_PARAMETERS] OF ST_DBParameter;
    nStartIndex     : UDINT;
    nRecordCount    : UDINT;
    cbRecordArraySize       : UDINT;
    pDesAddr        : DWORD;
    bExecute        : BOOL;
    tTimeout        : TIME         := T#15s;
END_VAR
```

注：上方 `nRecordCount    : UDINT`（不带分号）+ 紧接 `PLC API` / `TS642080 Version: 1.2` 是 PDF §7.1.19 在第 79 页末尾排版分页造成的「源文逐字搬运」结果——PDF 原文该行末尾少打了一个分号，并且后续被换页页眉中断。**真实接口类型仍是 `UDINT`**，含义如表中说明。

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | `''` | 目标 AMS Net ID。本机 = `''`（默认即空串）。 |
| `hDBID` | `UDINT` | `1` | 数据库连接 ID。默认 `1`。 |
| `sProcedureName` | `T_MaxString` | `''` | 存储过程名。 |
| `cbParameterList` | `UDINT` | - | 参数列表字节大小。 |
| `pParameterList` | `POINTER TO ARRAY[0..MAX_STORED_PROCEDURES_PARAMETERS] OF ST_DBParameter` | - | 参数列表地址。 |
| `nStartIndex` | `UDINT` | - | 起始记录索引（0 开始）。 |
| `nRecordCount` | `UDINT` | - | 最多读取的记录数。 |
| `cbRecordArraySize` | `UDINT` | - | 结果数组字节大小，`SIZEOF(arrRecords)`。 |
| `pDesAddr` | `DWORD` | - | 结果数组地址，`ADR(arrRecords)`。**PDF 拼写为 `pDesAddr`（少一个 t），实际语义是 pDestAddr**。 |
| `bExecute` | `BOOL` | - | 上升沿触发。 |
| `tTimeout` | `TIME` | `T#15s` | ADS 超时。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy       : BOOL;
    bError      : BOOL;
    nErrID      : UDINT;
    sSQLState   : ST_DBSQLError;
    nRecords    : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 请求处理中。 |
| `bError` | `BOOL` | TRUE 表示调用失败。 |
| `nErrID` | `UDINT` | ADS 错误码 + Database Server 内部码。 |
| `sSQLState` | `ST_DBSQLError` | SQL 错误码结构。 |
| `nRecords` | `UDINT` | 实际返回的记录数。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿后 Server 用参数列表调用过程；过程执行后返回 SELECT 多行结果集，Server 把 `[nStartIndex, nStartIndex + nRecordCount)` 范围内的行按结构体二进制布局写入 `pDesAddr` 指向的数组。

**与 `FB_DBStoredProcedures` 的区别**：
- 普通版只调用过程，不取数据；本 FB 加 SELECT 结果集到 PLC。
- 参数列表机制完全相同（`ST_DBParameter` 同款）。
- 本 FB 多了 `nStartIndex` / `nRecordCount` / `cbRecordArraySize` / `pDesAddr` / `nRecords` 5 个数组相关字段。

**结构体布局要求与 `FB_DBRecordArraySelect` 同**：字段顺序匹配 SELECT 列序；ARM 平台对齐特殊处理；NVARCHAR ↔ STRING 大小匹配。

**`pDesAddr` 拼写错误**：PDF 原文是 `pDesAddr`（缺 t）。InfoSys 同款写法。调用代码必须按 PDF 拼写写 `pDesAddr := ADR(arr)`，否则编译报错。

**返回值不是过程的 `RETURN` 值**：本 FB 走的是 SELECT 结果集。如果想拿过程的 `RETURN code`，要在参数列表里加一项 `eDBParameter_ReturnValue`。

**典型场景过程模板（MS SQL）**：
```sql
CREATE PROC sp_GetLatestLogs
    @batchId NVARCHAR(40),
    @maxRows INT
AS
BEGIN
    SELECT TOP (@maxRows) ID, Timestamp, Name, Value
      FROM tProcessLog
     WHERE BatchID = @batchId
     ORDER BY Timestamp DESC
END
```
PLC 端用 paramList[0] = batchId Input、paramList[1] = maxRows Input；结果数组用 `ARRAY[0..19] OF ST_LogRecord`。

## 4. 错误码 / 返回值

| 错误号 | sSQLState | 含义 | 排查 |
|---|---|---|---|
| `0x6` | `00000` | Server 未启动 | 启动服务 |
| `0x0` | `42000` | SQL 语法错（过程内部） | DBA 检查 |
| `0x0` | `42501` | 过程 EXECUTE 权限不足 | GRANT |
| `0x0` | `42S02` | 过程不存在 | 检查名称 |
| `0x0` | `07002` | 参数数 / 类型不匹配 | 比对过程签名 |
| `0x705` | `00000` | 结果数组大小不对 | 检查 `SIZEOF` |
| `0x745` | `00000` | ADS 超时 | 加大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **`pDesAddr` 拼写陷阱**：少一个 t。这是 Beckhoff PDF 原文，无法绕过。要保持代码与 PDF 一致只能这么写。
- **结构体字段顺序匹配 SELECT 列**：与 `FB_DBRecordArraySelect` 同陷阱。
- **过程可返回多个结果集**：MS SQL 过程可有多个 SELECT，本 FB 只取第一个。复杂返回用 OUT 参数代替。
- **参数 + 结果数组双层缓冲**：参数 paraList 在调用前后被读 / 写；结果 arrRecords 在调用后被写。两个数组都必须是静态作用域。
- **ARM 对齐特殊**：与 `FB_DBRecordArraySelect` 同。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBStoredProceduresRecordArray.TcPOU`](../examples/P_Demo_FB_DBStoredProceduresRecordArray.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 上"批次报表"页要按 BatchID 查最近 20 条记录。DBA 写了存储过程 `sp_GetLatestLogs(@batchId, @maxRows)` 返回结果集。PLC 调用本 FB 把 20 行结果填到 `ARRAY[0..19] OF ST_LogRecord`，HMI 直接绑定。
- **价值**：相比 `FB_DBRecordArraySelect` 直接拼 SELECT——本 FB 走参数化过程：无 SQL 注入；过程内可加业务规则（如权限校验、时间范围限制）；DBA 改 SQL 不需要 PLC 改代码。
- **替代方案对比**：
  - **`FB_DBRecordArraySelect`**：拼 SQL 灵活，简单查询用；不安全且 SQL 在 PLC 端难维护。
  - **`FB_DBStoredProcedureRecordReturn`（obsolete）**：单行返回，已废弃。
  - **本 FB**：参数化 + 多行返回的现代推荐入口。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.19
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108035083.html
- **相关 FB / FC / DUT**：`FB_DBStoredProcedures`（无返回值版）、`FB_DBStoredProceduresRecordReturn`（obsolete 单行版）、`FB_DBRecordArraySelect`（裸 SQL 版）、`ST_DBParameter`、`E_DBParameterTypes`
