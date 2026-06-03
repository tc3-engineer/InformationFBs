# FB_DBRecordDelete

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Database` |
| Library Version | `1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108028939.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DBRecordDelete.TcPOU`](../examples/P_Demo_FB_DBRecordDelete.TcPOU) |

---

## 1. 功能简述

FB_DBRecordDelete 在数据库中执行用户自定义的 `DELETE` SQL 命令删除数据记录。SQL 命令以**指针 + 长度**方式传入，最大支持 10000 字符——足以容纳带复杂 WHERE 子句、多表 JOIN 的删除语句。是 `FB_DBRecordInsert_EX` 的删除对偶。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID          : T_AmsNetId;
    hDBID           : UDINT;
    cbCmdSize       : UDINT;
    pCmdAddr        : UDINT;
    bExecute        : BOOL;
    tTimeout        : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetId` | - | 目标 AMS Net ID。本机 = `''`。 |
| `hDBID` | `UDINT` | - | 数据库连接 ID。 |
| `cbCmdSize` | `UDINT` | - | SQL 命令字节长度，用 `SIZEOF(sCmd)` 或 `LEN(sCmd) + 1`。PDF 描述为"INSERT command 长度"（继承自 INSERT 版的文案，实际语义是 DELETE 命令）。 |
| `pCmdAddr` | `UDINT` | - | SQL 命令缓冲地址，`ADR(sCmd)`。PDF 用 `UDINT` 但语义是指针。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次删除。 |
| `tTimeout` | `TIME` | - | ADS 超时。删除涉及大数据量时建议 `T#60S` 以上。 |

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
| `bError` | `BOOL` | TRUE 表示删除失败。 |
| `nErrID` | `UDINT` | ADS 错误码 + Database Server 内部码。 |
| `sSQLState` | `ST_DBSQLError` | SQL 错误码结构。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿后 Server 在该连接上执行调用方提供的 SQL DELETE 命令。

**SQL 命令传入方式**：用 `STRING(10000)` 或更小的 STRING 变量，`pCmdAddr := ADR(sCmd)` + `cbCmdSize := SIZEOF(sCmd)`。Server 把缓冲内容当 SQL 字串处理。

**典型 SQL 模板**：
```sql
DELETE FROM tProcessLog WHERE Timestamp < '2026-01-01 00:00:00'
DELETE FROM tProcessLog WHERE Name = 'shift_total'
DELETE FROM tProcessLog WHERE Value > 1000.0 AND Name LIKE 'temp_%'
```

**SQL 命令长度上限 10000**：PDF 明确"could be till 10000 symbols"。STRING(10000) 在 PLC 中是 ~10 KB 内存。

**返回值不带删除条数**：本 FB 不返回"删了几条"。需要这个信息得用 `FB_DBStoredProcedures` 调用一个返回 `@@ROWCOUNT` 的存储过程。

**ASCII 数据库的限制**：PDF §6.5.7 描述 ASCII 文件型 DB 是顺序写入的纯文本（CSV / TSV），不支持随机 DELETE；本 FB 用于 ASCII 库会得到错误。

**SQL 注入风险**：调用方拼 SQL 时如果直接拼接用户输入（如 HMI 输入的变量名），可能造成 SQL 注入。生产代码应做输入校验或用参数化查询（`FB_DBStoredProcedures` 加 `ST_DBParameter`）。

## 4. 错误码 / 返回值

| 错误号 | sSQLState | 含义 | 排查 |
|---|---|---|---|
| `0x6` | `00000` | Server 未启动 | 启动服务 |
| `0x0` | `42000` | SQL 语法错误 | 检查 DELETE 语句拼写 |
| `0x0` | `42S02` | 表不存在 | 检查 FROM 后表名 |
| `0x0` | `42501` | DB 用户无 DELETE 权限 | 给用户 GRANT |
| `0x745` | `00000` | ADS 超时 | 加大 `tTimeout`（大批量删除可能很慢） |

## 5. 使用注意 / 常见坑

- **`DELETE FROM x;` 没 WHERE 会清空整表**：危险，删除前再检查 WHERE 子句。建议先用 `SELECT COUNT(*)` 看影响行数。（工程经验补充）
- **超长 SQL 截断**：超过 10000 字符的 SQL 会被截断且通常报语法错。复杂场景拆多次调用或用 Stored Procedure。
- **`pCmdAddr` 与 `cbCmdSize` 必须配对**：cbCmdSize 通常用 `SIZEOF(sCmd)`；如果用 `LEN(sCmd)+1`（C 风格字串）也行，Server 按 NUL 截断。
- **删除大量数据用 batch**：一次性 `DELETE FROM tLog WHERE Timestamp < '...'` 删 100 万条会锁表很久。建议分批 `DELETE TOP(1000) FROM ...` 循环。（工程经验补充）
- **MS SQL Compact 不支持 `DELETE TOP`**：分批删要用其他写法（Compact 限制较多）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DBRecordDelete.TcPOU`](../examples/P_Demo_FB_DBRecordDelete.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：生产日志保留策略——每周一凌晨 3 点（PLC 端定时器触发），删除 90 天前的日志条目，避免本地 SQL Compact 库无限增长撑爆 SD 卡。SQL 用 `DELETE FROM tProcessLog WHERE Timestamp < DATEADD(day,-90,GETDATE())`。
- **价值**：相比"换大 SD 卡 / 月度人工清理"——PLC 自动按策略清，运维零干预。
- **替代方案对比**：
  - **`eDBWriteMode_RingBuffer_Time`**：写入时自动按时长截断，但只在写入路径上工作；本 FB 适合按"业务规则"删除（按 Name 删某变量、按数值范围删等）。
  - **DBA SQL Agent 任务**：能用，但要 DBA 介入；OEM 设备难配。
  - **本 FB**：PLC 内嵌的灵活删除入口。

## 8. 参考资料

- **PDF**：[TS6420_tcdbserver_en.pdf](https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf) §7.1.15
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6420_tc3_database_server/108028939.html
- **相关 FB / FC**：`FB_DBRecordInsert_EX`（INSERT 对偶）、`FB_DBStoredProcedures`（参数化查询）、`E_DBWriteModes`（含环形缓冲模式）
